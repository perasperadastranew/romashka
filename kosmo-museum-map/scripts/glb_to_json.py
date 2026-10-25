"""site/kosmo_map.glb -> site/kosmo_map.json (glTF with the binary buffer embedded as a data URI)."""
import struct, json, base64, os
SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site')
b = open(os.path.join(SITE, 'kosmo_map.glb'), 'rb').read()
length = struct.unpack('<III', b[:12])[2]; off = 12; js = binbuf = None
while off < length:
    clen, ctype = struct.unpack('<II', b[off:off + 8]); data = b[off + 8:off + 8 + clen]; off += 8 + clen
    if ctype == 0x4E4F534A: js = json.loads(data)
    elif ctype == 0x004E4942: binbuf = data
js['buffers'][0]['uri'] = 'data:application/octet-stream;base64,' + base64.b64encode(binbuf).decode()
json.dump(js, open(os.path.join(SITE, 'kosmo_map.json'), 'w'), separators=(',', ':'))
print('ok', os.path.getsize(os.path.join(SITE, 'kosmo_map.json')))
