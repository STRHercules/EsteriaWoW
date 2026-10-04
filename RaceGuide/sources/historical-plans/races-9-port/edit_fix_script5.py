import pathlib

path = pathlib.Path("fix_item_component_prefixes.py")
text = path.read_text(encoding="utf-8")
old = '''                        tail = key[len(HEAD):]
                        stem, _sep, rest = tail.rpartition("_")
                        borrowed_key = f"{HEAD}{stem}_{fallback}{rest}"'''
new = '''                        tail = key[len(HEAD):]
                        stem, _sep, rest = tail.rpartition("_")
                        borrowed_key = f"{HEAD}{stem}_{fallback}{rest[2:]}"'''
assert old in text
path.write_text(text.replace(old, new), encoding="utf-8")
print("patched")
