#!/usr/bin/env python3
"""Egg moves + level-up diff from a pokeemerald-expansion checkout.

    python tools/import_learnsets.py <path-to-pokeemerald-expansion> [--report FILE]

* Writes data/sql/db-world/base/2026_11_05_02_battlemon_egg_moves.sql (new table, safe to apply).
* Compares the repo's latest-generation level-up learnsets with the catalog's battlemon_species_moves and
  writes the differences to the report. With --levelup it also writes 2026_11_05_04_battlemon_levelup_moves.sql,
  which replaces the level-up rows of dex species (1-1025) that have data; custom species keep their rows.
Species matching and the form-fallback rule are shared with import_ev_yields.py.
"""
import argparse
import glob
import os
import re
import sys

from import_ev_yields import ROOT, catalog_species, lookup

SQL_DIR = os.path.join(ROOT, 'data', 'sql', 'db-world', 'base')
DATA = os.path.join('src', 'data', 'pokemon')


def read(path):
    return open(path, encoding='utf-8').read()


def species_learnsets(repo):
    """SPECIES_X -> (levelUpLearnset symbol, eggMoveLearnset symbol)."""
    out = {}
    for path in sorted(glob.glob(os.path.join(repo, DATA, 'species_info', 'gen_*_families.h'))):
        current = None
        for line in open(path, encoding='utf-8'):
            m = re.match(r'\s*\[SPECIES_([A-Z0-9_]+)\]\s*=', line)
            if m:
                current = m.group(1)
                out[current] = [None, None]
                continue
            m = re.match(r'\s*\.(levelUpLearnset|eggMoveLearnset)\s*=\s*(\w+),', line)
            if m and current:
                out[current][0 if m.group(1) == 'levelUpLearnset' else 1] = m.group(2)
    return {k: tuple(v) for k, v in out.items()}


def level_up(repo):
    """symbol -> [(level, MOVE)], from the latest generation's table (the repo's default config)."""
    out = {}
    text = read(os.path.join(repo, DATA, 'level_up_learnsets', 'gen_9.h'))
    for name, body in re.findall(r'static const struct LevelUpMove (\w+)\[\] = \{(.*?)LEVEL_UP_END', text, re.S):
        out[name] = [(int(lv), mv) for lv, mv in re.findall(r'LEVEL_UP_MOVE\(\s*(\d+),\s*MOVE_(\w+)\)', body)]
    return out


def egg_moves(repo):
    out = {}
    text = read(os.path.join(repo, DATA, 'egg_moves.h'))
    for name, body in re.findall(r'static const u16 (\w+)\[\] = \{(.*?)MOVE_UNAVAILABLE', text, re.S):
        out[name] = re.findall(r'MOVE_(\w+),', body)
    return out


def catalog_moves():
    names = set()
    for path in glob.glob(os.path.join(SQL_DIR, '*catalog_moves.sql')) + glob.glob(
            os.path.join(SQL_DIR, '*battlemon_moves_gen9.sql')):
        names |= set(re.findall(r"^\(\d+, '([A-Z0-9]+)', ", read(path), re.M))
    return names


def catalog_level_up():
    """species_id -> {(level, MOVE)}; later files replace earlier rows by id, as REPLACE INTO would."""
    rows = {}
    for path in sorted(glob.glob(os.path.join(SQL_DIR, '*catalog_species_moves.sql'))):
        for rid, sid, lv, mv in re.findall(r"^\((\d+), (\d+), (\d+), '(\w+)'\)", read(path), re.M):
            rows[int(rid)] = (int(sid), int(lv), mv)
    out = {}
    for sid, lv, mv in rows.values():
        out.setdefault(sid, set()).add((lv, mv))
    return out


def norm(move):
    return move.replace('_', '')


