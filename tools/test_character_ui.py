"""Run the actual patched Lua against small Glue/native fixtures, without launching WoW."""

from lupa.lua51 import LuaRuntime
from luaparser import ast
from xml.etree import ElementTree
import character_ui_pack as pack


def check_creator(text):
    lua = LuaRuntime()
    lua.execute('''
CharacterCreate={selectedRaceID=50};
CHAR_CUSTOMIZATION1_DESC="Skin Color"; CHAR_CUSTOMIZATION2_DESC="Face";
function widget(name, parent)
    local w={name=name, parent=parent, shown=true, value=0, scripts={}};
    function w:GetName() return self.name; end
    function w:GetParent() return self.parent; end
    function w:GetID() return self.id; end
    function w:SetID(id) self.id=id; end
    function w:ClearAllPoints() self.point=nil; end
    function w:SetPoint(...) self.point={...}; end
    function w:SetSize(x,y) self.width=x; self.height=y; end
    function w:SetScript(event, callback) self.scripts[event]=callback; end
    function w:SetText(text) self.text=text; end
    function w:GetText() return self.text; end
    function w:Show()
        if self.shown then return; end
        self.shown=true;
        if self.scripts.OnShow then self.scripts.OnShow(self); end
    end
    function w:Hide()
        if not self.shown then return; end
        self.shown=false;
        if self.scripts.OnHide then self.scripts.OnHide(self); end
    end
    function w:IsShown() return self.shown; end
    function w:IsVisible() return self.shown and (not self.parent or self.parent:IsVisible()); end
    function w:SetMinMaxValues(low,high) self.low=low; self.high=high; end
    function w:SetValue(value)
        value=math.max(self.low or 0,math.min(self.high or 10000,value));
        if value==self.value then return; end
        self.value=value;
        if self.scripts.OnValueChanged then self.scripts.OnValueChanged(self,value); end
    end
    function w:SetValueStep(step) self.step=step; end
    function w:LockHighlight() self.highlight=true; end
    function w:UnlockHighlight() self.highlight=false; end
    function w:SetAllPoints(frame) self.allPoints=frame; end
    function w:GetFrameLevel() return self.frameLevel or 1; end
    function w:SetFrameLevel(value) self.frameLevel=value; end
    function w:EnableMouseWheel(value) self.wheelEnabled=value; end
    for _,method in ipairs({"SetFrameStrata","SetClampedToScreen","EnableMouse","SetBackdrop",
        "SetNormalFontObject","SetHighlightFontObject","SetHighlightTexture"}) do
        w[method]=function() end;
    end
    if name then _G[name]=w; end
    return w;
end
function CreateFrame(kind,name,parent,template)
    local w=widget(name,parent);
    if template=="GlueScrollBarTemplate" then
        widget(name.."ScrollUpButton",w); widget(name.."ScrollDownButton",w);
    end
    return w;
end
CharacterCreateFrame=widget("CharacterCreateFrame");
parent=widget("parent",CharacterCreateFrame);
for i=1,29 do
    local frame=widget("CharacterCustomizationButtonFrame"..i,parent); frame.id=i;
    widget(frame.name.."Text",frame):SetText("Option "..i);
    widget(frame.name.."ChoiceButton",frame);
end
for _,name in ipairs({"CharacterCreateRotateLeft","CharacterCreateRotateRight","CharacterCreateRotateLeft30",
    "CharacterCreateRotateRight30","CharacterCreateNameEdit","CharCreateRandomizeButton"}) do widget(name,parent); end
function GetSelectedSex() return sex or 0; end
function GetSelectedClass() return "Warrior","WARRIOR",class or 1; end
function PlaySound() end
values={}; counts={20,5};
function CycleCharCustomization(command,id,value)
    local current=values[id] or 0; local count=counts[id] or 1;
    if command=="EA_WHEEL_BLOCK" then wheelBlocked=id==1; return; end
    if command=="EA_PREVIEW_SAVE" then
        saved={}; for key,selected in pairs(values) do saved[key]=selected; end
        savedRace=CharacterCreate.selectedRaceID; savedSex=sex; savedClass=class;
        return 1;
    end
    if command=="EA_PREVIEW_END" then saved=nil; return 1; end
    if command=="EA_PREVIEW_RESTORE" then
        if not saved or CharacterCreate.selectedRaceID~=savedRace or sex~=savedSex or class~=savedClass then
            return 0;
        end
        values={}; for key,selected in pairs(saved) do values[key]=selected; end
        return 1;
    end
    if command=="EA_GET" or command=="EA_STOCK_GET" then return current,count,"Long Option Label"; end
    if command=="EA_CHOICES" or command=="EA_STOCK_CHOICES" then
        if id==2 then return "0,2,4,"; end
        local list={}; for i=0,count-1 do list[#list+1]=i; end
        return table.concat(list,",")..",";
    end
    if command=="EA_SET" then
        values[id]=value;
        if id==1 then values[2]=0; end
    end
    if type(command)=="number" then values[command]=((values[command] or 0)+2)%6; end
end
function CharacterCustomization_Left() end
function CharacterCustomization_Right() end
function CharacterCreate_UpdateHairCustomization() end
function CharacterCreate_Randomize() randomized=true; end
function CharacterCreate_OnKeyDown(key) lastKey=key; end
''')
    lua.execute(text[text.index("-- Esteria native appearance controls:"):])
    lua.execute('''
CharacterCreate_UpdateHairCustomization();
assert(CharCreateRandomizeButton.point[1]=="RIGHT" and CharCreateRandomizeButton.point[2]==CharacterCreateRotateLeft);
CharacterCustomization_OpenChoices(CharacterCustomizationButtonFrame1ChoiceButton);
local menu=CharacterCustomizationChoiceMenu;
assert(menu.shown and #menu.choices==20 and menu.height==256 and menu.scrollbar.step==1);
assert(CharacterCustomizationChoiceDismiss.shown);
assert(wheelBlocked);
menu.scripts.OnMouseWheel(menu,-12);
assert(menu.offset==10 and menu.rows[10].choice==19);
menu.rows[10].scripts.OnClick(menu.rows[10]);
assert(values[1]==19 and not menu.shown);
assert(not wheelBlocked);
CharacterCustomization_OpenChoices(CharacterCustomizationButtonFrame1ChoiceButton);
assert(menu.offset==10 and menu.rows[10].highlight);
CharacterCreate_OnKeyDown("ESCAPE"); assert(not menu.shown and lastKey==nil);
CharacterCreate_OnKeyDown("ESCAPE"); assert(lastKey=="ESCAPE");
CharacterCustomization_OpenChoices(CharacterCustomizationButtonFrame2ChoiceButton);
assert(#menu.choices==3 and not menu.scrollbar.shown and menu.rows[3].choice==4);
menu.rows[3].scripts.OnClick(menu.rows[3]); assert(values[2]==4);
CharacterCustomization_OpenChoices(CharacterCustomizationButtonFrame2ChoiceButton);
CharacterCreate.selectedRaceID=11;
menu.scripts.OnUpdate(menu,.2); assert(not menu.shown);
values[2]=0;
CharacterCustomization_OpenChoices(CharacterCustomizationButtonFrame2ChoiceButton);
menu.rows[3].scripts.OnClick(menu.rows[3]); assert(values[2]==4);
CharacterCustomization_OpenChoices(CharacterCustomizationButtonFrame2ChoiceButton);
sex=1; menu.scripts.OnUpdate(menu,.2); assert(not menu.shown);
CharacterCustomization_OpenChoices(CharacterCustomizationButtonFrame2ChoiceButton);
local dismiss=CharacterCustomizationChoiceDismiss;
assert(dismiss.shown and dismiss.allPoints==CharacterCreateFrame and dismiss:GetFrameLevel()<menu:GetFrameLevel());
dismiss.scripts.OnClick(dismiss); assert(not menu.shown and not dismiss.shown);
CharacterCreate.selectedRaceID=50;
values[1]=4; values[2]=4;
CharacterCustomization_OpenChoices(CharacterCustomizationButtonFrame1ChoiceButton);
menu.rows[2].scripts.OnEnter(menu.rows[2]);
assert(values[1]==1 and values[2]==0);
menu.scripts.OnUpdate(menu,.2); assert(menu.shown);
menu.rows[2].scripts.OnLeave(menu.rows[2]); assert(values[1]==4 and values[2]==4);
menu.rows[4].scripts.OnEnter(menu.rows[4]);
menu.rows[4].scripts.OnClick(menu.rows[4]); assert(values[1]==3 and not menu.shown and not wheelBlocked);
values[2]=4;
CharacterCustomization_OpenChoices(CharacterCustomizationButtonFrame1ChoiceButton);
menu.rows[2].scripts.OnEnter(menu.rows[2]);
assert(menu.rows[2].wheelEnabled);
menu.rows[2].scripts.OnMouseWheel(menu.rows[2],-1);
assert(menu.offset==1 and values[1]==2 and values[2]==0 and wheelBlocked);
menu.rows[2].scripts.OnLeave(menu.rows[2]); assert(values[1]==3 and values[2]==4);
assert(menu.scrollbar.wheelEnabled);
menu.scrollbar.scripts.OnMouseWheel(menu.scrollbar,-1); assert(menu.offset==2);
local up=CharacterCustomizationChoiceMenuScrollBarScrollUpButton;
local down=CharacterCustomizationChoiceMenuScrollBarScrollDownButton;
assert(up.wheelEnabled and down.wheelEnabled);
up.scripts.OnMouseWheel(up,1); assert(menu.offset==1);
down.scripts.OnMouseWheel(down,-1); assert(menu.offset==2);
menu.rows[1].scripts.OnEnter(menu.rows[1]);
CharacterCreate_OnKeyDown("ESCAPE"); assert(values[1]==3 and values[2]==4 and not wheelBlocked);
CharacterCustomization_OpenChoices(CharacterCustomizationButtonFrame1ChoiceButton);
menu.rows[1].scripts.OnEnter(menu.rows[1]);
CharacterCreate_OnKeyDown("ENTER"); assert(values[1]==3 and values[2]==4 and lastKey=="ENTER");
CharacterCreate.selectedRaceID=11;
values[2]=0;
CharacterCustomization_OpenChoices(CharacterCustomizationButtonFrame2ChoiceButton);
menu.rows[3].scripts.OnEnter(menu.rows[3]); assert(values[2]==4);
menu.rows[3].scripts.OnLeave(menu.rows[3]); assert(values[2]==0);
menu.rows[3].scripts.OnEnter(menu.rows[3]);
menu.rows[3].scripts.OnClick(menu.rows[3]); assert(values[2]==4);
CharacterCreate.selectedRaceID=47;
CharacterCreate_Randomize(); assert(randomized and not menu.shown and values[1]<20 and values[2]<5);
''')


