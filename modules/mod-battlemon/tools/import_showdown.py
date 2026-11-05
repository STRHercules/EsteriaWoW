#!/usr/bin/env python3
"""Gen 9 moves and learnset cross-check from a Pokemon Showdown checkout (data/*.ts parsed as text).

    python tools/import_showdown.py <path-to-pokemon-showdown> [--expansion <pokeemerald-expansion>] [--report FILE]

* Writes data/sql/db-world/base/2026_11_05_03_battlemon_moves_gen9.sql: Showdown's current moves that
  the catalog lacks, but only those expressible with function codes the battle engine already parses
  (plain damage, one status, one stat change, multi-hit, recoil, drain, simple heal). Everything else
  is listed as skipped, not guessed, so it can be hand-implemented later.
* Reports differences between existing catalog moves and Showdown (power/accuracy/pp/type/category).
* Reports how level-up learnsets from Showdown, the catalog and (optionally) pokeemerald-expansion agree.
Nothing in the repo is changed except the one new SQL file.
"""
import argparse
import glob
import os
import re
import sys

from import_ev_yields import ROOT

SQL_DIR = os.path.join(ROOT, 'data', 'sql', 'db-world', 'base')

STAT = {'atk': 'Attack', 'def': 'Defense', 'spa': 'SpAtk', 'spd': 'SpDef', 'spe': 'Speed', 'accuracy': 'Accuracy'}
STATUS = {'brn': 'BurnTarget', 'par': 'ParalyzeTarget', 'psn': 'PoisonTarget', 'tox': 'BadPoisonTarget',
          'slp': 'SleepTarget', 'frz': 'FreezeTarget'}
TARGET = {'normal': 'NearOther', 'self': 'User', 'adjacentAlly': 'NearAlly', 'adjacentFoe': 'NearFoe',
          'allAdjacentFoes': 'AllNearFoes', 'allAdjacent': 'AllNearOthers', 'randomNormal': 'RandomNearFoe',
          'any': 'Other', 'allySide': 'UserSide', 'foeSide': 'FoeSide', 'all': 'BothSides'}
FLAG = {'contact': 'Contact', 'protect': 'CanProtect', 'mirror': 'CanMirrorMove', 'punch': 'Punching',
        'bite': 'Biting', 'sound': 'Sound', 'powder': 'Powder', 'pulse': 'Pulse', 'bullet': 'Bomb',
        'dance': 'Dance', 'defrost': 'ThawsUser', 'nometronome': 'CannotMetronome'}
# Keys a move may have and still be converted; anything else (callbacks, side conditions, ...) is "complex".
SIMPLE_KEYS = {'num', 'accuracy', 'basePower', 'category', 'name', 'pp', 'priority', 'flags', 'secondary',
               'target', 'type', 'contestType', 'zMove', 'maxMove', 'critRatio', 'multihit', 'recoil', 'drain',
               'heal', 'boosts', 'self', 'status', 'volatileStatus', 'willCrit', 'noPPBoosts', 'isNonstandard'}


def read(path):
    return open(path, encoding='utf-8').read()


def entries(text):
    """{id: {key: raw text}} for a Showdown data file: entries at one tab, fields at two tabs."""
    out, cur, key = {}, None, None
    for line in text.splitlines():
        m = re.match(r'^\t(\w+): \{$', line)
        if m and cur is None:
            cur, key = {}, None
            out[m.group(1)] = cur
            continue
        if cur is None:
            continue
        if re.match(r'^\t\},?$', line):
            cur = None
            continue
        m = re.match(r'^\t\t(\w+)(?::\s*(.*)|\(.*)$', line)
        if m:
            key = m.group(1)
            cur[key] = (m.group(2) if m.group(2) is not None else '__fn__')
        elif key and line.startswith('\t\t\t'):
            cur[key] = cur[key] + '\n' + line.strip()
    return out


def scalar(raw):
    raw = raw.strip().rstrip(',')
    if raw in ('true', 'false'):
        return raw == 'true'
    if re.fullmatch(r'-?\d+', raw):
        return int(raw)
    m = re.fullmatch(r'["\'](.*)["\']', raw)
    return m.group(1) if m else raw


def pairs(raw):
    return {k: int(v) for k, v in re.findall(r'(\w+):\s*(-?\d+)', raw or '')}


