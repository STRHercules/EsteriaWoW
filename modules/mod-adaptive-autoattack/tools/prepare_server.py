#!/usr/bin/env python3
"""Read-only checks for hook-based Auto-Attack Forever; never edits core files."""
import argparse, subprocess
from pathlib import Path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core',required=True,type=Path)
    args=parser.parse_args()
    core=args.core.resolve()
    if Path(__file__).resolve().parents[1] != core/'modules/mod-adaptive-autoattack':
        parser.error('Install at CORE/modules/mod-adaptive-autoattack first.')
    if (core/'modules/mod-ranged-autoattack').exists():
        parser.error('Conflicting experimental module present.')
    for rel in ('Entities/Unit/Unit.cpp','Handlers/CombatHandler.cpp','Handlers/SpellHandler.cpp','Spells/Spell.cpp'):
        text=(core/'src/server/game'/rel).read_text()
        if any(s in text for s in ('RangedAutoStart','RangedAutoStop','RangedAutoUpdate','RangedAutoClientCancel')):
            parser.error('Old core integration in '+rel+'. Follow docs/UPGRADE-0.2.0.md.')
    for file,hook in (('ServerScript.h','CanPacketReceive'),('UnitScript.h','OnUnitUpdate')):
        if hook not in (core/'src/server/game/Scripting/ScriptDefines'/file).read_text():
            parser.error('Required hook missing: '+hook)
    revision=subprocess.check_output(['git','-C',str(core),'rev-parse','HEAD'],text=True).strip()
    print('PASS: hook names present; old integration symbols absent. No files changed.')
    print('Core revision: '+revision)
    print('Tested: e1823bb2db751a7cc0a90a8543e778449ebf7d84. Other revisions require validation.')
    print('Build, database ID checks and client installation remain. This is not a complete compatibility test.')
if __name__=='__main__':main()
