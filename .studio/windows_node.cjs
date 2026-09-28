'use strict';

if (process.platform === 'win32') {
  const path = require('node:path');
  const npm = path.resolve(__dirname, '../runtime/npm/node_modules');
  const koffi = require(path.join(npm, 'koffi'));
  // Keep the exact packaged DLL loaded even when PreferSystem32Images is enabled.
  module.exports = koffi.load(path.join(npm, 'onnxruntime-node/bin/napi-v3/win32', process.arch, 'onnxruntime.dll'));
}
