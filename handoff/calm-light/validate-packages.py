"""Validate each real module closure in a temporary directory, without acceptance."""
from pathlib import Path
import sys,tempfile,json
base=Path(__file__).resolve().parent
sys.path.insert(0,str(base.parent.parent/'.studio'))
from asset_contract import freeze_source
with tempfile.TemporaryDirectory(prefix='calm-light-validation-')as temp:
 for id in ['graph-grow','token-stream']:
  result=freeze_source(base/id,Path(temp)/id)
  print(json.dumps({'id':id,'package_sha256':result['package_sha256'],'files':len(result['files']),'status':'valid temporary freeze; not accepted'}))
