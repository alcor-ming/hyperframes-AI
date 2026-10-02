#!/usr/bin/env python3
"""Build original, brand-neutral phone and hinged laptop; no UI editing."""
import sys,json,math,argparse,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'common'))
import bpy
from bpy_utils import *

def phone(p,m):
    root=empty('phone',extras={'asset':'phone','unit':'meter','screen_aspect':p['screen_aspect'],'origin_rule':'chassis geometric center','front_axis':'+Z'})
    w,h,d,r=p['width'],p['height'],p['depth'],p['corner_radius']
    prism('chassis',w,h,d,r,(0,0,-.00035),m['hf_surface'],root,bevel=.00035)
    sw=p['screen_height']*p['screen_aspect'];sh=p['screen_height']
    ring('display_bezel',sw+.004,sh+.004,.007,.002,.00445,.00375,m['hf_muted'],root)
    screen('screen',sw,sh,.00415,m['hf_screen'],root,radius=.005)
    # Brand-neutral small centered circular camera, without a notch or logo.
    prism('camera_aperture',.0022,.0022,.0002,.0011,(0,sh/2-.005,.0043),m['hf_muted'],root,bevel=0)
    prism('camera_lens',.0014,.0014,.00021,.0007,(0,sh/2-.005,.00431),m['hf_screen'],root,bevel=0)
    box('power_key',(w/2+.00055,.025,-.00035),(.0011,.015,.0026),m['hf_muted'],root,.00035)
    box('volume_up',(-w/2-.00055,.031,-.00035),(.0011,.010,.0026),m['hf_muted'],root,.00035)
    box('volume_down',(-w/2-.00055,.016,-.00035),(.0011,.010,.0026),m['hf_muted'],root,.00035)
    # Rear single circular camera aperture remains generic.
    prism('rear_camera',.010,.010,.00032,.005,(0,.057,-.00443),m['hf_muted'],root,bevel=.00006)
    prism('rear_lens',.006,.006,.00035,.003,(0,.057,-.00451),m['hf_screen'],root,bevel=0)
    # Put the chassis geometric center exactly at the root, retaining all assembly clearances.
    for ob in root.children_recursive:
        if ob.type=='MESH':
            for vertex in ob.data.vertices:vertex.co.y-=.00035
    return root

def laptop(p,m):
    root=empty('laptop',extras={'asset':'laptop','unit':'meter','origin_rule':'base rear edge midpoint / hinge axis','front_axis':'+Z'})
    w,d,t=p['base_width'],p['base_depth'],p['base_thickness']
    prism('base',w,d,t,.008,(0,-t/2,d/2),m['hf_surface'],root,plane='xz',bevel=.0011)
    # Shallow inset keyboard tray; all top surfaces clear closed display by >= 3 mm.
    prism('keyboard_tray',w-.026,.085,.00055,.004,(0,.00025,.077),m['hf_muted'],root,plane='xz',bevel=.00018)
    for row in range(5):
        cols=14 if row<4 else 10
        for col in range(cols):
            kw=.017 if row<4 else (.056 if col==4 else .018)
            x=(col-(cols-1)/2)*(.020 if row<4 else .027)
            # Last row regular key spacing avoids merged keycaps.
            if row==4:kw=.021
            box(f'key_{row}_{col}',(x,.0009,.043+row*.014),(kw,.0014,.010),m['hf_surface'],root,.00065)
    prism('trackpad_border',.105,.062,.00035,.004,(0,.00018,.171),m['hf_muted'],root,plane='xz',bevel=.0001)
    prism('trackpad',.102,.059,.00036,.003,(0,.00034,.171),m['hf_surface'],root,plane='xz',bevel=.0001)
    # Two axis-aligned hinge barrels, centered exactly on the local X pivot.
    for x in (-.115,.115):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.0045,depth=.050,location=vec((x,0,0)),rotation=(0,math.pi/2,0))
        ob=bpy.context.object;ob.name='hinge_left' if x<0 else 'hinge_right';ob.parent=root;ob.data.materials.append(m['hf_muted']);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
        for f in ob.data.polygons:f.use_smooth=True
    angle=math.radians(p['lid_max_open_deg'])
    lid=empty('lid',root,{'lid_angle_range':[0,-angle],'angle_unit':'radians','closed_angle':0,'max_open_angle':-angle,'hinge_axis':'+X','screen_aspect':p['screen_aspect']})
    diag=p['screen_diagonal'];asp=p['screen_aspect'];sh=diag/math.sqrt(1+asp*asp);sw=sh*asp
    lh=sh+.020;lw=sw+.015;near=.007;cy=near+lh/2;bottom=p['closed_lid_bottom'];lt=p['lid_thickness']
    prism('lid_shell',lw,lh,lt,.007,(0,bottom+lt/2,cy),m['hf_surface'],lid,plane='xz',bevel=.0006)
    # Lower-facing bezel and inset screen. Shell is behind both; no light leaks.
    ring('lid_bezel',sw+.004,sh+.004,.003,.002,bottom-.00055,bottom+.00005,m['hf_muted'],lid,center=(0,cy),plane='xz')
    screen('screen',sw,sh,bottom-.00025,m['hf_screen'],lid,center=(0,cy),plane='xz')
    lid.rotation_euler.x=-math.radians(p['lid_default_open_deg'])
    bpy.context.view_layer.update()
    return root

def main():
    a=argparse.ArgumentParser();a.add_argument('--params',required=True);a.add_argument('--out',required=True);a.add_argument('--no-previews',action='store_true');args=a.parse_args(sys.argv[sys.argv.index('--')+1:])
    p=json.loads(Path(args.params).read_text());out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    allmetrics={'blender':bpy.app.version_string,'seed':p['seed'],'models':{}}
    for name,build in [('phone',phone),('laptop',laptop)]:
        reset();m=materials();root=build(p[name],m);bpy.context.view_layer.update();objects=[root]+list(root.children_recursive)
        export(out/(name+'.glb'),objects)
        stats=metrics(root);stats['bytes']=(out/(name+'.glb')).stat().st_size;stats['sha256']=hashlib.sha256((out/(name+'.glb')).read_bytes()).hexdigest();stats['screen_aspect']=p[name]['screen_aspect'];allmetrics['models'][name]=stats
        if not args.no_previews:render_views(root,out.parent/'previews'/name,p['preview_resolution'],p['preview_samples'])
    (out/'metrics.json').write_text(json.dumps(allmetrics,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
