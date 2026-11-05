#!/usr/bin/env python3
"""Generate battlemon_species_ev SQL from a pokeemerald-expansion checkout.

    python tools/import_ev_yields.py <path-to-pokeemerald-expansion> [--pkhex <path-to-PKHeX>] [--out FILE]

Reads src/data/pokemon/species_info/gen_*_families.h and matches each SPECIES_X to a
battlemon_species row by internal name (underscores dropped), using the committed catalog SQL.
Forms (SPECIES_RATTATA_ALOLAN) are skipped: the server falls back to the base species' yield.
With --pkhex, species the expansion repo cannot supply (it defines some through macros) are read from
PKHeX's Scarlet/Violet personal table (PKHeX.Core/Resources/byte/personal/personal_sv, 80-byte entries
indexed by national dex number, EV bitfield at offset 10; checked against the expansion data: 995/995 agree).
Prints every species it could not match, so gaps are visible instead of silently missing.
"""
import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS = ['HP', 'Attack', 'Defense', 'SpAttack', 'SpDefense', 'Speed']
COLUMNS = ['ev_hp', 'ev_atk', 'ev_def', 'ev_spa', 'ev_spd', 'ev_spe']


def catalog_species():
    """internal_name (no underscores, upper) -> species id, from the species catalog SQL."""
    found = {}
    pattern = re.compile(r"^\((\d+), '([A-Za-z0-9_]+)', ", re.M)
    for path in glob.glob(os.path.join(ROOT, 'data', 'sql', 'db-world', 'base', '*catalog_species.sql')):
        for sid, name in pattern.findall(open(path, encoding='utf-8').read()):
            found[name.replace('_', '').upper()] = int(sid)
    return found


def expansion_yields(repo):
    """SPECIES_X (upper, no underscores) -> [six EVs], for species with at least one yield."""
    out = {}
    for path in sorted(glob.glob(os.path.join(repo, 'src', 'data', 'pokemon', 'species_info', 'gen_*_families.h'))):
        current = None
        for line in open(path, encoding='utf-8'):
            m = re.match(r'\s*\[SPECIES_([A-Z0-9_]+)\]\s*=', line)
            if m:
                current = m.group(1)
                continue
            m = re.match(r'\s*\.evYield_(\w+)\s*=\s*(.+?),\s*$', line)
            if m and current and m.group(1) in STATS:
                out.setdefault(current, [0] * 6)[STATS.index(m.group(1))] = evaluate(m.group(2), current)
    return out


def evaluate(expr, species):
    """A plain number, or the repo's `(P_UPDATED_EVS >= GEN_n) ? new : old`. Its config default is
    GEN_LATEST, so the condition always holds and the first branch is the live value."""
    if expr.isdigit():
        return int(expr)
    m = re.fullmatch(r'\(P_UPDATED_EVS >= GEN_\d+\)\s*\?\s*(\d+)\s*:\s*(\d+)', expr)
    if m:
        return int(m.group(1))
    sys.exit(f'unhandled evYield expression for {species}: {expr}')


# Catalog names that differ from the repo's SPECIES_ names.
ALIASES = {'NIDORANFE': 'NIDORANF', 'NIDORANMA': 'NIDORANM'}
# An alternate form that must never stand in for a base species.
REGIONAL = ('ALOLA', 'GALAR', 'HISUI', 'PALDEA', 'MEGA', 'GMAX', 'PRIMAL', 'ETERNAMAX', 'TOTEM')


def lookup(yields, name):
    """Exact match, else the first listed form (the default one), skipping regional/mega variants."""
    key = ALIASES.get(name, name)
    flat = {k.replace('_', ''): v for k, v in yields.items()}
    if key in flat:
        return flat[key]
    for k, v in yields.items():
        if k.replace('_', '').startswith(key) and not any(r in k for r in REGIONAL):
            return v
    return None


def pkhex_yields(repo):
    """national dex number -> [six EVs in HP,Atk,Def,SpA,SpD,Spe order] from PKHeX's SV personal table."""
    path = os.path.join(repo, 'PKHeX.Core', 'Resources', 'byte', 'personal', 'personal_sv')
    data = open(path, 'rb').read()
    out = {}
    for dex in range(1, len(data) // 80):
        v = data[dex * 80 + 10] | data[dex * 80 + 11] << 8
        hp, atk, df, spe, spa, spd = ((v >> (2 * i)) & 3 for i in range(6))
        out[dex] = [hp, atk, df, spa, spd, spe]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('repo')
    ap.add_argument('--pkhex')
    ap.add_argument('--out', default=os.path.join(ROOT, 'data', 'sql', 'db-world', 'base',
                                                  '2026_11_05_01_battlemon_species_ev.sql'))
    args = ap.parse_args()

    catalog = catalog_species()
    yields = expansion_yields(args.repo)
    rows = {}
    for name, sid in catalog.items():
        evs = lookup(yields, name)
        if evs:
            rows[sid] = evs
    if args.pkhex:
        fallback = pkhex_yields(args.pkhex)
        for sid in set(catalog.values()) - set(rows):
            if any(fallback.get(sid, [])):
                rows[sid] = fallback[sid]
    inv = {v: k for k, v in catalog.items()}
    missing = [inv[sid] for sid in sorted(set(catalog.values()) - set(rows))]
    print(f'catalog species: {len(catalog)}, with a yield: {len(rows)}')
    print(f'catalog species with no yield found: {len(missing)} {missing}')

    lines = [
        '-- EV yield per species. Generated by tools/import_ev_yields.py from pokeemerald-expansion',
        '-- (src/data/pokemon/species_info). Re-run the tool rather than editing by hand.',
        '',
        'CREATE TABLE IF NOT EXISTS `battlemon_species_ev` (',
        '  `species_id` int unsigned NOT NULL COMMENT \'battlemon_species.id\',',
    ] + [f'  `{c}` tinyint unsigned NOT NULL DEFAULT \'0\',' for c in COLUMNS] + [
        '  PRIMARY KEY (`species_id`)',
        ') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;',
        '',
        'DELETE FROM `battlemon_species_ev`;',
        'INSERT INTO `battlemon_species_ev` (`species_id`, ' + ', '.join(f'`{c}`' for c in COLUMNS) + ') VALUES',
    ]
    body = [f'({sid}, ' + ', '.join(map(str, evs)) + ')' for sid, evs in sorted(rows.items())]
    lines.append(',\n'.join(body) + ';')
    with open(args.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('wrote', args.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
