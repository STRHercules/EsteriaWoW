"""Adapt missing NPC player actions from CRC-matched bones in the installed player rigs."""

import copy
import math
from pathlib import Path
import argparse
import hashlib
import os
import shutil
import struct
import subprocess
from datetime import datetime

from wotlkconv.m2 import parse_m2
from wotlkconv.m2.types import TrackBase

import creature_race_pack as c
import earthen_race_pack as e

ROOT = c.STAGE / 'repair/donors'


def sequence(model, animation):
    index = next((i for i, s in enumerate(model.sequences)
                  if s['id'] == animation and s['variation_index'] == 0), None)
    if index is None:
        raise ValueError(f'Donor has no animation {animation}')
    seen = set()
    while model.sequences[index]['flags'] & 0x40:
        if index in seen:
            raise ValueError('Animation alias cycle')
        seen.add(index)
        index = model.sequences[index]['alias_next']
    return index


def donor(slug, gender):
    family = 'BloodElf' if slug == 'naga' else 'Dwarf' if slug == 'tuskarr' else 'Human'
    sex = 'Female' if gender else 'Male'
    # Esteria uses the accepted HD *2 player models; legacy paths can have shadowed ANIM companions.
    key = f'Character\\{family}2\\{sex}\\{family}{sex}2.m2'
    target = ROOT / (family + sex + '2.m2')
    target.parent.mkdir(parents=True, exist_ok=True)
    data, provider = c.p._effective_file(c.p.CLIENT_DEFAULT / 'Data', key)
    c.immutable(target, data)
    model = parse_m2(data)
    files = c.p.ClientFiles(str(c.p.CLIENT_DEFAULT / 'Data'), 'enUS')
    try:
        for q in model.sequences:
            if q['flags'] & (0x20 | 0x40):
                continue
            name = f'{target.stem}{q["id"]:04d}-{q["variation_index"]:02d}.anim'
            if target.with_name(name).exists():
                continue
            source_key = str(c.PureWindowsPath(key).parent / name)
            payload, _ = files.find(source_key)
            c.immutable(target.with_name(name), payload)
    finally:
        files.close()
    model = e.v.read_player_model(target)
    e.tracks.embed(model, target.parent, target.stem)
    return model, {'path': key, 'provider': provider, 'sha256': c.p.sha256(target)}


def quat(values):
    decoded = [(v + 32768 if v < 0 else v - 32767) / 32767 for v in values]
    length = math.sqrt(sum(v * v for v in decoded))
    if length < .001:
        raise ValueError('Invalid compressed quaternion')
    return tuple(v / length for v in decoded)


def packed(values):
    length = math.sqrt(sum(v * v for v in values))
    values = [v / length for v in values]
    return tuple(max(-32768, min(32767, round(v * 32767) + (-32768 if v > 0 else 32767))) for v in values)


def multiply(a, b):
    x, y, z, w = a
    X, Y, Z, W = b
    return (w * X + x * W + y * Z - z * Y, w * Y - x * Z + y * W + z * X,
            w * Z + x * Y - y * X + z * W, w * W - x * X - y * Y - z * Z)


def keys(track, index):
    if not track.timestamps:
        return [], []
    slot = 0 if track.global_sequence >= 0 else index
    if slot >= len(track.timestamps):
        return [], []
    return track.timestamps[slot], track.values[slot]


def per_sequence(track, model):
    if track.global_sequence >= 0:
        # Shared animated effects keep their own clock. Constant bind transforms can be expanded exactly.
        if not hasattr(track, 'values') or not track.values or not track.values[0]:
            return False
        values = track.values[0]
        if any(v != values[0] for v in values):
            return False
        track.global_sequence = -1
        track.timestamps = [[0] for _ in model.sequences]
        track.values = [[copy.deepcopy(values[0])] for _ in model.sequences]
    count = len(model.sequences)
    while len(track.timestamps) < count:
        track.timestamps.append([])
    track.timestamp_spans = [(0, 0)] * count
    if hasattr(track, 'values'):
        while len(track.values) < count:
            track.values.append([])
        track.value_spans = [(0, 0)] * count
    track.external.clear()
    return True


