/*
 * CoA Dev Menu - server side of the in-game NPC/creature editor (client addon: DevMenu).
 *
 * Transport: the addon whispers itself an addon message "CDEV\tQ~OP~arg~arg...".
 * Replies go back the same way ("CDEV\t<CODE>~field~field..."). GM accounts only.
 * Every edit is written to the world DB and applied live (no restart needed),
 * except equipment of a freshly cloned template, which loads after a restart.
 */

#include "CellImpl.h"
#include "Chat.h"
#include "Config.h"
#include "Creature.h"
#include "CreatureData.h"
#include "DatabaseEnv.h"
#include "DBCStores.h"
#include "GameEventMgr.h"
#include "GameTime.h"
#include "WorldSessionMgr.h"
#include "ReputationMgr.h"
#include "GridNotifiers.h"
#include "GridNotifiersImpl.h"
#include "Log.h"
#include "Map.h"
#include "MotionMaster.h"
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "PlayerScript.h"
#include "ScriptMgr.h"
#include "TemporarySummon.h"
#include "WaypointMgr.h"
#include "WorldPacket.h"
#include "WorldSession.h"
#include "GameObject.h"
#include "SmartScriptMgr.h"
#include "Spell.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include "Transport.h"
#include "QuestDef.h"
#include <G3D/Matrix3.h>
#include <set>
#include <mutex>
#include "WorldScript.h"
#include "ServerScript.h"
#include "Opcodes.h"
#include <algorithm>
#include <atomic>
#include <map>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <functional>
#include <sstream>
#include <unordered_map>
#include <vector>

namespace
{
    constexpr char const* PREFIX = "CDEV";
    constexpr uint32 CLONE_FIRST = 9980001;   // entries made by "make unique"
    constexpr uint32 CLONE_LAST = 9989999;
    constexpr uint32 PAGE_SIZE = 30;
    constexpr uint32 MARKER_MS = 15 * 60 * 1000;

    struct EditState
    {
        std::vector<Position> path;
        std::vector<ObjectGuid> markers;
    };
    std::unordered_map<ObjectGuid::LowType, EditState> g_state;
    std::vector<std::pair<ObjectGuid, std::string>> g_queue;   // requests waiting for the world thread
    std::mutex g_queueLock;

    void RefreshLook(Creature* c);

    std::string Clean(std::string s, size_t maxLen = 80)
    {
        for (char& c : s)
            if (c == '~' || c == '\t' || c == '|' || c == '\n' || c == '\r')
                c = ' ';
        if (s.size() > maxLen)
            s.resize(maxLen);
        return s;
    }

