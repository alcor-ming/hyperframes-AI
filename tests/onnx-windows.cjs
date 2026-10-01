'use strict';

const assert = require('node:assert/strict');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
assert.equal(process.platform, 'win32', 'Run with the packaged native Windows runtime');
const root = path.resolve(process.argv[2]);
const npm = path.join(root, 'runtime/npm/node_modules');
const dll = path.join(npm, 'onnxruntime-node/bin/napi-v3/win32/x64/onnxruntime.dll');
const loadedOrt = () => process.report.getReport().sharedObjects
  .filter(p => path.basename(p).toLowerCase() === 'onnxruntime.dll');
global.gc?.();
assert.deepEqual(loadedOrt().map(p => path.resolve(p).toLowerCase()), [dll.toLowerCase()]);
const koffi = require(path.join(npm, 'koffi'));
const kernel = koffi.load('kernel32.dll');
const policy = [0];
assert.equal(kernel.func('bool __stdcall GetProcessMitigationPolicy(void *process, int policy, _Out_ uint32_t *buffer, size_t size)')(
  kernel.func('void * __stdcall GetCurrentProcess()')(), 10, policy, 4), true);

// ONNX v1.17.0 backend/test/data/node/test_identity/model.onnx (Apache-2.0).
const model = Buffer.from('CAoSDGJhY2tlbmQtdGVzdDpbChAKAXgSAXkiCElkZW50aXR5Eg10ZXN0X2lkZW50aXR5WhsKAXgSFgoUCAESEAoCCAEKAggBCgIIAgoCCAJiGwoBeRIWChQIARIQCgIIAQoCCAEKAggCCgIIAkIECgAQFQ==', 'base64');
(async () => {
  const ort = require(path.join(npm, 'onnxruntime-node'));
  const session = await ort.InferenceSession.create(model, { executionProviders: ['cpu'] });
  try {
    const output = await session.run({ x: new ort.Tensor('float32', Float32Array.from([1, 2, 3, 4]), [1, 1, 2, 2]) });
    assert.deepEqual(Array.from(output.y.data), [1, 2, 3, 4]);
  } finally {
    await session.release();
  }
  const child = spawnSync(process.execPath, ['-e', `require(${JSON.stringify(path.join(npm, 'onnxruntime-node'))});`], { encoding: 'utf8' });
  assert.equal(child.status, 0, child.stderr);
  console.log(JSON.stringify({ platform: process.platform, loadedOrt: loadedOrt(), imageLoadPolicy: policy[0],
    inference: [1, 2, 3, 4], child: child.status, nodeOptions: process.env.NODE_OPTIONS }));
})().catch(error => { console.error(error); process.exitCode = 1; });
