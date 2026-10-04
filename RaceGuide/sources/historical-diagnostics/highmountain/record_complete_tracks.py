import sys
sys.path.insert(0, r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
import highmountain_complete_tracks as repair

report = repair.h.p.load_json(repair.STAGE / 'last-install.json')
storm = repair.h.p.Storm(repair.h.p.DLL_DEFAULT)
for relative, expected in report['installed_hashes'].items():
    live = repair.h.p.CLIENT_DEFAULT / relative
    assert repair.h.p.sha256(live) == expected
    for row in report['models'].values():
        key = row['model_path']
        stage = repair.STAGE.joinpath(*repair.h.p.PureWindowsPath(key).parts)
        assert repair.h.p._read_archive_entry(storm, live, key) == stage.read_bytes()
assert repair.h.p.sha256(repair.h.p.CLIENT_DEFAULT / 'Wow.exe') == (
    '9e0949a90b19486325beafc255a10bda715beabb1df16d8d9eab1fa868a4375f')
path = repair.h.ROOT / 'integration/acceptance.json'
data = repair.h.p.load_json(path)
data['animation_runtime_issue']['live_acceptance'] = (
    'First repair disproven: no visible change, talk invisible, dance crash, sword/shield remain sheathed')
data['complete_animation_tracks'] = {
    'crash_report': r'G:\3.3.5a - Dev\Errors\2026-10-01 07.49.09 Crash.txt',
    'crash_site': '008310AC event timestamp traversal; invalid timestamp pointer D29C93CC',
    'findings': [
        'PEDC parent event tables omitted during conversion, including left/right sheath triggers',
        'in-model event/material/camera keys corrupted by external-track marking and model rewrites',
        'two-step animation alias retained unrelocated offsets into the wrong file region'],
    'repair': [
        'restore raw PEDC events, opaque default, source UV transforms and downgraded source cameras',
        'embed skeletal and attachment keys; resolve final alias target spans',
        'retain all 349 male/341 female sequences and accepted geometry, textures and SKINs'],
    'checks': 'inline spans, sorted finite keys, source events within durations, sheath89/90, alias equality, '
              'talk/dance/sheath hand-key equality, three-archive readback and installed SHA256',
    'unrelated_entries_verified_identical': 43728,
    'installation': report,
    'live_acceptance': 'Pending fresh launch: both genders, talking, dance without crash/fade, sword/shield in hands'
}
repair.h.save(path, data)
print('Installed hashes and model readback verified; executable fingerprint unchanged; acceptance recorded.')
