"""Low-poly exhibits of the Moscow Museum of Cosmonautics. Units: metres, z up, front = -Y."""
import math
from klib import B, PAL

PAL.update({'plinth_low': '#C9CDD6', 'floor_low': '#EEF0F5', 'khaki': '#A8AD8C', 'olive': '#8C9177', 'concrete': '#C9C4BA', 'sea': '#8FC9E6',
            'mlibrown': '#9C7B55'})
pi = math.pi
RX = (0, pi / 2, 0)      # local z -> +x


# ---------------------------------------------------------------- helpers
def podium(b, r=0.8, h=0.18, square=None):
    if square:
        b.box(square[0], square[1], h, 'stand')
    else:
        b.cyl(r, h, 'stand', seg=24)
    return h


def pole_stand(b, h, r_base=0.45, r_pole=0.05):
    b.cyl(r_base, 0.08, 'steel', seg=16)
    b.cyl(r_pole, h, 'steel', (0, 0, 0.08), seg=8)
    return h + 0.08


def suit(b, body='white', accent='offwhite', visor='gold', back=None, hard=False, z=0.0, flag=False):
    for sx in (-0.11, 0.11):
        b.box(0.15, 0.27, 0.12, 'dark' if not hard else accent, (sx, -0.03, z))
        b.cyl(0.085, 0.72, body, (sx, 0, z + 0.12), r2=0.095, seg=8)
    b.box(0.38, 0.25, 0.2, body, (0, 0, z + 0.8))
    if hard:
        b.box(0.5, 0.44, 0.6, body, (0, 0, z + 0.98))
        b.box(0.26, 0.06, 0.18, accent, (0, -0.24, z + 1.2))
    else:
        b.cyl(0.21, 0.55, body, (0, 0, z + 0.98), r2=0.24, seg=10, scale=(1, 0.75, 1))
        b.cyl(0.225, 0.06, accent, (0, 0, z + 0.98), seg=10, scale=(1, 0.78, 1))
    sh = z + 1.45
    for s in (-1, 1):
        b.sph(0.1, body, (s * 0.27, 0, sh), seg=8, rings=6)
        b.tube((s * 0.28, 0, sh), (s * 0.36, -0.06, z + 0.95), 0.075, body, 8)
        b.sph(0.075, accent, (s * 0.37, -0.07, z + 0.92), seg=8, rings=6)
    b.cyl(0.13, 0.08, accent, (0, 0, z + 1.52), seg=12)
    b.sph(0.19, 'white' if body != 'white' else 'offwhite', (0, 0, z + 1.72), seg=12, rings=8)
    b.sph(0.14, visor, (0, -0.1, z + 1.71), seg=10, rings=6, scale=(1, 0.55, 0.8))
    if flag:
        b.box(0.16, 0.05, 0.05, 'red', (0, -0.15, z + 1.83))
    if back:
        b.box(0.42, 0.22, 0.55, back, (0, 0.27, z + 0.95))


def soyuz(b, scale=1.0, panels=True, om='khaki', dm='olive', sm='offwhite', x0=0.0, z=0.0, y=0.0):
    """Soyuz spacecraft lying along +X, rear (engine) at x0."""
    s = scale
    def X(v): return x0 + v * s
    b.cyl(0.35 * s, 0.4 * s, 'steel', (X(-0.35), y, z), RX, r2=0.15 * s)       # engine
    b.cyl(1.36 * s, 0.75 * s, sm, (X(0), y, z), RX, r2=1.15 * s, seg=16)        # flared aft
    b.cyl(1.1 * s, 1.7 * s, sm, (X(0.75), y, z), RX, seg=16)                    # instrument
    b.cyl(1.14 * s, 0.12 * s, 'silver', (X(1.2), y, z), RX, seg=16)
    b.cyl(1.08 * s, 2.1 * s, dm, (X(2.45), y, z), RX, r2=0.62 * s, seg=16)     # descent module
    b.sph(1.12 * s, om, (X(5.75), y, z), seg=16, rings=10, scale=(1.25, 1, 1))  # orbital module
    b.cyl(0.32 * s, 0.45 * s, 'silver', (X(7.1), y, z), RX, r2=0.18 * s, seg=10)  # docking probe
    b.cyl(0.22 * s, 0.25 * s, 'glass', (X(3.4), y - 0.85 * s, z + 0.3 * s), (pi / 2, 0, 0), seg=8)
    if panels:
        for sg in (-1, 1):
            b.box(0.12 * s, 0.6 * s, 0.12 * s, 'steel', (X(1.6), y + sg * 1.4 * s, z - 0.06 * s))
            for k in range(4):
                b.box(1.15 * s, 1.0 * s, 0.05 * s, 'panel',
                      (X(1.6), y + sg * (1.9 + k * 1.05) * s, z - 0.025 * s))
    return X(7.5)


def strip_bands(b, r, zs, m='dark', h=0.08, seg=16):
    for zz in zs:
        b.cyl(r * 1.01, h, m, (0, 0, zz), seg=seg)


def boosters(b, n, ring_r, r, h, z0, m, cone_h=0.6, tilt=0.0, phase=0.0, mtop=None, seg=10):
    for i in range(n):
        a = phase + i * 2 * pi / n
        x, y = ring_r * math.cos(a), ring_r * math.sin(a)
        b.cyl(r * 1.12, 0.3, 'steel', (x, y, z0 - 0.3), r2=r * 0.7, seg=8)
        b.cyl(r, h, m, (x, y, z0), seg=seg)
        b.cyl(r, cone_h, mtop or m, (x, y, z0 + h), r2=0.02, seg=seg)


def fins(b, n, r, z0, h, w, m, t=0.04, phase=pi / 4):
    for i in range(n):
        a = phase + i * 2 * pi / n
        b.prism([(0, 0), (w, 0), (0, h)], -t / 2, t / 2, m,
                loc=(r * math.cos(a), r * math.sin(a), z0), rot=(pi / 2, 0, a))


def dish(b, r, depth, m, loc, rot=(0, 0, 0)):
    b.cyl(r, depth, m, loc, rot, r2=0.06, seg=16, cap=False)
    b.cyl(r * 1.02, 0.03, m, loc, rot, seg=16)


def pad(b, sx=4.0, sy=4.0, h=0.7):
    b.box(sx, sy, h, 'concrete')
    b.box(sx * 0.35, sy * 1.02, h * 0.6, 'dark', (0, 0, h * 0.42))   # flame trench
    return h


# ------------------------------------------------------------- exhibits
def ex_sputnik1(b):
    z = pole_stand(b, 1.0, 0.35)
    b.sph(0.29, 'silver', (0, 0, z + 0.25), seg=16, rings=10)
    b.cyl(0.3, 0.03, 'steel', (0, 0, z + 0.24), seg=16)
    for k, (a, l) in enumerate([(0.55, 2.4), (-0.55, 2.4), (0.35, 2.9), (-0.35, 2.9)]):
        zz = z + 0.25 + (0.12 if k < 2 else -0.12)
        b.tube((0, 0.2, zz), (l * math.sin(a), 0.2 + l * math.cos(a), zz - 0.5), 0.012, 'steel', 4)


