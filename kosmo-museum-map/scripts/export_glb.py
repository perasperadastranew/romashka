import os
import bpy, os
bpy.ops.wm.open_mainfile(filepath=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','blender','kosmo_map.blend'))
bpy.data.scenes.remove(bpy.data.scenes['Библиотека экспонатов'])
sc=bpy.data.scenes['Карта']
vl=sc.view_layers[0]
for o in sc.objects: o.select_set(False, view_layer=vl)
keep=['Архитектура','Экспонаты','Зоны и сервисы','Монумент','Маскоты']
for cn in keep:
    for o in bpy.data.collections[cn].all_objects:
        if o.name!='Ground': o.select_set(True, view_layer=vl)
if True:
    bpy.ops.export_scene.gltf(filepath=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','site','')+'kosmo_map.glb', export_format='GLB',
        use_selection=True, export_apply=True, export_yup=True, export_cameras=False, export_lights=False,
        export_extras=True, export_texcoords=False, export_normals=True)
print('GLB', os.path.getsize(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','site','')+'kosmo_map.glb'))
