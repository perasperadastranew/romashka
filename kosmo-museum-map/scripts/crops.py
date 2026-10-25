import os
import bpy, sys, json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','blender','kosmo_map.blend'))
sc=bpy.data.scenes['Карта']; sc.render.engine='CYCLES'; sc.cycles.samples=14; sc.cycles.use_denoising=True
sc.render.resolution_x=1200; sc.render.resolution_y=800; sc.render.resolution_percentage=100
sc.render.image_settings.file_format='JPEG'
cam=sc.camera; d=cam.rotation_euler.to_quaternion()@Vector((0,0,1))
S=0.1
def P(px,py,f):
    OX={'upper':0.0,'lower':0.0}; OY={'upper':0.0,'lower':0.0}
    return Vector(((px-400)*S+OX[f], -(py-650)*S+OY[f], 1))
crops=json.loads(sys.argv[-1])
for name,(px,py,f,os_) in crops.items():
    cam.data.ortho_scale=os_; cam.location=P(px,py,f)+d*300
    sc.render.filepath=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','renders',f'crop_{name}.jpg')
    bpy.ops.render.render(write_still=True, scene=sc.name)
