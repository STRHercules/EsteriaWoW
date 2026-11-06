Battlemon = Battlemon or {}

function Battlemon.CalcHP(base, level)
    base = tonumber(base) or 1
    level = tonumber(level) or 1
    return math.floor((2 * base + 31) * level / 100) + level + 10
end

function Battlemon.CalcStat(base, level)
    base = tonumber(base) or 1
    level = tonumber(level) or 1
    return math.floor((2 * base + 31) * level / 100) + 5
end

function Battlemon.CreateBattler(speciesId, level, gender)
    local s = Battlemon.Species[speciesId]
    if not s then
        return nil
    end
    level = Battlemon.Clamp(tonumber(level) or 1, 1, 100)
    local hp = Battlemon.CalcHP(s.hp, level)
    local battler = {
        speciesId = speciesId,
        species = s,
        name = s.name,
        level = level,
        gender = gender or Battlemon.RollGender(s.gender_ratio),
        hp = hp,
        maxhp = hp,
        atk = Battlemon.CalcStat(s.atk, level),
        def = Battlemon.CalcStat(s.def, level),
        spa = Battlemon.CalcStat(s.spa, level),
        spd = Battlemon.CalcStat(s.spd, level),
        spe = Battlemon.CalcStat(s.spe, level),
        type1 = s.type1,
        type2 = (s.type2 ~= "" and s.type2) or nil,
        moves = {},
        fainted = false,
        sprite = s.sprite,
    }
    local internals = Battlemon.PickMoves(speciesId, level)
    for i = 1, #internals do
        local mv = Battlemon.MovesByInternal[internals[i]]
        if mv then
            local pp = tonumber(mv.pp) or 5
            table.insert(battler.moves, { data = mv, pp = pp, maxpp = pp })
        end
    end
    if #battler.moves == 0 then
        local tackle = Battlemon.MovesByInternal["TACKLE"]
        if tackle then
            table.insert(battler.moves, { data = tackle, pp = tackle.pp, maxpp = tackle.pp })
        end
    end
    return battler
end

function Battlemon.CalcDamage(attacker, defender, move)
    local power = tonumber(move.power) or 0
    local category = move.move_category
    if category == "Status" or power <= 0 then
        return 0, 1, false
    end
    local atk, def
    if category == "Physical" then
        atk = attacker.atk
        def = defender.def
    else
        atk = attacker.spa
        def = defender.spd
    end
    if def < 1 then def = 1 end
    local dmg = math.floor(math.floor(math.floor(2 * attacker.level / 5 + 2) * power * atk / def) / 50) + 2
    if move.type == attacker.type1 or move.type == attacker.type2 then
        dmg = math.floor(dmg * 1.5)
    end
    local eff = Battlemon.Effectiveness(move.type, defender.type1, defender.type2)
    dmg = math.floor(dmg * eff)
    local crit = math.random(1, 16) == 1
    if crit then
        dmg = math.floor(dmg * 1.5)
    end
    dmg = math.floor(dmg * (85 + math.random(0, 15)) / 100)
    if dmg < 1 and eff > 0 then
        dmg = 1
    end
    return dmg, eff, crit
end

function Battlemon.MoveHits(move)
    local acc = tonumber(move.accuracy)
    if not acc or acc <= 0 then
        return true
    end
    return math.random(1, 100) <= acc
end
