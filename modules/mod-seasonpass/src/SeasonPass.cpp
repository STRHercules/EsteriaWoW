/*
 * mod-seasonpass v4 — Kern: Punkte, zwei KOSTENLOSE Belohnungspfade,
 * Zufallskisten (kuratierter 100er-Beutepool mit Raritäten und Kistenfieber-Pity),
 * Wochen-Mutatoren, Traumsturm, Saison-Erbe (Prestige-Bonus), Login-Serien,
 * wählbares XP-Tempo, Levelkisten, Bonus-Wochenende, Sprache DE/EN pro
 * Charakter, NPC, Befehle.
 */

#include "SeasonPass.h"

#include "ScriptMgr.h"
#include "Player.h"
#include "Creature.h"
#include "Chat.h"
#include "Config.h"
#include "DatabaseEnv.h"
#include "ScriptedGossip.h"
#include "GameTime.h"
#include "World.h"
#include "ObjectMgr.h"
#include "ItemTemplate.h"
#include "SharedDefines.h"
#include "SpellInfo.h"
#include "WorldSessionMgr.h"

#include <algorithm>
#include <ctime>
#include <limits>
#include <unordered_map>
#include <vector>
#include <sstream>

using SeasonPass::T;

namespace
{
    enum BPRewardType : uint8
    {
        BP_REWARD_ITEM  = 0,
        BP_REWARD_GOLD  = 1,
        BP_REWARD_TITLE = 2,
        BP_REWARD_CHEST = 3 // id = Kistenstufe 1-3
    };

    enum BPTrack : uint8
    {
        BP_TRACK_FREE = 0,
        BP_TRACK_EPIC = 1
    };

    struct BPReward
    {
        uint8       track     = BP_TRACK_FREE;
        uint32      classmask = 0;
        uint8       type      = BP_REWARD_GOLD;
        uint32      id        = 0;
        uint32      count     = 1;
        std::string name;
        std::string nameEn;
    };

    struct BPShopEntry
    {
        uint8  kind  = 0; // 0=Item, 1=Mystery-Box (item = Kistenstufe)
        uint32 item  = 0;
        uint32 count = 1;
        uint32 price = 10000;
    };

    struct BPSupply
    {
        uint32 item   = 0;
        uint32 count  = 20;
        uint32 points = 150;
        uint32 gold   = 10000;
    };

    struct BPFish
    {
        uint32 item   = 0;
        uint32 count  = 10;
        uint32 points = 150;
        uint32 gold   = 10000;
    };

    struct BPMutator
    {
        uint8       kind  = 0;
        uint32      value = 200;
        std::string name;
        std::string nameEn;
    };

    struct BPData
    {
        uint32 season       = 0;
        uint32 points       = 0;
        uint32 claimedTier  = 0;
        uint32 claimedEpic  = 0;
        uint32 lastDailyDay = 0;
        uint32 streak       = 0;
        uint32 prestige     = 0;
        uint32 xpRate       = 100;
        uint8  lang         = 0;  // 0=Deutsch, 1=Englisch
        uint32 chestPity    = 0;  // Kistenfieber
        bool   welcomed     = false; // Willkommenspaket (Stufe 0) schon erhalten?
        uint8  hardcore     = 0;  // 0=aus, 1=aktiv, 2=gescheitert, 3=geschafft
        uint32 supplyDay    = 0;  // letzter erledigter Versorgungsauftrag (Tag)
        uint32 startRune    = 0;  // gewählte Startfähigkeit (Fähigkeits-Rune)
        uint32 fishDay      = 0;  // Tag des laufenden Angelauftrags
        uint32 fishCount    = 0;  // heutige Fänge
        uint32 renown       = 0;
        uint32 renownPoints = 0;
        bool   loaded       = false;
        bool   isBot        = false;
        std::unordered_map<ObjectGuid::LowType, uint32> pvpVictims;
    };

    // Konfiguration
    bool   g_enabled          = true;
    uint32 g_season           = 1;
    uint32 g_pointsPerTier    = 100;
    uint32 g_maxTier          = 100;
    uint32 g_ptsQuest         = 10;
    uint32 g_ptsKill          = 1;
    uint32 g_ptsElite         = 5;
    uint32 g_ptsBoss          = 100;
    uint32 g_ptsRare          = 25;
    uint32 g_ptsLevel         = 50;
    uint32 g_ptsDaily         = 50;
    uint32 g_ptsPvP           = 10;
    uint32 g_ptsDuel          = 5;
    uint32 g_pvpCooldown      = 300;
    uint32 g_streakBonus      = 5;
    bool   g_announce         = true;
    bool   g_announceRare     = true;
    bool   g_ignoreBots       = true;
    bool   g_weekendEnable    = true;
    uint32 g_weekendPoints    = 200;
    uint32 g_weekendXP        = 150;
    uint32 g_zoneEventMult    = 200;
    bool   g_chestEnable      = true;
    uint32 g_chestKillPct     = 2;
    uint32 g_chestElitePct    = 10;
    uint32 g_chestBossPct     = 100;
    uint32 g_chestLegPct      = 10;   // Chance auf legendaere statt epische Kiste beim Boss
    uint32 g_chestEpicBase    = 15;   // Basis-Epicchance pro Kistenitem (Stufe 1)
    uint32 g_chestPityStep    = 5;    // +X% Epicchance pro Kiste ohne Episches
    bool   g_stormEnable      = true;
    uint32 g_stormPoints      = 300;
    uint32 g_legacyPct        = 2;    // +X% Punkte pro Prestige (Saison-Erbe)
    bool   g_mutatorEnable    = true;
    bool   g_lvlChestEnable   = true;
    uint32 g_chestGoldPer10   = 50000;
    uint32 g_chestBagItem     = 21841;
    bool   g_internalPrestigeEnable = false;
    bool   g_internalParagonEnable = false;
    bool   g_prestigeMobScalingEnable = false;
    bool   g_prestigeEnable   = false;
    std::vector<std::string> g_botPrefixes;

    // ------------------- Traumschmiede (Paragon, Diablo-Stil) -------------------
    // Jedes Prestige (bis g_prestigeMax) gibt 1 frei verteilbaren Punkt.
    // Werte: 1 Macht (Nahkampf) 2 Zauberkunst 3 Flächenwirkung 4 Toxine (DoTs)
    //        5 Vitalität (Leben) 6 Seelenkraft (Mana) 7 Heilkunst 8 Weisheit (XP)
    // Gegner skalieren pro Prestige mit (+Schaden, +effektives Leben).
    uint32 g_prestigeMax      = 300;
    uint32 g_prestigeGoldBase = 500000;   // 50 G Grundbelohnung je Prestige
    uint32 g_prestigeGoldPer  = 100000;   // +10 G je bereits erreichtem Prestige
    uint32 g_prestigeXPPct    = 3;        // +3% Erfahrung je Prestige (schneller neu leveln)
    uint32 g_prestigeAutoGold = 100000;   // 10 G je Auto-Prestige im Prestige-Modus
    uint32 g_paragonCap       = 75;       // maximale Punkte je Wert
    uint32 g_paragonPtsPer    = 2;        // Traumschmiede-Punkte je Prestige
    uint32 g_mobScalePct      = 1;        // Gegner: +1% Schaden und eff. Leben je Prestige
    uint32 g_runeResonance    = 2;        // Runenresonanz: +2% Schaden/Leben/Heilung je Dauerbuff-Rune

    uint32 const PG_STATS = 8;
    uint32 const PG_PER[9] = { 0, 1, 1, 2, 2, 1, 1, 1, 1 }; // +% je Punkt

    struct BPParagon
    {
        bool loaded = false;
        uint32 pts[9] = {};
    };
    std::unordered_map<ObjectGuid::LowType, BPParagon> g_paragon;

    // Kuratierter Kisten-Beutepool (v5): pro Kiste 1-3 gewichtete Eintraege in 4 Raritaeten
    struct BPChestLoot
    {
        uint8  rarity = 1;   // 1=Haeufig 2=Selten 3=Episch 4=Legendaer
        uint8  kind   = 0;   // 0=Item, 1=Gold (id=Kupfer), 2=Verlorene Rune
        uint32 id     = 0;
        uint32 count  = 1;
        uint32 weight = 10;
        std::string name, nameEn;
    };

    std::unordered_map<uint32, std::vector<BPReward>> g_rewards;
    std::vector<BPChestLoot> g_chestLoot[4]; // Index = Kistenstufe 1-3
    uint32 g_chestRarity[4][5] = {};         // [Kiste][Raritaet] = Promille
    std::vector<BPShopEntry> g_shop; // Sortiment der Saisonhändlerin (.bp buy)
    std::vector<BPSupply>    g_supplies; // Versorgungsauftraege (SoD Waylaid Supplies)
    std::vector<BPFish>      g_fish;     // Angelauftraege (taeglich rotierender Fisch)
    std::vector<BPMutator> g_mutators;
    std::unordered_map<ObjectGuid::LowType, BPData> g_cache;

    bool g_stormWasActive = false;

    void GrantTier(Player* player, uint32 tier, uint8 track); // weiter unten definiert

    uint32 NowSecs()    { return static_cast<uint32>(GameTime::GetGameTime().count()); }
    uint32 CurrentDay() { return NowSecs() / 86400; }

    bool IsWeekend()
    {
        if (!g_weekendEnable)
            return false;
        time_t t = static_cast<time_t>(NowSecs());
        std::tm lt{};
        localtime_r(&t, &lt);
        return lt.tm_wday == 0 || lt.tm_wday == 6;
    }

    uint32 TierFromPoints(uint32 points)
    {
        uint32 tier = points / g_pointsPerTier;
        return tier > g_maxTier ? g_maxTier : tier;
    }

    BPMutator const* Mutator()
    {
        if (!g_mutatorEnable || g_mutators.empty())
            return nullptr;
        uint32 week = NowSecs() / (86400 * 7);
        return &g_mutators[week % g_mutators.size()];
    }

    uint32 MutatorMult(uint8 kind)
    {
        BPMutator const* m = Mutator();
        return (m && m->kind == kind) ? m->value : 100;
    }

