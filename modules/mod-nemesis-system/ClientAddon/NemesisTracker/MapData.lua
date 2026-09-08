NemesisTracker = NemesisTracker or {}
local NT = NemesisTracker

NT.MapData = NT.MapData or {}
local MapData = NT.MapData

MapData.tileColumns = 4
MapData.tileRows = 3
MapData.tileCount = 12

local function zone(folder, texture, key)
    return {
        folder = folder,
        texture = texture or folder,
        key = key or folder,
    }
end

local byZoneId = {
    [1] = zone("DunMorogh"),
    [3] = zone("Badlands"),
    [4] = zone("BlastedLands"),
    [8] = zone("SwampOfSorrows"),
    [10] = zone("Duskwood"),
    [11] = zone("Wetlands"),
    [12] = zone("Elwynn"),
    [14] = zone("Durotar"),
    [15] = zone("Dustwallow"),
    [16] = zone("Azshara"),
    [17] = zone("Barrens"),
    [28] = zone("WesternPlaguelands"),
    [33] = zone("Stranglethorn"),
    [36] = zone("Alterac"),
    [38] = zone("LochModan"),
    [40] = zone("Westfall"),
    [41] = zone("DeadwindPass"),
    [44] = zone("RedRidge"),
    [45] = zone("Arathi"),
    [46] = zone("BurningSteppes"),
    [47] = zone("Hinterlands"),
    [51] = zone("SearingGorge"),
    [65] = zone("Dragonblight"),
    [66] = zone("ZulDrak"),
    [67] = zone("StormPeaks"),
    [85] = zone("Tirisfal"),
    [130] = zone("Silverpine"),
    [139] = zone("EasternPlaguelands"),
    [141] = zone("Teldrassil"),
    [148] = zone("Darkshore"),
    [209] = zone("StonetalonMountains"),
    [210] = zone("IcecrownGlacier"),
    [215] = zone("Mulgore"),
    [267] = zone("Hilsbrad"),
    [331] = zone("Ashenvale"),
    [357] = zone("Feralas"),
    [361] = zone("Felwood"),
    [394] = zone("GrizzlyHills"),
    [400] = zone("ThousandNeedles"),
    [405] = zone("Desolace"),
    [406] = zone("StonetalonMountains"),
    [418] = zone("HowlingFjord"),
    [440] = zone("Tanaris"),
    [490] = zone("UnGoroCrater"),
    [493] = zone("Moonglade"),
    [495] = zone("CrystalsongForest"),
    [618] = zone("Winterspring"),
    [1377] = zone("Silithus"),
    [1497] = zone("Undercity"),
    [1519] = zone("Stormwind"),
    [1537] = zone("Ironforge"),
    [1637] = zone("Orgrimmar"),
    [1638] = zone("ThunderBluff"),
    [2597] = zone("AlteracValley"),
    [2817] = zone("CrystalsongForest"),
    [3430] = zone("EversongWoods"),
    [3433] = zone("Ghostlands"),
    [3483] = zone("Hellfire"),
    [3518] = zone("Nagrand"),
    [3519] = zone("TerokkarForest"),
    [3520] = zone("ShadowmoonValley"),
    [3521] = zone("Zangarmarsh"),
    [3522] = zone("BladesEdgeMountains"),
    [3523] = zone("Netherstorm"),
    [3524] = zone("AzuremystIsle"),
    [3525] = zone("BloodmystIsle"),
    [3537] = zone("BoreanTundra"),
    [3703] = zone("ShattrathCity"),
    [3711] = zone("SholazarBasin"),
    [4197] = zone("Wintergrasp"),
    [4395] = zone("Dalaran1_", "Dalaran1_", "Dalaran"),
}

