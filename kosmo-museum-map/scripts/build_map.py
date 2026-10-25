"""Build the Museum of Cosmonautics isometric map. Run: python3 build_map.py <out_dir>"""
import sys, os, json, math, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from mathutils import Vector, Matrix, Euler
import klib, exhibits
importlib.reload(klib); importlib.reload(exhibits)
from klib import B, get_coll, ground_object, mat
from exhibits import EXHIBITS, AMENITIES, MASCOTS, lm_monument

OUT = sys.argv[-1] if len(sys.argv) > 1 and not sys.argv[-1].endswith('.py') else os.path.join(HERE, '..', 'blender')
os.makedirs(OUT, exist_ok=True)
PLAN = json.load(open(os.path.join(HERE, '..', 'data', 'plan_one.json')))

S = 0.1
# one space: both floors in true relative position, lower floor one step down
OX = {'upper': 0.0, 'lower': 0.0}
OY = {'upper': 0.0, 'lower': 0.0}
FZ = {'upper': 1.3, 'lower': 0.3}
WALL_H = 2.0


def P(px, py, floor):
    return ((px - 400) * S + OX[floor], -(py - 650) * S + OY[floor])


def poly_m(p, floor):
    o = [P(x, y, floor) for x, y in p['outer']]
    h = [[P(x, y, floor) for x, y in hh] for hh in p['holes']]
    # svg y is flipped -> winding flips; tessellate handles either
    return o, h


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = 'Карта'
scene.unit_settings.system = 'METRIC'

root = scene.collection
c_arch = get_coll('Архитектура')
c_ex = get_coll('Экспонаты')
c_am = get_coll('Зоны и сервисы')
c_lm = get_coll('Монумент')
c_lab = get_coll('Подписи')
c_ms = get_coll('Маскоты')

# ---------------------------------------------------------------- architecture
g = B('Ground')
g.prism([(-400, -400), (400, -400), (400, 400), (-400, 400)], -0.3, 0.0, 'ground')
g.build(c_arch)

for floor in ('upper', 'lower'):
    b = B(f'Floor_{floor}')
    for p in PLAN[floor + '_floor']:
        o, h = poly_m(p, floor)
        b.prism(o, 0.0, FZ[floor], 'plinth' if floor == 'upper' else 'plinth_low', holes=h, mtop='floor' if floor == 'upper' else 'floor_low')
    b.build(c_arch)['floor'] = floor
    w = B(f'Walls_{floor}')
    for p in PLAN[floor + '_walls']:
        o, h = poly_m(p, floor)
        w.prism(o, FZ[floor], FZ[floor] + WALL_H, 'wallside', holes=h, mtop='wall')
    w.build(c_arch)['floor'] = floor

# stairs between levels (real transition zones of the museum plan)
for st in PLAN['stairs']:
    x0, y0, x1, y1 = st['rect']
    b = B(f'Stairs_{st["id"]}')
    n = 7
    for i in range(n):
        if st['up_side'] == '+y':      # svg +y is upper end
            ya, yb = y0 + (y1 - y0) * i / n, y0 + (y1 - y0) * (i + 1) / n
            xa, xb = x0, x1
        else:                          # svg +x is upper end
            xa, xb = x0 + (x1 - x0) * i / n, x0 + (x1 - x0) * (i + 1) / n
            ya, yb = y0, y1
        h = FZ['lower'] + (FZ['upper'] - FZ['lower']) * (i + 1) / n
        o = [P(xa, ya, 'upper'), P(xb, ya, 'upper'), P(xb, yb, 'upper'), P(xa, yb, 'upper')]
        b.prism(o, 0.0, h, 'plinth', mtop='stand')
    # side rails
    if st['up_side'] == '+y':
        for xx in (x0 + 1, x1 - 1):
            b.prism([P(xx - 1, y0, 'upper'), P(xx + 1, y0, 'upper'), P(xx + 1, y1, 'upper'), P(xx - 1, y1, 'upper')],
                    FZ['upper'], FZ['upper'] + 0.9, 'steel')
    else:
        for yy in (y0 + 1, y1 - 1):
            b.prism([P(x0, yy - 1, 'upper'), P(x1, yy - 1, 'upper'), P(x1, yy + 1, 'upper'), P(x0, yy + 1, 'upper')],
                    FZ['upper'], FZ['upper'] + 0.9, 'steel')
    ob = b.build(c_arch); ob['floor'] = 'both'