    void LoadCoreTables()
    {
        g_rewards.clear();
        uint32 n = 0;
        if (QueryResult result = WorldDatabase.Query(
                "SELECT tier, track, classmask, type, id, count, name, name_en FROM seasonpass_rewards WHERE season = {}", g_season))
        {
            do
            {
                Field* f = result->Fetch();
                uint32 tier = f[0].Get<uint16>();
                BPReward r;
                r.track     = f[1].Get<uint8>();
                r.classmask = f[2].Get<uint32>();
                r.type      = f[3].Get<uint8>();
                r.id        = f[4].Get<uint32>();
                r.count     = f[5].Get<uint32>();
                r.name      = f[6].Get<std::string>();
                r.nameEn    = f[7].Get<std::string>();
                g_rewards[tier].push_back(std::move(r));
                ++n;
            } while (result->NextRow());
        }

        for (auto& v : g_chestLoot)
            v.clear();
        uint32 nLoot = 0;
        if (QueryResult result = WorldDatabase.Query(
            "SELECT `chest`, `rarity`, `kind`, `id`, `count`, `weight`, `name`, `name_en` FROM seasonpass_chest_loot"))
        {
            do
            {
                Field* f = result->Fetch();
                uint8 chest = f[0].Get<uint8>();
                if (chest < 1 || chest > 3)
                    continue;
                BPChestLoot e;
                e.rarity = f[1].Get<uint8>();
                e.kind   = f[2].Get<uint8>();
                e.id     = f[3].Get<uint32>();
                e.count  = std::max<uint32>(1, f[4].Get<uint32>());
                e.weight = std::max<uint32>(1, f[5].Get<uint32>());
                e.name   = f[6].Get<std::string>();
                e.nameEn = f[7].Get<std::string>();
                g_chestLoot[chest].push_back(std::move(e));
                ++nLoot;
            } while (result->NextRow());
        }
        if (QueryResult result = WorldDatabase.Query("SELECT `chest`, `rarity`, `chance` FROM seasonpass_chest_rarity"))
        {
            do
            {
                Field* f = result->Fetch();
                uint8 c = f[0].Get<uint8>();
                uint8 r = f[1].Get<uint8>();
                if (c <= 3 && r >= 1 && r <= 4) // Zeile 0 = Aufwertungs-Chancen der Traumkiste
                    g_chestRarity[c][r] = f[2].Get<uint32>();
            } while (result->NextRow());
        }

        g_shop.clear();
        if (QueryResult result = WorldDatabase.Query("SELECT kind, item, count, price FROM seasonpass_shop ORDER BY slot"))
        {
            do
            {
                Field* f = result->Fetch();
                BPShopEntry e;
                e.kind  = f[0].Get<uint8>();
                e.item  = f[1].Get<uint32>();
                e.count = f[2].Get<uint32>();
                e.price = f[3].Get<uint32>();
                g_shop.push_back(e);
            } while (result->NextRow());
        }

        g_supplies.clear();
        if (QueryResult result = WorldDatabase.Query("SELECT item, count, points, gold FROM seasonpass_supplies ORDER BY id"))
        {
            do
            {
                Field* f = result->Fetch();
                BPSupply s;
                s.item   = f[0].Get<uint32>();
                s.count  = f[1].Get<uint32>();
                s.points = f[2].Get<uint32>();
                s.gold   = f[3].Get<uint32>();
                g_supplies.push_back(s);
            } while (result->NextRow());
        }

        g_fish.clear();
        if (QueryResult result = WorldDatabase.Query("SELECT item, count, points, gold FROM seasonpass_fish ORDER BY id"))
        {
            do
            {
                Field* f = result->Fetch();
                BPFish fi;
                fi.item   = f[0].Get<uint32>();
                fi.count  = f[1].Get<uint32>();
                fi.points = f[2].Get<uint32>();
                fi.gold   = f[3].Get<uint32>();
                g_fish.push_back(fi);
            } while (result->NextRow());
        }

        g_mutators.clear();
        if (QueryResult result = WorldDatabase.Query("SELECT kind, value, name, name_en FROM seasonpass_mutators ORDER BY id"))
        {
            do
            {
                Field* f = result->Fetch();
                BPMutator m;
                m.kind   = f[0].Get<uint8>();
                m.value  = f[1].Get<uint32>();
                m.name   = f[2].Get<std::string>();
                m.nameEn = f[3].Get<std::string>();
                g_mutators.push_back(std::move(m));
            } while (result->NextRow());
        }

        LOG_INFO("module", "[SeasonPass] {} Belohnungen, {} Kisten-Eintraege, {} Mutatoren geladen (Saison {}).",
            n, nLoot, g_mutators.size(), g_season);
    }

    void SaveData(Player* player, BPData const& d)
    {
        CharacterDatabase.Execute(
            "REPLACE INTO character_seasonpass (guid, season, points, claimed_tier, claimed_epic, last_daily, streak, prestige, xprate, lang, chest_pity, welcomed, hardcore, supply_day, start_rune, "
            "fish_day, fish_count, renown, renown_points) "
            "VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})",
            player->GetGUID().GetCounter(), d.season, d.points, d.claimedTier, d.claimedEpic,
            d.lastDailyDay, d.streak, d.prestige, d.xpRate, d.lang, d.chestPity, d.welcomed ? 1 : 0,
            d.hardcore, d.supplyDay, d.startRune, d.fishDay, d.fishCount, d.renown, d.renownPoints);
    }

    BPData& GetData(Player* player)
    {
        BPData& d = g_cache[player->GetGUID().GetCounter()];
        if (d.loaded && d.season != g_season)
        {
            SaveData(player, d);
            bool isBot = d.isBot;
            d = BPData{};
            d.isBot = isBot;
        }
        if (!d.loaded)
        {
            d.season = g_season;
            if (QueryResult result = CharacterDatabase.Query(
                    "SELECT points, claimed_tier, claimed_epic, last_daily, streak, prestige, xprate, lang, chest_pity, welcomed, hardcore, supply_day, start_rune, "
                    "fish_day, fish_count, renown, renown_points "
                    "FROM character_seasonpass WHERE guid = {} AND season = {}",
                    player->GetGUID().GetCounter(), g_season))
            {
                Field* f = result->Fetch();
                d.points       = f[0].Get<uint32>();
                d.claimedTier  = f[1].Get<uint32>();
                d.claimedEpic  = f[2].Get<uint32>();
                d.lastDailyDay = f[3].Get<uint32>();
                d.streak       = f[4].Get<uint32>();
                d.prestige     = f[5].Get<uint32>();
                d.xpRate       = f[6].Get<uint32>();
                d.lang         = f[7].Get<uint8>();
                d.chestPity    = f[8].Get<uint32>();
                d.welcomed     = f[9].Get<uint8>() != 0;
                d.hardcore     = f[10].Get<uint8>();
                d.supplyDay    = f[11].Get<uint32>();
                d.startRune    = f[12].Get<uint32>();
                d.fishDay      = f[13].Get<uint32>();
                d.fishCount    = f[14].Get<uint32>();
                d.renown       = f[15].Get<uint32>();
                d.renownPoints = f[16].Get<uint32>();
            }
            d.loaded = true;
        }
        return d;
    }

    bool ClassMatches(Player* player, uint32 classmask)
    {
        return classmask == 0 || (classmask & player->getClassMask()) != 0;
    }

    char const* RewardName(Player* player, BPReward const& r)
    {
        return (SeasonPass::GetLang(player) == 1 && !r.nameEn.empty()) ? r.nameEn.c_str() : r.name.c_str();
    }

    // ------------------------- Zufallskisten (kuratierter Pool) -------------------------

    // Raritätswurf (Promille) — Kistenfieber verstärkt Episch + Legendär,
    // dann gewichtete Auswahl innerhalb der Rarität (Fallback: nächstniedrigere).
    BPChestLoot const* RollChestLoot(uint8 chest, uint32 pityPct, uint8 minRarity)
    {
        uint32 w[5] = {};
        uint32 total = 0;
        for (uint8 r = 1; r <= 4; ++r)
        {
            w[r] = g_chestRarity[chest][r];
            if (r >= 3)
                w[r] = w[r] * (100 + pityPct) / 100;
            if (r < minRarity)
                w[r] = 0;
            total += w[r];
        }
        if (!total)
            return nullptr;
        uint32 roll = urand(0, total - 1);
        uint8 rarity = 4;
        for (uint8 r = 1; r <= 4; ++r)
        {
            if (roll < w[r]) { rarity = r; break; }
            roll -= w[r];
        }
        for (int r = rarity; r >= 1; --r)
        {
            uint32 sum = 0;
            for (BPChestLoot const& e : g_chestLoot[chest])
                if (e.rarity == r && (e.kind != 0 || sObjectMgr->GetItemTemplate(e.id)))
                    sum += e.weight;
            if (!sum)
                continue;
            uint32 pick = urand(0, sum - 1);
            for (BPChestLoot const& e : g_chestLoot[chest])
            {
                if (e.rarity != r || (e.kind == 0 && !sObjectMgr->GetItemTemplate(e.id)))
                    continue;
                if (pick < e.weight)
                    return &e;
                pick -= e.weight;
            }
        }
        return nullptr;
    }

    void GrantItemOrMail(Player* player, uint32 entry, uint32 count)
    {
        if (!player->AddItem(entry, count))
            player->SendItemRetrievalMail(entry, count);
    }

    // ------------------- Traumschmiede (Paragon) -------------------

    BPParagon& GetParagon(Player* player)
    {
        BPParagon& p = g_paragon[player->GetGUID().GetCounter()];
        if (!p.loaded)
        {
            p.loaded = true;
            if (QueryResult result = CharacterDatabase.Query(
                "SELECT stat, points FROM character_seasonpass_paragon WHERE guid = {}",
                player->GetGUID().GetCounter()))
            {
                do
                {
                    Field* f = result->Fetch();
                    uint32 s = f[0].Get<uint32>();
                    if (s >= 1 && s <= PG_STATS)
                        p.pts[s] = std::min(f[1].Get<uint32>(), g_paragonCap);
                } while (result->NextRow());
            }
        }
        return p;
    }

    uint32 ParagonSpent(BPParagon const& p)
    {
        uint32 sum = 0;
        for (uint32 s = 1; s <= PG_STATS; ++s)
            sum += p.pts[s];
        return sum;
    }

    void SendParagonSync(Player* player)
    {
        if (!g_internalParagonEnable)
        {
            ChatHandler(player->GetSession()).SendSysMessage(
                "BPPG:0:0:0:0:0:0:0:0:0:0:0:0:0");
            return;
        }
        BPData& d = GetData(player);
        BPParagon& p = GetParagon(player);
        uint32 spent = ParagonSpent(p);
        uint32 earned = d.prestige * g_paragonPtsPer;
        // BPPG:prestige:maxPrestige:frei:cap:mobPct:s1:...:s8
        ChatHandler(player->GetSession()).PSendSysMessage(
            "BPPG:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}",
            d.prestige, g_prestigeMax, earned > spent ? earned - spent : 0,
            g_paragonCap, g_mobScalePct,
            p.pts[1], p.pts[2], p.pts[3], p.pts[4], p.pts[5], p.pts[6], p.pts[7], p.pts[8]);
    }

