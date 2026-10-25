"""Kosmo map low-poly toolkit: palette materials + bmesh builder."""
import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler
from mathutils.geometry import tessellate_polygon

PAL = {
    # architecture
    'floor': '#F8F5EF', 'plinth': '#D6CCBB', 'wall': '#FFFFFF', 'wallside': '#ECE6DD',
    'ground': '#DDE1E8', 'path': '#E6DFD2', 'stand': '#FBFAF7', 'standside': '#DDD6CA',
    # halls
    'h_utro': '#F5CDB6', 'h_tvortsy': '#F2DC9C', 'h_dom': '#BFD9F0', 'h_luna': '#D2C8F0',
    'h_mezhdu': '#BCE5D1', 'h_chelovechestvu': '#F0C2D2', 'h_park': '#CDE3B3',
    'h_vest': '#EEE4D2', 'h_kino': '#DDD3EC',
    # exhibits
    'white': '#F6F6F3', 'offwhite': '#E9E6DF', 'silver': '#C6CCD5', 'steel': '#8F97A4',
    'dark': '#3B404C', 'black': '#25272D', 'gold': '#E3B14B', 'foil': '#D9A441',
    'orange': '#EA7A3F', 'red': '#D9473B', 'blue': '#3A5DAE', 'panel': '#2F4B8F',
    'glass': '#A8D8F2', 'copper': '#C97C4B', 'green': '#6C9A63', 'cream': '#EBDDC3',
    'wood': '#BC8A5A', 'darkwood': '#8A5E3B', 'char': '#5B4A3E', 'grey': '#A9AEB6',
    'yellow': '#F2C94C', 'navy': '#2D3A5E', 'tan': '#D9B48A', 'pink': '#E9A7A0',
    'titan': '#D7DCE3', 'beige': '#E5CFA8', 'brown': '#7A5233', 'skin': '#E8B79A',
}
METAL = {'silver': (0.55, 0.35), 'steel': (0.6, 0.4), 'gold': (0.7, 0.3), 'foil': (0.7, 0.3),
         'copper': (0.7, 0.35), 'titan': (0.75, 0.25)}


