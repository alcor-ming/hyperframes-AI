#!/usr/bin/env python3
"""Compare two independent Blender exports byte-for-byte, recording exact hashes."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('first');p.add_argument('second');p.add_argument('--report',required=True);a=p.parse_args();files=[]
for f in sorted(Path(a.first).glob('*.glb')):
 g=Path(a.second)/f.name;h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 files.append({'file':f.name,'first_sha256':h(f),'second_sha256':h(g),'identical':f.read_bytes()==g.read_bytes(),'bytes':f.stat().st_size})
r={'passed':bool(files) and all(x['identical'] for x in files),'files':files};Path(a.report).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
raise SystemExit(0 if r['passed'] else 1)
