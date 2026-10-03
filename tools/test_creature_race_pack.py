"""Run with python tools/test_creature_race_pack.py after preparing and staging the NPC race pack."""

import ctypes
import hashlib
import itertools
import struct
from pathlib import Path

from luaparser import ast
from wotlkconv.m2 import parse_m2, parse_skin

import creature_race_pack as c


def check():
    decompress = ctypes.WinDLL('ntdll').RtlDecompressBuffer
    decompress.argtypes = [ctypes.c_ushort, ctypes.c_void_p, ctypes.c_ulong,
                           ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong)]
    decompress.restype = ctypes.c_long
    states = 0
    for slug, spec in c.SPECS.items():
        root = c.WORK / slug
        render = c.p.load_json(root / 'integration/rendering.json')
        inventory = c.p.load_json(root / 'reports/source-inventory.json')
        converted = c.p.load_json(root / 'reports/asset-convert.json')
        assert set(render['profiles']) == {str(g) for g in spec['genders']}
        for asset in inventory['assets'].values():
            assert c.p.sha256(Path(asset['path'])) == asset['sha256']
        name = 'ThinHuman' if slug == 'thinhuman' else slug.title()
        bank = (c.STAGE / f'Esteria{name}Textures.bin').read_bytes()
        magic, version, count, digest = struct.unpack_from('<4I', bank)
        assert (magic, version) == (0x31544845, 1) and count > 0
        assert digest == int.from_bytes(hashlib.sha256(bank[16:]).digest()[:4], 'little')
        selectors = (c.STAGE / f'Esteria{name}.bin').read_bytes()
        magic, version, count = struct.unpack_from('<3I', selectors)
        assert (magic, version, len(selectors)) == (0x314D4845, 1, 12 + count * 156)
        records = [struct.unpack_from('<7I', selectors, 12 + i * 156) for i in range(count)]
        decoded = {}
        for record in records:
            if record[1] != 3 or record[3] in decoded:
                continue
            offset = record[3]
            width, height, length = struct.unpack_from('<3I', bank, offset)
            assert 0 < width <= 512 and 0 < height <= 512 and offset + 12 + length <= len(bank)
            packed = ctypes.create_string_buffer(bank[offset + 12:offset + 12 + length])
            output = ctypes.create_string_buffer(width * height * 4)
            size = ctypes.c_ulong()
            assert decompress(2, output, len(output), packed, length, ctypes.byref(size)) == 0
            assert size.value == len(output)
            decoded[offset] = output.raw
        for gender, model_info in render['models'].items():
            profile = render['profiles'][gender]
            native = root.joinpath('integration/patch-root', *c.PureWindowsPath(model_info['path']).parts)
            model = parse_m2(native.read_bytes())
            skin = parse_skin(native.with_name(native.stem + '00.skin').read_bytes())
            original_key = converted['models'][inventory['core_models'][gender].__str__()]['path']
            original_path = root.joinpath('output/patch-root', *c.PureWindowsPath(original_key).parts)
            original = parse_m2(original_path.read_bytes())
            assert model.vertex_count == original.vertex_count
            assert all(model.vertices[i:i + 12] == original.vertices[i:i + 12]
                       for i in range(0, len(model.vertices), 48))
            assert len(model.sequences) >= len(original.sequences) > 0
            assert len(model.events) >= len(original.events)
            assert len(skin.vertices) <= 65535 and skin.bone_count_max <= 75
            assert all(not track.external for track in model.tracks())
            if spec['hide_helm']:
                assert model.attachment_lookup[11] == 65535
            for texture in model.textures:
                if texture['type'] == 0 and texture['filename']:
                    assert root.joinpath('integration/patch-root', *c.PureWindowsPath(texture['filename']).parts).is_file()
            active = [r for r in records if r[0] == int(gender)]
            for fields in itertools.product(*(range(n) for n in profile['capacities'])):
                selected = [r for r in active if all(v == 0xffffffff or fields[v & 65535] == v >> 16
                                                    for v in r[4:])]
                assert any(r[1] == 3 and r[2] == 0 for r in selected), (slug, gender, fields)
                assert any(r[1] == 2 and r[3] == 10000 for r in selected)
                if slug != 'naga':
                    assert any(r[1] == 3 and r[2] == 2 for r in selected), (slug, fields)
                states += 1
    for path in (c.STAGE / 'glue').glob('*.lua'):
        ast.parse(path.read_text(encoding='utf-8'))
    for name in ('ChrRaces', 'CharSections', 'CharHairGeosets', 'BarberShopStyle', 'CharStartOutfit', 'NameGen',
                 'CreatureDisplayInfo', 'CreatureModelData'):
        staged = c.p.RawWdbc((c.STAGE / 'server-dbc' / (name + '.dbc')).read_bytes())
        old = c.p.RawWdbc(c.p._full_table(c.p.CLIENT_DEFAULT / 'Data', name)[0])
        new_records = set(staged.records)
        assert all(row in new_records for row in old.records), name
        assert staged.strings.startswith(old.strings), name
        assert len({row[:4] for row in staged.records}) == len(staged.records), name
    races = c.p.RawWdbc((c.STAGE / 'server-dbc/ChrRaces.dbc').read_bytes())
    rows = {c.p._value(r, 0): r for r in races.records}
    assert c.p._value(rows[54], 4) & 2
    for slug, spec in c.SPECS.items():
        for race, faction in zip(spec['targets'], spec['factions']):
            assert c.p._value(rows[race], 13 * 4) == (0 if faction == 'alliance' else 1)
            assert c.p._value(rows[race], 5 * 4) == (60049 if race == 54 else 0)
    report = c.p.load_json(c.STAGE / 'build-report.json')
    assert c.p.sha256(c.p.CLIENT_DEFAULT / 'Wow.exe') == report['exe_sha256']
    for rel, digest in report['source_hashes'].items():
        assert c.p.sha256(c.p.CLIENT_DEFAULT / rel) == digest
    print(f'PASS: {states} appearance combinations; source geometry/animations, texture banks, gender/faction '
          'data, Lua and unrelated DBC rows preserved. Native compilation and live rendering remain unverified.')


if __name__ == '__main__':
    check()
