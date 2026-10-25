import json
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')
sys.path.insert(0, HERE)
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
d=json.load(open(os.path.join(DATA,'plan.json')))
def F(f): return unary_union([Polygon(p['outer'],p['holes']) for p in d[f+'_floor']])
def tl(g):
    gs=[g] if g.geom_type=='Polygon' else list(getattr(g,'geoms',[]))
    return [{"outer":list(p.exterior.coords)[:-1],"holes":[list(h.coords)[:-1] for h in p.interiors]} for p in gs if p.geom_type=='Polygon' and p.area>20]
zones=[]
for f in ('upper','lower'):
    fl=F(f).buffer(-1.5)
    for h in d['halls'][f]:
        g=Polygon(h['poly'][0]['outer']).buffer(-2.5).intersection(fl)
        zones.append({"id":h['id'],"name":h['name'],"floor":f,"polys":tl(g),"c":list(g.representative_point().coords[0])})
up=F('upper').buffer(-1.5)
zones.append({"id":"vest","name":"Вестибюль","floor":"upper","polys":tl(up.intersection(box(0,1162,800,1304)).buffer(-2)),"c":[400,1240]})
zones.append({"id":"kino","name":"Кинозал","floor":"upper","polys":tl(Polygon([(338.5,592.9),(461,592.9),(488.5,743.6),(311.8,743.6)]).buffer(-3)),"c":[400,640]})
d['zones']=zones
json.dump(d,open(os.path.join(DATA,'plan.json'),'w'),ensure_ascii=False)
for z in zones: print(z['id'],len(z['polys']),[round(Polygon(p['outer']).area) for p in z['polys']])
