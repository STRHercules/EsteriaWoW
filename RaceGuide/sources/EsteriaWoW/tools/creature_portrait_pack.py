"""Install the seven supplied NPC-race portraits and hide redundant single-gender creator buttons."""

import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
from datetime import datetime

from PIL import Image, ImageDraw
from luaparser import ast
from lupa.lua51 import LuaRuntime

import creature_race_pack as c
import race_portrait_pack as portraits

STAGE = c.STAGE / 'portraits'
SOURCE = portraits.DEFAULT_SOURCE
ART = (
    (58, 'ThinHuman', 'Male', 'Alliance/Charactercreate-races_thinhuman-male_alliance.png'),
    (55, 'Tuskarr', 'Male', 'Alliance/Charactercreate-races_tuskarr-male.png'),
    (56, 'Vrykul', 'Male', 'Alliance/Charactercreate-races_vrykul-male_alliance.png'),
    (57, 'VrykulHorde', 'Male', 'Horde/Charactercreate-races_vrykul-male_horde.png'),
    (54, 'NagaHorde', 'Female', 'Horde/Charactercreate-races_naga-female.png'),
    (54, 'NagaHorde', 'Male', 'Horde/Charactercreate-races_naga-male.png'),
    (59, 'ThinHumanHorde', 'Male', 'Horde/Charactercreate-races_thinhuman-male_horde.png'),
)


def patch_creator(text):
    for _, token, sex, _ in ART:
        pattern = r'(\["' + token.upper() + '_' + sex.upper() + r'"\]\s*=\s*)"[^"]+"'
        target = 'Interface\\\\Glues\\\\CharacterCreate\\\\UI-CharacterCreate-' + token + sex
        text, count = re.subn(pattern, lambda match: match[1] + '"' + target + '"', text)
        if count != 1:
            raise ValueError('Creator portrait key is missing or ambiguous: ' + token + sex)
    old = '''    if maleOnly then
        CharacterCreateGenderButtonFemale:Hide();
        if GetSelectedSex() ~= SEX_MALE then SetCharacterGender(SEX_MALE); end
    else
        CharacterCreateGenderButtonFemale:Show();
    end'''
    new = old.replace('        CharacterCreateGenderButtonFemale:Hide();',
        '        CharacterCreateGenderButtonMale:Hide();\n        CharacterCreateGenderButtonFemale:Hide();')
    new = new.replace('        CharacterCreateGenderButtonFemale:Show();',
        '        CharacterCreateGenderButtonMale:Show();\n        CharacterCreateGenderButtonFemale:Show();')
    if new not in text:
        if text.count(old) != 1:
            raise ValueError('Single-gender race wrapper changed')
        text = text.replace(old, new, 1)
    for race, token, sex, _ in ART:
        if sex != 'Male' or not 55 <= race <= 59:
            continue
        key = token.upper() + '_FEMALE'
        if '["' + key + '"]' not in text:
            row = '    ["' + key + '"] = "Interface\\\\Glues\\\\CharacterCreate\\\\'
            row += 'UI-CharacterCreate-' + token + 'Male",'
            text = text.replace('RACE_ICON_TEXTURES = {', 'RACE_ICON_TEXTURES = {\n' + row, 1)
    return patch_model_update(text, False)


def patch_model_update(text, selected):
    marker = '-- Esteria Vrykul preview sizing.'
    if marker in text:
        if selected:
            text = text.replace('    local index = GetSelectedCharacter();',
                                '    local index = self.selectedIndex or 0;', 1)
        return text
    function = 'CharacterSelect_UpdateModel' if selected else 'CharacterCreate_UpdateModel'
    index = 'self.selectedIndex or 0' if selected else '0'
    guard = 'index and index > 0' if selected else 'index == 0'
    text += ('\n' + marker + '\nlocal creaturePreviewUpdate = ' + function + ';\n'
        'function ' + function + '(self)\n    creaturePreviewUpdate(self);\n'
        '    local index = ' + index + ';\n'
        '    if ' + guard + ' and type(CycleCharCustomization) == "function" then\n'
        '        CycleCharCustomization("EA_PREVIEW_SCALE", index);\n    end\nend\n')
    return text


