import pathlib

path = pathlib.Path(".agents/plans/races-9-port/retune_vulpera_helm_calibration.py")
text = path.read_text(encoding="utf-8")

old = '''def skull_box(payload: bytes):
    count, offset = struct.unpack_from("<II", payload, 0x3C)
    bones = head_bone_set(payload)'''
new = '''def head_bone_pivot(payload: bytes):
    count, offset = struct.unpack_from("<II", payload, 0x2C)
    for index in range(count):
        record = offset + index * BONE_SIZE
        if struct.unpack_from("<i", payload, record)[0] == HEAD_KEY_BONE:
            return struct.unpack_from("<3f", payload, record + 0x4C)
    return (0.0, 0.0, 0.0)


def real_anchor(payload: bytes, attachment_id: int = 11):
    count, offset = struct.unpack_from("<II", payload, 0xF0)
    for index in range(count):
        record = offset + index * STRIDE
        if struct.unpack_from("<I", payload, record)[0] == attachment_id:
            return struct.unpack_from("<3f", payload, record + 8)
    raise SystemExit("attachment 11 not found in the model's real table")


def skull_box(payload: bytes):
    count, offset = struct.unpack_from("<II", payload, 0x3C)
    bones = head_bone_set(payload)
    ceiling = head_bone_pivot(payload)[2] + 0.30  # keep the skull, drop the ear tips'''
assert old in text
text = text.replace(old, new)

old = '''        if not weights[best] or indices[best] not in bones:
            continue'''
new = '''        if not weights[best] or indices[best] not in bones:
            continue
        if point[2] > ceiling:
            continue'''
assert old in text
text = text.replace(old, new)

old = '''            ideal_x = ((low[0] + high[0]) - (helm_low[0] + helm_high[0])) / 2
            ideal_z = ((low[2] + high[2]) - (helm_low[2] + helm_high[2])) / 2'''
new = '''            anchor = real_anchor(character)
            print(f"   real attachment 11: ({anchor[0]:+.3f}, {anchor[1]:+.3f}, {anchor[2]:+.3f})")
            ideal_x = ((low[0] + high[0]) - (helm_low[0] + helm_high[0])) / 2 - anchor[0]
            ideal_z = ((low[2] + high[2]) - (helm_low[2] + helm_high[2])) / 2 - anchor[2]'''
assert old in text
text = text.replace(old, new)
path.write_text(text, encoding="utf-8")
print("patched")
