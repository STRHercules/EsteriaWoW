"""Finish the validated archive stage after correcting the server-only prefix test."""

import rename as n

backup = n.Path('G:/EsteriaBackups/forgotten-name-20261003-082903')
n.closed_client()
report = {'backup': str(backup), 'source_hashes': {}, 'stage_hashes': {},
          'exe_hash': n.p.sha256(n.p.CLIENT_DEFAULT / 'Wow.exe'), 'status': 'staged'}
for relative in n.RELATIVES:
    report['source_hashes'][str(relative)] = n.p.sha256(backup / relative)
    assert n.p.sha256(n.p.CLIENT_DEFAULT / relative) == report['source_hashes'][str(relative)]
    report['stage_hashes'][str(relative)] = n.p.sha256(backup / 'staged' / relative)
report['server_hash'] = n.p.sha256(backup / 'ChrRaces.before.dbc')
assert n.p.sha256(n.SERVER) == report['server_hash']
(backup / 'ChrRaces.dbc').write_bytes(n.rename_dbc((backup / 'ChrRaces.before.dbc').read_bytes()))
n.check.check(backup / 'staged', backup / 'ChrRaces.dbc')
n.REPORT.write_text(n.json.dumps(report, indent=2) + '\n', encoding='utf-8')
(backup / 'install.json').write_bytes(n.REPORT.read_bytes())
print('READY', backup)
