import sys,shutil,json
from pathlib import Path
from datetime import datetime
sys.path.insert(0,r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
import vulpera_race_pack as v
stamp=datetime.now().strftime('%Y%m%d-%H%M%S')
root=Path(r'C:\Users\Zach\.codex\backups')/('vulpera-render-'+stamp)
root.mkdir(parents=True,exist_ok=False)
report={'backup':str(root),'client_before':{},'source_before':{},'server_before':{}}
for rel in (v.p.GLOBAL_ARCHIVE_REL,v.p.LOCALE_ARCHIVE_REL,Path('EsteriaAppearance.dll'),
 Path('EsteriaVulpera.bin'),Path('EsteriaVulperaTextures.bin'),Path('EsteriaAppearanceGeometry.bin')):
 target=root/'client'/rel
 target.parent.mkdir(parents=True,exist_ok=True)
 source=v.p.CLIENT_DEFAULT/rel
 digest=v.p.sha256(source)
 shutil.copy2(source,target)
 assert v.p.sha256(target)==digest
 report['client_before'][str(rel)]=digest
for rel in ('tools/vulpera_race_pack.py','src/server/shared/VulperaAppearance.h'):
 target=root/'source'/rel;target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(v.p.ROOT/rel,target)
 report['source_before'][rel]=v.p.sha256(target)
target=root/'codec-v1.json'
shutil.copy2(v.ROOT/'integration/codec.json',target)
for name in v.p.SERVER_DBC_TABLES:
 target=root/'server-dbc'/(name+'.dbc');target.parent.mkdir(exist_ok=True)
 shutil.copy2(v.p.SERVER_DBC_ROOT/target.name,target)
 report['server_before'][name]=v.p.sha256(target)
v.save(v.STAGE/'repair-checkpoint.json',report)
v.save(root/'checkpoint.json',report)
print(root)