def ex_vostok(b):
    b.box(2.2, 2.2, 0.25, 'stand')
    for sx in (-0.7, 0.7):
        b.box(0.12, 1.6, 0.55, 'steel', (sx, 0, 0.25))
    b.sph(1.15, 'char', (0, 0, 1.55), seg=18, rings=12)
    b.cyl(0.52, 0.08, 'dark', (0, -1.1, 1.75), (pi / 2, 0, 0), seg=16)        # hatch
    b.cyl(0.18, 0.06, 'glass', (0.55, -0.95, 1.2), (pi / 2.6, 0, 0.5), seg=10)
    b.sph(0.3, 'mlibrown', (0, 0.35, 2.55), seg=10, rings=6, scale=(1, 1, 0.5))
    b.box(0.6, 0.3, 0.2, 'stand', (1.4, -0.6, 0))                              # label stand


def dog(b, x, y, z, fur, spots=None, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    def P(dx, dy, dz): return (x + dx * c - dy * s, y + dx * s + dy * c, z + dz)
    b.sph(0.17, fur, P(0, 0, 0.32), seg=10, rings=6, scale=(1.7, 0.95, 0.95), rot=(0, 0, rot))
    for dx in (-0.17, 0.17):
        for dy in (-0.08, 0.08):
            b.cyl(0.04, 0.24, fur, P(dx, dy, 0), seg=6)
    b.sph(0.12, fur, P(0.33, 0, 0.47), seg=10, rings=6)
    b.sph(0.06, spots or fur, P(0.44, 0, 0.44), seg=8, rings=5, scale=(1.2, 0.9, 0.8))
    for dy in (-0.06, 0.06):
        b.cyl(0.04, 0.12, spots or fur, P(0.3, dy, 0.54), r2=0.0, seg=6)
    b.tube(P(-0.27, 0, 0.36), P(-0.42, 0, 0.5), 0.025, fur, 5)


def ex_container(b):
    b.box(2.8, 1.8, 0.22, 'stand')
    b.cyl(0.48, 1.4, 'steel', (-0.95, 0.15, 0.75), RX, seg=14)
    b.sph(0.48, 'steel', (-0.95, 0.15, 0.75), seg=14, rings=8, scale=(0.5, 1, 1))
    b.sph(0.48, 'steel', (0.45, 0.15, 0.75), seg=14, rings=8, scale=(0.5, 1, 1))
    b.cyl(0.5, 0.08, 'dark', (-0.3, 0.15, 0.75), RX, seg=14)
    for sx in (-0.6, 0.2):
        b.box(0.1, 0.8, 0.5, 'silver', (sx, 0.15, 0.22))
    dog(b, 0.65, -0.45, 0.22, 'white', 'tan', rot=2.6)
    dog(b, 1.05, -0.05, 0.22, 'cream', 'brown', rot=2.9)


def ex_sk1(b):
    podium(b, 0.6, 0.25)
    suit(b, 'orange', 'white', 'glass', z=0.25, flag=True)


def ex_berkut(b):
    podium(b, 0.6, 0.25)
    suit(b, 'offwhite', 'silver', 'gold', back='offwhite', z=0.25)


def ex_yastreb(b):
    podium(b, 0.6, 0.25)
    suit(b, 'white', 'grey', 'gold', back='grey', z=0.25)
    b.box(0.26, 0.1, 0.22, 'orange', (0, -0.26, 1.35))


def ex_orlan(b):
    podium(b, 0.65, 0.25)
    suit(b, 'white', 'silver', 'gold', back='white', hard=True, z=0.25)
    b.box(0.6, 0.35, 0.8, 'white', (0, 0.4, 1.0))


def ex_krechet(b):
    podium(b, 0.7, 0.25)
    suit(b, 'white', 'orange', 'gold', hard=True, z=0.25)
    b.box(0.62, 0.42, 0.9, 'offwhite', (0, 0.42, 0.95))
    b.ring(0.32, 0.27, 0.05, 'steel', (0, 0, 1.02), seg=12)


def ex_venera1(b):
    z = pole_stand(b, 0.7, 0.4)
    b.cyl(0.5, 1.4, 'silver', (0, 0, z), seg=12)
    b.sph(0.5, 'silver', (0, 0, z + 1.4), seg=12, rings=8, scale=(1, 1, 0.6))
    for s in (-1, 1):
        b.box(1.1, 0.04, 0.9, 'panel', (s * 1.1, 0, z + 0.4))
        b.tube((s * 0.5, 0, z + 0.85), (s * 0.6, 0, z + 0.85), 0.03, 'steel', 4)
    dish(b, 1.0, 0.28, 'silver', (0, 0.45, z + 1.6), (-0.4, 0, 0))
    b.tube((0, 0, z + 1.7), (0, -0.2, z + 3.0), 0.015, 'steel', 4)


def ex_luna9(b):
    z = pole_stand(b, 0.75, 0.35)
    b.sph(0.3, 'silver', (0, 0, z + 0.3), seg=14, rings=8)
    for i in range(4):
        a = i * pi / 2 + pi / 4
        b.prism([(-0.2, 0), (0.2, 0), (0, 0.55)], 0, 0.02, 'silver',
                loc=(0.25 * math.cos(a), 0.25 * math.sin(a), z + 0.18), rot=(1.2, 0, a - pi / 2))
        b.tube((0.1 * math.cos(a), 0.1 * math.sin(a), z + 0.5),
               (0.35 * math.cos(a + 0.4), 0.35 * math.sin(a + 0.4), z + 1.1), 0.01, 'steel', 4)


def ex_gird09(b):
    b.box(0.9, 0.9, 0.2, 'stand')
    b.box(0.08, 0.08, 1.4, 'steel', (0.2, 0, 0.2))
    z = b.stack([(0.09, 0.09, 1.8, 'silver'), (0.09, 0.0, 0.45, 'red')], 0, 0, 0.35, seg=10)
    fins(b, 4, 0.09, 0.35, 0.45, 0.25, 'red', t=0.02)


def ex_veranda(b):
    b.box(4.4, 3.2, 0.2, 'darkwood')
    b.box(4.2, 3.0, 0.04, 'wood', (0, 0, 0.2))
    b.box(4.4, 0.12, 2.4, 'cream', (0, 1.55, 0.2))
    b.box(0.12, 3.2, 2.4, 'cream', (-2.15, 0, 0.2))
    for wx in (-1.2, 0.0, 1.2):
        b.box(0.9, 0.06, 1.2, 'glass', (wx, 1.5, 0.95))
        b.box(0.06, 0.08, 1.2, 'white', (wx, 1.48, 0.95))
        b.box(0.9, 0.08, 0.06, 'white', (wx, 1.48, 1.55))
    b.box(1.4, 0.7, 0.75, 'darkwood', (0.6, 0.9, 0.24))
    b.box(1.5, 0.8, 0.05, 'wood', (0.6, 0.9, 0.99))
    b.box(0.5, 0.4, 0.3, 'cream', (0.3, 0.9, 1.04))
    b.box(0.5, 0.5, 0.45, 'wood', (0.6, 0.2, 0.24))
    b.box(0.5, 0.06, 0.6, 'wood', (0.6, 0.45, 0.69))
    b.box(0.5, 1.4, 1.8, 'darkwood', (-1.75, 0.3, 0.24))
    b.cyl(0.05, 1.2, 'brown', (1.6, -0.6, 0.24), (0.35, 0, 0), r2=0.04, seg=6)
    b.cyl(0.25, 0.25, 'gold', (1.6, -0.25, 1.2), (1.1, 0, 0), r2=0.06, seg=10)   # ear-trumpet
    b.cyl(0.04, 0.6, 'red', (0.95, 0.9, 1.04), seg=6, r2=0.0)                     # rocket model


def ex_soyuz45_fixed(b):
    z = pole_stand(b, 1.1, 0.6)
    s = 0.33
    from mathutils import Matrix
    T0 = b.T
    soyuz(b, s, x0=-7.55 * s, z=z + 0.55)
    b.T = T0 @ Matrix.Rotation(pi, 4, 'Z')
    soyuz(b, s, x0=-7.55 * s, z=z + 0.55, om='cream', dm='khaki')
    b.T = T0


def ex_mir(b):
    from mathutils import Matrix
    for x in (-3.5, 0.5, 4.5):
        b.box(0.5, 2.6, 0.9, 'steel', (x, 0, 0))
    z = 2.4
    b.cyl(1.45, 4.2, 'white', (-5.2, 0, z), RX, seg=18)
    b.cyl(1.45, 1.1, 'offwhite', (-1.0, 0, z), RX, r2=2.07, seg=18)
    b.cyl(2.07, 5.6, 'white', (0.1, 0, z), RX, seg=20)
    for xx in (1.2, 3.0, 4.6):
        b.cyl(2.1, 0.12, 'offwhite', (xx, 0, z), RX, seg=20)
    b.cyl(1.4, 0.8, 'offwhite', (5.7, 0, z), RX, r2=0.7, seg=14)
    b.cyl(0.55, 0.5, 'silver', (6.5, 0, z), RX, seg=10)
    b.sph(1.15, 'offwhite', (-6.3, 0, z), seg=14, rings=10)
    for d in [(-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1)]:
        rot = {(-1, 0, 0): (0, -pi / 2, 0), (0, 1, 0): (-pi / 2, 0, 0), (0, -1, 0): (pi / 2, 0, 0),
               (0, 0, 1): (0, 0, 0)}[d]
        b.cyl(0.5, 1.4, 'silver', (-6.3, 0, z), rot, seg=10)
    b.cyl(0.25, 0.9, 'white', (-1.5, 0, z + 1.6), seg=8)
    dish(b, 0.5, 0.18, 'silver', (-1.5, 0, z + 2.6))


def ex_shso(b):
    for x in (-0.8, 0.8):
        b.box(0.35, 1.8, 0.7, 'steel', (x, 0, 0))
    b.cyl(1.0, 2.4, 'white', (-1.2, 0, 1.7), RX, seg=16)
    b.cyl(1.0, 0.3, 'offwhite', (1.2, 0, 1.7), RX, r2=0.6, seg=16)
    b.cyl(0.55, 0.1, 'silver', (-0.2, -1.0, 1.9), (pi / 2, 0, 0), seg=14)


def ex_luna16(b):
    podium(b, 1.6, 0.2)
    z = 0.2
    for i in range(4):
        a = i * pi / 2 + pi / 4
        x, y = 1.25 * math.cos(a), 1.25 * math.sin(a)
        b.cyl(0.22, 0.06, 'silver', (x, y, z), seg=10)
        b.tube((x, y, z + 0.05), (0.6 * math.cos(a), 0.6 * math.sin(a), z + 1.0), 0.05, 'steel', 6)
        b.sph(0.38, 'gold', (0.62 * math.cos(a + pi / 4), 0.62 * math.sin(a + pi / 4), z + 1.0), seg=10, rings=6)
    b.cyl(0.75, 0.5, 'foil', (0, 0, z + 0.75), seg=8)
    b.box(0.9, 0.9, 0.5, 'silver', (0, 0, z + 1.25))
    b.cyl(0.3, 0.9, 'gold', (0, 0, z + 1.75), seg=10)
    for i in range(3):
        a = i * 2 * pi / 3
        b.sph(0.18, 'silver', (0.35 * math.cos(a), 0.35 * math.sin(a), z + 2.0), seg=8, rings=5)
    b.sph(0.26, 'char', (0, 0, z + 2.9), seg=12, rings=8)
    for s in (-1, 1):
        b.tube((s * 0.4, 0, z + 1.6), (s * 1.0, 0, z + 2.6), 0.015, 'steel', 4)


def ex_lunokhod(b):
    podium(b, 2.0, 0.2)
    z = 0.2
    for i, x in enumerate((-0.8, -0.27, 0.27, 0.8)):
        for y in (-0.82, 0.82):
            b.cyl(0.26, 0.14, 'steel', (x, y - 0.07, z + 0.26), (-pi / 2, 0, 0), seg=10)
            b.ring(0.26, 0.2, 0.15, 'dark', (x, y - 0.075, z + 0.26), (-pi / 2, 0, 0), seg=10)
    b.cyl(0.62, 0.5, 'silver', (0, 0, z + 0.38), r2=0.86, seg=12, scale=(1.35, 1, 1))
    b.cyl(0.88, 0.06, 'steel', (0, 0, z + 0.88), seg=12, scale=(1.35, 1, 1))
    b.cyl(0.86, 0.05, 'panel', (-0.35, 0, z + 1.35), (0, -1.05, 0), seg=12, scale=(1.0, 1, 1))
    b.box(0.15, 0.1, 0.12, 'black', (1.05, -0.25, z + 0.75))
    b.box(0.15, 0.1, 0.12, 'black', (1.05, 0.25, z + 0.75))
    b.cyl(0.04, 0.6, 'steel', (0.6, 0.5, z + 0.9), seg=5)
    b.cyl(0.18, 0.3, 'silver', (0.6, 0.5, z + 1.5), r2=0.0, seg=8)
    b.tube((0.75, -0.55, z + 0.9), (0.95, -0.7, z + 1.6), 0.015, 'steel', 4)


def ex_mars3(b):
    z = pole_stand(b, 0.6, 0.6)
    b.cyl(1.6, 0.5, 'white', (0, 0, z), r2=0.5, seg=16)
    b.cyl(1.62, 0.06, 'steel', (0, 0, z), seg=16)
    b.sph(0.6, 'silver', (0, 0, z + 0.9), seg=14, rings=8, scale=(1, 1, 0.85))
    b.cyl(0.62, 0.08, 'gold', (0, 0, z + 0.85), seg=14)
    for i in range(4):
        a = i * pi / 2
        b.prism([(-0.2, 0), (0.2, 0), (0, 0.4)], 0, 0.02, 'silver',
                loc=(0.45 * math.cos(a), 0.45 * math.sin(a), z + 1.1), rot=(0.5, 0, a - pi / 2))


def ex_venera4(b):
    z = pole_stand(b, 0.5, 0.4)
    b.sph(0.5, 'char', (0, 0, z + 0.5), seg=14, rings=9)
    b.cyl(0.52, 0.08, 'silver', (0, 0, z + 0.55), seg=14)
    b.cyl(0.25, 0.3, 'silver', (0, 0, z + 0.95), seg=10)
    b.tube((0, 0, z + 1.2), (0, 0, z + 2.0), 0.02, 'steel', 4)


def ex_glonass(b):
    z = pole_stand(b, 1.6, 0.5)
    b.box(1.2, 1.2, 0.25, 'white', (0, 0, z))
    for i in range(3):
        for j in range(3):
            b.cyl(0.08, 0.25, 'silver', (-0.35 + i * 0.35, -0.35 + j * 0.35, z - 0.2), seg=6)
    b.cyl(0.62, 1.7, 'gold', (0, 0, z + 0.25), seg=12)
    b.sph(0.62, 'gold', (0, 0, z + 1.95), seg=12, rings=6, scale=(1, 1, 0.4))
    for s in (-1, 1):
        b.tube((0, s * 0.6, z + 1.2), (0, s * 1.2, z + 1.2), 0.04, 'steel', 5)
        for k in range(2):
            b.box(1.3, 1.6, 0.04, 'panel', (0, s * (2.05 + k * 1.65), z + 1.18), (0, 0.25, 0))


def ex_soyuz_apollo(b):
    z = pole_stand(b, 1.4, 0.6) + 0.6
    s = 0.36
    soyuz(b, s, x0=-7.6 * s - 1.0, z=z)
    b.cyl(0.36, 1.1, 'silver', (-1.0, 0, z), RX, seg=12)                       # docking module
    b.cyl(0.7, 1.05, 'silver', (0.1, 0, z), RX, r2=0.15, seg=14)               # Apollo CM (apex fwd->)
    b.cyl(0.7, 0.05, 'steel', (1.12, 0, z), RX, seg=14)
    b.cyl(0.7, 2.6, 'white', (1.15, 0, z), RX, seg=14)                        # SM
    for xx in (1.6, 2.6, 3.4):
        b.cyl(0.71, 0.05, 'dark', (xx, 0, z), RX, seg=14)
    b.cyl(0.18, 0.9, 'steel', (3.75, 0, z), RX, r2=0.4, seg=12)                # SPS bell
    b.box(0.3, 0.3, 0.2, 'silver', (2.3, 0.75, z - 0.1))


def ex_soyuz37(b):
    b.box(2.6, 2.6, 0.22, 'stand')
    b.ring(1.0, 0.85, 0.35, 'steel', (0, 0, 0.22), seg=16)
    b.cyl(1.08, 1.9, 'char', (0, 0, 0.45), r2=0.6, seg=16)
    b.cyl(0.62, 0.15, 'mlibrown', (0, 0, 2.35), seg=14)
    b.cyl(0.3, 0.15, 'dark', (0, 0, 2.5), seg=12)
    b.cyl(0.2, 0.06, 'glass', (0.85, -0.3, 1.0), (0, 1.1, -0.3), seg=8)


def ex_apas(b):
    podium(b, 1.2, 0.2)
    b.cyl(0.95, 0.7, 'silver', (0, 0, 0.2), seg=16)
    b.ring(0.95, 0.68, 0.18, 'steel', (0, 0, 0.9), seg=16)
    for i in range(3):
        a = i * 2 * pi / 3
        b.prism([(-0.32, 0), (0.32, 0), (0, 0.55)], 0, 0.04, 'silver',
                loc=(0.78 * math.cos(a), 0.78 * math.sin(a), 1.05), rot=(1.25, 0, a - pi / 2))
    for i in range(6):
        a = i * pi / 3 + 0.3
        b.tube((0.5 * math.cos(a), 0.5 * math.sin(a), 0.9), (0.7 * math.cos(a + 0.5), 0.7 * math.sin(a + 0.5), 0.3),
               0.03, 'steel', 5)


def ex_iss(b):
    z = pole_stand(b, 2.6, 0.7, 0.07) + 0.2
    b.box(10.0, 0.35, 0.35, 'silver', (0, 0, z))
    for x in (-4.4, -3.4, 3.4, 4.4):
        for s in (-1, 1):
            b.box(0.75, 3.0, 0.03, 'foil', (x, s * 1.75, z + 0.16))
        b.box(0.15, 0.4, 0.15, 'steel', (x, 0, z + 0.33))
    for x in (-1.8, 1.8):
        b.box(0.05, 1.6, 1.4, 'white', (x, 0, z - 1.3))
    b.cyl(0.32, 4.2, 'white', (0, -2.6, z - 0.5), (-pi / 2, 0, 0), seg=10)
    b.cyl(0.32, 1.2, 'white', (0, 0.4, z - 0.5), (-pi / 2, 0, 0), seg=10)
    for y, l in ((-1.2, 1.4), (-2.0, 1.2)):
        b.cyl(0.3, l, 'offwhite', (0, y, z - 0.5), RX, seg=10)
        b.cyl(0.3, l, 'offwhite', (0, y, z - 0.5), (0, -pi / 2, 0), seg=10)
    for s in (-1, 1):
        b.box(0.5, 1.6, 0.03, 'panel', (0.0, -3.6, z - 0.5 + s * 0.0), (0, 0, 0))
    b.sph(0.35, 'white', (0, -1.2, z - 0.5), seg=10, rings=6)


def ex_cospas(b):
    z = pole_stand(b, 1.2, 0.45)
    b.cyl(0.5, 1.1, 'panel', (0, 0, z), seg=8)
    b.cyl(0.52, 0.08, 'gold', (0, 0, z + 0.5), seg=8)
    b.cyl(0.5, 0.3, 'gold', (0, 0, z + 1.1), r2=0.25, seg=8)
    b.tube((0, 0, z + 1.4), (0, 0, z + 3.0), 0.03, 'steel', 5)
    b.sph(0.1, 'silver', (0, 0, z + 3.0), seg=8, rings=5)
    for i in range(4):
        a = i * pi / 2
        b.tube((0.3 * math.cos(a), 0.3 * math.sin(a), z), (0.9 * math.cos(a), 0.9 * math.sin(a), z - 0.6), 0.015, 'steel', 4)


def r7(b, z0=0.0, scale=1.0, main='offwhite', band='khaki'):
    """Soyuz / R-7 family launcher, base at z0."""
    s = scale
    b.cyl(0.26 * s, 3.2 * s, main, (0, 0, z0 + 0.25 * s), r2=0.31 * s, seg=12)
    b.cyl(0.31 * s, 0.4 * s, main, (0, 0, z0 + 3.45 * s), r2=0.27 * s, seg=12)
    for i in range(4):
        a = i * pi / 2 + pi / 4
        x, y = 0.48 * s * math.cos(a), 0.48 * s * math.sin(a)
        b.cyl(0.25 * s, 0.25 * s, 'steel', (x, y, z0), r2=0.2 * s, seg=8)
        b.cyl(0.31 * s, 2.3 * s, main, (x, y, z0 + 0.25 * s), r2=0.12 * s, seg=10)
        b.cyl(0.12 * s, 0.45 * s, main, (x * 0.72, y * 0.72, z0 + 2.55 * s), r2=0.02 * s, seg=8)
        b.box(0.03 * s, 0.25 * s, 0.25 * s, band, (x * 1.3, y * 1.3, z0 + 0.3 * s), (0, 0, a))
    b.cyl(0.27 * s, 1.1 * s, band, (0, 0, z0 + 3.85 * s), seg=12)
    b.cyl(0.33 * s, 0.9 * s, 'white', (0, 0, z0 + 4.95 * s), seg=12)
    b.cyl(0.33 * s, 0.7 * s, 'white', (0, 0, z0 + 5.85 * s), r2=0.08 * s, seg=12)
    b.tube((0, 0, z0 + 6.5 * s), (0, 0, z0 + 7.2 * s), 0.035 * s, 'red', 5)
    return z0 + 7.2 * s


def ex_baikonur(b):
    h = pad(b, 4.6, 4.6, 0.8)
    top = r7(b, h + 0.15, 1.0)
    for i in range(4):
        a = i * pi / 2 + pi / 4
        b.tube((1.5 * math.cos(a), 1.5 * math.sin(a), h), (0.6 * math.cos(a), 0.6 * math.sin(a), h + 3.0), 0.07, 'steel', 6)
    b.truss(0.9, 0.9, 5.2, 'red', (-1.9, 1.5, h), bar=0.07, levels=5)
    b.box(1.2, 1.2, 0.15, 'red', (-1.9, 1.5, h + 5.2))
    b.truss(0.8, 0.8, 4.0, 'steel', (1.9, -1.6, h), bar=0.06, levels=4)


def ex_shuttle(b):
    h = pad(b, 4.8, 4.8, 0.7)
    b.truss(1.1, 1.1, 8.2, 'red', (1.6, 1.4, h), bar=0.08, levels=7)
    b.box(1.6, 1.6, 0.25, 'red', (1.6, 1.4, h + 8.2))
    b.tube((1.6, 1.4, h + 8.4), (1.6, 1.4, h + 9.3), 0.05, 'steel', 5)
    b.box(1.2, 0.12, 0.12, 'steel', (1.0, 0.9, h + 6.4))
    z = h + 0.6
    b.cyl(0.5, 4.6, 'orange', (0, 0, z), seg=14)
    b.cyl(0.5, 1.0, 'orange', (0, 0, z + 4.6), r2=0.02, seg=14)
    for y in (-0.72, 0.72):
        b.cyl(0.22, 0.4, 'steel', (0, y, z - 0.45), r2=0.18, seg=8)
        b.cyl(0.21, 4.3, 'white', (0, y, z - 0.05), seg=10)
        b.cyl(0.21, 0.55, 'white', (0, y, z + 4.25), r2=0.02, seg=10)
    ox = -0.95
    b.cyl(0.3, 3.0, 'white', (ox, 0, z + 0.3), seg=10, scale=(1, 1.2, 1))
    b.cyl(0.3, 0.7, 'black', (ox, 0, z + 3.3), r2=0.05, seg=10, scale=(1, 1.2, 1))
    b.prism([(-0.25, 0.0), (1.6, 0.0), (-0.25, 2.2)], -0.04, 0.04, 'white', loc=(ox, 0, z + 0.3),
            rot=(pi / 2, 0, -pi / 2))
    b.prism([(0.25, 0.0), (-1.6, 0.0), (0.25, 2.2)], -0.04, 0.04, 'white', loc=(ox, 0, z + 0.3),
            rot=(pi / 2, 0, -pi / 2))
    b.prism([(0, 0), (0.75, 0), (0.0, 0.9)], -0.03, 0.03, 'white', loc=(ox - 0.3, 0, z + 0.4),
            rot=(pi / 2, -pi / 2, 0))
    b.box(0.08, 0.5, 0.5, 'black', (ox + 0.28, 0, z + 0.8))


def ex_proton(b):
    podium(b, 1.4, 0.25)
    z = 0.6
    b.cyl(0.33, 2.4, 'white', (0, 0, z), seg=12)
    for i in range(6):
        a = i * pi / 3
        x, y = 0.6 * math.cos(a), 0.6 * math.sin(a)
        b.cyl(0.18, 0.35, 'steel', (x, y, z - 0.35), r2=0.14, seg=8)
        b.cyl(0.24, 2.2, 'offwhite', (x, y, z), seg=10)
        b.cyl(0.24, 0.35, 'offwhite', (x, y, z + 2.2), r2=0.05, seg=10)
    b.box(0.25, 0.06, 0.1, 'steel', (0, 0, 0.25))
    for i in range(3):
        a = i * 2 * pi / 3
        b.tube((0, 0, 0.25), (0.6 * math.cos(a), 0.6 * math.sin(a), 0.6), 0.04, 'steel', 5)
    zz = b.stack([(0.33, 0.33, 2.0, 'white'), (0.33, 0.33, 0.1, 'dark'), (0.33, 0.33, 1.0, 'white'),
                  (0.36, 0.36, 1.2, 'white'), (0.36, 0.06, 0.8, 'white')], 0, 0, z + 2.4, seg=12)


def ex_sealaunch(b):
    b.cyl(3.2, 0.12, 'sea', seg=24, scale=(1.25, 1, 1))
    for y in (-1.3, 1.3):
        b.box(5.6, 0.75, 0.55, 'red', (0, y, 0.1))
        for x in (-1.8, 1.8):
            b.cyl(0.28, 1.2, 'white', (x, y, 0.6), seg=10)
    b.box(4.4, 3.4, 0.35, 'white', (0, 0, 1.8))
    b.box(1.6, 3.0, 0.9, 'offwhite', (-1.4, 0, 2.15))
    b.box(0.6, 0.6, 0.4, 'steel', (1.0, 0, 2.15))
    z = 2.55
    b.stack([(0.3, 0.3, 3.4, 'offwhite'), (0.3, 0.3, 0.1, 'navy'), (0.3, 0.3, 1.1, 'offwhite'),
             (0.34, 0.34, 0.9, 'white'), (0.34, 0.05, 0.6, 'white')], 1.0, 0, z, seg=12)
    b.truss(0.5, 0.5, 4.0, 'steel', (1.6, 0.8, z), bar=0.05, levels=4)


def ex_longmarch(b):
    podium(b, 1.3, 0.25)
    z = 0.55
    b.cyl(0.3, 4.0, 'white', (0, 0, z), seg=12)
    strip_bands(b, 0.3, [z + 3.0, z + 3.3], 'red', 0.06)
    for i in range(4):
        a = i * pi / 2
        x, y = 0.5 * math.cos(a), 0.5 * math.sin(a)
        b.cyl(0.16, 0.3, 'steel', (x, y, z - 0.3), r2=0.12, seg=8)
        b.cyl(0.18, 2.3, 'white', (x, y, z), seg=10)
        b.cyl(0.18, 0.55, 'white', (x, y, z + 2.3), r2=0.03, seg=10)
    b.cyl(0.3, 1.2, 'white', (0, 0, z + 4.0), seg=12)
    b.cyl(0.4, 1.0, 'white', (0, 0, z + 5.2), seg=12)
    b.cyl(0.4, 0.8, 'white', (0, 0, z + 6.2), r2=0.08, seg=12)
    b.tube((0, 0, z + 6.9), (0, 0, z + 7.7), 0.05, 'red', 5)
    for i in range(4):
        a = i * pi / 2 + pi / 4
        b.box(0.05, 0.25, 0.3, 'white', (0.45 * math.cos(a), 0.45 * math.sin(a), z + 5.6), (0, 0, a))


def ex_rd107(b):
    podium(b, 1.0, 0.3)
    z = 0.3
    for x, y in ((-0.25, -0.25), (0.25, -0.25), (0.25, 0.25), (-0.25, 0.25)):
        b.cyl(0.24, 0.85, 'copper', (x, y, z), r2=0.11, seg=12)
    for x in (-0.62, 0.62):
        b.cyl(0.11, 0.5, 'copper', (x, 0, z + 0.3), r2=0.05, seg=8)
    b.box(0.95, 0.95, 0.15, 'steel', (0, 0, z + 0.85))
    b.cyl(0.25, 0.6, 'steel', (0, 0, z + 1.0), seg=10)
    b.cyl(0.18, 0.4, 'silver', (0.25, 0.1, z + 1.6), RX, seg=8)
    for i in range(4):
        a = i * pi / 2
        b.tube((0.4 * math.cos(a), 0.4 * math.sin(a), z + 1.0), (0.1 * math.cos(a), 0.1 * math.sin(a), z + 1.9),
               0.03, 'steel', 5)


def ex_explorer1(b):
    b.box(0.7, 0.7, 0.2, 'stand')
    b.box(0.06, 0.06, 1.0, 'steel', (0, 0, 0.2))
    z = b.stack([(0.08, 0.08, 0.5, 'white'), (0.08, 0.08, 0.6, 'dark'), (0.08, 0.08, 0.15, 'white'),
                 (0.08, 0.08, 0.35, 'dark'), (0.08, 0.0, 0.3, 'silver')], 0, 0, 1.1, seg=10)
    for i in range(4):
        a = i * pi / 2
        b.tube((0, 0, 1.65), (0.45 * math.cos(a), 0.45 * math.sin(a), 1.4), 0.008, 'steel', 4)


def ex_energia_buran(b):
    h = pad(b, 5.0, 5.0, 0.6)
    z = h + 0.6
    b.cyl(0.62, 6.6, 'tan', (0, 0, z), seg=14)
    b.cyl(0.62, 1.3, 'tan', (0, 0, z + 6.6), r2=0.05, seg=14)
    strip_bands(b, 0.62, [z + 1.0, z + 4.0], 'dark', 0.1)
    for i in range(4):
        a = pi / 2 + (i - 1.5) * 0.62
        x, y = 1.05 * math.cos(a), 1.05 * math.sin(a)
        b.cyl(0.28, 0.4, 'steel', (x, y, z - 0.45), r2=0.22, seg=8)
        b.cyl(0.32, 5.0, 'grey', (x, y, z - 0.05), seg=10)
        b.cyl(0.32, 0.8, 'grey', (x, y, z + 4.95), r2=0.04, seg=10)
    oy = -0.98
    b.cyl(0.38, 3.8, 'white', (0, oy, z + 0.6), seg=12, scale=(1.15, 1, 1))
    b.cyl(0.38, 0.9, 'black', (0, oy, z + 4.4), r2=0.06, seg=12, scale=(1.15, 1, 1))
    b.prism([(-2.0, 0.0), (2.0, 0.0), (0.0, 2.9)], -0.05, 0.05, 'white', loc=(0, oy, z + 0.6), rot=(0, 0, 0))
    b.prism([(-1.8, 0.02), (1.8, 0.02), (0.0, 2.6)], -0.06, 0.06, 'black', loc=(0, oy + 0.01, z + 0.6))
    b.prism([(0, 0), (0.0, 1.0), (0.85, 0.0)], -0.04, 0.04, 'white', loc=(0, oy - 0.38, z + 0.7), rot=(pi / 2, 0, -pi / 2))
    b.truss(1.0, 1.0, 7.5, 'steel', (-2.0, 1.4, h), bar=0.07, levels=6)


def ex_soyuz_full(b):
    for x in (0.8, 3.0, 5.6):
        b.box(0.5, 1.8, 0.75, 'steel', (x, 0, 0))
    soyuz(b, 1.0, x0=0.0, z=1.85)


def ex_painting(b):
    b.box(0.5, 0.5, 0.6, 'darkwood')
    b.box(0.12, 3.4, 2.5, 'gold', (0, 0, 0.6))
    b.box(0.14, 3.0, 2.1, 'navy', (0, 0, 0.8))
    b.box(0.15, 3.0, 0.7, 'grey', (0, 0, 0.8))
    b.sph(0.35, 'cream', (0.05, 0.8, 2.3), seg=10, rings=6, scale=(0.3, 1, 1))
    b.box(0.16, 0.25, 0.7, 'white', (0, -0.3, 1.4))
    b.sph(0.13, 'white', (0, -0.3, 2.2), seg=8, rings=5)
    b.box(0.16, 0.02, 0.6, 'steel', (0, 0.25, 1.4))
    b.box(0.17, 0.4, 0.25, 'red', (0, 0.25, 1.95))


def ex_saturn5(b):
    podium(b, 1.4, 0.3)
    z = 0.5
    b.cyl(0.55, 3.4, 'white', (0, 0, z), seg=14)
    for i in range(4):
        a = i * pi / 2 + pi / 4
        b.box(0.12, 0.3, 1.2, 'black', (0.52 * math.cos(a), 0.52 * math.sin(a), z), (0, 0, a))
        b.cyl(0.18, 0.3, 'steel', (0.3 * math.cos(a), 0.3 * math.sin(a), z - 0.2), r2=0.12, seg=8)
    fins(b, 4, 0.55, z - 0.2, 0.7, 0.35, 'white', t=0.06)
    strip_bands(b, 0.55, [z + 3.0], 'black', 0.25)
    b.cyl(0.55, 2.8, 'white', (0, 0, z + 3.45), seg=14)
    strip_bands(b, 0.55, [z + 6.05], 'black', 0.18)
    b.cyl(0.55, 0.6, 'white', (0, 0, z + 6.25), r2=0.36, seg=14)
    b.cyl(0.36, 1.7, 'white', (0, 0, z + 6.85), seg=12)
    b.cyl(0.36, 0.25, 'black', (0, 0, z + 7.6), seg=12)
    b.cyl(0.36, 0.8, 'white', (0, 0, z + 8.55), r2=0.3, seg=12)
    b.cyl(0.3, 0.5, 'silver', (0, 0, z + 9.35), r2=0.08, seg=12)
    b.tube((0, 0, z + 9.85), (0, 0, z + 10.7), 0.04, 'red', 5)


# ------------------------------------------------------------- landmarks / amenities
def lm_monument(b, H=42.0):
    """«Покорителям космоса»: curved titanium plume with rocket on top."""
    from mathutils import Vector
    b.prism([(-14, -9), (14, -9), (11, 9), (-11, 9)], 0, 3.2, 'plinth', mtop='floor')
    b.prism([(-12.5, -9.4), (12.5, -9.4), (12.5, -9.0), (-12.5, -9.0)], 0.6, 2.8, 'titan')
    n, seg = 24, 10
    bm = b.bm
    rings = []
    for k in range(n + 1):
        t = k / n
        z = 3.2 + H * t
        x = -9.0 * (1 - t) ** 2.2
        w = 7.0 * (1 - t) ** 1.25 + 0.55
        d = 2.6 * (1 - t) ** 1.25 + 0.55
        ring = []
        for i in range(seg):
            a = i * 2 * math.pi / seg
            ring.append(bm.verts.new(b.T @ Vector((x + w * math.cos(a) * 0.5, d * math.sin(a), z))))
        rings.append(ring)
    n0 = len(bm.faces)
    for r0, r1 in zip(rings[:-1], rings[1:]):
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    bm.faces.new(rings[-1])
    bm.faces.new(rings[0][::-1])
    b._tag(n0, 'titan', verts=[v for r in rings for v in r])
    top = 3.2 + H
    b.cyl(0.55, 2.4, 'titan', (0, 0, top), seg=10)
    b.cyl(0.55, 1.8, 'titan', (0, 0, top + 2.4), r2=0.02, seg=10)
    fins(b, 4, 0.5, top - 0.2, 1.4, 0.9, 'titan', t=0.12)


def am_vestibule(b):
    b.box(3.2, 1.2, 1.1, 'white', (6.0, 4.5, 0))          # кассы
    b.box(3.4, 0.08, 0.6, 'red', (6.0, 3.88, 0.5))
    b.box(4.5, 1.0, 1.0, 'offwhite', (-7.0, 3.0, 0))      # гардероб
    for i in range(5):
        b.box(0.06, 1.2, 1.8, 'steel', (-8.8 + i * 0.9, 4.2, 0))
    for i in range(3):                                   # сувениры
        b.box(1.8, 0.6, 1.4, 'wood', (6.3 + (i - 1) * 2.0, -1.4, 0))
        b.box(1.8, 0.62, 0.06, 'yellow', (6.3 + (i - 1) * 2.0, -1.4, 1.0))
    for i in range(4):                                   # турникеты
        b.box(0.25, 1.0, 1.0, 'silver', (-1.8 + i * 1.2, 7.0, 0))
    b.cyl(1.3, 0.3, 'stand', (-3.2, -4.0, 0), seg=16)   # «Орион»
    b.sph(1.05, 'white', (-3.2, -4.0, 1.4), seg=14, rings=10, scale=(1.2, 1, 0.95))
    b.box(0.9, 0.1, 1.0, 'blue', (-3.2, -5.05, 1.0))
    b.cyl(1.32, 0.08, 'blue', (-3.2, -4.0, 1.4), seg=16, scale=(1.2, 1, 1))


def am_kino(b):
    b.box(9.0, 0.3, 3.0, 'navy', (0, 6.4, 0))
    b.box(8.4, 0.05, 2.2, 'glass', (0, 6.22, 0.6))
    for r in range(6):
        w = 6.0 + r * 0.5
        b.box(w, 0.7, 0.45, 'red', (0, 3.6 - r * 1.25, 0))
        b.box(w, 0.15, 0.8, 'red', (0, 3.25 - r * 1.25, 0))


def am_class(b):
    for i in range(3):
        for j in range(2):
            x, y = -2.4 + i * 2.4, -1.2 + j * 2.4
            b.box(1.6, 0.7, 0.75, 'wood', (x, y, 0))
            for s in (-0.4, 0.4):
                b.box(0.4, 0.4, 0.45, 'blue', (x + s, y - 0.6, 0))
    b.box(4.0, 0.15, 1.6, 'green', (0, 3.4, 0.6))


def am_cafe(b):
    b.box(6.0, 0.9, 1.1, 'white', (0, 3.2, 0))
    b.box(6.2, 1.0, 0.06, 'orange', (0, 3.2, 1.1))
    for i in range(3):
        for j in range(2):
            x, y = -3.6 + i * 3.6, -0.4 - j * 2.6
            b.cyl(0.55, 0.05, 'white', (x, y, 0.75), seg=12)
            b.cyl(0.06, 0.75, 'steel', (x, y, 0), seg=6)
            for k in range(3):
                a = k * 2 * pi / 3
                b.box(0.4, 0.4, 0.45, 'orange', (x + 0.8 * math.cos(a), y + 0.8 * math.sin(a), 0), (0, 0, a))


def am_stairs(b):
    for i in range(8):
        b.box(5.8, 1.0, 0.12 * (8 - i), 'stand', (0, -3.5 + i * 1.0, 0))
    b.box(0.12, 8.0, 1.0, 'steel', (-2.9, 0.0, 0.9))
    b.box(0.12, 8.0, 1.0, 'steel', (2.9, 0.0, 0.9))


def am_vitrines(b, n=4, step=2.4):
    for i in range(n):
        x = (i - (n - 1) / 2) * step
        b.box(1.7, 0.85, 0.85, 'white', (x, 0, 0))
        b.box(1.6, 0.75, 0.6, 'glass', (x, 0, 0.85))
        b.cyl(0.12, 0.25, ('red', 'gold', 'silver', 'orange')[i % 4], (x - 0.35, 0, 0.85), seg=8)
        b.box(0.35, 0.25, 0.18, ('navy', 'cream', 'steel', 'green')[i % 4], (x + 0.3, 0, 0.85))


def am_vitrines3(b):
    am_vitrines(b, 3)


def am_conf(b):
    b.box(7.0, 1.6, 0.75, 'wood', (0, 0, 0))
    for i in range(6):
        for s in (-1, 1):
            b.box(0.45, 0.45, 0.45, 'navy', (-2.9 + i * 1.15, s * 1.15, 0))
    b.box(5.0, 0.12, 2.6, 'glass', (0, 3.6, 0.4))


# (id, slug, name, fn, hall, floor, svg_x, svg_y, map_scale, rot_z_deg)
EXHIBITS = [
    (12, 'vostok', 'Спускаемый аппарат «Восток»', ex_vostok, 'utro', 'upper', 275, 900, 2.0, 0),
    (13, 'sk1', 'Скафандр «СК-1»', ex_sk1, 'utro', 'upper', 290, 820, 2.2, 0),
    (11, 'container', 'Катапультируемый контейнер с Белкой и Стрелкой', ex_container, 'utro', 'upper', 262, 1010, 2.0, 0),
    (10, 'sputnik1', 'Первый искусственный спутник Земли', ex_sputnik1, 'utro', 'upper', 380, 950, 2.2, 20),
    (16, 'venera1', 'АМС «Венера-1»', ex_venera1, 'utro', 'upper', 470, 930, 2.0, 0),
    (14, 'berkut', 'Скафандр «Беркут»', ex_berkut, 'utro', 'upper', 460, 820, 2.2, 0),
    (24, 'luna9', 'Спускаемый аппарат «Луна-9»', ex_luna9, 'utro', 'upper', 495, 1020, 2.2, 0),
    (17, 'gird09', 'Ракета «ГИРД-09»', ex_gird09, 'tvortsy', 'upper', 590, 680, 2.2, 0),
    (50, 'veranda', 'Интерьер веранды дома К.Э. Циолковского', ex_veranda, 'tvortsy', 'upper', 622, 772, 1.4, 0),
    (44, 'soyuz45', 'Корабли «Союз-4» и «Союз-5»', ex_soyuz45_fixed, 'dom', 'upper', 568, 585, 1.4, -80),
    (49, 'yastreb', 'Скафандр «Ястреб»', ex_yastreb, 'dom', 'upper', 532, 470, 2.2, 0),
    (36, 'mir', 'Базовый блок станции «Мир»', ex_mir, 'dom', 'upper', 390, 212, 1.15, 0),
    (45, 'shso', 'Шлюзовой отсек станции «Мир»', ex_shso, 'dom', 'upper', 285, 330, 1.4, -80),
    (19, 'orlan', 'Скафандр «Орлан-Д»', ex_orlan, 'dom', 'upper', 512, 300, 2.2, 0),
    (114, 'painting', 'Картина А.К. Соколова «Впервые на Луне»', ex_painting, 'luna', 'lower', 70, 487, 1.6, 0),
    (21, 'luna16', 'Автоматическая станция «Луна-16»', ex_luna16, 'luna', 'lower', 112, 497, 1.5, 0),
    (22, 'lunokhod', '«Луноход-1»', ex_lunokhod, 'luna', 'lower', 165, 500, 1.8, 20),
    (47, 'krechet', 'Скафандр «Кречет»', ex_krechet, 'luna', 'lower', 195, 462, 2.0, 0),
    (23, 'venera4', 'Спускаемый аппарат «Венера-4»', ex_venera4, 'luna', 'lower', 222, 343, 2.0, 0),
    (15, 'mars3', 'Спускаемый аппарат «Марс-3»', ex_mars3, 'luna', 'lower', 207, 298, 1.5, 0),
    (56, 'glonass', 'Спутник «Глонасс-М»', ex_glonass, 'chelovechestvu', 'lower', 652, 140, 1.0, 90),
    (26, 'soyuz_apollo', 'Корабли «Союз-Аполлон»', ex_soyuz_apollo, 'mezhdu', 'lower', 350, 118, 1.3, 0),
    (27, 'soyuz37', 'Спускаемый аппарат «Союз-37»', ex_soyuz37, 'mezhdu', 'lower', 385, 152, 1.6, 0),
    (25, 'apas', 'Стыковочный агрегат АПАС', ex_apas, 'mezhdu', 'lower', 340, 155, 1.6, 0),
    (30, 'cospas', 'Аппарат «КОСПАС-САРСАТ»', ex_cospas, 'mezhdu', 'lower', 300, 150, 1.6, 0),
    (29, 'iss', 'Международная космическая станция', ex_iss, 'mezhdu', 'lower', 462, 132, 0.85, 0),
    (31, 'baikonur', 'Стартовый комплекс Байконура с РН «Союз»', ex_baikonur, 'park', 'lower', 557, 140, 1.15, 0),
    (38, 'shuttle', 'Стартовый комплекс «Спейс шаттл»', ex_shuttle, 'park', 'lower', 568, 192, 1.15, 0),
    (900, 'saturn5', 'Ракета-носитель «Сатурн-5»', ex_saturn5, 'park', 'lower', 578, 242, 1.2, 0),
    (33, 'proton', 'Ракета-носитель «Протон»', ex_proton, 'park', 'lower', 587, 287, 1.2, 0),
    (41, 'longmarch', 'Ракета-носитель «Великий поход-2F»', ex_longmarch, 'park', 'lower', 596, 330, 1.2, 0),
    (32, 'rd107', 'Жидкостный ракетный двигатель РД-107', ex_rd107, 'park', 'lower', 603, 367, 1.8, 0),
    (37, 'explorer1', '«Эксплорер-1»', ex_explorer1, 'park', 'lower', 608, 396, 2.0, 0),
    (34, 'sealaunch', 'Комплекс «Морской старт»', ex_sealaunch, 'park', 'lower', 612, 428, 0.75, 0),
    (35, 'energia', 'Система «Энергия-Буран»', ex_energia_buran, 'park', 'lower', 618, 480, 0.85, 0),
    (20, 'soyuz', 'Космический корабль «Союз» (полноразмерный)', ex_soyuz_full, 'park', 'lower', 690, 466, 0.45, 0),
]

AMENITIES = [
    ('vestibule', 'Вестибюль', am_vestibule, 'upper', 400, 1230, 1.0, 0),
    ('kino', 'Кинозал', am_kino, 'upper', 400, 680, 1.0, 0),
    ('classroom', 'Учебный класс', am_class, 'upper', 110, 690, 1.0, 0),
    ('cafe', 'Кафе «Взлёт»', am_cafe, 'upper', 610, 45, 1.0, 0),
    ('conference', 'Конференц-зал', am_conf, 'upper', 488, 45, 1.0, 0),
    ('vitr_mem', 'Витрины', am_vitrines3, 'upper', 380, 845, 1.0, 0),
    ('vitr_dom_l', 'Витрины', am_vitrines, 'upper', 252, 470, 1.0, -80),
    ('vitr_dom_r', 'Витрины', am_vitrines, 'upper', 532, 395, 1.0, 80),
    ('vitr_luna', 'Витрины', am_vitrines3, 'lower', 205, 180, 1.0, 90),
]


# ------------------------------------------------------------- mascots: tour guides
def ms_dog(b, fur, spot, ear, vest='orange', helmet=True):
    """Standing cartoon space-dog guide, facing +X, ~0.75 m tall (scaled up on the map)."""
    # legs + paws
    for dx in (-0.13, 0.13):
        for dy in (-0.08, 0.08):
            b.cyl(0.045, 0.2, fur, (dx, dy, 0.02), seg=8)
            b.sph(0.05, spot, (dx + 0.02, dy, 0.025), seg=8, rings=5, scale=(1.3, 1, 0.6))
    # body with vest
    b.sph(0.17, fur, (0, 0, 0.33), seg=12, rings=8, scale=(1.45, 0.95, 0.95))
    b.cyl(0.175, 0.22, vest, (-0.12, 0, 0.33), RX, seg=12, scale=(1, 0.98, 1.0))
    b.box(0.06, 0.18, 0.04, 'white', (0.0, 0, 0.485))                        # vest stripe
    # tail
    b.tube((-0.22, 0, 0.38), (-0.32, 0, 0.55), 0.035, fur, 6)
    b.sph(0.045, spot, (-0.33, 0, 0.57), seg=8, rings=5)
    # head
    b.sph(0.15, fur, (0.24, 0, 0.58), seg=14, rings=9)
    b.sph(0.085, spot, (0.36, 0, 0.54), seg=10, rings=6, scale=(1.15, 0.95, 0.8))   # muzzle
    b.sph(0.03, 'black', (0.44, 0, 0.56), seg=8, rings=5)                          # nose
    for dy in (-0.06, 0.06):
        b.sph(0.024, 'black', (0.36, dy, 0.63), seg=8, rings=5)                   # eyes
        b.sph(0.008, 'white', (0.38, dy + 0.008, 0.64), seg=6, rings=4)
        b.cyl(0.055, 0.14, ear, (0.2, dy * 1.5, 0.68), (0, 0.0, 0), r2=0.0, seg=6) # ears
    b.sph(0.035, spot, (0.24, 0.13, 0.62), seg=8, rings=5)                          # cheek patch
    if helmet:
        b.ring(0.13, 0.09, 0.05, 'red', (0.2, 0, 0.45), seg=14)                 # collar
        b.sph(0.03, 'gold', (0.29, 0, 0.44), seg=8, rings=5)                     # tag
        b.tube((0.18, 0, 0.72), (0.14, 0, 0.86), 0.012, 'steel', 4)              # tiny antenna
        b.sph(0.025, 'red', (0.14, 0, 0.87), seg=8, rings=5)


def ms_belka(b):
    ms_dog(b, 'white', 'tan', 'tan', vest='orange')


def ms_strelka(b):
    ms_dog(b, 'cream', 'brown', 'brown', vest='blue')


MASCOTS = [
    ('belka', 'Белка', ms_belka, 'upper', 385, 1205, 4.2, 200),
    ('strelka', 'Стрелка', ms_strelka, 'upper', 415, 1210, 4.2, 160),
]
