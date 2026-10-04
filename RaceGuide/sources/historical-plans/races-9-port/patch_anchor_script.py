import pathlib

path = pathlib.Path(".agents/plans/races-9-port/apply_vulpera_head_anchor.py")
text = path.read_text(encoding="utf-8")
old = '''                entries[f"{HEAD}HelmCal{label}_{PREFIX}{sex}.m2"] = shifted_vertices(
                    helm, ideal[0] + ddx - old[0], ideal[2] + ddz - old[2])'''
new = '''                # the anchor now carries the ideal, so the variants only need the delta
                entries[f"{HEAD}HelmCal{label}_{PREFIX}{sex}.m2"] = shifted_vertices(
                    helm, ddx, ddz)'''
assert old in text
path.write_text(text.replace(old, new), encoding="utf-8")
print("patched")
