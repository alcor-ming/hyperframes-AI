// Parse untrusted source as data; never resolve modules relative to its directory.
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');

function dependency(name) {
  const root = path.resolve(__dirname, '..');
  const runtime = path.join(root, 'runtime/npm/package.json');
  const bases = process.platform !== 'win32' && process.env.HYPERFRAMES_DEPENDENCY_MODULE_ROOT
      ? [path.join(process.env.HYPERFRAMES_DEPENDENCY_MODULE_ROOT, 'package.json')]
    : fs.existsSync(runtime) ? [runtime]
      : [path.join(__dirname, '.runtime/dependency-parser/package.json'),
        path.join(__dirname, 'package.json'), path.join(__dirname, 'remotion/package.json')];
  for (const base of bases) {
    try { return createRequire(base)(path.join(path.dirname(base), 'node_modules', name)); }
    catch (error) { if (error.code !== 'MODULE_NOT_FOUND') throw error; }
  }
  throw new Error(`Dependency scanner requires installed ${name} in the controlled tool runtime`);
}

function javascript(text, mode) {
  const acorn = dependency('acorn');
  const options = { ecmaVersion: 'latest', sourceType: mode === 'auto' ? 'module' : mode,
    allowHashBang: true, allowReturnOutsideFunction: mode === 'handler' };
  if (mode === 'handler') options.sourceType = 'script';
  let ast;
  try { ast = acorn.parse(text, options); }
  catch (error) {
    if (mode !== 'auto') throw error;
    ast = acorn.parse(text, { ...options, sourceType: 'script' });
  }
  const refs = [], dynamic = [];
  const literal = node => node?.type === 'Literal' && typeof node.value === 'string' ? node.value
    : node?.type === 'TemplateLiteral' && node.expressions.length === 0 ? node.quasis[0].value.cooked : null;
  const reference = (node, kind) => {
    const value = literal(node);
    if (value === null) dynamic.push(kind);
    else refs.push({ value, kind });
  };
  const pending = [ast];
  while (pending.length) {
    const node = pending.pop();
    if (!node || typeof node !== 'object') continue;
    if (node.type === 'ImportDeclaration' || node.type === 'ExportNamedDeclaration' || node.type === 'ExportAllDeclaration') {
      if (node.source) reference(node.source, 'import');
    } else if (node.type === 'ImportExpression') reference(node.source, 'import');
    else if (node.type === 'CallExpression') {
      const callee = node.callee;
      const fetch = callee.type === 'Identifier' && callee.name === 'fetch'
        || callee.type === 'MemberExpression' && callee.object.type === 'Identifier'
          && ['window', 'globalThis', 'self'].includes(callee.object.name)
          && (callee.computed ? literal(callee.property) === 'fetch' : callee.property.name === 'fetch');
      if (fetch) reference(node.arguments[0], 'fetch');
    }
    for (const value of Object.values(node)) {
      if (Array.isArray(value)) { for (const child of value) pending.push(child); }
      else if (value && typeof value === 'object' && value.type) pending.push(value);
    }
  }
  return { refs, dynamic };
}

async function css(text) {
  const refs = [];
  await dependency('esbuild').build({ stdin: { contents: text, loader: 'css' },
    bundle: true, write: false, logLevel: 'silent', plugins: [{ name: 'collect-references', setup(build) {
      build.onResolve({ filter: /.*/ }, args => {
        refs.push({ value: args.path, kind: args.kind === 'import-rule' ? 'executable' : 'css' });
        return { path: args.path, external: true };
      });
    } }] });
  return { refs, dynamic: [] };
}

(async () => {
  const units = JSON.parse(fs.readFileSync(0, 'utf8'));
  const result = { refs: [], dynamic: [] };
  for (const unit of units) {
    const scanned = unit.kind === 'css' ? await css(unit.text) : javascript(unit.text, unit.mode);
    result.refs.push(...scanned.refs);
    result.dynamic.push(...scanned.dynamic);
  }
  process.stdout.write(JSON.stringify(result));
})().catch(error => { process.stderr.write(error.message); process.exitCode = 1; });
