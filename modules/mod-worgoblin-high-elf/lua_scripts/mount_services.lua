-- Service passengers on retail utility mounts (Grand Expedition Yak, Brutosaurs, ...).
-- Each entry lists the windows its gossip offers; creature_template.npcflag must carry the matching flags,
-- because the core checks them again on every vendor, repair, auction, mail and bank request.
local SERVICES = {
    [4600001] = {"vendor"},                    -- vendor and repair: Grand Expedition Yak
    [4600024] = {"vendor"},                    -- Grizzly Hills Packmaster's anvil
    [4600004] = {"auction", "vendor"},         -- Mighty Caravan Brutosaur
    [4600005] = {"auction", "mail"},           -- Trader's Gilded Brutosaur
    [4600006] = {"auction", "vendor", "mail"}, -- Sporebearer Fungal Strider
    [4600007] = {"vendor", "mail"},            -- Hearthkeeper's Wandering Caravan
}

local LABELS = {
    vendor  = {1, "Let me browse your goods."},
    auction = {0, "I'd like to visit the auction house."},
    mail    = {0, "Check my mail."},
    bank    = {0, "I'd like to visit my bank."},
}

local function Open(player, creature, service)
    if service == "vendor" then player:SendListInventory(creature)
    elseif service == "auction" then player:SendAuctionMenu(creature)
    elseif service == "mail" then player:SendShowMailBox(creature:GetGUID())
    elseif service == "bank" then player:SendShowBank(creature) end
end

local function OnHello(event, player, creature)
    local services = SERVICES[creature:GetEntry()]
    if #services == 1 then
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

-- Scripts load before creature templates, and registering an unknown entry fails, so wait for world startup (14).
RegisterServerEvent(14, function()
    for entry in pairs(SERVICES) do
        RegisterCreatureGossipEvent(entry, 1, OnHello)
        RegisterCreatureGossipEvent(entry, 2, OnSelect)
    end
end)