local zoneNameAliases = {
    ["Aerie Peak"] = zone("Hinterlands"),
    ["Agmar's Hammer"] = zone("Dragonblight"),
    ["Aldor Rise"] = zone("ShattrathCity"),
    ["Alterac Mountains"] = zone("Alterac"),
    ["Amberpine Lodge"] = zone("GrizzlyHills"),
    ["Arathi Highlands"] = zone("Arathi"),
    ["Area 52"] = zone("Netherstorm"),
    ["Ashenvale"] = zone("Ashenvale"),
    ["Astranaar"] = zone("Ashenvale"),
    ["Azshara"] = zone("Azshara"),
    ["Azure Watch"] = zone("AzuremystIsle"),
    ["Azuremyst Isle"] = zone("AzuremystIsle"),
    ["Badlands"] = zone("Badlands"),
    ["Blasted Lands"] = zone("BlastedLands"),
    ["Blade's Edge Mountains"] = zone("BladesEdgeMountains"),
    ["Blood Watch"] = zone("BloodmystIsle"),
    ["Bloodmyst Isle"] = zone("BloodmystIsle"),
    ["Booty Bay"] = zone("Stranglethorn"),
    ["Borean Tundra"] = zone("BoreanTundra"),
    ["Bouldercrag's Refuge"] = zone("StormPeaks"),
    ["Brill"] = zone("Tirisfal"),
    ["Burning Steppes"] = zone("BurningSteppes"),
    ["Camp Mojache"] = zone("Feralas"),
    ["Camp Oneqwah"] = zone("GrizzlyHills"),
    ["Camp Taurajo"] = zone("Barrens"),
    ["Cathedral Square"] = zone("Stormwind"),
    ["Cenarion Hold"] = zone("Silithus"),
    ["Coldridge Valley"] = zone("DunMorogh"),
    ["Crossroads"] = zone("Barrens"),
    ["Crystalsong Forest"] = zone("CrystalsongForest"),
    ["Dalaran"] = zone("Dalaran1_", "Dalaran1_", "Dalaran"),
    ["Darkshire"] = zone("Duskwood"),
    ["Darkshore"] = zone("Darkshore"),
    ["Deadwind Pass"] = zone("DeadwindPass"),
    ["Deathknell"] = zone("Tirisfal"),
    ["Desolace"] = zone("Desolace"),
    ["Dragonblight"] = zone("Dragonblight"),
    ["Dun Morogh"] = zone("DunMorogh"),
    ["Durotar"] = zone("Durotar"),
    ["Duskwood"] = zone("Duskwood"),
    ["Dustwallow Marsh"] = zone("Dustwallow"),
    ["Dwarven District"] = zone("Stormwind"),
    ["Eastern Plaguelands"] = zone("EasternPlaguelands"),
    ["Elwynn Forest"] = zone("Elwynn"),
    ["Eversong Woods"] = zone("EversongWoods"),
    ["Falconwing Square"] = zone("EversongWoods"),
    ["Felwood"] = zone("Felwood"),
    ["Feralas"] = zone("Feralas"),
    ["Fizzcrank Airstrip"] = zone("BoreanTundra"),
    ["Forest Song"] = zone("Ashenvale"),
    ["Garadar"] = zone("Nagrand"),
    ["Ghostlands"] = zone("Ghostlands"),
    ["Goldshire"] = zone("Elwynn"),
    ["Grom'gol Base Camp"] = zone("Stranglethorn"),
    ["Grizzly Hills"] = zone("GrizzlyHills"),
    ["Hammerfall"] = zone("Arathi"),
    ["Hellfire Peninsula"] = zone("Hellfire"),
    ["Hillsbrad Foothills"] = zone("Hilsbrad"),
    ["Honor Hold"] = zone("Hellfire"),
    ["Howling Fjord"] = zone("HowlingFjord"),
    ["Icecrown"] = zone("IcecrownGlacier"),
    ["Icecrown Glacier"] = zone("IcecrownGlacier"),
    ["Ironforge"] = zone("Ironforge"),
    ["K3"] = zone("StormPeaks"),
    ["Kharanos"] = zone("DunMorogh"),
    ["Lakeshire"] = zone("RedRidge"),
    ["Light's Breach"] = zone("ZulDrak"),
    ["Light's Hope Chapel"] = zone("EasternPlaguelands"),
    ["Loch Modan"] = zone("LochModan"),
    ["Menethil Harbor"] = zone("Wetlands"),
    ["Moa'ki Harbor"] = zone("Dragonblight"),
    ["Moonglade"] = zone("Moonglade"),
    ["Mulgore"] = zone("Mulgore"),
    ["Nagrand"] = zone("Nagrand"),
    ["Nesingwary Base Camp"] = zone("SholazarBasin"),
    ["Netherstorm"] = zone("Netherstorm"),
    ["Northshire Valley"] = zone("Elwynn"),
    ["Old Town"] = zone("Stormwind"),
    ["Orgrimmar"] = zone("Orgrimmar"),
    ["Ratchet"] = zone("Barrens"),
    ["Razor Hill"] = zone("Durotar"),
    ["Redridge Mountains"] = zone("RedRidge"),
    ["Refuge Pointe"] = zone("Arathi"),
    ["Revenant's Toll"] = zone("Dragonblight"),
    ["Sen'jin Village"] = zone("Durotar"),
    ["Searing Gorge"] = zone("SearingGorge"),
    ["Shadowmoon Valley"] = zone("ShadowmoonValley"),
    ["Shattrath City"] = zone("ShattrathCity"),
    ["Sholazar Basin"] = zone("SholazarBasin"),
    ["Silvermoon City"] = zone("SilvermoonCity"),
    ["Silverpine Forest"] = zone("Silverpine"),
    ["Southshore"] = zone("Hilsbrad"),
    ["Storm Peaks"] = zone("StormPeaks"),
    ["Stormwind City"] = zone("Stormwind"),
    ["Stranglethorn Vale"] = zone("Stranglethorn"),
    ["Swamp of Sorrows"] = zone("SwampOfSorrows"),
    ["Tanaris"] = zone("Tanaris"),
    ["Tarren Mill"] = zone("Hilsbrad"),
    ["Telaar"] = zone("Nagrand"),
    ["Teldrassil"] = zone("Teldrassil"),
    ["Terokkar Forest"] = zone("TerokkarForest"),
    ["The Barrens"] = zone("Barrens"),
    ["The Exodar"] = zone("TheExodar"),
    ["The Hinterlands"] = zone("Hinterlands"),
    ["The Park"] = zone("Stormwind"),
    ["The Sepulcher"] = zone("Silverpine"),
    ["The Storm Peaks"] = zone("StormPeaks"),
    ["The Temple of Atal'Hakkar"] = zone("SwampOfSorrows"),
    ["The Trade District"] = zone("Stormwind"),
    ["Thousand Needles"] = zone("ThousandNeedles"),
    ["Thrallmar"] = zone("Hellfire"),
    ["Thunder Bluff"] = zone("ThunderBluff"),
    ["Tirisfal Glades"] = zone("Tirisfal"),
    ["Trade District"] = zone("Stormwind"),
    ["Undercity"] = zone("Undercity"),
    ["Un'Goro Crater"] = zone("UnGoroCrater"),
    ["Vale of Honor"] = zone("Orgrimmar"),
    ["Vale of Spirits"] = zone("Orgrimmar"),
    ["Vale of Strength"] = zone("Orgrimmar"),
    ["Vale of Trials"] = zone("Durotar"),
    ["Vale of Wisdom"] = zone("Orgrimmar"),
    ["Valiance Keep"] = zone("BoreanTundra"),
    ["Valley of Trials"] = zone("Durotar"),
    ["Vengeance Landing"] = zone("HowlingFjord"),
    ["Warsong Hold"] = zone("BoreanTundra"),
    ["Western Plaguelands"] = zone("WesternPlaguelands"),
    ["Westfall"] = zone("Westfall"),
    ["Westguard Keep"] = zone("HowlingFjord"),
    ["Wetlands"] = zone("Wetlands"),
    ["Wintergrasp"] = zone("Wintergrasp"),
    ["Wyrmrest Temple"] = zone("Dragonblight"),
    ["Zangarmarsh"] = zone("Zangarmarsh"),
    ["Zul'Drak"] = zone("ZulDrak"),
}