for z in PLAN['zones']:
    b = B(f'Zone_{z["id"]}')
    for p in z['polys']:
        o, h = poly_m(p, z['floor'])
        b.prism(o, FZ[z['floor']], FZ[z['floor']] + 0.03, 'h_' + z['id'], holes=h)
    b.build(c_arch)['floor'] = z['floor']

# ---------------------------------------------------------------- exhibits
lib_scene = bpy.data.scenes.new('Библиотека экспонатов')
lib_root = get_coll('Библиотека', None)
bpy.data.scenes['Карта'].collection.children.unlink(lib_root)
lib_scene.collection.children.link(lib_root)

meta = {'exhibits': [], 'amenities': [], 'zones': []}
ex_dir = os.path.join(OUT, 'exhibits')
os.makedirs(ex_dir, exist_ok=True)


def make(name, fn):
    b = B(name)
    fn(b)
    ob = b.build(lib_root)
    ground_object(ob)
    return ob


cols = 7
for i, (eid, slug, title, fn, hall, floor, sx, sy, sc, rz) in enumerate(EXHIBITS):
    lib = make(f'EX_{eid}_{slug}', fn)
    lib['title'] = title
    lib.location = ((i % cols) * 14.0, -(i // cols) * 14.0, 0)
    bpy.data.libraries.write(os.path.join(ex_dir, f'{eid:03d}_{slug}.blend'), {lib}, fake_user=True)
    ob = bpy.data.objects.new(f'EX_{eid}', lib.data)
    c_ex.objects.link(ob)
    x, y = P(sx, sy, floor)
    ob.location = (x, y, FZ[floor] + 0.03)
    ob.rotation_euler = (0, 0, math.radians(rz))
    ob.scale = (sc, sc, sc)
    ob['title'] = title
    ob['hall'] = hall
    ob['floor'] = floor
    dims = [d * sc for d in lib.dimensions]
    meta['exhibits'].append({'id': eid, 'slug': slug, 'title': title, 'hall': hall, 'floor': floor,
                             'pos': [round(x, 2), round(y, 2), round(FZ[floor] + dims[2], 2)],
                             'size': [round(v, 2) for v in dims],
                             'tris': sum(len(p.vertices) - 2 for p in lib.data.polygons)})

for j, (aid, title, fn, floor, sx, sy, sc, rz) in enumerate(AMENITIES):
    sc2 = 0.75 if aid.startswith('stairs') else sc
    lib = make(f'AM_{aid}', fn)
    lib.location = ((j % cols) * 18.0, -((len(EXHIBITS) // cols) + 2 + j // cols) * 18.0, 0)
    ob = bpy.data.objects.new(f'AM_{aid}', lib.data)
    c_am.objects.link(ob)
    x, y = P(sx, sy, floor)
    ob.location = (x, y, FZ[floor] + 0.03)
    ob.rotation_euler = (0, 0, math.radians(rz))
    ob.scale = (sc2, sc2, sc2)
    ob['floor'] = floor
    meta['amenities'].append({'id': aid, 'title': title, 'floor': floor, 'pos': [round(x, 2), round(y, 2)]})

for j, (mid, title, fn, floor, sx, sy, sc, rz) in enumerate(MASCOTS):
    lib = make(f'MSL_{mid}', fn)
    lib.location = (j * 4.0, 40.0, 0)
    bpy.data.libraries.write(os.path.join(ex_dir, f'mascot_{mid}.blend'), {lib}, fake_user=True)
    ob = bpy.data.objects.new(f'MS_{mid}', lib.data)
    c_ms.objects.link(ob)
    x, y = P(sx, sy, floor)
    ob.location = (x, y, FZ[floor] + 0.03)
    ob.rotation_euler = (0, 0, math.radians(rz))
    ob.scale = (sc, sc, sc)
    ob['floor'] = 'both'
    ob['title'] = title
    meta.setdefault('mascots', []).append({'id': mid, 'title': title, 'pos': [round(x, 2), round(y, 2)]})

mb = B('LM_monument')
lm_monument(mb)
mon = mb.build(c_lm)
mon['floor'] = 'both'
mon.location = (-54.0, 44.0, 0)
mon.rotation_euler = (0, 0, math.radians(-25))
meta['monument'] = {'title': 'Монумент «Покорителям космоса»', 'pos': [-54.0, 44.0, 48.0]}

for z in PLAN['zones']:
    x, y = P(z['c'][0], z['c'][1], z['floor'])
    meta['zones'].append({'id': z['id'], 'name': z['name'], 'floor': z['floor'], 'pos': [round(x, 2), round(y, 2)]})

# ---------------------------------------------------------------- labels (render only)
for z in meta['zones']:
    cu = bpy.data.curves.new('L_' + z['id'], 'FONT')
    cu.body = z['name'].upper()
    cu.size = 1.6
    cu.align_x = 'CENTER'
    cu.extrude = 0.02
    ob = bpy.data.objects.new('L_' + z['id'], cu)
    ob.location = (z['pos'][0], z['pos'][1], FZ[z['floor']] + 0.05)
    ob.data.materials.append(mat('dark'))
    c_lab.objects.link(ob)
c_lab.hide_render = True

# ---------------------------------------------------------------- light, world, camera
world = bpy.data.worlds.new('World')
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.93, 0.92, 0.9, 1)
bg.inputs['Strength'].default_value = 0.9

sun_d = bpy.data.lights.new('Sun', 'SUN')
sun_d.energy = 3.2
sun_d.angle = math.radians(8)
sun_d.color = (1.0, 0.97, 0.92)
sun = bpy.data.objects.new('Sun', sun_d)
sun.rotation_euler = (math.radians(42), 0, math.radians(35))
root.objects.link(sun)

cam_d = bpy.data.cameras.new('Iso')
cam_d.type = 'ORTHO'
cam_d.ortho_scale = 160
cam_d.clip_end = 2000
cam = bpy.data.objects.new('Iso', cam_d)
root.objects.link(cam)
AZ = math.radians(-35)     # camera from south-west
EL = math.radians(36)
target = Vector((-12, 0, 8))
d = Vector((math.sin(AZ) * math.cos(EL), -math.cos(AZ) * math.cos(EL), math.sin(EL)))
cam.location = target + d * 400
cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam
meta['camera'] = {'az_deg': -35, 'el_deg': 36, 'target': list(target)}

scene.render.resolution_x = 1920
scene.render.resolution_y = 1200
try:
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
except Exception:
    pass

# library scene gets own camera/light
lib_scene.world = world
lib_scene.collection.objects.link(sun)
lc = bpy.data.objects.new('LibCam', cam_d.copy())
lc.data.ortho_scale = 110
lib_scene.collection.objects.link(lc)
lc.location = Vector((42, -40, 0)) + d * 300
lc.rotation_euler = cam.rotation_euler
lib_scene.camera = lc
lib_scene.render.resolution_x = 1920
lib_scene.render.resolution_y = 1400

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'kosmo_map.blend'))
json.dump(meta, open(os.path.join(OUT, 'meta.json'), 'w'), ensure_ascii=False, indent=1)
tris = sum(e['tris'] for e in meta['exhibits'])
print('BUILD OK exhibits', len(meta['exhibits']), 'tris', tris)