    void SpendParagon(Player* player, uint32 stat, uint32 n)
    {
        if (!g_internalParagonEnable || stat < 1 || stat > PG_STATS || !n)
            return;
        BPData& d = GetData(player);
        BPParagon& p = GetParagon(player);
        uint32 spent = ParagonSpent(p);
        uint32 earned = d.prestige * g_paragonPtsPer;
        uint32 freePts = earned > spent ? earned - spent : 0;
        n = std::min({ n, freePts, g_paragonCap - std::min(p.pts[stat], g_paragonCap) });
        ChatHandler ch(player->GetSession());
        if (!n)
        {
            ch.SendSysMessage(T(player,
                "|cffFF0000[Traumpfad]|r Kein freier Punkt (oder Wert am Maximum). Prestige bringt neue Punkte!",
                "|cffFF0000[Dream Path]|r No free point (or stat capped). Prestige grants new points!"));
            return;
        }
        p.pts[stat] += n;
        CharacterDatabase.Execute(
            "REPLACE INTO character_seasonpass_paragon (guid, stat, points) VALUES ({}, {}, {})",
            player->GetGUID().GetCounter(), stat, p.pts[stat]);
        if (stat == 5)
            player->UpdateMaxHealth();
        if (stat == 6)
            player->UpdateMaxPower(POWER_MANA);
        ch.PSendSysMessage(T(player,
            "|cffFFD700[Traumpfad]|r Traumschmiede: Wert {} jetzt bei |cff00FF00{}|r Punkt(en) (+{}%).",
            "|cffFFD700[Dream Path]|r Dream Forge: stat {} now at |cff00FF00{}|r point(s) (+{}%)."),
            stat, p.pts[stat], p.pts[stat] * PG_PER[stat]);
        SendParagonSync(player);
    }

    void ResetParagon(Player* player)
    {
        if (!g_internalParagonEnable)
            return;
        BPParagon& p = GetParagon(player);
        for (uint32 s = 1; s <= PG_STATS; ++s)
            p.pts[s] = 0;
        CharacterDatabase.Execute("DELETE FROM character_seasonpass_paragon WHERE guid = {}",
            player->GetGUID().GetCounter());
        player->UpdateMaxHealth();
        player->UpdateMaxPower(POWER_MANA);
        ChatHandler(player->GetSession()).SendSysMessage(T(player,
            "|cffFFD700[Traumpfad]|r Traumschmiede zurückgesetzt — alle Punkte wieder frei.",
            "|cffFFD700[Dream Path]|r Dream Forge reset — all points refunded."));
        SendParagonSync(player);
    }

    // ------------------- Versorgungsaufträge (SoD "Waylaid Supplies") -------------------

    BPSupply const* ActiveSupply()
    {
        if (g_supplies.empty())
            return nullptr;
        return &g_supplies[CurrentDay() % g_supplies.size()];
    }

    void SendSupplySync(Player* player)
    {
        BPSupply const* s = ActiveSupply();
        if (!s)
            return;
        BPData& d = GetData(player);
        // BPSUP:item:menge:erledigt:punkte:gold
        ChatHandler(player->GetSession()).PSendSysMessage("BPSUP:{}:{}:{}:{}:{}",
            s->item, s->count, d.supplyDay == CurrentDay() ? 1 : 0, s->points, s->gold);
    }

    // ------------------- Angelaufträge -------------------

    BPFish const* ActiveFish()
    {
        if (g_fish.empty())
            return nullptr;
        return &g_fish[CurrentDay() % g_fish.size()];
    }

    void SendFishSync(Player* player)
    {
        BPFish const* f = ActiveFish();
        if (!f)
            return;
        BPData& d = GetData(player);
        uint32 count = (d.fishDay == CurrentDay()) ? d.fishCount : 0;
        // BPFI:item:menge:fortschritt:punkte:gold
        ChatHandler(player->GetSession()).PSendSysMessage("BPFI:{}:{}:{}:{}:{}",
            f->item, f->count, count, f->points, f->gold);
    }
    void SendRenownSync(Player* player)
    {
        BPData& d = GetData(player);
        ChatHandler(player->GetSession()).PSendSysMessage(
            "BPRENOWN:{}:{}:{}", d.renown, d.renownPoints, g_pointsPerTier);
    }
}

// ---------------------------------------------------------------------------
//  Oeffentliche Schnittstelle (SeasonPass.h)
// ---------------------------------------------------------------------------
namespace SeasonPass
{
    bool IsTracked(Player* player)
    {
        if (!g_enabled || !player || !player->GetSession())
            return false;
        BPData& d = g_cache[player->GetGUID().GetCounter()];
        return !d.isBot;
    }

    uint32 GetSeason() { return g_season; }

    uint32 GetTier(Player* player)
    {
        if (!player)
            return 0;
        return TierFromPoints(GetData(player).points);
    }

    uint32 GetStartRune(Player* player)
    {
        if (!player)
            return 0;
        return GetData(player).startRune;
    }

    uint8 GetLang(Player* player)
    {
        if (!player)
            return 0;
        return GetData(player).lang;
    }

    void SetLang(Player* player, uint8 lang)
    {
        BPData& d = GetData(player);
        d.lang = lang > 1 ? 0 : lang;
        SaveData(player, d);
        ChatHandler(player->GetSession()).SendSysMessage(d.lang == 1
            ? "|cffFFD700[Dream Path]|r Language set to English."
            : "|cffFFD700[Traumpfad]|r Sprache auf Deutsch gestellt.");
    }

    uint8 ActiveMutatorKind()
    {
        BPMutator const* m = Mutator();
        return m ? m->kind : 255;
    }

    uint32 ActiveMutatorValue()
    {
        BPMutator const* m = Mutator();
        return m ? m->value : 100;
    }

    std::string ActiveMutatorName(Player* player)
    {
        BPMutator const* m = Mutator();
        if (!m)
            return "-";
        return (player && GetLang(player) == 1) ? m->nameEn : m->name;
    }

    bool StormActive()
    {
        if (!g_stormEnable)
            return false;
        uint32 hour = NowSecs() / 3600;
        if (((hour * 2654435761u) >> 8) % 4 != 0)
            return false;
        return (NowSecs() % 3600) < 900; // erste 15 Minuten der Sturmstunde
    }

    void SendSync(Player* player)
    {
        BPData& d = GetData(player);
        ChatHandler(player->GetSession()).PSendSysMessage("BPSYNC:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}",
            d.points, TierFromPoints(d.points), d.claimedTier, d.claimedEpic,
            g_pointsPerTier, g_maxTier, IsWeekend() ? 1 : 0, g_prestigeEnable ? d.prestige : 0, d.streak,
            d.chestPity * g_chestPityStep, d.welcomed ? 1 : 0);
        ChatHandler(player->GetSession()).PSendSysMessage("BPPRESTIGE:{}", g_prestigeEnable ? 1 : 0);
        SendRenownSync(player);
    }

    void AddPoints(Player* player, uint32 amount, char const* reason)
    {
        if (!amount || !IsTracked(player))
            return;

        if (IsWeekend() && g_weekendPoints > 100)
            amount = amount * g_weekendPoints / 100;
        if (g_zoneEventMult > 100 && ActiveEventZone() && player->GetZoneId() == ActiveEventZone())
            amount = amount * g_zoneEventMult / 100;
        if (StormActive() && g_stormPoints > 100)
            amount = amount * g_stormPoints / 100;

        BPData& d = GetData(player);
        if (g_prestigeEnable && g_legacyPct && d.prestige) // Saison-Erbe: permanenter Prestige-Bonus
            amount = amount * (100 + d.prestige * g_legacyPct) / 100;

        // Prestige-Modus: nach dem ersten Prestige zählt jede volle Leiste
        // (PointsPerTier Punkte) direkt als +1 Prestige — keine 100 Stufen mehr.
        if (g_prestigeEnable && d.prestige > 0)
        {
            d.points += amount;
            uint32 leveled = 0;
            while (d.points >= g_pointsPerTier && d.prestige < g_prestigeMax)
            {
                d.points -= g_pointsPerTier;
                ++d.prestige;
                ++leveled;
                player->ModifyMoney(static_cast<int32>(g_prestigeAutoGold));
                ChatHandler(player->GetSession()).PSendSysMessage(
                    T(player, "|cffFF8800[Traumpfad]|r Prestige |cffFF8800{}|r erreicht! +{} Traumschmiede-Punkte, +{} Gold ({})",
                              "|cffFF8800[Dream Path]|r Prestige |cffFF8800{}|r reached! +{} Dream Forge points, +{} gold ({})"),
                    d.prestige, g_paragonPtsPer, g_prestigeAutoGold / 10000, reason);
                if (d.prestige % 10 == 0) // Meilensteine serverweit feiern
                {
                    std::ostringstream ann;
                    ann << "|cffFF8800[Traumpfad]|r " << player->GetName() << " hat Prestige "
                        << d.prestige << " / " << g_prestigeMax << " erreicht!";
                    ChatHandler(nullptr).SendGlobalSysMessage(ann.str().c_str());
                }
            }
            if (d.prestige >= g_prestigeMax)
                d.points = std::min(d.points, g_pointsPerTier); // Deckel am Maximum
            SaveData(player, d);
            WeeklyProgress(player, WK_POINTS, amount);
            if (leveled)
            {
                AchProgress(player, ACH_PRESTIGE, d.prestige);
                SendParagonSync(player);
            }
            SendSync(player);
            return;
        }

        uint32 oldTier = TierFromPoints(d.points);
        uint32 oldRenownPoints = d.renownPoints;
        if (d.renown == std::numeric_limits<uint32>::max())
            d.renownPoints = 0;
        uint64 cap = static_cast<uint64>(g_maxTier) * g_pointsPerTier;
        uint64 total = static_cast<uint64>(d.points) + amount;
        uint64 completedRenown = 0;

        if (total >= cap)
        {
            d.points = static_cast<uint32>(cap);
            uint64 overflow = total - cap + d.renownPoints;
            completedRenown = overflow / g_pointsPerTier;
            if (d.renown == std::numeric_limits<uint32>::max()
                || completedRenown >= std::numeric_limits<uint32>::max() - d.renown)
            {
                d.renown = std::numeric_limits<uint32>::max();
                d.renownPoints = 0;
            }
            else
            {
                d.renown += static_cast<uint32>(completedRenown);
                d.renownPoints = static_cast<uint32>(overflow % g_pointsPerTier);
            }
        }
        else
            d.points = static_cast<uint32>(total);

        uint32 newTier = TierFromPoints(d.points);
        SaveData(player, d);

        WeeklyProgress(player, WK_POINTS, amount);

        if (newTier > oldTier)
        {
            AchProgress(player, ACH_TIER, newTier);
            if (g_announce)
                ChatHandler(player->GetSession()).PSendSysMessage(
                    T(player, "|cffFFD700[Traumpfad]|r Stufe |cff00FF00{}|r erreicht! ({})",
                              "|cffFFD700[Dream Path]|r Tier |cff00FF00{}|r reached! ({})"),
                    newTier, reason);
        }
        if (completedRenown > 0)
            ChatHandler(player->GetSession()).PSendSysMessage(
                T(player, "|cffFFD700[Traumpfad]|r Traumruhm |cff00FF00{}|r erreicht! ({})",
                          "|cffFFD700[Dream Path]|r Dream Renown |cff00FF00{}|r reached! ({})"),
                d.renown, reason);
        if (newTier != oldTier || completedRenown > 0 || d.renownPoints != oldRenownPoints)
            SendSync(player);
    }

