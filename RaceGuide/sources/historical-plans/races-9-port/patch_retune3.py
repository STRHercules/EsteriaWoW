import pathlib

path = pathlib.Path(".agents/plans/races-9-port/retune_vulpera_helm_calibration.py")
text = path.read_text(encoding="utf-8")
text = text.replace('STRIDE = 48\nBONE_SIZE = 0x58',
                    'STRIDE = 48\nATTACHMENT_STRIDE = 0x28\nBONE_SIZE = 0x58')
text = text.replace('''def real_anchor(payload: bytes, attachment_id: int = 11):
    count, offset = struct.unpack_from("<II", payload, 0xF0)
    for index in range(count):
        record = offset + index * STRIDE''',
                    '''def real_anchor(payload: bytes, attachment_id: int = 11):
    count, offset = struct.unpack_from("<II", payload, 0xF0)
    for index in range(count):
        record = offset + index * ATTACHMENT_STRIDE''')
path.write_text(text, encoding="utf-8")
print("patched")
