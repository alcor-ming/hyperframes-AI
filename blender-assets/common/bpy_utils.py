"""Original, script-only asset helpers for Blender 4.5.14 LTS.
Coordinates accepted by mesh functions are glTF-world meters (+Y up, +Z front).
"""
import bpy, bmesh, math, json, hashlib
from mathutils import Vector
from pathlib import Path
VERSION=(4,5,14)
ROLES={'hf_surface':('D9D9D9',1), 'hf_muted':('8C8C8C',1), 'hf_accent':('4C7DFF',1), 'hf_emissive':('FFFFFF',1), 'hf_glass':('FFFFFF',.3), 'hf_screen':('080A0D',1), 'hf_inner':('4C7DFF',1)}
def reset():
    if bpy.app.version!=VERSION: raise RuntimeError(f'Expected Blender {VERSION}; got {bpy.app.version}')
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    for d in list(bpy.data.materials): bpy.data.materials.remove(d)
    bpy.context.scene.unit_settings.system='METRIC'; bpy.context.scene.unit_settings.scale_length=1

def linear(v): return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4

def materials():
    out={}
    for name,(h,a) in ROLES.items():
        m=bpy.data.materials.new(name); m.use_nodes=True
        rgb=[linear(int(h[i:i+2],16)/255) for i in (0,2,4)]
        p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*rgb,a)
        p.inputs['Metallic'].default_value=0.08 if name=='hf_muted' else 0
        p.inputs['Roughness'].default_value=.64
        p.inputs['Alpha'].default_value=a
        if name in ('hf_emissive','hf_inner'):
            p.inputs['Emission Color'].default_value=(*rgb,1);p.inputs['Emission Strength'].default_value=1.5
        if a<1: m.surface_render_method='BLENDED'
        m.diffuse_color=(*rgb,a);m['role']=name;out[name]=m
    return out

def vec(p): return (p[0],-p[2],p[1])
def empty(name,parent=None,extras=None):
    ob=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(ob);ob.parent=parent
    for k,v in (extras or {}).items():ob[k]=v
    return ob

def mesh(name,verts,faces,mat,parent=None,bevel=0,segments=3):
    me=bpy.data.meshes.new(name);me.from_pydata([vec(v) for v in verts],[],faces);me.update()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=parent;me.materials.append(mat)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-9);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    if bevel:
        mod=ob.modifiers.new('edge_softening','BEVEL');mod.width=bevel;mod.segments=segments
        mod.affect='EDGES';mod.limit_method='ANGLE'
        bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);ob.select_set(False)
    for f in me.polygons:f.use_smooth=True
    if bevel:
        mod=ob.modifiers.new('weighted_normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50
        bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);ob.select_set(False)
    return ob

def box(name,center,size,mat,parent=None,bevel=.001,segments=3):
    x,y,z=center; a,b,c=[s/2 for s in size]
    vs=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(-1,-1,1),(-1,1,1),(-1,1,-1),(1,-1,-1),(1,-1,1),(1,1,1),(1,1,-1)]]
    return mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(1,2,6,5),(0,4,7,3)],mat,parent,bevel,segments)

def outline(w,h,r,n=8):
    raw=[(cx+r*math.cos(t),cy+r*math.sin(t)) for cx,cy,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)] for t in [math.radians(start+i*90/n) for i in range(n+1)]]
    out=[]
    for p in raw:
        if not out or math.dist(p,out[-1])>1e-10:out.append(p)
    if len(out)>2 and math.dist(out[0],out[-1])<1e-10:out.pop()
    return out

def prism(name,w,h,d,r,center,mat,parent=None,plane='xy',bevel=.0003):
    p=outline(w,h,r);n=len(p)
    def coord(a,b,c):
        q=(a,b,c) if plane=='xy' else (a,c,b)
        return tuple(q[i]+center[i] for i in range(3))
    vs=[coord(a,b,c) for c in (-d/2,d/2) for a,b in p]
    fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vs,fs,mat,parent,bevel)