def patch_schema(text):
    identities = {race: token for race, token, _, _ in ART}
    for race, token in identities.items():
        pattern = r'(\[' + str(race) + r'\]\s*=\s*\{[^\n]*artKey\s*=\s*)"[^"]+"'
        text, count = re.subn(pattern, lambda match: match[1] + '"' + token + '"', text)
        if count != 1:
            raise ValueError('Character-select race override changed: ' + str(race))
    model_rows = '\n'.join('    { "' + token.upper() + '", { name = "' + c.SPECS[slug]['name']
        + '", faction = ' + str(1 if faction == 'alliance' else 2) + ', artKey = "' + token + '" } },'
        for slug in c.SPECS for faction in reversed(c.SPECS[slug]['factions'])
        for token in (c.token(slug, faction),))
    if model_rows not in text:
        text = text.replace('S.RaceByModelKey = {', 'S.RaceByModelKey = {\n' + model_rows, 1)
    keys = ', '.join(token + '=true' for token in identities.values())
    if keys not in text:
        text = text.replace('S.PortraitArtKeys = {', 'S.PortraitArtKeys = {\n    ' + keys + ',', 1)
    return text


def check_lua(creator, schema, integrate, selected=None):
    lua = LuaRuntime(unpack_returned_tuples=True)
    compile_lua = lua.eval('function(s) local f,e=loadstring(s); assert(f,e); return true; end')
    for text in (creator, schema, integrate, *(tuple([selected]) if selected else ())):
        ast.parse(text)
        assert compile_lua(text)
    lua.execute('''
SEX_MALE=2; SEX_FEMALE=3; currentSex=SEX_FEMALE;
CharacterCreate={};
function widget()
    return {visible=true, Hide=function(self) self.visible=false end,
            Show=function(self) self.visible=true end};
end
CharacterCreateGenderButtonMale=widget(); CharacterCreateGenderButtonFemale=widget();
function GetSelectedSex() return currentSex; end
function SetCharacterRace(race) CharacterCreate.selectedRaceID=race; end
function SetCharacterGender(sex) currentSex=sex; SetCharacterRace(CharacterCreate.selectedRaceID); end
function CharacterCreate_UpdateModel(self) modelAdvanced=true; end
function CharacterSelect_UpdateModel(self) modelAdvanced=true; end
GetSelectedCharacter=nil;
function CycleCharCustomization(command, index)
    assert(modelAdvanced and command=="EA_PREVIEW_SCALE");
    previewIndex=index;
end
''')
    lua.execute(creator[creator.index('-- Only Naga has an authored second playable body type'):])
    for race in (54, 55, 54, 56, 57, 58, 59, 54, 1):
        lua.globals().SetCharacterRace(race)
        male = lua.globals().CharacterCreateGenderButtonMale.visible
        female = lua.globals().CharacterCreateGenderButtonFemale.visible
        assert (male, female) == ((False, False) if 55 <= race <= 59 else (True, True)), race
        if 55 <= race <= 59:
            assert lua.globals().currentSex == 2
    lua.globals().CharacterCreate_UpdateModel(lua.table())
    assert lua.globals().previewIndex == 0
    if selected:
        lua.execute(selected[selected.index('-- Esteria Vrykul preview sizing.'):])
        lua.globals().CharacterSelect_UpdateModel(lua.table(selectedIndex=2, scrollOffset=1))
        assert lua.globals().previewIndex == 2
        lua.globals().previewIndex = -1
        lua.globals().CharacterSelect_UpdateModel(lua.table(selectedIndex=0))
        assert lua.globals().previewIndex == -1
    for race, token, sex, _ in ART:
        if sex == 'Male' and 55 <= race <= 59:
            assert '["' + token.upper() + '_FEMALE"]' in creator
    # Click the actual race handler from a female race, with button ordinals distinct from real race IDs.
    lua.execute('''
selectedOrdinal=1;
function GetSelectedRace() return selectedOrdinal; end
function SetSelectedSex(sex) currentSex=sex; end
function SetSelectedRace(id) assert(currentSex==SEX_MALE); selectedOrdinal=id; end
function SetCharacterRace(id)
    local button=_G["CharacterCreateRaceButton"..id];
    CharacterCreate.selectedRaceID=button and button.raceID or id;
end
function PlaySound() end
function SetCharacterCreateFacing() end
function CharacterCreateEnumerateClasses() end
function GetAvailableClasses() return 1; end
function GetSelectedClass() return nil,nil,1; end
function SetCharacterClass() end
function CharacterCreate_UpdateHairCustomization() end
function CharacterChangeFixup() end
function CharacterCreate_UpdateButtonCheckedStates() end
''')
    click = creator[creator.index('function CharacterRace_OnClick(self, id)'):
                    creator.index('function SetCharacterGender(sex)')]
    lua.execute(click)
    for ordinal, race in enumerate((55, 56, 57, 58, 59), 13):
        lua.globals().currentSex = 3
        lua.globals().selectedOrdinal = 1
        button = lua.table(raceID=race)
        button.GetChecked = lua.eval('function() return true end')
        lua.globals()['CharacterCreateRaceButton' + str(ordinal)] = button
        lua.globals().CharacterRace_OnClick(button, ordinal)
        assert lua.globals().currentSex == 2 and lua.globals().CharacterCreate.selectedRaceID == race
    lua.execute('ECS={Const={FALLBACK_RACE_NAME="Unknown",TEX={portraitNs="ECS-Portrait-",create="Create-"}}};')
    lua.execute(schema)
    for race, token, sex, _ in ART:
        actual = lua.globals().ECS.Schema.GetRace(race, token, None, None)
        assert actual.artKey == token
        resolved = lua.globals().ECS.Schema.GetRace(None, token, None, None)
        assert resolved.artKey == token
        assert lua.globals().ECS.Schema.GetPortrait(token, 1 if sex == 'Female' else 0) == \
            'ECS-Portrait-' + token + sex


