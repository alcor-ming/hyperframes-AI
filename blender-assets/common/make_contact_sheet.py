#!/usr/bin/env python3
"""Combine actual CPU PNGs. Requires Pillow; labels use the system DejaVu Sans."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import argparse
p=argparse.ArgumentParser();p.add_argument('--previews',required=True);a=p.parse_args();root=Path(a.previews)
try:f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',25)
except OSError:f=ImageFont.load_default(size=25)
canvas=Image.new('RGB',(2048,1152),'#eff1f4');d=ImageDraw.Draw(canvas)
for row,asset in enumerate(['phone','laptop']):
 for col,view in enumerate(['front','three-quarter','back','top']):
  im=Image.open(root/asset/(view+'.png')).convert('RGBA');im.thumbnail((512,512));x=col*512;y=row*576
  canvas.paste(im,(x+(512-im.width)//2,y+52+(512-im.height)//2),im);d.text((x+18,y+14),f'{asset.upper()} | {view}',font=f,fill='#29333e')
canvas.save(root/'T1-device-four-views.png')
