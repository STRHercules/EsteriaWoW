Battlemon = Battlemon or {}

local function indexBy(rows, key)
    local t = {}
    for _, row in ipairs(rows) do
        if row[key] ~= nil and row[key] ~= "" then
            t[row[key]] = row
        end
    end
    return t
end

-- Empty defaults so a failed payload can never turn a lookup into a nil index
-- error halfway through a battle packet.
Battlemon.Types = {}
Battlemon.Species = {}
Battlemon.SpeciesList = {}
Battlemon.SpeciesByInternal = {}
Battlemon.Forms = {}
Battlemon.FormsList = {}
Battlemon.FormsBySprite = {}
Battlemon.DefaultForm = {}
Battlemon.Abilities = {}
Battlemon.Items = {}
Battlemon.ItemsById = {}
Battlemon.Moves = {}
Battlemon.MovesByInternal = {}
Battlemon.TypeChart = {}
Battlemon.Learnsets = {}
Battlemon.DataReport = {}

local function payload(raw, key)
    return raw[key .. "_parts"] or raw[key]
end

-- Each payload loads on its own so one bad file cannot take the rest with it.
local function section(raw, key, apply)
    local rows
    local ok, err = pcall(function()
        rows = Battlemon.ParseCSV(payload(raw, key))
        apply(rows)
    end)
    if ok then
        Battlemon.DataReport[key] = string.format("%d rows", rows and #rows or 0)
    else
        Battlemon.DataReport[key] = "FAILED: " .. tostring(err)
    end
end

function Battlemon.LoadData()
    local raw = BattlemonRawCSV or {}

    section(raw, "types", function(rows)
        Battlemon.Types = indexBy(rows, "internal_name")
    end)

    section(raw, "species", function(rows)
        Battlemon.SpeciesList = rows
        Battlemon.Species = indexBy(rows, "id")
        Battlemon.SpeciesByInternal = indexBy(rows, "internal_name")
        Battlemon.SpeciesCount = #rows
    end)

    section(raw, "forms", function(rows)
        Battlemon.FormsList = rows
        Battlemon.Forms = indexBy(rows, "id")
        Battlemon.FormsBySprite = indexBy(rows, "sprite")
        Battlemon.FormCount = #rows
        local default = {}
        for i = 1, #rows do
            local f = rows[i]
            local sid = f.species_id
            if sid then
                local cur = default[sid]
                if not cur or ((f.variant or "") == "" and (cur.variant or "") ~= "") then
                    default[sid] = f
                end
            end
        end
        Battlemon.DefaultForm = default
    end)

    section(raw, "abilities", function(rows)
        Battlemon.Abilities = indexBy(rows, "internal_name")
    end)

    section(raw, "items", function(rows)
        Battlemon.Items = indexBy(rows, "internal_name")
        Battlemon.ItemsById = indexBy(rows, "id")
    end)

    section(raw, "moves", function(rows)
        Battlemon.Moves = indexBy(rows, "id")
        Battlemon.MovesByInternal = indexBy(rows, "internal_name")
    end)

    section(raw, "type_chart", function(rows)
        local chart = {}
        for _, row in ipairs(rows) do
            chart[row.attacker] = chart[row.attacker] or {}
            chart[row.attacker][row.defender] = row.multiplier
        end
        Battlemon.TypeChart = chart
    end)

    -- Learnsets stay on the server; the client never needs the ~14k rows.
    Battlemon.Learnsets = {}
    Battlemon.DataLoaded = #Battlemon.SpeciesList > 0
    if Battlemon.ResetDexCatalog then
        Battlemon.ResetDexCatalog()
    end
end

-- Called before any window opens, so a failed load at login can still recover.
function Battlemon.EnsureData()
    if Battlemon.DataLoaded then
        return true
    end
    local ok, err = pcall(Battlemon.LoadData)
    if not ok then
        Battlemon.Print("|cffff4040data load failed:|r " .. tostring(err))
    end
    return Battlemon.DataLoaded == true
end

-- Display name for an owned Pokémon. Prefers whatever the server sent, then the
-- form catalog, then the species, so the UI never falls back to a bare "#id".
function Battlemon.FormName(formId, serverName)
    if serverName and serverName ~= "" then
        return serverName
    end
    local form = Battlemon.Forms[formId]
    if form then
        if form.name and form.name ~= "" then
            return form.name
        end
        local species = Battlemon.Species[form.species_id]
        if species and species.name and species.name ~= "" then
            return species.name
        end
    end
    return "#" .. tostring(formId or 0)
end

function Battlemon.FormSprite(formId, serverSprite)
    if serverSprite and serverSprite ~= "" then
        return serverSprite
    end
    local form = Battlemon.Forms[formId]
    if form and form.sprite and form.sprite ~= "" then
        return form.sprite
    end
    local species = form and Battlemon.Species[form.species_id]
    return species and species.sprite or ""
end

-- Cosplay / cap Pikachu, indexed the way this sprite pack numbers them.
local PIKACHU_FORM = {
    ["02"] = "Partner",
    ["03"] = "Cosplay",
    ["04"] = "Rock Star",
    ["05"] = "Belle",
    ["06"] = "Pop Star",
    ["07"] = "Ph.D",
    ["08"] = "Libre",
    ["09"] = "Original Cap",
    ["10"] = "Hoenn Cap",
    ["11"] = "Sinnoh Cap",
    ["12"] = "Unova Cap",
    ["13"] = "Kalos Cap",
    ["14"] = "Alola Cap",
    ["15"] = "Partner Cap",
    ["16"] = "World Cap",
}

local ALCREMIE_CREAM = {
    "Vanilla Cream", "Ruby Cream", "Matcha Cream", "Mint Cream",
    "Lemon Cream", "Salted Cream", "Ruby Swirl", "Caramel Swirl", "Rainbow Swirl",
}
local ALCREMIE_SWEET = {
    "Strawberry", "Berry", "Love", "Star", "Clover", "Flower", "Ribbon",
}

local MAGIC = "([%^%$%(%)%%%.%[%]%*%+%-%?])"

-- Some variants exist in the sprite pack as an index only, so the exporter falls
-- back to "Pikachu (02)". Those carry nothing the variant logic below cannot
-- rebuild better, unlike a real catalog name such as "Trash Cloak Wormadam".
local function isGeneratedName(name, speciesName)
    if not name or name == "" then
        return true
    end
    if not speciesName or speciesName == "" then
        return false
    end
    if name == speciesName then
        return true
    end
    return string.find(name, "^" .. string.gsub(speciesName, MAGIC, "%%%1") .. " %(%d+%)$") ~= nil
end

-- Variants come out of the sprite pack as bare indices ("02", "03_female"), so
-- build a readable label from the species name instead of the generated one.
local function formLabel(form)
    if not form then
        return "???"
    end
    local species = Battlemon.Species[form.species_id]
    local speciesName = species and species.name
    local base = speciesName or form.name or "???"
    local variant = tostring(form.variant or "")
    -- The 3D catalog already supplies readable names; its variant is a machine key.
    if form.id == 2970 then return "Pecharunt (Closed Shell)" end
    if form.id == 2971 then return "Pecharunt (Open Shell)" end
    if string.sub(variant, 1, 9) == "pixelmon:" then
        return form.name and form.name ~= "" and form.name or base
    end
    if variant == "" then
        return base
    end
    if not isGeneratedName(form.name, speciesName) then
        return form.name
    end

    local sid = tonumber(form.species_id) or 0
    local female = false
    local key = ""
    if type(variant) == "number" then
        key = string.format("%02d", variant)
    elseif variant == "female" then
        female = true
    else
        local numberedFemale = string.match(variant, "^(%d+)_female$")
        if numberedFemale then
            female = true
            key = string.format("%02d", tonumber(numberedFemale))
        elseif string.match(variant, "^%d+$") then
            key = string.format("%02d", tonumber(variant))
        else
            key = variant
        end
    end

    local extra
    if sid == 25 and PIKACHU_FORM[key] then
        extra = PIKACHU_FORM[key]
    elseif sid == 869 then
        local idx = tonumber(key)
        if idx then
            extra = (ALCREMIE_CREAM[(idx % 9) + 1] or "Cream")
                .. " " .. (ALCREMIE_SWEET[math.floor(idx / 9) + 1] or "Sweet")
        end
    end
    if not extra and key ~= "" then
        if string.match(key, "^%d+$") then
            extra = "Form " .. tonumber(key)
        else
            extra = key
        end
    end

    if extra and extra ~= "" then
        base = base .. " (" .. extra .. ")"
    end
    if female then
        base = base .. " (Female)"
    end
    return base
end

-- Some client fonts lack the gender glyphs; keep every label readable.
function Battlemon.FormLabel(form)
    local label = formLabel(form)
    label = string.gsub(label, "\226\153\128", " (Female)")
    label = string.gsub(label, "\226\153\130", " (Male)")
    return label
end

Battlemon.FormLabelPlain = Battlemon.FormLabel

-- Form names read as "<form words> <Species>", which is a mouthful on one line.
-- Splits the leading words off so a plate can stack them over the species. The
-- prefix comes back nil when there is nothing to stack, so callers that get a
-- plain species name lay out exactly as they did before.
function Battlemon.SplitFormName(name, speciesId, formId)
    name = name or ""
    if (not speciesId or speciesId == 0) and formId then
        local form = Battlemon.Forms[formId]
        speciesId = form and form.species_id
    end
    local species = speciesId and Battlemon.Species[speciesId]
    local base = species and species.name
    if not base or base == "" or name == base then
        return nil, name
    end
    local at = string.find(name, base, 1, true)
    if not at or at <= 1 then
        return nil, name
    end
    local prefix = string.gsub(string.sub(name, 1, at - 1), "%s+$", "")
    if prefix == "" then
        return nil, name
    end
    return prefix, string.sub(name, at)
end

function Battlemon.SpeciesSprite(speciesId)
    local form = Battlemon.DefaultForm[speciesId]
    if form and form.sprite and form.sprite ~= "" then
        return form.sprite
    end
    local species = Battlemon.Species[speciesId]
    return species and species.sprite or ""
end

function Battlemon.PrintDataReport()
    Battlemon.Print("data payloads:")
    local keys = { "types", "type_chart", "abilities", "moves", "items", "species", "forms" }
    for _, key in ipairs(keys) do
        DEFAULT_CHAT_FRAME:AddMessage("  " .. key .. ": " .. tostring(Battlemon.DataReport[key] or "not loaded"))
    end
end

function Battlemon.TypeMultiplier(attackType, defType)
    if not attackType or not defType or defType == "" then
        return 1
    end
    local row = Battlemon.TypeChart[attackType]
    if not row then
        return 1
    end
    return row[defType] or 1
end

function Battlemon.Effectiveness(attackType, type1, type2)
    local m = Battlemon.TypeMultiplier(attackType, type1)
    if type2 and type2 ~= "" then
        m = m * Battlemon.TypeMultiplier(attackType, type2)
    end
    return m
end

function Battlemon.PickMoves(speciesId, level)
    local list = Battlemon.Learnsets[speciesId] or {}
    local order = {}
    for i = 1, #list do
        local e = list[i]
        if e.level <= level then
            table.insert(order, e.move_internal_name)
        end
    end
    local picked = {}
    local used = {}
    for i = #order, 1, -1 do
        local name = order[i]
        if not used[name] then
            used[name] = true
            table.insert(picked, 1, name)
            if #picked >= 4 then
                break
            end
        end
    end
    return picked
end

function Battlemon.RollGender(ratio)
    if ratio == "AlwaysMale" then return "M" end
    if ratio == "AlwaysFemale" then return "F" end
    if ratio == "Genderless" then return "N" end
    local female = 50
    if ratio == "FemaleOneEighth" then female = 12.5
    elseif ratio == "Female25Percent" then female = 25
    elseif ratio == "Female50Percent" then female = 50
    elseif ratio == "Female75Percent" then female = 75
    elseif ratio == "FemaleSevenEighths" then female = 87.5
    end
    if math.random() * 100 < female then
        return "F"
    end
    return "M"
end
