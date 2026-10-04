import pathlib

path = pathlib.Path("compare_vulpera_rows.py")
text = path.read_text(encoding="utf-8")
old = '               "patch-x.mpq", "patch-y.mpq", "patch-z.mpq"]'
new = ('               "patch-x.mpq", "patch-y.mpq", "patch-z.mpq",\n'
       '               "enUS' + chr(92) + 'locale-enUS.MPQ", "enUS' + chr(92) + 'patch-enUS.MPQ",\n'
       '               "enUS' + chr(92) + 'patch-enUS-2.MPQ", "enUS' + chr(92) + 'patch-enUS-3.MPQ",\n'
       '               "enUS' + chr(92) + 'patch-enUS-4.MPQ", "enUS' + chr(92) + 'patch-enUS-5.MPQ"]')
assert old in text, "anchor missing"
path.write_text(text.replace(old, new), encoding="utf-8")
print("patched")
