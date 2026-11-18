import argparse
import json
from pathlib import Path
from .core import analyze
from .exports import save
from .server import serve


def main():
    parser=argparse.ArgumentParser(description='PeopleComfort: CBE-based scenario comparison')
    commands=parser.add_subparsers(dest='command',required=True)
    a=commands.add_parser('analyze');a.add_argument('--project',type=Path,default=Path(__file__).parent/'data/demo.json')
    a.add_argument('--out',type=Path,default=Path('results'));a.add_argument('--no-uncertainty',action='store_true')
    s=commands.add_parser('serve');s.add_argument('--port',type=int,default=8765)
    args=parser.parse_args()
    if args.command=='serve': serve(args.port);return
    p=json.loads(args.project.read_text(encoding='utf-8-sig'))
    if p.get('schema_version')==2:
        from .framework import analyze as analyze_general
        from .framework_exports import save as save_general
        result=analyze_general(p,not args.no_uncertainty);save_general(result,args.out)
    else:
        result=analyze(p,not args.no_uncertainty);save(result,args.out)
    print(json.dumps(result['selection'],ensure_ascii=False,indent=2))
    print(f'Wrote outputs to {args.out.resolve()}')

if __name__=='__main__':main()
