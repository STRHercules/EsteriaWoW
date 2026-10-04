import pathlib

path = pathlib.Path("fix_item_component_prefixes.py")
text = path.read_text(encoding="utf-8")

old = '''            total = 0
            missing = []
            for key in sorted(wanted.values()):
                _source, blob = read(storm, donor, key)
                if blob is None:
                    missing.append(key)
                    continue
                entries[key] = blob
                total += len(blob)
            staged = len(entries) - (1 if CHRRACES in entries else 0)
            print(f"   staging {staged} files, {total / 1048576:.1f} MB; "
                  f"absent from donor: {len(missing)}")
            for key in missing[:10]:
                print(f"      ! {key[len(HEAD):]}")
'''
new = '''            total = 0
            borrowed = []
            missing = []
            for key in sorted(wanted.values()):
                _source, blob = read(storm, donor, key)
                if blob is None:
                    # No dedicated model: borrow the same stem from a stock code so
                    # the helm still renders instead of drawing the missing-model cube.
                    for fallback in FALLBACK_CODES:
                        tail = key[len(HEAD):]
                        stem, _sep, rest = tail.rpartition("_")
                        borrowed_key = f"{HEAD}{stem}_{fallback}{rest}"
                        _source, blob = read(storm, ours, borrowed_key)
                        if blob is not None:
                            borrowed.append((key, borrowed_key))
                            break
                if blob is None:
                    missing.append(key)
                    continue
                entries[key] = blob
                total += len(blob)
            staged = len(entries) - (1 if CHRRACES in entries else 0)
            print(f"   staging {staged} files, {total / 1048576:.1f} MB; "
                  f"{len(borrowed)} borrowed from stock codes, {len(missing)} unavailable")
            for key, source_key in borrowed[:5]:
                print(f"      ~ {key[len(HEAD):]} <- {source_key[len(HEAD):]}")
            for key in missing[:10]:
                print(f"      ! {key[len(HEAD):]}")
'''
assert old in text
text = text.replace(old, new)
text = text.replace(
    'STAGE_CODES = ("Pa", "Vu")',
    'STAGE_CODES = ("Pa", "Vu")\nFALLBACK_CODES = ("Hu", "Ni", "Be", "Or", "Ta")')
path.write_text(text, encoding="utf-8")
print("rewritten")
