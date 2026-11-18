// Adapter only. Unmodified CBE source files and their GPL-2.0 license are adjacent.
const fs = require('fs');
const {comf} = require('./comfort-models.js');
comf.useSelfGeneratedAirSpeed = true;
const cases = JSON.parse(fs.readFileSync(0, 'utf8'));
const results = cases.map(x => {
  const r = comf.pmvElevatedAirspeed(x.ta, x.tr, x.v, x.rh, x.met, x.clo, 0);
  if (!Number.isFinite(r.pmv) || !Number.isFinite(r.ppd) || !Number.isFinite(r.cooling_effect))
    throw new Error('CBE returned non-finite output');
  return {...r, relative_air_speed:comf.relativeAirSpeed(x.v,x.met),
    dynamic_clothing:comf.dynamicClothing(x.clo,x.met)};
});
process.stdout.write(JSON.stringify(results));
