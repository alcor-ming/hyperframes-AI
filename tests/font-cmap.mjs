import assert from 'node:assert/strict';
import {deflateSync,brotliCompressSync} from 'node:zlib';
import {coveredCharacters} from '../.studio/font_cmap.mjs';
// One Unicode format-12 group deliberately contains only A/B, no C.
const cmap=Buffer.alloc(40); cmap.writeUInt16BE(1,2);cmap.writeUInt16BE(3,4);cmap.writeUInt16BE(10,6);cmap.writeUInt32BE(12,8);
cmap.writeUInt16BE(12,12);cmap.writeUInt32BE(28,16);cmap.writeUInt32BE(1,24);cmap.writeUInt32BE(65,28);cmap.writeUInt32BE(66,32);cmap.writeUInt32BE(1,36);
const sfnt=Buffer.alloc(28);sfnt.writeUInt32BE(0x10000);sfnt.writeUInt16BE(1,4);sfnt.write('cmap',12);sfnt.writeUInt32BE(28,20);sfnt.writeUInt32BE(cmap.length,24);
const compressed=deflateSync(cmap), woff=Buffer.alloc(64);woff.write('wOFF');woff.writeUInt16BE(1,12);woff.write('cmap',44);woff.writeUInt32BE(64,48);woff.writeUInt32BE(compressed.length,52);woff.writeUInt32BE(cmap.length,56);
const brotli=brotliCompressSync(cmap), woff2=Buffer.alloc(50);woff2.write('wOF2');woff2.writeUInt16BE(1,12);woff2.writeUInt32BE(brotli.length,20);woff2[48]=0;woff2[49]=cmap.length;
for(const data of [Buffer.concat([sfnt,cmap]),Buffer.concat([woff,compressed]),Buffer.concat([woff2,brotli])])
  assert.deepEqual([...coveredCharacters(data,new Set('ABC'))],['A','B']);
assert.throws(()=>coveredCharacters(Buffer.alloc(5),new Set('A')));
console.log('SFNT/WOFF/WOFF2 Unicode coverage and malformed font checks passed');
