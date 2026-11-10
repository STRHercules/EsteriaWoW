-- Service passengers on retail utility mounts (Grand Expedition Yak, Brutosaurs, ...).
-- Each entry lists the windows its gossip offers; creature_template.npcflag must carry the matching flags,
-- because the core checks them again on every vendor, repair, auction, mail and bank request.
local SERVICES = {
    [4600001] = {"vendor"},                    -- vendor and repair: Grand Expedition Yak
    [4600002] = {"auction"},                   -- Brutosaurs' auctioneer
    [4600003] = {"vendor"},                    -- Mighty Caravan Brutosaur's merchant
    [4600008] = {"mail"},                      -- Trader's Gilded Brutosaur's postmaster
    [4600024] = {"vendor"},                    -- Grizzly Hills Packmaster's anvil
    [4600004] = {"auction", "vendor"},         -- Mighty Caravan Brutosaur
    [4600005] = {"auction", "mail"},           -- Trader's Gilded Brutosaur
    [4600006] = {"auction", "vendor", "mail"}, -- Sporebearer Fungal Strider
    [4600007] = {"vendor", "mail"},            -- Hearthkeeper's Wandering Caravan
    [4600010] = {"transmog"},                  -- Grand Expedition Yak's Mystic Birdhat
    [4600025] = {"transmog"},                  -- Grizzly Hills Packmaster's satchel
}

local LABELS = {
    vendor  = {1, "Let me browse your goods."},
    auction = {0, "I'd like to visit the auction house."},
    mail    = {0, "Check my mail."},
    bank    = {0, "I'd like to visit my bank."},
    transmog = {0, "I'd like to transmogrify my gear."},
}
-- mod-transmog hides its scripted transmogrifier from everyone but a summon's owner, and a mount passenger has no
-- owner, so transmog passengers call up the module's own portable transmogrifier (its PetSpellId) instead.
local PORTABLE_TRANSMOG_SPELL = 200100

local function Open(player, creature, service)
    if service == "vendor" then player:SendListInventory(creature)
    elseif service == "auction" then player:SendAuctionMenu(creature)
    elseif service == "mail" then player:SendShowMailBox(creature:GetGUID())
    elseif service == "bank" then player:SendShowBank(creature)
    elseif service == "transmog" then player:CastSpell(player, PORTABLE_TRANSMOG_SPELL, true) end
end

local function OnHello(event, player, creature)
    local services = SERVICES[creature:GetEntry()]
    if #services == 1 and (services[1] == "vendor" or services[1] == "auction") then
        Open(player, creature, services[1])
        return true
    end
    player:GossipClearMenu()
    for index, service in ipairs(services) do
        player:GossipMenuAddItem(LABELS[service][1], LABELS[service][2], 0, index)
    end
    player:GossipSendMenu(1, creature)
    return true
end

local function OnSelect(event, player, creature, sender, action)
    player:GossipComplete()
    Open(player, creature, SERVICES[creature:GetEntry()][action])
end

-- Every passenger the utility mounts carry (service NPCs and the Yak's sidecars and stalls). Retail removes them with
-- the mount; the core instead lets an accessory jump down to the ground and unsummons it 2 s later, so despawn it as
-- soon as it leaves its seat. 4600010/4600025 keep mod-transmog's C++ AI, so they still take the 2 s exit.
local PASSENGERS = {4600001, 4600002, 4600003, 4600008, 4600004, 4600005, 4600006, 4600007, 4600010, 4600020, 4600021, 4600022, 4600023,
                    4600024, 4600025}
local seated = {}

local function OnUpdate(event, creature, diff)
    local key = creature:GetGUIDLow()
    if creature:IsOnVehicle() then
        seated[key] = true
    elseif seated[key] then  -- seen seated before, so it is leaving rather than still boarding
        seated[key] = nil
        creature:DespawnOrUnsummon(0)
    end
end

-- Scripts load before creature templates, and registering an unknown entry fails, so wait for world startup (14).
RegisterServerEvent(14, function()
    for entry in pairs(SERVICES) do
        RegisterCreatureGossipEvent(entry, 1, OnHello)
        RegisterCreatureGossipEvent(entry, 2, OnSelect)
    end
    for _, entry in ipairs(PASSENGERS) do
        RegisterCreatureEvent(entry, 7, OnUpdate)  -- CREATURE_EVENT_ON_AIUPDATE
    end
end)
