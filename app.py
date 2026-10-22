import json, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROLE = sys.argv[1]
HOST = sys.argv[2] if len(sys.argv) > 2 else "0.0.0.0"   # ecoute sur sa seule adresse

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            b = b'{"ok":true}'
        else:
            data = {"application": ROLE, "path": self.path, "server_time": round(time.time(), 3),
                    "message": "Reponse du service local au laboratoire."}
            b = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers(); self.wfile.write(b)
    def log_message(self, format, *args):
        if not self.path.startswith("/health"):
            print(f"[{ROLE}] {self.client_address[0]} {format % args}", flush=True)

print(f"{ROLE} listening on {HOST}:8000", flush=True)
ThreadingHTTPServer((HOST, 8000), Handler).serve_forever()
