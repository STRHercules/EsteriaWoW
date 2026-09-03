--[[
    Worgen "Running Wild" speed-spell teacher
    ------------------------------------------
    Fires whenever a player casts/learns a native riding spell, or logs in.
    Teaches the correctly-gendered custom speed spell for their tier, and
    removes the wrong tier if they have it.

    Native riding spells (static WotLK content, do not change per-core):
        33388 = Apprentice Riding   (75 skill,  60% speed)
        33391 = Journeyman Riding   (150 skill, 100% speed)

    Death Knights start with 150 riding skill at creation, but the engine
    only ever casts 33388 on them (never 33391). We do NOT try to fix that
    on the native-spell side anymore -- any LearnSpell/CastSpell of 33391
    triggers the engine's own rank-supersede logic and strips 33388 from
    the spellbook, which then falsely shows Apprentice Riding as
    purchasable at trainers. Instead we leave native riding spells alone
    entirely and just directly grant DKs the Journeyman-tier CUSTOM speed
    spell, since they already have full 150 skill regardless of what the
    trainer UI shows.
]]

local RACE_WORGEN = 12
local CLASS_DEATH_KNIGHT = 6

local RIDE_APPRENTICE_SPELL = 33388
local RIDE_JOURNEYMAN_SPELL = 33391

local WORGEN_APPRENTICE_MALE   = 87840
local WORGEN_APPRENTICE_FEMALE = 87841
local WORGEN_JOURNEYMAN_MALE   = 110010
local WORGEN_JOURNEYMAN_FEMALE = 110011

local DARKFLIGHT_SPELL_ID = 68992

-- Replace these with your actual spell IDs
local TWO_FORMS_HUMAN_MALE      = 68996  -- placeholder
local TWO_FORMS_HUMAN_FEMALE    = 68995  -- placeholder
local PRE_WORGEN_HUMAN_MALE     = 68994  -- placeholder
local PRE_WORGEN_HUMAN_FEMALE   = 110020  -- placeholder

local WORGEN_HUMAN_AURAS = {
    TWO_FORMS_HUMAN_MALE,
    TWO_FORMS_HUMAN_FEMALE,
    PRE_WORGEN_HUMAN_MALE,
    PRE_WORGEN_HUMAN_FEMALE
}

local function OnSpellCast(event, player, spell, skipCheck)
    if spell:GetEntry() == DARKFLIGHT_SPELL_ID then
        for _, auraId in ipairs(WORGEN_HUMAN_AURAS) do
            if player:HasAura(auraId) then
                player:RemoveAura(auraId)
            end
        end
    end
end

RegisterPlayerEvent(5, OnSpellCast) -- PLAYER_EVENT_ON_SPELL_CAST

-- GENDER_MALE = 0, GENDER_FEMALE = 1 (standard Eluna/DBC convention)
local function GetGenderedSpells(player)
    local isMale = (player:GetGender() == 0)
    return {
        apprentice = isMale and WORGEN_APPRENTICE_MALE or WORGEN_APPRENTICE_FEMALE,
        journeyman = isMale and WORGEN_JOURNEYMAN_MALE or WORGEN_JOURNEYMAN_FEMALE,
    }
end

-- What custom RW tier SHOULD this player have right now?
-- DKs always target journeyman directly, bypassing native spell state.
-- Everyone else follows whichever native riding spell they've trained.
local function GetTargetTier(player)
    if player:GetClass() == CLASS_DEATH_KNIGHT then
        return "journeyman"
    end
    if player:HasSpell(RIDE_JOURNEYMAN_SPELL) then
        return "journeyman"
    elseif player:HasSpell(RIDE_APPRENTICE_SPELL) then
        return "apprentice"
    end
    return nil -- hasn't trained any riding yet, nothing to do
end

-- Bring the player's custom Running Wild spell in line with their target
-- tier. Only calls RemoveSpell/LearnSpell if something is actually wrong;
-- if they already have exactly the right spell and nothing else, this is
-- a complete no-op. That single up-front check is what stops any
-- remove/re-add flicker on repeat logins.
local function SyncRunningWild(player)
    if player:GetRace() ~= RACE_WORGEN then
        return
    end

    local targetTier = GetTargetTier(player)
    if not targetTier then
        return
    end

    local spells = GetGenderedSpells(player)
    local otherTier = (targetTier == "journeyman") and "apprentice" or "journeyman"
    local wantSpell  = spells[targetTier]
    local otherSpell = spells[otherTier]

    local hasWant  = player:HasSpell(wantSpell)
    local hasOther = player:HasSpell(otherSpell)

    if hasWant and not hasOther then
        return -- already exactly correct, do nothing
    end

    if hasOther then
        player:RemoveSpell(otherSpell)
    end

    if not hasWant then
        player:RegisterEvent(function(eventId, delay, repeats, plr)
            if plr and plr:IsInWorld() and not plr:HasSpell(wantSpell) then
                plr:LearnSpell(wantSpell)
            end
        end, 250, 1)
    end
end

local function OnLearnSpell(event, player, spellId)
    if spellId == RIDE_APPRENTICE_SPELL or spellId == RIDE_JOURNEYMAN_SPELL then
        SyncRunningWild(player)
    end
end

-- Hook the actual spell CAST (training) rather than relying solely on
-- PLAYER_EVENT_ON_LEARN_SPELL, which doesn't fire reliably for Journeyman
-- Riding's auto-grant path.
local function OnCastRidingSpell(event, caster, spell, skipCheck)
    local player = caster
    if player.ToPlayer then
        player = caster:ToPlayer()
    end
    if player then
        SyncRunningWild(player)
    end
end

RegisterSpellEvent(RIDE_APPRENTICE_SPELL, 2, OnCastRidingSpell) -- SPELL_EVENT_ON_CAST
RegisterSpellEvent(RIDE_JOURNEYMAN_SPELL, 2, OnCastRidingSpell) -- SPELL_EVENT_ON_CAST

-- Safety net + DK handling: re-sync on every login. Thanks to the
-- early-return guard in SyncRunningWild, this is a true no-op for anyone
-- who's already correct, so it's safe to run unconditionally every time.
local function OnLogin(event, player)
    SyncRunningWild(player)
end

RegisterPlayerEvent(44, OnLearnSpell) -- PLAYER_EVENT_ON_LEARN_SPELL
RegisterPlayerEvent(3, OnLogin)       -- PLAYER_EVENT_ON_LOGIN