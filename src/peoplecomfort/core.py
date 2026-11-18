"""Exhaustive two-zone allocation and minimax-regret comparison, no stochastic behaviour."""
from copy import deepcopy
import hashlib
from itertools import product
import json
import math
from .comfort import calculate, provenance
from . import __version__


def validate(p):
    if p.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    zones, profiles, designs, scenarios = (p[k] for k in ("zones","profiles","designs","scenarios"))
    if len(zones) != 2 or not 2 <= len(profiles) <= 4 or not 3 <= len(designs) <= 10:
        raise ValueError("Prototype supports 2 zones, 2-4 types, 3-10 designs")
    for group in (zones, profiles, designs, scenarios):
        ids = [x["id"] for x in group]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate identifier")
    if not scenarios or len(scenarios) > 100:
        raise ValueError("Need 1-100 scenarios")
    def integer(v):
        return isinstance(v,int) and not isinstance(v,bool) and v >= 0
    if not integer(p["total_people"]) or not 1 <= p["total_people"] <= 24:
        raise ValueError("total_people must be 1-24")
    n = p["total_people"]
    zids = {z["id"] for z in zones}
    for z in zones:
        if not integer(z["max_seats"]): raise ValueError("Invalid zone capacity")
        if not z.get("source") or not z.get("evidence_status"):
            raise ValueError("Zone provenance required")
    for t in profiles:
        if not t.get("allowed_zones") or not set(t["allowed_zones"]) <= zids:
            raise ValueError("Unknown or empty allowed_zones")
    pids = {x["id"] for x in profiles}
    for s in scenarios:
        if set(s["counts"]) != pids or not all(integer(v) for v in s["counts"].values()) or sum(s["counts"].values()) != n:
            raise ValueError("Composition counts must be nonnegative integers summing to total_people")
        if s["split"] not in ("development","holdout"):
            raise ValueError("Unknown scenario split")
    for d in designs:
        if set(d["seats"]) != zids or not all(integer(v) for v in d["seats"].values()) or sum(d["seats"].values()) != n:
            raise ValueError("Each design must provide exactly total_people seats")
        if any(d["seats"][z["id"]] > z["max_seats"] for z in zones):
            raise ValueError("Design exceeds zone capacity")
    if not any(s["id"] == p["baseline_scenario"] and s["split"] == "development" for s in scenarios):
        raise ValueError("Baseline must belong to development scenarios")
    if p["existing_design"] not in {d["id"] for d in designs}:
        raise ValueError("Unknown existing_design")
    if not any(s["split"] == "holdout" for s in scenarios):
        raise ValueError("At least one holdout scenario required")
    for value in [p["pmv_limit"], *p["uncertainty"]["thresholds"]]:
        if not isinstance(value,(float,int)) or not math.isfinite(value) or not .1 <= value <= 1:
            raise ValueError("PMV screening threshold must be in [0.1,1]")
    keys = ["temperature_offsets","gradient_offsets","clothing_offsets","thresholds"]
    for key in keys:
        values = p["uncertainty"][key]
        if not values or len(values) > 5 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in values):
            raise ValueError("Invalid uncertainty grid")
    if math.prod(len(p["uncertainty"][k]) for k in keys) > 100:
        raise ValueError("Uncertainty grid limited to 100 worlds")
    work=sum(math.prod(c+1 for c in s['counts'].values()) for s in scenarios)*len(designs)*math.prod(len(p['uncertainty'][k]) for k in keys)
    if work > 5_000_000:
        raise ValueError("Enumeration budget exceeded; reduce scenario count, population or uncertainty grid")
    return p


def allocate(counts, capacities, pmvs, limit, allowed):
    """Integer allocations x[i] to zone 0; remainder to zone 1.
    Primary: mean PMV exceedance. Tie: worst type mean exceedance, then x tuple.
    Assumes managed allocation; does not predict occupant choices.
    """
    n = sum(counts)
    best, valid = None, 0
    for x in product(*(range(c+1) for c in counts)):
        if sum(x) > capacities[0] or n-sum(x) > capacities[1]: continue
        if any((x[i] and not allowed[i][0]) or (counts[i]-x[i] and not allowed[i][1]) for i in range(len(counts))): continue
        burdens, flagged, assignment = [], 0, []
        for i,c in enumerate(counts):
            amounts = [x[i],c-x[i]]
            burden = sum(amounts[z]*max(0,abs(pmvs[i][z])-limit) for z in range(2))
            burdens.append(burden)
            flagged += sum(amounts[z] for z in range(2) if abs(pmvs[i][z]) > limit)
            assignment.append(amounts)
        score = sum(burdens)/n
        worst = max((b/c for b,c in zip(burdens,counts) if c),default=0)
        key = (round(score,12),round(worst,12),x)
        valid += 1
        if best is None or key < best[0]:
            best = (key, {"loss":score,"worst_type_loss":worst,"flagged":flagged,
                          "flagged_share":flagged/n,"allocation":assignment,
                          "type_loss":[b/c if c else None for b,c in zip(burdens,counts)]})
    if best is None:
        return {"feasible":False,"loss":None,"reason":"No allocation satisfies capacity and allowed-zone constraints",
                "feasible_allocations":0}
    return {"feasible":True,**best[1],"feasible_allocations":valid}