def ring(name,w,h,r,border,front,back,mat,parent=None,center=(0,0),plane='xy'):
    outer=outline(w,h,r);inner=outline(w-2*border,h-2*border,max(r-border,.0001));n=len(outer)
    def c(q,d):
        a,b=q; a+=center[0];b+=center[1]
        return (a,b,d) if plane=='xy' else (a,d,b)
    vs=[c(q,d) for d in (back,front) for loop in (outer,inner) for q in loop];fs=[]
    for i in range(n):
        j=(i+1)%n
        fs.extend([(i,j,2*n+j,2*n+i),(n+j,n+i,3*n+i,3*n+j),(2*n+i,2*n+j,3*n+j,3*n+i),(j,i,n+i,n+j)])
    return mesh(name,vs,fs,mat,parent,bevel=.00012)

def screen(name,w,h,depth,mat,parent,center=(0,0),plane='xy',radius=0):
    p=outline(w,h,radius) if radius else [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]
    vs=[(a+center[0],b+center[1],depth) if plane=='xy' else (a+center[0],depth,b+center[1]) for a,b in p]
    ob=mesh(name,vs,[tuple(range(len(p)))],mat,parent)
    # For closed laptop the screen faces DOWN, so when opened it faces the viewer.
    for f in ob.data.polygons:f.use_smooth=False
    if plane=='xz':
        # from_pydata clockwise XZ has -Y, correct. Recalc on an isolated face preserves winding.
        pass
    uv=ob.data.uv_layers.new(name='UVMap')
    for loop in ob.data.loops:
        a,b=p[loop.vertex_index];uv.data[loop.index].uv=(a/w+.5,b/h+.5)
    ob['screen_aspect']=w/h;ob['screen_uv']='full_0_1_top_left';ob['intentional_open_surface']=True
    return ob

def export(path,objects):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objects:ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_materials='EXPORT',export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_force_sampling=True,export_frame_range=True,export_cameras=False,export_lights=False,export_texcoords=True,export_normals=True,export_tangents=False)

def metrics(root):
    obs=[root]+list(root.children_recursive);result={'triangles':0,'meshes':{},'axis':'+Y up; +Z front','unit':'meter'}
    for ob in obs:
        if ob.type!='MESH':continue
        me=ob.data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
        rec={'triangles':len(me.loop_triangles),'vertices':len(me.vertices),'zero_area_faces':sum(f.calc_area()<1e-14 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True),'duplicate_vertices':len(bm.verts)-len({tuple(round(float(v.co[i]),9) for i in range(3)) for v in bm.verts}),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'rotation':list(ob.rotation_euler),'scale':list(ob.scale),'intentional_open_surface':bool(ob.get('intentional_open_surface',False))}
        result['triangles']+=rec['triangles'];result['meshes'][ob.name]=rec;bm.free()
    return result

def render_views(root,directory,res=512,samples=24):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=samples;scene.cycles.use_denoising=False
    scene.render.resolution_x=res;scene.render.resolution_y=res;scene.render.resolution_percentage=100
    scene.view_settings.view_transform='Standard';scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
    scene.world.color=(.22,.22,.22)
    pts=[ob.matrix_world@Vector(c) for ob in root.children_recursive if ob.type=='MESH' for c in ob.bound_box]
    low=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)]);target=(low+hi)/2;size=max(hi-low)
    def aim(ob):ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
    lighting=[]
    for name,loc,power,scale in [('key',(-2,-3,4),35,2),('fill',(3,-2,1),20,2.5),('rim',(0,3,3),40,2)]:
        d=bpy.data.lights.new(name,'AREA');d.energy=power*size*size;d.shape='DISK';d.size=scale*size
        ob=bpy.data.objects.new(name,d);scene.collection.objects.link(ob);ob.location=target+Vector(loc)*size;aim(ob);lighting.append(ob)
    d=bpy.data.cameras.new('preview_camera');ob=bpy.data.objects.new('preview_camera',d);scene.collection.objects.link(ob);d.type='ORTHO';d.ortho_scale=size*1.35;scene.camera=ob
    for name,view in [('front',(0,-4,0)),('three-quarter',(2.7,-4,2.2)),('back',(0,4,.3)),('top',(0,-.001,4))]:
        ob.location=target+Vector(view)*size;aim(ob);scene.render.filepath=str(directory/(name+'.png'));bpy.ops.render.render(write_still=True)
    for x in lighting+[ob]:bpy.data.objects.remove(x,do_unlink=True)
