import pathlib

path = pathlib.Path("verify_calibration.py")
text = path.read_text(encoding="utf-8")
text = text.replace('model = struct.unpack_from("<i", storm.read(handle, key + ".m2"), 0)',
                    'model = struct.unpack_from("<i", storm.read(handle, key + ".m2"), 0)[0]')
path.write_text(text, encoding="utf-8")
print("patched")
