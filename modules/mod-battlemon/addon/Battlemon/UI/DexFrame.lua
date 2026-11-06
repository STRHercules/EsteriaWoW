Battlemon = Battlemon or {}

local ui
local selectedForm = 1
local ROW = 26
local VISIBLE = 16
local filter = ""
local filtered = nil
local catalog = nil
local catalogById = {}
local shinyMode = false

-- The two modes share one form list; only which entries count as caught, and
-- which sprite folder they load from, differ.
local function caughtForms()
    if shinyMode then
        return Battlemon.state.dexShiny or {}
    end
    return Battlemon.state.dexOwned or {}
end

local function caughtSpecies(forms)
    local t = {}
    for fid in pairs(forms) do
        local form = Battlemon.Forms[fid]
        if form and form.species_id then
            t[form.species_id] = true
        end
    end
    return t
end

-- One row per form, grouped under its species number so every variant of a
-- Pokemon sits directly beneath the base entry.
local function buildCatalog()
    if catalog then
        return catalog
    end
    local out = {}
    local forms = Battlemon.FormsList or {}
    for i = 1, #forms do
        local form = forms[i]
        if form.species_id and Battlemon.ModelForms[form.id]
            and Battlemon.ModelForms[form.id][shinyMode and 1 or 0] then
            table.insert(out, {
                form = form,
                speciesId = form.species_id,
                base = (form.variant or "") == "",
                label = Battlemon.FormLabel(form),
                plain = string.lower(Battlemon.FormLabel(form)),
            })
        end
    end
    table.sort(out, function(a, b)
        if a.speciesId ~= b.speciesId then
            return a.speciesId < b.speciesId
        end
        if a.base ~= b.base then
            return a.base
        end
        return (a.form.id or 0) < (b.form.id or 0)
    end)
    catalog = out
    catalogById = {}
    for i = 1, #out do
        catalogById[out[i].form.id] = i
    end
    return out
end

function Battlemon.ResetDexCatalog()
    catalog = nil
    filtered = nil
end

local function entries()
    if filtered then
        return filtered
    end
    local all = buildCatalog()
    if filter == "" then
        filtered = all
        return filtered
    end
    local needle = string.lower(filter)
    local out = {}
    for i = 1, #all do
        local e = all[i]
        if string.find(e.plain, needle, 1, true)
            or string.find(string.format("%03d", e.speciesId or 0), needle, 1, true)
            or string.find(tostring(e.speciesId or ""), needle, 1, true) then
            table.insert(out, e)
        end
    end
    filtered = out
    return out
end

local function entryFor(formId)
    local all = buildCatalog()
    local idx = catalogById[formId]
    if idx then
        return all[idx]
    end
    return all[1]
end

local function typeLabel(s)
    local t1 = Battlemon.Types[s.type1]
    local label = t1 and t1.name or s.type1 or ""
    if s.type2 and s.type2 ~= "" then
        local t2 = Battlemon.Types[s.type2]
        label = label .. "  /  " .. (t2 and t2.name or s.type2)
    end
    return label
end