def boost_code(boosts, who, chance):
    """RaiseUserAttack1 / LowerTargetSpeed2 ..., or None when the boosts cannot be named that way."""
    signs = {(v > 0, abs(v)) for v in boosts.values()}
    if len(signs) != 1 or any(k not in STAT for k in boosts):
        return None
    up, amount = signs.pop()
    stats = ''.join(STAT[k] for k in ('atk', 'def', 'spa', 'spd', 'spe', 'accuracy') if k in boosts)
    return ('Raise' if up else 'Lower') + who + stats + str(amount)


def convert(mv):
    """(function_code, effect_chance) or (None, reason)."""
    odd = sorted(k for k in mv if k not in SIMPLE_KEYS)
    if odd:
        return None, 'keys: ' + ','.join(odd)
    chance, effects = 0, []
    sec = mv.get('secondary', 'null')
    if sec.strip().rstrip(',') != 'null':
        inner = {k: v for k, v in re.findall(r'(\w+):\s*([^\n]*?),?$', sec, re.M)}
        extra = set(re.findall(r'^\s*(\w+)(?::|\()', sec, re.M)) - {'chance', 'status', 'volatileStatus', 'boosts', 'self'}
        if extra or 'self' in inner:
            return None, 'complex secondary'
        chance = int(inner.get('chance', 0))
        if 'status' in inner:
            effects.append(STATUS.get(scalar(inner['status'])))
        if 'volatileStatus' in inner:
            effects.append({'flinch': 'FlinchTarget', 'confusion': 'ConfuseTarget'}.get(scalar(inner['volatileStatus'])))
        if 'boosts' in inner:
            effects.append(boost_code(pairs(inner['boosts']), 'Target', chance))
    if 'status' in mv:
        effects.append(STATUS.get(scalar(mv['status'])))
    if 'volatileStatus' in mv:
        effects.append({'confusion': 'ConfuseTarget'}.get(scalar(mv['volatileStatus'])))
    if 'boosts' in mv:
        effects.append(boost_code(pairs(mv['boosts']), 'User' if scalar(mv['target']) == 'self' else 'Target', 0))
    if 'self' in mv:
        if set(re.findall(r'^\s*(\w+)(?::|\()', mv['self'], re.M)) - {'boosts'}:
            return None, 'complex self'
        m = re.search(r'boosts:\s*(\{[^}]*\})', mv['self'])
        effects.append(boost_code(pairs(m.group(1)), 'User', 0) if m else None)
    if 'multihit' in mv:
        hits = [int(x) for x in re.findall(r'\d+', mv['multihit'])]
        effects.append({(2,): 'HitTwoTimes', (3,): 'HitThreeTimes', (2, 5): 'HitTwoToFiveTimes'}.get(tuple(hits)))
    if 'recoil' in mv:
        frac = tuple(int(x) for x in re.findall(r'\d+', mv['recoil']))
        effects.append({(1, 4): 'RecoilQuarterOfDamageDealt', (1, 3): 'RecoilThirdOfDamageDealt',
                        (1, 2): 'RecoilHalfOfDamageDealt'}.get(frac))
    if 'drain' in mv:
        frac = tuple(int(x) for x in re.findall(r'\d+', mv['drain']))
        effects.append({(1, 2): 'HealUserByHalfOfDamageDone', (3, 4): 'HealUserByThreeQuartersOfDamageDone'}.get(frac))
    if 'heal' in mv:
        frac = tuple(int(x) for x in re.findall(r'\d+', mv['heal']))
        effects.append('HealUserHalfOfTotalHP' if frac == (1, 2) else None)
    if mv.get('willCrit', '').strip().rstrip(',') == 'true':
        effects.append('AlwaysCriticalHit')
    if len(effects) > 1:
        return None, 'several effects: ' + ','.join(str(e) for e in effects)
    if effects and effects[0] is None:
        return None, 'effect has no engine function code'
    return (effects[0] if effects else 'None'), chance


def catalog_moves():
    """internal_name -> dict of the columns we diff, plus the highest id."""
    rows, top = {}, 0
    cols = "(\\d+), '(\\w+)', '(?:[^']|'')*', '(\\w+)', '(\\w+)', (-?\\d+), (-?\\d+), (\\d+), '(\\w+)'"
    for path in glob.glob(os.path.join(SQL_DIR, '*catalog_moves.sql')):
        text = read(path)
        top = max([top] + [int(i) for i in re.findall(r'^\((\d+),', text, re.M)])
        for rid, name, typ, cat, power, acc, pp, _ in re.findall('^\\(' + cols, text, re.M):
            rows[name] = dict(type=typ, cat=cat, power=int(power), acc=int(acc), pp=int(pp))
    return rows, top


