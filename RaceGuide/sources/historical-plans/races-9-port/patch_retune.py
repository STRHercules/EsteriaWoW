import pathlib

path = pathlib.Path(".agents/plans/races-9-port/retune_vulpera_helm_calibration.py")
text = path.read_text(encoding="utf-8")
text = text.replace('BASE_STEM = "Helm_Leather_B_06"\nPREFIX = "Vu"',
                    'BASE_STEM = "Helm_Leather_B_06"\nPREFIX = "Vu"\n'
                    'VULPERA = {"M": "character\\\\vulpera\\\\male\\\\vulperamale.m2",\n'
                    '           "F": "character\\\\vulpera\\\\female\\\\vulperafemale.m2"}')
old = '''            low, high = skull_box(model)
            helm_low = struct.unpack_from("<3f", model, 0xA0)
            helm_high = struct.unpack_from("<3f", model, 0xAC)
            print(f"sex {sex}: skull x[{low[0]:+.3f},{high[0]:+.3f}] z[{low[2]:+.3f},{high[2]:+.3f}]")
            helm_low, helm_high = helm_box(model)'''
new = '''            _source, character = read(storm, handles, VULPERA[sex])
            if character is None:
                raise SystemExit(f"{VULPERA[sex]}: not found")
            low, high = skull_box(character)
            print(f"sex {sex}: skull x[{low[0]:+.3f},{high[0]:+.3f}] z[{low[2]:+.3f},{high[2]:+.3f}]")
            helm_low, helm_high = helm_box(model)'''
assert old in text
path.write_text(text.replace(old, new), encoding="utf-8")
print("patched")