local function paintDetail(row, owned)
    local s = row and Battlemon.Species[row.speciesId]
    if not row or not s then
        ui.num:SetText("")
        ui.name:SetText("Pokedex")
        ui.types:SetText("")
        ui.meta:SetText("")
        ui.stats:SetText("")
        ui.ownedTag:SetText("")
        ui.desc:SetText(#(Battlemon.SpeciesList or {}) == 0
            and "Pokedex data did not load. Type /bm debug in chat to see which payload failed."
            or "Select an entry on the left.")
        ui.sprite:Hide()
        return
    end
    -- The form words ride on the number line above rather than doubling up with
    -- the big name, which used to print the whole label twice.
    local prefix, base = Battlemon.SplitFormName(
        Battlemon.FormLabel(row.form), row.speciesId, row.form.id)
    if prefix then
        ui.num:SetText(string.format("No. %03d   -   %s", s.id or 0, prefix))
    else
        ui.num:SetText(string.format("No. %03d", s.id or 0))
    end
    ui.name:SetText(shinyMode
        and ("|cffffd200*|r " .. base .. " |cffffd200*|r")
        or base)
    ui.types:SetText(typeLabel(s))
    ui.types:SetTextColor(Battlemon.TypeRGB(s.type1))

    local bits = {}
    if s.category and s.category ~= "" then
        table.insert(bits, s.category .. " Pokemon")
    end
    if s.height and s.height ~= "" then
        table.insert(bits, tostring(s.height) .. " m")
    end
    if s.weight and s.weight ~= "" then
        table.insert(bits, tostring(s.weight) .. " kg")
    end
    ui.meta:SetText(table.concat(bits, "   -   "))

    ui.stats:SetText(string.format(
        "HP |cffffffff%s|r   Atk |cffffffff%s|r   Def |cffffffff%s|r   SpA |cffffffff%s|r   SpD |cffffffff%s|r   Spe |cffffffff%s|r",
        tostring(s.hp or "-"), tostring(s.atk or "-"), tostring(s.def or "-"),
        tostring(s.spa or "-"), tostring(s.spd or "-"), tostring(s.spe or "-")))

    local flavor = s.pokedex
    if not flavor or flavor == "" then
        flavor = "No Pokedex entry recorded."
    end
    ui.desc:SetText(flavor)

    if owned then
        ui.ownedTag:SetText(shinyMode and "SHINY CAUGHT" or "CAUGHT")
        ui.ownedTag:SetTextColor(0.45, 0.95, 0.45)
    else
        ui.ownedTag:SetText(shinyMode and "NO SHINY" or "NOT CAUGHT")
        ui.ownedTag:SetTextColor(0.58, 0.58, 0.62)
    end

    local sprite = row.form.sprite
    if sprite == nil or sprite == "" then
        sprite = Battlemon.SpeciesSprite(s.id)
    end
    -- Open-shell Pecharunt is very flat; center it within this preview only.
    ui.sprite.battlemonPreviewZ = (sprite == "1025_Pecharunt" or sprite == "BM3D_2971") and 0.35 or 0
    if Battlemon.SetPokemonTexture(ui.sprite, "Front", sprite, shinyMode) then
        ui.sprite:SetDesaturated(not owned)
        if owned then
            ui.sprite:SetVertexColor(1, 1, 1)
        else
            ui.sprite:SetVertexColor(0.35, 0.35, 0.40)
        end
        ui.sprite:Show()
    else
        ui.sprite:Hide()
    end
end

-- Cache of the per-refresh, catalog-wide work (caughtForms/caughtSpecies and
-- the counts derived from them). Scrolling calls RefreshDex on every wheel
-- tick/drag update but never changes which forms/species are caught, so
-- redoing these full-table walks every tick is wasted work that shows up as
-- choppy scrolling. scrollOnly=true reuses the last computed values instead.
local cachedForms, cachedSpecies, cachedCaughtSpec, cachedCaughtForm

