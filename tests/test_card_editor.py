"""Synthetic loopback editor checks; no running Studio or production files."""
import hashlib
import http.client
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.studio'))
from card_build import replace_card
from card_editor import make_server


PLAN = ('---\n{"plan_format":"3.5.2"}\n---\n## S01\n```card C1 · P001\n'
        'preset: F01\narea: full\n- Before @hello\n```\n')


class CardEditorTest(unittest.TestCase):
    def test_edit_security_and_stale_write(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = Path(directory) / 'ANIMATION_PLAN.md'
            plan.write_text(PLAN)
            calls = []

            def save(data):
                calls.append(data)
                plan.write_text(replace_card(plan.read_text(), data['card'], data['body']))

            with make_server(plan, directory, 'http://127.0.0.1:3101/#project/test', save) as server:
                thread = threading.Thread(target=server.serve_forever)
                thread.start()
                origin = f'http://127.0.0.1:{server.server_port}'
                token = urlsplit(server.url).fragment

                def request(method, path, payload=None, headers=None):
                    connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
                    auth = {'X-Card-Token': token, 'Origin': origin, 'Content-Type': 'application/json'}
                    auth.update(headers or {})
                    body = json.dumps(payload) if payload is not None else None
                    connection.request(method, path, body, auth)
                    response = connection.getresponse()
                    result = response.read()
                    status = response.status
                    connection.close()
                    return status, result

                try:
                    code, page = request('GET', '/')
                    self.assertEqual(200, code)
                    self.assertNotIn(token.encode(), page)
                    code, raw = request('GET', '/cards')
                    state = json.loads(raw)
                    self.assertEqual(200, code)
                    self.assertEqual(hashlib.sha256(plan.read_bytes()).hexdigest(), state['plan_sha256'])
                    payload = {'card': 'C1', 'body': 'preset: F01\narea: full\n- After @hello',
                               'plan_sha256': state['plan_sha256']}
                    for method, path, headers, expected in [
                        ('GET', '/cards', {'X-Card-Token': 'wrong'}, 403),
                        ('GET', '/cards', {'Host': 'evil.test'}, 403),
                        ('POST', '/save', {'Origin': 'http://evil.test'}, 403),
                        ('POST', '/save', {'Content-Type': 'text/plain'}, 415),
                        ('GET', '/../ANIMATION_PLAN.md', {}, 404),
                        ('POST', '/arbitrary', {}, 404),
                    ]:
                        self.assertEqual(expected, request(method, path, payload if method == 'POST' else None, headers)[0])
                    self.assertEqual(413, request('POST', '/save', {**payload, 'body': 'x' * 65536})[0])
                    self.assertEqual(400, request('POST', '/save', {**payload, 'card': 'unknown'})[0])
                    self.assertEqual([], calls)
                    code, raw = request('POST', '/save', payload)
                    self.assertEqual(200, code)
                    self.assertIn('After', plan.read_text())
                    self.assertNotEqual(state['plan_sha256'], json.loads(raw)['plan_sha256'])
                    self.assertEqual(409, request('POST', '/save', payload)[0])
                    self.assertEqual(1, len(calls))
                    latest = json.loads(request('GET', '/cards')[1])
                    self.assertEqual(400, request('POST', '/save', {**payload, 'body': 'invalid', 'plan_sha256': latest['plan_sha256']})[0])
                    self.assertIn('After', plan.read_text())
                finally:
                    server.shutdown()
                    thread.join(timeout=5)

    def test_remote_studio_is_rejected(self):
        for url in ('https://example.com/', 'http://evil.test:3101/', 'http://localhost/', 'http://u:p@localhost:3101/'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                make_server('unused', 'unused', url, lambda _: None)


if __name__ == '__main__':
    unittest.main()
