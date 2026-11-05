"""Read the committed species catalog SQL, for tests that check rules against the real data."""
import glob
import os
import re

SQL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'sql', 'db-world', 'base')


def parse_row(line):
    """One SQL VALUES tuple -> list of strings (NULL stays 'NULL'); handles quotes and '' escapes."""
    vals, i, n = [], 1, len(line)
    while i < n:
        if line[i] == "'":
            j, buf = i + 1, []
            while True:
                if line[j] == "'":
                    if j + 1 < n and line[j + 1] == "'":
                        buf.append("'")
                        j += 2
                        continue
                    break
                buf.append(line[j])
                j += 1
            vals.append(''.join(buf))
            i = j + 1
        else:
            j = i
            while j < n and line[j] not in ',)':
                j += 1
            vals.append(line[i:j].strip())
            i = j
        while i < n and line[i] in ', ':
            i += 1
        if i < n and line[i] == ')':
            break
    return vals


def load_species():
    """id -> dict of the columns tests use; a later file replaces an earlier row, as REPLACE INTO would."""
    out = {}
    for path in sorted(glob.glob(os.path.join(SQL, '*catalog_species.sql'))):
        for line in open(path, encoding='utf-8'):
            if re.match(r"\(\d+, '", line):
                v = parse_row(line.strip())
                nul = lambda x: '' if x == 'NULL' else x
                out[int(v[0])] = dict(internal=v[1], name=v[2], type1=v[3], type2=nul(v[4]), gender=v[11],
                                      catch=int(v[14]), egg_groups=nul(v[19]), hatch=None if v[20] == 'NULL' else int(v[20]), evolutions=nul(v[29]))
    return out


def evolution_links(species):
    """target species id -> (the species it evolves from, evolution level or 0 when not level-based)."""
    by_name = {s['internal']: sid for sid, s in species.items()}
    links = {}
    for sid, s in species.items():
        parts = s['evolutions'].split(',') if s['evolutions'] else []
        for i in range(0, len(parts) - 2, 3):
            if parts[i] in by_name:
                level = int(parts[i + 2]) if parts[i + 1].startswith('Level') and parts[i + 2].isdigit() else 0
                links.setdefault(by_name[parts[i]], (sid, level))
    return links


def base_species(sid, links):
    for _ in range(8):
        if sid not in links:
            break
        sid = links[sid][0]
    return sid
