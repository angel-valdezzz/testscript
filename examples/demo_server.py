"""Deterministic local UI and API for TestScript examples (not a production app)."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from itertools import count
from threading import Lock

PAGE = '''<!doctype html><html lang="en"><meta charset="utf-8"><title>TestScript Demo</title>
<style>body{background:#0b1016;color:#e9f0f6;font:18px system-ui;padding:80px;max-width:700px;margin:auto}
input,select,button{display:block;padding:12px;margin:14px 0;background:#16232e;color:inherit;border:1px solid #547083;border-radius:6px}
button{background:#70e3c4;color:#0b1016}input[type=checkbox]{display:inline}</style>
<h1>TestScript / Local Lab</h1><form><label for="username">Name</label><input id="username" required>
<label for="role">Role</label><select id="role"><option value="tester">Tester</option><option value="developer">Developer</option></select>
<label><input id="remember" type="checkbox"> Remember</label><button type="submit">Sign in</button></form><h2 id="welcome" hidden></h2>
<script>document.querySelector('form').addEventListener('submit',e=>{e.preventDefault();const h=document.querySelector('#welcome');
h.textContent='Welcome, '+document.querySelector('#username').value;h.hidden=false;});</script></html>'''
USERS, IDS, LOCK = {}, count(1), Lock()


class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):
        if self.path == '/':
            self.send(200, PAGE, 'text/html; charset=utf-8')
            return
        if self.path.startswith('/users/'):
            with LOCK:
                user = USERS.get(self.path.split('/')[-1])
            self.send(200 if user else 404, json.dumps(user or {'error': 'User not found'}))
            return
        self.send(404, json.dumps({'error': 'Not found'}))

    def do_POST(self):
        if self.path != '/users':
            self.send(404, json.dumps({'error': 'Not found'}))
            return
        try:
            user = json.loads(self.rfile.read(int(self.headers.get('Content-Length', '0'))))
            if not isinstance(user, dict) or not isinstance(user.get('name'), str):
                raise ValueError('name must be a string')
        except (ValueError, TypeError):
            self.send(400, json.dumps({'error': 'Invalid JSON user'}))
            return
        with LOCK:
            user['id'] = str(next(IDS))
            USERS[user['id']] = user
        self.send(201, json.dumps(user))

    def log_message(self, *_):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'TestScript local lab: http://127.0.0.1:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
