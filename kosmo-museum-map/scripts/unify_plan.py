"""One-space plan: floors in true relative position, stair openings, cut where lower floor lies under upper."""
import json
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
sys.path.insert(0, HERE)
from svg_paths import *
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
d=json.load(open(os.path.join(DATA,'plan.json')))
exec(open(os.path.join(HERE,'parse_plan.py')).read().split('data={}')[0])   # polys/evenodd/tolist helpers
from shapely.validation import make_valid
F=lambda f: unary_union([Polygon(p['outer'],p['holes']) for p in d[f+'_floor']])
up0, lo0 = F('upper'), F('lower')
ST_L = box(159,355,233,445); ST_R = box(640,488,708,531)
stairs = unary_union([ST_L, ST_R])
lo = lo0.difference(stairs).buffer(0)
up = up0.difference(lo0.buffer(1.0)).difference(stairs).buffer(0)
up = up.buffer(-0.01).buffer(0.01)
def walls(dd, floor, other, hall_polys):
    parts=[]
    for pg in polys(dd):
        thin = pg.area/pg.length
        parts.append(pg.buffer(0.3) if thin<2.2 else pg.boundary.buffer(1.5))
    w = unary_union(parts).intersection(floor.buffer(1.8))
    w = w.union(floor.boundary.buffer(1.6)).intersection(floor.buffer(2.0))
    w = w.difference(stairs.buffer(1.0))
    if other is not None: w = w.difference(other.buffer(0.2))
    return w.buffer(0)
w_lo = walls(LOWER_WALLS, lo, None, None)
w_up = walls(UPPER_WALLS, up, lo, None)
out={'upper_floor':tolist(up),'lower_floor':tolist(lo),'upper_walls':tolist(w_up),'lower_walls':tolist(w_lo),
     'stairs':[{'id':'L','rect':[159,355,233,445],'up_side':'+y'},{'id':'R','rect':[640,488,708,531],'up_side':'+x'}],
     'halls':d['halls']}
def tl(g):
    gs=[g] if g.geom_type=='Polygon' else list(getattr(g,'geoms',[]))
    return [{"outer":list(p.exterior.coords)[:-1],"holes":[list(h.coords)[:-1] for h in p.interiors]} for p in gs if p.geom_type=='Polygon' and p.area>20]
zones=[]
FL={'upper':up,'lower':lo}
for f in ('upper','lower'):
    fl=FL[f].buffer(-1.5)
    for h in d['halls'][f]:
        g=Polygon(h['poly'][0]['outer']).buffer(-2.5).intersection(fl)
        zones.append({"id":h['id'],"name":h['name'],"floor":f,"polys":tl(g),"c":list(g.representative_point().coords[0])})
zones.append({"id":"vest","name":"Вестибюль","floor":"upper","polys":tl(up.buffer(-1.5).intersection(box(0,1162,800,1304)).buffer(-2)),"c":[400,1240]})
zones.append({"id":"kino","name":"Кинозал","floor":"upper","polys":tl(Polygon([(338.5,592.9),(461,592.9),(488.5,743.6),(311.8,743.6)]).buffer(-3)),"c":[400,640]})
out['zones']=zones
json.dump(out,open(os.path.join(DATA,'plan_one.json'),'w'),ensure_ascii=False)
print('upper',round(up.area),'lower',round(lo.area),'overlap',round(up.intersection(lo).area))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as P
fig,ax=plt.subplots(figsize=(7,10))
for p in out['upper_floor']: ax.add_patch(P(p['outer'],fc='#f3d9c8'))
for p in out['lower_floor']: ax.add_patch(P(p['outer'],fc='#cfd8f0'))
for k in ('upper_walls','lower_walls'):
    for p in out[k]: ax.add_patch(P(p['outer'],fc='k'))
for s in out['stairs']: x0,y0,x1,y1=s['rect']; ax.add_patch(P([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],fc='#8c8',alpha=.8))
ax.set_xlim(0,800); ax.set_ylim(1304,0); ax.set_aspect(1); plt.savefig(os.path.join(DATA,'plan_one.png'),dpi=70)