def retarget(model, provider, animation):
    source_index = sequence(provider, animation)
    base_source = sequence(provider, 0)
    base_target = sequence(model, 0)
    old_count = len(model.sequences)
    duration = provider.sequences[source_index]['duration']
    added = copy.deepcopy(provider.sequences[source_index])
    added.update(id=animation, variation_index=0, variation_next=-1, alias_next=old_count,
                 flags=(added['flags'] & ~0x40) | 0x20)
    model.sequences.append(added)
    for track in model.tracks():
        if track.global_sequence >= 0:
            continue
        values = copy.deepcopy(track.values[base_target]) if hasattr(track, 'values') \
            and base_target < len(track.values) else []
        times = copy.deepcopy(track.timestamps[base_target]) if base_target < len(track.timestamps) else []
        if times:
            source_duration = model.sequences[base_target]['duration']
            times = [round(t * duration / max(1, source_duration)) for t in times]
        per_sequence(track, model)
        track.timestamps[old_count] = times
        if hasattr(track, 'values'):
            track.values[old_count] = values
    by_crc = {b['bone_name_crc']: b for b in provider.bones if b['bone_name_crc']}
    semantic = {}
    for finger in (8, 13):
        if finger >= len(model.key_bone_lookup) or finger >= len(provider.key_bone_lookup):
            continue
        a, b = model.key_bone_lookup[finger], provider.key_bone_lookup[finger]
        if a >= len(model.bones) or b >= len(provider.bones):
            continue
        # The index/thumb key's parent is the palm. This also handles Naga female's unnamed arm joints.
        a, b = model.bones[a]['parent_bone'], provider.bones[b]['parent_bone']
        for _ in range(5):
            if a < 0 or b < 0:
                break
            semantic[a] = provider.bones[b]
            a, b = model.bones[a]['parent_bone'], provider.bones[b]['parent_bone']
    changed = []
    for i, bone in enumerate(model.bones):
        source_bone = by_crc.get(bone['bone_name_crc'], semantic.get(i))
        if source_bone is None:
            continue
        altered = False
        for name in ('rotation', 'translation'):
            track = bone[name]
            source_track = source_bone[name]
            times, motion = keys(source_track, source_index)
            _, initial = keys(source_track, base_source)
            _, target_bind = keys(track, base_target)
            if not times or not motion or not initial or not per_sequence(track, model):
                continue
            if source_track.global_sequence >= 0:
                if all(value == motion[0] for value in motion):
                    times, motion = [0], motion[:1]
                else:
                    period = provider.global_loops[source_track.global_sequence]
                    times = [min(duration, round(t * duration / max(1, period))) for t in times]
            if name == 'rotation':
                reference = quat(initial[0])
                inverse = (-reference[0], -reference[1], -reference[2], reference[3])
                base = quat(target_bind[0]) if target_bind else (0, 0, 0, 1)
                result = [packed(multiply(multiply(quat(value), inverse), base)) for value in motion]
            else:
                base = target_bind[0] if target_bind else (0, 0, 0)
                target_parent = model.bones[bone['parent_bone']] if bone['parent_bone'] >= 0 else bone
                source_parent = provider.bones[source_bone['parent_bone']] \
                    if source_bone['parent_bone'] >= 0 else source_bone
                a = math.dist(bone['pivot'], target_parent['pivot'])
                b = math.dist(source_bone['pivot'], source_parent['pivot'])
                scale = a / b if a > .001 and b > .001 else 1
                result = [tuple(base[j] + (value[j] - initial[0][j]) * scale for j in range(3)) for value in motion]
            track.interpolation = source_track.interpolation
            track.timestamps[old_count] = copy.deepcopy(times)
            track.values[old_count] = result
            altered = altered or len(set(result)) > 1
        if altered:
            changed.append(i)
    if not changed:
        raise ValueError(f'Retargeted action {animation} has no moving CRC-matched bones')
    if animation in (89, 90):
        for identifier in (b'$SHL', b'$SHR'):
            authored = next(event for event in provider.events if event['identifier'] == identifier)
            event = next((event for event in model.events if event['identifier'] == identifier), None)
            if event is None:
                event = copy.deepcopy(authored)
                crc = provider.bones[event['bone']]['bone_name_crc']
                event['bone'] = next((j for j, b in enumerate(model.bones) if b['bone_name_crc'] == crc),
                    next(a['bone'] for a in model.attachments if a['id'] == (2 if identifier == b'$SHL' else 1)))
                event['enabled'] = TrackBase(interpolation=0, global_sequence=-1,
                                              timestamps=[[] for _ in model.sequences])
                model.events.append(event)
            per_sequence(event['enabled'], model)
            times = authored['enabled'].timestamps[source_index]
            if not times:
                raise ValueError(f'Player donor has no {identifier} event for {animation}')
            event['enabled'].timestamps[old_count] = copy.deepcopy(times)
    return {'animation': animation, 'duration': duration, 'moving_matched_bones': changed}


