import json
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
sys.path.insert(0, HERE)
from svg_paths import *
from svgpathtools import parse_path
from shapely.geometry import Polygon, MultiPolygon, mapping
from shapely.ops import unary_union
from shapely.validation import make_valid
def polys(d):
    p=parse_path(d); out=[]
    for sp in p.continuous_subpaths():
        pts=[(s.start.real,s.start.imag) for s in sp]+[(sp[-1].end.real,sp[-1].end.imag)]
        if len(pts)>=3:
            pg=make_valid(Polygon(pts))
            if pg.geom_type=='GeometryCollection': pg=unary_union([x for x in pg.geoms if x.geom_type in ('Polygon','MultiPolygon')])
            if pg.area>1: out.append(pg)
    return out
def evenodd(d):
    g=None
    for pg in polys(d):
        g=pg if g is None else g.symmetric_difference(pg)
    return g.buffer(0)
def tolist(g):
    gs=[g] if g.geom_type=='Polygon' else list(getattr(g,'geoms',[]))
    res=[]
    for p in gs:
        if p.geom_type!='Polygon' or p.area<2: continue
        p=p.simplify(0.4)
        res.append({"outer":list(p.exterior.coords)[:-1],"holes":[list(h.coords)[:-1] for h in p.interiors]})
    return res
data={}
for k,d in [("upper_floor",UPPER_FLOOR),("lower_floor",LOWER_FLOOR),("upper_walls",UPPER_WALLS),("lower_walls",LOWER_WALLS)]:
    g=evenodd(d); data[k]=tolist(g); print(k, round(g.area), len(data[k]), g.bounds)
data["halls"]={f:[{"id":i,"name":n,"poly":tolist(make_valid(Polygon([(s.start.real,s.start.imag) for s in parse_path(d)]+[(parse_path(d)[-1].end.real,parse_path(d)[-1].end.imag)])).buffer(0))} for i,n,d in L] for f,L in HALLS.items()}
for f in data["halls"]:
    for h in data["halls"][f]: print(f,h["id"],round(Polygon(h["poly"][0]["outer"]).area))
json.dump(data,open(os.path.join(DATA,"plan.json"),"w"))

# wall network: thin strips kept, big closed outlines -> buffered outline
from shapely.geometry import LineString
def walls(d):
    parts=[]
    for pg in polys(d):
        thin = pg.area/pg.length
        if thin<2.2: parts.append(pg.buffer(0.3))
        else: parts.append(pg.boundary.buffer(1.5))
    return unary_union(parts)
for f,d in [("upper",UPPER_WALLS),("lower",LOWER_WALLS)]:
    floor=unary_union([Polygon(p['outer'],p['holes']) for p in data[f+'_floor']]+([Polygon(h['poly'][0]['outer']) for h in data['halls'][f]] if f=='lower' else []))
    data[f+'_floor']=tolist(floor.buffer(0))
    w=walls(d).union(floor.boundary.buffer(1.6)).intersection(floor.buffer(2.0))
    data[f+'_walls']=tolist(w)
    print(f,'walls',round(w.area),len(data[f+'_walls']))
json.dump(data,open(os.path.join(DATA,"plan.json"),"w"))