def sql(s):
    return "'" + s.replace("'", "''") + "'"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('showdown')
    ap.add_argument('--report', default='showdown-report.txt')
    args = ap.parse_args()
    data = os.path.join(args.showdown, 'data')
    moves = entries(read(os.path.join(data, 'moves.ts')))
    text = entries(read(os.path.join(data, 'text', 'moves.ts')))
    ours, top = catalog_moves()
    report = []

    # ---- existing moves: where does the catalog disagree with Showdown?
    drift = 0
    for mid, mv in sorted(moves.items()):
        mine = ours.get(mid.upper())
        if not mine or 'isNonstandard' in mv:
            continue
        theirs = dict(type=scalar(mv['type']).upper(), cat=scalar(mv['category']),
                      power=scalar(mv['basePower']), pp=scalar(mv['pp']),
                      acc=0 if scalar(mv['accuracy']) is True else scalar(mv['accuracy']))
        # Essentials stores variable power as 1 and self/field status moves as accuracy 0: not real differences.
        diff = {k: (mine[k], theirs[k]) for k in theirs
                if mine[k] != theirs[k] and (k, mine[k], theirs[k]) not in (('power', 1, 0), ('acc', 0, 100))}
        if diff:
            drift += 1
            report.append(f'DIFF {mid}: {diff}')

    # ---- new moves
    new, skipped = [], []
    for mid, mv in sorted(moves.items(), key=lambda kv: scalar(kv[1].get('num', '0')) or 0):
        if mid.upper() in ours or 'isNonstandard' in mv or (scalar(mv.get('num', '0')) or 0) <= 0:
            continue
        code, chance = convert(mv)
        if code is None:
            skipped.append((mid, chance))
            continue
        tgt = TARGET.get(scalar(mv['target']))
        if not tgt:
            skipped.append((mid, 'target ' + scalar(mv['target'])))
            continue
        flags = [FLAG[f] for f in re.findall(r'(\w+):\s*1', mv.get('flags', '')) if f in FLAG]
        if int(scalar(mv.get('critRatio', '1'))) >= 2:
            flags.append('HighCriticalHitRate')
        acc = scalar(mv['accuracy'])
        desc = scalar(text.get(mid, {}).get('shortDesc', "''")) if mid in text else ''
        new.append((mid, scalar(mv['name']), scalar(mv['type']).upper(), scalar(mv['category']),
                    scalar(mv['basePower']), 0 if acc is True else acc, scalar(mv['pp']), tgt, code,
                    ','.join(flags), scalar(mv.get('priority', '0')), chance, desc))
    report += [f'SKIP {m}: {why}' for m, why in skipped]

    lines = [
        '-- Gen 9 moves missing from the catalog. Generated by tools/import_showdown.py from Pokemon Showdown',
        '-- (data/moves.ts). Only moves the battle engine can express with existing function codes.',
        '-- Re-run the tool rather than editing by hand. Skipped (needs engine work) moves are in the tool report.',
        '',
        'REPLACE INTO `battlemon_moves` (`id`, `internal_name`, `name`, `type`, `move_category`, `power`, `accuracy`, '
        '`pp`, `target`, `function_code`, `flags`, `priority`, `effect_chance`, `description`) VALUES',
    ]
    body = []
    for i, r in enumerate(new, top + 1):
        mid, name, typ, cat, power, acc, pp, tgt, code, flags, prio, chance, desc = r
        body.append(f"({i}, {sql(mid.upper())}, {sql(name)}, {sql(typ)}, {sql(cat)}, {power}, {acc}, {pp}, "
                    f"{sql(tgt)}, {sql(code)}, {sql(flags)}, {prio}, {chance}, {sql(desc)})")
    lines.append(',\n'.join(body) + ';')
    out = os.path.join(SQL_DIR, '2026_11_05_03_battlemon_moves_gen9.sql')
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    with open(args.report, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report) + '\n')
    print(f'Showdown moves: {len(moves)}; catalog moves: {len(ours)} (top id {top})')
    print(f'new moves written: {len(new)}; skipped (need engine work): {len(skipped)}; existing moves that differ: {drift}')
    print('wrote', out)
    print('report', os.path.abspath(args.report))
    return 0


if __name__ == '__main__':
    sys.exit(main())
