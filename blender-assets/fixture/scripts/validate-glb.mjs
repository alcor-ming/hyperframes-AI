import { readFile, writeFile, mkdir, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import validator from 'gltf-validator';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const outIndex = args.indexOf('--out');
const reportDir = path.resolve(outIndex < 0 ? path.join(root, 'reports', 'validator') : args.splice(outIndex, 2)[1]);
const strict = args.includes('--strict');
async function collect(target) {
  if (target.toLowerCase().endsWith('.glb')) return [target];
  const entries = await readdir(target, { withFileTypes: true });
  return (await Promise.all(entries.map(e => e.isDirectory() ? collect(path.join(target, e.name)) : e.name.toLowerCase().endsWith('.glb') ? [path.join(target, e.name)] : []))).flat();
}
const targets = args.filter(a => a !== '--strict');
if (!targets.length) { console.error('Usage: npm run validate -- ../T1-device-mockups/out [more files/directories] [--out reports/path] [--strict]'); process.exit(2); }
await mkdir(reportDir, { recursive: true });
const summary = [];
for (const filename of (await Promise.all(targets.map(t => collect(path.resolve(t))))).flat().sort()) {
  const bytes = await readFile(filename);
  const report = await validator.validateBytes(new Uint8Array(bytes), { uri: path.basename(filename), format: 'glb', maxIssues: 0,
    externalResourceFunction: async uri => { throw new Error(`Self-contained GLB required; external resource rejected: ${uri}`); }
  });
  const id = `${path.basename(filename, '.glb')}-${createHash('sha256').update(bytes).digest('hex').slice(0, 12)}`;
  await writeFile(path.join(reportDir, `${id}.validator.json`), JSON.stringify(report, null, 2) + '\n');
  const result = { file: path.relative(root, filename), bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex'), validatorVersion: validator.version(), errors: report.issues.numErrors, warnings: report.issues.numWarnings, infos: report.issues.numInfos, report: `${id}.validator.json` };
  summary.push(result); console.log(`${result.errors ? 'FAIL' : 'PASS'} ${result.file}: ${result.errors} errors, ${result.warnings} warnings`);
}
await writeFile(path.join(reportDir, 'summary.json'), JSON.stringify(summary, null, 2) + '\n');
if (!summary.length || summary.some(r => r.errors || (strict && r.warnings))) process.exitCode = 1;
