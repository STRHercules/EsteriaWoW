Battlemon = Battlemon or {}

-- Total EXP required to reach a given level (0 at level 1).
-- Curves match Pokémon Essentials / main-series growth rates.
function Battlemon.ExpAtLevel(growth, level)
    level = tonumber(level) or 1
    if level <= 1 then
        return 0
    end
    if level > 100 then
        level = 100
    end
    local n = level
    local n3 = n * n * n
    growth = growth or "Medium"

    if growth == "Fast" then
        return math.floor(n3 * 4 / 5)
    elseif growth == "Slow" then
        return math.floor(n3 * 5 / 4)
    elseif growth == "Parabolic" or growth == "MediumSlow" then
        local v = math.floor(n3 * 6 / 5) - 15 * n * n + 100 * n - 140
        if v < 0 then
            return 0
        end
        return v
    elseif growth == "Erratic" then
        if n < 50 then
            return math.floor(n3 * (100 - n) / 50)
        elseif n < 68 then
            return math.floor(n3 * (150 - n) / 100)
        elseif n < 98 then
            return math.floor(n3 * math.floor((1911 - 10 * n) / 3) / 500)
        end
        return math.floor(n3 * (160 - n) / 100)
    elseif growth == "Fluctuating" then
        if n < 15 then
            return math.floor(n3 * ((math.floor((n + 1) / 3) + 24) / 50))
        elseif n < 36 then
            return math.floor(n3 * ((n + 14) / 50))
        end
        return math.floor(n3 * ((math.floor(n / 2) + 32) / 50))
    end
    -- Medium / MediumFast
    return n3
end

function Battlemon.ExpToNext(growth, level, currentExp)
    if (tonumber(level) or 1) >= 100 then
        return 0
    end
    local need = Battlemon.ExpAtLevel(growth, level + 1)
    local have = tonumber(currentExp) or 0
    local remain = need - have
    if remain < 0 then
        return 0
    end
    return remain
end

function Battlemon.ExpYield(enemy)
    local base = tonumber(enemy.species and enemy.species.base_exp) or 64
    local level = tonumber(enemy.level) or 1
    local n = math.floor(base * level / 7)
    if n < 1 then
        n = 1
    end
    return n
end

function Battlemon.AddExp(save, amount)
    if not save then
        return {}
    end
    local species = Battlemon.Species[save.speciesId]
    local growth = species and species.growth_rate or "Medium"
    save.exp = (tonumber(save.exp) or 0) + (tonumber(amount) or 0)
    local gained = {}
    while save.level < 100 do
        local need = Battlemon.ExpAtLevel(growth, save.level + 1)
        if save.exp >= need then
            save.level = save.level + 1
            table.insert(gained, save.level)
        else
            break
        end
    end
    return gained
end

function Battlemon.ApplyLevelStats(battler)
    local s = battler.species
    local oldMax = battler.maxhp
    battler.maxhp = Battlemon.CalcHP(s.hp, battler.level)
    battler.atk = Battlemon.CalcStat(s.atk, battler.level)
    battler.def = Battlemon.CalcStat(s.def, battler.level)
    battler.spa = Battlemon.CalcStat(s.spa, battler.level)
    battler.spd = Battlemon.CalcStat(s.spd, battler.level)
    battler.spe = Battlemon.CalcStat(s.spe, battler.level)
    local delta = battler.maxhp - (oldMax or battler.maxhp)
    battler.hp = Battlemon.Clamp((battler.hp or battler.maxhp) + delta, 1, battler.maxhp)
    battler.fainted = battler.hp <= 0
end

function Battlemon.TryLearnMoves(battler, newLevel)
    local messages = {}
    local list = Battlemon.Learnsets[battler.speciesId] or {}
    for i = 1, #list do
        local e = list[i]
        if e.level == newLevel then
            local mv = Battlemon.MovesByInternal[e.move_internal_name]
            if mv then
                local known = false
                for j = 1, #battler.moves do
                    if battler.moves[j].data.internal_name == mv.internal_name then
                        known = true
                        break
                    end
                end
                if not known and #battler.moves < 4 then
                    local pp = tonumber(mv.pp) or 5
                    table.insert(battler.moves, { data = mv, pp = pp, maxpp = pp })
                    table.insert(messages, battler.name .. " learned " .. mv.name .. "!")
                end
            end
        end
    end
    return messages
end