def repair_model(slug, gender, model):
    wanted = (89, 90) if slug in ('tuskarr', 'vrykul') else \
        (37, 38, 39, 63, 89, 90, 91, 123, 128, 129) if slug == 'naga' else ()
    existing = {q['id'] for q in model.sequences}
    missing = [i for i in wanted if i not in existing]
    report = {'added_actions': [], 'wrath_action_aliases': []}
    if missing:
        source, report['donor'] = donor(slug, gender)
        for animation in missing:
            report['added_actions'].append(retarget(model, source, animation))
    # Wrath spell kits can request the old generic IDs, while these Retail NPCs author 51-54.
    for animation, authored in ((2, 53), (31, 51), (32, 53), (33, 54), (72, 97)):
        if animation in {q['id'] for q in model.sequences} or authored not in {q['id'] for q in model.sequences}:
            continue
        index = sequence(model, authored)
        slot = len(model.sequences)
        added = copy.deepcopy(model.sequences[index])
        added.update(id=animation, variation_index=0, variation_next=-1, alias_next=slot,
                     flags=(added['flags'] & ~0x40) | 0x20)
        model.sequences.append(added)
        for track in model.tracks():
            if track.global_sequence >= 0:
                continue
            times = copy.deepcopy(track.timestamps[index]) if index < len(track.timestamps) else []
            values = copy.deepcopy(track.values[index]) if hasattr(track, 'values') \
                and index < len(track.values) else []
            per_sequence(track, model)
            track.timestamps[slot] = times
            if hasattr(track, 'values'):
                track.values[slot] = values
        report['wrath_action_aliases'].append({'animation': animation, 'authored_source': authored})
    e.rebuild_sequence_lookup(model)
    if slug == 'naga' and gender == 0:
        report['weapon_anchors'] = weapon_anchors(model)
    return report


