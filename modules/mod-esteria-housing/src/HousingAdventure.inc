// Combat, training and adventure (Esteria_Housing_Main_Updated.md section 3). Included inside the anonymous namespace of
// mod_esteria_housing.cpp, after HousingCommerce.inc, whose text channel it shares: the addon sends "adv\t..." commands
// through ActionCommerce and gets "training", "portal", "stone", "stoneinvite", "homechoice" and "note" records back
// through SMSG_COMMERCE (Adventure.lua reads them).
//
// Training dummies, portals and meeting stones are decor (catalog rows AdventureDecorBase + kind, tools/make_adventure.py):
// the editor places, moves and stores them. Dummies are creatures (npc_esteria_housing_dummy), the others objects
// (go_esteria_housing_adventure). Teleport: Home and Portal: Home are spells every homeowner knows
// (spell_esteria_housing_home).

    struct DummyConfig
    {
        uint8 level = 80;
        uint32 armor = 0;      // 0: what a creature of its level has
        uint16 resist = 0;     // every school
        uint32 health = 1000000;
        bool killable = false;
        uint16 duration = 0;   // seconds a session runs; 0 until it is stopped (or goes idle)
        uint8 drills = 1;      // boss dummy: 1 interruptible heals, 4 enrage timer
        uint16 enrage = 180;   // seconds
    };

    struct PortalConfig
    {
        uint8 destKind = 0;    // 0 a city (housing_portal_destination), 1 one of the owner's homes
        uint32 dest = 0, destHood = 0;
        uint8 look = 0;        // PortalLookBase + look
        uint8 access = AccessParty;
        std::string name;
    };

    struct Destination { uint32 id = 0; std::string name; uint8 faction = 0, minLevel = 1; WorldLocation loc; };
    struct Stone { uint32 guid = 0; std::string name; uint8 minLevel = 1, expansion = 0; WorldLocation loc; };

    // One player's training: every dummy they hit in one house, until it ends.
    struct Session
    {
        bool active = false;
        uint8 kind = 0;                // the dummy kind that started it (its stats are what the summary leads with)
        uint32 house = 0;
        uint64 start = 0, last = 0;    // ms
        uint16 duration = 0;
        uint64 damage = 0, healing = 0, overheal = 0, taken = 0;
        uint32 kicks = 0, missed = 0, puddles = 0, drops = 0;
        std::set<ObjectGuid> targets;
        std::string result;
    };

    constexpr uint32 AdventureDecorBase = 40100, DummyEntryBase = 9505000, VoidZoneEntry = 9505004;
    constexpr uint32 PortalLookBase = 9506020, MagePortalLook = 3, PortalLooks = 4;
    // the Mage Portal look shows its city (make_adventure.py MAGE_PORTAL_DISPLAY); + 0 is a home's (Dalaran's violet)
    constexpr uint32 MagePortalBase = 9506040, MagePortalDestinations = 13;
    // the boss dummy's drill: Greater Heal on itself, a 3 s interruptible cast that harms no one (only the tank dummy fights)
    constexpr uint32 SpellTeleportHome = 9500100, SpellPortalHome = 9500101, DrillCast = 2060;
    constexpr uint64 IdleEndMs = 15000;

    std::unordered_map<uint64, DummyConfig> s_dummyConfig;   // placed id ->
    std::unordered_map<uint64, PortalConfig> s_portalConfig; // placed id ->
    std::unordered_map<uint64, uint32> s_stoneBind;          // placed id -> world meeting stone guid
    std::unordered_map<uint64, uint8> s_stoneLook;           // placed id -> StoneLookBase + look
    constexpr uint32 StoneLookBase = 9506030, StoneLooks = 4;
    std::vector<Destination> s_destinations;
    std::map<uint32, Stone> s_stones;                         // world meeting stone guid ->
    std::unordered_map<uint32, std::pair<uint32, uint32>> s_homeChoice; // account -> house, neighborhood
    std::unordered_map<ObjectGuid, Session> s_sessions;      // player ->
    std::unordered_map<ObjectGuid, ObjectGuid> s_trainingView; // player -> the dummy whose panel they have open
    std::map<std::pair<uint32, uint8>, uint32> s_best;       // (character, kind) -> best per second
    struct HomePortal { ObjectGuid caster; uint32 account = 0; };
    std::unordered_map<ObjectGuid, HomePortal> s_homePortals; // summoned Portal: Home -> who opened it
    struct Respawn { uint32 instance = 0; uint64 placed = 0; uint32 wait = 0; };
    std::vector<Respawn> s_respawns;                         // defeated dummies, back in a few seconds
    uint32 s_trainingTick = 0;

    uint8 AdventureKindOf(uint32 decorId) { return decorId > AdventureDecorBase && decorId <= AdventureDecorBase + 6 ? uint8(decorId - AdventureDecorBase) : 0; }
    bool IsDummyKind(uint8 kind) { return kind >= AdvDummy && kind <= AdvBoss; }

    std::string Join(std::initializer_list<std::string> fields)
    {
        std::string out;
        for (std::string const& f : fields)
            out += (out.empty() ? "" : "\t") + f;
        return out;
    }
    template <typename T> std::string S(T v) { return std::to_string(v); }

    void SaveAdventure(uint64 placed, std::string const& config)
    {
        CharacterDatabase.Execute("REPLACE INTO housing_adventure (placed_id, config) VALUES ({}, '{}')", placed, config);
    }

    std::string DummyText(DummyConfig const& c)
    {
        return Join({ S(c.level), S(c.armor), S(c.resist), S(c.health), S(int(c.killable)), S(c.duration), S(c.drills), S(c.enrage) });
    }

    std::string PortalText(PortalConfig const& c)
    {
        std::string name = c.name;
        for (char& ch : name) if (ch == '\t' || ch == '\n' || ch == '\'' || ch == '\\') ch = ' ';
        return Join({ S(c.destKind), S(c.dest), S(c.destHood), S(c.look), S(c.access), name });
    }

    void LoadAdventure()
    {
        s_dummyConfig.clear(); s_portalConfig.clear(); s_stoneBind.clear(); s_stoneLook.clear(); s_destinations.clear(); s_stones.clear();
        s_homeChoice.clear(); s_best.clear();
        std::unordered_map<uint64, uint32> decorOf;
        for (auto const& [id, house] : s_houses)
        {
            for (auto const& [pid, p] : house.placed)
                decorOf[pid] = p.decorId;
            for (auto const& [hood, decor] : house.outdoor)
                for (auto const& [pid, p] : decor)
                    decorOf[pid] = p.decorId;
        }
        if (QueryResult r = CharacterDatabase.Query("SELECT placed_id, config FROM housing_adventure"))
            do
            {
                uint64 const placed = r->Fetch()[0].Get<uint64>();
                Fields f = Split(r->Fetch()[1].Get<std::string>());
                auto num = [&](size_t i) { return i < f.size() ? uint32(std::strtoul(f[i].c_str(), nullptr, 10)) : 0u; };
                uint8 const kind = decorOf.count(placed) ? AdventureKindOf(decorOf[placed]) : 0;
                if (IsDummyKind(kind) && f.size() >= 8)
                    s_dummyConfig[placed] = { uint8(num(0)), num(1), uint16(num(2)), num(3), num(4) != 0, uint16(num(5)), uint8(num(6)),
                        uint16(num(7)) };
                else if (kind == AdvPortal && f.size() >= 5)
                    s_portalConfig[placed] = { uint8(num(0)), num(1), num(2), uint8(num(3)), uint8(num(4)), f.size() > 5 ? f[5] : "" };
                else if (kind == AdvStone)
                {
                    s_stoneBind[placed] = num(0);
                    s_stoneLook[placed] = uint8(std::min<uint32>(num(1), StoneLooks - 1));
                }
            } while (r->NextRow());
        if (QueryResult r = CharacterDatabase.Query("SELECT account_id, house_id, neighborhood_id FROM housing_home_choice"))
            do s_homeChoice[r->Fetch()[0].Get<uint32>()] = { r->Fetch()[1].Get<uint32>(), r->Fetch()[2].Get<uint32>() };
            while (r->NextRow());
        if (QueryResult r = CharacterDatabase.Query("SELECT guid, kind, best FROM housing_training_best"))
            do s_best[{ r->Fetch()[0].Get<uint32>(), r->Fetch()[1].Get<uint8>() }] = r->Fetch()[2].Get<uint32>();
            while (r->NextRow());
        if (QueryResult r = WorldDatabase.Query("SELECT id, name, spell_id, faction, min_level FROM housing_portal_destination ORDER BY id"))
            do
            {
                Field* f = r->Fetch();
                SpellTargetPosition const* at = sSpellMgr->GetSpellTargetPosition(f[2].Get<uint32>(), EFFECT_0);
                if (!at)
                    continue;
                s_destinations.push_back({ f[0].Get<uint32>(), f[1].Get<std::string>(), f[3].Get<uint8>(), f[4].Get<uint8>(),
                    WorldLocation(at->target_mapId, at->target_X, at->target_Y, at->target_Z, at->target_Orientation) });
            } while (r->NextRow());
        // Meeting stones: WotLK's own summoning stones (type 23) beside each dungeon, named for the dungeon's zone.
        std::set<uint32> areas;
        if (QueryResult r = WorldDatabase.Query("SELECT g.guid, t.Data0, t.Data2, g.map, g.position_x, g.position_y, g.position_z, "
            "g.orientation FROM gameobject g JOIN gameobject_template t ON t.entry = g.id WHERE t.type = 23 AND t.Data2 <> 0 ORDER BY g.guid"))
            do
            {
                Field* f = r->Fetch();
                AreaTableEntry const* area = sAreaTableStore.LookupEntry(f[2].Get<uint32>());
                if (!area || !areas.insert(area->ID).second)
                    continue;
                uint32 const map = f[3].Get<uint16>();
                float const o = f[7].Get<float>();
                Stone s;
                s.guid = f[0].Get<uint32>();
                s.name = area->area_name[sWorld->GetDefaultDbcLocale()];
                s.minLevel = uint8(std::max<uint32>(1, f[1].Get<uint32>()));
                s.expansion = map == 530 ? 1 : map == 571 ? 2 : 0;
                // beside the stone, not on it
                s.loc = WorldLocation(map, f[4].Get<float>() + 2.5f * std::cos(o), f[5].Get<float>() + 2.5f * std::sin(o),
                    f[6].Get<float>() + 0.5f, o);
                s_stones[s.guid] = s;
            } while (r->NextRow());
        LOG_INFO("module", "housing: {} portal destinations, {} meeting stone destinations, {} configured training dummies",
            s_destinations.size(), s_stones.size(), s_dummyConfig.size());
    }

    // ---------------------------------------------------------------- where things are

    // The placed decor a spawned object or creature is, and its house; 0 and null when it is none of ours.
    uint64 PlacedOf(WorldObject const* object, House** house = nullptr)
    {
        uint64 placed = 0;
        for (auto const& [id, guid] : s_spawned[object->GetInstanceId()])
            if (guid == object->GetGUID())
                placed = id;
        if (placed && house)
        {
            *house = nullptr;
            for (auto& [hid, h] : s_houses)
                if (FindPlaced(h, placed))
                    *house = &h;
        }
        return placed;
    }

    House* HouseOfPlaced(uint64 placed)
    {
        for (auto& [hid, h] : s_houses)
            if (FindPlaced(h, placed))
                return &h;
        return nullptr;
    }

    // Teleport: Home's destination: the home the account chose, else its first house; on a plot, in front of the door.
    struct HomeTarget { House* house = nullptr; Lot lot{ 0, 0 }; Plot const* plot = nullptr; };
    HomeTarget HomeOf(uint32 account)
    {
        HomeTarget t;
        auto mine = s_accountHouses.find(account);
        if (mine == s_accountHouses.end() || mine->second.empty())
            return t;
        uint32 houseId = mine->second.front(), hoodId = 0;
        if (auto c = s_homeChoice.find(account); c != s_homeChoice.end() && s_houses.count(c->second.first)
            && s_houses[c->second.first].account == account)
            std::tie(houseId, hoodId) = c->second;
        t.house = &s_houses[houseId];
        auto const& lots = s_houseLots[houseId];
        for (Lot const& l : lots)
            if (!t.plot || l.first == hoodId)
            {
                t.lot = l;
                t.plot = PlotOfLot(l);
            }
        return t;
    }

    void GoHome(Player* player, HomeTarget const& t)
    {
        if (t.plot)
            if (Hood const* hood = FindHood(t.lot.first))
                return TravelInto(player, *hood, t.plot->exit[0], t.plot->exit[1], t.plot->exit[2], t.plot->corner[3]);
        if (t.house)
            EnterHouse(player, *t.house);
    }

    // Homeowners know the two home spells; an account with no house does not.
    void SyncHomeSpells(Player* player)
    {
        bool const owner = HouseOfAccount(player->GetSession()->GetAccountId()) != nullptr;
        for (uint32 spell : { SpellTeleportHome, SpellPortalHome })
        {
            if (!sSpellMgr->GetSpellInfo(spell))
                continue;
            if (owner && !player->HasSpell(spell))
                player->learnSpell(spell);
            else if (!owner && player->HasSpell(spell))
                player->removeSpell(spell, SPEC_MASK_ALL, false);
        }
    }

    // ---------------------------------------------------------------- training dummies

    DummyConfig& ConfigOf(uint64 placed) { return s_dummyConfig[placed]; }

    void ApplyDummy(Creature* c, DummyConfig const& cfg)
    {
        c->SetLevel(std::clamp<uint8>(cfg.level, 1, 83));
        c->SetCreateHealth(cfg.health);
        c->SetMaxHealth(std::max<uint32>(cfg.health, 1));
        c->SetFullHealth();
        if (cfg.armor)
        {
            c->SetStatFlatModifier(UNIT_MOD_ARMOR, BASE_VALUE, float(cfg.armor));
            c->SetArmor(int32(cfg.armor));
        }
        for (uint8 school = SPELL_SCHOOL_HOLY; school < MAX_SPELL_SCHOOL; ++school)
            c->SetResistance(SpellSchools(school), int32(cfg.resist));
        c->SetControlled(true, UNIT_STATE_ROOT);
    }

    void SpawnDummy(Map* map, Placed const& p)
    {
        uint8 const kind = AdventureKindOf(p.decorId);
        if (Creature* c = map->SummonCreature(DummyEntryBase + kind - 1, Position(p.pos[0], p.pos[1], p.pos[2], p.yaw)))
        {
            c->SetObjectScale(p.scale);
            ApplyDummy(c, ConfigOf(p.id));
            s_spawned[map->GetInstanceId()][p.id] = c->GetGUID();
        }
    }

    uint32 StoneLookEntry(uint64 placed)
    {
        auto it = s_stoneLook.find(placed);
        return StoneLookBase + (it == s_stoneLook.end() ? 0 : it->second);
    }

    uint32 PortalLookEntry(uint64 placed)
    {
        auto it = s_portalConfig.find(placed);
        if (it == s_portalConfig.end())
            return PortalLookBase;
        PortalConfig const& c = it->second;
        if (c.look == MagePortalLook)
            return MagePortalBase + (c.destKind == 0 && c.dest <= MagePortalDestinations ? c.dest : 0);
        return PortalLookBase + std::min<uint32>(c.look, PortalLooks - 1);
    }

    void AdventureRemoved(uint64 placed, CharacterDatabaseTransaction trans)
    {
        if (s_dummyConfig.erase(placed) | s_portalConfig.erase(placed) | s_stoneBind.erase(placed) | s_stoneLook.erase(placed))
            trans->Append("DELETE FROM housing_adventure WHERE placed_id = {}", placed);
    }

    void SendTraining(Player* player, Creature* dummy)
    {
        uint64 const placed = PlacedOf(dummy);
        House* house = HouseOfPlaced(placed);
        if (!placed || !house)
            return;
        uint8 const kind = uint8(dummy->GetEntry() - DummyEntryBase + 1);
        DummyConfig const& c = ConfigOf(placed);
        Session const& s = s_sessions[player->GetGUID()];
        uint64 const now = GameTime::GetGameTimeMS().count();
        uint64 const ms = s.start ? std::max<uint64>(1000, (s.active ? now : s.last) - s.start) : 0;
        double const secs = ms / 1000.0;
        auto rate = [&](uint64 v) { return secs > 0 ? S(uint64(v / secs)) : std::string("0"); };
        auto best = s_best.find({ player->GetGUID().GetCounter(), kind });
        std::string text = "training\n" + Join({ "dummy", dummy->GetGUID().ToString(), S(kind), S(int(house->account ==
            player->GetSession()->GetAccountId())), S(placed), dummy->GetName() }) + "\n";
        text += "config\t" + DummyText(c) + "\n";
        text += Join({ "session", S(int(s.active)), S(ms / 1000), S(s.damage), rate(s.damage), S(s.healing), rate(s.healing),
            S(s.overheal), S(s.taken), S(s.kicks), S(s.missed), S(s.puddles), S(s.drops), S(s.targets.size()), S(s.duration),
            s.result }) + "\n";
        text += "best\t" + (best == s_best.end() ? std::string("0") : S(best->second));
        SendCommerce(player, text);
    }

    // The dummy a session's live panel shows, if the player still has it open and in reach.
    void RefreshTraining(Player* player)
    {
        auto view = s_trainingView.find(player->GetGUID());
        if (view == s_trainingView.end())
            return;
        if (Creature* c = player->GetMap()->GetCreature(view->second))
            SendTraining(player, c);
        else
            s_trainingView.erase(view);
    }

    void EndSession(Player* player, std::string const& result)
    {
        Session& s = s_sessions[player->GetGUID()];
        if (!s.active)
            return;
        s.active = false;
        s.result = result;
        uint64 const ms = std::max<uint64>(1000, s.last - s.start);
        uint64 const value = (s.kind == AdvHeal ? s.healing : s.damage) * 1000 / ms;
        uint32& best = s_best[{ player->GetGUID().GetCounter(), s.kind }];
        if (value > best && ms >= 10000) // a personal best needs at least ten seconds
        {
            best = uint32(value);
            CharacterDatabase.Execute("REPLACE INTO housing_training_best (guid, kind, best, at) VALUES ({}, {}, {}, {})",
                player->GetGUID().GetCounter(), s.kind, best, uint32(GameTime::GetGameTime().count()));
            s.result += " New personal best!";
        }
        RefreshTraining(player);
    }

    Session& Touch(Player* player, Creature* dummy)
    {
        Session& s = s_sessions[player->GetGUID()];
        uint64 const now = GameTime::GetGameTimeMS().count();
        if (!s.active)
        {
            uint64 const placed = PlacedOf(dummy);
            House const* house = HouseOfPlaced(placed);
            s = Session{};
            s.active = true;
            s.kind = uint8(dummy->GetEntry() - DummyEntryBase + 1);
            s.house = house ? house->id : 0;
            s.start = now;
            s.duration = ConfigOf(placed).duration;
        }
        s.last = now;
        s.targets.insert(dummy->GetGUID());
        return s;
    }

    Player* SessionPlayerOf(Creature* dummy)
    {
        for (auto const& [guid, s] : s_sessions)
            if (s.active && s.targets.count(dummy->GetGUID()))
                if (Player* p = ObjectAccessor::GetPlayer(*dummy, guid))
                    return p;
        return nullptr;
    }

    struct DummyAI : public ScriptedAI
    {
        explicit DummyAI(Creature* c) : ScriptedAI(c)
        {
            me->SetReactState(REACT_PASSIVE);
            me->SetCombatMovement(false);
        }

        uint8 Kind() const { return uint8(me->GetEntry() - DummyEntryBase + 1); }
        uint32 m_heal = 0, m_drill = 0, m_idle = 0;
        bool m_casting = false, m_castDone = false;
        std::vector<ObjectGuid> m_zones;

        void DamageTaken(Unit* attacker, uint32& damage, DamageEffectType, SpellSchoolMask) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            Player* p = attacker ? attacker->GetCharmerOrOwnerPlayerOrPlayerItself() : nullptr;
            uint64 const placed = PlacedOf(me);
            bool const killable = placed && ConfigOf(placed).killable;
            if (p)
            {
                Session& s = Touch(p, me);
                s.damage += std::min<uint32>(damage, me->GetHealth());
                if (damage >= me->GetHealth() && killable)
                {
                    s.last = GameTime::GetGameTimeMS().count();
                    EndSession(p, "Defeated in " + S((s.last - s.start) / 1000) + " s.");
                    s_respawns.push_back({ me->GetInstanceId(), placed, 5000 });
                    return;
                }
            }
            if (!killable && damage >= me->GetHealth())
                damage = me->GetHealth() > 1 ? me->GetHealth() - 1 : 0;
        }

        void HealReceived(Unit* healer, uint32& heal) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            Player* p = healer ? healer->GetCharmerOrOwnerPlayerOrPlayerItself() : nullptr;
            if (!p || Kind() != AdvHeal)
                return;
            Session& s = Touch(p, me);
            uint32 const missing = me->GetMaxHealth() - me->GetHealth();
            s.healing += std::min(heal, missing);
            s.overheal += heal > missing ? heal - missing : 0;
        }

        void OnSpellCast(SpellInfo const* spell) override
        {
            if (spell->Id == DrillCast)
                m_castDone = true;
        }

        void ClearZones()
        {
            for (ObjectGuid const& z : m_zones)
                if (Creature* c = me->GetMap()->GetCreature(z))
                    c->DespawnOrUnsummon();
            m_zones.clear();
        }

        void UpdateAI(uint32 diff) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            Player* p = SessionPlayerOf(me);
            uint8 const kind = Kind();
            if (!p)
            {
                // back to full once nobody trains on it
                if (me->IsInCombat() && (m_idle += diff) > 5000)
                    EnterEvadeMode();
                if (!me->IsInCombat() && !me->IsFullHealth() && kind != AdvHeal)
                    me->SetFullHealth();
                if (kind == AdvHeal && me->GetHealthPct() < 100.0f && !me->IsInCombat())
                    me->SetFullHealth();
                ClearZones();
                m_casting = false;
                return;
            }
            m_idle = 0;
            Session& s = s_sessions[p->GetGUID()];
            uint64 const placed = PlacedOf(me);
            DummyConfig const& cfg = ConfigOf(placed);
            if (kind == AdvHeal && (m_heal += diff) >= 2000) // a steady wound to heal through
            {
                m_heal = 0;
                uint32 const hit = std::max<uint32>(1, me->GetMaxHealth() / 12);
                if (me->GetHealth() <= hit + 1)
                {
                    ++s.drops;
                    me->SetHealth(1);
                }
                else
                    me->ModifyHealth(-int32(hit));
                s.last = GameTime::GetGameTimeMS().count(); // the patient keeps the session going
            }
            if (kind == AdvTank)
            {
                s.last = GameTime::GetGameTimeMS().count();
                if (me->GetVictim() != p)
                {
                    me->SetReactState(REACT_AGGRESSIVE);
                    AttackStart(p);
                }
                DoMeleeAttackIfReady();
            }
            if (kind == AdvBoss)
            {
                // it stands and heals itself, again and again (a cast every 6 s); kicked when the cast stops before it lands
                if ((cfg.drills & 1) && (m_drill += diff) >= 6000 && !me->HasUnitState(UNIT_STATE_CASTING))
                {
                    m_drill = 0;
                    m_casting = true;
                    m_castDone = false;
                    me->CastSpell(me, DrillCast, false);
                }
                else if (m_casting && !me->HasUnitState(UNIT_STATE_CASTING))
                {
                    m_casting = false;
                    if (m_castDone) ++s.missed; else ++s.kicks;
                }
                uint64 const now = GameTime::GetGameTimeMS().count(); // the session idles out like any other once hits stop
                if ((cfg.drills & 4) && cfg.enrage && now - s.start >= uint64(cfg.enrage) * 1000)
                {
                    EndSession(p, "Enraged: the dummy outlasted you.");
                    me->SetFullHealth();
                    EnterEvadeMode();
                }
            }
        }

        void DamageDealt(Unit* victim, uint32& damage, DamageEffectType, SpellSchoolMask) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            if (Kind() != AdvTank) // only the tank dummy hurts anyone
            {
                damage = 0;
                return;
            }
            if (Player* p = victim ? victim->ToPlayer() : nullptr)
                if (auto s = s_sessions.find(p->GetGUID()); s != s_sessions.end() && s->second.active)
                    s->second.taken += damage;
        }

        void EnterEvadeMode(EvadeReason why = EVADE_REASON_OTHER) override
        {
            ClearZones();
            me->SetReactState(REACT_PASSIVE);
            ScriptedAI::EnterEvadeMode(why);
            me->SetControlled(true, UNIT_STATE_ROOT);
        }
    };

    class npc_esteria_housing_dummy : public CreatureScript
    {
    public:
        npc_esteria_housing_dummy() : CreatureScript("npc_esteria_housing_dummy") { }
        CreatureAI* GetAI(Creature* creature) const override { return new DummyAI(creature); }
    };

    // Every second: sessions that ran their length or went idle end, open panels refresh, defeated dummies come back.
    void TrainingTick(uint32 diff)
    {
        for (auto it = s_respawns.begin(); it != s_respawns.end();)
        {
            if (it->wait > diff) { it->wait -= diff; ++it; continue; }
            House* house = HouseOfPlaced(it->placed);
            Placed const* p = house ? FindPlaced(*house, it->placed) : nullptr;
            Map* map = nullptr;
            if (house)
            {
                if (auto inst = s_houseInstance.find(house->id); inst != s_houseInstance.end() && inst->second == it->instance)
                    map = sMapMgr->FindMap(Room(*house) ? Room(*house)->mapId : 0, it->instance);
                if (!map)
                    for (auto const& [hoodId, decor] : house->outdoor)
                        if (decor.count(it->placed))
                            if (Hood const* hood = FindHood(hoodId))
                                map = LiveMap(*hood);
            }
            if (map && p)
            {
                Despawn(map, it->placed);
                Spawn(map, *p);
            }
            it = s_respawns.erase(it);
        }
        if ((s_trainingTick += diff) < 1000)
            return;
        s_trainingTick = 0;
        uint64 const now = GameTime::GetGameTimeMS().count();
        for (auto& [guid, s] : s_sessions)
        {
            Player* p = ObjectAccessor::FindPlayer(guid);
            if (!p)
            {
                s.active = false;
                continue;
            }
            if (s.active && s.duration && now - s.start >= uint64(s.duration) * 1000)
            {
                s.last = s.start + uint64(s.duration) * 1000;
                EndSession(p, "Time is up.");
            }
            else if (s.active && now - s.last >= IdleEndMs)
                EndSession(p, "Ended: no hits for 15 s.");
            else if (s.active)
                RefreshTraining(p);
        }
    }

    // ---------------------------------------------------------------- portals

    std::string DestinationName(PortalConfig const& c)
    {
        if (c.destKind == 1)
        {
            uint16 const plot = PlotNumber(c.dest, c.destHood);
            Hood const* hood = FindHood(c.destHood);
            return plot && hood ? "Plot " + S(plot) + ", " + HoodName(*hood) : "A home";
        }
        for (Destination const& d : s_destinations)
            if (d.id == c.dest)
                return d.name;
        return "";
    }

    void SendPortal(Player* player, uint64 placed, House const& house)
    {
        PortalConfig const& c = s_portalConfig[placed];
        bool const owner = house.account == player->GetSession()->GetAccountId();
        std::string text = "portal\n" + Join({ "portal", S(placed), S(int(owner)), c.name, DestinationName(c), S(c.destKind), S(c.dest),
            S(c.destHood), S(c.look), S(c.access) });
        if (owner)
        {
            for (Destination const& d : s_destinations)
                text += "\n" + Join({ "dest", "0", S(d.id), "0", d.name, S(d.faction), S(d.minLevel) });
            for (uint32 id : s_accountHouses[house.account])
                for (Lot const& l : s_houseLots[id])
                    if (Hood const* hood = FindHood(l.first))
                        text += "\n" + Join({ "dest", "1", S(id), S(l.first), "Plot " + S(l.second + 1) + ", " + HoodName(*hood), "0", "1" });
        }
        SendCommerce(player, text);
    }

    bool MayUsePortal(Player* player, House const& house, PortalConfig const& c)
    {
        uint32 const account = player->GetSession()->GetAccountId();
        if (house.account == account)
            return true;
        House probe = house;
        probe.access = c.access;
        return MayEnter(account, TiesOf(player), probe);
    }

    std::string UsePortal(Player* player, uint64 placed, House const& house)
    {
        auto it = s_portalConfig.find(placed);
        if (it == s_portalConfig.end() || (!it->second.dest))
            return "This portal leads nowhere yet.";
        PortalConfig const& c = it->second;
        if (!MayUsePortal(player, house, c))
            return "The owner has not opened this portal to you.";
        if (std::string const block = TravelBlock(player); !block.empty())
            return block;
        if (c.destKind == 1)
        {
            Plot const* plot = PlotOfLot({ c.destHood, uint8(PlotNumber(c.dest, c.destHood) - 1) });
            Hood const* hood = FindHood(c.destHood);
            if (!plot || !hood || !PlotNumber(c.dest, c.destHood))
                return "That home no longer stands there.";
            if (!MayEnterHood(player, *hood))
                return "You may not go to that neighborhood.";
            TravelInto(player, *hood, plot->exit[0], plot->exit[1], plot->exit[2], plot->corner[3]);
            return "";
        }
        for (Destination const& d : s_destinations)
            if (d.id == c.dest)
            {
                if (d.faction && d.faction != (player->GetTeamId() == TEAM_ALLIANCE ? 1 : 2))
                    return d.name + " is not open to your faction.";
                if (player->GetLevel() < d.minLevel)
                    return d.name + " needs level " + S(d.minLevel) + ".";
                player->TeleportTo(d.loc);
                return "";
            }
        return "This portal leads nowhere yet.";
    }

    // ---------------------------------------------------------------- meeting stones

    void SendStone(Player* player, uint64 placed, House const& house)
    {
        bool const owner = house.account == player->GetSession()->GetAccountId();
        auto bind = s_stoneBind.find(placed);
        Stone const* s = bind == s_stoneBind.end() || !s_stones.count(bind->second) ? nullptr : &s_stones[bind->second];
        std::string text = "stone\n" + Join({ "stone", S(placed), S(int(owner)), s ? s->name : "", S(s ? s->minLevel : 0),
            S(s ? s->expansion : 0), S(s ? s->guid : 0), S(int(player->GetGroup() != nullptr)),
            S(s_stoneLook.count(placed) ? s_stoneLook[placed] : 0) });
        if (owner)
            for (auto const& [guid, st] : s_stones)
                text += "\n" + Join({ "stoneopt", S(guid), st.name, S(st.minLevel), S(st.expansion) });
        SendCommerce(player, text);
    }

    std::string UseStone(Player* player, uint64 placed)
    {
        auto bind = s_stoneBind.find(placed);
        if (bind == s_stoneBind.end() || !s_stones.count(bind->second))
            return "This stone is not bound to a dungeon yet.";
        Stone const& s = s_stones[bind->second];
        if (player->GetLevel() < s.minLevel)
            return s.name + " needs level " + S(s.minLevel) + ".";
        if (std::string const block = TravelBlock(player); !block.empty())
            return block;
        player->TeleportTo(s.loc);
        return "";
    }

    // ---------------------------------------------------------------- the addon's commands

    void HandleAdventure(Player* player, Fields const& f)
    {
        uint32 const account = player->GetSession()->GetAccountId();
        std::string const& cmd = f.size() > 1 ? f[1] : std::string();
        auto num = [&](size_t i) { return i < f.size() ? std::strtoull(f[i].c_str(), nullptr, 10) : 0ull; };
        auto note = [&](std::string const& text) { if (!text.empty()) SendCommerce(player, "note\t" + text); };
        // a placed thing in the house or neighborhood instance the player stands in
        auto here = [&](uint64 placed) -> House* {
            House* house = HouseOfPlaced(placed);
            return house && s_spawned[player->GetInstanceId()].count(placed) ? house : nullptr;
        };
        if (cmd == "dummy" && f.size() > 2)
        {
            ObjectGuid guid;
            std::string const& text = f[2];
            uint64 raw = std::strtoull(text.c_str() + (text.rfind("0x", 0) == 0 ? 2 : 0), nullptr, 16);
            guid.Set(raw);
            Creature* c = player->GetMap()->GetCreature(guid);
            if (!c || c->GetEntry() < DummyEntryBase || c->GetEntry() >= VoidZoneEntry)
                return;
            s_trainingView[player->GetGUID()] = guid;
            SendTraining(player, c);
        }
        else if (cmd == "close")
            s_trainingView.erase(player->GetGUID());
        else if (cmd == "stop" || cmd == "reset")
        {
            if (cmd == "stop")
            {
                Session& s = s_sessions[player->GetGUID()];
                s.last = GameTime::GetGameTimeMS().count();
                EndSession(player, "Stopped.");
            }
            else
                s_sessions.erase(player->GetGUID());
            RefreshTraining(player);
        }
        else if (cmd == "dummyset" && f.size() >= 11)
        {
            uint64 const placed = num(2);
            House* house = here(placed);
            if (!house || house->account != account)
                return note("Only the owner can set up this dummy.");
            DummyConfig& c = ConfigOf(placed);
            c.level = uint8(std::clamp<uint64>(num(3), 1, 83));
            c.armor = uint32(std::min<uint64>(num(4), 100000));
            c.resist = uint16(std::min<uint64>(num(5), 1000));
            c.health = uint32(std::clamp<uint64>(num(6), 100, 2000000000));
            c.killable = num(7) != 0;
            c.duration = uint16(std::min<uint64>(num(8), 3600));
            c.drills = uint8(num(9) & 7);
            c.enrage = uint16(std::clamp<uint64>(num(10), 10, 3600));
            SaveAdventure(placed, DummyText(c));
            if (Creature* dummy = player->GetMap()->GetCreature(s_spawned[player->GetInstanceId()][placed]))
            {
                ApplyDummy(dummy, c);
                SendTraining(player, dummy);
            }
        }
        else if (cmd == "portalgo" || cmd == "portalset")
        {
            uint64 const placed = num(2);
            House* house = here(placed);
            if (!house)
                return;
            if (cmd == "portalgo")
                return note(UsePortal(player, placed, *house));
            if (house->account != account || f.size() < 9)
                return note("Only the owner can set up this portal.");
            PortalConfig& c = s_portalConfig[placed];
            uint32 const before = PortalLookEntry(placed); // what stands there now
            c.destKind = uint8(num(3) ? 1 : 0);
            c.dest = uint32(num(4));
            c.destHood = uint32(num(5));
            if (c.destKind == 1 && (!s_houses.count(c.dest) || s_houses[c.dest].account != account))
                c.dest = 0;
            uint8 const look = uint8(std::min<uint64>(num(6), PortalLooks - 1));
            c.look = look;
            bool const relook = PortalLookEntry(placed) != before; // a new look, or the Mage Portal's new city
            c.access = uint8(num(7)) & (AccessEveryone | AccessFriends | AccessGuild | AccessParty);
            c.name = f[8].substr(0, 40);
            SaveAdventure(placed, PortalText(c));
            if (relook) // a new look is a new object
                if (Placed const* p = FindPlaced(*house, placed))
                {
                    Despawn(player->GetMap(), placed);
                    Spawn(player->GetMap(), *p);
                }
            SendPortal(player, placed, *house);
        }
        else if (cmd == "stonego" || cmd == "stoneset" || cmd == "stoneparty" || cmd == "stonelook")
        {
            uint64 const placed = num(2);
            House* house = here(placed);
            if (!house)
                return note(cmd == "stonego" ? "You are no longer beside that stone." : "");
            if (cmd == "stonego")
                return note(UseStone(player, placed));
            if (cmd == "stoneset")
            {
                if (house->account != account)
                    return note("Only the owner can bind this stone.");
                s_stoneBind[placed] = uint32(num(3));
                SaveAdventure(placed, Join({ S(s_stoneBind[placed]), S(s_stoneLook[placed]) }));
                return SendStone(player, placed, *house);
            }
            if (cmd == "stonelook")
            {
                if (house->account != account)
                    return note("Only the owner can change this stone.");
                uint8 const look = uint8(std::min<uint64>(num(3), StoneLooks - 1));
                if (look != s_stoneLook[placed])
                {
                    s_stoneLook[placed] = look;
                    SaveAdventure(placed, Join({ S(s_stoneBind[placed]), S(look) }));
                    if (Placed const* p = FindPlaced(*house, placed)) // a new look is a new object
                    {
                        Despawn(player->GetMap(), placed);
                        Spawn(player->GetMap(), *p);
                    }
                }
                return SendStone(player, placed, *house);
            }
            // the party: each member beside it gets a choice, and goes only if they are eligible themselves
            Group* group = player->GetGroup();
            auto bind = s_stoneBind.find(placed);
            if (!group || bind == s_stoneBind.end() || !s_stones.count(bind->second))
                return note("You need a party, and the stone a dungeon.");
            uint32 asked = 0;
            for (GroupReference* ref = group->GetFirstMember(); ref; ref = ref->next())
                if (Player* m = ref->GetSource(); m && m != player && m->GetMap() == player->GetMap())
                {
                    SendCommerce(m, Join({ "stoneinvite", S(placed), s_stones[bind->second].name, player->GetName() }));
                    ++asked;
                }
            note(asked ? "Your party is asked to come along." : "No party member is here with you.");
            note(UseStone(player, placed));
        }
        else if (cmd == "home" && f.size() >= 4)
        {
            uint32 const houseId = uint32(num(2));
            if (!s_houses.count(houseId) || s_houses[houseId].account != account)
                return;
            s_homeChoice[account] = { houseId, uint32(num(3)) };
            CharacterDatabase.Execute("REPLACE INTO housing_home_choice (account_id, house_id, neighborhood_id) VALUES ({}, {}, {})",
                account, houseId, uint32(num(3)));
            SendCommerce(player, Join({ "homechoice", S(houseId), S(num(3)) }));
        }
        else if (cmd == "homeget")
        {
            HomeTarget const t = HomeOf(account);
            SendCommerce(player, Join({ "homechoice", S(t.house ? t.house->id : 0), S(t.plot ? t.lot.first : 0) }));
        }
    }

    // A portal or meeting stone was clicked (and a summoned Portal: Home).
    bool OpenAdventure(Player* player, GameObject* go)
    {
        if (auto portal = s_homePortals.find(go->GetGUID()); portal != s_homePortals.end())
        {
            Player* caster = ObjectAccessor::GetPlayer(*go, portal->second.caster);
            bool const ours = player->GetGUID() == portal->second.caster
                || (caster && player->GetGroup() && player->GetGroup() == caster->GetGroup());
            if (!ours)
            {
                ChatHandler(player->GetSession()).SendNotification("This portal is for its caster's party.");
                return true;
            }
            HomeTarget const t = HomeOf(portal->second.account);
            if (!t.house)
                return true;
            if (std::string const block = TravelBlock(player); !block.empty())
                ChatHandler(player->GetSession()).SendNotification("{}", block);
            else if (!t.plot && !MayEnter(player, *t.house))
                ChatHandler(player->GetSession()).SendNotification("That house is closed to you.");
            else
                GoHome(player, t);
            return true;
        }
        House* house = nullptr;
        uint64 const placed = PlacedOf(go, &house);
        if (!placed || !house || !s_hasUi.count(player->GetSession()->GetAccountId()))
            return false;
        Placed const* p = FindPlaced(*house, placed);
        uint8 const kind = p ? AdventureKindOf(p->decorId) : 0;
        if (kind == AdvPortal)
            SendPortal(player, placed, *house);
        else if (kind == AdvStone)
            SendStone(player, placed, *house);
        else
            return false;
        return true;
    }

    class go_esteria_housing_adventure : public GameObjectScript
    {
    public:
        go_esteria_housing_adventure() : GameObjectScript("go_esteria_housing_adventure") { }
        bool OnGossipHello(Player* player, GameObject* go) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            ClearGossipMenuFor(player);
            if (s_config.enabled && s_loaded && OpenAdventure(player, go))
                return true;
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "This needs the Esteria housing client.", 0, 0);
            SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, go->GetGUID());
            return true;
        }
    };

    // Teleport: Home and Portal: Home: where travel is allowed, with a home to go to.
    class spell_esteria_housing_home : public SpellScript
    {
        PrepareSpellScript(spell_esteria_housing_home);

        SpellCastResult CheckCast()
        {
            Player* player = GetCaster() ? GetCaster()->ToPlayer() : nullptr;
            if (!player)
                return SPELL_FAILED_DONT_REPORT;
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            if (!s_config.enabled || !s_loaded || !HomeOf(player->GetSession()->GetAccountId()).house)
            {
                ChatHandler(player->GetSession()).SendNotification("You have no home to go to.");
                return SPELL_FAILED_DONT_REPORT;
            }
            Map const* map = player->GetMap();
            if (map->IsBattlegroundOrArena() || (map->Instanceable() && !IsHousingMap(map->GetId()) && !IsNeighborhoodMap(map->GetId())))
                return SPELL_FAILED_NOT_HERE;
            return SPELL_CAST_OK;
        }

        void HandleDummy(SpellEffIndex /*effIndex*/)
        {
            Player* player = GetCaster() ? GetCaster()->ToPlayer() : nullptr;
            if (!player)
                return;
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            HomeTarget const t = HomeOf(player->GetSession()->GetAccountId());
            if (!t.house)
                return;
            if (GetSpellInfo()->Id == SpellTeleportHome)
                return GoHome(player, t);
            float const o = player->GetOrientation();
            if (GameObject* go = player->SummonGameObject(MagePortalBase, player->GetPositionX() + 2.5f * std::cos(o),
                player->GetPositionY() + 2.5f * std::sin(o), player->GetPositionZ(), o, 0, 0, 0, 0, 60))
                s_homePortals[go->GetGUID()] = { player->GetGUID(), player->GetSession()->GetAccountId() };
        }

        void Register() override
        {
            OnCheckCast += SpellCheckCastFn(spell_esteria_housing_home::CheckCast);
            OnEffectHit += SpellEffectFn(spell_esteria_housing_home::HandleDummy, EFFECT_0, SPELL_EFFECT_DUMMY);
        }
    };

    // Homeowners learn the home spells when they log in.
    class EsteriaHousingHomeSpells : public PlayerScript
    {
    public:
        EsteriaHousingHomeSpells() : PlayerScript("EsteriaHousingHomeSpells", { PLAYERHOOK_ON_LOGIN }) { }
        void OnPlayerLogin(Player* player) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            if (s_config.enabled && s_loaded)
                SyncHomeSpells(player);
        }
    };
