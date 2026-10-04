import sys
sys.path.insert(0, r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
import highmountain_complete_tracks as r
from collections import Counter

for sex in ('male', 'female'):
    path = r.previous.STAGE / f'custom/highmountain/native/{sex}/highmountaintauren{sex}.m2'
    m = r.h.v.read_player_model(path)
    print(sex, 'kinds', Counter(getattr(t, 'kind', 'event') for t in m.tracks() if t.external))
    missing = []
    for i, s in enumerate(m.sequences):
        anim = path.with_name(f"{path.stem}{s['id']:04d}-{s['variation_index']:02d}.anim")
        if s['flags'] & 32 or anim.exists():
            continue
        target = s
        seen = set()
        while target['flags'] & 64:
            index = target['alias_next']
            assert index not in seen
            seen.add(index)
            target = m.sequences[index]
        target_path = path.with_name(f"{path.stem}{target['id']:04d}-{target['variation_index']:02d}.anim")
        populated = sum(i < len(t.timestamp_spans) and t.timestamp_spans[i][0] > 0
                        for t in m.bone_tracks())
        missing.append((i, s['id'], s['flags'], target['id'], target['variation_index'],
                        target_path.exists(), bool(target['flags'] & 32), populated))
    print('missing', missing)
    print('globals', m.global_loops)
    staged = r.STAGE.joinpath('custom/highmountain/native', sex, path.name)
    if staged.exists():
        from wotlkconv.m2 import parse_m2
        from wotlkconv.m2.skel import parse_skel
        out = parse_m2(staged.read_bytes())
        parent_id = 1839011 if sex == 'male' else 1830371
        parent = parse_skel((r.h.PROJECT / 'sources/retail/races/highmountain_tauren' / f'{parent_id}.skel').read_bytes())
        bad = []
        for bi, bone in enumerate(out.bones):
            for kind in ('translation', 'rotation', 'scale'):
                for i, times in enumerate(bone[kind].timestamps):
                    if times != sorted(times):
                        if len(bad) < 4:
                            s = m.sequences[i]
                            target = s['alias_next']
                            print('BAD', bi, kind, i, s['id'], times[:12],
                                  'alias span', m.bones[bi][kind].timestamp_spans[i],
                                  'target span', m.bones[bi][kind].timestamp_spans[target],
                                  'source spans', parent.bones[bi][kind].timestamp_spans[parent.sequence_lookups[s['id']]])
                        bad.append((bi, kind, i, m.sequences[i]['id']))
        print('bad bone tracks', len(bad), Counter(x[-1] for x in bad))
        raw = parse_m2((r.h.PROJECT / 'sources/retail/races/highmountain_tauren' / f'{r.h.MODELS[sex]}.m2').read_bytes())
        out.bones_from_skeleton = True
        out.attachments_from_skeleton = True
        print('own groups', [(name, len(getattr(raw, name)), len(getattr(out, name)))
                             for name in ('colors', 'texture_transforms', 'lights', 'cameras', 'ribbons', 'particles')])
        for n, t in enumerate(raw.own_tracks()):
            if getattr(t, 'kind', '') in ('splinevec3', 'splinef32', 'quat', 'vec3'):
                print('raw own', n, t.kind, t.global_sequence, len(t.timestamps),
                      [(i, len(times), times[:4]) for i, times in enumerate(t.timestamps) if times][:3],
                      'external', t.external)
        for n, t in enumerate(out.own_tracks()):
            bad_times = [(i, times[:5]) for i, times in enumerate(t.timestamps) if times != sorted(times)]
            if bad_times:
                print('bad own', n, getattr(t, 'kind', 'event'), bad_times[:3])