def batches(insert, rows, size=1000):
    """INSERT statements of at most `size` rows each, so no single statement outgrows max_allowed_packet."""
    return [insert + '\n' + ',\n'.join(rows[i:i + size]) + ';' for i in range(0, len(rows), size)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('repo')
    ap.add_argument('--report', default='learnset-diff.txt')
    ap.add_argument('--levelup', action='store_true')
    args = ap.parse_args()

    catalog = catalog_species()
    inv = {v: k for k, v in catalog.items()}
    moves = catalog_moves()
    by_species = species_learnsets(args.repo)
    lvl, egg = level_up(args.repo), egg_moves(args.repo)
    ours = catalog_level_up()

    egg_rows, unknown, report, levelup = [], set(), [], {}
    same = differ = nodata = 0
    for sid in sorted(inv):
        syms = lookup(by_species, inv[sid])
        if not syms:
            nodata += 1
            continue
        for mv in egg.get(syms[1], []):
            if norm(mv) in moves:
                egg_rows.append((sid, norm(mv)))
            else:
                unknown.add(mv)
        theirs = {(lv, norm(mv)) for lv, mv in lvl.get(syms[0], [])}
        unknown |= {mv for _, mv in lvl.get(syms[0], []) if norm(mv) not in moves}
        # Level order matters: the server reads rows by id and takes the last four known moves.
        known = sorted({(lv, norm(mv)) for lv, mv in lvl.get(syms[0], []) if norm(mv) in moves}, key=lambda x: x[0])
        ordered = [(lv, norm(mv)) for lv, mv in lvl.get(syms[0], []) if norm(mv) in moves]
        ordered = sorted(dict.fromkeys(ordered), key=lambda x: x[0])
        if ordered:
            levelup[sid] = [(max(lv, 1), mv) for lv, mv in ordered]
        mine = ours.get(sid, set())
        if theirs == mine:
            same += 1
            continue
        differ += 1
        report.append(f'{inv[sid]} (id {sid}): only in catalog {sorted(mine - theirs)} | only in expansion {sorted(theirs - mine)}')

    print(f'species: {len(inv)}  level-up identical: {same}  differ: {differ}  no expansion data: {nodata}')
    print(f'egg-move rows: {len(egg_rows)} across {len({s for s, _ in egg_rows})} species')
    print(f'moves in the repo that the catalog lacks ({len(unknown)}): {sorted(unknown)[:60]}')
    with open(args.report, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report) + '\n')
    print('level-up diff written to', os.path.abspath(args.report))

    lines = [
        '-- Egg moves per species. Generated by tools/import_learnsets.py from pokeemerald-expansion',
        '-- (src/data/pokemon/egg_moves.h). Re-run the tool rather than editing by hand.',
        '',
        'CREATE TABLE IF NOT EXISTS `battlemon_species_egg_moves` (',
        "  `species_id` int unsigned NOT NULL COMMENT 'battlemon_species.id',",
        "  `move_internal_name` varchar(64) NOT NULL COMMENT 'battlemon_moves.internal_name',",
        '  PRIMARY KEY (`species_id`, `move_internal_name`)',
        ') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;',
        '',
        # All or nothing: an interrupted run must not leave the table empty.
        'START TRANSACTION;',
        'DELETE FROM `battlemon_species_egg_moves`;',
        *batches('INSERT INTO `battlemon_species_egg_moves` (`species_id`, `move_internal_name`) VALUES',
                 [f"({s}, '{m}')" for s, m in sorted(set(egg_rows))]),
        'COMMIT;',
    ]
    if args.levelup:
        ids = ', '.join(str(s) for s in sorted(levelup))
        # Numbered after the whole list exists: the server reads rows in id order, so each row needs its own n.
        flat = [(sid, lv, mv) for sid in sorted(levelup) for lv, mv in levelup[sid]]
        body = [f"(@bm_base + {n}, {sid}, {lv}, '{mv}')" for n, (sid, lv, mv) in enumerate(flat, 1)]
        sqlup = [
            '-- Level-up moves for dex species, from pokeemerald-expansion (latest generation), cross-checked',
            '-- against Pokemon Showdown. Generated by tools/import_learnsets.py --levelup; do not edit by hand.',
            '-- Custom species (id > 1025) and species with no data keep their existing rows.',
            '',
            '-- One transaction: if anything fails nothing changes, so no species is left without level-up moves.',
            'START TRANSACTION;',
            f'DELETE FROM `battlemon_species_moves` WHERE `species_id` IN ({ids});',
            'SET @bm_base = (SELECT COALESCE(MAX(`id`), 0) FROM `battlemon_species_moves`);',
            *batches('INSERT INTO `battlemon_species_moves` (`id`, `species_id`, `level`, `move_internal_name`) VALUES',
                     body),
            'COMMIT;',
        ]
        path = os.path.join(SQL_DIR, '2026_11_05_04_battlemon_levelup_moves.sql')
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(sqlup) + '\n')
        print(f'wrote {path}: {len(body)} rows for {len(levelup)} species')
    out = os.path.join(SQL_DIR, '2026_11_05_02_battlemon_egg_moves.sql')
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('wrote', out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
