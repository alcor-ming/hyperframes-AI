// Read Unicode cmap tables using only Node's standard compression library.
import {inflateSync, brotliDecompressSync} from 'node:zlib';
const tags = 'cmap head hhea hmtx maxp name OS/2 post cvt_ fpgm glyf loca prep CFF_ VORG EBDT EBLC gasp hdmx kern LTSH PCLT VDMX vhea vmtx BASE GDEF GPOS GSUB EBSC JSTF MATH CBDT CBLC COLR CPAL SVG_ sbix acnt avar bdat bloc bsln cvar fdsc feat fmtx fvar gvar hsty just lcar mort morx opbd prop trak Zapf Silf Glat Gloc Feat Sill'.split(' ').map(x => x.replace('_',' '));
function cmap(data) {
  const signature = data.toString('ascii',0,4);
  if (signature === 'wOF2') {
    let at = 48, offset = 0, selected;
    const base128 = () => {
      let result = 0;
      for (let i=0;i<5;i++) { const value=data[at++]; if (value===undefined || i===0 && value===128 || result>0x1ffffff) throw Error('Invalid WOFF2 length'); result=result*128+(value&127); if (!(value&128)) return result; }
      throw Error('Invalid WOFF2 length');
    };
    for (let i=0;i<data.readUInt16BE(12);i++) {
      const flags=data[at++], tag=(flags&63)===63 ? data.toString('ascii',at,at+=4) : tags[flags&63];
      const length=base128(), version=flags>>6;
      const transformed=['glyf','loca'].includes(tag) ? version!==3 : version!==0;
      const size=transformed ? base128() : length;
      if(tag==='cmap') { if(transformed) throw Error('Transformed cmap is unsupported'); selected={offset,size}; }
      offset+=size;
    }
    if(!selected) throw Error('Font has no cmap');
    const stream=brotliDecompressSync(data.subarray(at,at+data.readUInt32BE(20)));
    return stream.subarray(selected.offset,selected.offset+selected.size);
  }
  const woff=signature==='wOFF', count=data.readUInt16BE(woff?12:4);
  for(let i=0;i<count;i++) {
    const at=(woff?44:12)+i*(woff?20:16);
    if(data.toString('ascii',at,at+4)!=='cmap') continue;
    const offset=data.readUInt32BE(at+(woff?4:8)), length=data.readUInt32BE(at+(woff?8:12));
    const table=data.subarray(offset,offset+length);
    return woff && length<data.readUInt32BE(at+12) ? inflateSync(table) : table;
  }
  throw Error('Font has no cmap');
}
export function coveredCharacters(data, characters) {
  const table=cmap(data), covered=new Set();
  for(let i=0;i<table.readUInt16BE(2);i++) {
    const at=4+i*8, platform=table.readUInt16BE(at), encoding=table.readUInt16BE(at+2);
    if(platform!==0 && !(platform===3 && [1,10].includes(encoding))) continue;
    const sub=table.subarray(table.readUInt32BE(at+4)), format=sub.readUInt16BE(0);
    for(const character of characters) {
      const cp=character.codePointAt(0); let glyph=0;
      if(format===12 || format===13) {
        for(let group=0;group<sub.readUInt32BE(12);group++) {
          const pos=16+group*12, first=sub.readUInt32BE(pos), last=sub.readUInt32BE(pos+4);
          if(cp<first) break;
          if(cp<=last) { glyph=sub.readUInt32BE(pos+8)+(format===12?cp-first:0); break; }
        }
      } else if(format===4 && cp<=0xffff) {
        const n=sub.readUInt16BE(6)/2;
        for(let segment=0;segment<n;segment++) {
          if(cp>sub.readUInt16BE(14+segment*2)) continue;
          const first=sub.readUInt16BE(16+n*2+segment*2); if(cp<first) break;
          const delta=sub.readInt16BE(16+n*4+segment*2), pos=16+n*6+segment*2, range=sub.readUInt16BE(pos);
          glyph=range ? sub.readUInt16BE(pos+range+(cp-first)*2) : cp;
          if(!range || glyph) glyph=(glyph+delta)&0xffff;
          break;
        }
      }
      if(glyph) covered.add(character);
    }
  }
  return covered;
}
export const actualCharacters = text => new Set([...text.normalize('NFC')].filter(c => !/[\p{Cc}\p{Cf}\p{Z}]/u.test(c)));
