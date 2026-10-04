"""Append Ascension appearance choices without changing installed choices or models.

The input ZIP must match its GitHub tree manifest. Only playable, ordinary
customizations for the ten supplied HD races are used; donor NPC and DK data
are excluded. Stage first, review merge-report.json, then install the artifacts.
"""

import argparse
import hashlib
import io
import json
import re
import struct
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

from PIL import Image

from cars_mount_pack import Wdbc
from playable_race_pack import RawWdbc

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'modules/mod-classless-wildcard/client-patch'))
from lib.clientfs import ClientFiles

RACES = {1: 'Human', 2: 'Orc', 3: 'Dwarf', 4: 'NightElf', 5: 'Scourge',
         6: 'Tauren', 7: 'Gnome', 8: 'Troll', 10: 'BloodElf', 11: 'Draenei'}


def normal(row):
    return row[7] & 1 and not row[7] & 4


def blob_sha(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def key(row):
    # Race2's model flag does not define a separate saved appearance choice.
    return (*row[1:4], row[7] & ~16, *row[8:10])


def selection_map(groups, occupied, matches):
    """Reuse compatible choices; append incompatible/new choices above every old ID."""
    next_id = max(occupied, default=-1) + 1
    result = {}
    for value in sorted(groups):
        equivalent = matches(value, groups[value])
        if equivalent is None:
            if next_id > 255:
                raise ValueError('Appearance selection exceeds its saved byte')
            equivalent = next_id
            next_id += 1
        result[value] = equivalent
    return result


def plan_sections(current, incoming, current_payload, donor_payload, hairstyle_map):
    """Return donor row copies with collision-free appearance bytes, plus the mapping."""
    existing = {key(r): current_payload(r) for r in current if normal(r)}
    normal_current = [r for r in current if normal(r)]
    donor = [list(r) for r in incoming if normal(r)]
    skin_rows = {r[9]: r for r in donor if r[3] == 0}
    hair_colors = {r[9] for r in donor if r[3] == 3}
    # Face/underwear rows for NPC-only or DK-only skin colors are not playable.
    donor = [r for r in donor if r[3] in (2, 3) or r[9] in skin_rows]
    donor = [r for r in donor if r[3] != 2 or r[9] in hair_colors]
    for row in donor:
        if row[3] == 3:
            row[8] = hairstyle_map[row[8]]

    old_skins = {r[9]: current_payload(r) for r in normal_current if r[3] == 0}
    skin_groups = {v: [r] for v, r in skin_rows.items()}

    def skin_match(value, rows):
        payload = donor_payload(rows[0])
        candidates = [v for v, old in old_skins.items() if old == payload]
        return value if value in candidates else min(candidates, default=None)

    skins = selection_map(skin_groups, {r[9] for r in current if r[3] in (0, 1, 4)}, skin_match)
    for row in donor:
        if row[3] in (0, 1, 4):
            row[9] = skins[row[9]]

    maps = {'skin': skins}
    for label, types, field in (('face', (1,), 8), ('hair_color', (2, 3), 9)):
        groups = defaultdict(list)
        for row in donor:
            if row[3] in types:
                groups[row[field]].append(row)
        old_values = {r[field] for r in normal_current if r[3] in types}

        def matches(value, rows):
            if value not in old_values:
                return None
            compatible = all(key(r) not in existing or existing[key(r)] == donor_payload(r) for r in rows)
            return value if compatible else None

        mapping = selection_map(groups, {r[field] for r in current if r[3] in types}, matches)
        maps[label] = mapping
        for row in donor:
            if row[3] in types:
                row[field] = mapping[row[field]]

    additions = []
    for row in donor:
        payload = donor_payload(row)
        selection = key(row)
        if selection in existing:
            if existing[selection] != payload:
                raise ValueError(f'Unresolved appearance collision: {selection}')
            continue
        existing[selection] = payload
        additions.append(row)
    return additions, maps


def append_rows(data, additions, paths=None):
    base = RawWdbc(data)
    pool = bytearray(base.strings)
    offsets = {}
    records = []
    next_id = max((int.from_bytes(r[:4], 'little') for r in base.records), default=0) + 1
    for original in additions:
        row = list(original)
        row[0] = next_id
        next_id += 1
        if paths:
            for field in (4, 5, 6):
                value = paths(row[field]) if row[field] else ''
                if not value:
                    row[field] = 0
                    continue
                if value not in offsets:
                    offsets[value] = len(pool)
                    pool.extend(value.encode('ascii') + b'\0')
                row[field] = offsets[value]
        records.append(struct.pack('<' + 'I' * base.fields, *row))
    output = base.build([*base.records, *records], bytes(pool))
    after = RawWdbc(output)
    if after.records[:base.count] != base.records or not after.strings.startswith(base.strings):
        raise ValueError('Existing DBC bytes changed')
    return output


def append_barber(data, sections):
    barber = Wdbc(data)
    existing = {(r[1], *r[37:40]) for r in barber.rows}
    additions = []
    for row in sections:
        if row[3] != 0 or (3, row[1], row[2], row[9]) in existing:
            continue
        template = next((r for r in barber.rows if r[1] == 3 and r[37:39] == row[1:3]),
                        next(r for r in barber.rows if r[1] == 3))
        new = list(template)
        new[37:40] = [row[1], row[2], row[9]]
        # A copied name would describe a different color; the native UI supplies its label.
        new[2:36] = [0] * 34
        additions.append(new)
        existing.add((3, *new[37:40]))
    return append_rows(data, additions), len(additions)


def stage(args):
    root = args.workspace
    tree = {x['path'].replace('/', '\\').lower(): x for x in
            json.loads((root / 'upstream-tree.json').read_text())['tree'] if x['type'] == 'blob'}
    for name in ('CharSections', 'CharHairGeosets'):
        data = (root / 'donor-dbc' / (name + '.dbc')).read_bytes()
        if blob_sha(data) != tree['dbfilesclient\\' + name.lower() + '.dbc']['sha']:
            raise ValueError('Donor DBC does not match the pinned source: ' + name)
    archive = zipfile.ZipFile(root / 'upstream.zip')
    members = {n.split('/', 1)[1].replace('/', '\\').lower(): n for n in archive.namelist() if '/' in n}
    client = ClientFiles(str(args.client / 'Data'), 'enUS')
    source = Wdbc((root / 'donor-dbc/CharSections.dbc').read_bytes())
    base_bytes = (root / 'client-before/CharSections.dbc').read_bytes()
    base = Wdbc(base_bytes)
    current_geo = Wdbc((root / 'client-before/CharHairGeosets.dbc').read_bytes())
    donor_geo = Wdbc((root / 'donor-dbc/CharHairGeosets.dbc').read_bytes())
    out = root / 'staged'
    assets = out / 'assets'
    assets.mkdir(parents=True, exist_ok=True)
    repairs = {}
    cache = {}
    content_cache = {}
    report = {'source_commit': json.loads((root / 'upstream-commit.json').read_text())['sha'],
              'races': [], 'repairs': repairs, 'excluded_dk_and_npc_rows': 0}

    def read_original(path):
        normalized = path.replace('/', '\\').lower()
        if normalized in tree:
            payload = archive.read(members[normalized])
            if blob_sha(payload) != tree[normalized]['sha']:
                raise ValueError('Source blob mismatch: ' + path)
            return payload
        return None

    def texture(path):
        if path in cache:
            return cache[path]
        payload = read_original(path)
        if payload is None:
            # Several source rows name absent transparent overlays. Verify before reuse.
            fallback = re.sub(r'_\d+\.blp$', '_00.blp', path, flags=re.I)
            candidate = read_original(fallback)
            alpha = Image.open(io.BytesIO(candidate)).convert('RGBA').getchannel('A') if candidate else None
            if alpha is not None and alpha.getextrema() == (0, 0):
                payload = candidate
                repairs[path] = {'transparent_overlay': fallback}
            else:
                # These two missing Scourge files exist by exact name in the local donor extraction.
                permitted = {'Character\\Scourge\\Female\\ScourgeFemaleFaceLower06_25.blp',
                             'Character\\Scourge\\Female\\ScourgeFemaleNakedPelvisSkin00_24.blp'}
                if path not in permitted:
                    raise FileNotFoundError('Unresolved donor texture: ' + path)
                original = args.extracted / Path(*path.split('\\'))
                payload = original.read_bytes()
                Image.open(io.BytesIO(payload)).load()
                repairs[path] = {'exact_source': str(original), 'sha256': hashlib.sha256(payload).hexdigest()}
        if payload[:4] not in (b'BLP1', b'BLP2'):
            raise ValueError('Invalid donor texture: ' + path)
        fingerprint = blob_sha(payload)
        parts = path.split('\\')
        if len(parts) > 2 and parts[0].lower() == 'character':
            parts[1] += '2'
        candidate_path = '\\'.join(parts)
        try:
            current, _ = client.find(candidate_path)
        except FileNotFoundError:
            current = None
        if current is not None and blob_sha(current) == fingerprint:
            destination = candidate_path
        else:
            destination = 'Character\\EsteriaAscensionCustomization\\' + path.split('\\', 1)[1]
            target = assets.joinpath(*destination.split('\\'))
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and target.read_bytes() != payload:
                raise ValueError('Asset staging collision: ' + destination)
            target.write_bytes(payload)
        cache[path] = (fingerprint, destination)
        return cache[path]

    def donor_payload(row):
        return tuple(texture(source.text(row[f]))[0] if row[f] else '' for f in (4, 5, 6))

    def current_payload(row):
        result = []
        for field in (4, 5, 6):
            path = base.text(row[field]) if row[field] else ''
            if path and path not in content_cache:
                try:
                    content_cache[path] = blob_sha(client.find(path)[0])
                except FileNotFoundError:
                    # Preserve pre-existing broken rows; never treat them as donor matches.
                    content_cache[path] = 'missing:' + path
            result.append(content_cache[path] if path else '')
        return tuple(result)

    additions = []
    for race, name in RACES.items():
        for gender in (0, 1):
            old = [r for r in base.rows if r[1:3] == [race, gender]]
            incoming = [r for r in source.rows if r[1:3] == [race, gender]]
            style_map = {}
            old_geo = [r for r in current_geo.rows if r[1:3] == [race, gender]]
            for donor_row in donor_geo.rows:
                if donor_row[1:3] != [race, gender]:
                    continue
                candidates = [r[3] for r in old_geo if r[4:] == donor_row[4:]]
                if not candidates:
                    raise ValueError(f'Donor hairstyle needs new model geometry: {donor_row}')
                style_map[donor_row[3]] = donor_row[3] if donor_row[3] in candidates else min(candidates)
            new, maps = plan_sections(old, incoming, current_payload, donor_payload, style_map)
            # Retain Esteria's extra bald choices with every newly appended hair color.
            extra_styles = {r[3] for r in old_geo} - set(style_map.values())
            old_colors = {r[9] for r in old if r[3] == 3}
            for style in sorted(extra_styles):
                template = next(r for r in old if r[3] == 3 and r[8] == style and r[9] == 0)
                payload = current_payload(template)
                counterpart = next((r for r in incoming if r[3] == 3 and r[9] == 0 and normal(r)
                                    and all(not p or p == d for p, d in zip(payload, donor_payload(r)))), None)
                if counterpart is None:
                    raise ValueError(f'No compatible color template for existing hairstyle: {race}, {gender}, {style}')
                source_style = style_map[counterpart[8]]
                colored = [r for r in new if r[3] == 3 and r[8] == source_style and r[9] not in old_colors]
                for candidate in colored:
                    copy = list(candidate)
                    copy[8] = style
                    for field in (4, 5, 6):
                        if not template[field]:
                            copy[field] = 0
                    new.append(copy)
            hair_pairs = {(r[8], r[9]) for r in old + new if r[3] == 3 and normal(r)}
            styles = {r[8] for r in old if r[3] == 3 and normal(r)}
            missing = [(s, c) for s in styles for c in maps['hair_color'].values() if (s, c) not in hair_pairs]
            if missing:
                raise ValueError(f'New hair colors are incomplete: {race}, {gender}, {missing}')
            additions.extend(new)
            report['races'].append({'race': race, 'name': name, 'gender': gender, 'added_rows': len(new),
                                    'mapping': maps, 'hair_style_mapping': style_map})
            print(name, gender, 'appended rows:', len(new), flush=True)
    report['excluded_dk_and_npc_rows'] = sum(1 for r in source.rows if r[1] not in RACES or not normal(r))
    sections = append_rows(base_bytes, additions, lambda offset: texture(source.text(offset))[1])
    barber, count = append_barber((root / 'client-before/BarberShopStyle.dbc').read_bytes(), additions)
    for name, data in (('CharSections', sections), ('BarberShopStyle', barber)):
        (out / (name + '.dbc')).write_bytes(data)
    report.update(added_sections=len(additions), added_barber_rows=count, assets=len(list(assets.rglob('*.blp'))))
    (out / 'merge-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    client.close()
    archive.close()
    print(json.dumps({k: v for k, v in report.items() if k not in ('races', 'repairs')}))


def self_check():
    def row(kind, variation, color, texture, flags=17):
        return [1, 1, 0, kind, texture, 0, 0, flags, variation, color]

    old = [row(0, 0, 0, 100), row(0, 0, 1, 999, 5), row(1, 0, 0, 200, 1), row(3, 0, 0, 300)]
    donor = [row(0, 0, 0, 100), row(0, 0, 2, 101), row(1, 0, 0, 201, 1),
             row(1, 0, 2, 202, 1), row(3, 0, 0, 301), row(0, 0, 3, 900, 5)]
    payload = lambda r: tuple(r[4:7])
    added, maps = plan_sections(old, donor, payload, payload, {0: 0})
    assert maps == {'skin': {0: 0, 2: 2}, 'face': {0: 1}, 'hair_color': {0: 1}}
    assert all(r[7] != 5 for r in added)
    assert {(r[3], r[8], r[9]) for r in added} == {(0, 0, 2), (1, 1, 0), (1, 1, 2), (3, 0, 1)}
    raw = struct.pack('<4s4I', b'WDBC', len(old), 10, 40, 1)
    raw += b''.join(struct.pack('<10I', *r) for r in old) + b'\0'
    output = append_rows(raw, added)
    assert RawWdbc(output).records[:len(old)] == RawWdbc(raw).records
    swapped, _ = plan_sections(old, [row(3, 1, 2, 400)], payload, payload, {1: 0})
    assert swapped[0][8] == 0
    orphaned, _ = plan_sections(old, [row(2, 0, 2, 400)], payload, payload, {0: 0})
    assert not orphaned
    try:
        selection_map({1: []}, {255}, lambda *_: None)
    except ValueError:
        pass
    else:
        raise AssertionError('Byte capacity guard did not run')
    print('Additive merge self-check passed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check', action='store_true')
    parser.add_argument('--workspace', type=Path, default=Path(r'C:\Users\Zach\.codex\tmp\ascension-customization'))
    parser.add_argument('--client', type=Path, default=Path(r'G:\3.3.5a - Dev'))
    parser.add_argument('--extracted', type=Path,
                        default=Path(r'G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\patch-CHA.mpq'))
    args = parser.parse_args()
    self_check() if args.self_check else stage(args)
