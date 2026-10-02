import http from 'node:http';
import { readFile, realpath } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const fixtureRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const assetsRoot = path.resolve(fixtureRoot, '..');
const types = { '.html': 'text/html', '.mjs': 'application/javascript', '.js': 'application/javascript', '.json': 'application/json', '.css': 'text/css', '.glb': 'model/gltf-binary', '.png': 'image/png', '.woff2': 'font/woff2' };
export function startServer({ host = '127.0.0.1', port = 4173 } = {}) {
  const server = http.createServer(async (req, res) => {
    try {
      const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
      const isAsset = pathname.startsWith('/assets/');
      const root = isAsset ? assetsRoot : fixtureRoot;
      const local = pathname === '/' ? 'index.html' : isAsset ? pathname.slice(8) : pathname.slice(1);
      const filename = await realpath(path.resolve(root, local));
      if (!filename.startsWith(root + path.sep)) { res.writeHead(403).end('Outside fixture root'); return; }
      const bytes = await readFile(filename);
      res.writeHead(200, { 'Content-Type': types[path.extname(filename)] ?? 'application/octet-stream', 'Cache-Control': 'no-store' }); res.end(bytes);
    } catch (error) { res.writeHead(error.code === 'ENOENT' ? 404 : 500).end(error.message); }
  });
  return new Promise((resolve, reject) => { server.once('error', reject); server.listen(port, host, () => resolve(server)); });
}
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const server = await startServer({ host: process.env.HOST ?? '127.0.0.1', port: Number(process.env.PORT ?? 4173) });
  console.log(`Fixture: http://${server.address().address}:${server.address().port}`);
}