    void OpenChest(Player* player, uint8 chestTier)
    {
        if (!g_chestEnable || !IsTracked(player))
            return;

        BPData& d = GetData(player);
        uint32 pityPct = d.chestPity * g_chestPityStep;

        if (chestTier == 0) // Traumkiste: Qualität wird beim Öffnen ausgewürfelt
        {
            uint32 w1 = g_chestRarity[0][1], w2 = g_chestRarity[0][2], w3 = g_chestRarity[0][3];
            if (!w1 && !w2 && !w3) { w1 = 500; w2 = 350; w3 = 150; }
            w2 = w2 * (100 + pityPct) / 100; // Kistenfieber verbessert die Aufwertung
            w3 = w3 * (100 + pityPct) / 100;
            uint32 roll = urand(0, w1 + w2 + w3 - 1);
            chestTier = roll < w1 ? 1 : roll < w1 + w2 ? 2 : 3;
        }
        chestTier = std::max<uint8>(1, std::min<uint8>(3, chestTier));

        ChatHandler ch(player->GetSession());
        ch.PSendSysMessage("BPCHEST:{}", uint32(chestTier)); // Client: Aufwertungs-Animation

        uint32 pulls = 1 + chestTier;                        // 2 / 3 / 4 Ziehungen

        char const* chestName = chestTier == 3
            ? T(player, "Goldene Traumkiste", "Golden Dream Chest")
            : chestTier == 2 ? T(player, "Mythische Traumkiste", "Mythic Dream Chest")
                             : T(player, "Blaue Traumkiste", "Blue Dream Chest");

        ch.PSendSysMessage(T(player,
            "|cffFFD700[Traumpfad]|r {} geöffnet! (Kistenfieber: +{}% Aufwertungs-Chance)",
            "|cffFFD700[Dream Path]|r {} opened! (Chest Fever: +{}% upgrade chance)"),
            chestName, pityPct);

        static char const* const rarColor[5] = { "ffffffff", "ffffffff", "ff0070dd", "ffa335ee", "ffff8000" };

        bool gotEpic = false;
        for (uint32 i = 0; i < pulls; ++i)
        {
            // Kiste 2/3: erste Ziehung garantiert mindestens Selten/Episch
            uint8 minRarity = i == 0 ? chestTier : 1;
            BPChestLoot const* e = RollChestLoot(chestTier, pityPct, minRarity);
            if (!e)
            {
                player->ModifyMoney(50000); // Notgroschen statt leerer Hand
                ch.SendSysMessage(T(player, "  ... 5 Gold", "  ... 5 gold"));
                continue;
            }
            if (e->rarity >= 3)
                gotEpic = true;

            char const* nm = (d.lang == 1 && !e->nameEn.empty()) ? e->nameEn.c_str() : e->name.c_str();
            switch (e->kind)
            {
                case 1: // Gold
                    player->ModifyMoney(static_cast<int32>(e->id));
                    ch.PSendSysMessage("  |c{}+{} Gold|r", rarColor[e->rarity], e->id / 10000);
                    break;
                case 2: // Verlorene Rune: lehrt eine zufällige unbekannte Runen-Fähigkeit
                {
                    uint32 spell = SeasonPass::RandomUnknownRuneSpell(player);
                    if (spell)
                    {
                        player->learnSpell(spell);
                        ch.SendSysMessage(T(player,
                            "  |cffa335ee[Verlorene Rune]|r Neue Fähigkeit erlernt — schau ins Zauberbuch!",
                            "  |cffa335ee[Lost Rune]|r New ability learned — check your spellbook!"));
                    }
                    else
                    {
                        player->ModifyMoney(250000);
                        ch.SendSysMessage(T(player,
                            "  |cffa335ee[Verlorene Rune]|r Du kennst schon alle Fähigkeiten — 25 Gold!",
                            "  |cffa335ee[Lost Rune]|r You already know every ability — 25 gold!"));
                    }
                    break;
                }
                default: // Item
                    GrantItemOrMail(player, e->id, e->count);
                    if (e->count > 1)
                        ch.PSendSysMessage("  |c{}|Hitem:{}:0:0:0:0:0:0:0:0|h[{}]|h|r x{}",
                            rarColor[e->rarity], e->id, nm, e->count);
                    else
                        ch.PSendSysMessage("  |c{}|Hitem:{}:0:0:0:0:0:0:0:0|h[{}]|h|r",
                            rarColor[e->rarity], e->id, nm);
                    break;
            }

            if (e->rarity == 4) // Legendär: serverweite Ansage!
            {
                std::ostringstream ann;
                ann << "|cffFF8000[Traumpfad]|r " << player->GetName() << " zieht |cffFF8000"
                    << e->name << "|r aus einer Kiste! GZ!";
                auto const& sessions = sWorldSessionMgr->GetAllSessions();
                for (auto const& itr : sessions)
                    if (Player* p = itr.second ? itr.second->GetPlayer() : nullptr)
                        if (p->IsInWorld())
                            ChatHandler(p->GetSession()).SendSysMessage(ann.str().c_str());
            }
        }

        // Kistenfieber (Pity): ohne Episches steigt die Chance der naechsten Kiste
        d.chestPity = gotEpic ? 0 : std::min<uint32>(d.chestPity + 1, 50);
        SaveData(player, d);

        // Kisten lohnen sich: Bonuspunkte + Kisten-Erfolge
        AddPoints(player, 10, T(player, "Traumkiste", "Dream Chest"));
        SeasonPass::AchProgress(player, SeasonPass::ACH_CHEST, 1);
    }
}

// ---------------------------------------------------------------------------
//  Welt: Config + Tabellen + Traumsturm-Ansage
// ---------------------------------------------------------------------------
class SeasonPassWorld : public WorldScript
{
public:
    SeasonPassWorld() : WorldScript("SeasonPassWorld") { }

    void OnAfterConfigLoad(bool reload) override
    {
        g_enabled        = sConfigMgr->GetOption<bool>("SeasonPass.Enable", true);
        g_season         = sConfigMgr->GetOption<uint32>("SeasonPass.Season", 1);
        g_pointsPerTier  = std::max<uint32>(1, sConfigMgr->GetOption<uint32>("SeasonPass.PointsPerTier", 100));
        g_maxTier        = std::max<uint32>(1, sConfigMgr->GetOption<uint32>("SeasonPass.MaxTier", 100));
        uint32 configuredMaxTier = g_maxTier;
        g_maxTier = std::min<uint32>(g_maxTier, std::numeric_limits<uint32>::max() / g_pointsPerTier);
        if (g_maxTier != configuredMaxTier)
            LOG_WARN("module", "[SeasonPass] MaxTier {} reduced to {} to fit PointsPerTier {} in uint32 progress.",
                configuredMaxTier, g_maxTier, g_pointsPerTier);
        g_ptsQuest       = sConfigMgr->GetOption<uint32>("SeasonPass.Points.Quest", 10);
        g_ptsKill        = sConfigMgr->GetOption<uint32>("SeasonPass.Points.Kill", 1);
        g_ptsElite       = sConfigMgr->GetOption<uint32>("SeasonPass.Points.EliteKill", 5);
        g_ptsBoss        = sConfigMgr->GetOption<uint32>("SeasonPass.Points.BossKill", 100);
        g_ptsRare        = sConfigMgr->GetOption<uint32>("SeasonPass.Points.RareKill", 25);
        g_ptsLevel       = sConfigMgr->GetOption<uint32>("SeasonPass.Points.LevelUp", 50);
        g_ptsDaily       = sConfigMgr->GetOption<uint32>("SeasonPass.Points.DailyLogin", 50);
        g_ptsPvP         = sConfigMgr->GetOption<uint32>("SeasonPass.Points.PvPKill", 10);
        g_ptsDuel        = sConfigMgr->GetOption<uint32>("SeasonPass.Points.DuelWin", 5);
        g_pvpCooldown    = sConfigMgr->GetOption<uint32>("SeasonPass.PvP.VictimCooldown", 300);
        g_streakBonus    = sConfigMgr->GetOption<uint32>("SeasonPass.Streak.BonusPerDay", 5);
        g_announce       = sConfigMgr->GetOption<bool>("SeasonPass.AnnounceTier", true);
        g_announceRare   = sConfigMgr->GetOption<bool>("SeasonPass.AnnounceRareKill", true);
        g_ignoreBots     = sConfigMgr->GetOption<bool>("SeasonPass.IgnoreBots", true);
        g_weekendEnable  = sConfigMgr->GetOption<bool>("SeasonPass.Weekend.Enable", true);
        g_weekendPoints  = sConfigMgr->GetOption<uint32>("SeasonPass.Weekend.PointsPercent", 200);
        g_weekendXP      = sConfigMgr->GetOption<uint32>("SeasonPass.Weekend.XPPercent", 150);
        g_zoneEventMult  = sConfigMgr->GetOption<uint32>("SeasonPass.ZoneEvent.PointsPercent", 200);
        g_chestEnable    = sConfigMgr->GetOption<bool>("SeasonPass.Chest.Enable", true);
        g_chestKillPct   = sConfigMgr->GetOption<uint32>("SeasonPass.Chest.DropChanceKillPct", 2);
        g_chestElitePct  = sConfigMgr->GetOption<uint32>("SeasonPass.Chest.DropChanceElitePct", 10);
        g_chestBossPct   = sConfigMgr->GetOption<uint32>("SeasonPass.Chest.DropChanceBossPct", 100);
        g_chestLegPct    = sConfigMgr->GetOption<uint32>("SeasonPass.Chest.LegendaryFromBossPct", 10);
        g_chestEpicBase  = sConfigMgr->GetOption<uint32>("SeasonPass.Chest.EpicChanceBasePct", 15);
        g_chestPityStep  = sConfigMgr->GetOption<uint32>("SeasonPass.Chest.PityStepPct", 5);
        g_stormEnable    = sConfigMgr->GetOption<bool>("SeasonPass.Storm.Enable", true);
        g_stormPoints    = sConfigMgr->GetOption<uint32>("SeasonPass.Storm.PointsPercent", 300);
        g_legacyPct      = sConfigMgr->GetOption<uint32>("SeasonPass.Legacy.PointsPercentPerPrestige", 2);
        g_mutatorEnable  = sConfigMgr->GetOption<bool>("SeasonPass.Mutators.Enable", true);
        g_lvlChestEnable = sConfigMgr->GetOption<bool>("SeasonPass.LevelChest.Enable", true);
        g_chestGoldPer10 = sConfigMgr->GetOption<uint32>("SeasonPass.LevelChest.GoldPer10Levels", 50000);
        g_chestBagItem   = sConfigMgr->GetOption<uint32>("SeasonPass.LevelChest.BagItem", 21841);
        g_internalPrestigeEnable = sConfigMgr->GetOption<bool>("SeasonPass.InternalPrestige.Enable", false);
        g_internalParagonEnable = sConfigMgr->GetOption<bool>("SeasonPass.InternalParagon.Enable", false);
        g_prestigeMobScalingEnable = sConfigMgr->GetOption<bool>("SeasonPass.PrestigeMobScaling.Enable", false);
        g_prestigeEnable = sConfigMgr->GetOption<bool>("SeasonPass.Prestige.Enable", true) && g_internalPrestigeEnable;
        g_prestigeMax      = std::max<uint32>(1, sConfigMgr->GetOption<uint32>("SeasonPass.Prestige.Max", 300));
        g_prestigeGoldBase = sConfigMgr->GetOption<uint32>("SeasonPass.Prestige.GoldBase", 500000);
        g_prestigeGoldPer  = sConfigMgr->GetOption<uint32>("SeasonPass.Prestige.GoldPerLevel", 100000);
        g_prestigeXPPct    = sConfigMgr->GetOption<uint32>("SeasonPass.Prestige.XPPctPerLevel", 3);
        g_prestigeAutoGold = sConfigMgr->GetOption<uint32>("SeasonPass.Prestige.AutoGold", 100000);
        g_paragonCap       = std::max<uint32>(1, sConfigMgr->GetOption<uint32>("SeasonPass.Paragon.CapPerStat", 75));
        g_paragonPtsPer    = std::max<uint32>(1, sConfigMgr->GetOption<uint32>("SeasonPass.Paragon.PointsPerPrestige", 2));
        g_mobScalePct      = sConfigMgr->GetOption<uint32>("SeasonPass.Paragon.MobScalePctPerPrestige", 1);
        g_runeResonance    = sConfigMgr->GetOption<uint32>("SeasonPass.Runes.ResonancePct", 2);

        g_botPrefixes.clear();
        std::string prefixes = sConfigMgr->GetOption<std::string>("SeasonPass.BotAccountPrefixes", "RNDBOT,ADDCLASS");
        std::stringstream ss(prefixes);
        std::string part;
        while (std::getline(ss, part, ','))
            if (!part.empty())
                g_botPrefixes.push_back(part);

        if (g_enabled)
            LoadCoreTables();

        if (reload && g_enabled)
        {
            auto const& sessions = sWorldSessionMgr->GetAllSessions();
            for (auto const& itr : sessions)
                if (Player* player = itr.second ? itr.second->GetPlayer() : nullptr)
                    if (player->IsInWorld() && SeasonPass::IsTracked(player))
                        SeasonPass::SendSync(player);
        }
    }

