"""Embed the checked example and standalone solver in a static GitHub Pages demo."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
project=json.loads((ROOT.parent/'examples/general/project.json').read_text(encoding='utf-8'))
source=(ROOT/'demo.template.txt').read_text(encoding='utf-8')
script=(ROOT/'demo.js').read_text(encoding='utf-8')
result=source.replace('__PROJECT_JSON__',json.dumps(project,ensure_ascii=True).replace('</',r'<\/')).replace('__DEMO_JS__',script)
(ROOT/'demo.html').write_text(result,encoding='utf-8')
print('Built docs/demo.html from examples/general/project.json')
