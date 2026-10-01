// Parse author code as data, without evaluating callbacks or resolving author imports.
const fs = require('node:fs');
const { dependency } = require('./dependency_scan.cjs');

function scan(unit) {
  const acorn = dependency('acorn');
  const options = { ecmaVersion: 'latest', sourceType: unit.mode === 'module' ? 'module' : 'script',
    allowHashBang: true, allowReturnOutsideFunction: unit.mode === 'handler', locations: true };
  let ast;
  try { ast = acorn.parse(unit.text, options); }
  catch (error) {
    if (unit.mode !== 'auto') throw error;
    ast = acorn.parse(unit.text, { ...options, sourceType: 'module' });
  }
  const literal = node => node?.type === 'Literal' ? node.value
    : node?.type === 'TemplateLiteral' && !node.expressions.length ? node.quasis[0].value.cooked : null;
  const name = node => node?.computed ? literal(node.key || node.property)
    : (node?.key || node?.property)?.name || literal(node?.key || node?.property);
  const findings = [], pending = [ast];
  while (pending.length) {
    const node = pending.pop();
    if (!node || typeof node !== 'object') continue;
    const property = node.type === 'Property' && name(node) === 'onUpdate';
    const call = node.type === 'CallExpression' && node.callee.type === 'MemberExpression'
      && name(node.callee) === 'eventCallback' && literal(node.arguments[0]) === 'onUpdate'
      && node.arguments.length > 1;
    const callback = property ? node.value : call ? node.arguments[1] : null;
    if (callback && !(callback.type === 'Literal' && callback.value === null)) {
      findings.push({ kind: 'on_update_seek_risk', file: unit.file, unit: unit.unit,
        line: node.loc.start.line, detail: 'onUpdate callback requires seek-safe state review; state writes are not proven' });
    }
    for (const value of Object.values(node)) {
      if (Array.isArray(value)) pending.push(...value);
      else if (value && typeof value === 'object' && value.type) pending.push(value);
    }
  }
  return findings;
}

try {
  const units = JSON.parse(fs.readFileSync(0, 'utf8'));
  const findings = [];
  for (const unit of units) {
    try { findings.push(...scan(unit)); }
    catch (error) { findings.push({ kind: 'seek_scan_unverified', file: unit.file, unit: unit.unit, detail: error.message }); }
  }
  process.stdout.write(JSON.stringify(findings));
} catch (error) { process.stderr.write(error.message); process.exitCode = 1; }
