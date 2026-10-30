"""Check that tighter garment shells retain their anatomical relationship in animated poses."""

import argparse
import json
from pathlib import Path

import numpy as np
from wotlkconv.m2 import parse_m2

import creature_animation_repair as motion


def check(work):
    baseline = json.loads((work / 'baseline.json').read_text())['files']
    validation = json.loads((work / 'fit-validation.json').read_text())
    report = {}
    for name in ('drakkin', 'drakonid'):
        before = parse_m2((work / (name + '.m2.before')).read_bytes())
        path = work / 'stage' / Path(*baseline[name + '.m2']['entry'].split('\\'))
        after = parse_m2(path.read_bytes())
        pairs = np.array(validation[name]['matches'])
        shells, parents = pairs[:, 0], pairs[:, 1]
        assert before.vertex_count == after.vertex_count
        for index, material in enumerate(before.materials):
            if index in validation[name]['changed_materials']:
                assert after.materials[index] == {'flags': 0, 'blending_mode': 1}
            else:
                assert material == after.materials[index]
        for vertex, parent in pairs:
            offset, body_offset = int(vertex) * 48, int(parent) * 48
            assert before.vertices[offset + 12:offset + 20] == before.vertices[body_offset + 12:body_offset + 20]
            assert before.vertices[offset + 12:offset + 48] == after.vertices[offset + 12:offset + 48]
        available = {sequence['id'] for sequence in before.sequences}
        actions = [action for action in (0, 4, 5, 16, 37, 42) if action in available]
        assert len(actions) >= 4
        samples = 0
        for action in actions:
            sequence = before.sequences[motion.sequence(before, action)]
            for fraction in (0.25, 0.75):
                time = int(sequence['duration'] * fraction)
                matrices = motion.pose_matrices(before, action, time)
                old = motion.posed_vertices(before, matrices)
                new = motion.posed_vertices(after, matrices)
                expected = old[parents] + (old[shells] - old[parents]) * 0.25
                assert np.allclose(new[shells], expected, atol=2e-6), (name, action, time)
                samples += 1
        report[name] = {'sampled_actions': actions, 'poses_checked': samples,
                        'garment_vertices_per_pose': len(shells), 'posed_clearance_contract': True}
    (work / 'pose-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    print(json.dumps(check(parser.parse_args().work), indent=2))
