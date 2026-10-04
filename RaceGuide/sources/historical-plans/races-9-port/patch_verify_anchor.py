import pathlib

path = pathlib.Path("verify_calibration3.py")
text = path.read_text(encoding="utf-8")
text = text.replace("ANCHOR = (-0.001, 0.0, 1.270)", "ANCHOR = (-0.103, 0.0, 1.171)")
path.write_text(text, encoding="utf-8")
print("patched")