def check_scroll(text, xml):
    lua = LuaRuntime()
    lua.execute('''
CHARACTER_SELECT_ROW_HEIGHT=67; MAX_CHARACTERS_DISPLAYED=8;
CharacterSelect={scrollOffset=0,scrollMax=15,selectedIndex=1};
function GetNumCharacters() return 23; end
CharacterSelectCharacterScrollFrameScrollBar={value=0};
local bar=CharacterSelectCharacterScrollFrameScrollBar;
function bar:GetValue() return self.value; end
function bar:SetValue(value)
    self.value=value;
    if not CharacterSelect.scrollUpdating then CharacterSelect_SetScrollOffset(value/67); end
end
CharacterSelectCharacterScrollFrame={};
function CharacterSelectCharacterScrollFrame:SetVerticalScroll(value)
    self.value=value; CharacterSelect_OnVerticalScroll(self,value);
end
function GlueScrollFrame_OnVerticalScroll(self,value)
    bar:SetValue(value); upDisabled=value==0; downDisabled=value==15*67;
end
function GlueScrollFrame_OnScrollRangeChanged() end
function UpdateCharacterList() refreshes=(refreshes or 0)+1; CharacterSelect_ApplyScrollOffset(); end
''')
    start = text.index("function CharacterSelect_ClampScrollOffset(offset)")
    end = text.index("function CharacterSelect_OnKeyDown", start)
    lua.execute(text[start:end])
    ns = {"ui": "http://www.blizzard.com/wow/ui/"}
    root = ElementTree.fromstring(xml)
    frame = root.find(".//ui:ScrollFrame[@name='CharacterSelectCharacterScrollFrame']", ns)
    onload = frame.find("ui:Scripts/ui:OnLoad", ns).text
    begin = onload.index("local scrollbar")
    lua.execute('''
function widget() local w={}; function w:SetScript(event,fn) self[event]=fn; end; return w; end
CharacterSelectCharacterScrollFrameScrollBarScrollUpButton=widget();
CharacterSelectCharacterScrollFrameScrollBarScrollDownButton=widget();
function CharacterSelectCharacterScrollFrameScrollBar:SetValueStep(value) self.step=value; end
function CharacterSelectCharacterScrollFrameScrollBar:SetScript(event,fn) self[event]=fn; end
''')
    lua.execute(onload[begin:])
    lua.execute('''
local bar=CharacterSelectCharacterScrollFrameScrollBar;
assert(bar.step==67);
CharacterSelect_ScrollBy(-1); assert(CharacterSelect.scrollOffset==1 and bar.value==67);
CharacterSelectCharacterScrollFrameScrollBarScrollDownButton.OnClick();
assert(CharacterSelect.scrollOffset==2 and bar.value==134);
bar.OnValueChanged(bar,8.7*67); assert(CharacterSelect.scrollOffset==9 and bar.value==9*67);
CharacterSelect.selectedIndex=23; CharacterSelect_AdjustOffsetForSelection(); CharacterSelect_ApplyScrollOffset();
assert(CharacterSelect.scrollOffset==15 and bar.value==15*67 and downDisabled);
CharacterSelect_SetScrollOffset(-100); assert(bar.value==0 and upDisabled);
CharacterSelect.scrollMax=0; CharacterSelect_SetScrollOffset(2); assert(bar.value==0);
''')


