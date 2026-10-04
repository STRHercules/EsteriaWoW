import sys,subprocess,json,hashlib
from pathlib import Path
sys.path.insert(0,r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
import vulpera_race_pack as v
import vulpera_migration as migration
report=v.p.load_json(v.STAGE/'last-install.json')
for name,digest in report['installed_hashes'].items():
 assert v.p.sha256(v.p.CLIENT_DEFAULT/name)==digest,name
assert v.p.sha256(v.p.CLIENT_DEFAULT/'Wow.exe')==report['preserved_exe_sha256']
hashes=subprocess.check_output(['docker','exec','ac-worldserver','sha256sum',
 *['/azerothcore/env/dist/data/dbc/'+n+'.dbc' for n in v.p.SERVER_DBC_TABLES]],text=True)
for line in hashes.splitlines():
 digest,name=line.split()
 assert report['installed_server_hashes'][Path(name).stem]==digest
image,state=subprocess.check_output(['docker','inspect','ac-worldserver','--format','{{.Image}} {{.State.Running}}'],
 text=True).split()
assert state=='true'
logs=subprocess.check_output(['docker','logs','ac-worldserver'],text=True,encoding='utf-8',errors='replace',
 stderr=subprocess.STDOUT)
assert 'AC>' in logs and 'world initialized' in logs.lower() and 'worldserver-daemon) ready' in logs
plan=v.p.load_json(v.STAGE/'migration-plan.json')
expected={int(line.split()[0]):list(map(int,line.split())) for line in plan['before'].splitlines()}
for row in plan['characters']:expected[row['guid']][4:]=row['new']
assert {int(line.split()[0]):list(map(int,line.split())) for line in migration.snapshot().splitlines()}==expected
report.update(status='installed_server_ready_live_client_acceptance_pending',running_image=image,
 mounted_dbc_hashes=hashes,source_build='12.1.0.69933',automated_contract='PASS',
 native_harnesses='PASS',exe_preserved=True,live_client_test='not_performed',
 known_limits=['Two legacy helmet families have no matching Retail variant: Helm_Plate_BloodKnight_D and '
              'Helm_Robe_AhnQiraj_A.', 'HelmetGeosetData condition32 remains undocumented; stock behavior retained.',
              'Stock barber retains combined values; independent controls are in character creator.'])
v.save(v.STAGE/'last-install.json',report)
v.save(Path(report['backup'])/'install-report.json',report)
v.save(v.ROOT/'integration/acceptance.json',{'status':report['status'],'source_complete':True,
 'stage_validated':True,'installed':True,'server_ready':True,'live_accepted':False,'retail_parity':False,
 'known_limits':report['known_limits'],'receipt':str(v.STAGE/'last-install.json')})
print('INSTALL VERIFIED',image,'matching seven mounted DBCs; unchanged non-Vulpera appearances and executable')
