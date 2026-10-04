import pathlib

broken = 'R:' + chr(92) + 'Zach' + chr(92) + 'Documents'
fixed = 'R:' + chr(92) + 'Users' + chr(92) + 'Zach' + chr(92) + 'Documents'
touched = []
for path in pathlib.Path(".").glob("*.py"):
    text = path.read_text(encoding="utf-8")
    if broken in text and fixed not in text:
        path.write_text(text.replace(broken, fixed), encoding="utf-8")
        touched.append(path.name)
print("repaired:", touched)
