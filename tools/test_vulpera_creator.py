"""Exercise exact race identity and all Vulpera creator controls using WoW's Lua 5.1 runtime."""

from lupa.lua51 import LuaRuntime
import vulpera_race_pack as v


def check(text, info):
    lua = LuaRuntime(unpack_returned_tuples=True)
    compiled = lua.eval("function(s) local f,e=loadstring(s); assert(f,e); return true; end")
    assert compiled(text) and compiled(info)
    identity = info[info.index("local EXACT_RACE_DATA = {"):info.index("local ALLIANCE_RACES = ")]
    lookup = lua.execute("strupper=string.upper;\n" + identity + "\nreturn GetExactRaceIDForFileString;")
    assert lookup("Vulpera") == 20 and lookup("VULPERA") == 20
    for token, race in (("HighmountainTauren", 46), ("Earthen", 48), ("Haranir", 50)):
        assert lookup(token) == race
    lua.execute('''
CharacterCreate={}; CHAR_CUSTOMIZATION1_DESC="Skin Color"; CHAR_CUSTOMIZATION2_DESC="Face";
function widget()
    local w={shown=true};
    function w:GetParent() return self; end
    function w:ClearAllPoints() end
    function w:SetPoint(...) end
    function w:SetID(id) self.id=id; end
    function w:IsShown() return self.shown; end
    function w:Show() self.shown=true; end
    function w:Hide() self.shown=false; end
    function w:SetText(text) self.text=text; end
    function w:SetScript(...) end
    return w;
end
CharacterCreateFrame=widget();
for i=1,29 do
    _G["CharacterCustomizationButtonFrame"..i]=widget();
    _G["CharacterCustomizationButtonFrame"..i.."Text"]=widget();
end
function CreateFrame() return widget(); end
function CharacterCustomization_Left(id) clicked={id,-1}; end
function CharacterCustomization_Right(id) clicked={id,1}; end
function CharacterCreate_UpdateHairCustomization()
    CharacterCustomizationButtonFrame3Text:SetText("Hair Style");
    CharacterCustomizationButtonFrame4Text:SetText("Hair Color");
    CharacterCustomizationButtonFrame5Text:SetText("Piercings");
end
function CycleCharCustomization(command,index,delta)
    if command=="EA_GET" then
        local option=options[index];
        if option then
            local count=option.count;
            if index==10 and not supportedEyes then count=1; end
            return 0,count,option.label;
        end
        return 0,0,"";
    end
    clicked={command,index,delta};
end
''')
    native = text[text.index("-- Esteria native appearance controls:"):
                  text.index("-- Esteria customization dropdown:")]
    lua.execute(native)
    for sex, profile in v.audit().items():
        options = lua.table_from([lua.table_from({"label": o["label"], "count": len(o["choices"])})
                                  for o in profile["options"]])
        lua.globals().options = options
        lua.globals().supportedEyes = True
        # Without exact metadata, the legacy Vulpera button supplies its list ordinal17 rather than race20.
        lua.globals().CharacterCreate.selectedRaceID = lookup("Vulpera") or 17
        lua.globals().CharacterCreate_UpdateHairCustomization()
        expected = [o["label"] for o in profile["options"] if len(o["choices"]) > 1]
        visible = []
        for index, option in enumerate(profile["options"], 1):
            frame = lua.globals()["CharacterCustomizationButtonFrame" + str(index)]
            if frame.shown:
                label = lua.globals()["CharacterCustomizationButtonFrame" + str(index) + "Text"].text
                assert label.startswith(option["label"]), (sex, index, label)
                visible.append(option["label"])
        assert visible == expected and len(visible) == 9, (sex, visible)
        lua.globals().CharacterCustomization_Right(10)
        assert list(lua.globals().clicked.values()) == ["EA_CYCLE", 10, 1]
        lua.globals().supportedEyes = False
        lua.globals().CharacterCreate_UpdateHairCustomization()
        assert not lua.globals().CharacterCustomizationButtonFrame10.shown
        lua.globals().CharacterCreate.selectedRaceID = 11
        lua.globals().CharacterCreate_UpdateHairCustomization()
        for index in range(6, 30):
            assert not lua.globals()["CharacterCustomizationButtonFrame" + str(index)].shown
        assert lua.globals().CharacterCustomizationButtonFrame1Text.text == "Skin Color"
    return "PASS: legacy Vulpera ordinal17 resolves race20; both genders show all nine controls and restore stock UI"


if __name__ == "__main__":
    updates = v.glue()
    print(check(updates[v.p.GLUE_ROOT + "CharacterCreate.lua"].decode(),
                updates[v.p.GLUE_ROOT + "CharacterInfo.lua"].decode()))
