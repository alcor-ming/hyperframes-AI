"""Build disposable fixture-only frozen appearance inputs. Never packs/accepts assets."""
import argparse, hashlib, json, shutil
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--font',type=Path,required=True,help='Local licensed font supporting your labels (TTF/OTF/WOFF2)')
p.add_argument('--font-license',type=Path,required=True)
a=p.parse_args()
base=Path(__file__).resolve().parent
repo=base.parent.parent
for id in ['graph-grow','token-stream']:
 root=base/id/'fixture/generated';root.mkdir(parents=True,exist_ok=True)
 for name in ['broll.js','appearance.js']:
  shutil.copyfile(repo/'.studio/runtime'/name,root/name)
 for theme,colors in [('light',{'text':'#37464b','accent':'#457f91','muted':'#a0b0b4','bg':'#edf1ef'}),('dark',{'text':'#dbe7e6','accent':'#92c3c8','muted':'#61797d','bg':'#1f292d'})]:
  for ratio in ['16-9','9-16']:
   project=root/(theme+'-'+ratio);vendor=project/'theme';vendor.mkdir(parents=True,exist_ok=True)
   font='font'+a.font.suffix;shutil.copyfile(a.font,vendor/font);shutil.copyfile(a.font_license,vendor/'LICENSE.txt')
   metadata={'schema_version':2,'contract_version':1,'id':'fixture-theme','version':1,'kind':'theme','entry':'theme.json','dependencies':[font,'LICENSE.txt'],'parameters':{},'compatibility':{}}
   payload={'tokens':{'colors':{k:v for k,v in colors.items()if k!='bg'},'surface':{'color':colors['bg']},'typography':{'body':'FixtureFont'}},'fonts':[{'family':'FixtureFont','path':font,'license':'LICENSE.txt','weight':400,'style':'normal'}]}
   (vendor/'asset.json').write_text(json.dumps(metadata));(vendor/'theme.json').write_text(json.dumps(payload))
   digest=hashlib.sha256(b''.join(x.read_bytes()for x in sorted(vendor.iterdir()))).hexdigest()
   asset={'ref':'fixture-theme@v1','kind':'theme','package_sha256':digest,'vendor_path':'theme'}
   lock={'schema_version':1,'contract_version':1,'resolver_version':1,'mode':'showcase','ratio':ratio.replace('-',':'),'assets':[asset],'selection':{'theme':{'ref':asset['ref'],'package_sha256':digest},'background':None,'motion':{}},'parameters':{'theme':{},'background':{},'motion':{}}}
   (project/'appearance-lock.json').write_text(json.dumps(lock))
print('Prepared fixture-only appearance inputs; no assets packed or accepted.')