    std::string Lower(std::string s)
    {
        std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c) { return char(std::tolower(c)); });
        return s;
    }

    std::vector<std::string> Split(std::string const& s, char d)
    {
        std::vector<std::string> out;
        std::string cur;
        for (char c : s)
        {
            if (c == d) { out.push_back(cur); cur.clear(); }
            else cur += c;
        }
        out.push_back(cur);
        return out;
    }

    uint32 U(std::vector<std::string> const& a, size_t i, uint32 def = 0)
    {
        if (i >= a.size() || a[i].empty())
            return def;
        return uint32(std::strtoul(a[i].c_str(), nullptr, 10));
    }

    float F(std::vector<std::string> const& a, size_t i, float def = 0.f)
    {
        if (i >= a.size() || a[i].empty())
            return def;
        return std::strtof(a[i].c_str(), nullptr);
    }

    std::string S(std::vector<std::string> const& a, size_t i)
    {
        return i < a.size() ? a[i] : std::string();
    }

    template <typename... Args>
    std::string Join(Args const&... args)
    {
        std::ostringstream ss;
        ss.setf(std::ios::fixed);
        ss.precision(2);
        bool first = true;
        ((ss << (first ? "" : "~") << args, first = false), ...);
        return ss.str();
    }

    void Send(Player* p, std::string const& text)
    {
        WorldPacket data;
        ChatHandler::BuildChatPacket(data, CHAT_MSG_WHISPER, LANG_ADDON, p, p, std::string(PREFIX) + "\t" + text);
        p->GetSession()->SendPacket(&data);
    }

    void Ok(Player* p, std::string const& msg) { Send(p, Join("OK", Clean(msg, 200))); }
    void Err(Player* p, std::string const& msg) { Send(p, Join("ER", Clean(msg, 200))); }

    char Reaction(CreatureTemplate const* ct)
    {
        if (ct->type == CREATURE_TYPE_CRITTER)
            return 'C';
        FactionTemplateEntry const* ft = sFactionTemplateStore.LookupEntry(ct->faction);
        if (!ft)
            return 'N';
        if (ft->IsHostileToPlayers())
            return 'H';
        if (ft->IsNeutralToAll())
            return 'N';
        return 'F';
    }

    // Warm the client's creature cache so names and the Ctrl+click 3D preview work instantly
    void SendQuery(Player* p, CreatureTemplate const* ct)
    {
        WorldPacket pkt(ct->queryData);
        p->GetSession()->SendPacket(&pkt);
    }

    CreatureTemplate* MutableTemplate(uint32 entry)
    {
        return const_cast<CreatureTemplate*>(sObjectMgr->GetCreatureTemplate(entry));
    }

    Creature* FindSpawn(Player* p, ObjectGuid::LowType guid)
    {
        ChatHandler handler(p->GetSession());
        return handler.GetCreatureFromPlayerMapByDbGuid(guid);
    }

    uint32 CountSpawnsOfEntry(uint32 entry)
    {
        if (QueryResult r = WorldDatabase.Query("SELECT COUNT(*) FROM creature WHERE id = {}", entry))
            return r->Fetch()[0].Get<uint32>();
        return 0;
    }

    void RestartMovement(Creature* c)
    {
        c->GetMotionMaster()->Initialize();
        if (c->IsAlive())
        {
            c->setDeathState(DeathState::JustDied);
            c->Respawn(true);
        }
    }

    void SendInfo(Player* p, Creature* c)
    {
        CreatureTemplate const* ct = c->GetCreatureTemplate();
        CreatureData const* d = sObjectMgr->GetCreatureData(c->GetSpawnId());
        uint32 pathId = c->GetWaypointPath();
        uint32 pts = 0;
        if (pathId)
            if (WaypointPath const* wp = sWaypointMgr->GetPath(pathId))
                pts = uint32(wp->Nodes.size());
        uint32 emote = c->GetUInt32Value(UNIT_NPC_EMOTESTATE);
        SendQuery(p, ct);
        Send(p, Join("IN", c->GetSpawnId(), c->GetEntry(), Clean(ct->Name, 60), Clean(ct->SubName, 60),
            c->GetPositionX(), c->GetPositionY(), c->GetPositionZ(), c->GetOrientation(),
            uint32(c->GetDefaultMovementType()), c->GetWanderDistance(), emote, c->GetNpcFlags(),
            ct->faction, pathId, pts, uint32(ct->minlevel), uint32(ct->maxlevel), c->GetDisplayId(),
            d ? d->spawntimesecs : 0, std::string(1, Reaction(ct)), (ct->flags_extra & CREATURE_FLAG_EXTRA_GUARD) ? 1 : 0,
            CountSpawnsOfEntry(c->GetEntry()), ct->npcflag));
    }

    void ClearMarkers(Player* p, EditState& st)
    {
        for (ObjectGuid const& g : st.markers)
            if (Creature* m = ObjectAccessor::GetCreature(*p, g))
                m->DespawnOrUnsummon();
        st.markers.clear();
    }

    void AddMarker(Player* p, EditState& st, Position const& pos)
    {
        if (TempSummon* m = p->SummonCreature(VISUAL_WAYPOINT, pos.GetPositionX(), pos.GetPositionY(), pos.GetPositionZ(), pos.GetOrientation(), TEMPSUMMON_TIMED_DESPAWN, MARKER_MS))
            st.markers.push_back(m->GetGUID());
    }

    // Writes creature_addon and updates the in-memory copy without any core change:
    // edit the existing entry in place, or (first edit of this spawn) reload the table.
    // Chat packets are handled in the world thread while maps are idle, so the reload is safe.
    void SaveAddon(ObjectGuid::LowType guid, uint32 pathId, uint32 emote, bool setPath, bool setEmote)
    {
        WorldDatabase.DirectExecute("INSERT IGNORE INTO creature_addon (guid) VALUES ({})", guid);
        if (setPath)
            WorldDatabase.DirectExecute("UPDATE creature_addon SET path_id = {} WHERE guid = {}", pathId, guid);
        if (setEmote)
            WorldDatabase.DirectExecute("UPDATE creature_addon SET emote = {} WHERE guid = {}", emote, guid);
        if (CreatureAddon const* a = sObjectMgr->GetCreatureAddon(guid))
        {
            CreatureAddon* m = const_cast<CreatureAddon*>(a);
            if (setPath) m->path_id = pathId;
            if (setEmote) m->emote = emote;
        }
        else
            sObjectMgr->LoadCreatureAddons();
    }

    // Copies a creature_template (DB + memory) into the dev clone range; returns the new entry or 0
    uint32 CloneTemplate(uint32 base)
    {
        CreatureTemplate const* src = sObjectMgr->GetCreatureTemplate(base);
        if (!src)
            return 0;

        uint32 entry = CLONE_FIRST;
        if (QueryResult r = WorldDatabase.Query("SELECT MAX(entry) FROM creature_template WHERE entry BETWEEN {} AND {}", CLONE_FIRST, CLONE_LAST))
            if (!r->Fetch()[0].IsNull())
                entry = r->Fetch()[0].Get<uint32>() + 1;
        while (entry <= CLONE_LAST && sObjectMgr->GetCreatureTemplate(entry))
            ++entry;
        if (entry > CLONE_LAST)
            return 0;

        auto copyRows = [&](char const* table, char const* keyCol)
        {
            QueryResult cols = WorldDatabase.Query("SHOW COLUMNS FROM `{}`", table);
            if (!cols)
                return;
            std::string colList, selList;
            do
            {
                std::string c = cols->Fetch()[0].Get<std::string>();
                if (!colList.empty()) { colList += ","; selList += ","; }
                colList += "`" + c + "`";
                selList += (c == keyCol) ? std::to_string(entry) : "`" + c + "`";
            } while (cols->NextRow());
            WorldDatabase.DirectExecute("INSERT INTO `{}` ({}) SELECT {} FROM `{}` WHERE `{}` = {}", table, colList, selList, table, keyCol, base);
        };
        copyRows("creature_template", "entry");
        copyRows("creature_template_model", "CreatureID");
        copyRows("creature_equip_template", "CreatureID");

        WorldDatabasePreparedStatement* stmt = WorldDatabase.GetPreparedStatement(WORLD_SEL_CREATURE_TEMPLATE);
        stmt->SetData(0, entry);
        PreparedQueryResult res = WorldDatabase.Query(stmt);
        if (!res)
            return 0;
        sObjectMgr->LoadCreatureTemplate(res->Fetch(), true);

        CreatureTemplate* dst = MutableTemplate(entry);
        if (!dst)
            return 0;
        dst->Models = src->Models;
        for (uint8 i = 0; i < MAX_SPELL_SCHOOL; ++i)
            dst->resistance[i] = src->resistance[i];
        for (uint8 i = 0; i < MAX_CREATURE_SPELLS; ++i)
            dst->spells[i] = src->spells[i];
        sObjectMgr->CheckCreatureTemplate(dst);
        dst->InitializeQueryData();

        if (VendorItemData const* vendor = sObjectMgr->GetNpcVendorItemList(base))
            for (VendorItem const* vi : vendor->m_items)
                if (vi)
                    sObjectMgr->AddVendorItem(entry, vi->item, vi->maxcount, vi->incrtime, vi->ExtendedCost, true);
        return entry;
    }

    // Puts the spawn on its own copy of its template so template-level edits only touch it
    Creature* MakeUnique(Player* p, Creature* c)
    {
        uint32 newEntry = CloneTemplate(c->GetEntry());
        if (!newEntry)
        {
            Err(p, "Could not copy the template (dev entry range full?)");
            return nullptr;
        }
        c->UpdateEntry(newEntry, nullptr, true, true);
        c->SaveToDB();
        return c;
    }

    void ApplyTemplateChange(Player* p, CreatureTemplate* ct)
    {
        ct->InitializeQueryData();
        SendQuery(p, ct);
    }

    // ---------------------------------------------------------------- handlers
    void OpSearch(Player* p, std::vector<std::string> const& a)
    {
        std::string q = Lower(S(a, 2));
        uint32 page = U(a, 3);
        uint32 filter = U(a, 4);   // 0 all, 1 friendly, 2 hostile, 3 neutral, 4 critter, 5 vendors/services, 6 dev made
        uint32 qEntry = uint32(std::strtoul(q.c_str(), nullptr, 10));

        std::vector<CreatureTemplate const*> hits;
        for (auto const& [entry, ct] : *sObjectMgr->GetCreatureTemplates())
        {
            if (!q.empty() && entry != qEntry && Lower(ct.Name).find(q) == std::string::npos && Lower(ct.SubName).find(q) == std::string::npos)
                continue;
            char r = Reaction(&ct);
            switch (filter)
            {
                case 1: if (r != 'F') continue; break;
                case 2: if (r != 'H') continue; break;
                case 3: if (r != 'N') continue; break;
                case 4: if (r != 'C') continue; break;
                case 5: if (!ct.npcflag) continue; break;
                case 6: if (entry < 9900000) continue; break;
                default: break;
            }
            hits.push_back(&ct);
        }
        std::sort(hits.begin(), hits.end(), [&](CreatureTemplate const* x, CreatureTemplate const* y)
        {
            bool xe = x->Entry == qEntry, ye = y->Entry == qEntry;
            if (xe != ye) return xe;
            if (x->Name != y->Name) return x->Name < y->Name;
            return x->Entry < y->Entry;
        });
        uint32 total = uint32(hits.size());
        uint32 pages = std::max<uint32>(1, (total + PAGE_SIZE - 1) / PAGE_SIZE);
        page = std::min(page, pages - 1);
        Send(p, Join("SB", total, page, pages));
        for (uint32 i = page * PAGE_SIZE; i < std::min(total, (page + 1) * PAGE_SIZE); ++i)
        {
            CreatureTemplate const* ct = hits[i];
            SendQuery(p, ct);
            CreatureModel const* m = ct->GetFirstValidModel();
            Send(p, Join("SR", ct->Entry, Clean(ct->Name, 60), Clean(ct->SubName, 50), uint32(ct->minlevel), uint32(ct->maxlevel),
                std::string(1, Reaction(ct)), ct->npcflag, ct->rank, ct->type, m ? m->CreatureDisplayID : 0));
        }
        Send(p, Join("SE", total, page, pages));
    }

    void OpSpawn(Player* p, std::vector<std::string> const& a)
    {
        uint32 entry = U(a, 2);
        bool save = U(a, 3, 1) != 0;
        if (!sObjectMgr->GetCreatureTemplate(entry))
            return Err(p, "Unknown creature entry " + std::to_string(entry));
        if (p->GetTransport())
            return Err(p, "Step off the transport first (use .npc add there)");

        if (!save)
        {
            p->SummonCreature(entry, p->GetPositionX(), p->GetPositionY(), p->GetPositionZ(), p->GetOrientation(), TEMPSUMMON_TIMED_DESPAWN, 5 * 60 * 1000);
            return Ok(p, "Preview spawned (despawns in 5 min, not saved)");
        }

        Map* map = p->GetMap();
        Creature* c = new Creature();
        if (!c->Create(map->GenerateLowGuid<HighGuid::Unit>(), map, p->GetPhaseMaskForSpawn(), entry, 0, p->GetPositionX(), p->GetPositionY(), p->GetPositionZ(), p->GetOrientation()))
        {
            delete c;
            return Err(p, "Create failed");
        }
        c->SaveToDB(map->GetId(), (1 << map->GetSpawnMode()), p->GetPhaseMaskForSpawn());
        ObjectGuid::LowType spawnId = c->GetSpawnId();
        c->CleanupsBeforeDelete();
        delete c;
        c = new Creature();
        if (!c->LoadCreatureFromDB(spawnId, map, true, true))
        {
            delete c;
            return Err(p, "Saved but failed to load spawn " + std::to_string(spawnId));
        }
        sObjectMgr->AddCreatureToGrid(spawnId, sObjectMgr->GetCreatureData(spawnId));
        Ok(p, "Spawned and saved (guid " + std::to_string(spawnId) + ")");
        SendInfo(p, c);
    }

    // Duplicate any NPC type into a brand-new one (new entry) with its own name; no spawn needed
    void OpDuplicate(Player* p, std::vector<std::string> const& a)
    {
        uint32 base = U(a, 2);
        std::string name = Clean(S(a, 3), 90), sub = Clean(S(a, 4), 90);
        CreatureTemplate const* src = sObjectMgr->GetCreatureTemplate(base);
        if (!src)
            return Err(p, "Unknown creature entry " + std::to_string(base));
        if (name.empty())
            name = src->Name + " (copy)";
        uint32 entry = CloneTemplate(base);
        if (!entry)
            return Err(p, "Could not duplicate (dev entry range full?)");
        CreatureTemplate* ct = MutableTemplate(entry);
        ct->Name = name;
        ct->SubName = sub;
        std::string en = name, es = sub;
        WorldDatabase.EscapeString(en);
        WorldDatabase.EscapeString(es);
        WorldDatabase.DirectExecute("UPDATE creature_template SET name = '{}', subname = '{}' WHERE entry = {}", en, es, entry);
        ApplyTemplateChange(p, ct);
        CreatureModel const* m = ct->GetFirstValidModel();
        Send(p, Join("DP", entry, Clean(ct->Name, 60), Clean(ct->SubName, 50), uint32(ct->minlevel), uint32(ct->maxlevel),
            std::string(1, Reaction(ct)), ct->npcflag, ct->rank, ct->type, m ? m->CreatureDisplayID : 0));
        Ok(p, "New NPC " + std::to_string(entry) + " created from " + std::to_string(base) + ". Spawn it, then edit it freely.");
    }

    // Rename an NPC type by entry (all its spawns), straight from a list
    void OpRenameType(Player* p, std::vector<std::string> const& a)
    {
        uint32 entry = U(a, 2);
        std::string name = Clean(S(a, 3), 90), sub = Clean(S(a, 4), 90);
        CreatureTemplate* ct = MutableTemplate(entry);
        if (!ct)
            return Err(p, "Unknown creature entry " + std::to_string(entry));
        if (name.empty())
            return Err(p, "Name can't be empty");
        ct->Name = name;
        ct->SubName = sub;
        std::string en = name, es = sub;
        WorldDatabase.EscapeString(en);
        WorldDatabase.EscapeString(es);
        WorldDatabase.DirectExecute("UPDATE creature_template SET name = '{}', subname = '{}' WHERE entry = {}", en, es, entry);
        ApplyTemplateChange(p, ct);
        CreatureModel const* m = ct->GetFirstValidModel();
        Send(p, Join("RT", entry, Clean(ct->Name, 60), Clean(ct->SubName, 50), uint32(ct->minlevel), uint32(ct->maxlevel),
            std::string(1, Reaction(ct)), ct->npcflag, ct->rank, ct->type, m ? m->CreatureDisplayID : 0));
        Ok(p, "Renamed NPC type " + std::to_string(entry) + " (" + std::to_string(CountSpawnsOfEntry(entry)) + " spawns use it)");
    }

    // ---------------- Advanced: every useful creature_template field, editable by name
    struct TField
    {
        char const* key;      // protocol key
        char const* column;   // creature_template column
        bool query;           // part of the client query packet (resend)
        std::function<double(CreatureTemplate const&)> get;
        std::function<void(CreatureTemplate&, double)> set;
    };

    std::vector<TField> const& TFields()
    {
        static std::vector<TField> const f = {
            { "minlevel", "minlevel", false, [](auto& t) { return t.minlevel; }, [](auto& t, double v) { t.minlevel = uint8(std::clamp(v, 1.0, 83.0)); } },
            { "maxlevel", "maxlevel", false, [](auto& t) { return t.maxlevel; }, [](auto& t, double v) { t.maxlevel = uint8(std::clamp(v, 1.0, 83.0)); } },
            { "faction", "faction", false, [](auto& t) { return t.faction; }, [](auto& t, double v) { t.faction = uint32(v); } },
            { "rank", "rank", true, [](auto& t) { return t.rank; }, [](auto& t, double v) { t.rank = uint32(std::clamp(v, 0.0, 4.0)); } },
            { "type", "type", true, [](auto& t) { return t.type; }, [](auto& t, double v) { t.type = uint32(v); } },
            { "family", "family", true, [](auto& t) { return t.family; }, [](auto& t, double v) { t.family = uint32(v); } },
            { "unit_class", "unit_class", false, [](auto& t) { return t.unit_class; }, [](auto& t, double v) { t.unit_class = uint32(v); } },
            { "health", "HealthModifier", false, [](auto& t) { return t.ModHealth; }, [](auto& t, double v) { t.ModHealth = float(v); } },
            { "mana", "ManaModifier", false, [](auto& t) { return t.ModMana; }, [](auto& t, double v) { t.ModMana = float(v); } },
            { "damage", "DamageModifier", false, [](auto& t) { return t.DamageModifier; }, [](auto& t, double v) { t.DamageModifier = float(v); } },
            { "armor", "ArmorModifier", false, [](auto& t) { return t.ModArmor; }, [](auto& t, double v) { t.ModArmor = float(v); } },
            { "xp", "ExperienceModifier", false, [](auto& t) { return t.ModExperience; }, [](auto& t, double v) { t.ModExperience = float(v); } },
            { "attacktime", "BaseAttackTime", false, [](auto& t) { return t.BaseAttackTime; }, [](auto& t, double v) { t.BaseAttackTime = uint32(v); } },
            { "walk", "speed_walk", false, [](auto& t) { return t.speed_walk; }, [](auto& t, double v) { t.speed_walk = float(v); } },
            { "run", "speed_run", false, [](auto& t) { return t.speed_run; }, [](auto& t, double v) { t.speed_run = float(v); } },
            { "aggro", "detection_range", false, [](auto& t) { return t.detection_range; }, [](auto& t, double v) { t.detection_range = float(v); } },
            { "hover", "HoverHeight", false, [](auto& t) { return t.HoverHeight; }, [](auto& t, double v) { t.HoverHeight = float(v); } },
            { "mingold", "mingold", false, [](auto& t) { return t.mingold; }, [](auto& t, double v) { t.mingold = uint32(v); } },
            { "maxgold", "maxgold", false, [](auto& t) { return t.maxgold; }, [](auto& t, double v) { t.maxgold = uint32(v); } },
            { "lootid", "lootid", false, [](auto& t) { return t.lootid; }, [](auto& t, double v) { t.lootid = uint32(v); } },
            { "gossip", "gossip_menu_id", false, [](auto& t) { return t.GossipMenuId; }, [](auto& t, double v) { t.GossipMenuId = uint32(v); } },
            { "regen", "RegenHealth", false, [](auto& t) { return t.RegenHealth ? 1 : 0; }, [](auto& t, double v) { t.RegenHealth = v != 0; } },
            { "unit_flags", "unit_flags", false, [](auto& t) { return t.unit_flags; }, [](auto& t, double v) { t.unit_flags = uint32(v); } },
            { "flags_extra", "flags_extra", false, [](auto& t) { return t.flags_extra; }, [](auto& t, double v) { t.flags_extra = uint32(v); } },
            { "type_flags", "type_flags", true, [](auto& t) { return t.type_flags; }, [](auto& t, double v) { t.type_flags = uint32(v); } },
            { "npcflag_tpl", "npcflag", false, [](auto& t) { return t.npcflag; }, [](auto& t, double v) { t.npcflag = uint32(v); } },
        };
        return f;
    }

    void SendAdvanced(Player* p, Creature* c)
    {
        CreatureTemplate const* ct = c->GetCreatureTemplate();
        Send(p, Join("TB", c->GetSpawnId()));
        for (TField const& f : TFields())
            Send(p, Join("TV", f.key, f.get(*ct)));
        CreatureData const* d = sObjectMgr->GetCreatureData(c->GetSpawnId());
        Send(p, Join("TV", "spawntime", d ? d->spawntimesecs : 0));
        if (ReputationOnKillEntry const* r = sObjectMgr->GetReputationOnKilEntry(c->GetEntry()))
            Send(p, Join("RP", r->RepFaction1, r->RepValue1, r->ReputationMaxCap1));
        else if (QueryResult q = WorldDatabase.Query("SELECT RewOnKillRepFaction1, RewOnKillRepValue1, MaxStanding1 FROM creature_onkill_reputation WHERE creature_id = {}", c->GetEntry()))
            Send(p, Join("RP", q->Fetch()[0].Get<uint32>(), q->Fetch()[1].Get<float>(), q->Fetch()[2].Get<uint32>()));
        else
            Send(p, Join("RP", 0, 0, 0));
        Send(p, Join("TE", c->GetSpawnId()));
    }

    void RefreshFromTemplate(Creature* c)
    {
        c->UpdateEntry(c->GetEntry(), sObjectMgr->GetCreatureData(c->GetSpawnId()), true, true);
        RestartMovement(c);
    }

    void OpTSet(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        std::string key = S(a, 3);
        auto const& fields = TFields();
        auto it = std::find_if(fields.begin(), fields.end(), [&](TField const& f) { return key == f.key; });
        if (key == "spawntime")
        {
            c->SetRespawnDelay(U(a, 4));
            c->SaveToDB();
            Ok(p, "Respawn time saved for this spawn");
            return SendAdvanced(p, c);
        }
        if (it == fields.end())
            return Err(p, "Unknown field " + Clean(key, 30));
        double v = std::strtod(S(a, 4).c_str(), nullptr);
        if (key == "faction" && !sFactionTemplateStore.LookupEntry(uint32(v)))
            return Err(p, "Unknown faction template " + S(a, 4));
        if (U(a, 5) && !(c = MakeUnique(p, c)))
            return;
        CreatureTemplate* ct = MutableTemplate(c->GetEntry());
        it->set(*ct, v);
        WorldDatabase.DirectExecute("UPDATE creature_template SET `{}` = {} WHERE entry = {}", it->column, it->get(*ct), ct->Entry);
        if (it->query)
            ApplyTemplateChange(p, ct);
        RefreshFromTemplate(c);
        Ok(p, std::string(it->key) + " saved");
        SendInfo(p, c);
        SendAdvanced(p, c);
    }

    void OpRep(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        uint32 faction = U(a, 3);
        float value = F(a, 4);
        uint32 cap = std::min<uint32>(U(a, 5, 7), 7);
        if (faction && !sFactionStore.LookupEntry(faction))
            return Err(p, "Unknown faction (reputation) id " + std::to_string(faction));
        if (U(a, 6) && !(c = MakeUnique(p, c)))
            return;
        uint32 entry = c->GetEntry();
        if (!faction)
            WorldDatabase.DirectExecute("DELETE FROM creature_onkill_reputation WHERE creature_id = {}", entry);
        else
            WorldDatabase.DirectExecute("REPLACE INTO creature_onkill_reputation (creature_id, RewOnKillRepFaction1, RewOnKillRepFaction2, MaxStanding1, IsTeamAward1, RewOnKillRepValue1, MaxStanding2, IsTeamAward2, RewOnKillRepValue2, TeamDependent) "
                "VALUES ({}, {}, 0, {}, 0, {}, 0, 0, 0, 0)", entry, faction, cap, value);
        bool live = false;
        if (ReputationOnKillEntry const* r = sObjectMgr->GetReputationOnKilEntry(entry))
        {
            ReputationOnKillEntry* m = const_cast<ReputationOnKillEntry*>(r);
            m->RepFaction1 = faction; m->RepValue1 = value; m->ReputationMaxCap1 = cap;
            live = true;
        }
        Ok(p, faction ? (live ? "Kill reputation saved (live)" : "Kill reputation saved (works after the next server restart)") : "Kill reputation removed");
        SendAdvanced(p, c);
    }

    void OpNear(Player* p, std::vector<std::string> const& a)
    {
        float radius = std::clamp(F(a, 2, 30.f), 2.f, 200.f);
        std::list<Creature*> list;
        Acore::AllWorldObjectsInRange check(p, radius);
        Acore::CreatureListSearcher<Acore::AllWorldObjectsInRange> searcher(p, list, check);
        Cell::VisitObjects(p, searcher, radius);
        std::vector<Creature*> v;
        for (Creature* c : list)
            if (c->GetSpawnId() && !c->IsPet() && c->GetEntry() != VISUAL_WAYPOINT)
                v.push_back(c);
        std::sort(v.begin(), v.end(), [p](Creature* x, Creature* y) { return p->GetDistance(x) < p->GetDistance(y); });
        if (v.size() > 60)
            v.resize(60);
        Send(p, Join("NB", uint32(v.size())));
        for (Creature* c : v)
        {
            SendQuery(p, c->GetCreatureTemplate());
            Send(p, Join("NR", c->GetSpawnId(), c->GetEntry(), Clean(c->GetCreatureTemplate()->Name, 60), p->GetDistance(c), std::string(1, Reaction(c->GetCreatureTemplate()))));
        }
        Send(p, Join("NE", uint32(v.size())));
    }

    Creature* Target(Player* p, std::vector<std::string> const& a)
    {
        ObjectGuid::LowType guid = U(a, 2);
        Creature* c = nullptr;
        if (guid)
            c = FindSpawn(p, guid);
        else if (Unit* u = p->GetSelectedUnit())
            c = u->ToCreature();
        if (!c || !c->GetSpawnId())
        {
            Err(p, guid ? "Spawn not found on your map (move closer?)" : "Target a saved NPC first");
            return nullptr;
        }
        return c;
    }

    void SetPos(Creature* c, float x, float y, float z, float o)
    {
        CreatureData const* d = sObjectMgr->GetCreatureData(c->GetSpawnId());
        if (d)
        {
            sObjectMgr->RemoveCreatureFromGrid(c->GetSpawnId(), d);
            CreatureData* md = const_cast<CreatureData*>(d);
            md->posX = x; md->posY = y; md->posZ = z; md->orientation = o;
            sObjectMgr->AddCreatureToGrid(c->GetSpawnId(), d);
        }
        WorldDatabase.DirectExecute("UPDATE creature SET position_x = {}, position_y = {}, position_z = {}, orientation = {} WHERE guid = {}", x, y, z, o, c->GetSpawnId());
        c->SetHomePosition(x, y, z, o);
        c->NearTeleportTo(x, y, z, o);
        c->GetMotionMaster()->Initialize();
    }

    void OpMoveHere(Player* p, Creature* c)
    {
        if (p->GetMapId() != c->GetMapId())
            return Err(p, "Different map");
        SetPos(c, p->GetPositionX(), p->GetPositionY(), p->GetPositionZ(), p->GetOrientation());
        Ok(p, "Moved to you and saved");
        SendInfo(p, c);
    }

    void OpNudge(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        float fwd = F(a, 3), right = F(a, 4), up = F(a, 5), turnDeg = F(a, 6);
        float po = p->GetOrientation();
        float x = c->GetHomePosition().GetPositionX() + std::cos(po) * fwd + std::cos(po - float(M_PI) / 2) * right;
        float y = c->GetHomePosition().GetPositionY() + std::sin(po) * fwd + std::sin(po - float(M_PI) / 2) * right;
        float z = c->GetHomePosition().GetPositionZ() + up;
        float o = Position::NormalizeOrientation(c->GetHomePosition().GetOrientation() + turnDeg * float(M_PI) / 180.f);
        SetPos(c, x, y, z, o);
        SendInfo(p, c);
    }

    // world-axis nudge (dx dy dz, yards) and absolute facing (degrees)
    void OpNudgeW(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        Position const& h = c->GetHomePosition();
        SetPos(c, h.GetPositionX() + F(a, 3), h.GetPositionY() + F(a, 4), h.GetPositionZ() + F(a, 5), h.GetOrientation());
        SendInfo(p, c);
    }

    void OpSetO(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        Position const& h = c->GetHomePosition();
        SetPos(c, h.GetPositionX(), h.GetPositionY(), h.GetPositionZ(), Position::NormalizeOrientation(F(a, 3) * float(M_PI) / 180.f));
        SendInfo(p, c);
    }

    void OpFace(Player* p, Creature* c)
    {
        Position const& h = c->GetHomePosition();
        SetPos(c, h.GetPositionX(), h.GetPositionY(), h.GetPositionZ(), c->GetAngle(p));
        Ok(p, "Now faces you (saved)");
        SendInfo(p, c);
    }

    void OpDelete(Player* p, Creature* c)
    {
        ObjectGuid::LowType guid = c->GetSpawnId();
        uint32 path = c->GetWaypointPath();
        c->CombatStop();
        c->DeleteFromDB();
        c->AddObjectToRemoveList();
        WorldDatabase.DirectExecute("DELETE FROM creature_addon WHERE guid = {}", guid);
        if (path == guid * 10)
            WorldDatabase.DirectExecute("DELETE FROM waypoint_data WHERE id = {}", path);
        Ok(p, "Deleted spawn " + std::to_string(guid));
        Send(p, "DL~" + std::to_string(guid));
    }

    void OpMoveType(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        uint32 type = U(a, 3);
        float wander = F(a, 4, 5.f);
        if (type == 2 && !c->GetWaypointPath())
            return Err(p, "Record a path first (Path tab)");
        if (type == 1 && wander < 0.5f)
            wander = 5.f;
        c->SetWanderDistance(type == 1 ? wander : 0.f);
        c->SetDefaultMovementType(MovementGeneratorType(type == 2 ? WAYPOINT_MOTION_TYPE : (type == 1 ? RANDOM_MOTION_TYPE : IDLE_MOTION_TYPE)));
        RestartMovement(c);
        c->SaveToDB();
        Ok(p, type == 0 ? "Stands still" : (type == 1 ? "Wanders around its spot" : "Walks its path"));
        SendInfo(p, c);
    }

    void OpEmote(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        uint32 emote = U(a, 3);
        if (emote && !sEmotesStore.LookupEntry(emote))
            return Err(p, "Unknown emote id " + std::to_string(emote));
        // sit / sleep / kneel / dead are stand states for NPCs: the emote state alone does nothing on most models
        uint8 stand = emote == EMOTE_STATE_SIT ? UNIT_STAND_STATE_SIT : emote == EMOTE_STATE_SLEEP ? UNIT_STAND_STATE_SLEEP
            : emote == EMOTE_STATE_KNEEL ? UNIT_STAND_STATE_KNEEL : emote == EMOTE_STATE_DEAD ? UNIT_STAND_STATE_DEAD : UNIT_STAND_STATE_STAND;
        uint32 loop = stand == UNIT_STAND_STATE_STAND ? emote : 0;
        c->SetUInt32Value(UNIT_NPC_EMOTESTATE, loop);
        c->SetStandState(stand);
        SaveAddon(c->GetSpawnId(), 0, loop, false, true);
        WorldDatabase.DirectExecute("UPDATE creature_addon SET bytes1 = (bytes1 & 0xFFFFFF00) | {} WHERE guid = {}", uint32(stand), c->GetSpawnId());
        if (CreatureAddon const* ad = sObjectMgr->GetCreatureAddon(c->GetSpawnId()))
            const_cast<CreatureAddon*>(ad)->bytes1 = (ad->bytes1 & 0xFFFFFF00) | stand;
        Ok(p, stand != UNIT_STAND_STATE_STAND ? "Pose saved" : (emote ? "Looping emote saved" : "Emote cleared"));
        SendInfo(p, c);
    }

    void OpPlay(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        c->HandleEmoteCommand(U(a, 3));
        (void)p;
    }

    void OpRole(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        uint32 flags = U(a, 3);
        c->ReplaceAllNpcFlags(NPCFlags(flags));
        c->SaveToDB();
        Ok(p, "Role saved for this spawn");
        SendInfo(p, c);
    }

    void OpGuard(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        bool on = U(a, 3) != 0;
        if (U(a, 4) && !(c = MakeUnique(p, c)))
            return;
        CreatureTemplate* ct = MutableTemplate(c->GetEntry());
        if (on) ct->flags_extra |= CREATURE_FLAG_EXTRA_GUARD;
        else ct->flags_extra &= ~uint32(CREATURE_FLAG_EXTRA_GUARD);
        WorldDatabase.DirectExecute("UPDATE creature_template SET flags_extra = {} WHERE entry = {}", ct->flags_extra, ct->Entry);
        c->AIM_Initialize();
        Ok(p, on ? "Guard behaviour on (attacks hostiles near it)" : "Guard behaviour off");
        SendInfo(p, c);
    }

    void OpFaction(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        uint32 faction = U(a, 3);
        if (!sFactionTemplateStore.LookupEntry(faction))
            return Err(p, "Unknown faction template " + std::to_string(faction));
        if (U(a, 4) && !(c = MakeUnique(p, c)))
            return;
        CreatureTemplate* ct = MutableTemplate(c->GetEntry());
        ct->faction = faction;
        WorldDatabase.DirectExecute("UPDATE creature_template SET faction = {} WHERE entry = {}", faction, ct->Entry);
        c->SetFaction(faction);
        Ok(p, "Faction saved");
        SendInfo(p, c);
    }

    void OpRename(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        std::string name = Clean(S(a, 3), 90), sub = Clean(S(a, 4), 90);
        if (name.empty())
            return Err(p, "Name can't be empty");
        if (U(a, 5) && !(c = MakeUnique(p, c)))
            return;
        CreatureTemplate* ct = MutableTemplate(c->GetEntry());
        ct->Name = name;
        ct->SubName = sub;
        std::string en = name, es = sub;
        WorldDatabase.EscapeString(en);
        WorldDatabase.EscapeString(es);
        WorldDatabase.DirectExecute("UPDATE creature_template SET name = '{}', subname = '{}' WHERE entry = {}", en, es, ct->Entry);
        ApplyTemplateChange(p, ct);
        RestartMovement(c);
        Ok(p, "Renamed (other players see it after their cache refreshes)");
        SendInfo(p, c);
    }

    void OpLevel(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        uint32 lo = std::clamp<uint32>(U(a, 3, 1), 1, 83), hi = std::clamp<uint32>(U(a, 4, lo), lo, 83);
        if (U(a, 5) && !(c = MakeUnique(p, c)))
            return;
        CreatureTemplate* ct = MutableTemplate(c->GetEntry());
        ct->minlevel = uint8(lo);
        ct->maxlevel = uint8(hi);
        WorldDatabase.DirectExecute("UPDATE creature_template SET minlevel = {}, maxlevel = {} WHERE entry = {}", lo, hi, ct->Entry);
        RestartMovement(c);
        Ok(p, "Level range saved");
        SendInfo(p, c);
    }

    void OpModel(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        uint32 display = U(a, 3);
        if (!sCreatureDisplayInfoStore.LookupEntry(display))
            return Err(p, "Unknown display id " + std::to_string(display));
        if (U(a, 4) && !(c = MakeUnique(p, c)))
            return;
        CreatureTemplate* ct = MutableTemplate(c->GetEntry());
        ct->Models.clear();
        ct->Models.emplace_back(display, 1.f, 1.f);
        WorldDatabase.DirectExecute("DELETE FROM creature_template_model WHERE CreatureID = {}", ct->Entry);
        WorldDatabase.DirectExecute("INSERT INTO creature_template_model (CreatureID, Idx, CreatureDisplayID, DisplayScale, Probability, VerifiedBuild) VALUES ({}, 0, {}, 1, 1, 12340)", ct->Entry, display);
        c->SetDisplayId(display);
        c->SetNativeDisplayId(display);
        ApplyTemplateChange(p, ct);
        Ok(p, "Model saved");
        SendInfo(p, c);
    }

    void OpEntry(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        uint32 entry = U(a, 3);
        if (!sObjectMgr->GetCreatureTemplate(entry))
            return Err(p, "Unknown creature entry " + std::to_string(entry));
        c->UpdateEntry(entry, nullptr, true, true);
        c->SaveToDB();
        RestartMovement(c);
        RefreshLook(c);   // dressed (mirror image) NPCs: clients ask for the new look
        Ok(p, "Spawn now uses NPC " + std::to_string(entry));
        SendInfo(p, c);
    }

    void OpUnique(Player* p, Creature* c)
    {
        if (MakeUnique(p, c))
        {
            Ok(p, "This spawn now has its own copy (entry " + std::to_string(c->GetEntry()) + ")");
            SendInfo(p, c);
        }
    }

    void OpVendorAdd(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        uint32 item = U(a, 3);
        if (!sObjectMgr->GetItemTemplate(item))
            return Err(p, "Unknown item " + std::to_string(item));
        sObjectMgr->AddVendorItem(c->GetEntry(), item, 0, 0, 0, true);
        if (!(c->GetNpcFlags() & UNIT_NPC_FLAG_VENDOR))
        {
            c->ReplaceAllNpcFlags(NPCFlags(c->GetNpcFlags() | UNIT_NPC_FLAG_VENDOR | UNIT_NPC_FLAG_GOSSIP));
            c->SaveToDB();
        }
        Ok(p, "Item added to this NPC's shop (shared by every spawn of the entry)");
    }

    void OpRespawn(Player* p, Creature* c)
    {
        RestartMovement(c);
        if (!c->IsAlive())
            c->Respawn(true);
        Ok(p, "Respawned");
    }

    void OpGoto(Player* p, Creature* c)
    {
        p->TeleportTo(c->GetMapId(), c->GetPositionX(), c->GetPositionY(), c->GetPositionZ() + 0.5f, p->GetOrientation());
    }

    // ------------------------------------------------------------- paths
    // the points the client draws in the path preview (plus where the selected NPC stands)
    void SendPathList(Player* p, std::vector<Position> const& pts)
    {
        Send(p, Join("PLB", uint32(pts.size())));
        for (size_t i = 0; i < pts.size(); ++i)
            Send(p, Join("PL", uint32(i + 1), pts[i].GetPositionX(), pts[i].GetPositionY(), pts[i].GetPositionZ()));
        Send(p, Join("PLE", p->GetPositionX(), p->GetPositionY()));
    }

    constexpr uint32 CLICK_SPELL = 1543;   // Flare: a ground-targeting spell; the cast is swallowed, only the spot is used
    std::set<ObjectGuid::LowType> g_clickMode;
    std::mutex g_clickLock;

    void OpPathClickMode(Player* p, std::vector<std::string> const& a)
    {
        bool on = U(a, 2) != 0;
        {
            std::lock_guard<std::mutex> lock(g_clickLock);
            if (on) g_clickMode.insert(p->GetGUID().GetCounter()); else g_clickMode.erase(p->GetGUID().GetCounter());
        }
        if (on && !p->HasSpell(CLICK_SPELL))
            p->learnSpell(CLICK_SPELL, true);
        else if (!on && p->HasSpell(CLICK_SPELL))
            p->removeSpell(CLICK_SPELL, SPEC_MASK_ALL, true);
        Send(p, Join("PM", on ? 1 : 0, CLICK_SPELL));
    }

    // a ground click from the click spell: becomes a path point (runs in the network/map thread -> queue it)
    bool AnswerPathClick(WorldSession* session, WorldPacket const& packet)
    {
        if (packet.GetOpcode() != CMSG_CAST_SPELL || packet.size() < 6 || !session->GetPlayer())
            return true;
        Player* p = session->GetPlayer();
        uint8 castCount = packet.read<uint8>(0);
        uint32 spellId = packet.read<uint32>(1);
        if (spellId != CLICK_SPELL)
            return true;
        {
            std::lock_guard<std::mutex> lock(g_clickLock);
            if (!g_clickMode.count(p->GetGUID().GetCounter()))
                return true;
        }
        WorldPacket copy(packet);
        copy.rpos(6);
        SpellCastTargets targets;
        targets.Read(copy, p);
        if (SpellInfo const* si = sSpellMgr->GetSpellInfo(CLICK_SPELL))
            Spell::SendCastResult(p, si, castCount, SPELL_FAILED_DONT_REPORT);
        if (targets.HasDst())
        {
            WorldLocation const* d = targets.GetDstPos();
            std::ostringstream ss;
            ss.setf(std::ios::fixed); ss.precision(3);
            ss << "Q~PADDAT~" << d->GetPositionX() << "~" << d->GetPositionY() << "~" << d->GetPositionZ();
            std::lock_guard<std::mutex> lock(g_queueLock);
            g_queue.emplace_back(p->GetGUID(), ss.str());
        }
        return false;   // never really cast it
    }

    void OpPathAddAt(Player* p, std::vector<std::string> const& a)
    {
        EditState& st = g_state[p->GetGUID().GetCounter()];
        Position pos(F(a, 2), F(a, 3), F(a, 4) + 0.1f, 0.f);
        st.path.push_back(pos);
        AddMarker(p, st, pos);
        Send(p, Join("PP", uint32(st.path.size()), pos.GetPositionX(), pos.GetPositionY(), pos.GetPositionZ()));
        SendPathList(p, st.path);
    }

    void OpPathAdd(Player* p)
    {
        EditState& st = g_state[p->GetGUID().GetCounter()];
        Position pos = p->GetPosition();
        st.path.push_back(pos);
        AddMarker(p, st, pos);
        Send(p, Join("PP", uint32(st.path.size()), pos.GetPositionX(), pos.GetPositionY(), pos.GetPositionZ()));
        SendPathList(p, st.path);
    }

    // PPT~op~n : work on point n (1-based) of the recording. op: go / set (move it to me) / ins (insert my spot after it) / del
    void OpPathPoint(Player* p, std::vector<std::string> const& a)
    {
        EditState& st = g_state[p->GetGUID().GetCounter()];
        std::string what = S(a, 2);
        uint32 n = U(a, 3);
        if (what == "go" && a.size() > 6)   // a shown (not loaded) path: the client sends the spot
        {
            p->NearTeleportTo(F(a, 4), F(a, 5), F(a, 6) + 0.5f, p->GetOrientation());
            return Ok(p, "At point " + std::to_string(n));
        }
        if (n < 1 || n > st.path.size())
            return Err(p, "No point " + std::to_string(n) + " in the recording (Edit path loads a saved one)");
        Position& pt = st.path[n - 1];
        if (what == "go")
        {
            p->NearTeleportTo(pt.GetPositionX(), pt.GetPositionY(), pt.GetPositionZ() + 0.5f, p->GetOrientation());
            return Ok(p, "At point " + std::to_string(n));
        }
        if (what == "set")
            pt = p->GetPosition();
        else if (what == "ins")
            st.path.insert(st.path.begin() + n, p->GetPosition());
        else if (what == "del")
            st.path.erase(st.path.begin() + (n - 1));
        else
            return;
        ClearMarkers(p, st);
        for (Position const& q : st.path)
            AddMarker(p, st, q);
        Ok(p, what == "set" ? "Point " + std::to_string(n) + " moved here" : what == "ins" ? "Point added after " + std::to_string(n)
            : "Point " + std::to_string(n) + " removed");
        Send(p, Join("PC", uint32(st.path.size())));
        SendPathList(p, st.path);
    }

    void OpPathUndo(Player* p)
    {
        EditState& st = g_state[p->GetGUID().GetCounter()];
        if (!st.path.empty())
            st.path.pop_back();
        if (!st.markers.empty())
        {
            if (Creature* m = ObjectAccessor::GetCreature(*p, st.markers.back()))
                m->DespawnOrUnsummon();
            st.markers.pop_back();
        }
        Send(p, Join("PC", uint32(st.path.size())));
        SendPathList(p, st.path);
    }

    void OpPathClear(Player* p)
    {
        EditState& st = g_state[p->GetGUID().GetCounter()];
        st.path.clear();
        ClearMarkers(p, st);
        Send(p, Join("PC", 0));
        SendPathList(p, st.path);
    }

    void OpPathLoad(Player* p, Creature* c, bool editable)
    {
        EditState& st = g_state[p->GetGUID().GetCounter()];
        ClearMarkers(p, st);
        if (editable)
            st.path.clear();
        // the live path id can be 0 (template addon, spawned copy...): try the spawn addon, the template addon, then our own id
        std::vector<uint32> ids = { c->GetWaypointPath() };
        if (CreatureAddon const* ad = sObjectMgr->GetCreatureAddon(c->GetSpawnId())) ids.push_back(ad->path_id);
        if (CreatureAddon const* ad = sObjectMgr->GetCreatureTemplateAddon(c->GetEntry())) ids.push_back(ad->path_id);
        ids.push_back(c->GetSpawnId() * 10);
        std::vector<Position> shown;
        for (uint32 id : ids)
        {
            if (!id || !shown.empty())
                continue;
            if (WaypointPath const* wp = sWaypointMgr->GetPath(id))
                for (WaypointNode const& n : wp->Nodes)
                    shown.emplace_back(n.X, n.Y, n.Z, 0.f);
            if (shown.empty())   // written to the DB but not in memory yet
                if (QueryResult r = WorldDatabase.Query("SELECT position_x, position_y, position_z FROM waypoint_data WHERE id = {} ORDER BY point", id))
                    do { Field* f = r->Fetch(); shown.emplace_back(f[0].Get<float>(), f[1].Get<float>(), f[2].Get<float>(), 0.f); } while (r->NextRow());
        }
        if (shown.empty())
        {
            Send(p, Join("PC", uint32(st.path.size())));
            return Err(p, "This NPC has no path");
        }
        for (Position const& pos : shown)
        {
            AddMarker(p, st, pos);
            if (editable)
                st.path.push_back(pos);
        }
        Send(p, Join("PC", uint32(st.path.size())));
        SendPathList(p, shown);
        Ok(p, std::to_string(shown.size()) + (editable ? " points loaded for editing (markers shown)" : " path points shown"));
    }

    void OpPathSave(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        EditState& st = g_state[p->GetGUID().GetCounter()];
        if (st.path.size() < 2)
            return Err(p, "Add at least 2 points (stand somewhere, press Add point)");
        bool backAndForth = U(a, 3) != 0;
        uint32 delay = std::min<uint32>(U(a, 4), 600) * 1000;
        bool run = U(a, 5) != 0;

        std::vector<Position> pts = st.path;
        if (backAndForth)
            for (size_t i = st.path.size() - 1; i-- > 1;)
                pts.push_back(st.path[i]);

        uint32 pathId = c->GetSpawnId() * 10;
        WorldDatabase.DirectExecute("DELETE FROM waypoint_data WHERE id = {}", pathId);
        for (size_t i = 0; i < pts.size(); ++i)
        {
            bool endStop = (i == 0) || (!backAndForth && i == pts.size() - 1) || (backAndForth && i == st.path.size() - 1);
            WorldDatabase.DirectExecute("INSERT INTO waypoint_data (id, point, position_x, position_y, position_z, orientation, velocity, delay, smoothTransition, move_type, action, action_chance, wpguid) "
                "VALUES ({}, {}, {}, {}, {}, NULL, 0, {}, 0, {}, 0, 100, 0)", pathId, i + 1, pts[i].GetPositionX(), pts[i].GetPositionY(), pts[i].GetPositionZ(),
                endStop ? delay : 0, run ? 1 : 0);
        }
        sWaypointMgr->ReloadPath(pathId);
        SaveAddon(c->GetSpawnId(), pathId, 0, true, false);
        c->LoadPath(pathId);
        c->SetWanderDistance(0.f);
        c->SetDefaultMovementType(WAYPOINT_MOTION_TYPE);
        Position const& first = st.path.front();
        SetPos(c, first.GetPositionX(), first.GetPositionY(), first.GetPositionZ(), first.GetOrientation());
        RestartMovement(c);
        c->SaveToDB();
        st.path.clear();
        ClearMarkers(p, st);
        Ok(p, "Path saved (" + std::to_string(pts.size()) + " points)");
        Send(p, Join("PC", 0));
        SendInfo(p, c);
    }

    void OpPathDelete(Player* p, Creature* c)
    {
        uint32 path = c->GetWaypointPath();
        SaveAddon(c->GetSpawnId(), 0, 0, true, false);
        if (path == c->GetSpawnId() * 10)
            WorldDatabase.DirectExecute("DELETE FROM waypoint_data WHERE id = {}", path);
        c->LoadPath(0);
        c->SetDefaultMovementType(IDLE_MOTION_TYPE);
        RestartMovement(c);
        c->SaveToDB();
        Ok(p, "Path removed, NPC stands still");
        SendInfo(p, c);
    }

    // ================================================================ v2: generic table editor, quests, objects
    constexpr uint32 QUEST_FIRST = 9990001, QUEST_LAST = 9999999;
    constexpr uint32 GOTPL_FIRST = 9980001, GOTPL_LAST = 9989999;
    constexpr uint32 ESCORT_WP_BASE = 99800000;

    std::unordered_map<ObjectGuid::LowType, std::string> g_buf;   // long text arrives in chunks
    std::set<std::string> g_dirty;                                 // tables written since the last RLOAD

    // tables the editor may touch, with the column that identifies a record / a list
    std::unordered_map<std::string, std::string> const& RowTables()
    {
        static std::unordered_map<std::string, std::string> const t = {
            { "quest_template", "ID" }, { "quest_template_addon", "ID" }, { "quest_offer_reward", "ID" },
            { "quest_request_items", "ID" }, { "npc_text", "ID" }, { "trainer", "Id" }, { "gameobject_template", "entry" },
            { "npc_vendor", "entry" }, { "trainer_spell", "TrainerId" }, { "creature_default_trainer", "CreatureId" },
            { "gossip_menu", "MenuID" }, { "gossip_menu_option", "MenuID" }, { "creature_queststarter", "id" },
            { "creature_questender", "id" },
        };
        return t;
    }

    std::set<std::string> const& Columns(std::string const& table)
    {
        static std::unordered_map<std::string, std::set<std::string>> cache;
        auto itr = cache.find(table);
        if (itr != cache.end())
            return itr->second;
        std::set<std::string>& cols = cache[table];
        if (QueryResult r = WorldDatabase.Query("SHOW COLUMNS FROM `{}`", table))
            do { cols.insert(r->Fetch()[0].Get<std::string>()); } while (r->NextRow());
        return cols;
    }

    bool ValidTable(Player* p, std::string const& t)
    {
        if (RowTables().count(t))
            return true;
        Err(p, "Table not editable: " + Clean(t, 40));
        return false;
    }

    bool ValidColumn(Player* p, std::string const& t, std::string const& c)
    {
        if (Columns(t).count(c))
            return true;
        Err(p, "Unknown column " + Clean(c, 40) + " in " + t);
        return false;
    }

    std::string Esc(std::string s)
    {
        WorldDatabase.EscapeString(s);
        return s;
    }

    void ReloadTables(Player* p)
    {
        auto has = [](std::initializer_list<char const*> l) { for (char const* t : l) if (g_dirty.count(t)) return true; return false; };
        if (has({ "quest_template", "quest_template_addon", "quest_offer_reward", "quest_request_items" }))
        {
            sObjectMgr->LoadQuests();
            sObjectMgr->LoadGameObjectForQuests();
            sObjectMgr->LoadQuestStartersAndEnders();
        }
        else if (has({ "creature_queststarter", "creature_questender" }))
            sObjectMgr->LoadQuestStartersAndEnders();
        if (has({ "npc_text" })) sObjectMgr->LoadGossipText();
        if (has({ "gossip_menu" })) sObjectMgr->LoadGossipMenu();
        if (has({ "gossip_menu_option" })) sObjectMgr->LoadGossipMenuItems();
        if (has({ "npc_vendor" })) sObjectMgr->LoadVendors();
        if (has({ "trainer", "trainer_spell", "creature_default_trainer" }))
        {
            sObjectMgr->LoadTrainers();
            sObjectMgr->LoadCreatureDefaultTrainers();
        }
        bool goTpl = g_dirty.count("gameobject_template") != 0;
        g_dirty.clear();
        Ok(p, goTpl ? "Saved. Object type changes show after a restart" : "Saved and applied live");
    }

    // RGET~table~key : every column of one record, long values split in chunks
    void OpRGet(Player* p, std::vector<std::string> const& a)
    {
        std::string t = S(a, 2);
        if (!ValidTable(p, t))
            return;
        uint32 key = U(a, 3);
        std::string const& kc = RowTables().at(t);
        Send(p, Join("RH", t, key));
        if (QueryResult r = WorldDatabase.Query("SELECT * FROM `{}` WHERE `{}` = {} LIMIT 1", t, kc, key))
        {
            Field* f = r->Fetch();
            for (uint32 i = 0; i < r->GetFieldCount(); ++i)
            {
                std::string col = r->GetFieldName(i);
                std::string v = f[i].IsNull() ? std::string() : f[i].Get<std::string>();
                for (char& c : v)
                    if (c == '~' || c == '\t' || c == '|' || c == '\r') c = ' ';
                    else if (c == '\n') c = '\x01';
                std::string out;
                for (char c : v) { if (c == '\x01') out += "$B"; else out += c; }
                if (out.empty())
                    Send(p, Join("RR", col, 0, ""));
                for (size_t o = 0, n = 0; o < out.size(); o += 180, ++n)
                    Send(p, Join("RR", col, n, out.substr(o, 180)));
            }
        }
        Send(p, Join("RX", t, key));
    }

    // RSET~table~key~column : value = text buffer (BUF chunks). Creates the record when missing.
    void OpRSet(Player* p, std::vector<std::string> const& a)
    {
        std::string t = S(a, 2), col = S(a, 4);
        uint32 key = U(a, 3);
        if (!ValidTable(p, t) || !ValidColumn(p, t, col))
            return;
        std::string const& kc = RowTables().at(t);
        if (col == kc)
            return Err(p, "The id column can't be changed");
        std::string& v = g_buf[p->GetGUID().GetCounter()];
        WorldDatabase.DirectExecute("INSERT IGNORE INTO `{}` (`{}`) VALUES ({})", t, kc, key);
        WorldDatabase.DirectExecute("UPDATE `{}` SET `{}` = '{}' WHERE `{}` = {}", t, col, Esc(v), kc, key);
        v.clear();
        g_dirty.insert(t);
    }

    std::string RowName(std::string const& col, uint32 id)
    {
        if (col == "item")
            if (ItemTemplate const* it = sObjectMgr->GetItemTemplate(id)) return it->Name1;
        if (col == "SpellId")
            if (SpellEntry const* s = sSpellStore.LookupEntry(id)) return s->SpellName[0];
        if (col == "quest")
            if (Quest const* q = sObjectMgr->GetQuestTemplate(id)) return q->GetTitle();
        return "";
    }

    // LGET~table~listKey : all rows of a list table (vendor items, trainer spells, gossip options, quest givers)
    void OpLGet(Player* p, std::vector<std::string> const& a)
    {
        std::string t = S(a, 2);
        if (!ValidTable(p, t))
            return;
        uint32 key = U(a, 3);
        Send(p, Join("LH", t, key));
        if (QueryResult r = WorldDatabase.Query("SELECT * FROM `{}` WHERE `{}` = {} LIMIT 200", t, RowTables().at(t), key))
        {
            do
            {
                Field* f = r->Fetch();
                std::string line = "LR~" + t;
                std::string name;
                for (uint32 i = 0; i < r->GetFieldCount(); ++i)
                {
                    std::string col = r->GetFieldName(i);
                    if (col == "VerifiedBuild")
                        continue;
                    std::string v = f[i].IsNull() ? std::string() : Clean(f[i].Get<std::string>(), 60);
                    line += "~" + col + "=" + v;
                    if (name.empty() && !v.empty())
                        name = RowName(col, uint32(std::strtoul(v.c_str(), nullptr, 10)));
                }
                Send(p, line + "~_name=" + Clean(name, 50));
            } while (r->NextRow());
        }
        Send(p, Join("LE", t, key));
    }

    // LADD / LDEL ~table~col=val~col=val... : insert a row / delete matching rows
    void OpLRow(Player* p, std::vector<std::string> const& a, bool add)
    {
        std::string t = S(a, 2);
        if (!ValidTable(p, t))
            return;
        std::string cols, vals, where;
        bool hasKey = false;
        for (size_t i = 3; i < a.size(); ++i)
        {
            size_t eq = a[i].find('=');
            if (eq == std::string::npos)
                continue;
            std::string c = a[i].substr(0, eq), v = a[i].substr(eq + 1);
            if (!ValidColumn(p, t, c))
                return;
            hasKey |= c == RowTables().at(t);
            cols += (cols.empty() ? "`" : ",`") + c + "`";
            vals += (vals.empty() ? "'" : ",'") + Esc(v) + "'";
            where += (where.empty() ? "`" : " AND `") + c + "` = '" + Esc(v) + "'";
        }
        if (!hasKey)
            return Err(p, "Missing " + RowTables().at(t));
        if (add)
            WorldDatabase.DirectExecute("REPLACE INTO `{}` ({}) VALUES ({})", t, cols, vals);
        else
            WorldDatabase.DirectExecute("DELETE FROM `{}` WHERE {}", t, where);
        g_dirty.insert(t);
    }

    uint32 NextFree(char const* table, char const* col, uint32 first, uint32 last)
    {
        uint32 id = first;
        if (QueryResult r = WorldDatabase.Query("SELECT MAX(`{}`) FROM `{}` WHERE `{}` BETWEEN {} AND {}", col, table, col, first, last))
            if (!r->Fetch()[0].IsNull())
                id = r->Fetch()[0].Get<uint32>() + 1;
        return id <= last ? id : 0;
    }

    // NEWID~kind : a free id in the dev range (npc_text, gossip menu, trainer)
    void OpNewId(Player* p, std::vector<std::string> const& a)
    {
        std::string k = S(a, 2);
        uint32 id = 0;
        if (k == "npc_text") id = NextFree("npc_text", "ID", 16000001, 16099999);
        else if (k == "gossip") id = std::max(NextFree("gossip_menu", "MenuID", 9998001, 9998999), NextFree("gossip_menu_option", "MenuID", 9998001, 9998999));
        else if (k == "trainer") id = NextFree("trainer", "Id", 9980001, 9989999);
        if (!id)
            return Err(p, "No free id left");
        Send(p, Join("NI", k, id));
    }

    // ---------------------------------------------------------------- quests
    void OpQSearch(Player* p, std::vector<std::string> const& a)
    {
        std::string q = Lower(S(a, 2));
        uint32 qid = U(a, 2);
        std::vector<Quest const*> hits;
        for (auto const& [id, quest] : sObjectMgr->GetQuestTemplates())
        {
            bool dev = id >= QUEST_FIRST && id <= QUEST_LAST;
            if (q.empty() ? !dev : (id != qid && Lower(quest->GetTitle()).find(q) == std::string::npos))
                continue;
            hits.push_back(quest);
            if (hits.size() >= 300)
                break;
        }
        std::sort(hits.begin(), hits.end(), [](Quest const* x, Quest const* y) { return x->GetQuestId() > y->GetQuestId(); });
        Send(p, Join("QB", uint32(hits.size())));
        for (Quest const* quest : hits)
            Send(p, Join("QR", quest->GetQuestId(), quest->GetQuestLevel(), Clean(quest->GetTitle(), 70)));
        Send(p, Join("QE", uint32(hits.size())));
    }

    // QNEW~title~guid(optional): new quest, given and finished by that NPC
    void OpQNew(Player* p, std::vector<std::string> const& a)
    {
        uint32 id = NextFree("quest_template", "ID", QUEST_FIRST, QUEST_LAST);
        if (!id)
            return Err(p, "No free quest id left");
        std::string title = S(a, 2).empty() ? "New quest" : S(a, 2);
        uint32 level = p->GetLevel();
        if (Creature* c = U(a, 3) ? FindSpawn(p, U(a, 3)) : nullptr)
        {
            level = c->GetLevel();
            WorldDatabase.DirectExecute("REPLACE INTO creature_queststarter (id, quest) VALUES ({}, {})", c->GetEntry(), id);
            WorldDatabase.DirectExecute("REPLACE INTO creature_questender (id, quest) VALUES ({}, {})", c->GetEntry(), id);
            if (!c->HasNpcFlag(UNIT_NPC_FLAG_QUESTGIVER))
            {
                c->SetNpcFlag(UNIT_NPC_FLAG_QUESTGIVER);
                c->SaveToDB();
            }
        }
        WorldDatabase.DirectExecute("INSERT INTO quest_template (ID, QuestType, QuestLevel, MinLevel, LogTitle, LogDescription, QuestDescription, RewardXPDifficulty) "
            "VALUES ({}, 2, {}, {}, '{}', 'Objectives go here.', 'Quest text goes here.', 5)", id, level, std::max<uint32>(1, level > 3 ? level - 3 : 1), Esc(title));
        WorldDatabase.DirectExecute("INSERT IGNORE INTO quest_offer_reward (ID, RewardText) VALUES ({}, 'Well done.')", id);
        WorldDatabase.DirectExecute("INSERT IGNORE INTO quest_request_items (ID, CompletionText) VALUES ({}, 'Is it done?')", id);
        WorldDatabase.DirectExecute("INSERT IGNORE INTO quest_template_addon (ID) VALUES ({})", id);
        g_dirty.insert("quest_template");
        ReloadTables(p);
        Send(p, Join("QN", id));
    }

    void OpQDel(Player* p, std::vector<std::string> const& a)
    {
        uint32 id = U(a, 2);
        if (id < QUEST_FIRST || id > QUEST_LAST)
            return Err(p, "Only quests made with the dev menu can be deleted");
        for (char const* t : { "quest_template", "quest_template_addon", "quest_offer_reward", "quest_request_items" })
            WorldDatabase.DirectExecute("DELETE FROM `{}` WHERE ID = {}", t, id);
        WorldDatabase.DirectExecute("DELETE FROM creature_queststarter WHERE quest = {}", id);
        WorldDatabase.DirectExecute("DELETE FROM creature_questender WHERE quest = {}", id);
        g_dirty.insert("quest_template");
        ReloadTables(p);
    }

    // QESCORT~quest~guid~run : the NPC walks the path you recorded in the path editor when the quest is accepted;
    // the quest completes for the escorting players when it reaches the end.
    void OpQEscort(Player* p, std::vector<std::string> const& a)
    {
        uint32 quest = U(a, 2);
        Creature* c = FindSpawn(p, U(a, 3));
        if (!c || !sObjectMgr->GetQuestTemplate(quest))
            return Err(p, "Select the NPC and save the quest first");
        EditState& st = g_state[p->GetGUID().GetCounter()];
        if (st.path.size() < 2)
            return Err(p, "Record at least 2 points in the Path editor first (Add point here)");
        uint32 wp = ESCORT_WP_BASE + quest % 100000;
        WorldDatabase.DirectExecute("DELETE FROM waypoints WHERE entry = {}", wp);
        for (size_t i = 0; i < st.path.size(); ++i)
            WorldDatabase.DirectExecute("INSERT INTO waypoints (entry, pointid, position_x, position_y, position_z, point_comment) VALUES ({}, {}, {}, {}, {}, 'dev menu escort')",
                wp, uint32(i + 1), st.path[i].GetPositionX(), st.path[i].GetPositionY(), st.path[i].GetPositionZ());
        int64 eog = -int64(c->GetSpawnId());
        WorldDatabase.DirectExecute("DELETE FROM smart_scripts WHERE entryorguid = {} AND source_type = 0 AND event_type = 19 AND event_param1 = {}", eog, quest);
        uint32 sid = 0;
        if (QueryResult r = WorldDatabase.Query("SELECT MAX(id) FROM smart_scripts WHERE entryorguid = {} AND source_type = 0", eog))
            if (!r->Fetch()[0].IsNull())
                sid = r->Fetch()[0].Get<uint32>() + 1;
        WorldDatabase.DirectExecute("INSERT INTO smart_scripts (entryorguid, source_type, id, link, event_type, event_param1, action_type, action_param1, action_param2, action_param3, action_param4, action_param5, action_param6, target_type, comment) "
            "VALUES ({}, 0, {}, 0, 19, {}, 53, {}, {}, 0, {}, 15000, 1, 7, 'dev menu: escort on quest accept')", eog, sid, quest, U(a, 4) ? 2 : 1, wp, quest);
        WorldDatabase.DirectExecute("INSERT IGNORE INTO quest_template_addon (ID) VALUES ({})", quest);
        WorldDatabase.DirectExecute("UPDATE quest_template_addon SET SpecialFlags = SpecialFlags | 2 WHERE ID = {}", quest);
        CreatureTemplate* ct = MutableTemplate(c->GetEntry());
        if (ct->AIName != "SmartAI")
        {
            if (ct->ScriptID)
                Ok(p, "Note: this NPC type had a C++ script, it now uses SmartAI");
            ct->AIName = "SmartAI";
            WorldDatabase.DirectExecute("UPDATE creature_template SET AIName = 'SmartAI' WHERE entry = {}", ct->Entry);
        }
        sSmartWaypointMgr->LoadFromDB();
        sSmartScriptMgr->LoadSmartAIFromDB();
        g_dirty.insert("quest_template");
        ReloadTables(p);
        c->AIM_Initialize();
        st.path.clear();
        ClearMarkers(p, st);
        Send(p, Join("PC", 0));
        Ok(p, "Escort saved: the NPC walks the path when the quest is accepted");
    }

    // ---------------------------------------------------------------- vendor price & currency
    // Gold price is the item's own BuyPrice (the 3.3.5 client shows that for every vendor, no per-vendor price exists).
    // Currencies are the server's ItemExtendedCost entries (badges, emblems, honor, arena points...).
    std::string ExtCostText(ItemExtendedCostEntry const* e)
    {
        std::string t;
        for (uint8 i = 0; i < MAX_ITEM_EXTENDED_COST_REQUIREMENTS; ++i)
            if (e->reqitem[i] && e->reqitemcount[i])
            {
                ItemTemplate const* it = sObjectMgr->GetItemTemplate(e->reqitem[i]);
                t += (t.empty() ? "" : " + ") + std::to_string(e->reqitemcount[i]) + "x " + (it ? it->Name1 : "item " + std::to_string(e->reqitem[i]));
            }
        if (e->reqhonorpoints)
            t += (t.empty() ? "" : " + ") + std::to_string(e->reqhonorpoints) + " honor";
        if (e->reqarenapoints)
            t += (t.empty() ? "" : " + ") + std::to_string(e->reqarenapoints) + " arena points";
        if (e->reqpersonalarenarating)
            t += " (rating " + std::to_string(e->reqpersonalarenarating) + ")";
        return Clean(t.empty() ? "nothing" : t, 120);
    }

    // a[2] text: currency name ("emblem", "honor") or an extended cost id
    void OpExtCostSearch(Player* p, std::vector<std::string> const& a)
    {
        std::string q = Lower(S(a, 2));
        uint32 asId = uint32(std::strtoul(q.c_str(), nullptr, 10));
        uint32 shown = 0;
        Send(p, Join("XCB", 0));
        for (uint32 i = 1; i < sItemExtendedCostStore.GetNumRows() && shown < 60; ++i)
        {
            ItemExtendedCostEntry const* e = sItemExtendedCostStore.LookupEntry(i);
            if (!e)
                continue;
            std::string t = ExtCostText(e);
            if (asId ? i != asId : (q.empty() || Lower(t).find(q) == std::string::npos))
                continue;
            Send(p, Join("XC", i, t));
            ++shown;
        }
        Send(p, Join("XCE", shown));
    }

    // a[2] item, a[3] price in copper (optional: only reports when missing)
    void OpItemPrice(Player* p, std::vector<std::string> const& a)
    {
        uint32 item = U(a, 2);
        ItemTemplate* it = const_cast<ItemTemplate*>(sObjectMgr->GetItemTemplate(item));
        if (!it)
            return Err(p, "No item with that id");
        if (a.size() > 3 && !a[3].empty())
        {
            it->BuyPrice = U(a, 3);
            WorldDatabase.DirectExecute("UPDATE item_template SET BuyPrice = {} WHERE entry = {}", it->BuyPrice, item);
            Ok(p, "Price saved for " + Clean(it->Name1, 40) + " (every vendor that sells it)");
        }
        Send(p, Join("IP", item, it->BuyPrice));
    }

    // a[2] vendor entry, a[3] item, a[4] old extended cost, a[5] new extended cost (0 = gold only)
    void OpVendorCurrency(Player* p, std::vector<std::string> const& a)
    {
        uint32 entry = U(a, 2), item = U(a, 3), oldCost = U(a, 4), cost = U(a, 5);
        if (cost && !sItemExtendedCostStore.LookupEntry(cost))
            return Err(p, "No currency entry with that id");
        WorldDatabase.DirectExecute("UPDATE npc_vendor SET ExtendedCost = {} WHERE entry = {} AND item = {} AND ExtendedCost = {}", cost, entry, item, oldCost);
        g_dirty.insert("npc_vendor");
        ReloadTables(p);
        if (cost)
            Ok(p, "Now costs " + ExtCostText(sItemExtendedCostStore.LookupEntry(cost)) + " (no gold)");
        else
            Ok(p, "Now costs gold only");
    }

    // ---------------------------------------------------------------- combat (SmartAI rows on the NPC type)
    std::string SpellLabel(uint32 id)
    {
        SpellInfo const* si = sSpellMgr->GetSpellInfo(id);
        if (!si || !si->SpellName[0])
            return "?";
        std::string n = si->SpellName[0];
        if (si->Rank[0] && *si->Rank[0])
            n += std::string(" (") + si->Rank[0] + ")";
        return Clean(n, 60);
    }

    void SendSpellRow(Player* p, uint32 id)
    {
        SpellInfo const* si = sSpellMgr->GetSpellInfo(id);
        if (!si)
            return;
        Send(p, Join("SP", id, SpellLabel(id), si->CalcCastTime(), uint32(si->GetMaxRange(false)), si->SpellIconID));
    }

    // text search over every spell the server knows, "npc:<entry>" lists what another mob casts
    void OpSpellSearch(Player* p, std::vector<std::string> const& a)
    {
        std::string q = Lower(S(a, 2));
        uint32 page = U(a, 3), shown = 0, total = 0;
        Send(p, Join("SPB", page));
        if (q.rfind("npc:", 0) == 0)
        {
            uint32 entry = uint32(std::strtoul(q.c_str() + 4, nullptr, 10));
            std::set<uint32> ids;
            if (CreatureTemplate const* ct = sObjectMgr->GetCreatureTemplate(entry))
                for (uint32 s : ct->spells)
                    if (s) ids.insert(s);
            if (QueryResult r = WorldDatabase.Query("SELECT DISTINCT action_param1 FROM smart_scripts WHERE entryorguid = {} AND source_type = 0 AND action_type = 11", entry))
                do ids.insert(r->Fetch()[0].Get<uint32>()); while (r->NextRow());
            for (uint32 s : ids)
                if (sSpellMgr->GetSpellInfo(s) && total++ >= page * 30 && shown < 30) { SendSpellRow(p, s); ++shown; }
            return Send(p, Join("SPE", total));
        }
        uint32 asId = uint32(std::strtoul(q.c_str(), nullptr, 10));
        for (uint32 i = 1; i < sSpellMgr->GetSpellInfoStoreSize(); ++i)
        {
            SpellInfo const* si = sSpellMgr->GetSpellInfo(i);
            if (!si || !si->SpellName[0] || !*si->SpellName[0])
                continue;
            if (asId ? i != asId : Lower(si->SpellName[0]).find(q) == std::string::npos)
                continue;
            if (total++ >= page * 30 && shown < 30) { SendSpellRow(p, i); ++shown; }
        }
        Send(p, Join("SPE", total));
    }

    void SendCombat(Player* p, Creature* c)
    {
        CreatureTemplate const* ct = c->GetCreatureTemplate();
        Send(p, Join("CB", c->GetSpawnId(), uint32(c->GetWeaponDamageRange(BASE_ATTACK, MINDAMAGE)), uint32(c->GetWeaponDamageRange(BASE_ATTACK, MAXDAMAGE)),
            ct->BaseAttackTime, ct->DamageModifier, ct->AIName == "SmartAI" ? 1 : (ct->ScriptID ? 2 : 0)));
        if (QueryResult r = WorldDatabase.Query("SELECT id, action_param1, event_param3, event_param4, event_param1, target_type, event_chance FROM smart_scripts "
            "WHERE entryorguid = {} AND source_type = 0 AND event_type = 0 AND action_type = 11 ORDER BY id", c->GetEntry()))
            do
            {
                Field* f = r->Fetch();
                Send(p, Join("CS", f[0].Get<uint32>(), f[1].Get<uint32>(), SpellLabel(f[1].Get<uint32>()), f[2].Get<uint32>(), f[3].Get<uint32>(), f[4].Get<uint32>(), uint32(f[5].Get<uint8>()), uint32(f[6].Get<uint8>())));
            } while (r->NextRow());
        Send(p, Join("CE", c->GetSpawnId()));
    }

    void ReloadSmart(Player* p, Creature* c)
    {
        CreatureTemplate* ct = MutableTemplate(c->GetEntry());
        if (ct->AIName != "SmartAI")
        {
            if (ct->ScriptID)
                Ok(p, "Note: this NPC type had a C++ script, it now uses SmartAI");
            ct->AIName = "SmartAI";
            WorldDatabase.DirectExecute("UPDATE creature_template SET AIName = 'SmartAI' WHERE entry = {}", ct->Entry);
        }
        sSmartScriptMgr->LoadSmartAIFromDB();
        // every loaded copy of this type on the map switches now; fighting ones after their fight (they respawn with it too)
        uint32 const entry = c->GetEntry();
        for (auto const& [spawnId, other] : c->GetMap()->GetCreatureBySpawnIdStore())
            if (other && other->GetEntry() == entry && other->IsAlive() && !other->IsInCombat())
                other->AIM_Initialize();
    }

    // a[3] spell, a[4] first cast after (ms), a[5] repeat min, a[6] repeat max, a[7] target (2 victim, 1 self, 5 random enemy), a[8] chance
    void OpCombatAdd(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        uint32 spell = U(a, 3);
        if (!sSpellMgr->GetSpellInfo(spell))
            return Err(p, "No spell with that id on this server");
        uint32 first = U(a, 4, 2000), rmin = std::max<uint32>(U(a, 5, 8000), 500), rmax = std::max(U(a, 6, rmin), rmin);
        uint32 tgt = U(a, 7, 2);
        if (tgt != 1 && tgt != 2 && tgt != 5)
            tgt = 2;
        uint32 chance = std::clamp<uint32>(U(a, 8, 100), 1, 100);
        uint32 sid = 0;
        if (QueryResult r = WorldDatabase.Query("SELECT MAX(id) FROM smart_scripts WHERE entryorguid = {} AND source_type = 0", c->GetEntry()))
            if (!r->Fetch()[0].IsNull())
                sid = r->Fetch()[0].Get<uint32>() + 1;
        WorldDatabase.DirectExecute("INSERT INTO smart_scripts (entryorguid, source_type, id, link, event_type, event_chance, event_param1, event_param2, event_param3, event_param4, action_type, action_param1, target_type, comment) "
            "VALUES ({}, 0, {}, 0, 0, {}, {}, {}, {}, {}, 11, {}, {}, 'dev menu: combat spell')", c->GetEntry(), sid, chance, first, first, rmin, rmax, spell, tgt);
        ReloadSmart(p, c);
        SendCombat(p, c);
        Ok(p, "Added " + SpellLabel(spell) + " (every NPC of this type)");
    }

    void OpCombatDel(Player* p, Creature* c, std::vector<std::string> const& a)
    {
        WorldDatabase.DirectExecute("DELETE FROM smart_scripts WHERE entryorguid = {} AND source_type = 0 AND id = {} AND event_type = 0 AND action_type = 11", c->GetEntry(), U(a, 3));
        ReloadSmart(p, c);
        SendCombat(p, c);
    }

    // ---------------------------------------------------------------- objects
    std::string ModelPath(uint32 display)
    {
        if (GameObjectDisplayInfoEntry const* d = sGameObjectDisplayInfoStore.LookupEntry(display))
            if (d->filename)
                return Clean(d->filename, 150);
        return "";
    }

    void OpGSearch(Player* p, std::vector<std::string> const& a)
    {
        std::string q = Lower(S(a, 2));
        uint32 page = U(a, 3), mode = U(a, 4);   // mode 0 object types, 1 raw models (every asset)
        uint32 qid = uint32(std::strtoul(q.c_str(), nullptr, 10));
        struct Hit { uint32 entry, type, display; std::string name; };
        std::vector<Hit> hits;
        if (mode == 0)
        {
            for (auto const& [entry, gt] : *sObjectMgr->GetGameObjectTemplates())
                if (q.empty() || entry == qid || Lower(gt.name).find(q) != std::string::npos)
                    hits.push_back({ entry, gt.type, gt.displayId, gt.name });
        }
        else
        {
            for (uint32 i = 0; i < sGameObjectDisplayInfoStore.GetNumRows(); ++i)
                if (GameObjectDisplayInfoEntry const* d = sGameObjectDisplayInfoStore.LookupEntry(i))
                    if (d->filename && (q.empty() || i == qid || Lower(d->filename).find(q) != std::string::npos))
                    {
                        std::string f = d->filename;
                        size_t s = f.find_last_of("\\/");
                        hits.push_back({ 0, 0, i, s == std::string::npos ? f : f.substr(s + 1) });
                    }
        }
        std::sort(hits.begin(), hits.end(), [&](Hit const& x, Hit const& y)
        {
            bool xe = (x.entry ? x.entry : x.display) == qid, ye = (y.entry ? y.entry : y.display) == qid;
            if (xe != ye) return xe;
            return x.name != y.name ? x.name < y.name : x.display < y.display;
        });
        uint32 total = uint32(hits.size());
        uint32 pages = std::max<uint32>(1, (total + PAGE_SIZE - 1) / PAGE_SIZE);
        page = std::min(page, pages - 1);
        Send(p, Join("GB", total, page, pages));
        for (uint32 i = page * PAGE_SIZE; i < std::min(total, (page + 1) * PAGE_SIZE); ++i)
            Send(p, Join("GR", hits[i].entry, Clean(hits[i].name, 60), hits[i].type, hits[i].display, ModelPath(hits[i].display)));
        Send(p, Join("GE", total, page, pages));
    }

    // a generic (decoration) object type for a raw model, made once per model
    uint32 TemplateForDisplay(Player* p, uint32 display)
    {
        for (auto const& [entry, gt] : *sObjectMgr->GetGameObjectTemplates())
            if (entry >= GOTPL_FIRST && entry <= GOTPL_LAST && gt.displayId == display)
                return entry;
        uint32 id = NextFree("gameobject_template", "entry", GOTPL_FIRST, GOTPL_LAST);
        if (!id)
        {
            Err(p, "No free object id left");
            return 0;
        }
        std::string f = ModelPath(display);
        size_t s = f.find_last_of("\\/");
        std::string name = s == std::string::npos ? f : f.substr(s + 1);
        if (name.size() > 4) name.resize(name.size() - 4);
        WorldDatabase.DirectExecute("INSERT INTO gameobject_template (entry, type, displayId, name, size) VALUES ({}, 5, {}, '{}', 1)", id, display, Esc(name));
        GameObjectTemplate& gt = (*const_cast<GameObjectTemplateContainer*>(sObjectMgr->GetGameObjectTemplates()))[id];
        gt = GameObjectTemplate();
        gt.entry = id;
        gt.type = GAMEOBJECT_TYPE_GENERIC;
        gt.displayId = display;
        gt.name = name;
        gt.size = 1.f;
        return id;
    }

    GameObject* FindGo(Player* p, ObjectGuid::LowType guid)
    {
        auto bounds = p->GetMap()->GetGameObjectBySpawnIdStore().equal_range(guid);
        return bounds.first != bounds.second ? bounds.first->second : nullptr;
    }

    void SendGoInfo(Player* p, GameObject* go)
    {
        float yaw = 0, pitch = 0, roll = 0;
        if (GameObjectData const* d = go->GetGameObjectData())
            G3D::Matrix3(d->rotation).toEulerAnglesZYX(yaw, pitch, roll);
        GameObjectTemplate const* gt = go->GetGOInfo();
        Send(p, Join("GI", go->GetSpawnId(), go->GetEntry(), Clean(gt->name, 60), go->GetPositionX(), go->GetPositionY(), go->GetPositionZ(),
            go->GetOrientation(), yaw * 180.f / float(M_PI), pitch * 180.f / float(M_PI), roll * 180.f / float(M_PI), gt->displayId, gt->type, ModelPath(gt->displayId)));
    }

    // rewrite position/rotation and respawn the object fresh (the 3.3.5 client ignores updates of a known guid)
    GameObject* GoPlace(Player* p, GameObject* go, float x, float y, float z, float yaw, float pitch, float roll)
    {
        ObjectGuid::LowType guid = go->GetSpawnId();
        Map* map = go->GetMap();
        sObjectMgr->RemoveGameobjectFromGrid(guid, go->GetGameObjectData());
        go->Relocate(x, y, z, yaw);
        go->SetWorldRotationAngles(yaw, pitch, roll);
        go->SaveToDB();
        sObjectMgr->AddGameobjectToGrid(guid, go->GetGameObjectData());
        go->Delete();
        GameObject* ngo = new GameObject();
        if (!ngo->LoadGameObjectFromDB(guid, map, true))
        {
            delete ngo;
            Err(p, "Object saved but could not respawn");
            return nullptr;
        }
        SendGoInfo(p, ngo);
        return ngo;
    }

    void OpGSpawn(Player* p, std::vector<std::string> const& a)
    {
        uint32 entry = U(a, 2);
        if (U(a, 3))   // spawn by raw model id
            entry = TemplateForDisplay(p, U(a, 3));
        GameObjectTemplate const* gt = entry ? sObjectMgr->GetGameObjectTemplate(entry) : nullptr;
        if (!gt)
            return Err(p, "Unknown object");
        if (gt->displayId && !sGameObjectDisplayInfoStore.LookupEntry(gt->displayId))
            return Err(p, "That object has a missing model");
        Map* map = p->GetMap();
        GameObject* go = sObjectMgr->IsGameObjectStaticTransport(entry) ? new StaticTransport() : new GameObject();
        float o = p->GetOrientation();
        G3D::Quat rot = G3D::Quat::fromAxisAngleRotation(G3D::Vector3::unitZ(), o);
        if (!go->Create(map->GenerateLowGuid<HighGuid::GameObject>(), entry, map, p->GetPhaseMaskForSpawn(), p->GetPositionX(), p->GetPositionY(), p->GetPositionZ(), o, rot, 0, GO_STATE_READY))
        {
            delete go;
            return Err(p, "Could not create the object here");
        }
        go->SaveToDB(map->GetId(), (1 << map->GetSpawnMode()), p->GetPhaseMaskForSpawn());
        ObjectGuid::LowType guid = go->GetSpawnId();
        delete go;
        go = sObjectMgr->IsGameObjectStaticTransport(entry) ? new StaticTransport() : new GameObject();
        if (!go->LoadGameObjectFromDB(guid, map, true))
        {
            delete go;
            return Err(p, "Saved but could not load");
        }
        sObjectMgr->AddGameobjectToGrid(guid, sObjectMgr->GetGameObjectData(guid));
        Ok(p, "Object placed and saved");
        SendGoInfo(p, go);
    }

    void OpGNear(Player* p, std::vector<std::string> const& a)
    {
        float r = std::min(200.f, std::max(5.f, F(a, 2, 40.f)));
        Send(p, Join("GNB", 0));
        if (QueryResult q = WorldDatabase.Query("SELECT guid, id, SQRT(POW(position_x - {0}, 2) + POW(position_y - {1}, 2) + POW(position_z - {2}, 2)) AS d FROM gameobject "
            "WHERE map = {3} AND position_x BETWEEN {0} - {4} AND {0} + {4} AND position_y BETWEEN {1} - {4} AND {1} + {4} ORDER BY d LIMIT 60",
            p->GetPositionX(), p->GetPositionY(), p->GetPositionZ(), p->GetMapId(), r))
        {
            do
            {
                Field* f = q->Fetch();
                GameObjectTemplate const* gt = sObjectMgr->GetGameObjectTemplate(f[1].Get<uint32>());
                Send(p, Join("GN", f[0].Get<uint32>(), f[1].Get<uint32>(), Clean(gt ? gt->name : "?", 60), f[2].Get<float>()));
            } while (q->NextRow());
        }
        Send(p, Join("GNE", 0));
    }

    void GoOps(Player* p, std::string const& op, std::vector<std::string> const& a)
    {
        GameObject* go = nullptr;
        if (op == "GPICK" && !S(a, 2).empty())
        {
            // the object the player clicked: nearest saved object with the tooltip's name
            std::string want = Lower(S(a, 2));
            float best = 60.f;
            if (QueryResult q = WorldDatabase.Query("SELECT guid FROM gameobject WHERE map = {} AND position_x BETWEEN {} AND {} AND position_y BETWEEN {} AND {}",
                p->GetMapId(), p->GetPositionX() - 60, p->GetPositionX() + 60, p->GetPositionY() - 60, p->GetPositionY() + 60))
                do
                {
                    if (GameObject* g = FindGo(p, q->Fetch()[0].Get<uint32>()))
                        if (Lower(g->GetGOInfo()->name) == want && p->GetDistance(g) < best) { best = p->GetDistance(g); go = g; }
                } while (q->NextRow());
            if (go)
                return SendGoInfo(p, go);
        }
        if (op == "GTGT" || op == "GPICK")
        {
            // nearest saved object in front of you
            float best = 15.f;
            if (QueryResult q = WorldDatabase.Query("SELECT guid FROM gameobject WHERE map = {} AND position_x BETWEEN {} AND {} AND position_y BETWEEN {} AND {}",
                p->GetMapId(), p->GetPositionX() - 15, p->GetPositionX() + 15, p->GetPositionY() - 15, p->GetPositionY() + 15))
                do
                {
                    if (GameObject* g = FindGo(p, q->Fetch()[0].Get<uint32>()))
                    {
                        float d = p->GetDistance(g) + (p->HasInArc(float(M_PI) / 2, g) ? 0.f : 6.f);
                        if (d < best) { best = d; go = g; }
                    }
                } while (q->NextRow());
            if (!go)
                return Err(p, "No saved object within 15 yards");
            return SendGoInfo(p, go);
        }
        go = FindGo(p, U(a, 2));
        if (!go)
            return Err(p, "Object not found on your map (move closer?)");
        float yaw = go->GetOrientation(), pitch = 0, roll = 0;
        if (GameObjectData const* d = go->GetGameObjectData())
            G3D::Matrix3(d->rotation).toEulerAnglesZYX(yaw, pitch, roll);
        float x = go->GetPositionX(), y = go->GetPositionY(), z = go->GetPositionZ();
        float po = p->GetOrientation();
        float const R = float(M_PI) / 180.f;
        if (op == "GSEL") return SendGoInfo(p, go);
        if (op == "GMOVE") { GoPlace(p, go, p->GetPositionX(), p->GetPositionY(), p->GetPositionZ(), yaw, pitch, roll); return Ok(p, "Moved to you"); }
        if (op == "GNUDGE")
        {
            float fwd = F(a, 3), right = F(a, 4);
            x += std::cos(po) * fwd + std::cos(po - float(M_PI) / 2) * right;
            y += std::sin(po) * fwd + std::sin(po - float(M_PI) / 2) * right;
            GoPlace(p, go, x, y, z + F(a, 5), Position::NormalizeOrientation(yaw + F(a, 6) * R), pitch, roll);
            return;
        }
        if (op == "GNUDGEW") { GoPlace(p, go, x + F(a, 3), y + F(a, 4), z + F(a, 5), yaw, pitch, roll); return; }
        if (op == "GROT") { GoPlace(p, go, x, y, z, Position::NormalizeOrientation(F(a, 3) * R), F(a, 4) * R, F(a, 5) * R); return; }
        if (op == "GFACE") { GoPlace(p, go, x, y, z, go->GetAngle(p), pitch, roll); return; }
        if (op == "GGOTO") { p->NearTeleportTo(x, y, z + 1.f, p->GetOrientation()); return; }
        if (op == "GDEL")
        {
            ObjectGuid::LowType guid = go->GetSpawnId();
            go->SetRespawnTime(0);
            go->Delete();
            go->DeleteFromDB();
            Ok(p, "Object deleted");
            return Send(p, Join("GD", guid));
        }
        if (op == "GDUP")
        {
            std::vector<std::string> b = { "Q", "GSPAWN", std::to_string(go->GetEntry()) };
            return OpGSpawn(p, b);
        }
        Err(p, "Unknown op " + Clean(op, 20));
    }

    // ================================================================ v3: NPC outfits (player-race NPCs dressed in any armor)
    // Works on every 3.3.5 client: the NPC uses its race's character model with UNIT_FLAG2_MIRROR_IMAGE,
    // and the client asks the server for skin/face/hair + armor (SMSG_MIRRORIMAGE_DATA), like Mirror Image.
    constexpr uint32 OUTFIT_BASE_ENTRY = 68;     // humanoid template copied for brand new NPCs
    constexpr size_t OUTFIT_ARMOR = 11, OUTFIT_WEAPONS = 3;

    struct Outfit
    {
        uint8 race = 1, gender = 0, skin = 0, face = 0, hair = 0, hairColor = 0, facial = 0;
        int32 armor[OUTFIT_ARMOR] = {};   // item entry (>0) or -display id (<0), 0 = nothing
        uint32 weapons[OUTFIT_WEAPONS] = {};
        std::string ext;   // extra looks for custom clients ("key=value,key=value"); stock clients ignore them
    };
    std::unordered_map<uint32, Outfit> g_outfits;            // by creature entry
    std::unordered_map<ObjectGuid, Outfit> g_previews;       // temporary preview NPCs
    std::unordered_map<ObjectGuid::LowType, ObjectGuid> g_previewOf;   // player -> his preview NPC
    std::mutex g_outfitLock;

    char const* const ARMOR_COLS[OUTFIT_ARMOR] = { "head", "shoulders", "body", "chest", "waist", "legs", "feet", "wrists", "hands", "back", "tabard" };
    uint8 const ARMOR_SLOTS[OUTFIT_ARMOR] = { EQUIPMENT_SLOT_HEAD, EQUIPMENT_SLOT_SHOULDERS, EQUIPMENT_SLOT_BODY, EQUIPMENT_SLOT_CHEST, EQUIPMENT_SLOT_WAIST,
        EQUIPMENT_SLOT_LEGS, EQUIPMENT_SLOT_FEET, EQUIPMENT_SLOT_WRISTS, EQUIPMENT_SLOT_HANDS, EQUIPMENT_SLOT_BACK, EQUIPMENT_SLOT_TABARD };
    uint8 const WEAPON_SLOTS[OUTFIT_WEAPONS] = { EQUIPMENT_SLOT_MAINHAND, EQUIPMENT_SLOT_OFFHAND, EQUIPMENT_SLOT_RANGED };

    uint32 RaceModel(Outfit const& o)
    {
        if (ChrRacesEntry const* r = sChrRacesStore.LookupEntry(o.race))
            return o.gender ? r->model_f : r->model_m;
        return 0;
    }

    std::string PackOutfit(Outfit const& o)
    {
        std::ostringstream ss;
        ss << uint32(o.race) << ',' << uint32(o.gender) << ',' << uint32(o.skin) << ',' << uint32(o.face) << ',' << uint32(o.hair) << ','
           << uint32(o.hairColor) << ',' << uint32(o.facial);
        for (int32 a : o.armor) ss << ',' << a;
        for (uint32 w : o.weapons) ss << ',' << w;
        if (!o.ext.empty())
            ss << ';' << o.ext;
        return ss.str();
    }

    bool UnpackOutfit(std::string const& all, Outfit& o)
    {
        size_t semi = all.find(';');
        std::string s = all.substr(0, semi);
        o.ext.clear();
        if (semi != std::string::npos)
            for (char ch : all.substr(semi + 1, 200))   // only safe characters: letters, digits, _ = , - .
                if (std::isalnum(uint8(ch)) || ch == '_' || ch == '=' || ch == ',' || ch == '-' || ch == '.')
                    o.ext += ch;
        std::vector<std::string> v = Split(s, ',');
        if (v.size() < 7 + OUTFIT_ARMOR + OUTFIT_WEAPONS)
            return false;
        auto n = [&](size_t i) { return std::strtol(v[i].c_str(), nullptr, 10); };
        o.race = uint8(n(0)); o.gender = uint8(n(1) ? 1 : 0); o.skin = uint8(n(2)); o.face = uint8(n(3)); o.hair = uint8(n(4));
        o.hairColor = uint8(n(5)); o.facial = uint8(n(6));
        for (size_t i = 0; i < OUTFIT_ARMOR; ++i) o.armor[i] = int32(n(7 + i));
        for (size_t i = 0; i < OUTFIT_WEAPONS; ++i) o.weapons[i] = uint32(std::max<long>(0, n(7 + OUTFIT_ARMOR + i)));
        return RaceModel(o) != 0;
    }

    void LoadOutfits()
    {
        WorldDatabase.DirectExecute("CREATE TABLE IF NOT EXISTS coa_npc_outfit (entry INT UNSIGNED NOT NULL PRIMARY KEY, outfit VARCHAR(255) NOT NULL, "
            "comment VARCHAR(100) NOT NULL DEFAULT '') ENGINE=InnoDB COMMENT='Dev Menu: player-race NPC looks'");
        WorldDatabase.DirectExecute("CREATE TABLE IF NOT EXISTS coa_devmenu_changes (tbl VARCHAR(64) NOT NULL, cond VARCHAR(255) NOT NULL, "
            "PRIMARY KEY (tbl, cond)) ENGINE=InnoDB COMMENT='Dev Menu: rows changed since the last clear (for SQL export)'");
        WorldDatabase.DirectExecute("ALTER TABLE coa_npc_outfit MODIFY outfit VARCHAR(600) NOT NULL");
        std::lock_guard<std::mutex> lock(g_outfitLock);
        g_outfits.clear();
        if (QueryResult r = WorldDatabase.Query("SELECT entry, outfit FROM coa_npc_outfit"))
            do
            {
                Outfit o;
                if (UnpackOutfit(r->Fetch()[1].Get<std::string>(), o))
                    g_outfits[r->Fetch()[0].Get<uint32>()] = o;
            } while (r->NextRow());
        LOG_INFO("module", ">> Dev Menu: {} NPC outfits loaded", g_outfits.size());
    }

    bool FindOutfit(Creature const* c, Outfit& out)
    {
        std::lock_guard<std::mutex> lock(g_outfitLock);
        auto p = g_previews.find(c->GetGUID());
        if (p != g_previews.end()) { out = p->second; return true; }
        auto e = g_outfits.find(c->GetEntry());
        if (e != g_outfits.end()) { out = e->second; return true; }
        return false;
    }

    uint32 ArmorDisplay(int32 v)
    {
        if (v < 0)
            return uint32(-v);
        if (ItemTemplate const* it = v ? sObjectMgr->GetItemTemplate(uint32(v)) : nullptr)
            return it->DisplayInfoID;
        return 0;
    }

    // answer the client's mirror image request for our NPCs (return false = handled)
    bool AnswerOutfit(WorldSession* session, WorldPacket const& packet)
    {
        if (packet.GetOpcode() != CMSG_GET_MIRRORIMAGE_DATA || packet.size() < sizeof(uint64) || !session->GetPlayer())
            return true;
        ObjectGuid guid = packet.read<ObjectGuid>(0);
        if (!guid.IsCreatureOrVehicle())
            return true;
        Creature* c = ObjectAccessor::GetCreature(*session->GetPlayer(), guid);
        Outfit o;
        if (!c || !FindOutfit(c, o))
            return true;
        WorldPacket data(SMSG_MIRRORIMAGE_DATA, 68);
        data << guid << uint32(RaceModel(o)) << uint8(o.race) << uint8(o.gender) << uint8(1)
             << uint8(o.skin) << uint8(o.face) << uint8(o.hair) << uint8(o.hairColor) << uint8(o.facial) << uint32(0);
        for (int32 a : o.armor)
            data << uint32(ArmorDisplay(a));
        // extra look bits for custom-race clients ride after the stock fields: "extra" (uint64) + magic 'DMX1'.
        // Stock clients stop reading after the armor, so the tail is ignored there.
        if (std::string::size_type at = o.ext.find("extra="); at != std::string::npos)
            if (uint64 extra = std::strtoull(o.ext.c_str() + at + 6, nullptr, 10))
                data << extra << uint32(0x31584D44);
        session->SendPacket(&data);
        // custom clients: the addon hands these to the client's look adapter (see the Help page)
        if (!o.ext.empty())
        {
            char g[24];
            std::snprintf(g, sizeof(g), "0x%016llX", (unsigned long long)guid.GetRawValue());
            Send(session->GetPlayer(), Join("XL", std::string(g), o.ext));
        }
        return false;
    }

    void Dress(Creature* c, Outfit const& o)
    {
        c->SetUnitFlag2(UNIT_FLAG2_MIRROR_IMAGE);
        c->SetDisplayId(RaceModel(o));
        c->SetNativeDisplayId(RaceModel(o));
        for (size_t i = 0; i < OUTFIT_WEAPONS; ++i)
            c->SetVirtualItem(i, o.weapons[i]);
    }

    // send the look to the client after a change: the client only asks for it when the NPC appears, so re-create it
    void RefreshLook(Creature* c)
    {
        if (c->IsSummon())
            return;
        c->DespawnOrUnsummon(0ms, 1s);
    }

    // OUT~... : player's own look (visible items = transmog included), a spawn's look, the race list
    void OpOutfitRaces(Player* p)
    {
        Send(p, Join("ORB", 0));
        for (uint32 i = 0; i < sChrRacesStore.GetNumRows(); ++i)
        {
            ChrRacesEntry const* r = sChrRacesStore.LookupEntry(i);
            if (!r || (!r->model_m && !r->model_f))
                continue;
            // any locale's name (servers with non-English DBCs), else "Race <id>"
            std::string name;
            for (char const* n : r->name)
                if (n && *n) { name = n; break; }
            if (name.empty())
                name = "Race " + std::to_string(i);
            for (uint8 g = 0; g < 2; ++g)
            {
                if (!(g ? r->model_f : r->model_m))
                    continue;   // male-only / female-only races

                uint32 skins = 0, faces = 0, hairs = 0, colors = 0, facials = 0;
                for (uint32 k = 0; k < sCharSectionsStore.GetNumRows(); ++k)
                {
                    CharSectionsEntry const* s = sCharSectionsStore.LookupEntry(k);
                    if (!s || s->Race != i || s->Gender != g)
                        continue;
                    switch (s->GenType)
                    {
                        case 0: skins = std::max(skins, s->Color + 1); break;
                        case 1: faces = std::max(faces, s->Type + 1); break;
                        case 2: facials = std::max(facials, s->Type + 1); break;
                        case 3: hairs = std::max(hairs, s->Type + 1); colors = std::max(colors, s->Color + 1); break;
                        default: break;
                    }
                }
                Send(p, Join("OR", i, Clean(name, 40), uint32(g), g ? r->model_f : r->model_m, skins, faces, hairs, colors, facials));
            }
        }
        Send(p, Join("ORE", 0));
    }

    void OpOutfitMine(Player* p)
    {
        Outfit o;
        o.race = p->getRace(); o.gender = p->getGender();
        o.skin = p->GetByteValue(PLAYER_BYTES, 0); o.face = p->GetByteValue(PLAYER_BYTES, 1); o.hair = p->GetByteValue(PLAYER_BYTES, 2);
        o.hairColor = p->GetByteValue(PLAYER_BYTES, 3); o.facial = p->GetByteValue(PLAYER_BYTES_2, 0);
        for (size_t i = 0; i < OUTFIT_ARMOR; ++i)
            o.armor[i] = int32(p->GetUInt32Value(PLAYER_VISIBLE_ITEM_1_ENTRYID + ARMOR_SLOTS[i] * 2));
        for (size_t i = 0; i < OUTFIT_WEAPONS; ++i)
            o.weapons[i] = p->GetUInt32Value(PLAYER_VISIBLE_ITEM_1_ENTRYID + WEAPON_SLOTS[i] * 2);
        if (p->HasPlayerFlag(PLAYER_FLAGS_HIDE_HELM)) o.armor[0] = 0;
        if (p->HasPlayerFlag(PLAYER_FLAGS_HIDE_CLOAK)) o.armor[9] = 0;
        Send(p, Join("OL", PackOutfit(o), "Your look"));
    }

    void OpOutfitGet(Player* p, std::vector<std::string> const& a)
    {
        Creature* c = FindSpawn(p, U(a, 2));
        if (!c)
            return Err(p, "Select an NPC first");
        Outfit o;
        if (FindOutfit(c, o))
            return Send(p, Join("OL", PackOutfit(o), Clean(c->GetName(), 40)));
        Err(p, "This NPC has no outfit yet (it uses a normal creature model)");
    }

    // a template that already carries the mirror-image flag, so a fresh preview is created with it
    uint32 PreviewEntry()
    {
        static uint32 entry = 0;
        if (entry && sObjectMgr->GetCreatureTemplate(entry))
            return entry;
        if (QueryResult r = WorldDatabase.Query("SELECT entry FROM creature_template WHERE name = 'Dev outfit preview' AND entry BETWEEN {} AND {} LIMIT 1", CLONE_FIRST, CLONE_LAST))
            entry = r->Fetch()[0].Get<uint32>();
        if (!entry || !sObjectMgr->GetCreatureTemplate(entry))
        {
            entry = CloneTemplate(OUTFIT_BASE_ENTRY);
            if (!entry)
                return 0;
            WorldDatabase.DirectExecute("UPDATE creature_template SET name = 'Dev outfit preview', subname = '', npcflag = 0, faction = 35, ScriptName = '', AIName = '', unit_flags2 = unit_flags2 | {} WHERE entry = {}", uint32(UNIT_FLAG2_MIRROR_IMAGE), entry);
        }
        CreatureTemplate* ct = MutableTemplate(entry);
        ct->Name = "Preview"; ct->npcflag = 0; ct->faction = 35; ct->ScriptID = 0; ct->AIName = "";
        ct->unit_flags2 |= UNIT_FLAG2_MIRROR_IMAGE;
        ct->InitializeQueryData();
        return entry;
    }

    void OpPreviewRemove(Player* p)
    {
        std::lock_guard<std::mutex> lock(g_outfitLock);
        auto itr = g_previewOf.find(p->GetGUID().GetCounter());
        if (itr == g_previewOf.end())
            return Err(p, "No preview to remove");
        if (Creature* old = ObjectAccessor::GetCreature(*p, itr->second))
            old->DespawnOrUnsummon();
        g_previews.erase(itr->second);
        g_previewOf.erase(itr);
        Ok(p, "Preview removed");
    }

    // OPREV~packed : (re)spawn a preview copy 3 yards in front of you, kept 2 minutes
    void OpOutfitPreview(Player* p, std::vector<std::string> const& a)
    {
        Outfit o;
        if (!UnpackOutfit(S(a, 2), o))
            return Err(p, "Unknown race for this client/server");
        ObjectGuid::LowType me = p->GetGUID().GetCounter();
        {
            std::lock_guard<std::mutex> lock(g_outfitLock);
            auto itr = g_previewOf.find(me);
            if (itr != g_previewOf.end())
            {
                if (Creature* old = ObjectAccessor::GetCreature(*p, itr->second))
                    old->DespawnOrUnsummon();
                g_previews.erase(itr->second);
                g_previewOf.erase(itr);
            }
        }
        float o2 = p->GetOrientation();
        float x = p->GetPositionX() + std::cos(o2) * 3.f, y = p->GetPositionY() + std::sin(o2) * 3.f;
        uint32 pe = PreviewEntry();
        if (!pe)
            return Err(p, "Could not create the preview NPC type");
        TempSummon* c = p->SummonCreature(pe, x, y, p->GetPositionZ(), Position::NormalizeOrientation(o2 + float(M_PI)), TEMPSUMMON_TIMED_DESPAWN, 120000);
        if (!c)
            return Err(p, "Could not place the preview here");
        {
            std::lock_guard<std::mutex> lock(g_outfitLock);
            g_previews[c->GetGUID()] = o;
            g_previewOf[me] = c->GetGUID();
        }
        c->SetReactState(REACT_PASSIVE);
        c->SetFaction(35);
        c->SetUnitFlag(UNIT_FLAG_NON_ATTACKABLE);
        c->SetName("Preview");
        Dress(c, o);
    }

    // OSAVE~guid~packed~name : guid 0 = create a brand new NPC at your feet; otherwise dress that NPC's type
    void OpOutfitSave(Player* p, std::vector<std::string> const& a)
    {
        Outfit o;
        if (!UnpackOutfit(S(a, 3), o))
            return Err(p, "Unknown race for this client/server");
        Creature* c = U(a, 2) ? FindSpawn(p, U(a, 2)) : nullptr;
        uint32 entry;
        if (c)
        {
            if (CountSpawnsOfEntry(c->GetEntry()) > 1 || c->GetEntry() < CLONE_FIRST)
                if (!(c = MakeUnique(p, c)))
                    return;
            entry = c->GetEntry();
        }
        else
        {
            entry = CloneTemplate(OUTFIT_BASE_ENTRY);
            if (!entry)
                return Err(p, "Could not create a new NPC type (dev entry range full?)");
            std::string name = S(a, 4).empty() ? "New NPC" : S(a, 4);
            CreatureTemplate* ct = MutableTemplate(entry);
            ct->Name = name; ct->SubName = ""; ct->npcflag = 0; ct->faction = 35; ct->ScriptID = 0; ct->AIName = "";
            WorldDatabase.DirectExecute("UPDATE creature_template SET name = '{}', subname = '', npcflag = 0, faction = 35, ScriptName = '', AIName = '' WHERE entry = {}", Esc(name), entry);
        }
        uint32 model = RaceModel(o);
        CreatureTemplate* ct = MutableTemplate(entry);
        ct->unit_flags2 |= UNIT_FLAG2_MIRROR_IMAGE;
        ct->Models.clear();
        ct->Models.emplace_back(model, 1.f, 1.f);
        WorldDatabase.DirectExecute("UPDATE creature_template SET unit_flags2 = unit_flags2 | {} WHERE entry = {}", uint32(UNIT_FLAG2_MIRROR_IMAGE), entry);
        WorldDatabase.DirectExecute("DELETE FROM creature_template_model WHERE CreatureID = {}", entry);
        WorldDatabase.DirectExecute("INSERT INTO creature_template_model (CreatureID, Idx, CreatureDisplayID, DisplayScale, Probability) VALUES ({}, 0, {}, 1, 1)", entry, model);
        WorldDatabase.DirectExecute("REPLACE INTO creature_equip_template (CreatureID, ID, ItemID1, ItemID2, ItemID3) VALUES ({}, 1, {}, {}, {})", entry, o.weapons[0], o.weapons[1], o.weapons[2]);
        WorldDatabase.DirectExecute("REPLACE INTO coa_npc_outfit (entry, outfit, comment) VALUES ({}, '{}', '{}')", entry, PackOutfit(o), Esc(Clean(ct->Name, 90)));
        sObjectMgr->LoadEquipmentTemplates();
        ct->InitializeQueryData();
        SendQuery(p, ct);
        {
            std::lock_guard<std::mutex> lock(g_outfitLock);
            g_outfits[entry] = o;
        }
        if (!c)
        {
            std::vector<std::string> b = { "Q", "SPAWN", std::to_string(entry), "1" };
            OpSpawn(p, b);
            return Ok(p, "New NPC created and placed. Rename it in Identity");
        }
        c->SetCurrentEquipmentId(1);
        Dress(c, o);
        Ok(p, "Outfit saved");
        SendInfo(p, c);
        RefreshLook(c);
    }

    // ---- wardrobe "disguise": the client can only draw a textured, dressable model of the player in menus,
    // so while the wardrobe is open the GM is shown with the NPC's race and look (never saved: restored before any save)
    struct RealLook { uint8 race, gender, facial, gender3; uint32 bytes, display, native; };
    std::unordered_map<ObjectGuid::LowType, RealLook> g_disguised;
    std::mutex g_disguiseLock;   // autosave runs in map threads, the menu in the world thread

    bool Undisguise(Player* p)
    {
        std::lock_guard<std::mutex> lock(g_disguiseLock);
        auto itr = g_disguised.find(p->GetGUID().GetCounter());
        if (itr == g_disguised.end())
            return false;
        RealLook const& r = itr->second;
        p->SetByteValue(UNIT_FIELD_BYTES_0, 0, r.race);
        p->SetByteValue(UNIT_FIELD_BYTES_0, 2, r.gender);
        p->SetUInt32Value(PLAYER_BYTES, r.bytes);
        p->SetByteValue(PLAYER_BYTES_2, 0, r.facial);
        p->SetByteValue(PLAYER_BYTES_3, 0, r.gender3);
        p->SetNativeDisplayId(r.native);
        p->SetDisplayId(r.display);
        g_disguised.erase(itr);
        return true;
    }

    void OpDisguise(Player* p, std::vector<std::string> const& a)
    {
        Outfit o;
        if (!UnpackOutfit(S(a, 2), o))
            return Err(p, "Unknown race");
        std::lock_guard<std::mutex> lock(g_disguiseLock);
        if (p->GetDisplayId() != p->GetNativeDisplayId() && !g_disguised.count(p->GetGUID().GetCounter()))
            return Err(p, "Leave your shapeshift or morph first");
        if (!g_disguised.count(p->GetGUID().GetCounter()))
            g_disguised[p->GetGUID().GetCounter()] = { p->getRace(), p->getGender(), p->GetByteValue(PLAYER_BYTES_2, 0), p->GetByteValue(PLAYER_BYTES_3, 0),
                p->GetUInt32Value(PLAYER_BYTES), p->GetDisplayId(), p->GetNativeDisplayId() };
        p->SetByteValue(UNIT_FIELD_BYTES_0, 0, o.race);
        p->SetByteValue(UNIT_FIELD_BYTES_0, 2, o.gender);
        p->SetUInt32Value(PLAYER_BYTES, uint32(o.skin) | (uint32(o.face) << 8) | (uint32(o.hair) << 16) | (uint32(o.hairColor) << 24));
        p->SetByteValue(PLAYER_BYTES_2, 0, o.facial);
        p->SetByteValue(PLAYER_BYTES_3, 0, o.gender);
        p->SetNativeDisplayId(RaceModel(o));
        p->SetDisplayId(RaceModel(o));
        Send(p, Join("DG", 1));
    }

    // ISEARCH~text~slot~page : items that fit an outfit slot (slot index as in the outfit, 11-13 = weapons)
    void OpItemSearch(Player* p, std::vector<std::string> const& a)
    {
        static std::vector<std::set<uint32>> const types = {
            { 1 }, { 3 }, { 4 }, { 5, 20 }, { 6 }, { 7 }, { 8 }, { 9 }, { 10 }, { 16 }, { 19 },
            { 13, 17, 21 }, { 13, 14, 22, 23 }, { 15, 25, 26 }, {},
        };
        std::string q = Lower(S(a, 2));
        uint32 slot = std::min<uint32>(U(a, 3), uint32(types.size() - 1));
        uint32 page = U(a, 4);
        int32 sub = S(a, 5).empty() ? -1 : int32(std::strtol(S(a, 5).c_str(), nullptr, 10));   // armor material / weapon type, -1 any
        uint32 sortBy = U(a, 6);              // 0 name, 1 quality (best first), 2 item level
        bool availOnly = U(a, 7) != 0;        // only items whose model exists in the game data
        uint32 qid = uint32(std::strtoul(q.c_str(), nullptr, 10));
        std::vector<ItemTemplate const*> hits;
        for (auto const& [id, it] : *sObjectMgr->GetItemTemplateStore())
        {
            if ((!types[slot].empty() && !types[slot].count(it.InventoryType)) || !it.DisplayInfoID)
                continue;
            if (!q.empty() && id != qid && Lower(it.Name1).find(q) == std::string::npos)
                continue;
            if (sub >= 0)
            {
                // weapons: 100 + weapon subclass; shields / held in off-hand use armor subclass 6 / InventoryType 23
                if (sub >= 100) { if (it.Class != ITEM_CLASS_WEAPON || int32(it.SubClass) != sub - 100) continue; }
                else if (sub == 99) { if (it.InventoryType != INVTYPE_HOLDABLE) continue; }
                else if (it.Class != ITEM_CLASS_ARMOR || int32(it.SubClass) != sub) continue;
            }
            if (availOnly && !sItemDisplayInfoStore.LookupEntry(it.DisplayInfoID))
                continue;
            hits.push_back(&it);
        }
        std::sort(hits.begin(), hits.end(), [&](ItemTemplate const* x, ItemTemplate const* y)
        {
            if ((x->ItemId == qid) != (y->ItemId == qid)) return x->ItemId == qid;
            if (sortBy == 1 && x->Quality != y->Quality) return x->Quality > y->Quality;
            if (sortBy == 2 && x->ItemLevel != y->ItemLevel) return x->ItemLevel > y->ItemLevel;
            return x->Name1 != y->Name1 ? x->Name1 < y->Name1 : x->ItemId < y->ItemId;
        });
        uint32 total = uint32(hits.size());
        uint32 pages = std::max<uint32>(1, (total + PAGE_SIZE - 1) / PAGE_SIZE);
        page = std::min(page, pages - 1);
        Send(p, Join("IB", total, page, pages));
        for (uint32 i = page * PAGE_SIZE; i < std::min(total, (page + 1) * PAGE_SIZE); ++i)
            Send(p, Join("IR", hits[i]->ItemId, Clean(hits[i]->Name1, 60), hits[i]->Quality, hits[i]->DisplayInfoID, hits[i]->InventoryType));
        Send(p, Join("IE", total, page, pages));
    }

    // ================================================================ change log -> shareable SQL
    // Every write marks the rows it touched (table + WHERE). Export reads those rows as they are NOW and writes
    // DELETE + INSERT for each, so the file is re-runnable and also carries deletions (row gone = DELETE only).
    void Mark(std::string const& tbl, std::string const& cond)
    {
        WorldDatabase.DirectExecute("INSERT IGNORE INTO coa_devmenu_changes (tbl, cond) VALUES ('{}', '{}')", Esc(tbl), Esc(cond));
    }
    std::string Eq(char const* col, uint64 v) { return std::string("`") + col + "` = " + std::to_string(v); }

    uint32 MaxOf(std::string const& sql)
    {
        QueryResult r = WorldDatabase.Query(sql);
        return r && !r->Fetch()[0].IsNull() ? r->Fetch()[0].Get<uint32>() : 0;
    }

    void MarkType(uint32 entry)
    {
        if (!entry)
            return;
        Mark("creature_template", Eq("entry", entry));
        Mark("creature_template_model", Eq("CreatureID", entry));
        Mark("creature_template_addon", Eq("entry", entry));
        Mark("creature_equip_template", Eq("CreatureID", entry));
        Mark("creature_onkill_reputation", Eq("creature_id", entry));
        Mark("npc_vendor", Eq("entry", entry));
        Mark("creature_default_trainer", Eq("CreatureId", entry));
        Mark("creature_queststarter", Eq("id", entry));
        Mark("creature_questender", Eq("id", entry));
        Mark("smart_scripts", Eq("entryorguid", entry) + " AND `source_type` = 0");
        Mark("coa_npc_outfit", Eq("entry", entry));
        // talk menus and trainers the menu made for this NPC
        uint32 menu = MaxOf("SELECT gossip_menu_id FROM creature_template WHERE entry = " + std::to_string(entry));
        if (menu >= 9998001 && menu <= 9998999)
        {
            Mark("gossip_menu", Eq("MenuID", menu));
            Mark("gossip_menu_option", Eq("MenuID", menu));
            if (QueryResult t = WorldDatabase.Query("SELECT TextID FROM gossip_menu WHERE MenuID = {}", menu))
                do Mark("npc_text", Eq("ID", t->Fetch()[0].Get<uint32>())); while (t->NextRow());
        }
        uint32 tr = MaxOf("SELECT TrainerId FROM creature_default_trainer WHERE CreatureId = " + std::to_string(entry));
        if (tr >= CLONE_FIRST && tr <= CLONE_LAST)
        {
            Mark("trainer", Eq("Id", tr));
            Mark("trainer_spell", Eq("TrainerId", tr));
        }
    }

    void MarkSpawn(uint32 guid)
    {
        Mark("creature", Eq("guid", guid));
        Mark("creature_addon", Eq("guid", guid));
        Mark("waypoint_data", Eq("id", uint64(guid) * 10));
        uint32 e = MaxOf("SELECT id FROM creature WHERE guid = " + std::to_string(guid));
        if (e >= CLONE_FIRST && e <= CLONE_LAST)
            MarkType(e);
    }

    void MarkGoType(uint32 e)
    {
        Mark("gameobject_template", Eq("entry", e));
        Mark("gameobject_template_addon", Eq("entry", e));
    }

    void MarkGo(uint32 guid)
    {
        Mark("gameobject", Eq("guid", guid));
        Mark("gameobject_addon", Eq("guid", guid));
        uint32 e = MaxOf("SELECT id FROM gameobject WHERE guid = " + std::to_string(guid));
        if (e >= GOTPL_FIRST && e <= GOTPL_LAST)
            MarkGoType(e);
    }

    void MarkQuest(uint32 id)
    {
        for (char const* t : { "quest_template", "quest_template_addon", "quest_offer_reward", "quest_request_items" })
            Mark(t, Eq("ID", id));
        Mark("creature_queststarter", Eq("quest", id));
        Mark("creature_questender", Eq("quest", id));
        Mark("waypoints", Eq("entry", ESCORT_WP_BASE + id));
    }

    // highest ids before an op, so whatever it created can be marked afterwards
    struct HighWater { uint32 cr = 0, go = 0, ct = 0, gt = 0, q = 0; };
    HighWater TakeHighWater()
    {
        HighWater h;
        h.cr = MaxOf("SELECT MAX(guid) FROM creature");
        h.go = MaxOf("SELECT MAX(guid) FROM gameobject");
        h.ct = MaxOf("SELECT MAX(entry) FROM creature_template");
        h.gt = MaxOf("SELECT MAX(entry) FROM gameobject_template");
        h.q = MaxOf("SELECT MAX(ID) FROM quest_template");
        return h;
    }
    void MarkNewSince(HighWater const& h)
    {
        if (QueryResult r = WorldDatabase.Query("SELECT guid FROM creature WHERE guid > {}", h.cr))
            do MarkSpawn(r->Fetch()[0].Get<uint32>()); while (r->NextRow());
        if (QueryResult r = WorldDatabase.Query("SELECT guid FROM gameobject WHERE guid > {}", h.go))
            do MarkGo(r->Fetch()[0].Get<uint32>()); while (r->NextRow());
        if (QueryResult r = WorldDatabase.Query("SELECT entry FROM creature_template WHERE entry > {}", h.ct))
            do MarkType(r->Fetch()[0].Get<uint32>()); while (r->NextRow());
        if (QueryResult r = WorldDatabase.Query("SELECT entry FROM gameobject_template WHERE entry > {}", h.gt))
            do MarkGoType(r->Fetch()[0].Get<uint32>()); while (r->NextRow());
        if (QueryResult r = WorldDatabase.Query("SELECT ID FROM quest_template WHERE ID > {}", h.q))
            do MarkQuest(r->Fetch()[0].Get<uint32>()); while (r->NextRow());
    }

    void SendChangeCount(Player* p) { Send(p, Join("SQLN", MaxOf("SELECT COUNT(*) FROM coa_devmenu_changes"))); }

    // SQLAREA~radius : every saved NPC and object around you (radius 0 = your whole zone)
    void OpSqlArea(Player* p, std::vector<std::string> const& a)
    {
        float r = F(a, 2);
        uint32 n = 0;
        std::string where = r > 0
            ? Acore::StringFormat("map = {} AND POW(position_x - ({}), 2) + POW(position_y - ({}), 2) <= {}", p->GetMapId(), p->GetPositionX(), p->GetPositionY(), r * r)
            : Acore::StringFormat("map = {} AND zoneId = {}", p->GetMapId(), p->GetZoneId());
        if (QueryResult q = WorldDatabase.Query("SELECT guid FROM creature WHERE " + where))
            do { MarkSpawn(q->Fetch()[0].Get<uint32>()); ++n; } while (q->NextRow());
        if (QueryResult q = WorldDatabase.Query("SELECT guid FROM gameobject WHERE " + where))
            do { MarkGo(q->Fetch()[0].Get<uint32>()); ++n; } while (q->NextRow());
        Ok(p, std::to_string(n) + " NPCs and objects added to the change set");
        SendChangeCount(p);
    }

    // SQLALL : everything made with the menu (its id ranges) and every spawn of it
    void OpSqlAll(Player* p)
    {
        if (QueryResult q = WorldDatabase.Query("SELECT guid FROM creature WHERE id BETWEEN {} AND {}", CLONE_FIRST, CLONE_LAST))
            do MarkSpawn(q->Fetch()[0].Get<uint32>()); while (q->NextRow());
        if (QueryResult q = WorldDatabase.Query("SELECT entry FROM creature_template WHERE entry BETWEEN {} AND {}", CLONE_FIRST, CLONE_LAST))
            do MarkType(q->Fetch()[0].Get<uint32>()); while (q->NextRow());
        if (QueryResult q = WorldDatabase.Query("SELECT guid FROM gameobject WHERE id BETWEEN {} AND {}", GOTPL_FIRST, GOTPL_LAST))
            do MarkGo(q->Fetch()[0].Get<uint32>()); while (q->NextRow());
        if (QueryResult q = WorldDatabase.Query("SELECT ID FROM quest_template WHERE ID BETWEEN {} AND {}", QUEST_FIRST, QUEST_LAST))
            do MarkQuest(q->Fetch()[0].Get<uint32>()); while (q->NextRow());
        Ok(p, "Everything made with the dev menu added to the change set");
        SendChangeCount(p);
    }

    std::string SqlValue(Field const& f)
    {
        if (f.IsNull())
            return "NULL";
        std::string v = f.Get<std::string>();
        WorldDatabase.EscapeString(v);
        return "'" + v + "'";
    }

    // SQLEXP~name : writes devmenu_sql/<date>_<name>.sql next to worldserver
    void OpSqlExport(Player* p, std::vector<std::string> const& a)
    {
        std::string name;
        for (char ch : S(a, 2))
            if (std::isalnum(uint8(ch)) || ch == '-' || ch == '_') name += ch;
        if (name.empty()) name = "changes";
        // CoA repository format (jealous-sound pending_db_world lint): no DELETE on the protected template tables
        // (upsert instead), every other INSERT right after its DELETE, backticked names, module-only tables left out
        bool coa = S(a, 3) == "coa";
        static std::set<std::string> const protectedTables = { "creature_template", "gameobject_template", "item_template", "quest_template" };
        QueryResult list = WorldDatabase.Query("SELECT tbl, cond FROM coa_devmenu_changes ORDER BY tbl, cond");
        if (!list)
            return Err(p, "Nothing in the change set yet");
        std::filesystem::create_directories("devmenu_sql");
        time_t now = time(nullptr);
        std::tm lt = *std::localtime(&now);
        char stamp[32], day[16];
        strftime(stamp, sizeof(stamp), "%Y_%m_%d_%H%M", &lt);
        strftime(day, sizeof(day), "%Y%m%d", &lt);
        std::string path;
        if (coa)
        {
            std::string low = Lower(name);
            for (char& ch : low) if (ch == '-') ch = '_';
            for (uint32 n = 0; n < 100 && (path.empty() || std::filesystem::exists(path)); ++n)
                path = Acore::StringFormat("devmenu_sql/rev_{}_{:02}_{}.sql", day, n, low);
        }
        else
            path = std::string("devmenu_sql/") + stamp + "_" + name + ".sql";
        std::ofstream out(path, std::ios::binary);
        if (!out)
            return Err(p, "Could not write " + path);
        out << "-- Made with ilusixn Dev Menu (" << stamp << "). World database. Safe to run more than once.\n";
        if (!coa)
            out << "CREATE TABLE IF NOT EXISTS `coa_npc_outfit` (`entry` INT UNSIGNED NOT NULL PRIMARY KEY, `outfit` VARCHAR(600) NOT NULL, "
                   "`comment` VARCHAR(100) NOT NULL DEFAULT '') ENGINE=InnoDB COMMENT='Dev Menu: player-race NPC looks';\n"
                   "CREATE TABLE IF NOT EXISTS `coa_devmenu_heirloom` (`entry` INT UNSIGNED NOT NULL PRIMARY KEY, `stats` VARCHAR(200) NOT NULL, "
                   "`max_level` TINYINT UNSIGNED NOT NULL DEFAULT 80) ENGINE=InnoDB COMMENT='Dev Menu: heirloom items, stat gained per level';\n";
        uint32 rows = 0;
        std::string skippedLooks, keptTemplates;
        do
        {
            std::string tbl = list->Fetch()[0].Get<std::string>(), cond = list->Fetch()[1].Get<std::string>();
            if (!MaxOf("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = '" + Esc(tbl) + "'"))
                continue;   // a table this server doesn't have
            QueryResult r = WorldDatabase.Query("SELECT * FROM `" + tbl + "` WHERE " + cond);
            if (coa && tbl == "coa_npc_outfit")
            {
                if (r)
                    skippedLooks += (skippedLooks.empty() ? "" : ", ") + cond.substr(cond.find('=') + 2);
                continue;
            }
            bool upsert = coa && protectedTables.count(tbl);
            if (upsert && !r)
            {
                keptTemplates += "\n-- " + tbl + " " + cond + " was deleted on the editing server (protected table: not deleted here)";
                continue;
            }
            if (upsert)
                out << "\n";
            else
                out << "\nDELETE FROM `" << tbl << "` WHERE " << cond << ";\n";
            if (!r)
                continue;
            std::string cols, update;
            for (uint32 i = 0; i < r->GetFieldCount(); ++i)
            {
                std::string c = r->GetFieldName(i);
                cols += (i ? ", `" : "`") + c + "`";
                update += (i ? ", `" : "`") + c + "` = VALUES(`" + c + "`)";
            }
            out << "INSERT INTO `" << tbl << "` (" << cols << ")\nVALUES\n";
            bool first = true;
            do
            {
                Field* f = r->Fetch();
                out << (first ? "(" : ",\n(");
                for (uint32 i = 0; i < r->GetFieldCount(); ++i)
                    out << (i ? "," : "") << SqlValue(f[i]);
                out << ")";
                first = false;
                ++rows;
            } while (r->NextRow());
            if (upsert)
                out << "\nON DUPLICATE KEY UPDATE " << update;
            out << ";\n";
        } while (list->NextRow());
        if (!keptTemplates.empty())
            out << keptTemplates << "\n";
        if (!skippedLooks.empty())
            out << "\n-- Dressed NPC looks are not included (module table coa_npc_outfit): " << skippedLooks
                << "\n-- On a server without the Dev Menu module these NPCs show their race's base model.\n";
        out.close();
        std::string full = std::filesystem::absolute(path).string();
        Ok(p, "Exported " + std::to_string(rows) + " rows");
        Send(p, Join("SQLF", Clean(full, 220), rows));
    }

    // ====================================================================================================
    // Create an item (item_template rows in the dev range) and heirlooms that grow with your level
    // ====================================================================================================
    // The dev item range starts at 9400001 (DevMenu.Items.FirstId overrides it); LoadHeirlooms grows the fast id table once at startup so a stock core fits.
    uint32 ITEM_FIRST = 9400001, ITEM_LAST = 9409999;

    struct HeirStat { uint32 type; float per; };
    struct Heirloom { std::vector<HeirStat> st; uint32 maxLevel = 80; };
    std::map<uint32, Heirloom> g_heir;
    std::mutex g_heirLock;
    std::atomic<bool> g_heirAny{ false };
    std::unordered_map<ObjectGuid::LowType, std::vector<std::pair<uint32, int32>>> g_heirApplied;
    std::unordered_map<ObjectGuid::LowType, uint32> g_heirTimer;

    char const* StatLabel(uint32 t)
    {
        switch (t)
        {
            case 0: return "Mana"; case 1: return "Health"; case 3: return "Agility"; case 4: return "Strength"; case 5: return "Intellect";
            case 6: return "Spirit"; case 7: return "Stamina"; case 12: return "Defense rating"; case 13: return "Dodge rating";
            case 14: return "Parry rating"; case 15: return "Block rating"; case 31: return "Hit rating"; case 32: return "Crit rating";
            case 35: return "Resilience rating"; case 36: return "Haste rating"; case 37: return "Expertise rating"; case 38: return "Attack power";
            case 39: return "Ranged attack power"; case 43: return "Mana per 5 sec"; case 44: return "Armor penetration"; case 45: return "Spell power";
            case 46: return "Health per 5 sec"; case 47: return "Spell penetration";
        }
        return nullptr;
    }

    // "7:1.5,4:1" -> stats that grow per level
    std::vector<HeirStat> ParseHeir(std::string const& s)
    {
        std::vector<HeirStat> out;
        for (std::string const& part : Split(s, ','))
        {
            size_t c = part.find(':');
            if (c == std::string::npos)
                continue;
            uint32 t = uint32(std::strtoul(part.c_str(), nullptr, 10));
            float per = std::strtof(part.c_str() + c + 1, nullptr);
            if (StatLabel(t) && per > 0.f && per < 1000.f && out.size() < 5)
                out.push_back({ t, per });
        }
        return out;
    }

    std::string HeirText(Heirloom const& h)
    {
        std::string t = "Heirloom: grows with your level (";
        for (size_t i = 0; i < h.st.size(); ++i)
        {
            char buf[64];
            snprintf(buf, sizeof buf, "%+g", double(h.st[i].per));
            t += (i ? ", " : "") + std::string(buf) + " " + StatLabel(h.st[i].type);
        }
        return t + " per level, up to level " + std::to_string(h.maxLevel) + ").";
    }

    void LoadHeirlooms()
    {
        WorldDatabase.DirectExecute("CREATE TABLE IF NOT EXISTS coa_devmenu_heirloom (entry INT UNSIGNED NOT NULL PRIMARY KEY, stats VARCHAR(200) NOT NULL, "
            "max_level TINYINT UNSIGNED NOT NULL DEFAULT 80) ENGINE=InnoDB COMMENT='Dev Menu: heirloom items, stat gained per level'");
        std::lock_guard<std::mutex> lock(g_heirLock);
        g_heir.clear();
        if (QueryResult r = WorldDatabase.Query("SELECT entry, stats, max_level FROM coa_devmenu_heirloom"))
            do
            {
                Heirloom h;
                h.st = ParseHeir(r->Fetch()[1].Get<std::string>());
                h.maxLevel = r->Fetch()[2].Get<uint8>();
                if (!h.st.empty())
                    g_heir[r->Fetch()[0].Get<uint32>()] = h;
            } while (r->NextRow());
        g_heirAny = !g_heir.empty();
        // room for new item templates without the store ever rehashing while maps run
        auto& store = const_cast<ItemTemplateContainer&>(*sObjectMgr->GetItemTemplateStore());
        store.reserve(store.size() + 20000);
        auto& fast = const_cast<std::vector<ItemTemplate*>&>(*sObjectMgr->GetItemTemplateStoreFast());
        uint32 maxId = fast.empty() ? 0 : uint32(fast.size() - 1);
        uint32 first = sConfigMgr->GetOption<uint32>("DevMenu.Items.FirstId", 0);
        if (!first)
            first = 9400001;
        ITEM_FIRST = first; ITEM_LAST = first + 9998;
        if (fast.size() <= ITEM_LAST)
            fast.resize(ITEM_LAST + 1, nullptr);   // done once at startup, before any map thread reads the table
        LOG_INFO("module", ">> Dev Menu: new items use ids {}-{}", ITEM_FIRST, ITEM_LAST);
        LOG_INFO("module", ">> Dev Menu: {} heirloom items", g_heir.size());
    }

    void ApplyBonusStat(Player* p, uint32 t, int32 v, bool apply)
    {
        float f = float(v);
        switch (t)
        {
            case 0: p->HandleStatFlatModifier(UNIT_MOD_MANA, BASE_VALUE, f, apply); break;
            case 1: p->HandleStatFlatModifier(UNIT_MOD_HEALTH, BASE_VALUE, f, apply); break;
            case 3: p->HandleStatFlatModifier(UNIT_MOD_STAT_AGILITY, BASE_VALUE, f, apply); p->UpdateStatBuffMod(STAT_AGILITY); break;
            case 4: p->HandleStatFlatModifier(UNIT_MOD_STAT_STRENGTH, BASE_VALUE, f, apply); p->UpdateStatBuffMod(STAT_STRENGTH); break;
            case 5: p->HandleStatFlatModifier(UNIT_MOD_STAT_INTELLECT, BASE_VALUE, f, apply); p->UpdateStatBuffMod(STAT_INTELLECT); break;
            case 6: p->HandleStatFlatModifier(UNIT_MOD_STAT_SPIRIT, BASE_VALUE, f, apply); p->UpdateStatBuffMod(STAT_SPIRIT); break;
            case 7: p->HandleStatFlatModifier(UNIT_MOD_STAT_STAMINA, BASE_VALUE, f, apply); p->UpdateStatBuffMod(STAT_STAMINA); break;
            case 12: p->ApplyRatingMod(CR_DEFENSE_SKILL, v, apply); break;
            case 13: p->ApplyRatingMod(CR_DODGE, v, apply); break;
            case 14: p->ApplyRatingMod(CR_PARRY, v, apply); break;
            case 15: p->ApplyRatingMod(CR_BLOCK, v, apply); break;
            case 31: p->ApplyRatingMod(CR_HIT_MELEE, v, apply); p->ApplyRatingMod(CR_HIT_RANGED, v, apply); p->ApplyRatingMod(CR_HIT_SPELL, v, apply); break;
            case 32: p->ApplyRatingMod(CR_CRIT_MELEE, v, apply); p->ApplyRatingMod(CR_CRIT_RANGED, v, apply); p->ApplyRatingMod(CR_CRIT_SPELL, v, apply); break;
            case 35: p->ApplyRatingMod(CR_CRIT_TAKEN_MELEE, v, apply); p->ApplyRatingMod(CR_CRIT_TAKEN_RANGED, v, apply); p->ApplyRatingMod(CR_CRIT_TAKEN_SPELL, v, apply); break;
            case 36: p->ApplyRatingMod(CR_HASTE_MELEE, v, apply); p->ApplyRatingMod(CR_HASTE_RANGED, v, apply); p->ApplyRatingMod(CR_HASTE_SPELL, v, apply); break;
            case 37: p->ApplyRatingMod(CR_EXPERTISE, v, apply); break;
            case 38: p->HandleStatFlatModifier(UNIT_MOD_ATTACK_POWER, TOTAL_VALUE, f, apply); p->HandleStatFlatModifier(UNIT_MOD_ATTACK_POWER_RANGED, TOTAL_VALUE, f, apply); break;
            case 39: p->HandleStatFlatModifier(UNIT_MOD_ATTACK_POWER_RANGED, TOTAL_VALUE, f, apply); break;
            case 43: p->ApplyManaRegenBonus(v, apply); break;
            case 44: p->ApplyRatingMod(CR_ARMOR_PENETRATION, v, apply); break;
            case 45: p->ApplySpellPowerBonus(v, apply); break;
            case 46: p->ApplyHealthRegenBonus(v, apply); break;
            case 47: p->ApplySpellPenetrationBonus(v, apply); break;
        }
    }

    // what the equipped heirlooms add at the player's level; re-applied only when it changes
    void RefreshHeirlooms(Player* p)
    {
        std::vector<std::pair<uint32, int32>> want, old;
        {
            std::lock_guard<std::mutex> lock(g_heirLock);
            std::map<uint32, float> sum;
            for (uint8 s = EQUIPMENT_SLOT_START; s < EQUIPMENT_SLOT_END; ++s)
            {
                Item* it = p->GetItemByPos(INVENTORY_SLOT_BAG_0, s);
                if (!it || it->IsBroken())
                    continue;
                auto h = g_heir.find(it->GetEntry());
                if (h == g_heir.end())
                    continue;
                uint32 lv = std::min<uint32>(p->GetLevel(), h->second.maxLevel);
                for (HeirStat const& st : h->second.st)
                    sum[st.type] += st.per * float(lv);
            }
            for (auto const& [t, v] : sum)
                if (int32(v) != 0)
                    want.push_back({ t, int32(v) });
            auto& cur = g_heirApplied[p->GetGUID().GetCounter()];
            if (cur == want)
                return;
            old = cur;
            cur = want;
        }
        for (auto const& [t, v] : old)
            ApplyBonusStat(p, t, v, false);
        for (auto const& [t, v] : want)
            ApplyBonusStat(p, t, v, true);
        p->UpdateAllStats();
    }

    void HeirloomTick(Player* p, uint32 diff)
    {
        if (!g_heirAny)
            return;
        {
            std::lock_guard<std::mutex> lock(g_heirLock);
            uint32& t = g_heirTimer[p->GetGUID().GetCounter()];
            t += diff;
            if (t < 1000)
                return;
            t = 0;
        }
        RefreshHeirlooms(p);
    }

    // "k=v;k=v" (the client sends it in chunks through BUF)
    std::map<std::string, std::string> ParseSpec(std::string const& s)
    {
        std::map<std::string, std::string> out;
        for (std::string const& kv : Split(s, ';'))
        {
            size_t e = kv.find('=');
            if (e != std::string::npos)
                out[kv.substr(0, e)] = kv.substr(e + 1);
        }
        return out;
    }

    int64 SpecInt(std::map<std::string, std::string> const& m, char const* k, int64 def, int64 lo, int64 hi)
    {
        auto it = m.find(k);
        if (it == m.end() || it->second.empty())
            return def;
        return std::max(lo, std::min(hi, int64(std::strtoll(it->second.c_str(), nullptr, 10))));
    }

    float SpecFloat(std::map<std::string, std::string> const& m, char const* k, float def, float lo, float hi)
    {
        auto it = m.find(k);
        if (it == m.end() || it->second.empty())
            return def;
        return std::max(lo, std::min(hi, std::strtof(it->second.c_str(), nullptr)));
    }

    // the client caches item data by id: send the new version so tooltips update at once
    void PushItem(Player* p, uint32 id) { p->GetSession()->SendItemQuerySingleResponse(id); }

    // IMAKE : spec in the BUF text. id=0 makes a new item, id in range edits one made before
    void OpItemMake(Player* p, std::vector<std::string> const&)
    {
        std::string& buf = g_buf[p->GetGUID().GetCounter()];
        auto m = ParseSpec(buf);
        buf.clear();
        std::string name = Clean(m["name"], 100);
        if (name.empty())
            return Err(p, "Give the item a name");
        uint32 id = uint32(SpecInt(m, "id", 0, 0, 4294967295LL));
        if (id && (id < ITEM_FIRST || id > ITEM_LAST))
            return Err(p, "Only items made with the dev menu can be edited");
        if (!id && !(id = NextFree("item_template", "entry", ITEM_FIRST, ITEM_LAST)))
            return Err(p, "No free item id left");

        uint32 cls = uint32(SpecInt(m, "cls", 4, 0, 15)), sub = uint32(SpecInt(m, "sub", 0, 0, 20));
        uint32 q = uint32(SpecInt(m, "q", 4, 0, 7)), inv = uint32(SpecInt(m, "inv", 0, 0, 28));
        uint32 disp = uint32(SpecInt(m, "disp", 0, 0, 1000000)), ilvl = uint32(SpecInt(m, "ilvl", 1, 0, 1000)), rlvl = uint32(SpecInt(m, "rlvl", 0, 0, 255));
        uint32 bond = uint32(SpecInt(m, "bond", 0, 0, 3));
        int64 buy = SpecInt(m, "buy", 0, 0, 2000000000), sell = SpecInt(m, "sell", 0, 0, 2000000000);
        uint32 armor = uint32(SpecInt(m, "armor", 0, 0, 100000)), block = uint32(SpecInt(m, "blk", 0, 0, 100000));
        float dmin = SpecFloat(m, "dmin", 0, 0, 100000), dmax = SpecFloat(m, "dmax", 0, 0, 100000);
        uint32 delay = uint32(SpecInt(m, "dspd", 1000, 100, 10000));
        int32 spell = int32(SpecInt(m, "sp", 0, 0, 2000000)), trig = int32(SpecInt(m, "spt", 1, 0, 6));
        int32 stack = int32(SpecInt(m, "stack", 1, 1, 1000)), maxc = int32(SpecInt(m, "maxc", 0, 0, 1000));
        uint32 dur = uint32(SpecInt(m, "dur", 0, 0, 65000)), mat = uint32(SpecInt(m, "mat", 0, 0, 20)), sheath = uint32(SpecInt(m, "sheath", 0, 0, 7));
        bool bound = SpecInt(m, "bound", 0, 0, 1) != 0;
        uint32 stT[10] = {}; int32 stV[10] = {};
        uint32 nst = 0;
        for (int i = 0; i < 10; ++i)
        {
            auto it = m.find("s" + std::to_string(i + 1));
            if (it == m.end())
                continue;
            size_t c = it->second.find(':');
            if (c == std::string::npos)
                continue;
            uint32 t = uint32(std::strtoul(it->second.c_str(), nullptr, 10));
            int32 v = int32(std::strtol(it->second.c_str() + c + 1, nullptr, 10));
            if (v && StatLabel(t))
            {
                stT[nst] = t; stV[nst] = v; ++nst;
            }
        }

        Heirloom heir;
        heir.st = ParseHeir(m["hv"]);
        heir.maxLevel = uint32(SpecInt(m, "hmax", 80, 1, 255));
        std::string desc = Clean(m["desc"], 300);
        if (!heir.st.empty())
        {
            q = 7; bound = true;
            desc += (desc.empty() ? "" : " ") + HeirText(heir);
        }
        uint32 flags = bound ? 0x08000000u : 0u;

        std::ostringstream sql;
        sql << "REPLACE INTO item_template (entry, class, subclass, name, displayid, Quality, Flags, BuyPrice, SellPrice, InventoryType, ItemLevel, RequiredLevel, "
            << "maxcount, stackable, dmg_min1, dmg_max1, dmg_type1, armor, delay, spellid_1, spelltrigger_1, bonding, description, Material, sheath, block, MaxDurability";
        for (uint32 i = 0; i < 10; ++i)
            sql << ", stat_type" << (i + 1) << ", stat_value" << (i + 1);
        sql << ") VALUES (" << id << ", " << cls << ", " << sub << ", '" << Esc(name) << "', " << disp << ", " << q << ", " << flags << ", " << buy << ", " << sell
            << ", " << inv << ", " << ilvl << ", " << rlvl << ", " << maxc << ", " << stack << ", " << dmin << ", " << dmax << ", 0, " << armor << ", " << delay
            << ", " << spell << ", " << trig << ", " << bond << ", '" << Esc(desc) << "', " << mat << ", " << sheath << ", " << block << ", " << dur;
        for (uint32 i = 0; i < 10; ++i)
            sql << ", " << stT[i] << ", " << stV[i];
        sql << ")";
        WorldDatabase.DirectExecute("{}", sql.str());

        // the in-memory template, in place (existing copies of the item see it at once)
        auto& store = const_cast<ItemTemplateContainer&>(*sObjectMgr->GetItemTemplateStore());
        ItemTemplate& t = store[id];
        t = ItemTemplate();
        t.ItemId = id; t.Class = cls; t.SubClass = sub; t.SoundOverrideSubclass = -1; t.Name1 = name; t.DisplayInfoID = disp; t.Quality = q;
        t.Flags = ItemFlags(flags); t.BuyCount = 1; t.BuyPrice = int32(buy); t.SellPrice = uint32(sell); t.InventoryType = inv;
        t.AllowableClass = GetItemAllowableClassMask(uint32(int32(-1))); t.AllowableRace = uint32(int32(-1));
        t.ItemLevel = ilvl; t.RequiredLevel = rlvl; t.MaxCount = maxc; t.Stackable = stack;
        t.StatsCount = nst;
        for (uint32 i = 0; i < nst; ++i)
        {
            t.ItemStat[i].ItemStatType = stT[i]; t.ItemStat[i].ItemStatValue = stV[i];
        }
        t.Damage[0].DamageMin = dmin; t.Damage[0].DamageMax = dmax;
        t.Armor = armor; t.Delay = delay; t.Bonding = bond; t.Description = desc; t.Material = int32(mat); t.Sheath = sheath; t.Block = block; t.MaxDurability = dur;
        t.RequiredDisenchantSkill = uint32(int32(-1));
        for (auto& sp : t.Spells)
        {
            sp.SpellCooldown = -1; sp.SpellCategoryCooldown = -1;
        }
        t.Spells[0].SpellId = spell; t.Spells[0].SpellTrigger = uint32(trig);
        auto& fast = const_cast<std::vector<ItemTemplate*>&>(*sObjectMgr->GetItemTemplateStoreFast());
        if (id < fast.size())
            fast[id] = &t;

        if (!heir.st.empty())
        {
            std::string spec;
            for (size_t i = 0; i < heir.st.size(); ++i)
                spec += (i ? "," : "") + std::to_string(heir.st[i].type) + ":" + std::to_string(heir.st[i].per);
            WorldDatabase.DirectExecute("REPLACE INTO coa_devmenu_heirloom (entry, stats, max_level) VALUES ({}, '{}', {})", id, spec, heir.maxLevel);
            std::lock_guard<std::mutex> lock(g_heirLock);
            g_heir[id] = heir;
            g_heirAny = true;
        }
        else
        {
            WorldDatabase.DirectExecute("DELETE FROM coa_devmenu_heirloom WHERE entry = {}", id);
            std::lock_guard<std::mutex> lock(g_heirLock);
            g_heir.erase(id);
            g_heirAny = !g_heir.empty();
        }
        Mark("item_template", Eq("entry", id));
        Mark("coa_devmenu_heirloom", Eq("entry", id));
        PushItem(p, id);
        Ok(p, "Saved " + name);
        Send(p, Join("IMK", id, name));
    }

    void OpItemDelete(Player* p, std::vector<std::string> const& a)
    {
        uint32 id = U(a, 2);
        if (id < ITEM_FIRST || id > ITEM_LAST)
            return Err(p, "Only items made with the dev menu can be deleted");
        Mark("item_template", Eq("entry", id));
        Mark("coa_devmenu_heirloom", Eq("entry", id));
        WorldDatabase.DirectExecute("DELETE FROM item_template WHERE entry = {}", id);
        WorldDatabase.DirectExecute("DELETE FROM coa_devmenu_heirloom WHERE entry = {}", id);
        {
            std::lock_guard<std::mutex> lock(g_heirLock);
            g_heir.erase(id);
            g_heirAny = !g_heir.empty();
        }
        Ok(p, "Item deleted (copies already in bags vanish after a server restart)");
        Send(p, Join("IDL", id));
    }

    // ILIST : the items made with the menu, newest first
    void OpItemList(Player* p)
    {
        Send(p, "ILB~0");
        if (QueryResult r = WorldDatabase.Query("SELECT entry, name, Quality, displayid, InventoryType FROM item_template WHERE entry BETWEEN {} AND {} ORDER BY entry DESC LIMIT 80", ITEM_FIRST, ITEM_LAST))
            do
            {
                Field* f = r->Fetch();
                Send(p, Join("ILR", f[0].Get<uint32>(), Clean(f[1].Get<std::string>(), 60), uint32(f[2].Get<uint8>()), f[3].Get<uint32>(), uint32(f[4].Get<uint8>())));
            } while (r->NextRow());
        Send(p, "ILE~0");
    }

    // IGET~id : every field of an item made with the menu, to edit it
    void OpItemGet(Player* p, std::vector<std::string> const& a)
    {
        uint32 id = U(a, 2);
        ItemTemplate const* t = sObjectMgr->GetItemTemplate(id);
        if (!t)
            return Err(p, "No item with that id");
        auto kv = [&](std::string const& k, std::string const& v) { Send(p, Join("IGK", k, v)); };
        kv("id", std::to_string(id)); kv("name", Clean(t->Name1, 100));
        std::string desc = t->Description;
        size_t h = desc.find("Heirloom: grows");
        if (h != std::string::npos)
            desc = desc.substr(0, h > 0 ? h - 1 : 0);   // rebuilt from the stats on save
        kv("desc", Clean(desc, 200));
        kv("cls", std::to_string(t->Class)); kv("sub", std::to_string(t->SubClass)); kv("q", std::to_string(t->Quality)); kv("inv", std::to_string(t->InventoryType));
        kv("disp", std::to_string(t->DisplayInfoID)); kv("ilvl", std::to_string(t->ItemLevel)); kv("rlvl", std::to_string(t->RequiredLevel));
        kv("bond", std::to_string(t->Bonding)); kv("buy", std::to_string(t->BuyPrice)); kv("sell", std::to_string(t->SellPrice));
        kv("armor", std::to_string(t->Armor)); kv("blk", std::to_string(t->Block));
        kv("dmin", std::to_string(int(t->Damage[0].DamageMin))); kv("dmax", std::to_string(int(t->Damage[0].DamageMax))); kv("dspd", std::to_string(t->Delay));
        kv("sp", std::to_string(t->Spells[0].SpellId)); kv("spt", std::to_string(t->Spells[0].SpellTrigger));
        kv("stack", std::to_string(t->Stackable)); kv("maxc", std::to_string(t->MaxCount)); kv("dur", std::to_string(t->MaxDurability));
        kv("mat", std::to_string(t->Material)); kv("sheath", std::to_string(t->Sheath)); kv("bound", (uint32(t->Flags) & 0x08000000u) ? "1" : "0");
        for (uint32 i = 0; i < t->StatsCount; ++i)
            kv("s" + std::to_string(i + 1), std::to_string(t->ItemStat[i].ItemStatType) + ":" + std::to_string(t->ItemStat[i].ItemStatValue));
        {
            std::lock_guard<std::mutex> lock(g_heirLock);
            auto hv = g_heir.find(id);
            if (hv != g_heir.end())
            {
                std::string spec;
                for (size_t i = 0; i < hv->second.st.size(); ++i)
                {
                    char buf[48];
                    snprintf(buf, sizeof buf, "%u:%g", hv->second.st[i].type, double(hv->second.st[i].per));
                    spec += (i ? "," : "") + std::string(buf);
                }
                kv("hv", spec); kv("hmax", std::to_string(hv->second.maxLevel));
            }
        }
        Send(p, "IGE~0");
    }

    // IGIVE~id~count : any item into your bags
    void OpItemGive(Player* p, std::vector<std::string> const& a)
    {
        uint32 id = U(a, 2), n = std::max<uint32>(1, std::min<uint32>(U(a, 3, 1), 1000));
        ItemTemplate const* t = sObjectMgr->GetItemTemplate(id);
        if (!t)
            return Err(p, "No item with that id");
        if (!p->AddItem(id, n))
            return Err(p, "Your bags are full");
        Ok(p, "Added " + Clean(t->Name1, 50));
    }

    // ====================================================================================================
    // Your character tab
    // ====================================================================================================
    void RunCommand(Player* p, std::string const& cmd)
    {
        ChatHandler(p->GetSession()).ParseCommands(cmd);
    }

    void SendMeState(Player* p)
    {
        Send(p, Join("MS", p->IsGameMaster() ? 1 : 0, p->GetCommandStatus(CHEAT_GOD) ? 1 : 0, p->GetCommandStatus(CHEAT_CASTTIME) ? 1 : 0,
            p->GetCommandStatus(CHEAT_COOLDOWN) ? 1 : 0, p->GetCommandStatus(CHEAT_POWER) ? 1 : 0, p->GetCommandStatus(CHEAT_WATERWALK) ? 1 : 0,
            p->isGMChat() ? 1 : 0, p->CanFly() ? 1 : 0, p->isTaxiCheater() ? 1 : 0, uint32(p->GetLevel()), uint32(p->GetMoney() / 10000)));
    }

    // heirlooms of the retail game, per class: shoulders, chest, rings and trinkets, weapons
    std::vector<uint32> HeirloomSet(Player* p, bool all)
    {
        static std::vector<uint32> const everything = { 42985, 44107, 42950, 42951, 42952, 42984, 44101, 44102, 44103, 44105, 42949, 44099, 44100, 48677, 48683, 48687,
            48689, 48685, 48691, 50255, 42991, 42992, 44097, 44098, 48716, 44096, 42944, 44091, 42946, 42943, 48718, 44092, 42947, 44095, 42948, 44094, 42945, 44093, 69, 52887, 57403 };
        if (all)
            return everything;
        bool horde = p->GetTeamId() == TEAM_HORDE;
        std::vector<uint32> out = { 50255, 42991, 42992, horde ? 44097u : 44098u };
        auto add = [&](std::initializer_list<uint32> l) { out.insert(out.end(), l); };
        switch (p->getClass())
        {
            case CLASS_WARRIOR:      add({ 42949, 48685, 42943, 44092, 42945, 44096, 42946, 44093 }); break;
            case CLASS_PALADIN:      add({ 42949, 48685, 42948, 44094, 44092, 42945, 48716, 48718 }); break;
            case CLASS_HUNTER:       add({ 44101, 48683, 42946, 44093, 42943, 44092, 42947, 44095, 42944 }); break;
            case CLASS_ROGUE:        add({ 42952, 48689, 44091, 42944, 44096, 42945, 48716, 42946, 44093 }); break;
            case CLASS_PRIEST:       add({ 42985, 48691, 42947, 44095, 44091, 48716, 44094, 69 }); break;
            case CLASS_DEATH_KNIGHT: add({ 42949, 48685, 42943, 44092, 42948, 42945, 44096, 48716, 48718 }); break;
            case CLASS_SHAMAN:       add({ 42951, 48683, 44094, 48716, 42944, 42947, 44095, 48718 }); break;
            case CLASS_MAGE:         add({ 42985, 48691, 42947, 44095, 44091, 44096, 69 }); break;
            case CLASS_WARLOCK:      add({ 42985, 48691, 42947, 44095, 44091, 44096, 69 }); break;
            case CLASS_DRUID:        add({ 42984, 48687, 42947, 44095, 48716, 44094, 44091, 48718 }); break;
            default: return everything;
        }
        return out;
    }

    std::string SetName(ItemSetEntry const* s)
    {
        for (char const* n : s->name)
            if (n && *n)
                return n;
        return "";
    }

    // MESETS~text~page~mineOnly : item sets (PvP seasons, raid tiers, dungeon sets...)
    void OpMeSets(Player* p, std::vector<std::string> const& a)
    {
        std::string q = Lower(S(a, 2));
        uint32 page = U(a, 3);
        bool mineOnly = U(a, 4) != 0;
        uint32 lvl = U(a, 5);   // 0 = any, else sets whose highest required level is in lvl..lvl+9 (1 = 0..9)
        struct Row { uint32 id; std::string name; uint32 ilvl, count; };
        std::vector<Row> hits;
        for (uint32 i = 1; i < sItemSetStore.GetNumRows(); ++i)
        {
            ItemSetEntry const* s = sItemSetStore.LookupEntry(i);
            if (!s)
                continue;
            std::string name = SetName(s);
            if (name.empty() || (!q.empty() && Lower(name).find(q) == std::string::npos))
                continue;
            uint32 n = 0, ilvl = 0, req = 0;
            bool usable = true;
            for (uint32 id : s->itemId)
            {
                ItemTemplate const* it = id ? sObjectMgr->GetItemTemplate(id) : nullptr;
                if (!it)
                    continue;
                ++n;
                ilvl = std::max(ilvl, it->ItemLevel);
                req = std::max(req, it->RequiredLevel);
                if (!(it->AllowableClass & p->getClassMask()))
                    usable = false;
            }
            if (!n || (mineOnly && !usable))
                continue;
            if (lvl && (req < (lvl == 1 ? 0 : lvl) || req > lvl + 9))
                continue;
            hits.push_back({ i, name, ilvl, n });
        }
        std::sort(hits.begin(), hits.end(), [](Row const& x, Row const& y) { return x.ilvl != y.ilvl ? x.ilvl > y.ilvl : x.name < y.name; });
        uint32 total = uint32(hits.size()), per = 12, pages = std::max<uint32>(1, (total + per - 1) / per);
        page = std::min(page, pages - 1);
        Send(p, Join("MSB", total, page, pages));
        for (uint32 i = page * per; i < std::min(total, (page + 1) * per); ++i)
            Send(p, Join("MSR", hits[i].id, Clean(hits[i].name, 60), hits[i].ilvl, hits[i].count));
        Send(p, Join("MSE", total, page, pages));
    }

    void GiveList(Player* p, std::vector<uint32> const& items, std::string const& what)
    {
        uint32 given = 0, full = 0;
        for (uint32 id : items)
        {
            if (!sObjectMgr->GetItemTemplate(id))
                continue;
            if (p->AddItem(id, 1))
                ++given;
            else
                ++full;
        }
        if (full)
            Err(p, "Bags full: " + std::to_string(full) + " items not added");
        Ok(p, what + ": " + std::to_string(given) + " items added");
    }

    void LearnAllMounts(Player* p)
    {
        uint32 learned = 0;
        for (auto const& [id, it] : *sObjectMgr->GetItemTemplateStore())
        {
            if (it.Class != ITEM_CLASS_MISC || it.SubClass != 5 || !it.Spells[0].SpellId)
                continue;
            SpellInfo const* si = sSpellMgr->GetSpellInfo(it.Spells[0].SpellId);
            if (!si)
                continue;
            uint32 mountSpell = 0;
            for (SpellEffectInfo const& e : si->Effects)
            {
                if (e.Effect == SPELL_EFFECT_LEARN_SPELL && e.TriggerSpell)
                    mountSpell = e.TriggerSpell;
                else if (e.Effect == SPELL_EFFECT_APPLY_AURA && e.ApplyAuraName == SPELL_AURA_MOUNTED)
                    mountSpell = si->Id;
            }
            if (mountSpell && !p->HasSpell(mountSpell) && sSpellMgr->GetSpellInfo(mountSpell))
            {
                p->learnSpell(mountSpell);
                ++learned;
            }
        }
        Ok(p, "Learned " + std::to_string(learned) + " mounts");
    }

    void LearnAllPets(Player* p)
    {
        uint32 learned = 0;
        for (auto const& [id, it] : *sObjectMgr->GetItemTemplateStore())
        {
            if (it.Class != ITEM_CLASS_MISC || it.SubClass != 2 || !it.Spells[0].SpellId)   // 2 = companion pets
                continue;
            SpellInfo const* si = sSpellMgr->GetSpellInfo(it.Spells[0].SpellId);
            if (!si)
                continue;
            for (SpellEffectInfo const& e : si->Effects)
                if (e.Effect == SPELL_EFFECT_LEARN_SPELL && e.TriggerSpell && !p->HasSpell(e.TriggerSpell) && sSpellMgr->GetSpellInfo(e.TriggerSpell))
                {
                    p->learnSpell(e.TriggerSpell);
                    ++learned;
                }
        }
        Ok(p, "Learned " + std::to_string(learned) + " pets");
    }

    // REPSEARCH~text~page : factions with your standing
    void OpRepSearch(Player* p, std::vector<std::string> const& a)
    {
        std::string q = Lower(S(a, 2));
        uint32 page = U(a, 3), per = 14;
        struct Row { uint32 id; std::string name; int32 st; };
        std::vector<Row> hits;
        for (uint32 i = 0; i < sFactionStore.GetNumRows(); ++i)
        {
            FactionEntry const* f = sFactionStore.LookupEntry(i);
            if (!f || !f->CanHaveReputation())
                continue;
            std::string n;
            for (char const* c : f->name) if (c && *c) { n = c; break; }
            if (n.empty() || (!q.empty() && Lower(n).find(q) == std::string::npos))
                continue;
            hits.push_back({ i, n, p->GetReputationMgr().GetReputation(f) });
        }
        std::sort(hits.begin(), hits.end(), [](Row const& x, Row const& y) { return x.name < y.name; });
        uint32 total = uint32(hits.size()), pages = std::max<uint32>(1, (total + per - 1) / per);
        page = std::min(page, pages - 1);
        Send(p, Join("RPB", total, page, pages));
        for (uint32 i = page * per; i < std::min(total, (page + 1) * per); ++i)
            Send(p, Join("RPR", hits[i].id, Clean(hits[i].name, 50), hits[i].st));
        Send(p, Join("RPE", total, page, pages));
    }

    // ME~what~arg... : one-click GM helpers on your own character
    void OpMe(Player* p, std::vector<std::string> const& a)
    {
        std::string w = S(a, 2);
        bool on = U(a, 3) != 0;
        auto toggle = [&](char const* base) { RunCommand(p, std::string(".") + base + (on ? " on" : " off")); };
        if (w == "state") return SendMeState(p);
        if (w == "gm") toggle("gm");
        else if (w == "gmfly") toggle("gm fly");
        else if (w == "gmchat") toggle("gm chat");
        else if (w == "god") toggle("cheat god");
        else if (w == "cast") toggle("cheat casttime");
        else if (w == "cd") toggle("cheat cooldown");
        else if (w == "power") toggle("cheat power");
        else if (w == "water") toggle("cheat waterwalk");
        else if (w == "taxi") { p->SetTaxiCheater(on); Ok(p, on ? "All flight paths unlocked" : "Flight paths back to normal"); }
        else if (w == "level")
        {
            uint32 lv = std::max<uint32>(1, std::min<uint32>(U(a, 3), sWorld->getIntConfig(CONFIG_MAX_PLAYER_LEVEL)));
            p->GiveLevel(lv);
            p->InitTalentForLevel();
            p->SetUInt32Value(PLAYER_XP, 0);
            Ok(p, "Level " + std::to_string(lv));
        }
        else if (w == "money")
        {
            int64 g = int64(std::strtoll(S(a, 3).c_str(), nullptr, 10));
            int64 cur = int64(p->GetMoney());
            int64 next = std::max<int64>(0, std::min<int64>(cur + g * 10000, MAX_MONEY_AMOUNT));
            p->SetMoney(uint32(next));
            Ok(p, "You now have " + std::to_string(next / 10000) + " gold");
        }
        else if (w == "honor") { p->SetHonorPoints(std::min<uint32>(p->GetHonorPoints() + U(a, 3), 75000)); Ok(p, "Honor added"); }
        else if (w == "arena") { p->SetArenaPoints(std::min<uint32>(p->GetArenaPoints() + U(a, 3), 5000)); Ok(p, "Arena points added"); }
        else if (w == "emblem")
        {
            static std::map<std::string, uint32> const e = { { "frost", 49426 }, { "triumph", 47241 }, { "conquest", 45624 }, { "heroism", 40752 }, { "valor", 40753 } };
            auto it = e.find(S(a, 3));
            if (it == e.end() || !sObjectMgr->GetItemTemplate(it->second))
                return Err(p, "Unknown emblem");
            uint32 n = std::max<uint32>(1, std::min<uint32>(U(a, 4, 100), 1000));
            if (p->AddItem(it->second, n)) Ok(p, std::to_string(n) + " emblems added"); else Err(p, "Your bags are full");
        }
        else if (w == "learn")
        {
            std::string k = S(a, 3);
            if (k == "class") RunCommand(p, ".learn all my class");
            else if (k == "default") RunCommand(p, ".learn all default");
            else if (k == "lang") RunCommand(p, ".learn all lang");
            else if (k == "skills") { p->UpdateSkillsToMaxSkillsForLevel(); Ok(p, "Skills raised to the maximum"); }
            else if (k == "mounts") LearnAllMounts(p);
            else if (k == "pets") LearnAllPets(p);
            else return Err(p, "Unknown learn option");
        }
        else if (w == "explore")
        {
            for (uint32 i = 0; i < PLAYER_EXPLORED_ZONES_SIZE; ++i)
                p->SetUInt32Value(PLAYER_EXPLORED_ZONES_1 + i, 0xFFFFFFFF);
            Ok(p, "Whole map revealed");
        }
        else if (w == "heal")
        {
            if (p->isDead()) p->ResurrectPlayer(1.0f);
            p->SetFullHealth();
            if (p->GetMaxPower(POWER_MANA)) p->SetPower(POWER_MANA, p->GetMaxPower(POWER_MANA));
            Ok(p, "Fully healed");
        }
        else if (w == "cooldowns") { p->RemoveAllSpellCooldown(); Ok(p, "Cooldowns cleared"); }
        else if (w == "repair") { p->DurabilityRepairAll(false, 0.0f, false); Ok(p, "Everything repaired"); }
        else if (w == "speed") { float s = std::max(0.1f, std::min(F(a, 3, 1.f), 50.f)); RunCommand(p, ".modify speed all " + std::to_string(s)); }
        else if (w == "scale") { float s = std::max(0.1f, std::min(F(a, 3, 1.f), 10.f)); RunCommand(p, ".modify scale " + std::to_string(s)); }
        else if (w == "rep")
        {
            float v = float(std::strtol(S(a, 4).c_str(), nullptr, 10));
            v = std::max(-42000.f, std::min(v, 42999.f));
            if (S(a, 3) == "all")
            {
                uint32 n = 0;
                for (uint32 i = 0; i < sFactionStore.GetNumRows(); ++i)
                    if (FactionEntry const* f = sFactionStore.LookupEntry(i))
                        if (f->CanHaveReputation()) { p->GetReputationMgr().SetReputation(f, v); ++n; }
                Ok(p, "Set " + std::to_string(n) + " factions");
            }
            else
            {
                FactionEntry const* f = sFactionStore.LookupEntry(U(a, 5));
                if (!f || !f->CanHaveReputation())
                    return Err(p, "That faction has no reputation");
                p->GetReputationMgr().SetReputation(f, v);
                Ok(p, "Reputation set");
            }
        }
        else if (w == "faction")
        {
            std::string k = S(a, 3);
            if (k == "neutral") { p->SetFaction(35); Ok(p, "Friendly to everyone until you log out"); }
            else
            {
                TeamId want = k == "horde" ? TEAM_HORDE : TEAM_ALLIANCE;
                if (p->GetTeamId() == want)
                    Ok(p, "You are already in that faction");
                else
                {
                    RunCommand(p, ".character changefaction");
                    Ok(p, "Faction change queued: log out to the character screen to finish it");
                }
            }
        }
        else if (w == "heirloom") GiveList(p, HeirloomSet(p, S(a, 3) == "all"), "Heirlooms");
        else if (w == "set")
        {
            ItemSetEntry const* s = sItemSetStore.LookupEntry(U(a, 3));
            if (!s)
                return Err(p, "No such set");
            std::vector<uint32> items;
            for (uint32 id : s->itemId)
                if (id)
                    items.push_back(id);
            GiveList(p, items, SetName(s));
        }
        else return Err(p, "Unknown option");
        SendMeState(p);
    }

    // ====================================================================================================
    // Morph tab and Server tab
    // ====================================================================================================
    // MORSEARCH~text~page : creature models by the name of a creature that uses them (or a display id)
    void OpMorphSearch(Player* p, std::vector<std::string> const& a)
    {
        std::string raw = S(a, 2);
        std::string q = Esc(raw);
        uint32 page = U(a, 3), per = 14;
        std::string cond = "1";
        if (!raw.empty())
        {
            cond = "t.name LIKE '%" + q + "%'";
            if (std::all_of(raw.begin(), raw.end(), [](unsigned char c) { return std::isdigit(c) != 0; }))
                cond += " OR m.CreatureDisplayID = " + std::to_string(std::strtoull(raw.c_str(), nullptr, 10));
        }
        std::string from = " FROM creature_template_model m JOIN creature_template t ON t.entry = m.CreatureID WHERE " + cond;
        uint32 total = MaxOf("SELECT COUNT(DISTINCT m.CreatureDisplayID)" + from);
        uint32 pages = std::max<uint32>(1, (total + per - 1) / per);
        page = std::min(page, pages - 1);
        Send(p, Join("MORB", total, page, pages));
        if (QueryResult r = WorldDatabase.Query("{}", "SELECT m.CreatureDisplayID, MIN(t.name), MIN(t.entry)" + from + " GROUP BY m.CreatureDisplayID ORDER BY MIN(t.name) LIMIT "
            + std::to_string(per) + " OFFSET " + std::to_string(page * per)))
            do
            {
                Field* f = r->Fetch();
                Send(p, Join("MORR", f[0].Get<uint32>(), Clean(f[1].Get<std::string>(), 60), f[2].Get<uint32>()));
            } while (r->NextRow());
        Send(p, Join("MORE", total, page, pages));
    }

    // MORPH~displayid (0 = back to normal)
    void OpMorph(Player* p, std::vector<std::string> const& a)
    {
        uint32 id = U(a, 2);
        if (!id)
        {
            p->DeMorph();
            Ok(p, "Back to normal");
            return Send(p, Join("MORN", 0));
        }
        if (!sCreatureDisplayInfoStore.LookupEntry(id))
            return Err(p, "No model with that display id");
        p->SetDisplayId(id);
        // a creature that uses this model: send its data to the client so the panel can draw it
        uint32 entry = MaxOf("SELECT IFNULL(MIN(CreatureID), 0) FROM creature_template_model WHERE CreatureDisplayID = " + std::to_string(id));
        if (entry && sObjectMgr->GetCreatureTemplate(entry))
        {
            WorldPacket q(CMSG_CREATURE_QUERY, 12);
            q << uint32(entry) << uint64(0);
            p->GetSession()->HandleCreatureQueryOpcode(q);
        }
        else
            entry = 0;
        Ok(p, "Morphed into display " + std::to_string(id));
        Send(p, Join("MORN", id, entry));
    }

    // ICONSEARCH~icon~page : items (one per look) whose inventory icon is that texture; answers like ISEARCH
    void OpIconSearch(Player* p, std::vector<std::string> const& a)
    {
        auto base = [](std::string s)
        {
            s = Lower(s);
            size_t c = s.find_last_of("\\/");
            return c == std::string::npos ? s : s.substr(c + 1);
        };
        std::string icon = base(S(a, 2));
        uint32 page = U(a, 3), per = 30;
        std::set<uint32> good;
        for (uint32 i = 0; i < sItemDisplayInfoStore.GetNumRows(); ++i)
            if (ItemDisplayInfoEntry const* e = sItemDisplayInfoStore.LookupEntry(i))
                if (e->inventoryIcon && base(e->inventoryIcon) == icon)
                    good.insert(e->ID);
        std::map<uint32, ItemTemplate const*> byLook;
        for (auto const& [id, it] : *sObjectMgr->GetItemTemplateStore())
            if (good.count(it.DisplayInfoID))
            {
                auto f = byLook.find(it.DisplayInfoID);
                if (f == byLook.end() || it.ItemId < f->second->ItemId)
                    byLook[it.DisplayInfoID] = &it;
            }
        std::vector<ItemTemplate const*> hits;
        for (auto const& [d, it] : byLook)
            hits.push_back(it);
        std::sort(hits.begin(), hits.end(), [](ItemTemplate const* x, ItemTemplate const* y) { return x->Name1 != y->Name1 ? x->Name1 < y->Name1 : x->ItemId < y->ItemId; });
        uint32 total = uint32(hits.size()), pages = std::max<uint32>(1, (total + per - 1) / per);
        page = std::min(page, pages - 1);
        Send(p, Join("IB", total, page, pages));
        for (uint32 i = page * per; i < std::min(total, (page + 1) * per); ++i)
            Send(p, Join("IR", hits[i]->ItemId, Clean(hits[i]->Name1, 60), hits[i]->Quality, hits[i]->DisplayInfoID, hits[i]->InventoryType));
        Send(p, Join("IE", total, page, pages));
    }

    // MORSTEP~id~dir : the next (or previous) display id that exists, and morph into it
    void OpMorphStep(Player* p, std::vector<std::string> const& a)
    {
        int64 id = int64(U(a, 2)), dir = S(a, 3) == "-1" ? -1 : 1, last = int64(sCreatureDisplayInfoStore.GetNumRows());
        for (int64 n = 0; n < last; ++n)
        {
            id += dir;
            if (id < 1) id = last - 1;
            if (id >= last) id = 1;
            if (sCreatureDisplayInfoStore.LookupEntry(uint32(id)))
                break;
        }
        std::vector<std::string> b = { "Q", "MORPH", std::to_string(id) };
        OpMorph(p, b);
    }

    // time of day for everyone online (a client re-syncs when it logs in)
    void SetTimeOfDay(uint32 hour, uint32 minute, float speed)
    {
        time_t now = time(nullptr);
        tm lt = *localtime(&now);
        lt.tm_hour = int(hour % 24); lt.tm_min = int(minute % 60); lt.tm_sec = 0;
        time_t t = mktime(&lt);
        WorldPacket data(SMSG_LOGIN_SETTIMESPEED, 12);
        data.AppendPackedTime(t);
        data << float(speed);
        data << uint32(0);
        for (auto const& [id, session] : sWorldSessionMgr->GetAllSessions())
            if (session->GetPlayer() && session->GetPlayer()->IsInWorld())
                session->GetPlayer()->SendDirectMessage(&data);
    }

    // SRVTELE~text~page : places from the game_tele table
    void OpTeleSearch(Player* p, std::vector<std::string> const& a)
    {
        std::string q = Lower(S(a, 2));
        uint32 page = U(a, 3), per = 14;
        struct Row { uint32 id; std::string name; uint32 map; };
        std::vector<Row> hits;
        for (auto const& [id, t] : sObjectMgr->GetGameTeleMap())
            if (q.empty() || Lower(t.name).find(q) != std::string::npos)
                hits.push_back({ id, t.name, t.mapId });
        std::sort(hits.begin(), hits.end(), [](Row const& x, Row const& y) { return x.name < y.name; });
        uint32 total = uint32(hits.size()), pages = std::max<uint32>(1, (total + per - 1) / per);
        page = std::min(page, pages - 1);
        Send(p, Join("TLB", total, page, pages));
        for (uint32 i = page * per; i < std::min(total, (page + 1) * per); ++i)
            Send(p, Join("TLR", hits[i].id, Clean(hits[i].name, 50), hits[i].map));
        Send(p, Join("TLE", total, page, pages));
    }

    // SRVEV~text~page : game events (holidays, seasonal things) with their on/off state
    void OpEventSearch(Player* p, std::vector<std::string> const& a)
    {
        std::string q = Esc(S(a, 2));
        uint32 page = U(a, 3), per = 14;
        std::string from = " FROM game_event WHERE description LIKE '%" + q + "%'";
        uint32 total = MaxOf("SELECT COUNT(*)" + from);
        uint32 pages = std::max<uint32>(1, (total + per - 1) / per);
        page = std::min(page, pages - 1);
        Send(p, Join("EVB", total, page, pages));
        if (QueryResult r = WorldDatabase.Query("{}", "SELECT eventEntry, description" + from + " ORDER BY eventEntry LIMIT " + std::to_string(per) + " OFFSET " + std::to_string(page * per)))
            do
            {
                Field* f = r->Fetch();
                uint32 id = f[0].Get<uint32>();
                Send(p, Join("EVR", id, Clean(f[1].Get<std::string>(), 60), sGameEventMgr->IsActiveEvent(uint16(id)) ? 1 : 0));
            } while (r->NextRow());
        Send(p, Join("EVE", total, page, pages));
    }

    // SRV~what~arg... : world helpers
    void OpServer(Player* p, std::vector<std::string> const& a)
    {
        std::string w = S(a, 2);
        if (w == "time")
        {
            float speed = S(a, 5) == "0" ? 0.f : S(a, 5) == "10" ? 0.1666667f : 0.01666667f;
            SetTimeOfDay(U(a, 3), U(a, 4), speed);
            return Ok(p, "Time set for everyone online (a client re-syncs when it logs in)");
        }
        if (w == "weather")
        {
            RunCommand(p, ".wchange " + std::to_string(std::min<uint32>(U(a, 3), 3)) + " " + std::to_string(std::max(0.f, std::min(F(a, 4, 1.f), 1.f))));
            return;
        }
        if (w == "tele")
        {
            auto const& m = sObjectMgr->GetGameTeleMap();
            auto it = m.find(U(a, 3));
            if (it == m.end())
                return Err(p, "No such place");
            p->TeleportTo(it->second.mapId, it->second.position_x, it->second.position_y, it->second.position_z, it->second.orientation);
            return Ok(p, "Teleporting to " + Clean(it->second.name, 40));
        }
        if (w == "event")
        {
            std::string how = S(a, 3) == "stop" ? "stop" : "start";
            RunCommand(p, ".event " + how + " " + std::to_string(U(a, 4)));
            return;
        }
        if (w == "announce")
        {
            std::string t = Clean(S(a, 3), 200);
            if (t.empty())
                return Err(p, "Type the announcement first");
            return RunCommand(p, ".announce " + t);
        }
        if (w == "saveall") { RunCommand(p, ".saveall"); return Ok(p, "All players saved"); }
        if (w == "info")
            return Send(p, Join("SI", uint32(sWorldSessionMgr->GetActiveSessionCount()), uint32(GameTime::GetUptime().count())));
        if (w == "reload")
        {
            static std::set<std::string> const ok = { "creature_template", "gameobject_template", "npc_vendor", "smart_scripts", "gossip_menu", "game_tele",
                "quest_template", "creature_text", "conditions", "loot_templates" };
            std::string t = S(a, 3);
            if (!ok.count(t))
                return Err(p, "Not in the allowed list");
            RunCommand(p, ".reload " + (t == "loot_templates" ? std::string("all_loot") : t));
            return Ok(p, "Reloaded " + t);
        }
        if (w == "appear" || w == "summon")
        {
            std::string n = Clean(S(a, 3), 20);
            n.erase(std::remove(n.begin(), n.end(), ' '), n.end());
            if (n.empty())
                return Err(p, "Type a player name first");
            return RunCommand(p, "." + w + " " + n);
        }
        Err(p, "Unknown option");
    }

    // ops that only read or only touch your recording: they never mark anything
    bool IsReadOnly(std::string const& op)
    {
        static std::set<std::string> const ro = { "HELLO", "SEARCH", "NEAR", "PPT", "PADD", "PUNDO", "PCLEAR", "PCLICK", "PADDAT", "PLIST", "BUF", "BUFC",
            "RGET", "RLOAD", "LGET", "NEWID", "QSEARCH", "GSEARCH", "ORACES", "ISEARCH", "DISGUISE", "UNDISGUISE", "OMINE", "OGET", "OPREV",
            "OPREVDEL", "XCSEARCH", "SPSEARCH", "GNEAR", "GTGT", "GPICK", "GSEL", "GGOTO", "SEL", "TGET", "CGET", "GOTO", "PSHOW", "PEDIT",
            "RESPAWN", "PLAY", "SQLN", "SQLAREA", "SQLALL", "SQLEXP", "SQLCLR", "ILIST", "IGET", "IGIVE", "ME", "MESETS", "ICONSEARCH", "REPSEARCH", "MORSEARCH", "MORPH", "MORSTEP", "SRV", "SRVTELE", "SRVEV" };
        return ro.count(op) != 0;
    }

    // marks what a write op is about to change (rows that will be deleted are marked too)
    void MarkBefore(std::string const& op, std::vector<std::string> const& a, Creature* c)
    {
        if (c)
        {
            MarkSpawn(c->GetSpawnId());
            static std::set<std::string> const typeOps = { "TSET", "CADD", "CDEL", "REP", "ROLE", "GUARD", "FACTION", "RENAME", "LEVEL", "MODEL", "VENDORADD", "ENTRY", "UNIQUE" };
            if (typeOps.count(op))
                MarkType(c->GetEntry());
            return;
        }
        if (op == "RSET" && RowTables().count(S(a, 2)))
            Mark(S(a, 2), Eq(RowTables().at(S(a, 2)).c_str(), U(a, 3)));
        else if ((op == "LADD" || op == "LDEL") && RowTables().count(S(a, 2)))
        {
            std::string kc = RowTables().at(S(a, 2));
            for (size_t i = 3; i < a.size(); ++i)
                if (a[i].rfind(kc + "=", 0) == 0)
                    Mark(S(a, 2), Eq(kc.c_str(), std::strtoull(a[i].c_str() + kc.size() + 1, nullptr, 10)));
        }
        else if (op == "RENAMET" || op == "VCUR") MarkType(U(a, 2));
        else if (op == "QDEL") MarkQuest(U(a, 2));
        else if (op == "QESCORT") { MarkQuest(U(a, 2)); MarkSpawn(U(a, 3)); MarkType(MaxOf("SELECT id FROM creature WHERE guid = " + std::to_string(U(a, 3)))); }
        else if (op == "OSAVE" && U(a, 2)) MarkSpawn(U(a, 2));
        else if (op == "IPRICE" && a.size() > 3 && !a[3].empty()) Mark("item_template", Eq("entry", U(a, 2)));
        else if (op == "GMOVE" || op == "GNUDGE" || op == "GNUDGEW" || op == "GROT" || op == "GFACE" || op == "GDEL") MarkGo(U(a, 2));
    }

    void DispatchOp(Player* p, std::string const& payload);

    // every request: SQL change-set ops, then the op itself with change tracking around it
    void Dispatch(Player* p, std::string const& payload)
    {
        std::vector<std::string> a = Split(payload, '~');
        if (a.size() < 2 || a[0] != "Q" || !sConfigMgr->GetOption<bool>("DevMenu.Enable", true)
            || uint32(p->GetSession()->GetSecurity()) < sConfigMgr->GetOption<uint32>("DevMenu.MinSecurity", SEC_GAMEMASTER))
            return DispatchOp(p, payload);   // it reports the error
        std::string const& op = a[1];
        if (op == "SQLN") return SendChangeCount(p);
        if (op == "SQLAREA") return OpSqlArea(p, a);
        if (op == "SQLALL") return OpSqlAll(p);
        if (op == "SQLEXP") return OpSqlExport(p, a);
        if (op == "SQLCLR") { WorldDatabase.DirectExecute("DELETE FROM coa_devmenu_changes"); Ok(p, "Change set cleared"); return SendChangeCount(p); }
        if (IsReadOnly(op))
            return DispatchOp(p, payload);
        static std::set<std::string> const globalOps = { "SPAWN", "DUP", "RENAMET", "RSET", "LADD", "LDEL", "QNEW", "QDEL", "QESCORT", "OSAVE",
            "IPRICE", "VCUR", "GSPAWN", "GMOVE", "GNUDGE", "GNUDGEW", "GROT", "GFACE", "GDEL", "GDUP", "IMAKE", "IDEL" };
        Creature* c = nullptr;
        if (!globalOps.count(op))
        {
            if (U(a, 2)) c = FindSpawn(p, U(a, 2));
            else if (Unit* u = p->GetSelectedUnit()) c = u->ToCreature();
            if (c && !c->GetSpawnId()) c = nullptr;
        }
        MarkBefore(op, a, c);
        HighWater hw = TakeHighWater();
        DispatchOp(p, payload);
        MarkNewSince(hw);
        if ((op == "ENTRY" || op == "UNIQUE") && c && c->IsInWorld())
            MarkType(c->GetEntry());
        SendChangeCount(p);
    }

    void DispatchOp(Player* p, std::string const& payload)
    {
        std::vector<std::string> a = Split(payload, '~');
        if (a.size() < 2 || a[0] != "Q")
            return;
        std::string const& op = a[1];

        if (!sConfigMgr->GetOption<bool>("DevMenu.Enable", true))
            return Err(p, "Dev menu is disabled on this server (DevMenu.Enable)");
        if (uint32(p->GetSession()->GetSecurity()) < sConfigMgr->GetOption<uint32>("DevMenu.MinSecurity", SEC_GAMEMASTER))
            return Err(p, "Dev menu needs a GM account");

        if (op == "HELLO") return Send(p, Join("HI", uint32(p->GetSession()->GetSecurity())));
        if (op == "SEARCH") return OpSearch(p, a);
        if (op == "SPAWN") return OpSpawn(p, a);
        if (op == "DUP") return OpDuplicate(p, a);
        if (op == "RENAMET") return OpRenameType(p, a);
        if (op == "NEAR") return OpNear(p, a);
        if (op == "PADD") return OpPathAdd(p);
        if (op == "PUNDO") return OpPathUndo(p);
        if (op == "PCLEAR") return OpPathClear(p);
        if (op == "PCLICK") return OpPathClickMode(p, a);
        if (op == "PADDAT") return OpPathAddAt(p, a);
        if (op == "PPT") return OpPathPoint(p, a);
        if (op == "PLIST") return SendPathList(p, g_state[p->GetGUID().GetCounter()].path);
        if (op == "BUF") { g_buf[p->GetGUID().GetCounter()] += S(a, 2); return; }
        if (op == "BUFC") { g_buf[p->GetGUID().GetCounter()].clear(); return; }
        if (op == "RGET") return OpRGet(p, a);
        if (op == "RSET") return OpRSet(p, a);
        if (op == "RLOAD") return ReloadTables(p);
        if (op == "LGET") return OpLGet(p, a);
        if (op == "LADD") return OpLRow(p, a, true);
        if (op == "LDEL") return OpLRow(p, a, false);
        if (op == "NEWID") return OpNewId(p, a);
        if (op == "QSEARCH") return OpQSearch(p, a);
        if (op == "QNEW") return OpQNew(p, a);
        if (op == "QDEL") return OpQDel(p, a);
        if (op == "QESCORT") return OpQEscort(p, a);
        if (op == "GSEARCH") return OpGSearch(p, a);
        if (op == "ORACES") return OpOutfitRaces(p);
        if (op == "ISEARCH") return OpItemSearch(p, a);
        if (op == "DISGUISE") return OpDisguise(p, a);
        if (op == "UNDISGUISE") { Undisguise(p); return Send(p, Join("DG", 0)); }
        if (op == "OMINE") return OpOutfitMine(p);
        if (op == "OGET") return OpOutfitGet(p, a);
        if (op == "OPREV") return OpOutfitPreview(p, a);
        if (op == "OPREVDEL") return OpPreviewRemove(p);
        if (op == "OSAVE") return OpOutfitSave(p, a);
        if (op == "XCSEARCH") return OpExtCostSearch(p, a);
        if (op == "IPRICE") return OpItemPrice(p, a);
        if (op == "VCUR") return OpVendorCurrency(p, a);
        if (op == "SPSEARCH") return OpSpellSearch(p, a);
        if (op == "GSPAWN") return OpGSpawn(p, a);
        if (op == "GNEAR") return OpGNear(p, a);
        if (op == "IMAKE") return OpItemMake(p, a);
        if (op == "IDEL") return OpItemDelete(p, a);
        if (op == "ILIST") return OpItemList(p);
        if (op == "IGET") return OpItemGet(p, a);
        if (op == "IGIVE") return OpItemGive(p, a);
        if (op == "ME") return OpMe(p, a);
        if (op == "ICONSEARCH") return OpIconSearch(p, a);
        if (op == "REPSEARCH") return OpRepSearch(p, a);
        if (op == "MORSEARCH") return OpMorphSearch(p, a);
        if (op == "MORPH") return OpMorph(p, a);
        if (op == "MORSTEP") return OpMorphStep(p, a);
        if (op == "SRV") return OpServer(p, a);
        if (op == "SRVTELE") return OpTeleSearch(p, a);
        if (op == "SRVEV") return OpEventSearch(p, a);
        if (op == "MESETS") return OpMeSets(p, a);
        static std::set<std::string> const goOps = { "GTGT", "GPICK", "GSEL", "GMOVE", "GNUDGE", "GNUDGEW", "GROT", "GFACE", "GGOTO", "GDEL", "GDUP" };
        if (goOps.count(op)) return GoOps(p, op, a);

        Creature* c = Target(p, a);
        if (!c)
            return;
        if (op == "SEL") return SendInfo(p, c);
        if (op == "TGET") return SendAdvanced(p, c);
        if (op == "TSET") return OpTSet(p, c, a);
        if (op == "CGET") return SendCombat(p, c);
        if (op == "CADD") return OpCombatAdd(p, c, a);
        if (op == "CDEL") return OpCombatDel(p, c, a);
        if (op == "REP") return OpRep(p, c, a);
        if (op == "MOVE") return OpMoveHere(p, c);
        if (op == "NUDGE") return OpNudge(p, c, a);
        if (op == "FACE") return OpFace(p, c);
        if (op == "NUDGEW") return OpNudgeW(p, c, a);
        if (op == "SETO") return OpSetO(p, c, a);
        if (op == "DEL") return OpDelete(p, c);
        if (op == "MOVETYPE") return OpMoveType(p, c, a);
        if (op == "EMOTE") return OpEmote(p, c, a);
        if (op == "PLAY") return OpPlay(p, c, a);
        if (op == "ROLE") return OpRole(p, c, a);
        if (op == "GUARD") return OpGuard(p, c, a);
        if (op == "FACTION") return OpFaction(p, c, a);
        if (op == "RENAME") return OpRename(p, c, a);
        if (op == "LEVEL") return OpLevel(p, c, a);
        if (op == "MODEL") return OpModel(p, c, a);
        if (op == "ENTRY") return OpEntry(p, c, a);
        if (op == "UNIQUE") return OpUnique(p, c);
        if (op == "VENDORADD") return OpVendorAdd(p, c, a);
        if (op == "RESPAWN") return OpRespawn(p, c);
        if (op == "GOTO") return OpGoto(p, c);
        if (op == "PSHOW") return OpPathLoad(p, c, false);
        if (op == "PEDIT") return OpPathLoad(p, c, true);
        if (op == "PSAVE") return OpPathSave(p, c, a);
        if (op == "PDEL") return OpPathDelete(p, c);
        Err(p, "Unknown op " + Clean(op, 20));
    }
}