def srgb2lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hexc(h):
    h = h.lstrip('#')
    return tuple(srgb2lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def mat(name):
    m = bpy.data.materials.get('K_' + name)
    if m:
        return m
    m = bpy.data.materials.new('K_' + name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    c = hexc(PAL[name])
    b.inputs['Base Color'].default_value = (*c, 1)
    met, rough = METAL.get(name, (0.0, 0.62))
    b.inputs['Metallic'].default_value = met
    b.inputs['Roughness'].default_value = rough
    if name == 'glass':
        b.inputs['Roughness'].default_value = 0.15
    m.diffuse_color = (*c, 1)
    return m


def M(loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    return (Matrix.Translation(Vector(loc)) @ Euler(rot).to_matrix().to_4x4()
            @ Matrix.Diagonal((*scale, 1)))


class B:
    """Accumulates primitives into one bmesh with per-face materials."""

    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.mats = []
        self.T = Matrix.Identity(4)   # current parent transform

    def _mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def _tag(self, n0, m, verts=None, faces=None):
        i = self._mi(m)
        fs = set(faces or [])
        for v in (verts or []):
            fs.update(v.link_faces)
        for f in fs:
            f.material_index = i
            f.smooth = False
        return fs

    # --- primitives -------------------------------------------------------
    def cyl(self, r, h, m, loc=(0, 0, 0), rot=(0, 0, 0), r2=None, seg=12, scale=(1, 1, 1), cap=True):
        """cylinder/cone, loc = base centre (local z up)."""
        n0 = len(self.bm.faces)
        r2 = r if r2 is None else r2
        mt = self.T @ M(loc, rot, scale) @ Matrix.Translation((0, 0, h / 2))
        res = bmesh.ops.create_cone(self.bm, cap_ends=cap, cap_tris=False, segments=seg,
                                    radius1=r, radius2=max(r2, 0.0), depth=h, matrix=mt)
        self._tag(n0, m, verts=res['verts'])

    def box(self, sx, sy, sz, m, loc=(0, 0, 0), rot=(0, 0, 0)):
        """box, loc = base centre."""
        n0 = len(self.bm.faces)
        mt = self.T @ M(loc, rot) @ Matrix.Translation((0, 0, sz / 2)) @ Matrix.Diagonal((sx, sy, sz, 1))
        res = bmesh.ops.create_cube(self.bm, size=1, matrix=mt)
        self._tag(n0, m, verts=res['verts'])

    def sph(self, r, m, loc=(0, 0, 0), seg=12, rings=8, scale=(1, 1, 1), rot=(0, 0, 0)):
        n0 = len(self.bm.faces)
        mt = self.T @ M(loc, rot, scale)
        res = bmesh.ops.create_uvsphere(self.bm, u_segments=seg, v_segments=rings, radius=r, matrix=mt)
        self._tag(n0, m, verts=res['verts'])

    def ico(self, r, m, loc=(0, 0, 0), sub=1, scale=(1, 1, 1)):
        n0 = len(self.bm.faces)
        res = bmesh.ops.create_icosphere(self.bm, subdivisions=sub, radius=r, matrix=self.T @ M(loc, (0, 0, 0), scale))
        self._tag(n0, m, verts=res['verts'])

    def prism(self, outer, z0, z1, m, holes=(), mtop=None, loc=(0, 0, 0), rot=(0, 0, 0)):
        """extrude 2D polygon (list of (x,y)) with optional holes from z0 to z1."""
        n0 = len(self.bm.faces)
        mt = self.T @ M(loc, rot)
        rings = [list(outer)] + [list(h) for h in holes]
        bv = self.bm.verts
        top, bot = [], []
        for ring in rings:
            top.append([bv.new(mt @ Vector((x, y, z1))) for x, y in ring])
            bot.append([bv.new(mt @ Vector((x, y, z0))) for x, y in ring])
        flat = [v for ring in top for v in ring]
        flatb = [v for ring in bot for v in ring]
        tris = tessellate_polygon([[Vector((x, y, 0)) for x, y in ring] for ring in rings])
        topfaces = []
        for a, b_, c in tris:
            try:
                topfaces.append(self.bm.faces.new((flat[a], flat[b_], flat[c])))
            except ValueError:
                pass
            try:
                self.bm.faces.new((flatb[c], flatb[b_], flatb[a]))
            except ValueError:
                pass
        for tr, br in zip(top, bot):
            n = len(tr)
            for i in range(n):
                j = (i + 1) % n
                try:
                    self.bm.faces.new((br[i], br[j], tr[j], tr[i]))
                except ValueError:
                    pass
        fs = self._tag(n0, m, verts=flat + flatb)
        if mtop:
            it = self._mi(mtop)
            for f in topfaces:
                f.material_index = it
        bmesh.ops.recalc_face_normals(self.bm, faces=list(fs))

    def ring(self, r_out, r_in, h, m, loc=(0, 0, 0), rot=(0, 0, 0), seg=16):
        o = [(r_out * math.cos(a), r_out * math.sin(a)) for a in [i * 2 * math.pi / seg for i in range(seg)]]
        i_ = [(r_in * math.cos(a), r_in * math.sin(a)) for a in [i * 2 * math.pi / seg for i in range(seg)]]
        self.prism(o, 0, h, m, holes=[i_[::-1]], loc=loc, rot=rot)

    def tube(self, p0, p1, r, m, seg=6):
        """cylinder between two points."""
        p0, p1 = Vector(p0), Vector(p1)
        d = p1 - p0
        q = Vector((0, 0, 1)).rotation_difference(d.normalized())
        n0 = len(self.bm.faces)
        mt = self.T @ Matrix.Translation(p0) @ q.to_matrix().to_4x4() @ Matrix.Translation((0, 0, d.length / 2))
        res = bmesh.ops.create_cone(self.bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length, matrix=mt)
        self._tag(n0, m, verts=res['verts'])

    def panel(self, w, l, m, loc=(0, 0, 0), rot=(0, 0, 0), t=0.04, frame=None):
        """flat solar-panel slab, w along x, l along y."""
        self.box(w, l, t, m, loc, rot)

    def stack(self, parts, x=0, y=0, z=0, seg=12):
        """vertical stack of (r_bottom, r_top, h, mat). returns top z."""
        for rb, rt, h, mm in parts:
            if h > 0:
                self.cyl(rb, h, mm, (x, y, z), r2=rt, seg=seg)
            z += h
        return z

    def truss(self, sx, sy, sz, m, loc=(0, 0, 0), bar=0.06, levels=4):
        """open lattice tower (4 posts + rings + diagonals)."""
        x0, y0, z0 = loc
        hx, hy = sx / 2, sy / 2
        cs = [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)]
        for cx, cy in cs:
            self.box(bar, bar, sz, m, (x0 + cx, y0 + cy, z0))
        for k in range(levels + 1):
            z = z0 + sz * k / levels
            self.box(sx, bar, bar, m, (x0, y0 - hy, z - bar / 2 if k else z))
            self.box(sx, bar, bar, m, (x0, y0 + hy, z - bar / 2 if k else z))
            self.box(bar, sy, bar, m, (x0 - hx, y0, z - bar / 2 if k else z))
            self.box(bar, sy, bar, m, (x0 + hx, y0, z - bar / 2 if k else z))
        for k in range(levels):
            za, zb = z0 + sz * k / levels, z0 + sz * (k + 1) / levels
            self.tube((x0 - hx, y0 - hy, za), (x0 + hx, y0 - hy, zb), bar * 0.4, m, 4)
            self.tube((x0 + hx, y0 + hy, za), (x0 - hx, y0 + hy, zb), bar * 0.4, m, 4)
            self.tube((x0 - hx, y0 + hy, za), (x0 - hx, y0 - hy, zb), bar * 0.4, m, 4)
            self.tube((x0 + hx, y0 - hy, za), (x0 + hx, y0 + hy, zb), bar * 0.4, m, 4)

    # --- finish -----------------------------------------------------------
    def build(self, collection=None, merge=0.0005):
        bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts, dist=merge)
        me = bpy.data.meshes.new(self.name)
        self.bm.to_mesh(me)
        self.bm.free()
        for mm in self.mats:
            me.materials.append(mat(mm))
        ob = bpy.data.objects.new(self.name, me)
        (collection or bpy.context.scene.collection).objects.link(ob)
        return ob


def get_coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def ground_object(ob):
    """move mesh so its lowest point is z=0 and centre xy=0."""
    me = ob.data
    if not me.vertices:
        return
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]; zs = [v.co.z for v in me.vertices]
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    me.transform(Matrix.Translation(-off))
