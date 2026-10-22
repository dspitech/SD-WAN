import json, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"   # ecoute sur le seul reseau de controle
POLICY_FILE = '/lab/policy/policy.json'

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/policy":
            self.send_error(404); return
        try:
            # utf-8-sig : tolere un BOM ajoute par certains editeurs Windows
            with open(POLICY_FILE, encoding='utf-8-sig') as f: value = json.load(f)
            payload = json.dumps(value, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers(); self.wfile.write(payload)
        except Exception as exc:
            self.send_error(500, str(exc).replace('\n', ' '))
    def log_message(self, format, *args): pass

print(f'Meridian policy manager at {HOST}:9000', flush=True)
ThreadingHTTPServer((HOST, 9000), Handler).serve_forever()