local byNormalizedZoneName = {}

local function normalizeLookupKey(zoneName)
    return string.lower(string.gsub(zoneName or "", "[^A-Za-z0-9]", ""))
end

for zoneName, zoneData in pairs(zoneNameAliases) do
    byNormalizedZoneName[normalizeLookupKey(zoneName)] = zoneData
end

local function sanitizeZoneName(zoneName)
    local sanitized = string.gsub(zoneName or "", "[^A-Za-z0-9]", "")
    if sanitized == "" then
        return nil
    end
    return sanitized
end

function MapData:GetZone(zoneId, zoneName)
    local zone = byNormalizedZoneName[normalizeLookupKey(zoneName)]
    if zone then
        return {
            file = zone.folder,
            texture = zone.texture,
            key = zone.key,
            label = zoneName,
        }
    end

    zone = zoneId and byZoneId[zoneId] or nil
    if zone then
        return {
            file = zone.folder,
            texture = zone.texture,
            key = zone.key,
            label = zoneName or zone.key,
        }
    end

    local sanitized = sanitizeZoneName(zoneName)
    if sanitized then
        return {
            file = sanitized,
            key = sanitized,
            label = zoneName or sanitized,
        }
    end

    return nil
end

function MapData:GetZoneKey(zoneId, zoneName)
    local zone = self:GetZone(zoneId, zoneName)
    return zone and zone.key or nil
end

function MapData:GetZoneLabel(zoneId, zoneName)
    local zone = self:GetZone(zoneId, zoneName)
    return zone and zone.label or zoneName
end

function MapData:GetTileTexture(zoneId, zoneName, index)
    local zone = self:GetZone(zoneId, zoneName)
    if not zone or not zone.file then
        return nil
    end

    return string.format("Interface\\WorldMap\\%s\\%s%d", zone.file, zone.texture or zone.file, index)
end
