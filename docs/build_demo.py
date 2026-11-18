"""Embed the checked example and standalone solver in a static GitHub Pages demo."""
from pathlib import Path
import json
import shutil
ROOT=Path(__file__).resolve().parent
project=json.loads((ROOT.parent/'examples/a3-thermal/project.json').read_text(encoding='utf-8'))
source=(ROOT/'workbench.template.txt').read_text(encoding='utf-8')
script=(ROOT/'workbench.js').read_text(encoding='utf-8')
vendor=ROOT.parent/'src/peoplecomfort/_cbe'
target=ROOT/'cbe'
target.mkdir(exist_ok=True)
for name in ('util.js','psychrometrics.js','comfort-models.js','LICENSE','upstream.json'):
    shutil.copyfile(vendor/name,target/name)
result=source.replace('__PROJECT_JSON__',json.dumps(project,ensure_ascii=True).replace('</',r'<\/')).replace('__DEMO_JS__',script)
(ROOT/'demo.html').write_text(result,encoding='utf-8')
print('Built docs/demo.html from examples/a3-thermal/project.json and pinned CBE scripts')