def weapon_anchors(model):
    """Add the female model's authored sheath anchors; keep the male hand sockets and rig unchanged."""
    info = c.p.load_json(c.WORK / 'naga/integration/rendering.json')['models']['1']
    source_data = c.p._effective_file(c.p.CLIENT_DEFAULT / 'Data', info['path'])[0]
    source = parse_m2(source_data)
    existing = {a['id'] for a in model.attachments}
    by_crc = {b['bone_name_crc']: i for i, b in enumerate(model.bones)}
    added = []
    for attachment in source.attachments:
        if attachment['id'] not in (26, 27, 31, 32, 33) or attachment['id'] in existing:
            continue
        donor_bone = source.bones[attachment['bone']]
        source_parent = source.bones[donor_bone['parent_bone']]
        parent = by_crc[source_parent['bone_name_crc']]
        offset = tuple(model.bones[parent]['pivot'][i] - source_parent['pivot'][i] for i in range(3))
        bone = copy.deepcopy(donor_bone)
        bone['parent_bone'] = parent
        bone['pivot'] = tuple(bone['pivot'][i] + offset[i] for i in range(3))
        for name in ('translation', 'rotation', 'scale'):
            track = bone[name]
            _, values = keys(track, sequence(source, 0))
            if values and any(value != values[0] for value in values):
                raise ValueError('Sheath anchor is animated; explicit sequence remapping is required')
            track.global_sequence = -1
            track.external.clear()
            track.timestamps = [[0] for _ in model.sequences] if values else [[] for _ in model.sequences]
            track.values = [[copy.deepcopy(values[0])] for _ in model.sequences] if values else \
                [[] for _ in model.sequences]
            track.timestamp_spans = track.value_spans = [(0, 0)] * len(model.sequences)
        new = copy.deepcopy(attachment)
        new['bone'] = len(model.bones)
        new['position'] = tuple(new['position'][i] + offset[i] for i in range(3))
        model.bones.append(bone)
        model.attachments.append(new)
        while len(model.attachment_lookup) <= new['id']:
            model.attachment_lookup.append(65535)
        model.attachment_lookup[new['id']] = len(model.attachments) - 1
        added.append(new['id'])
    if len(model.bones) > 256:
        raise ValueError('Additional weapon anchors exceed the native bone index limit')
    return {'attachments': added, 'donor_path': info['path'],
            'donor_sha256': hashlib.sha256(source_data).hexdigest()}


STAGE = c.STAGE / 'repair'


def preview_repair():
    import creature_portrait_pack as portraits
    files = c.p.ClientFiles(str(c.p.CLIENT_DEFAULT / 'Data'), 'enUS')
    try:
        selected = files.find(c.p.GLUE_ROOT + 'CharacterSelect.lua')[0].decode()
        if '-- Esteria Vrykul preview sizing.' not in selected:
            return {}
        selected = portraits.patch_model_update(selected, True)
        texts = [files.find(c.p.GLUE_ROOT + name)[0].decode()
                 for name in ('CharacterCreate.lua', 'ECS_Schema.lua', 'ECS_Integrate.lua')]
    finally:
        files.close()
    portraits.check_lua(*texts, selected)
    return {c.p.GLUE_ROOT + 'CharacterSelect.lua': selected.encode()}


