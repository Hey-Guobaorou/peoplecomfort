"""Loopback-only interface; no network dependency after downloading the package."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
import json
from .core import analyze
from .exports import archive

ROOT=Path(__file__).parent
DOC_PAGES={'general-framework.html','index.html','getting-started.html','workflows.html','workflow/space.html','workflow/scenarios.html','workflow/calculate.html','workflow/compare.html','workflow/output.html','api/index.html','api/functions.html','cli/index.html','cli/analyze.html','cli/serve.html'}


def serve(port=8765):
    class Handler(BaseHTTPRequestHandler):
        def send(self,data,mime='application/json; charset=utf-8',status=200):
            if isinstance(data,str): data=data.encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type',mime)
            self.send_header('Content-Length',str(len(data)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.end_headers();self.wfile.write(data)

        def do_GET(self):
            if self.path=='/api/general-demo':
                return self.send((ROOT/'data/general.json').read_bytes())
            if self.path=='/api/demo':
                return self.send((ROOT/'data/demo.json').read_bytes())
            asset={'/':'index.html','/app.js':'app.js','/style.css':'style.css','/guide':'guide.html','/framework':'framework.html','/framework.js':'framework.js'}.get(self.path)
            if self.path.startswith('/docs/'):
                relative=self.path.removeprefix('/docs/')
                if relative in DOC_PAGES:
                    return self.send((ROOT/'web/docs'/relative).read_bytes(),'text/html; charset=utf-8')
            if not asset: return self.send('{"error":"Not found"}',status=404)
            mime={'html':'text/html','js':'application/javascript','css':'text/css'}[asset.rsplit('.',1)[1]]
            self.send((ROOT/'web'/asset).read_bytes(),mime+'; charset=utf-8')

        def do_POST(self):
            if self.path not in ('/api/analyze','/api/export'):
                return self.send('{"error":"Not found"}',status=404)
            origin=self.headers.get('Origin')
            if origin and origin not in (f'http://127.0.0.1:{port}',f'http://localhost:{port}'):
                return self.send('{"error":"Origin rejected"}',status=403)
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=2_000_000: raise ValueError('Project exceeds request size limit')
                payload=json.loads(self.rfile.read(length))
                project=payload['project']
                if project.get('schema_version')==2:
                    from .framework import analyze as analyze_general
                    from .framework_exports import archive as archive_general
                    result=analyze_general(project,bool(payload.get('uncertainty',True)))
                    zipper=archive_general
                else:
                    result=analyze(project,bool(payload.get('uncertainty',True)))
                    zipper=archive
                if self.path=='/api/export': return self.send(zipper(result),'application/zip')
                self.send(json.dumps(result,ensure_ascii=False))
            except (ValueError,KeyError,TypeError,RuntimeError) as e:
                self.send(json.dumps({'error':str(e)},ensure_ascii=False),status=400)
            except Exception as e:
                self.send(json.dumps({'error':type(e).__name__+': '+str(e)},ensure_ascii=False),status=500)

    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    print(f'PeopleComfort: http://127.0.0.1:{port}',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
