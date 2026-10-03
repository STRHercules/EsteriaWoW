"""Check the reported actions against source ANIM keys and the prepared native models."""

import math
import struct
import ctypes
from pathlib import Path

from PIL import Image

from wotlkconv.m2 import parse_m2, parse_skin
from wotlkconv.m2.types import VALUE_FORMATS, value_size

import creature_animation_repair as repair
import creature_race_pack as c
import skyborne_visual_pack as v


def check():
    tracks_checked = 0
    for slug, spec in c.SPECS.items():
        root = c.WORK / slug
        render = c.p.load_json(root / 'integration/rendering.json')
        inventory = c.p.load_json(root / 'reports/source-inventory.json')
        converted = c.p.load_json(root / 'reports/asset-convert.json')
        for gender, info in render['models'].items():
            path = root.joinpath('integration/patch-root', *c.PureWindowsPath(info['path']).parts)
            data = path.read_bytes()
            model = parse_m2(data)
            skin = parse_skin(path.with_name(path.stem + '00.skin').read_bytes())
            assert all(q['flags'] & 0x20 for q in model.sequences)
            for track in model.tracks():
                assert not track.external
                assert -1 <= track.global_sequence < len(model.global_loops)
                for i, (n, offset) in enumerate(track.timestamp_spans):
                    assert not n or 0 < offset <= offset + n * 4 <= len(data)
                    times = track.timestamps[i]
                    assert len(times) == n and times == sorted(times), (slug, gender, i)
                    if track.global_sequence < 0 and times:
                        assert max(times) <= model.sequences[i]['duration'] + 1
                    if hasattr(track, 'values'):
                        count, pos = track.value_spans[i]
                        assert count == n
                        assert not n or 0 < pos <= pos + n * value_size(track.kind) <= len(data)
                        assert all(math.isfinite(x) for row in track.values[i]
                                   for x in (row if isinstance(row, tuple) else (row,)))
                    tracks_checked += 1
            fid = str(inventory['core_models'][gender])
            original_key = converted['models'][fid]['path']
            original_path = root.joinpath('output/patch-root', *c.PureWindowsPath(original_key).parts)
            source = v.read_player_model(original_path)
            # Directly check every external skeletal track, including the reported Laugh/Use/Sit sequences.
            for old_bone, bone in zip(source.bones, model.bones[:len(source.bones)], strict=True):
                for name in ('translation', 'rotation', 'scale'):
                    source_track = old_bone[name]
                    track = bone[name]
                    for i in source_track.external:
                        sequence = source.sequences[i]
                        n, offset = source_track.timestamp_spans[i]
                        if not n or sequence['flags'] & 0x40:
                            continue
                        animation = original_path.with_name(
                            f'{original_path.stem}{sequence["id"]:04d}-{sequence["variation_index"]:02d}.anim')
                        blob = animation.read_bytes()
                        times = list(struct.unpack_from('<' + 'I' * n, blob, offset))
                        assert track.timestamps[i] == times, (slug, gender, sequence['id'], name)
                        count, pos = source_track.value_spans[i]
                        fmt = VALUE_FORMATS[source_track.kind]
                        stride = struct.calcsize('<' + fmt)
                        values = [struct.unpack_from('<' + fmt, blob, pos + j * stride) for j in range(count)]
                        assert track.values[i] == values, (slug, gender, sequence['id'], name)
            for action in info.get('action_repair', {}).get('added_actions', []):
                index = repair.sequence(model, action['animation'])
                assert action['moving_matched_bones']
                if action['animation'] in (89, 90):
                    for identifier in (b'$SHL', b'$SHR'):
                        event = next(e for e in model.events if e['identifier'] == identifier)
                        assert event['enabled'].timestamps[index]
            for alias in info.get('action_repair', {}).get('wrath_action_aliases', []):
                index = repair.sequence(model, alias['animation'])
                source_index = repair.sequence(model, alias['authored_source'])
                for track in model.tracks():
                    if track.global_sequence < 0 and source_index < len(track.timestamps):
                        assert track.timestamps[index] == track.timestamps[source_index]
                        if hasattr(track, 'values'):
                            assert track.values[index] == track.values[source_index]
            for index, q in enumerate(model.sequences):
                if not q['flags'] & 0x40:
                    continue
                target, visited = index, set()
                while model.sequences[target]['flags'] & 0x40:
                    assert target not in visited
                    visited.add(target)
                    target = model.sequences[target]['alias_next']
                for track in model.bone_tracks():
                    if track.global_sequence < 0 and index < len(track.timestamps):
                        assert track.timestamps[index] == track.timestamps[target]
            assert len(model.vertices) == len(source.vertices)
            assert all(model.vertices[i:i + 12] == source.vertices[i:i + 12]
                       for i in range(0, len(model.vertices), 48))
            for kind in (1, 6, 8):
                indices = [i for i, texture in enumerate(model.textures) if texture['type'] == kind]
                if indices:
                    assert model.replacable_texture_lookup[kind] == indices[-1]
            if slug == 'naga':
                for batch in skin.batches:
                    first = model.texture_combos[struct.unpack_from('<H', batch, 16)[0]]
                    if model.textures[first]['type'] in (1, 8):
                        assert struct.unpack_from('<H', batch, 14)[0] == 1
                for animation in (37, 38, 39, 89, 90, 91, 123, 128, 129):
                    assert repair.sequence(model, animation) >= 0
            print('PASS', slug, gender, len(model.sequences), 'actions; source keys and static art retained')
    assert abs(c.SPECS['vrykul']['display_scale'] - .55) < 1e-6
    for slug in ('vrykul', 'thinhuman'):
        family = 'Vrykul' if slug == 'vrykul' else 'ThinHuman'
        data = (c.STAGE / f'Esteria{family}.bin').read_bytes()
        count = struct.unpack_from('<I', data, 8)[0]
        records = [struct.unpack_from('<7I', data, 12 + i * 156) for i in range(count)]
        assert not any(r[1] == 0 and r[2] == 11 for r in records)
        assert any(r[1] == 0 and r[2] == 18 and r[3] == (1801 if slug == 'vrykul' else 1800) for r in records)
    naga_info = c.p.load_json(c.WORK / 'naga/integration/rendering.json')['models']['0']
    naga = parse_m2(c.WORK.joinpath('naga', 'integration/patch-root',
        *c.PureWindowsPath(naga_info['path']).parts).read_bytes())
    for attachment in (26, 27, 31, 32, 33):
        assert naga.attachment_lookup[attachment] < len(naga.attachments)
        assert naga.attachments[naga.attachment_lookup[attachment]]['id'] == attachment
    # Vrykul opaque hair must preserve authored RGB from the zero-alpha half of every source color.
    bank = (c.STAGE / 'EsteriaVrykulTextures.bin').read_bytes()
    decode = ctypes.WinDLL('ntdll').RtlDecompressBuffer
    decode.argtypes = [ctypes.c_ushort, ctypes.c_void_p, ctypes.c_ulong,
                       ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong)]
    decode.restype = ctypes.c_long
    rendering = c.p.load_json(c.WORK / 'vrykul/integration/rendering.json')
    inventory = c.p.load_json(c.WORK / 'vrykul/reports/source-inventory.json')
    count = 0
    for layer in rendering['layers']:
        if layer['target'] != 10 or layer['group'] != 2:
            continue
        blob = c.p.Blp.parse(Path(inventory['assets'][str(layer['file_id'])]['path']).read_bytes()).decode_level(0)
        expected = Image.frombytes('RGBA', (blob.width, blob.height), bytes(blob.data))
        expected.putalpha(255)
        expected.thumbnail((512, 512), Image.Resampling.LANCZOS)
        width, height, length = struct.unpack_from('<3I', bank, layer['offset'])
        source = ctypes.create_string_buffer(bank[layer['offset'] + 12:layer['offset'] + 12 + length])
        output = ctypes.create_string_buffer(width * height * 4)
        size = ctypes.c_ulong()
        assert decode(2, output, len(output), source, length, ctypes.byref(size)) == 0
        assert output.raw == expected.tobytes(), layer['file_id']
        assert width == 512 and height == 256
        count += 1
    assert count == 5
    print('PASS', tracks_checked, 'keyframe arrays, alias targets, sockets/events and material bindings')


if __name__ == '__main__':
    check()