function Battlemon.RefreshDex(scrollOnly)
    if not ui or not ui.frame:IsShown() then
        return
    end
    local list = entries()
    local forms, species, caughtSpec, caughtForm
    if scrollOnly and cachedForms then
        forms, species = cachedForms, cachedSpecies
        caughtSpec, caughtForm = cachedCaughtSpec, cachedCaughtForm
    else
        forms = caughtForms()
        species = caughtSpecies(forms)
        caughtSpec = 0
        for _ in pairs(species) do
            caughtSpec = caughtSpec + 1
        end
        caughtForm = 0
        for _ in pairs(forms) do
            caughtForm = caughtForm + 1
        end
        cachedForms, cachedSpecies = forms, species
        cachedCaughtSpec, cachedCaughtForm = caughtSpec, caughtForm
    end

    FauxScrollFrame_Update(ui.scroll, #list, VISIBLE, ROW)
    local offset = FauxScrollFrame_GetOffset(ui.scroll) or 0
    for i = 1, VISIBLE do
        local e = list[offset + i]
        local btn = ui.rows[i]
        if e then
            btn:Show()
            btn.formId = e.form.id
            local have = forms[e.form.id] and true or false
            if e.base then
                btn.text:SetText(string.format("%03d   %s", e.speciesId or 0, e.label))
            else
                btn.text:SetText(string.format("%03d   -  %s", e.speciesId or 0, e.label))
            end
            if e.form.id == selectedForm then
                Battlemon.Fill(btn.bg, 0.34, 0.28, 0.10, 1)
                btn.text:SetTextColor(1, 0.92, 0.55)
            elseif have then
                Battlemon.Fill(btn.bg, 0.12, 0.14, 0.18, 1)
                btn.text:SetTextColor(0.94, 0.95, 0.98)
            else
                Battlemon.Fill(btn.bg, 0.07, 0.08, 0.10, 1)
                btn.text:SetTextColor(0.58, 0.59, 0.63)
            end
            local sprite = e.form.sprite
            if sprite == nil or sprite == "" then
                sprite = Battlemon.SpeciesSprite(e.speciesId)
            end
            if Battlemon.SetPokemonTexture(btn.icon, "Front", sprite, shinyMode) then
                btn.icon:SetDesaturated(not have)
                if have then
                    btn.icon:SetVertexColor(1, 1, 1)
                else
                    btn.icon:SetVertexColor(0.42, 0.42, 0.46)
                end
                btn.icon:Show()
            else
                btn.icon:Hide()
            end
        else
            btn:Hide()
            btn.formId = nil
        end
    end

    local speciesSeen = {}
    for _, entry in ipairs(buildCatalog()) do speciesSeen[entry.speciesId] = true end
    local totalSpec = 0
    for _ in pairs(speciesSeen) do totalSpec = totalSpec + 1 end
    local totalForm = #buildCatalog()
    local text = string.format(
        "%s |cffffffff%d|r / |cffffffff%d|r species   -   |cffffffff%d|r / |cffffffff%d|r forms",
        shinyMode and "Shinies caught" or "Caught",
        caughtSpec, totalSpec, caughtForm, totalForm)
    if filter ~= "" then
        text = text .. string.format("   -   %d match%s", #list, #list == 1 and "" or "es")
    end
    ui.count:SetText(text)
    ui.title:SetText(shinyMode and "Shiny Pokedex" or "Pokedex")
    if shinyMode then
        ui.title:SetTextColor(1, 0.84, 0.28)
    else
        ui.title:SetTextColor(1, 0.90, 0.40)
    end
    ui.shinyBtn.text:SetText(shinyMode and "NORMAL" or "SHINY")

    local row = entryFor(selectedForm)
    paintDetail(row, row and forms[row.form.id] and true or false)
end

local function build()
    if ui then
        return ui
    end
    local f = Battlemon.MakeWindow("BattlemonDexFrame", 848, 552)

    local banner = f:CreateTexture(nil, "ARTWORK")
    banner:SetPoint("TOPLEFT", 4, -4)
    banner:SetPoint("TOPRIGHT", -4, -4)
    banner:SetHeight(62)
    Battlemon.Fill(banner, 0.10, 0.07, 0.14, 1)
    local shade = f:CreateTexture(nil, "ARTWORK")
    shade:SetAllPoints(banner)
    Battlemon.Fill(shade, 0, 0, 0, 0.45)

    local title = Battlemon.Font(f, 20, "", 1, 0.90, 0.40)
    title:SetPoint("TOP", 0, -16)
    title:SetText("Pokedex")

    local count = Battlemon.Font(f, 12, "", 0.86, 0.90, 0.96)
    count:SetPoint("TOP", title, "BOTTOM", 0, -4)

    local search = CreateFrame("EditBox", "BattlemonDexSearch", f, "InputBoxTemplate")
    search:SetSize(220, 20)
    search:SetPoint("TOPLEFT", 26, -76)
    search:SetAutoFocus(false)
    search:SetMaxLetters(32)
    search:SetScript("OnTextChanged", function(self)
        if not ui then
            return
        end
        filter = self:GetText() or ""
        filtered = nil
        FauxScrollFrame_SetOffset(ui.scroll, 0)
        local bar = getglobal("BattlemonDexScrollScrollBar")
        if bar then
            bar:SetValue(0)
        end
        Battlemon.RefreshDex()
    end)
    search:SetScript("OnEscapePressed", function(self)
        self:SetText("")
        self:ClearFocus()
    end)

    local searchLabel = Battlemon.Font(f, 11, "", 0.72, 0.75, 0.80)
    searchLabel:SetPoint("LEFT", search, "RIGHT", 8, 0)
    searchLabel:SetText("search by name, number, or form")

    local shinyBtn
    shinyBtn = Battlemon.MakeTextButton(f, 92, 22, "SHINY", function()
        catalog = nil
        filtered = nil
        shinyMode = not shinyMode
        if shinyMode then
            shinyBtn:SetTint(0.42, 0.33, 0.08)
        else
            shinyBtn:SetTint(0.18, 0.20, 0.27)
        end
        Battlemon.RefreshDex()
    end)
    shinyBtn:SetPoint("TOPRIGHT", -26, -74)

    local listFrame = CreateFrame("Frame", nil, f)
    listFrame:SetPoint("TOPLEFT", 18, -102)
    listFrame:SetSize(356, VISIBLE * ROW + 6)
    local listBg = listFrame:CreateTexture(nil, "BACKGROUND")
    listBg:SetAllPoints()
    Battlemon.Fill(listBg, 0.03, 0.04, 0.06, 0.9)

    local scroll = CreateFrame("ScrollFrame", "BattlemonDexScroll", listFrame, "FauxScrollFrameTemplate")
    scroll:SetPoint("TOPLEFT", 2, -3)
    scroll:SetPoint("BOTTOMRIGHT", -26, 3)
    scroll:SetScript("OnVerticalScroll", function(self, offset)
        FauxScrollFrame_OnVerticalScroll(self, offset, ROW, function() Battlemon.RefreshDex(true) end)
    end)

    local rows = {}
    for i = 1, VISIBLE do
        local btn = CreateFrame("Button", nil, listFrame)
        btn:SetSize(324, ROW - 2)
        btn:SetPoint("TOPLEFT", 4, -((i - 1) * ROW) - 4)
        btn.bg = btn:CreateTexture(nil, "BACKGROUND")
        btn.bg:SetAllPoints()
        Battlemon.Fill(btn.bg, 0.10, 0.11, 0.14, 1)
        btn.icon = btn:CreateTexture(nil, "ARTWORK")
        btn.icon:SetSize(22, 22)
        btn.icon:SetPoint("LEFT", 2, 0)
        btn.text = Battlemon.Font(btn, 12, "", 0.94, 0.95, 0.98)
        btn.text:SetPoint("LEFT", 28, 0)
        btn.text:SetJustifyH("LEFT")
        btn.text:SetWidth(288)
        btn.text:SetHeight(ROW - 2)
        btn.text:SetWordWrap(false)
        btn:SetScript("OnClick", function(self)
            if self.formId then
                selectedForm = self.formId
                Battlemon.RefreshDex()
            end
        end)
        rows[i] = btn
    end

    local detail = CreateFrame("Frame", nil, f)
    detail:SetPoint("TOPLEFT", listFrame, "TOPRIGHT", 16, 0)
    detail:SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", -18, 16)
    local detailBg = detail:CreateTexture(nil, "BACKGROUND")
    detailBg:SetAllPoints()
    Battlemon.Fill(detailBg, 0.04, 0.05, 0.07, 0.85)

    local num = Battlemon.Font(detail, 13, "", 0.78, 0.81, 0.88)
    num:SetPoint("TOPLEFT", 12, -10)

    local ownedTag = Battlemon.Font(detail, 12, "", 0.45, 0.95, 0.45)
    ownedTag:SetPoint("TOPRIGHT", -12, -10)

    local sprite = detail:CreateTexture(nil, "ARTWORK")
    sprite:SetSize(184, 184)
    sprite:SetPoint("TOP", 0, -24)

    local name = Battlemon.Font(detail, 20, "", 1, 0.95, 0.72)
    name:SetPoint("TOP", sprite, "BOTTOM", 0, -4)
    name:SetWidth(400)
    name:SetHeight(26)
    name:SetWordWrap(false)

    local types = Battlemon.Font(detail, 14, "", 0.75, 0.88, 1)
    types:SetPoint("TOP", name, "BOTTOM", 0, -6)

    local meta = Battlemon.Font(detail, 12, "", 0.82, 0.85, 0.90)
    meta:SetPoint("TOP", types, "BOTTOM", 0, -8)

    local stats = Battlemon.Font(detail, 12, "", 1, 0.86, 0.50)
    stats:SetPoint("TOP", meta, "BOTTOM", 0, -10)

    local descBg = detail:CreateTexture(nil, "BORDER")
    descBg:SetPoint("TOPLEFT", 14, -336)
    descBg:SetPoint("BOTTOMRIGHT", -14, 12)
    Battlemon.Fill(descBg, 0.02, 0.02, 0.03, 0.75)

    local desc = Battlemon.Font(detail, 13, "", 0.93, 0.94, 0.96)
    desc:SetPoint("TOPLEFT", descBg, "TOPLEFT", 10, -8)
    desc:SetPoint("BOTTOMRIGHT", descBg, "BOTTOMRIGHT", -10, 8)
    desc:SetJustifyH("LEFT")
    desc:SetJustifyV("TOP")

    f:SetScript("OnShow", function()
        filtered = nil
        Battlemon.RefreshDex()
    end)

    ui = {
        frame = f, scroll = scroll, rows = rows, count = count, search = search,
        sprite = sprite, name = name, types = types, meta = meta,
        stats = stats, desc = desc, num = num, ownedTag = ownedTag,
        title = title, shinyBtn = shinyBtn,
    }
    return ui
end

function Battlemon.BuildDex()
    return build().frame
end

function Battlemon.ShowDex()
    Battlemon.EnsureData()
    catalog = nil
    filtered = nil
    Battlemon.OpenPanel("dex")
    Battlemon.RefreshDex()
end