def stage():
    files = c.p.ClientFiles(str(c.p.CLIENT_DEFAULT / 'Data'), 'enUS')
    try:
        template = files.find(portraits.ICON_TEMPLATE_ENTRY)[0]
        ring = portraits.ring_layer(portraits.decode_client_blp(files.find(portraits.RING_ENTRY)[0]))
        select_border = portraits.decode_client_blp(files.find(
            'Interface\\Glues\\CharacterSelect\\ECS-Portrait-Border.blp')[0])
        creator = patch_creator(files.find(c.p.GLUE_ROOT + 'CharacterCreate.lua')[0].decode())
        selected = patch_model_update(files.find(c.p.GLUE_ROOT + 'CharacterSelect.lua')[0].decode(), True)
        schema = patch_schema(files.find(c.p.GLUE_ROOT + 'ECS_Schema.lua')[0].decode())
        integrate = files.find(c.p.GLUE_ROOT + 'ECS_Integrate.lua')[0].decode()
        old = 'or race == 52 or race == 53)'
        new = 'or race == 52 or race == 53 or (race >= 54 and race <= 59))'
        if new not in integrate and integrate.count(old) != 1:
            raise ValueError('Character-select identity hook changed')
        if new not in integrate:
            integrate = integrate.replace(old, new, 1)
    finally:
        files.close()
    check_lua(creator, schema, integrate, selected)
    updates = {c.p.GLUE_ROOT + n: text.encode() for n, text in
               (('CharacterCreate.lua', creator), ('CharacterSelect.lua', selected),
                ('ECS_Schema.lua', schema), ('ECS_Integrate.lua', integrate))}
    report = {'status': 'portraits_staged', 'source_images': {}, 'source_hashes': {}, 'stage_hashes': {},
              'checks': ['Lua5.1 compile', 'single-gender race transitions', 'all race/faction art keys'],
              'preserved_exe_sha256': c.p.sha256(c.p.CLIENT_DEFAULT / 'Wow.exe')}
    preview = Image.new('RGB', (len(ART) * 160, 334), (27, 27, 27))
    draw = ImageDraw.Draw(preview)
    for index, (race, token, sex, source) in enumerate(ART):
        image = SOURCE / source
        report['source_images'][str(image)] = c.p.sha256(image)
        pixels = portraits.portrait_bytes(image, portraits.circular_mask())
        bordered = portraits.compose_race_icon(pixels, ring)
        plain = c.p.encode_portrait(pixels, template)
        for folder, stem, data in (('Glues\\CharacterCreate', f'UI-CharacterCreate-{token}{sex}',
                                   c.p.encode_portrait(bordered, template)),
                                  ('Glues\\CharacterSelect', f'ECS-Portrait-{token}{sex}', plain),
                                  ('CharacterFrame', f'TemporaryPortrait-{sex}-{token}', plain)):
            key = f'Interface\\{folder}\\{stem}.blp'
            c.p.validate_portrait(data, Path(key))
            updates[key] = data
            if 55 <= race <= 59 and sex == 'Male':
                if folder == 'CharacterFrame':
                    alias = f'Interface\\{folder}\\TemporaryPortrait-Female-{token}.blp'
                else:
                    alias = f'Interface\\{folder}\\' + stem[:-4] + 'Female.blp'
                updates[alias] = data
        preview.paste(bordered.resize((128, 128), Image.Resampling.NEAREST), (index * 160 + 16, 10),
                      bordered.resize((128, 128), Image.Resampling.NEAREST))
        selected = Image.new('RGBA', (128, 128))
        selected.alpha_composite(pixels.resize((98, 98), Image.Resampling.LANCZOS), (15, 15))
        selected.alpha_composite(select_border.resize((128, 128), Image.Resampling.LANCZOS))
        preview.paste(selected, (index * 160 + 16, 165), selected)
        draw.text((index * 160 + 5, 141), token + ' ' + sex, fill='white')
        draw.text((index * 160 + 5, 302), 'Character Select', fill='white')
    STAGE.mkdir(parents=True, exist_ok=True)
    preview.save(STAGE / 'portrait-preview.png')
    (STAGE / 'glue').mkdir(exist_ok=True)
    for key, data in updates.items():
        if key.endswith('.lua'):
            (STAGE / 'glue' / c.PureWindowsPath(key).name).write_bytes(data)
    storm = c.p.Storm(c.p.DLL_DEFAULT)
    for relative in (c.p.GLOBAL_ARCHIVE_REL, c.p.LOCALE_ARCHIVE_REL):
        live = c.p.CLIENT_DEFAULT / relative
        target = STAGE / 'pack' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        report['source_hashes'][str(relative)] = c.p.sha256(live)
        shutil.copy2(live, target)
        assert c.p.sha256(target) == report['source_hashes'][str(relative)]
        storm.replace_archive_entries(target, updates)
        if target.stat().st_size >= 0x80000000:
            compacted = target.with_suffix('.compressed')
            c.p.rebuild_archive_streaming(storm, target, compacted, compress=True)
            os.replace(compacted, target)
        assert target.stat().st_size < 0x80000000
        archive = storm.open_archive(target)
        try:
            for key, data in updates.items():
                assert storm.read(archive, key) == data, key
        finally:
            storm.dll.SFileCloseArchive(archive)
        report['stage_hashes'][str(relative)] = c.p.sha256(target)
        print('PORTRAITS STAGED', relative, flush=True)
    report['entries'] = {n: hashlib.sha256(data).hexdigest() for n, data in updates.items()}
    helper = STAGE / 'EsteriaAppearance.dll'
    report['helper_before_sha256'] = c.p.sha256(c.p.CLIENT_DEFAULT / helper.name)
    report['helper_stage_sha256'] = c.p.sha256(helper)
    report['checks'].extend(['female portrait clicks choose male bodies', 'Vrykul create/select placement scale'])
    c.save(STAGE / 'build-report.json', report)


