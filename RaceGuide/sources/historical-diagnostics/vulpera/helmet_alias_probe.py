import sys,struct,hashlib,json
sys.path.insert(0,r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
import vulpera_race_pack as v
from wotlkconv.m2 import parse_m2
equipment=v.p.load_json(v.ROOT/'integration/equipment.json')
def signature(data):
 m=parse_m2(data)
 points=sorted(tuple(round(x,5) for x in struct.unpack_from('<3f',m.vertices,i*48)) for i in range(m.vertex_count))
 return hashlib.sha256(repr(points).encode()).hexdigest()
known={}
for row in equipment['converted']:
 known.setdefault(signature(v.path(v.ART,row['target']).read_bytes()),[]).append(row['target'])
storm=v.p.Storm(v.p.DLL_DEFAULT)
for row in equipment['missing']:
 key=f"Item\\ObjectComponents\\Head\\{row['stem']}_Vu{row['gender']}.m2"
 try:
  data=v.p._read_archive_entry(storm,v.STAGE/'legacy/Patch-Y.MPQ',key)
  print(key,'MATCH',known.get(signature(data),[]))
 except Exception as ex:print(key,ex)
