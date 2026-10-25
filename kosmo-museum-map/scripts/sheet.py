import os
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
meta=json.load(open(os.path.join(ROOT,'blender','meta.json')))
tiles=os.path.join(ROOT,'renders','tiles'); T=300
items=[(f"EX_{e['id']}_{e['slug']}", e['title']) for e in meta['exhibits']]
cols=6; rows=(len(items)+cols-1)//cols
W=Image.new('RGB',(cols*T, rows*(T+34)),'#F3F1EC'); d=ImageDraw.Draw(W)
try: f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
except: f=ImageFont.load_default()
for i,(n,t) in enumerate(items):
    p=os.path.join(tiles,n+'.png')
    if not os.path.exists(p): continue
    im=Image.open(p).convert('RGB').resize((T,T))
    x,y=(i%cols)*T,(i//cols)*(T+34); W.paste(im,(x,y))
    t=t if len(t)<38 else t[:36]+'…'
    d.text((x+8,y+T+8),t,fill='#333',font=f)
W.save(sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,'renders','exhibits_sheet.jpg'),quality=88)
print(W.size)