def install():
    report = c.p.load_json(STAGE / 'build-report.json')
    processes = subprocess.check_output(['tasklist', '/FO', 'CSV', '/NH'], text=True).lower()
    if any(n in processes for n in ('wow.exe', 'eclipse.exe', 'mpqeditor.exe')):
        raise RuntimeError('Close WoW/Eclipse/MPQEditor before installing the checked portraits')
    backup = Path(r'C:\Users\Zach\.codex\backups') / ('creature-portraits-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(parents=True, exist_ok=False)
    for source, digest in report['source_images'].items():
        assert c.p.sha256(Path(source)) == digest
    helper = c.p.CLIENT_DEFAULT / 'EsteriaAppearance.dll'
    assert c.p.sha256(helper) == report['helper_before_sha256']
    assert c.p.sha256(STAGE / helper.name) == report['helper_stage_sha256']
    shutil.copy2(helper, backup / helper.name)
    assert c.p.sha256(backup / helper.name) == report['helper_before_sha256']
    for relative, before in report['source_hashes'].items():
        live = c.p.CLIENT_DEFAULT / relative
        target = backup / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        assert c.p.sha256(live) == before
        assert c.p.sha256(STAGE / 'pack' / relative) == report['stage_hashes'][relative]
        shutil.copy2(live, target)
        assert c.p.sha256(target) == before
    try:
        for relative in report['stage_hashes']:
            live = c.p.CLIENT_DEFAULT / relative
            temporary = live.with_suffix(live.suffix + '.portrait-next')
            shutil.copy2(STAGE / 'pack' / relative, temporary)
            assert c.p.sha256(temporary) == report['stage_hashes'][relative]
            os.replace(temporary, live)
        temporary = helper.with_suffix('.portrait-next')
        shutil.copy2(STAGE / helper.name, temporary)
        assert c.p.sha256(temporary) == report['helper_stage_sha256']
        os.replace(temporary, helper)
    except Exception:
        for relative in report['source_hashes']:
            shutil.copy2(backup / relative, c.p.CLIENT_DEFAULT / relative)
        shutil.copy2(backup / helper.name, helper)
        raise
    assert c.p.sha256(c.p.CLIENT_DEFAULT / 'Wow.exe') == report['preserved_exe_sha256']
    report.update(backup=str(backup), status='portraits_installed_awaiting_fresh_client',
                  installed_hashes={n: c.p.sha256(c.p.CLIENT_DEFAULT / n)
                                    for n in (*report['stage_hashes'], helper.name)})
    c.save(STAGE / 'last-install.json', report)
    c.save(backup / 'install-report.json', report)
    print('PORTRAITS INSTALLED', len(ART), 'images;', backup, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('stage', 'install'))
    (stage if parser.parse_args().action == 'stage' else install)()
