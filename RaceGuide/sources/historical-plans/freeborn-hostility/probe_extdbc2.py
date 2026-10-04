import re, pathlib
d = pathlib.Path(r'G:\3.3.5a - Dev\Extensions\wxl-extended-dbc\wxl-extended-dbc.dll').read_bytes()
strs = [s.decode('ascii','replace') for s in re.findall(rb'[\x20-\x7e]{4,}', d)]
print('total strings', len(strs))
# find table-name-ish strings: CamelCase, no spaces, 4-30 chars
cand = [s for s in strs if re.fullmatch(r'[A-Z][A-Za-z0-9_]{3,29}', s)]
print('--- CamelCase candidates (%d) ---' % len(cand))
seen = []
for s in cand:
    if s not in seen: seen.append(s)
print(', '.join(seen))
