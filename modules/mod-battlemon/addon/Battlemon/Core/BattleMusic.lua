Battlemon = Battlemon or {}

local BM = {}
Battlemon.BattleMusic = BM

local MUSIC_DIR = "Interface\\AddOns\\Battlemon\\Music\\"

-- Track registry -- add more themes by dropping an .mp3/.ogg into the Music\ folder and adding one
-- line here. WoW addons have no API to list their own folder's contents, so this is the one thing
-- that can't be automatic. PlayMusic loops a track on its own for as long as nothing stops or
-- replaces it (the same mechanism zone/dungeon music uses -- confirmed against DBM's dungeon BGM in
-- this same client, which calls PlayMusic exactly once despite a dungeon far outlasting one track),
-- so no track duration or manual re-trigger timer is needed here.
BM.tracks = {
    {
        key = "vswild",
        name = "Battle (Vs. Wild Pokémon)",
        file = "01 - GBA - Battle Vs. Wild Pokemon.mp3",
    },
}

local restoreMusicCvar -- nil = we didn't touch the CVar; otherwise the value to put back
local currentTrack

local function trackByKey(key)
    for _, t in ipairs(BM.tracks) do
        if t.key == key then
            return t
        end
    end
    return nil
end

local function pickTrack()
    local theme = BM.GetTheme()
    if theme ~= "random" then
        local t = trackByKey(theme)
        if t then
            return t
        end
    end
    if #BM.tracks == 0 then
        return nil
    end
    return BM.tracks[math.random(#BM.tracks)]
end

-- Safe to call repeatedly; only the first call while a battle's music is already playing does
-- anything, so callers don't need to track whether they already started it.
function BM.Start()
    if currentTrack then
        return
    end
    local track = pickTrack()
    if not track then
        return
    end

    -- PlayMusic is silent if the player has in-game Music turned off. Force it on for the fight
    -- and put their setting back exactly as DBM does for dungeon/raid music, so this doesn't
    -- permanently change a preference the player set on purpose.
    local enabled = tonumber(GetCVar("Sound_EnableMusic")) or 1
    if enabled == 0 then
        restoreMusicCvar = 0
        SetCVar("Sound_EnableMusic", 1)
    end

    currentTrack = track
    PlayMusic(MUSIC_DIR .. track.file)
end

function BM.Stop()
    if not currentTrack then
        return
    end
    StopMusic()
    currentTrack = nil
    if restoreMusicCvar ~= nil then
        SetCVar("Sound_EnableMusic", restoreMusicCvar)
        restoreMusicCvar = nil
    end
end

-- key is a track key from BM.tracks, or "random". Persisted across sessions.
function BM.SetTheme(key)
    if key ~= "random" and not trackByKey(key) then
        return false
    end
    Battlemon.EnsureProfileDB()
    BattlemonDB.battleMusicTheme = key
    return true
end

function BM.GetTheme()
    Battlemon.EnsureProfileDB()
    return BattlemonDB.battleMusicTheme or "random"
end