    void OnUpdate(uint32 /*diff*/) override
    {
        if (!g_enabled || !g_stormEnable)
            return;
        bool active = SeasonPass::StormActive();
        if (active == g_stormWasActive)
            return;
        g_stormWasActive = active;
        if (active)
            ChatHandler(nullptr).SendGlobalSysMessage(
                "|cffFFD700[Traumpfad]|r |cff00CCFFEin Traumsturm tobt über Azeroth! 15 Minuten dreifache Punkte! / A dream storm rages — triple points for 15 minutes!|r");
        else
            ChatHandler(nullptr).SendGlobalSysMessage(
                "|cffFFD700[Traumpfad]|r Der Traumsturm ist verklungen. / The dream storm has passed.");
    }
};

// ---------------------------------------------------------------------------
//  Spieler-Hooks
// ---------------------------------------------------------------------------
class SeasonPassPlayer : public PlayerScript
{
public:
    SeasonPassPlayer() : PlayerScript("SeasonPassPlayer") { }

    void OnPlayerLogin(Player* player) override
    {
        if (!g_enabled || !player || !player->GetSession())
            return;

        BPData& d = g_cache[player->GetGUID().GetCounter()];

        d.isBot = false;
        if (g_ignoreBots)
        {
            if (QueryResult result = LoginDatabase.Query(
                    "SELECT username FROM account WHERE id = {}", player->GetSession()->GetAccountId()))
            {
                std::string name = (*result)[0].Get<std::string>();
                for (std::string const& prefix : g_botPrefixes)
                    if (name.rfind(prefix, 0) == 0)
                    {
                        d.isBot = true;
                        break;
                    }
            }
        }

        if (d.isBot)
        {
            d.season = g_season;
            d.loaded = true;
            return;
        }

        BPData& data = GetData(player);

        // Willkommenspaket (Stufe 0) wartet? Hinweis geben — geclaimt wird im Fenster
        if (!data.welcomed)
            ChatHandler(player->GetSession()).SendSysMessage(
                T(player, "|cffFFD700[Traumpfad]|r |cff00FF00Dein Willkommenspaket (Stufe 0) wartet!|r Klick den Geschenk-Slot im Traumpfad-Fenster.",
                          "|cffFFD700[Dream Path]|r |cff00FF00Your welcome package (tier 0) is waiting!|r Click the gift slot in the Dream Path window."));

        uint32 today = CurrentDay();
        if (data.lastDailyDay == 0)
        {
            // Allererster Login des Charakters: Serie startet still — der Pass
            // beginnt sauber bei 0 Punkten, Login-Bonus gibt es ab Tag 2.
            data.streak = 1;
            data.lastDailyDay = today;
            SaveData(player, data);
        }
        else if (data.lastDailyDay != today)
        {
            data.streak = (data.lastDailyDay == today - 1) ? data.streak + 1 : 1;
            data.lastDailyDay = today;
            SaveData(player, data);

            uint32 bonus = g_ptsDaily + std::min<uint32>(data.streak - 1, 10) * g_streakBonus;
            SeasonPass::AddPoints(player, bonus, T(player, "Täglicher Login", "Daily login"));
            ChatHandler(player->GetSession()).PSendSysMessage(
                T(player, "|cffFFD700[Traumpfad]|r Täglicher Login: +{} Punkte! Login-Serie: |cff00FF00{} Tag(e)|r",
                          "|cffFFD700[Dream Path]|r Daily login: +{} points! Streak: |cff00FF00{} day(s)|r"),
                bonus, data.streak);
            SeasonPass::AchProgress(player, SeasonPass::ACH_STREAK, data.streak);
        }

        // Startfähigkeit zur Sicherheit nachlernen (falls z. B. Zauber entfernt wurde)
        if (data.startRune)
            if (uint32 spell = SeasonPass::AbilityRuneSpell(data.startRune))
                if (!player->HasSpell(spell))
                    player->learnSpell(spell);

        if (IsWeekend())
            ChatHandler(player->GetSession()).PSendSysMessage(
                T(player, "|cffFFD700[Traumpfad]|r |cff00FF00Bonus-Wochenende:|r {}% Punkte und {}% XP!",
                          "|cffFFD700[Dream Path]|r |cff00FF00Bonus weekend:|r {}% points and {}% XP!"),
                g_weekendPoints, g_weekendXP);

        if (Mutator())
            ChatHandler(player->GetSession()).PSendSysMessage(
                T(player, "|cffFFD700[Traumpfad]|r Wochen-Mutator: |cffFF8800{}|r",
                          "|cffFFD700[Dream Path]|r Weekly mutator: |cffFF8800{}|r"),
                SeasonPass::ActiveMutatorName(player).c_str());
    }

    void OnPlayerLogout(Player* player) override
    {
        if (player)
            g_cache.erase(player->GetGUID().GetCounter());
    }

    void OnPlayerCompleteQuest(Player* player, Quest const* /*quest*/) override
    {
        if (!SeasonPass::IsTracked(player))
            return;
        uint32 pts = g_ptsQuest * MutatorMult(0) / 100;
        SeasonPass::AddPoints(player, pts, T(player, "Quest abgeschlossen", "Quest completed"));
        SeasonPass::WeeklyProgress(player, SeasonPass::WK_QUESTS, 1);
    }

    void OnPlayerLevelChanged(Player* player, uint8 oldlevel) override
    {
        if (!player || player->GetLevel() <= oldlevel || !SeasonPass::IsTracked(player))
            return;

        SeasonPass::AddPoints(player, g_ptsLevel, T(player, "Stufenaufstieg", "Level up"));
        SeasonPass::WeeklyProgress(player, SeasonPass::WK_LEVELUPS, 1);

        uint8 level = player->GetLevel();
        if (g_lvlChestEnable && level >= 10 && level % 10 == 0)
        {
            uint32 gold = g_chestGoldPer10 * (level / 10);
            player->ModifyMoney(static_cast<int32>(gold));
            if (level >= 20 && g_chestBagItem && sObjectMgr->GetItemTemplate(g_chestBagItem))
                player->SendItemRetrievalMail(g_chestBagItem, 1);
            ChatHandler(player->GetSession()).PSendSysMessage(
                T(player, "|cffFFD700[Traumpfad]|r Levelkiste für Stufe {}: |cff00FF00{} Gold|r{}",
                          "|cffFFD700[Dream Path]|r Level chest for level {}: |cff00FF00{} gold|r{}"),
                level, gold / 10000,
                level >= 20 ? T(player, " + Tasche per Post!", " + bag by mail!") : "!");
        }

    }

    void OnPlayerCreatureKill(Player* player, Creature* killed) override
    {
        if (!player || !killed || !SeasonPass::IsTracked(player))
            return;

        if (killed->GetLevel() + 8 < player->GetLevel())
            return;

        SeasonPass::WeeklyProgress(player, SeasonPass::WK_KILLS, 1);
        if (SeasonPass::ActiveEventZone() && player->GetZoneId() == SeasonPass::ActiveEventZone())
            SeasonPass::WeeklyProgress(player, SeasonPass::WK_ZONEKILLS, 1);

        uint32 pts = g_ptsKill;
        char const* reason = T(player, "Kill", "Kill");
        uint32 rank = killed->GetCreatureTemplate()->rank;
        bool isBoss = killed->IsDungeonBoss() || killed->isWorldBoss();
        bool isElite = killed->isElite();
        bool isRare = rank == CREATURE_ELITE_RAREELITE || rank == CREATURE_ELITE_RARE;

        if (isBoss)
        {
            pts = g_ptsBoss;
            reason = T(player, "Bosskill", "Boss kill");
            SeasonPass::WeeklyProgress(player, SeasonPass::WK_BOSS, 1);
            SeasonPass::OnWorldBossKilled(player, killed->GetEntry());
        }
        else if (isRare)
        {
            pts = g_ptsRare * MutatorMult(2) / 100;
            reason = T(player, "Seltener Gegner", "Rare enemy");
            SeasonPass::WeeklyProgress(player, SeasonPass::WK_RARES, 1);
            SeasonPass::AchProgress(player, SeasonPass::ACH_RARE, 1);
            if (g_announceRare)
            {
                std::ostringstream msg;
                msg << "|cffFFD700[Traumpfad]|r |cff00CCFF" << player->GetName()
                    << "|r hat den seltenen Gegner |cffFF8800" << killed->GetName() << "|r erlegt!";
                ChatHandler(nullptr).SendGlobalSysMessage(msg.str().c_str());
            }
        }
        else if (isElite)
        {
            pts = g_ptsElite * MutatorMult(1) / 100;
            reason = T(player, "Elite-Kill", "Elite kill");
            SeasonPass::WeeklyProgress(player, SeasonPass::WK_ELITE, 1);
        }

        SeasonPass::AddPoints(player, pts, reason);

        // Endlos-Endgame: nach Stufe 100 (oder im Prestige-Modus) droppen Kisten von Gegnern!
        if (g_chestEnable && (g_prestigeEnable && GetData(player).prestige > 0 ||
            TierFromPoints(GetData(player).points) >= g_maxTier))
        {
            uint32 chance = isBoss ? g_chestBossPct : isElite ? g_chestElitePct : g_chestKillPct;
            chance = chance * MutatorMult(5) / 100; // Kistenwoche
            if (roll_chance_i(std::min<uint32>(100, chance)))
                SeasonPass::OpenChest(player, 0); // Traumkiste — Qualität wird ausgewürfelt
        }
    }

