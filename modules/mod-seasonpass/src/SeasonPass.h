/*
 * mod-seasonpass v4 — gemeinsame Schnittstelle zwischen Kern (SeasonPass.cpp),
 * Saison-Erweiterung (SeasonPassSeason.cpp).
 */

#ifndef MOD_SEASONPASS_H
#define MOD_SEASONPASS_H

#include "Define.h"
#include "progression_events.h"

#include <string>

class Player;

namespace SeasonPass
{
    // --- vom Kern (SeasonPass.cpp) bereitgestellt ---
    void   AddPoints(Player* player, uint32 amount, char const* reason);
    bool   IsTracked(Player* player);
    uint32 GetSeason();
    uint32 GetTier(Player* player);
    void   SendSync(Player* player);

    // Sprache: 0 = Deutsch, 1 = Englisch (pro Charakter, persistent)
    uint8  GetLang(Player* player);
    void   SetLang(Player* player, uint8 lang);

    // Zufallskisten (tier 1-3), Kistenfieber-Pity inklusive
    void   OpenChest(Player* player, uint8 chestTier);

    // Wochen-Mutator (Open-World-Affix): kind 0=Quest 1=Elite 2=Rare 3=PvP/Duell
    // 4=XP 5=Kistenchance 6=Wochenziel-Punkte 7=Entdeckungen; value in Prozent
    uint8       ActiveMutatorKind();
    uint32      ActiveMutatorValue();
    std::string ActiveMutatorName(Player* player);

    // Traumsturm (15-Minuten-Zufallsevent, Punkte x3)
    bool StormActive();

    // --- von der Saison-Erweiterung (SeasonPassSeason.cpp) bereitgestellt ---
    enum WeeklyType : uint8
    {
        WK_KILLS     = 0,
        WK_ELITE     = 1,
        WK_BOSS      = 2,
        WK_QUESTS    = 3,
        WK_LEVELUPS  = 4,
        WK_PVPKILLS  = 5,
        WK_DUELWINS  = 6,
        WK_RARES     = 7,
        WK_POINTS    = 8,
        WK_DISCOVER  = 9,
        WK_ZONEKILLS = 10,
        WK_BOUNTY    = 11,
        WK_WORLDBOSS = 12
    };

    enum AchKind : uint8
    {
        ACH_BOSS     = 0,
        ACH_BOUNTY   = 1,
        ACH_RUNE     = 2,
        ACH_WEEKLY   = 3,
        ACH_DUEL     = 4,
        ACH_RARE     = 5,
        ACH_DUNGEON  = 6,
        ACH_TIER     = 7,  // Hoechststand
        ACH_PRESTIGE = 8,  // Hoechststand
        ACH_STREAK   = 9,  // Hoechststand
        ACH_DISCOVER = 10,
        ACH_HARDCORE = 11, // Hardcore-Herausforderung bestanden
        ACH_SUPPLY   = 12, // Versorgungsauftraege
        ACH_CHEST    = 13  // Traumkisten geoeffnet
    };

    void WeeklyProgress(Player* player, WeeklyType type, uint32 value);
    void HandleDungeonEvent(Progression::DungeonEvent const& event);
    void AchProgress(Player* player, AchKind kind, uint32 value);
    bool RerollWeekly(Player* player, uint32 slot); // Traumtausch: 1x pro Woche
    bool ToggleRune(Player* player, uint32 runeId); // Gravieren/Entfernen ohne NPC
    bool TeleportTo(Player* player, uint32 destId); // 999 = aktiver Weltboss
    uint32 AbilityRuneSpell(uint32 runeId);         // Zauber einer Fähigkeits-Rune (0 = keine)
    uint32 GetStartRune(Player* player);            // gewählte Startfähigkeit (Kern)
    uint32 RandomUnknownRuneSpell(Player* player);  // Verlorene Rune aus Kisten (0 = alle bekannt)
    uint32 EngravedBuffRunes(Player* player);       // Anzahl gravierter Dauerbuff-Runen (Runenresonanz)

    void SendWeeklySync(Player* player);
    void SendWeeklyStatus(Player* player);
    void SendRuneSync(Player* player);
    void SendEventSync(Player* player);
    void SendAchSync(Player* player);

    uint32      ActiveEventZone();
    std::string ActiveEventZoneName(Player* player);

    bool OnWorldBossKilled(Player* player, uint32 entry);

    // Kleiner Uebersetzungshelfer fuer Spielernachrichten
    inline char const* T(Player* player, char const* de, char const* en)
    {
        return GetLang(player) == 1 ? en : de;
    }
}

#endif // MOD_SEASONPASS_H
