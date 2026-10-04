"""Check the installed Forgotten names: python tools/test_forgotten_race_name.py."""

import argparse
from pathlib import Path

from lupa.lua51 import LuaRuntime
from luaparser import ast

import creature_race_pack as c

NAME_FIELDS = (*range(14, 30), *range(31, 47), *range(48, 64))
FILES = ('CharacterInfo.lua', 'GlueStrings.lua', 'ECS_Schema.lua')


def check_races(data):
    table = c.p.RawWdbc(data)
    rows = {c.p._value(row, 0): row for row in table.records}
    for race, token in ((58, 'ThinHuman'), (59, 'ThinHumanHorde')):
        row = rows[race]
        assert c.p._string(table.strings, c.p._value(row, 44)).decode() == token
        assert c.p._value(row, 16) == 60052
        assert c.p._value(row, 52) == (race == 59)
        for field in NAME_FIELDS:
            assert c.p._string(table.strings, c.p._value(row, field * 4)) == b'Forgotten', (race, field)
    assert c.p._string(table.strings, c.p._value(rows[1], 56)) == b'Human'


def check_glue(entries):
    lua = LuaRuntime()
    lua.execute('''
strupper=string.upper; strlower=string.lower;
function GetLocale() return "enUS"; end
function GetSelectedRace() return 1; end
function GetSelectedSex() return 2; end
function GetFactionForRace() return "Alliance","Alliance"; end
ECS={Const={FALLBACK_RACE_NAME="Unknown", TEX={}}};
''')
    for name in ('GlueStrings.lua', 'CharacterInfo.lua', 'ECS_Schema.lua'):
        text = entries[name].decode('utf-8-sig')
        ast.parse(text)
        lua.execute(text)
    lua.execute('''
for _, token in ipairs({"THINHUMAN", "THINHUMANHORDE"}) do
    assert(_G[token] == "Forgotten");
    assert(_G[token.."_MALE"] == "Forgotten" and _G[token.."_FEMALE"] == "Forgotten");
    local info = RaceInfoByFileString[token];
    assert(info.Name == "Forgotten");
    assert(not info.Description:lower():find("human", 1, true));
    for _, value in pairs(info) do
        if type(value) == "table" and value.name then
            assert(not value.name:lower():find("human", 1, true));
        end
    end
end
assert(RaceInfoByFileString.HUMAN.Name == "Human");
assert(RaceInfoByFileString.HUMAN.Spell_4.name == "The Human Spirit");
for _, row in ipairs({{58,"ThinHuman",1},{59,"ThinHumanHorde",2}}) do
    local direct = ECS.Schema.GetRace(row[1], row[2]);
    local fallback = ECS.Schema.GetRace(nil, row[2]);
    assert(direct.name == "Forgotten" and fallback.name == "Forgotten");
    assert(direct.faction == row[3] and fallback.faction == row[3]);
    assert(direct.artKey == row[2] and fallback.artKey == row[2]);
end
''')


def check(client=c.p.CLIENT_DEFAULT, server=c.p.SERVER_DBC_ROOT / 'ChrRaces.dbc'):
    assert c.SPECS['thinhuman']['name'] == 'Forgotten'
    manifest = c.p.load_manifest('thinhuman')
    assert manifest['name'] == 'Forgotten' and manifest['race_ids'] == [58, 59]
    registry = c.p.load_json(c.p.ROOT / 'modules/mod-custom-server/data/races/race_registry.json')
    assert [(row['id'], row['display_name']) for row in registry['playable']
            if row['species_key'] == 'thinhuman'] == [(58, 'Forgotten'), (59, 'Forgotten')]
    storm = c.p.Storm(c.p.DLL_DEFAULT)
    for relative in (c.p.GLOBAL_ARCHIVE_REL, c.p.LOCALE_ARCHIVE_REL):
        check_races(c.p._read_archive_entry(storm, client / relative, c.p.DBC_ROOT + 'ChrRaces.dbc'))
        check_glue({name: c.p._read_archive_entry(storm, client / relative, c.p.GLUE_ROOT + name)
                    for name in FILES})
    with c.p.ClientFiles(str(client / 'Data'), 'enUS') as files:
        check_races(files.find(c.p.DBC_ROOT + 'ChrRaces.dbc')[0])
        check_glue({name: files.find(c.p.GLUE_ROOT + name)[0] for name in FILES})
    check_races(server.read_bytes())
    print('PASS: Forgotten native names, creator tooltips, select ID/model fallbacks, '
          'both factions and gender labels; stock Human and internal tokens preserved.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--client', type=Path, default=c.p.CLIENT_DEFAULT)
    parser.add_argument('--server', type=Path, default=c.p.SERVER_DBC_ROOT / 'ChrRaces.dbc')
    args = parser.parse_args()
    check(args.client, args.server)