class CoADevMenuPlayerScript : public PlayerScript
{
public:
    CoADevMenuPlayerScript() : PlayerScript("CoADevMenuPlayerScript", { PLAYERHOOK_ON_BEFORE_SEND_CHAT_MESSAGE, PLAYERHOOK_ON_LOGOUT,
        PLAYERHOOK_ON_SAVE, PLAYERHOOK_ON_BEFORE_LOGOUT, PLAYERHOOK_ON_UPDATE }) { }

    void OnPlayerUpdate(Player* player, uint32 diff) override { HeirloomTick(player, diff); }

    // never let a wardrobe disguise reach the database
    void OnPlayerSave(Player* player) override { if (Undisguise(player)) Send(player, Join("DG", 0)); }
    void OnPlayerBeforeLogout(Player* player) override { Undisguise(player); }

    void OnPlayerBeforeSendChatMessage(Player* player, uint32& type, uint32& lang, std::string& msg) override
    {
        if (!player || type != CHAT_MSG_WHISPER || lang != LANG_ADDON)
            return;
        std::string const pfx = std::string(PREFIX) + "\t";
        if (msg.compare(0, pfx.size(), pfx) != 0)
            return;
        std::string payload = msg.substr(pfx.size());
        if (payload.compare(0, 2, "Q~") != 0)
            return;   // our own replies echoing back
        // chat runs inside the (multi-threaded) map update; edits touch shared stores, so run them on the world thread
        std::lock_guard<std::mutex> lock(g_queueLock);
        g_queue.emplace_back(player->GetGUID(), payload);
    }

