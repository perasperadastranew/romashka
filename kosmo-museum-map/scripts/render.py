import bpy, sys
args=sys.argv[sys.argv.index('--')+1:]
out, scene_name, res = args[0], args[1], float(args[2]) if len(args)>2 else 0.5
sc=bpy.data.scenes[scene_name]
sc.render.engine='CYCLES'
sc.cycles.device='CPU'; sc.cycles.samples=int(args[3]) if len(args)>3 else 24
sc.cycles.use_denoising=True
sc.render.resolution_percentage=int(res*100)
sc.render.image_settings.file_format='JPEG'
sc.render.filepath=out
if len(args)>4:
    import mathutils
    cam=sc.camera; cam.data.ortho_scale=float(args[4]); cam.location=mathutils.Vector(eval(args[5])) + (cam.rotation_euler.to_quaternion() @ mathutils.Vector((0,0,1)))*400
bpy.ops.render.render(write_still=True, scene=sc.name)
print('done')