    void OnPlayerPVPKill(Player* killer, Player* killed) override
    {
        if (!killer || !killed || killer == killed || !SeasonPass::IsTracked(killer))
            return;

        if (killed->GetLevel() + 8 < killer->GetLevel())
            return;

        BPData& d = GetData(killer);
        uint32 now = NowSecs();
        uint32& last = d.pvpVictims[killed->GetGUID().GetCounter()];
        if (last && now - last < g_pvpCooldown)
            return;
        last = now;

        SeasonPass::AddPoints(killer, g_ptsPvP * MutatorMult(3) / 100, T(killer, "PvP-Kill", "PvP kill"));
        SeasonPass::WeeklyProgress(killer, SeasonPass::WK_PVPKILLS, 1);
    }

    void OnPlayerDuelEnd(Player* winner, Player* /*loser*/, DuelCompleteType type) override
    {
        if (type != DUEL_WON || !winner || !SeasonPass::IsTracked(winner))
            return;
        SeasonPass::AddPoints(winner, g_ptsDuel * MutatorMult(3) / 100, T(winner, "Duellsieg", "Duel win"));
        SeasonPass::WeeklyProgress(winner, SeasonPass::WK_DUELWINS, 1);
        SeasonPass::AchProgress(winner, SeasonPass::ACH_DUEL, 1);
    }

    // Angelauftrag: Fänge des Tagesfischs zählen automatisch beim Looten
    void OnPlayerLootItem(Player* player, Item* item, uint32 count, ObjectGuid /*lootguid*/) override
    {
        if (!player || !item || !SeasonPass::IsTracked(player))
            return;
        BPFish const* f = ActiveFish();
        if (!f || item->GetEntry() != f->item)
            return;

        BPData& d = GetData(player);
        uint32 today = CurrentDay();
        if (d.fishDay != today)
        {
            d.fishDay = today;
            d.fishCount = 0;
        }
        if (d.fishCount >= f->count)
            return; // heute schon abgeschlossen

        d.fishCount = std::min(d.fishCount + std::max<uint32>(count, 1), f->count);
        SaveData(player, d);

        if (d.fishCount >= f->count)
        {
            player->ModifyMoney(static_cast<int32>(f->gold));
            SeasonPass::AddPoints(player, f->points, T(player, "Angelauftrag", "Fishing contract"));
            ChatHandler(player->GetSession()).PSendSysMessage(
                T(player, "|cffFFD700[Traumpfad]|r |cff00FF00Angelauftrag erfüllt!|r +{} Punkte, {} Gold und eine Traumkiste!",
                          "|cffFFD700[Dream Path]|r |cff00FF00Fishing contract complete!|r +{} points, {} gold and a dream chest!"),
                f->points, f->gold / 10000);
            SeasonPass::OpenChest(player, 0); // Bonus: tägliche Angel-Traumkiste
        }
        else
            ChatHandler(player->GetSession()).PSendSysMessage(
                T(player, "|cffFFD700[Traumpfad]|r Angelauftrag: {}/{}",
                          "|cffFFD700[Dream Path]|r Fishing contract: {}/{}"),
                d.fishCount, f->count);
        SendFishSync(player);
    }

    void OnPlayerGiveXP(Player* player, uint32& amount, Unit* /*victim*/, uint8 /*xpSource*/) override
    {
        if (!SeasonPass::IsTracked(player))
            return;
        if (IsWeekend() && g_weekendXP > 100)
            amount = amount * g_weekendXP / 100;
        amount = amount * MutatorMult(4) / 100; // Woche der Weisheit
        // Prestige: schneller neu leveln + Traumschmiede-Weisheit
        uint32 xpBonus = 0;
        if (g_prestigeEnable)
            xpBonus += GetData(player).prestige * g_prestigeXPPct;
        if (g_internalParagonEnable)
            xpBonus += GetParagon(player).pts[8] * PG_PER[8];
        if (xpBonus)
            amount += amount * xpBonus / 100;
    }

    // Traumschmiede: Vitalität (+Leben) und Seelenkraft (+Mana)
    void OnPlayerAfterUpdateMaxHealth(Player* player, float& value) override
    {
        if (!SeasonPass::IsTracked(player))
            return;
        uint32 pct = SeasonPass::EngravedBuffRunes(player) * g_runeResonance; // Runenresonanz
        if (g_internalParagonEnable)
            pct += GetParagon(player).pts[5] * PG_PER[5];
        if (pct)
            value += value * pct / 100.0f;
    }

    void OnPlayerAfterUpdateMaxPower(Player* player, Powers& power, float& value) override
    {
        if (power != POWER_MANA || !SeasonPass::IsTracked(player))
            return;
        if (g_internalParagonEnable)
            if (uint32 pts = GetParagon(player).pts[6])
                value += value * (pts * PG_PER[6]) / 100.0f;
    }
};

// ---------------------------------------------------------------------------
//  Belohnungen einloesen
// ---------------------------------------------------------------------------
namespace
{
    void GrantOneReward(Player* player, uint32 tier, BPReward const& r)
    {
        switch (r.type)
        {
            case BP_REWARD_ITEM:
            {
                if (!sObjectMgr->GetItemTemplate(r.id))
                {
                    LOG_ERROR("module", "[SeasonPass] Stufe {}: Item {} existiert nicht!", tier, r.id);
                    return;
                }
                if (!player->AddItem(r.id, r.count))
                {
                    player->SendItemRetrievalMail(r.id, r.count);
                    ChatHandler(player->GetSession()).PSendSysMessage(
                        T(player, "|cffFFD700[Traumpfad]|r Taschen voll — |cff00FF00{}|r kommt per Post!",
                                  "|cffFFD700[Dream Path]|r Bags full — |cff00FF00{}|r arrives by mail!"),
                        RewardName(player, r));
                    return;
                }
                break;
            }
            case BP_REWARD_GOLD:
                player->ModifyMoney(static_cast<int32>(r.id) * static_cast<int32>(r.count));
                break;
            case BP_REWARD_TITLE:
                if (CharTitlesEntry const* title = sCharTitlesStore.LookupEntry(r.id))
                    player->SetTitle(title);
                break;
            case BP_REWARD_CHEST:
                for (uint32 i = 0; i < std::max<uint32>(1, r.count); ++i)
                    SeasonPass::OpenChest(player, static_cast<uint8>(r.id));
                return; // Kiste meldet sich selbst
            default:
                break;
        }

        ChatHandler(player->GetSession()).PSendSysMessage(
            T(player, "|cffFFD700[Traumpfad]|r Stufe {} eingelöst: |cff00FF00{}|r{}",
                      "|cffFFD700[Dream Path]|r Tier {} claimed: |cff00FF00{}|r{}"),
            tier, RewardName(player, r),
            r.track == BP_TRACK_EPIC ? T(player, " |cffA335EE(Heldenpfad)|r", " |cffA335EE(Hero path)|r") : "");
    }

    void GrantTier(Player* player, uint32 tier, uint8 track)
    {
        auto it = g_rewards.find(tier);
        if (it == g_rewards.end())
            return;
        for (BPReward const& r : it->second)
            if (r.track == track && ClassMatches(player, r.classmask))
                GrantOneReward(player, tier, r);
    }

    uint32 ClaimDue(Player* player)
    {
        BPData& d = GetData(player);
        uint32 currentTier = TierFromPoints(d.points);
        uint32 claimedNow = 0;

        while (d.claimedTier < currentTier)
        {
            ++d.claimedTier;
            GrantTier(player, d.claimedTier, BP_TRACK_FREE);
            ++claimedNow;
        }
        while (d.claimedEpic < currentTier)
        {
            ++d.claimedEpic;
            GrantTier(player, d.claimedEpic, BP_TRACK_EPIC);
            ++claimedNow;
        }

        if (claimedNow)
            SaveData(player, d);
        return claimedNow;
    }

    // Willkommenspaket (Stufe 0) per Klick im Fenster einlösen
    void ClaimWelcome(Player* player)
    {
        BPData& d = GetData(player);
        if (d.welcomed)
        {
            ChatHandler(player->GetSession()).SendSysMessage(
                T(player, "|cffFFD700[Traumpfad]|r Dein Willkommenspaket hast du schon.",
                          "|cffFFD700[Dream Path]|r You already claimed your welcome package."));
            return;
        }
        d.welcomed = true;
        SaveData(player, d);
        ChatHandler(player->GetSession()).SendSysMessage(
            T(player, "|cffFFD700[Traumpfad]|r |cff00FF00Willkommen zur Saison!|r Dein Willkommenspaket:",
                      "|cffFFD700[Dream Path]|r |cff00FF00Welcome to the season!|r Your welcome package:"));
        GrantTier(player, 0, BP_TRACK_FREE);
        GrantTier(player, 0, BP_TRACK_EPIC);
        SeasonPass::SendSync(player);
    }

    void DoPrestige(Player* player)
    {
        BPData& d = GetData(player);
        if (!g_prestigeEnable || TierFromPoints(d.points) < g_maxTier)
        {
            ChatHandler(player->GetSession()).PSendSysMessage(
                T(player, "|cffFFD700[Traumpfad]|r Prestige geht erst auf Stufe {}!",
                          "|cffFFD700[Dream Path]|r Prestige unlocks at tier {}!"), g_maxTier);
            return;
        }
        if (d.prestige >= g_prestigeMax)
        {
            ChatHandler(player->GetSession()).PSendSysMessage(
                T(player, "|cffFF8800[Traumpfad]|r Maximales Prestige {} erreicht — du bist eine Legende!",
                          "|cffFF8800[Dream Path]|r Maximum prestige {} reached — you are a legend!"), g_prestigeMax);
            return;
        }

        ClaimDue(player);
        d.points = 0;
        d.claimedTier = 0;
        d.claimedEpic = 0;
        ++d.prestige;
        SaveData(player, d);

        // Prestige-Belohnung: Gold (steigt mit jedem Prestige) + Traumschmiede-Punkte
        uint32 gold = g_prestigeGoldBase + g_prestigeGoldPer * (d.prestige - 1);
        player->ModifyMoney(static_cast<int32>(gold));
        ChatHandler(player->GetSession()).PSendSysMessage(
            T(player, "|cffFFD700[Traumpfad]|r Prestige-Belohnung: |cffFFD700{} Gold|r + |cff00FF00{} Traumschmiede-Punkte|r (Prestige-Tab)!",
                      "|cffFFD700[Dream Path]|r Prestige reward: |cffFFD700{} gold|r + |cff00FF00{} Dream Forge points|r (Prestige tab)!"),
            gold / 10000, g_paragonPtsPer);

        std::ostringstream msg;
        msg << "|cffFFD700[Traumpfad]|r |cff00CCFF" << player->GetName()
            << "|r hat |cffFF8800Prestige " << d.prestige << " / " << g_prestigeMax << "|r erreicht! (+"
            << (d.prestige * g_legacyPct) << "% Saison-Erbe, +" << (d.prestige * g_prestigeXPPct)
            << "% Erfahrung — aber die Gegner werden stärker!)";
        ChatHandler(nullptr).SendGlobalSysMessage(msg.str().c_str());

        SeasonPass::AchProgress(player, SeasonPass::ACH_PRESTIGE, d.prestige);
        SeasonPass::SendSync(player);
        SendParagonSync(player);
    }