    void OnPlayerLogout(Player* player) override
    {
        {
            std::lock_guard<std::mutex> lock(g_heirLock);
            g_heirApplied.erase(player->GetGUID().GetCounter());
            g_heirTimer.erase(player->GetGUID().GetCounter());
        }
        Undisguise(player);
        auto itr = g_state.find(player->GetGUID().GetCounter());
        if (itr == g_state.end())
            return;
        ClearMarkers(player, itr->second);
        g_state.erase(itr);
    }
};

class CoADevMenuServerScript : public ServerScript
{
public:
    CoADevMenuServerScript() : ServerScript("CoADevMenuServerScript", { SERVERHOOK_CAN_PACKET_RECEIVE }) { }

    bool CanPacketReceive(WorldSession* session, WorldPacket const& packet) override
    {
        return !session || (AnswerOutfit(session, packet) && AnswerPathClick(session, packet));
    }
};

class CoADevMenuWorldScript : public WorldScript
{
public:
    CoADevMenuWorldScript() : WorldScript("CoADevMenuWorldScript", { WORLDHOOK_ON_STARTUP, WORLDHOOK_ON_UPDATE }) { }

    void OnStartup() override { LoadOutfits(); LoadHeirlooms(); }

    // between map updates: safe to change templates, reload quests/vendors/gossip, spawn and move things
    void OnUpdate(uint32 /*diff*/) override
    {
        std::vector<std::pair<ObjectGuid, std::string>> work;
        {
            std::lock_guard<std::mutex> lock(g_queueLock);
            work.swap(g_queue);
        }
        for (auto const& [guid, payload] : work)
        {
            Player* player = ObjectAccessor::FindPlayer(guid);
            if (!player || !player->IsInWorld())
                continue;
            try
            {
                Dispatch(player, payload);
            }
            catch (std::exception const& e)
            {
                LOG_ERROR("module", "Dev menu: {} failed: {}", payload, e.what());
                Err(player, "Server error, see worldserver log");
            }
        }
    }
};

void AddSC_ilusixn_devmenu()
{
    new CoADevMenuPlayerScript();
    new CoADevMenuServerScript();
    new CoADevMenuWorldScript();
}
