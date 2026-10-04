import pathlib

path = pathlib.Path("fix_item_component_prefixes.py")
text = path.read_text(encoding="utf-8")
before = text
text = text.replace(
    '"Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ")',
    '"Patch-O.mpq", "PATCH-X.MPQ")')
text = text.replace(
    '    if b"(listfile)" in b"":\n        pass\n    storm.replace_archive_entries',
    '    storm.replace_archive_entries')
assert text != before, "no change applied"
path.write_text(text, encoding="utf-8")
print("patched")
