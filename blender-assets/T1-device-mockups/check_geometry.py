"""Checks source geometry, UV bounds, exported-scale setup, and full hinge sweep."""
import sys,json,math,importlib.util,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import build
from bpy_utils import *
from mathutils.bvhtree import BVHTree

a=argparse.ArgumentParser();a.add_argument('--params',default=str(Path(__file__).with_name('params.json')));a.add_argument('--out',default=str(Path(__file__).parent/'out'/'geometry-check.json'));args=a.parse_args(sys.argv[sys.argv.index('--')+1:]);p=json.loads(Path(args.params).read_text());report={};errors=[]
for name,fn in [('phone',build.phone),('laptop',build.laptop)]:
    reset();root=fn(p[name],materials());bpy.context.view_layer.update();stats=metrics(root)
    for meshname,s in stats['meshes'].items():
        for k in ('zero_area_faces','duplicate_vertices'):
            if s[k]:errors.append(f'{name}/{meshname}: {k}={s[k]}')
        if not s['intentional_open_surface']:
            if s['nonmanifold_edges']:errors.append(f'{name}/{meshname}: nonmanifold')
            if s['signed_volume']<=0:errors.append(f'{name}/{meshname}: inverted volume')
        if s['rotation']!=[0,0,0] or s['scale']!=[1,1,1]:errors.append(f'{name}/{meshname}: unapplied transform')
    scr=next(x for x in root.children_recursive if x.name=='screen')
    uv=[tuple(x.uv) for x in scr.data.uv_layers.active.data];stats['screen_uv_range']=[min(v[0] for v in uv),max(v[0] for v in uv),min(v[1] for v in uv),max(v[1] for v in uv)]
    if any(abs(x-y)>1e-6 for x,y in zip(stats['screen_uv_range'],[0,1,0,1])):errors.append(f'{name}: UV not full range')
    stats['screen_vertices']=len(scr.data.vertices)
    if name=='phone':
        chassis=next(x for x in root.children_recursive if x.name=='chassis')
        coords=[v.co for v in chassis.data.vertices]
        center=[(min(v[i] for v in coords)+max(v[i] for v in coords))/2 for i in range(3)]
        stats['chassis_center_blender']=center
        if max(abs(v) for v in center)>1e-7:errors.append('phone: chassis center is not root origin')
    if name=='laptop':
        lid=next(x for x in root.children_recursive if x.name=='lid');fixed=[x for x in root.children_recursive if x.type=='MESH' and x.parent!=lid];moving=[x for x in lid.children_recursive if x.type=='MESH']
        def tree(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[tuple(f.vertices) for f in ob.data.polygons],all_triangles=False,epsilon=1e-8)
        fixedtrees=[(x.name,tree(x)) for x in fixed];collisions=[]
        for deg in range(131):
            lid.rotation_euler.x=-math.radians(deg);bpy.context.view_layer.update()
            for ob in moving:
                bvh=tree(ob)
                for fixedname,ftree in fixedtrees:
                    hits=bvh.overlap(ftree)
                    if hits:collisions.append({'angle_deg':deg,'lid_mesh':ob.name,'base_mesh':fixedname,'intersecting_pairs':len(hits)})
        stats['lid_sweep']={'angles_deg':list(range(131)),'surface_intersections':collisions,'tested_parts':'all lid meshes against all stationary meshes including hinges'}
        if collisions:errors.append(f'laptop: {len(collisions)} sampled surface intersections')
    report[name]=stats
report['errors']=errors;report['passed']=not errors;Path(args.out).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':not errors,'errors':errors}))
if errors:raise RuntimeError('Geometry gate failed')
