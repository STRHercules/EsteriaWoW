import pathlib

path = pathlib.Path("fix_vulpera_head_attachment.py")
text = path.read_text(encoding="utf-8")

text = text.replace(
    'HEAD_TOP_BONE_KEY = 197  # bone index that marks the top of the skull\n',
    'HEAD_KEY_BONE = 6  # M2 key bone id for the head\n')

old = '''def bone_pivot(payload: bytes, index: int):
    count, offset = struct.unpack_from("<II", payload, 0x2C)
    if index >= count:
        return None
    record = offset + index * BONE_SIZE
    return struct.unpack_from("<3f", payload, record + 0x4C)
'''
new = '''def bone_record(payload: bytes, index: int):
    count, offset = struct.unpack_from("<II", payload, 0x2C)
    if index >= count:
        return None
    return offset + index * BONE_SIZE


def head_top(payload: bytes):
    """Pivot of the highest bone hanging off the head bone (the top of the skull)."""
    count, offset = struct.unpack_from("<II", payload, 0x2C)
    head_index = None
    for index in range(count):
        record = offset + index * BONE_SIZE
        if struct.unpack_from("<i", payload, record)[0] == HEAD_KEY_BONE:
            head_index = index
    if head_index is None:
        raise SystemExit("model has no head key bone")
    head_pivot = struct.unpack_from("<3f", payload, offset + head_index * BONE_SIZE + 0x4C)
    best = None
    for index in range(count):
        record = offset + index * BONE_SIZE
        parent = struct.unpack_from("<h", payload, record + 8)[0]
        if parent != head_index:
            continue
        pivot = struct.unpack_from("<3f", payload, record + 0x4C)
        if not (head_pivot[2] - 0.05 <= pivot[2] <= head_pivot[2] + 0.35):
            continue
        if best is None or pivot[2] > best[1][2]:
            best = (index, pivot)
    if best is None:
        return head_pivot
    return best[1]
'''
assert old in text
text = text.replace(old, new)

text = text.replace('            top = bone_pivot(patched, HEAD_TOP_BONE_KEY)',
                    '            top = head_top(patched)')
path.write_text(text, encoding="utf-8")
print("patched")
