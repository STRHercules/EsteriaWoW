import sys,struct,json
sys.path.insert(0,r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
import vulpera_race_pack as v
from wotlkconv.m2 import parse_m2,parse_skin
s=v.p.Storm(v.p.DLL_DEFAULT)
for sex in ('male','female'):
 key=f'character\\vulpera\\{sex}\\vulpera{sex}.m2'
 m=parse_m2(v.p._read_archive_entry(s,v.STAGE/'legacy/Patch-Y.MPQ',key))
 skin=parse_skin(v.p._read_archive_entry(s,v.STAGE/'legacy/patch-U.MPQ',key[:-3]+'00.skin'))
 print(sex, 'oldgeos',[(v.e.v.u16(mesh,0),v.e.v.u16(mesh,6)) for mesh in skin.submeshes])
 source=v.path(v.ART,f'{v.PREFIX}\\{sex}\\vulpera{sex}.m2')
 if not source.exists():continue
 new=parse_m2(source.read_bytes());ns=parse_skin(source.with_name(source.stem+'00.skin').read_bytes())
 def points(model,sk,mesh):
  return {tuple(round(x,4) for x in struct.unpack_from('<3f',model.vertices,sk.vertices[i]*48)) for i in range(v.e.v.u16(mesh,4),v.e.v.u16(mesh,4)+v.e.v.u16(mesh,6))}
 oldsets={v.e.v.u16(mesh,0):points(m,skin,mesh) for mesh in skin.submeshes}
 newsets={v.e.v.u16(mesh,0):points(new,ns,mesh) for mesh in ns.submeshes}
 for geo,p in oldsets.items():
  if geo//100 in (1,2,3):
   matches=sorted(((len(p&q)/max(1,len(p|q)),g) for g,q in newsets.items()),reverse=True)[:3]
   print('MATCH',sex,geo,len(p),matches)