    void SendStatus(Player* player)
    {
        BPData& d = GetData(player);
        uint32 tier = TierFromPoints(d.points);
        uint32 into = d.points - std::min(d.points, tier * g_pointsPerTier);
        ChatHandler ch(player->GetSession());
        ch.PSendSysMessage(T(player, "|cffFFD700=== Traumpfad — Saison {} ===|r",
                                     "|cffFFD700=== Dream Path — Season {} ===|r"), g_season);
        ch.PSendSysMessage(T(player, "Stufe: |cff00FF00{}|r / {}   Punkte: {} ({}/{} zur nächsten Stufe)",
                                     "Tier: |cff00FF00{}|r / {}   Points: {} ({}/{} to next tier)"),
            tier, g_maxTier, d.points, tier >= g_maxTier ? 0 : into, g_pointsPerTier);
        ch.PSendSysMessage(T(player, "Traumruhm: |cff00FF00{}|r ({}/{} bis zum nächsten Traumruhm)",
                                     "Dream Renown: |cff00FF00{}|r ({}/{} to next Dream Renown)"),
            d.renown, d.renownPoints, g_pointsPerTier);
        if (g_prestigeEnable && d.prestige)
            ch.PSendSysMessage(T(player, "|cffFF8800Prestige {}|r (Saison-Erbe: +{}% Punkte)",
                                         "|cffFF8800Prestige {}|r (Season Legacy: +{}% points)"),
                d.prestige, d.prestige * g_legacyPct);
        ch.PSendSysMessage(T(player, "Login-Serie: {} Tag(e)   Kistenfieber: +{}%",
                                     "Streak: {} day(s)   Chest Fever: +{}%"),
            d.streak, d.chestPity * g_chestPityStep);
        if (Mutator())
            ch.PSendSysMessage(T(player, "Wochen-Mutator: |cffFF8800{}|r", "Weekly mutator: |cffFF8800{}|r"),
                SeasonPass::ActiveMutatorName(player).c_str());
        if (SeasonPass::StormActive())
            ch.SendSysMessage(T(player, "|cff00CCFFTraumsturm aktiv: dreifache Punkte!|r",
                                        "|cff00CCFFDream storm active: triple points!|r"));
        if (IsWeekend())
            ch.PSendSysMessage(T(player, "|cff00FF00Bonus-Wochenende aktiv: {}% Punkte, {}% XP!|r",
                                         "|cff00FF00Bonus weekend active: {}% points, {}% XP!|r"),
                g_weekendPoints, g_weekendXP);
        if (uint32 zone = SeasonPass::ActiveEventZone())
        {
            (void)zone;
            ch.PSendSysMessage(T(player, "Aktive Eventzone: |cff00CCFF{}|r (doppelte Punkte!)",
                                         "Active event zone: |cff00CCFF{}|r (double points!)"),
                SeasonPass::ActiveEventZoneName(player).c_str());
        }
        uint32 due = (tier - d.claimedTier) + (tier - d.claimedEpic);
        if (due > 0)
            ch.PSendSysMessage(T(player, "|cffFFA500{} Belohnung(en) abholbar!|r",
                                         "|cffFFA500{} reward(s) ready to claim!|r"), due);
    }
}

// ---------------------------------------------------------------------------
//  Gossip-NPC: Chronistin Elenya
// ---------------------------------------------------------------------------
class npc_seasonpass : public CreatureScript
{
public:
    npc_seasonpass() : CreatureScript("npc_seasonpass") { }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        if (!g_enabled)
            return false;

        BPData& d = GetData(player);
        uint32 tier = TierFromPoints(d.points);
        bool en = SeasonPass::GetLang(player) == 1;

        std::ostringstream head;
        head << "|cffFFD700Traumpfad — " << (en ? "Season " : "Saison ") << g_season << "|r\n"
             << (en ? "Tier " : "Stufe ") << tier << " / " << g_maxTier << "  (" << d.points << (en ? " points)" : " Punkte)");
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, head.str(), GOSSIP_SENDER_MAIN, 1);

        uint32 due = (tier - d.claimedTier) + (tier - d.claimedEpic);
        if (due > 0)
        {
            std::ostringstream claim;
            claim << "|cff00FF00" << (en ? "Claim rewards (" : "Belohnungen abholen (") << due << (en ? " due)|r" : " fällig)|r");
            AddGossipItemFor(player, GOSSIP_ICON_MONEY_BAG, claim.str(), GOSSIP_SENDER_MAIN, 2);
        }

        AddGossipItemFor(player, GOSSIP_ICON_CHAT, en ? "Show weekly goals" : "Wochenziele anzeigen", GOSSIP_SENDER_MAIN, 4);

        AddGossipItemFor(player, GOSSIP_ICON_CHAT, en ? "Sprache: Deutsch" : "Language: English", GOSSIP_SENDER_MAIN, 8);

        if (g_prestigeEnable && tier >= g_maxTier)
            AddGossipItemFor(player, GOSSIP_ICON_BATTLE,
                en ? "|cffFF8800Prestige: restart the pass, earn a star|r"
                   : "|cffFF8800Prestige: Pass zurücksetzen und Stern verdienen|r", GOSSIP_SENDER_MAIN, 6);

        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 /*sender*/, uint32 action) override
    {
        ClearGossipMenuFor(player);
        ChatHandler ch(player->GetSession());
        bool en = SeasonPass::GetLang(player) == 1;

        switch (action)
        {
            case 2:
                if (!ClaimDue(player))
                    ch.SendSysMessage(T(player, "|cffFFD700[Traumpfad]|r Nichts abzuholen.",
                                                "|cffFFD700[Dream Path]|r Nothing to claim."));
                SeasonPass::SendSync(player);
                break;
            case 4:
                SeasonPass::SendWeeklyStatus(player);
                break;
            case 6:
                ch.SendSysMessage(T(player,
                    "|cffFFD700[Traumpfad]|r Prestige setzt Punkte und Abholstand auf 0 (Belohnungen behältst du). Sicher?",
                    "|cffFFD700[Dream Path]|r Prestige resets points and claims to 0 (you keep all rewards). Sure?"));
                AddGossipItemFor(player, GOSSIP_ICON_BATTLE,
                    en ? "|cffFF0000Yes, prestige now!|r" : "|cffFF0000Ja, Prestige jetzt!|r", GOSSIP_SENDER_MAIN, 7);
                AddGossipItemFor(player, GOSSIP_ICON_CHAT, en ? "Maybe not." : "Lieber nicht.", GOSSIP_SENDER_MAIN, 1);
                SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
                return true;
            case 7:
                DoPrestige(player);
                break;
            case 8:
                SeasonPass::SetLang(player, en ? 0 : 1);
                SeasonPass::SendSync(player);
                break;
            default:
                SendStatus(player);
                break;
        }
        CloseGossipMenuFor(player);
        return true;
    }
};

// ---------------------------------------------------------------------------
//  Befehle
// ---------------------------------------------------------------------------
using namespace Acore::ChatCommands;

class SeasonPassCommand : public CommandScript
{
public:
    SeasonPassCommand() : CommandScript("SeasonPassCommand") { }

    ChatCommandTable GetCommands() const override
    {
        static ChatCommandTable bpTable =
        {
            { "claim",     HandleClaim,     SEC_PLAYER,     Console::No },
            { "sync",      HandleSync,      SEC_PLAYER,     Console::No },
            { "weekly",    HandleWeekly,    SEC_PLAYER,     Console::No },
            { "lang",      HandleLang,      SEC_PLAYER,     Console::No },
            { "reroll",    HandleReroll,    SEC_PLAYER,     Console::No },
            { "rune",      HandleRune,      SEC_PLAYER,     Console::No },
            { "buy",       HandleBuy,       SEC_PLAYER,     Console::No },
            { "welcome",   HandleWelcome,   SEC_PLAYER,     Console::No },
            { "deliver",   HandleDeliver,   SEC_PLAYER,     Console::No },
            { "startrune", HandleStartRune, SEC_PLAYER,     Console::No },
            { "prestige",  HandlePrestige,  SEC_PLAYER,     Console::No },
            { "paragon",   HandleParagon,   SEC_PLAYER,     Console::No },
            { "addpoints", HandleAddPoints, SEC_GAMEMASTER, Console::No },
            { "chest",     HandleChest,     SEC_GAMEMASTER, Console::No },
            { "",          HandleStatus,    SEC_PLAYER,     Console::No },
        };
        static ChatCommandTable root =
        {
            { "bp", bpTable },
        };
        return root;
    }

    static bool HandleStatus(ChatHandler* handler)
    {
        if (Player* player = handler->GetPlayer())
            if (g_enabled)
                SendStatus(player);
        return true;
    }

    static bool HandleClaim(ChatHandler* handler)
    {
        Player* player = handler->GetPlayer();
        if (!player || !g_enabled)
            return true;
        if (!ClaimDue(player))
            handler->SendSysMessage(T(player, "|cffFFD700[Traumpfad]|r Nichts abzuholen.",
                                              "|cffFFD700[Dream Path]|r Nothing to claim."));
        SeasonPass::SendSync(player);
        return true;
    }

    static bool HandleSync(ChatHandler* handler)
    {
        Player* player = handler->GetPlayer();
        if (!player || !g_enabled)
            return true;
        SeasonPass::SendSync(player);
        SeasonPass::SendWeeklySync(player);
        SeasonPass::SendRuneSync(player);
        SeasonPass::SendEventSync(player);
        SeasonPass::SendAchSync(player);
        SendSupplySync(player);
        SendFishSync(player);
        SendParagonSync(player);
        return true;
    }

    static bool HandleWeekly(ChatHandler* handler)
    {
        if (Player* player = handler->GetPlayer())
            if (g_enabled)
                SeasonPass::SendWeeklyStatus(player);
        return true;
    }

    static bool HandleLang(ChatHandler* handler, std::string lang)
    {
        Player* player = handler->GetPlayer();
        if (!player || !g_enabled)
            return true;
        if (lang == "en" || lang == "english" || lang == "englisch")
            SeasonPass::SetLang(player, 1);
        else if (lang == "de" || lang == "deutsch" || lang == "german")
            SeasonPass::SetLang(player, 0);
        else
            handler->SendSysMessage("|cffFFD700[Traumpfad]|r .bp lang de | en");
        return true;
    }

    static bool HandleReroll(ChatHandler* handler, uint32 slot)
    {
        Player* player = handler->GetPlayer();
        if (!player || !g_enabled || slot < 1 || slot > 3)
            return true;
        SeasonPass::RerollWeekly(player, slot - 1);
        return true;
    }

    static bool HandleRune(ChatHandler* handler, uint32 runeId)
    {
        Player* player = handler->GetPlayer();
        if (player && g_enabled)
            SeasonPass::ToggleRune(player, runeId);
        return true;
    }

