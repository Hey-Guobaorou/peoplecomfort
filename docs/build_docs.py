"""Build the offline PeopleComfort guide, API and CLI pages from Markdown."""
from pathlib import Path
import html,re,shutil
ROOT=Path(__file__).resolve().parent

def blocks(markdown):
 lines=markdown.splitlines();i=0
 while i<len(lines):
  line=lines[i].strip();i+=1
  if not line:continue
  if line.startswith('```'):
   code=[]
   while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
   i+=1;yield ('code','\n'.join(code));continue
  if line.startswith('|') and i<len(lines) and lines[i].startswith('|'):
   heads=[x.strip() for x in line.strip('|').split('|')];i+=1;rows=[]
   while i<len(lines) and lines[i].startswith('|'):
    rows.append([x.strip() for x in lines[i].strip('|').split('|')]);i+=1
   yield ('table',[heads,*rows]);continue
  figure=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',line)
  if figure:yield ('image',(figure.group(1),figure.group(2)));continue
  if line.startswith('# '):yield ('h1',line[2:]);continue
  if line.startswith('## '):yield ('h2',line[3:]);continue
  if line.startswith('- '):yield ('bullet',line[2:]);continue
  yield ('p',line)
NAV=[('Overview','index.html'),('Quick start','getting-started.html'),('General framework','general-framework.html'),('Workflow overview','workflows.html'),('1. Space & profiles','workflow/space.html'),('2. Designs & scenarios','workflow/scenarios.html'),('3. Calculate & allocate','workflow/calculate.html'),('4. Compare decisions','workflow/compare.html'),('5. Stress-test & export','workflow/output.html'),('Python API','api/index.html'),('Function details','api/functions.html'),('CLI reference','cli/index.html'),('analyze','cli/analyze.html'),('serve','cli/serve.html')]
CSS="""*{box-sizing:border-box}body{margin:0;background:#fff;color:#263832;font:15px/1.65 system-ui,Arial,sans-serif}header{position:fixed;top:0;left:0;right:0;height:56px;background:#153d38;color:white;display:flex;align-items:center;padding:0 24px;z-index:2}header strong{font-size:19px;font-weight:650}header span{margin-left:18px;color:#bddbd1;font-size:12px}aside{position:fixed;top:56px;bottom:0;left:0;width:235px;overflow:auto;background:#f4f8f5;border-right:1px solid #d6e1dc;padding:16px 10px}aside a{display:block;padding:5px 12px;color:#345f53;text-decoration:none;border-radius:4px;font-size:13px}aside a:hover,aside a.current{background:#dcebe3;color:#104b3e}aside .group{font-size:10px;letter-spacing:1.4px;color:#708d7e;margin:15px 12px 6px;font-weight:bold}main{margin:56px auto 0 calc(235px + (100vw - 235px - min(900px,100vw - 300px))/2);max-width:900px;padding:38px 32px 80px}h1{font-size:34px;line-height:1.2;color:#153d38}h2{font-size:23px;margin-top:34px;border-top:1px solid #e1eae4;padding-top:18px}p{margin:13px 0}a{color:#14735b}pre{background:#f0f4f2;border:1px solid #d5e1d9;padding:16px;overflow:auto;border-radius:4px;font-size:13px;line-height:1.5}code{background:#eff4f1;padding:2px 4px;border-radius:3px}pre code{padding:0}table{border-collapse:collapse;width:100%;font-size:13px;margin:16px 0}th,td{border:1px solid #d7e0da;padding:9px;text-align:left;vertical-align:top}th{background:#ebf2ed}.scroll{overflow:auto}ul{padding-left:24px}figure{margin:20px 0}figure img{max-width:100%}figcaption{font-size:12px;color:#698078}footer{border-top:1px solid #dce6df;color:#7b8c83;font-size:12px;margin-top:45px;padding-top:12px}@media(max-width:850px){header{position:static}aside{position:static;width:auto;height:auto;display:flex;flex-wrap:wrap;border:0;padding:10px}aside .group{display:none}aside a{display:inline-block}main{margin:0;max-width:none;padding:24px}}"""
def inline(s):
 s=html.escape(s)
 s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
 s=re.sub(r'\*\*(.*?)\*\*',r'<strong>\1</strong>',s)
 s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',s)
 return s
def page(source):
 rel=source.relative_to(ROOT);depth=len(rel.parts)-1;prefix='../'*depth
 body=[];title='PeopleComfort'
 for kind,data in blocks(source.read_text(encoding='utf-8')):
  if kind=='h1':title=data;body.append('<h1>'+inline(data)+'</h1>')
  elif kind=='h2':body.append('<h2>'+inline(data)+'</h2>')
  elif kind=='p':body.append('<p>'+inline(data)+'</p>')
  elif kind=='bullet':body.append('<p>• '+inline(data)+'</p>')
  elif kind=='code':body.append('<pre><code>'+html.escape(data)+'</code></pre>')
  elif kind=='table':body.append('<div class="scroll"><table>'+''.join('<tr>'+''.join(f'<{"th" if i==0 else "td"}>{inline(c)}</{"th" if i==0 else "td"}>' for c in row)+'</tr>' for i,row in enumerate(data))+'</table></div>')
  elif kind=='image':body.append('<figure><img src="'+html.escape(data[1])+'"><figcaption>'+html.escape(data[0])+'</figcaption></figure>')
 nav='';
 for i,(label,target) in enumerate(NAV):
  if i in (0,9,11):nav+='<div class="group">'+('GUIDE' if i==0 else 'API REFERENCE' if i==9 else 'CLI REFERENCE')+'</div>'
  nav+='<a'+(' class="current"' if target==rel.with_suffix('.html').as_posix() else '')+' href="'+prefix+target+'">'+html.escape(label)+'</a>'
 return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+' — PeopleComfort documentation</title><style>'+CSS+'</style><header><strong>PeopleComfort</strong><span>Documentation · v0.2.0</span></header><aside>'+nav+'</aside><main>'+''.join(body)+'<footer>PeopleComfort v0.2.0 · Offline documentation · Illustrative research prototype</footer></main></html>'
def main():
 for source in ROOT.rglob('*.md'):
  source.with_suffix('.html').write_text(page(source),encoding='utf-8')
 bundled=(ROOT/'index.md').read_text(encoding='utf-8')+'\n\n'+(ROOT/'getting-started.md').read_text(encoding='utf-8')+'\n\n'+(ROOT/'workflows.md').read_text(encoding='utf-8')
 # The embedded workbench guide is self-contained; its links go to the offline documentation in the source package.
 source=ROOT/'_embedded.md';source.write_text(bundled,encoding='utf-8')
 embedded=page(source)
 for label,target in NAV:embedded=embedded.replace('href="'+target+'"','href="/docs/'+target+'"')
 (ROOT.parent/'src/peoplecomfort/web/guide.html').write_text(embedded,encoding='utf-8')
 webdocs=ROOT.parent/'src/peoplecomfort/web/docs'
 for source_page in ROOT.rglob('*.html'):
  target=webdocs/source_page.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source_page,target)
 source.unlink()
 print('Built',len(list(ROOT.rglob('*.html'))),'offline documentation pages and workbench guide')
if __name__=='__main__':main()