def stage():
    c.save(STAGE / 'build-report.json', {'status': 'staging_in_progress'})
    from test_creature_animations import check
    check()
    updates = preview_repair()
    models = {}
    for slug in c.SPECS:
        render = c.p.load_json(c.WORK / slug / 'integration/rendering.json')
        models[slug] = render['models']
        for info in render['models'].values():
            key = info['path']
            path = c.WORK.joinpath(slug, 'integration/patch-root', *c.PureWindowsPath(key).parts)
            updates[key] = path.read_bytes()
            updates[key[:-3] + '00.skin'] = path.with_name(path.stem + '00.skin').read_bytes()
    display, _ = c.p._full_table(c.p.CLIENT_DEFAULT / 'Data', 'CreatureDisplayInfo')
    table = c.p.RawWdbc(display)
    rows = [row[:16] + struct.pack('<f', c.SPECS['vrykul']['display_scale']) + row[20:]
            if c.p._value(row, 0) == c.DISPLAY_IDS['vrykul'][0] else row for row in table.records]
    display = table.build(rows)
    assert sum(old != new for old, new in zip(table.records, rows, strict=True)) <= 1
    updates[c.p.DBC_ROOT + 'CreatureDisplayInfo.dbc'] = display
    (STAGE / 'server-dbc').mkdir(parents=True, exist_ok=True)
    (STAGE / 'server-dbc/CreatureDisplayInfo.dbc').write_bytes(display)
    baseline = (c.p.CLIENT_DEFAULT / 'EsteriaAppearanceGeometry.bin').read_bytes()
    magic, version, count = struct.unpack_from('<3I', baseline)
    assert (magic, version) == (0x4D474145, 1)
    offset, records, changed = 12, [], []
    for _ in range(count):
        key = baseline[offset:offset + 128].split(b'\0')[0].decode()
        size = struct.unpack_from('<I', baseline, offset + 128)[0]
        end = offset + 132 + size
        if key in updates:
            skin = updates[key[:-3] + '00.skin']
            records.append(key.encode().ljust(128, b'\0') + struct.pack('<I', len(skin)) + skin)
            changed.append(key)
        else:
            records.append(baseline[offset:end])
        offset = end
    assert offset == len(baseline) and len(changed) == 5
    (STAGE / 'EsteriaAppearanceGeometry.bin').write_bytes(baseline[:12] + b''.join(records))
    names = ['EsteriaAppearanceGeometry.bin']
    if c.p.sha256(c.STAGE / 'EsteriaAppearance.dll') != c.p.sha256(c.p.CLIENT_DEFAULT / 'EsteriaAppearance.dll'):
        shutil.copy2(c.STAGE / 'EsteriaAppearance.dll', STAGE / 'EsteriaAppearance.dll')
        names.append('EsteriaAppearance.dll')
    for slug in c.SPECS:
        family = 'ThinHuman' if slug == 'thinhuman' else slug.title()
        for suffix in ('', 'Textures'):
            name = f'Esteria{family}{suffix}.bin'
            if c.p.sha256(c.STAGE / name) != c.p.sha256(c.p.CLIENT_DEFAULT / name):
                shutil.copy2(c.STAGE / name, STAGE / name)
                names.append(name)
    report = {'status': 'repair_staged', 'models': models, 'source_hashes': {}, 'stage_hashes': {},
              'glue_hashes': {n: hashlib.sha256(data).hexdigest()
                              for n, data in updates.items() if n.endswith('.lua')},
              'companion_hashes': {n: c.p.sha256(STAGE / n) for n in names},
              'preserved_exe_sha256': c.p.sha256(c.p.CLIENT_DEFAULT / 'Wow.exe'),
              'preserved_helper_sha256': c.p.sha256(c.p.CLIENT_DEFAULT / 'EsteriaAppearance.dll'),
              'server_before_sha256': c.p.sha256(c.p.SERVER_DBC_ROOT / 'CreatureDisplayInfo.dbc'),
              'server_after_sha256': c.p.sha256(STAGE / 'server-dbc/CreatureDisplayInfo.dbc')}
    storm = c.p.Storm(c.p.DLL_DEFAULT)
    for relative in (c.p.GLOBAL_ARCHIVE_REL, c.p.LOCALE_ARCHIVE_REL):
        live = c.p.CLIENT_DEFAULT / relative
        target = STAGE / 'pack' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        report['source_hashes'][str(relative)] = c.p.sha256(live)
        shutil.copy2(live, target)
        assert c.p.sha256(target) == report['source_hashes'][str(relative)]
        storm.replace_archive_entries(target, updates)
        if target.stat().st_size >= 0x80000000:
            compressed = target.with_suffix('.compressed')
            c.p.rebuild_archive_streaming(storm, target, compressed, compress=True)
            os.replace(compressed, target)
        assert target.stat().st_size < 0x80000000
        archive = storm.open_archive(target)
        try:
            for key, data in updates.items():
                assert storm.read(archive, key) == data, key
        finally:
            storm.dll.SFileCloseArchive(archive)
        report['stage_hashes'][str(relative)] = c.p.sha256(target)
        print('REPAIR STAGED', relative, flush=True)
    c.save(STAGE / 'build-report.json', report)
    manifest = c.p.load_manifest('vrykul')
    manifest['models']['male']['display_scale'] = c.SPECS['vrykul']['display_scale']
    c.save(c.p.manifest_path('vrykul'), manifest)


