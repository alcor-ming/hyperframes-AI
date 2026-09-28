"""Loopback-only Plan editor accompanying the unmodified official Studio."""
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import secrets
import threading
from urllib.parse import urlsplit

from card_build import card_bodies


def make_server(plan_path, project, studio_url, save_callback, port=0):
    plan_path = Path(plan_path)
    studio = urlsplit(studio_url)
    if (studio.scheme != 'http' or studio.hostname not in {'127.0.0.1', 'localhost', '::1'}
            or studio.username or studio.password or not studio.port):
        raise ValueError('Studio URL must be an HTTP loopback URL with a port')
    token = secrets.token_urlsafe(32)
    lock = threading.Lock()
    page = Path(__file__).with_name('card-editor.html').read_bytes()

    def state():
        data = plan_path.read_bytes()
        return {'cards': card_bodies(data.decode('utf-8')), 'plan_sha256': hashlib.sha256(data).hexdigest(),
                'studio_url': studio_url}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, value, content_type='application/json; charset=utf-8'):
            data = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'unsafe-inline'; "
                             "style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; "
                             "base-uri 'none'; form-action 'none'; frame-src " + studio.scheme + '://' + studio.netloc)
            self.end_headers()
            self.wfile.write(data)

        def authorized(self, *, mutation=False, capability=True):
            origin = f'http://127.0.0.1:{self.server.server_port}'
            if (self.headers.get_all('Host') != [origin.removeprefix('http://')]
                    or len(self.headers.get_all('Origin', [])) > 1
                    or self.headers.get('Origin') not in ({origin} if mutation else {None, origin})):
                self.reply(403, {'error': 'Invalid Host or Origin'})
                return False
            supplied = self.headers.get_all('X-Card-Token', [])
            if capability and (len(supplied) != 1 or not secrets.compare_digest(supplied[0].encode(), token.encode())):
                self.reply(403, {'error': 'Invalid session token'})
                return False
            return True

        def do_GET(self):
            if not self.authorized(capability=self.path != '/'):
                return
            if self.path == '/':
                self.reply(200, page, 'text/html; charset=utf-8')
            elif self.path == '/cards':
                with lock:
                    self.reply(200, state())
            else:
                self.reply(404, {'error': 'Not found'})

        def do_POST(self):
            if not self.authorized(mutation=True):
                return
            if self.path != '/save':
                self.reply(404, {'error': 'Not found'})
                return
            if (len(self.headers.get_all('Content-Type', [])) != 1
                    or self.headers.get_content_type() != 'application/json'
                    or self.headers.get('Transfer-Encoding')
                    or len(self.headers.get_all('Content-Length', [])) != 1):
                self.reply(415, {'error': 'Expected length-delimited JSON'})
                return
            length = self.headers.get('Content-Length', '')
            if not length.isdecimal() or len(length) > 5 or not 0 < int(length) <= 65536:
                self.reply(413, {'error': 'Request exceeds 64 KiB'})
                return
            try:
                self.connection.settimeout(10)
                data = json.loads(self.rfile.read(int(length)))
                if (not isinstance(data, dict) or set(data) != {'card', 'body', 'plan_sha256'}
                        or not isinstance(data['card'], str) or not isinstance(data['body'], str)
                        or not isinstance(data['plan_sha256'], str)
                        or not re.fullmatch(r'[0-9a-f]{64}', data['plan_sha256'])):
                    raise ValueError('Expected card, body and plan_sha256')
                with lock:
                    current = state()
                    if data['plan_sha256'] != current['plan_sha256']:
                        self.reply(409, {'error': 'Plan changed; reload before saving'})
                        return
                    if data['card'] not in {card['id'] for card in current['cards']}:
                        raise ValueError('Unknown Plan card')
                    save_callback(data)
                    self.reply(200, state())
            except (ValueError, UnicodeError) as error:
                self.reply(400, {'error': str(error)})
            except Exception:
                self.reply(500, {'error': 'Card save failed; Plan was not confirmed saved'})

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.url = f'http://127.0.0.1:{server.server_port}/#{token}'
    return server


def serve(plan_path, project, studio_url, save_callback, port=0):
    with make_server(plan_path, project, studio_url, save_callback, port) as server:
        print(server.url, flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
