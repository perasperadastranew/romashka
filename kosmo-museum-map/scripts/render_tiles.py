import os
import bpy, sys, os, math
from mathutils import Vector
out=sys.argv[-1]; os.makedirs(out, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','blender','kosmo_map.blend'))
sc=bpy.data.scenes['Библиотека экспонатов']
sc.render.engine='CYCLES'; sc.cycles.samples=10; sc.cycles.use_denoising=True
sc.render.resolution_x=sc.render.resolution_y=420; sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
objs=[o for o in sc.collection.all_objects if o.type=='MESH']
cam=sc.camera
gp=bpy.data.objects.new('TileGround', bpy.data.objects['Ground'].data); sc.collection.objects.link(gp)
d=(cam.rotation_euler.to_quaternion()@Vector((0,0,1)))
only=sys.argv[-2].split(',') if sys.argv[-2]!='all' else None
for o in objs:
    if only and not any(o.name.startswith(p) for p in only): continue
    for p in objs: p.hide_render = (p is not o)
    bb=[o.location+Vector(c) for c in o.bound_box]
    c=sum(bb,Vector())/8; size=max((max(v[i] for v in bb)-min(v[i] for v in bb)) for i in range(3))
    gp.location=(c.x,c.y,0)
    cam.data.ortho_scale=size*1.35+0.3
    cam.location=c+d*200
    sc.render.filepath=os.path.join(out,o.name+'.png')
    bpy.ops.render.render(write_still=True, scene=sc.name)
print('TILES DONE')
