import sys,hashlib,shutil,json
from pathlib import Path
sys.path.insert(0,r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
import vulpera_race_pack as v
import vulpera_migration as migration
report=v.p.load_json(v.STAGE/'build-report.json')
report['companion_hashes']['EsteriaAppearance.dll']=v.p.sha256(v.STAGE/'EsteriaAppearance.dll')
v.save(v.STAGE/'build-report.json',report)
v.validate()
plan=v.p.load_json(v.STAGE/'install-plan.json')
characters=v.p.load_json(v.STAGE/'migration-plan.json')
assert characters['before']==migration.snapshot()
for name,expected in plan['before_hashes'].items():
 live=v.p.CLIENT_DEFAULT/name
 assert (v.p.sha256(live) if live.exists() else None)==expected
plan['companion_hashes']=report['companion_hashes']
plan['migration_sha256']=characters['migration_sha256']
backup=Path(plan['backup'])
shutil.copy2(migration.MIGRATION,backup/migration.MIGRATION.name)
v.save(backup/'character-migration.json',characters)
v.save(v.STAGE/'install-plan.json',plan)
v.save(backup/'install-plan.json',plan)
print('FINAL PLAN VERIFIED',backup)