    static bool HandleWelcome(ChatHandler* handler)
    {
        Player* player = handler->GetPlayer();
        if (player && g_enabled)
            ClaimWelcome(player);
        return true;
    }

    static bool HandleStartRune(ChatHandler* handler, uint32 runeId)
    {
        Player* player = handler->GetPlayer();
        if (!player || !g_enabled)
            return true;

        BPData& d = GetData(player);
        if (d.startRune != 0)
        {
            handler->SendSysMessage(T(player,
                "|cffFFD700[Traumpfad]|r Du hast deine Startfähigkeit bereits gewählt — die Wahl ist einmalig.",
                "|cffFFD700[Dream Path]|r You already chose your starting ability — the choice is one-time."));
            return true;
        }

        uint32 spell = SeasonPass::AbilityRuneSpell(runeId);
        if (!spell)
            return true;
        if (player->HasSpell(spell))
        {
            handler->SendSysMessage(T(player,
                "|cffFF0000[Traumpfad]|r Diese Fähigkeit kennt deine Klasse schon — wähl etwas Neues!",
                "|cffFF0000[Dream Path]|r Your class already knows that ability — pick something new!"));
            return true;
        }

        d.startRune = runeId;
        SaveData(player, d);
        player->learnSpell(spell);
        handler->SendSysMessage(T(player,
            "|cffFFD700[Traumpfad]|r |cffA335EEStartfähigkeit erlernt — schau ins Zauberbuch!|r Sie gehört dir dauerhaft und belegt keinen Runenslot.",
            "|cffFFD700[Dream Path]|r |cffA335EEStarting ability learned — check your spellbook!|r It is permanent and does not use a rune slot."));
        SeasonPass::SendRuneSync(player);
        return true;
    }

    static bool HandleDeliver(ChatHandler* handler)
    {
        Player* player = handler->GetPlayer();
        if (!player || !g_enabled)
            return true;

        BPSupply const* s = ActiveSupply();
        if (!s)
            return true;

        BPData& d = GetData(player);
        if (d.supplyDay == CurrentDay())
        {
            handler->SendSysMessage(T(player,
                "|cffFFD700[Traumpfad]|r Heutiger Versorgungsauftrag schon erledigt — morgen wartet der nächste!",
                "|cffFFD700[Dream Path]|r Today's supply run is done — the next one arrives tomorrow!"));
            return true;
        }

        ItemTemplate const* t = sObjectMgr->GetItemTemplate(s->item);
        if (!player->HasItemCount(s->item, s->count))
        {
            handler->PSendSysMessage(T(player,
                "|cffFF0000[Traumpfad]|r Dir fehlen Waren: {}x {} benötigt.",
                "|cffFF0000[Dream Path]|r You are missing goods: {}x {} required."),
                s->count, t ? t->Name1.c_str() : "?");
            return true;
        }

        player->DestroyItemCount(s->item, s->count, true);
        d.supplyDay = CurrentDay();
        SaveData(player, d);
        player->ModifyMoney(static_cast<int32>(s->gold));
        SeasonPass::AddPoints(player, s->points, T(player, "Versorgungsauftrag", "Supply run"));
        SeasonPass::AchProgress(player, SeasonPass::ACH_SUPPLY, 1);
        handler->PSendSysMessage(T(player,
            "|cffFFD700[Traumpfad]|r Lieferung angenommen! |cff00FF00+{} Punkte|r und |cffFFD700{} Gold|r.",
            "|cffFFD700[Dream Path]|r Delivery accepted! |cff00FF00+{} points|r and |cffFFD700{} gold|r."),
            s->points, s->gold / 10000);
        SendSupplySync(player);
        SeasonPass::SendSync(player);
        return true;
    }

    static bool HandleBuy(ChatHandler* handler, uint32 slot)
    {
        Player* player = handler->GetPlayer();
        if (!player || !g_enabled)
            return true;
        if (slot < 1 || slot > g_shop.size())
            return true;

        BPShopEntry const& e = g_shop[slot - 1];

        if (player->GetMoney() < e.price)
        {
            handler->SendSysMessage(T(player, "|cffFF0000[Traumpfad]|r Nicht genug Gold.",
                                              "|cffFF0000[Dream Path]|r Not enough gold."));
            return true;
        }

        if (e.kind == 1) // Mystery-Box: öffnet direkt eine Zufallskiste
        {
            player->ModifyMoney(-static_cast<int32>(e.price));
            handler->SendSysMessage(T(player,
                "|cffFFD700[Traumpfad]|r |cffA335EEMystery-Box gekauft — mal sehen, was drin ist ...|r",
                "|cffFFD700[Dream Path]|r |cffA335EEMystery box purchased — let's see what's inside ...|r"));
            SeasonPass::OpenChest(player, static_cast<uint8>(e.item));
            return true;
        }

        ItemTemplate const* t = sObjectMgr->GetItemTemplate(e.item);
        if (!t)
            return true;

        player->ModifyMoney(-static_cast<int32>(e.price));
        GrantItemOrMail(player, e.item, e.count);
        handler->PSendSysMessage(T(player, "|cffFFD700[Traumpfad]|r Gekauft: |cff00FF00{}x {}|r",
                                           "|cffFFD700[Dream Path]|r Purchased: |cff00FF00{}x {}|r"),
            e.count, t->Name1.c_str());
        return true;
    }

    static bool HandlePrestige(ChatHandler* handler, Optional<std::string> confirm)
    {
        Player* player = handler->GetPlayer();
        if (!player || !g_enabled)
            return true;
        if (!confirm || (*confirm != "ja" && *confirm != "yes"))
        {
            handler->SendSysMessage(T(player,
                "|cffFFD700[Traumpfad]|r Prestige setzt Punkte und Abholstand auf 0 (Belohnungen bleiben!). Bestätigen mit: .bp prestige ja",
                "|cffFFD700[Dream Path]|r Prestige resets points and claims to 0 (rewards stay!). Confirm with: .bp prestige yes"));
            return true;
        }
        DoPrestige(player);
        return true;
    }

    // .bp paragon <1-8> [Anzahl]  |  .bp paragon reset
    static bool HandleParagon(ChatHandler* handler, Optional<std::string> arg, Optional<uint32> num)
    {
        Player* player = handler->GetPlayer();
        if (!player || !g_enabled || !g_internalParagonEnable)
            return true;
        if (!arg)
        {
            SendParagonSync(player);
            return true;
        }
        if (*arg == "reset")
        {
            ResetParagon(player);
            return true;
        }
        uint32 stat = static_cast<uint32>(atoi(arg->c_str()));
        SpendParagon(player, stat, num ? *num : 1);
        return true;
    }

    static bool HandleAddPoints(ChatHandler* handler, uint32 amount)
    {
        Player* player = handler->GetPlayer();
        if (!player || !g_enabled)
            return true;
        SeasonPass::AddPoints(player, amount, "GM");
        SeasonPass::SendSync(player);
        handler->PSendSysMessage("[Traumpfad] +{}.", amount);
        return true;
    }

    static bool HandleChest(ChatHandler* handler, uint32 tier)
    {
        Player* player = handler->GetPlayer();
        if (!player || !g_enabled)
            return true;
        SeasonPass::OpenChest(player, static_cast<uint8>(tier));
        return true;
    }
};

// ---------------------------------------------------------------------------
//  Traumschmiede-Kampfskalierung: Paragon-Boni des Spielers und
//  Gegnerskalierung pro Prestige (mehr Schaden, mehr effektives Leben)
// ---------------------------------------------------------------------------
class SeasonPassParagonUnit : public UnitScript
{
public:
    SeasonPassParagonUnit() : UnitScript("SeasonPassParagonUnit") { }

    static void Adjust(Unit* target, Unit* attacker, uint32& damage, SpellInfo const* spellInfo, bool periodic)
    {
        if (!damage || !target || !attacker || target == attacker)
            return;
        Player* pAtt = attacker->GetCharmerOrOwnerPlayerOrPlayerItself();
        Player* pVic = target->GetCharmerOrOwnerPlayerOrPlayerItself();
        if (pAtt && !pVic) // Spieler (oder Pet) trifft Kreatur
        {
            if (!SeasonPass::IsTracked(pAtt))
                return;
            uint32 bonus = SeasonPass::EngravedBuffRunes(pAtt) * g_runeResonance; // Runenresonanz
            if (g_internalParagonEnable)
            {
                BPParagon& pg = GetParagon(pAtt);
                if (spellInfo)
                {
                    bonus += pg.pts[2] * PG_PER[2];      // Zauberkunst
                    if (spellInfo->IsAffectingArea())
                        bonus += pg.pts[3] * PG_PER[3];  // Flächenwirkung
                }
                else
                    bonus += pg.pts[1] * PG_PER[1];      // Macht (Autohiebe)
                if (periodic)
                    bonus += pg.pts[4] * PG_PER[4];      // Toxine (DoTs)
            }
            if (bonus)
                damage += damage * bonus / 100;
            uint32 prest = GetData(pAtt).prestige;   // Gegner: mehr effektives Leben
            if (g_prestigeMobScalingEnable && g_prestigeEnable && prest && g_mobScalePct)
                damage = damage * 100 / (100 + prest * g_mobScalePct);
        }
        else if (pVic && !pAtt) // Kreatur trifft Spieler (oder Pet)
        {
            uint32 prest = GetData(pVic).prestige;   // Gegner: mehr Schaden
            if (g_prestigeMobScalingEnable && g_prestigeEnable && prest && g_mobScalePct)
                damage += damage * (prest * g_mobScalePct) / 100;
        }
    }

    void ModifyMeleeDamage(Unit* target, Unit* attacker, uint32& damage) override
    {
        Adjust(target, attacker, damage, nullptr, false);
    }

    void ModifySpellDamageTaken(Unit* target, Unit* attacker, int32& damage, SpellInfo const* spellInfo) override
    {
        if (damage <= 0)
            return;
        uint32 dmg = static_cast<uint32>(damage);
        Adjust(target, attacker, dmg, spellInfo, false);
        damage = static_cast<int32>(dmg);
    }

    void ModifyPeriodicDamageAurasTick(Unit* target, Unit* attacker, uint32& damage, SpellInfo const* spellInfo) override
    {
        Adjust(target, attacker, damage, spellInfo, true);
    }

    void ModifyHealReceived(Unit* /*target*/, Unit* healer, uint32& heal, SpellInfo const* /*spellInfo*/) override
    {
        Player* p = healer ? healer->GetCharmerOrOwnerPlayerOrPlayerItself() : nullptr;
        if (!p || !SeasonPass::IsTracked(p))
            return;
        uint32 pct = SeasonPass::EngravedBuffRunes(p) * g_runeResonance; // Runenresonanz
        if (g_internalParagonEnable)
            pct += GetParagon(p).pts[7] * PG_PER[7];                    // Heilkunst
        if (pct)
            heal += heal * pct / 100;
    }
};

void AddSC_SeasonPass()
{
    new SeasonPassWorld();
    new SeasonPassPlayer();
    new SeasonPassParagonUnit();
    new npc_seasonpass();
    new SeasonPassCommand();
}