def install():
    import mechagnome_race_pack as db
    from test_creature_animations import check
    check()
    report = c.p.load_json(STAGE / 'build-report.json')
    if report.get('status') != 'repair_staged':
        raise ValueError('The current repair stage did not complete')
    processes = subprocess.check_output(['tasklist', '/FO', 'CSV', '/NH'], text=True).lower()
    if any(name in processes for name in ('wow.exe', 'eclipse.exe', 'mpqeditor.exe')):
        raise RuntimeError('Close WoW/Eclipse/MPQEditor before replacing the checked repair')
    for name, expected in (('Wow.exe', report['preserved_exe_sha256']),
                           ('EsteriaAppearance.dll', report['preserved_helper_sha256'])):
        if c.p.sha256(c.p.CLIENT_DEFAULT / name) != expected:
            raise ValueError('Installed runtime changed since staging: ' + name)
    files = {n: STAGE / 'pack' / n for n in report['stage_hashes']}
    files.update({n: STAGE / n for n in report['companion_hashes']})
    for name, source in files.items():
        expected = report['stage_hashes'].get(name, report['companion_hashes'].get(name))
        if c.p.sha256(source) != expected:
            raise ValueError('Staged repair changed: ' + name)
    backup = Path(r'C:\Users\Zach\.codex\backups') / ('creature-animation-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(parents=True, exist_ok=False)
    before = {}
    for name in files:
        live = c.p.CLIENT_DEFAULT / name
        before[name] = c.p.sha256(live)
        if name in report['source_hashes'] and before[name] != report['source_hashes'][name]:
            raise ValueError('Live archive changed since staging')
        target = backup / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live, target)
        assert c.p.sha256(target) == before[name]
    live_server = c.p.SERVER_DBC_ROOT / 'CreatureDisplayInfo.dbc'
    if c.p.sha256(live_server) != report['server_before_sha256']:
        raise ValueError('Live server DBC changed since staging')
    shutil.copy2(live_server, backup / 'CreatureDisplayInfo.dbc')
    assert c.p.sha256(backup / 'CreatureDisplayInfo.dbc') == report['server_before_sha256']
    appearance = db.sql('SELECT guid,race,gender,skin,face,hairStyle,hairColor,facialStyle,extraAppearance '
                        'FROM characters ORDER BY guid;', 'acore_characters')
    report.update(backup=str(backup), before_hashes=before,
                  saved_character_sha256=hashlib.sha256(appearance.encode()).hexdigest())
    c.save(backup / 'install-plan.json', report)
    server_changed = report['server_before_sha256'] != report['server_after_sha256']
    if server_changed:
        subprocess.run(['docker', 'compose', 'stop', 'ac-worldserver'], check=True)
    try:
        for name, source in files.items():
            target = c.p.CLIENT_DEFAULT / name
            temporary = target.with_suffix(target.suffix + '.animation-next')
            shutil.copy2(source, temporary)
            assert c.p.sha256(temporary) == c.p.sha256(source)
            os.replace(temporary, target)
        if server_changed:
            shutil.copy2(STAGE / 'server-dbc/CreatureDisplayInfo.dbc', live_server)
        assert c.p.sha256(live_server) == report['server_after_sha256']
        after = db.sql('SELECT guid,race,gender,skin,face,hairStyle,hairColor,facialStyle,extraAppearance '
                       'FROM characters ORDER BY guid;', 'acore_characters')
        if after != appearance:
            raise ValueError('Saved appearance changed during the repair')
    except Exception:
        for name in files:
            shutil.copy2(backup / name, c.p.CLIENT_DEFAULT / name)
        shutil.copy2(backup / 'CreatureDisplayInfo.dbc', live_server)
        if server_changed:
            subprocess.run(['docker', 'compose', 'up', '-d', '--no-deps', '--no-build', '--pull', 'never',
                            '--force-recreate', 'ac-worldserver'], check=True)
        raise
    if server_changed:
        subprocess.run(['docker', 'compose', 'up', '-d', '--no-deps', '--no-build', '--pull', 'never',
                        '--force-recreate', 'ac-worldserver'], check=True)
    report.update(status='repair_installed_awaiting_fresh_client',
                  worldserver_recreated=server_changed,
                  installed_hashes={n: c.p.sha256(c.p.CLIENT_DEFAULT / n) for n in files})
    c.save(STAGE / 'last-install.json', report)
    c.save(backup / 'install-report.json', report)
    print('REPAIR INSTALLED', backup, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('stage', 'install'))
    args = parser.parse_args()
    (stage if args.action == 'stage' else install)()