def check_race_visibility(text):
    lua = LuaRuntime()
    lua.execute('''
CharacterCreate={}; MAX_RACES=64; SEX_MALE=2; SEX_FEMALE=3; strupper=string.upper;
RACE_ICON_TEXTURES={}; RACE_ICON_TCOORDS={HUMAN_MALE={0,1,0,1},HUMAN_FEMALE={0,1,0,1}};
local ids={1,15,56,57,58,59,2};
function GetAvailableRaceIDs() return unpack(ids); end
function GetSelectedSex() return sex; end
function GetSelectedRace() return selected; end
function SetSelectedRace(index) selected=index; end
function GetFactionForRaceID(race) return (race==57 or race==59 or race==2) and "Horde" or "Alliance"; end
function GetFactionForRace(index) return "",GetFactionForRaceID(ids[index]); end
function GetRaceIconTextureKey(file,gender) return "HUMAN_"..gender; end
function CharacterCreate_PositionRaceButtons() end
function SetButtonDesaturated() end
local function widget(name)
    local w={name=name,shown=true};
    function w:GetName() return self.name; end
    function w:CreateTexture(name) return widget(name); end
    function w:Hide() self.shown=false; end
    function w:Show() self.shown=true; end
    function w:Disable() self.disabled=true; end
    function w:SetChecked(value) self.checked=value; end
    for _,method in ipairs({"SetTexture","SetTexCoord","SetSize","SetPoint","SetVertexColor",
        "SetAlpha","SetBlendMode","SetDrawLayer","SetScript"}) do w[method]=function() end; end
    return w;
end
for i=1,64 do
    local name="CharacterCreateRaceButton"..i;
    _G[name]=widget(name); _G[name.."NormalTexture"]=widget(); _G[name.."PushedTexture"]=widget();
end
''')
    start = text.index("function CharacterCreateEnumerateRaces(...)")
    end = text.index("function CharacterCreateEnumerateClasses", start)
    lua.execute(text[start:end])
    lua.execute('''
for _,gender in ipairs({SEX_MALE,SEX_FEMALE}) do
    sex=gender;
    for _,slot in ipairs({2,3,4,5,6}) do
        selected=slot;
        CharacterCreateEnumerateRaces("Human","Human",1,"Sethrak","Sethrak",1,
            "Vrykul","Vrykul",1,"Vrykul","VrykulHorde",1,"Human","ThinHuman",1,
            "Human","ThinHumanHorde",1,"Orc","Orc",1);
        assert(table.concat(CharacterCreate.raceIndicesAlliance,",")=="1,3,5");
        assert(table.concat(CharacterCreate.raceIndicesHorde,",")=="6,7");
        assert(not CharacterCreateRaceButton2.shown and not CharacterCreateRaceButton4.shown);
        assert(CharacterCreateRaceButton4.disabled and not CharacterCreateRaceButton4.enable);
        assert(CharacterCreateRaceButton3.shown and CharacterCreateRaceButton5.shown
            and CharacterCreateRaceButton6.shown);
        assert(selected==((slot==2 or slot==4) and 1 or slot));
    end
end
''')


def main():
    source = pack.STAGE / "locale"
    patched = {name: pack.patch(name, (source / name).read_text(encoding="utf-8-sig")) for name in pack.FILES}
    for name, text in patched.items():
        ast.parse(text) if name.endswith(".lua") else ElementTree.fromstring(text)
        assert pack.patch(name, text) == text, "Patch must be idempotent: " + name
    check_creator(patched["CharacterCreate.lua"])
    check_race_visibility(patched["CharacterCreate.lua"])
    check_scroll(patched["CharacterSelect.lua"], patched["CharacterSelect.xml"])
    print("Character UI: PASS (hover restore/commit, child wheel routing, randomize, "
          "roster navigation, race visibility)")


if __name__ == "__main__":
    main()
