import pathlib

path = pathlib.Path("check_pa_vu_textures.py")
text = path.read_text(encoding="utf-8")
lines = text.splitlines()
for index, line in enumerate(lines):
    if line.startswith("STEM ="):
        lines[index] = 'STEM = "item' + chr(92) * 2 + 'objectcomponents' + chr(92) * 2 + 'head' + chr(92) * 2 + '"'
path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(lines[22])