def evaluate(p, matrix, limit):
    profiles, zones = p["profiles"], p["zones"]
    allowed = [[z["id"] in t["allowed_zones"] for z in zones] for t in profiles]
    rows = []
    for s in p["scenarios"]:
        counts = [s["counts"][t["id"]] for t in profiles]
        scenario_rows = []
        for d in p["designs"]:
            row = allocate(counts,[d["seats"][z["id"]] for z in zones],matrix,limit,allowed)
            row.update(design=d["id"],scenario=s["id"],split=s["split"])
            scenario_rows.append(row)
        feasible = [r["loss"] for r in scenario_rows if r["feasible"]]
        optimum = min(feasible) if feasible else None
        for r in scenario_rows:
            r["regret"] = r["loss"]-optimum if r["feasible"] else None
        rows.extend(scenario_rows)
    return rows


def select(rows, scenario_ids, design_ids, metric="regret"):
    scores = {}
    for did in design_ids:
        group = [r for r in rows if r["design"] == did and r["scenario"] in scenario_ids]
        scores[did] = max(r[metric] for r in group) if len(group)==len(scenario_ids) and all(r["feasible"] for r in group) else None
    valid = [v for v in scores.values() if v is not None]
    winners = [d for d,v in scores.items() if v is not None and abs(v-min(valid)) <= 1e-10] if valid else []
    return {"winners":winners,"scores":scores}


def analyze(project, uncertainty=True):
    p = validate(deepcopy(project))
    profiles,zones = p["profiles"],p["zones"]
    physical_worlds = [(0.,0.,0.)]
    if uncertainty:
        for world in product(*(p["uncertainty"][k] for k in ("temperature_offsets","gradient_offsets","clothing_offsets"))):
            if tuple(world) not in physical_worlds: physical_worlds.append(tuple(world))
    cases=[]
    for dt,dg,dc in physical_worlds:
        for t in profiles:
            for j,z in enumerate(zones):
                shift=dt+(-dg if j==0 else dg)
                cases.append({"ta":z["ta"]+shift,"tr":z["tr"]+shift,"rh":z["rh"],"v":z["v"],
                              "met":t["met"],"clo":t["clo"]+dc})
    thermal = calculate(cases)
    width=len(profiles)*2
    matrices=[[[thermal[k*width+i*2+j]["pmv"] for j in range(2)] for i in range(len(profiles))] for k in range(len(physical_worlds))]
    rows=evaluate(p,matrices[0],p["pmv_limit"])
    ids=[d["id"] for d in p["designs"]]
    dev=[s["id"] for s in p["scenarios"] if s["split"]=="development"]
    hold=[s["id"] for s in p["scenarios"] if s["split"]=="holdout"]
    baseline=select(rows,[p["baseline_scenario"]],ids,"loss")
    robust=select(rows,dev,ids)
    holdout=select(rows,hold,ids)
    sensitivity=[]
    if uncertainty:
        for k,(dt,dg,dc) in enumerate(physical_worlds):
            for threshold in p["uncertainty"]["thresholds"]:
                altered=evaluate(p,matrices[k],threshold)
                train=select(altered,dev,ids)
                test=select(altered,hold,ids)
                sensitivity.append({"temperature_offset":dt,"gradient_offset":dg,"clothing_offset":dc,
                                    "pmv_limit":threshold,"development_winners":train["winners"],
                                    "holdout_regret_by_design":test["scores"]})
    ledger=[{"type":t["id"],"zone":z["id"],"input":cases[i*2+j],"output":thermal[i*2+j]}
            for i,t in enumerate(profiles) for j,z in enumerate(zones)]
    digest=hashlib.sha256(json.dumps(p,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
    return {"schema_version":1,"software_version":__version__,"project":p,"input_sha256":digest,
            "engine":provenance(),"thermal_ledger":ledger,"rows":rows,
            "selection":{"T1":[p["existing_design"]],"T2":baseline,"T3":robust,"holdout":holdout},
            "uncertainty":sensitivity,
            "interpretation":"Conditional illustrative scenarios; PMV screening is not measured personal satisfaction. "
              "Allocation is an ideal managed matching under constraints; no behaviour or environment feedback is predicted."}
