// Household services and utilities (Esteria_Housing_Main_Updated.md section 5). Included inside the anonymous namespace
// of mod_esteria_housing.cpp, after HousingCollections.inc, whose kinds, displays and windows it extends.
//
// Every service is decor (catalog rows 40217-40264, sql/world/housing_household_world.sql, category 9 Services). The
// NPCs (innkeeper, banker, repair smith, auctioneer, trainers) are figures like the mannequin: a pooled creature with a
// name and a customizable look. The objects (bank vault, mailbox, repair bench, storage chest, crafting stations) keep a
// hidden helper beside them where the core needs one: a banker for the bank's packets, a mailbox for mail's, a spell
// focus for recipes. Players use them through gossip (no addon needed); only a storage chest has a window (Household.lua,
// "storage" records). Every service packet whose first field is the service's guid is checked here (CanPacketReceive),
// so the owner's "who may use this" holds whatever the client sends.

    constexpr uint32 HiddenBankerEntry = 9505020, HiddenMailboxGo = 9506110, FocusGoBase = 9506100;
    constexpr uint32 HouseHearthItem = 9500200, SpellHouseHearth = 9500102;
    constexpr uint8 FlagGuestsBind = 1; // an innkeeper lets visitors bind their House Hearthstone
    // the spell focuses a station can be (SpellFocusObject.dbc), in the order of their hidden objects FocusGoBase + i
    constexpr uint32 FocusIds[] = { 1, 3, 4, 663, 623, 543, 1552 };
    constexpr char const* FocusNames[] = { "an Anvil", "a Forge", "a Cooking Fire", "an Alchemy Lab", "a Black Anvil", "a Black Forge",
        "a Runeforge" };
    struct Profession { uint32 decor, skill; char const* name; };
    constexpr Profession Professions[] = { { 40251, 171, "Alchemy" }, { 40252, 164, "Blacksmithing" }, { 40253, 185, "Cooking" },
        { 40254, 333, "Enchanting" }, { 40255, 202, "Engineering" }, { 40256, 129, "First Aid" }, { 40257, 356, "Fishing" },
        { 40258, 182, "Herbalism" }, { 40259, 773, "Inscription" }, { 40260, 755, "Jewelcrafting" }, { 40261, 165, "Leatherworking" },
        { 40262, 186, "Mining" }, { 40263, 393, "Skinning" }, { 40264, 197, "Tailoring" } };
    constexpr size_t StorageLogKept = 50;

    // gossip actions (sender 1)
    enum HouseholdAction : uint32 { ActUse = 1, ActBind, ActRepair, ActAccess = 10, ActGuests, ActRename, ActRetitle, ActAppearance,
        ActGreeting, ActNoGreeting };

    struct Held { Item* item = nullptr; uint32 depositor = 0, account = 0; };
    struct Storage
    {
        uint32 id = 0, account = 0, decor = 0;
        uint64 placed = 0;                // 0: packed away with its contents, waiting to be placed again
        std::string name = "Storage Chest";
        std::vector<Held> items;
        std::deque<std::string> log;      // newest first
    };
    struct HearthBind { uint32 house = 0; uint64 placed = 0; };

    std::map<uint32, Storage> s_storages;                       // storage id ->
    std::unordered_map<uint64, uint32> s_storageOf;             // placed id -> storage id
    uint32 s_nextStorage = 1;
    std::unordered_map<uint32, HearthBind> s_hearth;            // character guid ->
    std::map<uint32, std::unique_ptr<Trainer::Trainer>> s_trainers; // skill -> every trainer of it, merged
    std::unordered_map<ObjectGuid, uint64> s_householdMenu;     // player -> the service whose gossip they have open

    int FocusIndex(uint32 decor)
    {
        switch (decor)
        {
            case 40230: case 40231: return 0;
            case 40232: case 40233: return 1;
            case 40234: case 40235: return 2;
            case 40236: return 3;
            case 40237: return 4;
            case 40238: return 5;
            case 40239: return 6;
            default: return -1;
        }
    }
    Profession const* ProfessionOf(uint32 decor)
    {
        for (Profession const& p : Professions)
            if (p.decor == decor)
                return &p;
        return nullptr;
    }
    uint32 StorageSlots(uint32 decor) { return decor == 40227 ? 16 : decor == 40228 ? 28 : 40; }

    void HouseholdDefaults(Display& d)
    {
        switch (d.kind)
        {
            case ColInnkeeper: d.label = "Innkeeper"; d.flags = FlagGuestsBind; break;
            case ColBanker: d.label = "Banker"; break;
            case ColRepairNpc: d.label = "Smith"; d.sub = "Repairs"; break;
            case ColAuctioneer: d.label = "Auctioneer"; break;
            case ColTrainer: d.label = "Trainer"; break;
            case ColStorage: d.access = 0; d.access2 = 0; break; // the owner's alone until shared
            default: break;
        }
    }

    // ---------------------------------------------------------------- who may use what

    bool MayUse(Player* player, House const& house, uint8 access)
    {
        uint32 const account = player->GetSession()->GetAccountId();
        if (house.account == account)
            return true;
        if (!access || !MayEnter(player, house))
            return false;
        if (access & AccessEveryone)
            return true;
        Ties const t = TiesOf(player);
        return ((access & AccessParty) && t.party.count(house.account)) || ((access & AccessFriends) && t.friends.count(house.account))
            || ((access & AccessGuild) && t.guild.count(house.account));
    }

    char const* AccessName(uint8 access)
    {
        if (!access) return "only you";
        if (access & AccessEveryone) return "anyone who can come in";
        if (access & AccessFriends) return "your friends";
        if (access & AccessGuild) return "your guild";
        return "your group";
    }

    uint8 NextAccess(uint8 access) // anyone -> friends -> guild -> group -> only you -> anyone
    {
        if (access & AccessEveryone) return AccessFriends;
        if (access & AccessFriends) return AccessGuild;
        if (access & AccessGuild) return AccessParty;
        if (access & AccessParty) return 0;
        return AccessEveryone;
    }

    // ---------------------------------------------------------------- loading

    void LoadTrainers()
    {
        s_trainers.clear();
        std::map<uint32, std::set<uint32>> skillsOf;                 // trainer -> the skills its recipes need
        std::map<uint32, std::vector<Trainer::Spell>> spellsOf;
        if (QueryResult r = WorldDatabase.Query("SELECT s.TrainerId, s.SpellId, s.MoneyCost, s.ReqSkillLine, s.ReqSkillRank, s.ReqAbility1, "
            "s.ReqAbility2, s.ReqAbility3, s.ReqLevel FROM trainer_spell s JOIN trainer t ON t.Id = s.TrainerId WHERE t.Type = 2"))
            do
            {
                Field* f = r->Fetch();
                Trainer::Spell s;
                s.SpellId = f[1].Get<uint32>(); s.MoneyCost = f[2].Get<uint32>(); s.ReqSkillLine = f[3].Get<uint32>();
                s.ReqSkillRank = f[4].Get<uint32>();
                s.ReqAbility = { f[5].Get<uint32>(), f[6].Get<uint32>(), f[7].Get<uint32>() };
                s.ReqLevel = f[8].Get<uint8>();
                uint32 const trainer = f[0].Get<uint32>();
                if (s.ReqSkillLine)
                    skillsOf[trainer].insert(s.ReqSkillLine);
                spellsOf[trainer].push_back(s);
            } while (r->NextRow());
        // a house's trainer teaches what every trainer of one profession does (its ranks and every recipe), each once
        for (Profession const& p : Professions)
        {
            std::map<uint32, Trainer::Spell> merged;
            for (auto const& [trainer, skills] : skillsOf)
                if (skills.size() == 1 && *skills.begin() == p.skill)
                    for (Trainer::Spell const& s : spellsOf[trainer])
                        if (auto it = merged.find(s.SpellId); it == merged.end() || s.MoneyCost < it->second.MoneyCost)
                            merged[s.SpellId] = s;
            std::vector<Trainer::Spell> spells;
            for (auto const& [id, s] : merged)
                spells.push_back(s);
            s_trainers[p.skill] = std::make_unique<Trainer::Trainer>(0, Trainer::Type::Tradeskill, 0,
                std::string("Welcome. What would you learn of ") + p.name + "?", std::move(spells));
        }
    }

    void LoadHousehold()
    {
        for (auto& [id, s] : s_storages)
            for (Held& h : s.items)
                delete h.item;
        s_storages.clear(); s_storageOf.clear(); s_hearth.clear();
        LoadTrainers();
        if (QueryResult r = CharacterDatabase.Query("SELECT storage_id, account_id, decor_id, placed_id, name FROM housing_storage"))
            do
            {
                Field* f = r->Fetch();
                Storage s;
                s.id = f[0].Get<uint32>(); s.account = f[1].Get<uint32>(); s.decor = f[2].Get<uint32>();
                s.placed = f[3].IsNull() ? 0 : f[3].Get<uint64>(); s.name = f[4].Get<std::string>();
                s_nextStorage = std::max(s_nextStorage, s.id + 1);
                if (s.placed && !HouseOfPlaced(s.placed)) // its decor went without telling us: pack it, keep the contents
                {
                    s.placed = 0;
                    CharacterDatabase.Execute("UPDATE housing_storage SET placed_id = NULL WHERE storage_id = {}", s.id);
                }
                if (s.placed)
                    s_storageOf[s.placed] = s.id;
                s_storages[s.id] = std::move(s);
            } while (r->NextRow());
        // the first eleven columns are the order Item::LoadFromDB reads
        if (QueryResult r = CharacterDatabase.Query("SELECT i.creatorGuid, i.giftCreatorGuid, i.count, i.duration, i.charges, i.flags, "
            "i.enchantments, i.randomPropertyId, i.durability, i.playedTime, i.text, s.item_guid, i.itemEntry, s.storage_id, s.depositor_guid, "
            "s.depositor_account FROM housing_storage_item s JOIN item_instance i ON i.guid = s.item_guid ORDER BY s.slot"))
            do
            {
                Field* f = r->Fetch();
                auto st = s_storages.find(f[13].Get<uint32>());
                ItemTemplate const* proto = sObjectMgr->GetItemTemplate(f[12].Get<uint32>());
                if (st == s_storages.end() || !proto)
                    continue;
                Item* item = NewItemOrBag(proto);
                if (item->LoadFromDB(f[11].Get<uint32>(), ObjectGuid::Empty, f, f[12].Get<uint32>()))
                    st->second.items.push_back({ item, f[14].Get<uint32>(), f[15].Get<uint32>() });
                else
                {
                    LOG_ERROR("module", "housing: storage {} could not load item {}", st->first, f[11].Get<uint32>());
                    delete item;
                }
            } while (r->NextRow());
        if (QueryResult r = CharacterDatabase.Query("SELECT storage_id, line FROM housing_storage_log ORDER BY log_id DESC"))
            do
                if (auto st = s_storages.find(r->Fetch()[0].Get<uint32>()); st != s_storages.end() && st->second.log.size() < StorageLogKept)
                    st->second.log.push_back(r->Fetch()[1].Get<std::string>());
            while (r->NextRow());
        if (QueryResult r = CharacterDatabase.Query("SELECT guid, house_id, placed_id FROM housing_hearth"))
            do s_hearth[r->Fetch()[0].Get<uint32>()] = { r->Fetch()[1].Get<uint32>(), r->Fetch()[2].Get<uint64>() }; while (r->NextRow());
        // the House Hearthstone's cooldown is the realm's (EsteriaHousing.HearthCooldownMinutes)
        if (auto* item = const_cast<ItemTemplate*>(sObjectMgr->GetItemTemplate(HouseHearthItem)))
            item->Spells[0].SpellCooldown = int32(s_config.hearthCooldown * MINUTE * IN_MILLISECONDS);
        LOG_INFO("module", "housing: {} storage chests, {} house hearthstone bindings, {} trainers", s_storages.size(), s_hearth.size(),
            s_trainers.size());
    }

    // ---------------------------------------------------------------- the world

    void SpawnHouseholdExtras(Map* map, Placed const& p, Extras& e)
    {
        uint8 const kind = CollectionKindOf(p.decorId);
        Position const at(p.pos[0], p.pos[1], p.pos[2], p.yaw);
        if (kind == ColBankVault)
        {
            if (Creature* c = map->SummonCreature(HiddenBankerEntry, at))
            {
                Calm(c);
                c->SetNpcFlag(UNIT_NPC_FLAG_BANKER);
                e.units.push_back(c->GetGUID());
                s_extraPlaced[c->GetGUID()] = p.id;
            }
        }
        else if (kind == ColMailbox || kind == ColStation)
        {
            int const focus = FocusIndex(p.decorId);
            uint32 const entry = kind == ColMailbox ? HiddenMailboxGo : focus >= 0 ? FocusGoBase + uint32(focus) : 0;
            if (GameObject* go = entry ? SpawnExtraGo(map, entry, at, 1.0f) : nullptr)
            {
                go->SetSpawnedByDefault(true); // GameObjectFocusCheck only counts a spawned focus
                e.objects.push_back(go->GetGUID());
            }
        }
    }

    // A service NPC as it stands: the flags that give it its client icon and let the core's handlers talk to it.
    void ApplyFigure(Creature* c, Display const& d, uint32 decorId)
    {
        switch (d.kind)
        {
            case ColInnkeeper: c->SetNpcFlag(UNIT_NPC_FLAG_INNKEEPER); break;
            case ColBanker: c->SetNpcFlag(UNIT_NPC_FLAG_BANKER); break;
            case ColAuctioneer: c->SetNpcFlag(UNIT_NPC_FLAG_AUCTIONEER); break;
            case ColTrainer: if (ProfessionOf(decorId)) c->SetNpcFlag(NPCFlags(UNIT_NPC_FLAG_TRAINER | UNIT_NPC_FLAG_TRAINER_PROFESSION)); break;
            default: break;
        }
    }

    // A new figure's name: a trainer says what it teaches.
    void NameFigure(Display& d, uint32 decorId)
    {
        if (Profession const* p = ProfessionOf(decorId))
        {
            d.label = std::string(p->name) + " Trainer";
            d.sub = "Grand Master";
        }
    }

    ObjectGuid HelperOf(uint64 placed, bool unit)
    {
        auto it = s_extras.find(placed);
        if (it == s_extras.end())
            return ObjectGuid::Empty;
        auto const& list = unit ? it->second.units : it->second.objects;
        return list.empty() ? ObjectGuid::Empty : list.front();
    }

    // ---------------------------------------------------------------- repairs

    // What the player's gear would cost to repair at an ordinary smith (Player::DurabilityRepair's sum, before discounts).
    uint32 RepairCost(Player* player)
    {
        uint64 total = 0;
        auto cost = [&](Item* item) {
            if (!item)
                return;
            uint32 const max = item->GetUInt32Value(ITEM_FIELD_MAXDURABILITY), cur = item->GetUInt32Value(ITEM_FIELD_DURABILITY);
            if (!max || cur >= max)
                return;
            ItemTemplate const* t = item->GetTemplate();
            DurabilityCostsEntry const* dcost = sDurabilityCostsStore.LookupEntry(t->ItemLevel);
            DurabilityQualityEntry const* dq = sDurabilityQualityStore.LookupEntry((t->Quality + 1) * 2);
            if (!dcost || !dq)
                return;
            uint32 const c = uint32((max - cur) * dcost->multiplier[ItemSubClassToDurabilityMultiplierId(t->Class, t->SubClass)]
                * double(dq->quality_mod) * sWorld->getRate(RATE_REPAIRCOST));
            total += std::max<uint32>(c, 1);
        };
        for (uint8 i = EQUIPMENT_SLOT_START; i < INVENTORY_SLOT_ITEM_END; ++i)
            cost(player->GetItemByPos(INVENTORY_SLOT_BAG_0, i));
        for (uint8 bag = INVENTORY_SLOT_BAG_START; bag < INVENTORY_SLOT_BAG_END; ++bag)
            for (uint8 i = 0; i < MAX_BAG_SIZE; ++i)
                cost(player->GetItemByPos(bag, i));
        return uint32(std::min<uint64>(total, UINT32_MAX));
    }

    std::string Money(uint32 copper)
    {
        std::string out;
        if (copper >= 10000) out += S(copper / 10000) + "g ";
        if (copper >= 100) out += S(copper / 100 % 100) + "s ";
        return out + S(copper % 100) + "c";
    }

    // ---------------------------------------------------------------- the house hearthstone

    void Bind(ViewCtx const& v)
    {
        Player* player = v.player;
        if (!v.owner && (!(v.d->flags & FlagGuestsBind) || !MayUse(player, *v.house, v.d->access)))
            return ChatHandler(player->GetSession()).SendNotification("The owner does not let guests bind here.");
        uint32 const guid = player->GetGUID().GetCounter();
        s_hearth[guid] = { v.house->id, v.placed };
        CharacterDatabase.Execute("REPLACE INTO housing_hearth (guid, house_id, placed_id, bound_at) VALUES ({}, {}, {}, {})", guid,
            v.house->id, v.placed, uint32(GameTime::GetGameTime().count()));
        if (!player->HasItemCount(HouseHearthItem, 1, true))
            player->AddItem(HouseHearthItem, 1);
        ChatHandler(player->GetSession()).PSendSysMessage("Your House Hearthstone now leads to {}'s house.", v.house->owner);
    }

    // Where a House Hearthstone goes: the innkeeper it was bound at, wherever it now stands, while the binding still holds;
    // else the house's door (its owner), else the character's ordinary hearth.
    void GoHearth(Player* player)
    {
        ChatHandler chat(player->GetSession());
        auto bind = s_hearth.find(player->GetGUID().GetCounter());
        if (bind == s_hearth.end())
            return chat.SendNotification("Your House Hearthstone is not bound. Speak to an innkeeper in a house.");
        House* house = s_houses.count(bind->second.house) ? &s_houses[bind->second.house] : nullptr;
        bool const owner = house && house->account == player->GetSession()->GetAccountId();
        Placed const* p = house ? FindPlaced(*house, bind->second.placed) : nullptr;
        auto d = s_displays.find(bind->second.placed);
        bool const welcome = owner || (house && p && d != s_displays.end() && (d->second.flags & FlagGuestsBind)
            && MayUse(player, *house, d->second.access));
        if (!welcome || (!p && !owner))
        {
            chat.PSendSysMessage("You can no longer return to that house; your hearthstone takes you to your inn instead.");
            player->TeleportTo(player->m_homebindMapId, player->m_homebindX, player->m_homebindY, player->m_homebindZ, player->GetOrientation());
            return;
        }
        if (!p)
        {
            chat.PSendSysMessage("The innkeeper is gone; you arrive at your door.");
            EnterHouse(player, *house);
            return;
        }
        // a step in front of the innkeeper, facing them
        Position const at(p->pos[0] + 1.5f * std::cos(p->yaw), p->pos[1] + 1.5f * std::sin(p->yaw), p->pos[2],
            Position::NormalizeOrientation(p->yaw + float(M_PI)));
        if (house->placed.count(p->id))
        {
            EnterHouse(player, *house, &at);
            return;
        }
        for (auto const& [hoodId, decor] : house->outdoor)
            if (decor.count(p->id))
                if (Hood const* hood = FindHood(hoodId))
                    return TravelInto(player, *hood, at.GetPositionX(), at.GetPositionY(), at.GetPositionZ(), at.GetOrientation());
        EnterHouse(player, *house);
    }

    class spell_esteria_housing_hearth : public SpellScript
    {
        PrepareSpellScript(spell_esteria_housing_hearth);

        SpellCastResult CheckCast()
        {
            Player* player = GetCaster() ? GetCaster()->ToPlayer() : nullptr;
            if (!player)
                return SPELL_FAILED_DONT_REPORT;
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            if (!s_config.enabled || !s_loaded || !s_hearth.count(player->GetGUID().GetCounter()))
            {
                ChatHandler(player->GetSession()).SendNotification("Your House Hearthstone is not bound. Speak to an innkeeper in a house.");
                return SPELL_FAILED_DONT_REPORT;
            }
            if (std::string const why = TravelBlock(player); !why.empty())
            {
                ChatHandler(player->GetSession()).SendNotification("{}", why);
                return SPELL_FAILED_DONT_REPORT;
            }
            return SPELL_CAST_OK;
        }

        void HandleDummy(SpellEffIndex /*effIndex*/)
        {
            if (Player* player = GetCaster() ? GetCaster()->ToPlayer() : nullptr)
            {
                std::lock_guard<std::recursive_mutex> guard(s_lock);
                GoHearth(player);
            }
        }

        void Register() override
        {
            OnCheckCast += SpellCheckCastFn(spell_esteria_housing_hearth::CheckCast);
            OnEffectHit += SpellEffectFn(spell_esteria_housing_hearth::HandleDummy, EFFECT_0, SPELL_EFFECT_DUMMY);
        }
    };

    // ---------------------------------------------------------------- storage chests

    // A chest placed: the oldest chest of the same kind its account packed away comes back with its contents, else a new one.
    void HouseholdPlaced(Placed const& p, uint32 account, CharacterDatabaseTransaction trans)
    {
        if (CollectionKindOf(p.decorId) != ColStorage)
            return;
        Storage* s = nullptr;
        for (auto& [id, st] : s_storages)
            if (!st.placed && st.account == account && st.decor == p.decorId)
            {
                s = &st;
                break;
            }
        if (!s)
        {
            s = &s_storages[s_nextStorage];
            s->id = s_nextStorage++;
            s->account = account;
            s->decor = p.decorId;
        }
        s->placed = p.id;
        s_storageOf[p.id] = s->id;
        trans->Append("REPLACE INTO housing_storage (storage_id, account_id, decor_id, placed_id, name) VALUES ({}, {}, {}, {}, '{}')",
            s->id, s->account, s->decor, p.id, Sql(s->name));
    }

    // A chest picked up or sent back to storage: it keeps its contents, packed away until it is placed again.
    void StorageRemoved(uint64 placed, CharacterDatabaseTransaction trans)
    {
        auto it = s_storageOf.find(placed);
        if (it == s_storageOf.end())
            return;
        s_storages[it->second].placed = 0;
        trans->Append("UPDATE housing_storage SET placed_id = NULL WHERE storage_id = {}", it->second);
        s_storageOf.erase(it);
    }

    Storage* StorageAt(uint64 placed)
    {
        auto it = s_storageOf.find(placed);
        return it == s_storageOf.end() ? nullptr : &s_storages[it->second];
    }

    // Anything but conjured, timed, refundable or still-tradeable loot, and bags with something in them.
    bool Storable(Item const* item)
    {
        return item && !item->IsNotEmptyBag() && !item->m_lootGenerated && !item->IsRefundable() && !item->IsBOPTradable()
            && !item->GetTemplate()->HasFlag(ITEM_FLAG_CONJURED) && !item->GetUInt32Value(ITEM_FIELD_DURATION);
    }

    // Bound goods only go back to whoever could hold them: soulbound to the character, account-bound to the account.
    std::string BoundTo(Held const& h, Player* player)
    {
        if (h.item->IsBoundAccountWide())
            return h.account == player->GetSession()->GetAccountId() ? "" : "Account-bound to its depositor";
        if (h.item->IsSoulBound())
            return h.depositor == player->GetGUID().GetCounter() ? "" : "Soulbound to its depositor";
        return "";
    }

    void LogStorage(Storage& s, Player* player, char const* action, uint32 entry, uint32 count, CharacterDatabaseTransaction trans)
    {
        std::string const line = Join({ S(uint32(GameTime::GetGameTime().count())), player->GetName(), action, S(entry), S(count) });
        s.log.push_front(line);
        if (s.log.size() > StorageLogKept)
            s.log.pop_back();
        trans->Append("INSERT INTO housing_storage_log (storage_id, line) VALUES ({}, '{}')", s.id, Sql(line));
    }

    void SaveHeld(Storage const& s, CharacterDatabaseTransaction trans)
    {
        trans->Append("DELETE FROM housing_storage_item WHERE storage_id = {}", s.id);
        for (size_t i = 0; i < s.items.size(); ++i)
            trans->Append("INSERT INTO housing_storage_item (storage_id, slot, item_guid, depositor_guid, depositor_account) VALUES "
                "({}, {}, {}, {}, {})", s.id, i, s.items[i].item->GetGUID().GetCounter(), s.items[i].depositor, s.items[i].account);
    }

    std::string StoreItem(ViewCtx const& v, Storage& s, uint32 guid)
    {
        Player* player = v.player;
        if (!MayUse(player, *v.house, v.d->access2))
            return "You may not put things in this chest.";
        if (player->GetTradeData())
            return "Finish your trade first.";
        Item* found = nullptr;
        ForEachBagItem(player, [&](Item* item) { if (item->GetGUID().GetCounter() == guid) found = item; });
        if (!Storable(found))
            return "That cannot go in a chest.";
        uint32 const maxStack = found->GetTemplate()->GetMaxStackSize();
        bool const bound = found->IsSoulBound() || found->IsBoundAccountWide();
        Held* merge = nullptr;
        if (maxStack > 1 && !bound)
            for (Held& h : s.items)
                if (h.item->GetEntry() == found->GetEntry() && !h.item->IsSoulBound() && h.item->GetCount() + found->GetCount() <= maxStack)
                    merge = &h;
        if (!merge && s.items.size() >= StorageSlots(s.decor))
            return "This chest is full.";
        uint32 const entry = found->GetEntry(), count = found->GetCount();
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        player->MoveItemFromInventory(found->GetBagSlot(), found->GetSlot(), true);
        found->DeleteFromInventoryDB(trans);
        if (merge)
        {
            merge->item->SetCount(merge->item->GetCount() + count);
            merge->item->FSetState(ITEM_CHANGED);
            merge->item->SaveToDB(trans);
            found->FSetState(ITEM_REMOVED);
            found->SaveToDB(trans);
            delete found;
        }
        else
        {
            found->SetOwnerGUID(ObjectGuid::Empty); // deleting the character must not delete what the chest holds
            if (found->GetState() != ITEM_NEW)
                found->FSetState(ITEM_CHANGED);
            found->SaveToDB(trans);
            s.items.push_back({ found, player->GetGUID().GetCounter(), player->GetSession()->GetAccountId() });
        }
        SaveHeld(s, trans);
        LogStorage(s, player, "put in", entry, count, trans);
        player->SaveInventoryAndGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);
        return "";
    }

    std::string TakeItem(ViewCtx const& v, Storage& s, uint32 guid)
    {
        Player* player = v.player;
        if (!MayUse(player, *v.house, v.d->access))
            return "You may not take things from this chest.";
        auto it = std::find_if(s.items.begin(), s.items.end(), [guid](Held const& h) { return h.item->GetGUID().GetCounter() == guid; });
        if (it == s.items.end())
            return "That is no longer in the chest.";
        if (std::string const why = BoundTo(*it, player); !why.empty())
            return why + ".";
        Item* item = it->item;
        uint32 const entry = item->GetEntry(), count = item->GetCount();
        item->SetOwnerGUID(player->GetGUID());
        ItemPosCountVec dest;
        if (player->CanStoreItem(NULL_BAG, NULL_SLOT, dest, item, false) != EQUIP_ERR_OK)
        {
            item->SetOwnerGUID(ObjectGuid::Empty);
            return "Your bags are full.";
        }
        s.items.erase(it);
        player->MoveItemToInventory(dest, item, true); // may merge into a stack and delete it
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        SaveHeld(s, trans);
        LogStorage(s, player, "took", entry, count, trans);
        player->SaveInventoryAndGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);
        return "";
    }

    void SendStorage(ViewCtx const& v, std::string const& message)
    {
        Storage* s = StorageAt(v.placed);
        if (!s)
            return;
        Player* player = v.player;
        bool const canPut = MayUse(player, *v.house, v.d->access2), canTake = MayUse(player, *v.house, v.d->access);
        std::ostringstream out;
        out << "storage\t" << v.placed << '\t' << s->name << '\t' << s->items.size() << '\t' << StorageSlots(s->decor) << '\t' << int(canPut)
            << '\t' << int(canTake) << '\t' << int(v.owner) << '\t' << int(v.d->access) << '\t' << int(v.d->access2) << '\t' << message << '\n';
        for (Held const& h : s->items)
            out << "S\t" << h.item->GetGUID().GetCounter() << '\t' << h.item->GetEntry() << '\t' << h.item->GetCount() << '\t'
                << ItemLink(h.item, h.item->GetEntry()) << '\t' << BoundTo(h, player) << '\n';
        for (std::string const& line : s->log)
        {
            Fields const f = Split(line);
            ItemTemplate const* t = f.size() > 3 ? sObjectMgr->GetItemTemplate(Num(f, 3)) : nullptr;
            out << "L\t" << line << '\t' << (t ? t->Name1 : "") << '\n';
        }
        if (canPut)
            ForEachBagItem(player, [&](Item* item) {
                if (Storable(item))
                    out << "D\t" << item->GetGUID().GetCounter() << '\t' << item->GetEntry() << '\t' << item->GetCount() << '\t'
                        << ItemLink(item, item->GetEntry()) << '\n';
            });
        SendCommerce(player, out.str());
    }

    // The storage window's commands; false for verbs that are not a household's.
    bool HandleHousehold(ViewCtx& v, std::string const& verb, Fields const& f)
    {
        Storage* s = v.d->kind == ColStorage ? StorageAt(v.placed) : nullptr;
        if (!s)
            return false;
        if (verb == "stput")
            SendStorage(v, StoreItem(v, *s, Num(f, 3)));
        else if (verb == "sttake")
            SendStorage(v, TakeItem(v, *s, Num(f, 3)));
        else if (verb == "stset")
        {
            if (!v.owner)
                return true;
            if (std::string const name = Clean(f.size() > 3 ? f[3] : "", 32); !name.empty())
                s->name = name;
            v.d->access = uint8(Num(f, 4) & (AccessEveryone | AccessFriends | AccessGuild | AccessParty));
            v.d->access2 = uint8(Num(f, 5) & (AccessEveryone | AccessFriends | AccessGuild | AccessParty));
            SaveDisplay(v.placed, *v.d);
            CharacterDatabase.Execute("UPDATE housing_storage SET name = '{}' WHERE storage_id = {}", Sql(s->name), s->id);
            SendStorage(v, "Saved.");
        }
        else
            return false;
        return true;
    }

    // ---------------------------------------------------------------- gossip

    void FigureChanged(ViewCtx const& v)
    {
        if (v.d->kind == ColMannequin)
            SendMannequin(v);
        else
            SendCommerce(v.player, "note\tSaved.");
    }

    bool UseService(ViewCtx const& v, WorldObject* object)
    {
        Player* player = v.player;
        WorldSession* session = player->GetSession();
        Creature* npc = object->ToCreature();
        CloseGossipMenuFor(player);
        switch (v.d->kind)
        {
            case ColBanker:
                session->SendShowBank(object->GetGUID());
                return true;
            case ColBankVault:
                if (ObjectGuid const banker = HelperOf(v.placed, true))
                    session->SendShowBank(banker);
                return true;
            case ColMailbox:
                if (ObjectGuid const box = HelperOf(v.placed, false))
                    session->SendShowMailBox(box);
                return true;
            case ColAuctioneer:
                if (npc)
                {
                    if (!v.d->greeting.empty())
                        SpeakTo(player, object, v.d->greeting);
                    session->SendAuctionHello(npc->GetGUID(), npc);
                }
                return true;
            case ColTrainer:
                if (Profession const* p = npc ? ProfessionOf(v.p->decorId) : nullptr)
                    if (auto t = s_trainers.find(p->skill); t != s_trainers.end())
                        t->second->SendSpells(npc, player, session->GetSessionDbLocaleIndex());
                return true;
            default:
                return false;
        }
    }

    // A service was clicked: visitors get the service itself; the owner, a menu with its settings.
    bool OpenHousehold(ViewCtx& v, WorldObject* object)
    {
        Player* player = v.player;
        Display& d = *v.d;
        uint8 const k = d.kind;
        bool const may = MayUse(player, *v.house, d.access);
        ChatHandler chat(player->GetSession());
        s_householdMenu.erase(player->GetGUID());
        if (k == ColStorage)
        {
            CloseGossipMenuFor(player);
            if (!s_hasUi.count(player->GetSession()->GetAccountId()))
                chat.SendNotification("This chest needs the Esteria housing client.");
            else if (!v.owner && !may && !MayUse(player, *v.house, d.access2))
                chat.SendNotification("This chest is locked to you.");
            else
                SendStorage(v);
            return true;
        }
        if (!v.owner && !may)
        {
            CloseGossipMenuFor(player);
            chat.SendNotification("The owner keeps this for their own household.");
            return true;
        }
        if (!v.owner && UseService(v, object))
            return true;

        ClearGossipMenuFor(player);
        if (k == ColBanker || k == ColBankVault || k == ColMailbox || k == ColAuctioneer || k == ColTrainer)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, k == ColMailbox ? "Check my mail." : k == ColAuctioneer ? "Browse the auctions."
                : k == ColTrainer ? "Train me." : "Open my bank.", 1, ActUse);
        if (k == ColInnkeeper)
        {
            if (v.owner || (d.flags & FlagGuestsBind))
            {
                std::string confirm = "Make this house the home of your House Hearthstone?";
                if (auto old = s_hearth.find(player->GetGUID().GetCounter()); old != s_hearth.end() && s_houses.count(old->second.house))
                    confirm = "Your House Hearthstone now leads to " + s_houses[old->second.house].owner + "'s house. Bind it here instead?";
                AddGossipItemFor(player, GOSSIP_ICON_INTERACT_1, "Make this house your home.", 1, ActBind, confirm, 0, false);
            }
            else
                AddGossipItemFor(player, GOSSIP_ICON_CHAT, "The owner keeps this inn for their own household.", 1, 0);
        }
        if (k == ColRepairNpc || k == ColRepairBench)
        {
            uint32 const normal = RepairCost(player);
            uint32 const final = uint32(normal * (100 - s_config.repairDiscount) / 100);
            if (!normal)
                AddGossipItemFor(player, GOSSIP_ICON_VENDOR, "Nothing you carry needs repair.", 1, 0);
            else
                AddGossipItemFor(player, GOSSIP_ICON_VENDOR, "Repair everything: " + Money(final) + " (normally " + Money(normal) + ", "
                    + S(s_config.repairDiscount) + "% house discount)", 1, ActRepair, "Repair all your gear? Normal cost " + Money(normal)
                    + ", house discount " + Money(normal - final) + ", you pay:", final, false);
        }
        if (k == ColStation)
        {
            int const focus = FocusIndex(v.p->decorId);
            AddGossipItemFor(player, GOSSIP_ICON_TRAINER, std::string("Counts as ") + (focus >= 0 ? FocusNames[focus] : "a workstation")
                + " for recipes that need one.", 1, 0);
        }
        if (v.owner)
        {
            if (k != ColGuildVault)
                AddGossipItemFor(player, GOSSIP_ICON_DOT, std::string("Who may use this: ") + AccessName(d.access), 1, ActAccess);
            if (k == ColInnkeeper)
                AddGossipItemFor(player, GOSSIP_ICON_DOT, std::string("Guests may bind here: ") + ((d.flags & FlagGuestsBind) ? "yes" : "no"),
                    1, ActGuests);
            if (IsFigureKind(k))
            {
                AddGossipItemFor(player, GOSSIP_ICON_TALK, "Change name...", 1, ActRename, "Type a new name.", 0, true);
                AddGossipItemFor(player, GOSSIP_ICON_TALK, "Change title...", 1, ActRetitle, "Type a new title (empty for none).", 0, true);
                if (s_hasUi.count(player->GetSession()->GetAccountId()))
                    AddGossipItemFor(player, GOSSIP_ICON_TABARD, "Change appearance.", 1, ActAppearance);
            }
            if (k == ColAuctioneer)
            {
                AddGossipItemFor(player, GOSSIP_ICON_TALK, d.greeting.empty() ? "Set a greeting..." : "Change the greeting: " + d.greeting, 1,
                    ActGreeting, "What should the auctioneer say to visitors?", 0, true);
                if (!d.greeting.empty())
                    AddGossipItemFor(player, GOSSIP_ICON_TALK, "No greeting.", 1, ActNoGreeting);
            }
        }
        s_householdMenu[player->GetGUID()] = v.placed;
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, object->GetGUID());
        return true;
    }

    void HouseholdSelect(Player* player, WorldObject* object, uint32 /*sender*/, uint32 action, char const* code)
    {
        CloseGossipMenuFor(player);
        auto menu = s_householdMenu.find(player->GetGUID());
        ViewCtx v;
        if (menu == s_householdMenu.end() || !ViewOf(player, menu->second, v) || !object->IsWithinDistInMap(player, INTERACTION_DISTANCE + 5.0f))
            return;
        Display& d = *v.d;
        bool const may = MayUse(player, *v.house, d.access);
        if (action == ActUse && may)
            UseService(v, object);
        else if (action == ActBind && may)
            Bind(v);
        else if (action == ActRepair && may && (d.kind == ColRepairNpc || d.kind == ColRepairBench))
        {
            uint32 const normal = RepairCost(player);
            uint32 const paid = player->DurabilityRepairAll(true, (100 - s_config.repairDiscount) / 100.0f, false);
            if (paid)
                ChatHandler(player->GetSession()).PSendSysMessage("Repaired for {} (you saved {}).", Money(paid),
                    Money(normal > paid ? normal - paid : 0));
            else if (normal)
                ChatHandler(player->GetSession()).SendNotification("You cannot afford the repairs.");
        }
        if (!v.owner || action < ActAccess)
            return;
        std::string const text = code ? Clean(code, 40) : "";
        switch (action)
        {
            case ActAccess: d.access = NextAccess(d.access); break;
            case ActGuests: d.flags ^= FlagGuestsBind; break;
            case ActRename: if (!text.empty()) d.label = text; break;
            case ActRetitle: d.sub = text; break;
            case ActAppearance: return SendMannequinCustomize(v);
            case ActGreeting: d.greeting = code ? Clean(code, 120) : ""; break;
            case ActNoGreeting: d.greeting.clear(); break;
            default: return;
        }
        if (action == ActRename || action == ActRetitle)
            return Redisplay(v); // a new pooled name, spawned again: this object is gone
        SaveDisplay(v.placed, d);
        OpenHousehold(v, object);
    }

    bool npc_esteria_housing_display::OnGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 action)
    {
        std::lock_guard<std::recursive_mutex> guard(s_lock);
        HouseholdSelect(player, creature, sender, action, nullptr);
        return true;
    }

    bool npc_esteria_housing_display::OnGossipSelectCode(Player* player, Creature* creature, uint32 sender, uint32 action, char const* code)
    {
        std::lock_guard<std::recursive_mutex> guard(s_lock);
        HouseholdSelect(player, creature, sender, action, code);
        return true;
    }

    // ---------------------------------------------------------------- the core's own packets

    // The service a packet names by its leading guid, if it is one of ours.
    ViewCtx const* ServiceOf(Player* player, ObjectGuid guid, ViewCtx& v, WorldObject** object)
    {
        Map* map = player->GetMap();
        WorldObject* o = guid.IsGameObject() ? static_cast<WorldObject*>(map->GetGameObject(guid))
            : guid.IsAnyTypeCreature() ? static_cast<WorldObject*>(map->GetCreature(guid)) : nullptr;
        if (!o)
            return nullptr;
        uint64 placed = 0;
        if (auto it = s_extraPlaced.find(guid); it != s_extraPlaced.end())
            placed = it->second;
        else
            placed = PlacedOf(o);
        if (!placed)
            for (auto const& [id, e] : s_extras) // a hidden mailbox or focus
                if (e.instance == player->GetInstanceId() && std::find(e.objects.begin(), e.objects.end(), guid) != e.objects.end())
                    placed = id;
        if (!placed || !ViewOf(player, placed, v) || !IsHouseholdKind(v.d->kind))
            return nullptr;
        *object = o;
        return &v;
    }

    bool LeadingGuidOpcode(uint16 op)
    {
        switch (op)
        {
            case CMSG_SEND_MAIL: case CMSG_GET_MAIL_LIST: case CMSG_MAIL_TAKE_MONEY: case CMSG_MAIL_TAKE_ITEM: case CMSG_MAIL_RETURN_TO_SENDER:
            case CMSG_MAIL_DELETE: case CMSG_MAIL_MARK_AS_READ: case CMSG_MAIL_CREATE_TEXT_ITEM:
            case MSG_AUCTION_HELLO: case CMSG_AUCTION_SELL_ITEM: case CMSG_AUCTION_REMOVE_ITEM: case CMSG_AUCTION_LIST_ITEMS:
            case CMSG_AUCTION_LIST_OWNER_ITEMS: case CMSG_AUCTION_PLACE_BID: case CMSG_AUCTION_LIST_BIDDER_ITEMS:
            case CMSG_AUCTION_LIST_PENDING_SALES:
            case CMSG_BANKER_ACTIVATE: case CMSG_BUY_BANK_SLOT:
            case CMSG_GUILD_BANKER_ACTIVATE: case CMSG_GUILD_BANK_QUERY_TAB: case CMSG_GUILD_BANK_SWAP_ITEMS: case CMSG_GUILD_BANK_BUY_TAB:
            case CMSG_GUILD_BANK_UPDATE_TAB: case CMSG_GUILD_BANK_DEPOSIT_MONEY: case CMSG_GUILD_BANK_WITHDRAW_MONEY:
            case CMSG_TRAINER_LIST: case CMSG_TRAINER_BUY_SPELL:
                return true;
            default:
                return false;
        }
    }

    class EsteriaHousingHousehold : public ServerScript
    {
    public:
        EsteriaHousingHousehold() : ServerScript("EsteriaHousingHousehold", { SERVERHOOK_CAN_PACKET_RECEIVE }) { }

        bool CanPacketReceive(WorldSession* session, WorldPacket const& packet) override
        {
            uint16 const op = packet.GetOpcode();
            if (!LeadingGuidOpcode(op))
                return true;
            Player* player = session ? session->GetPlayer() : nullptr;
            if (!player || !player->IsInWorld() || packet.size() < 8)
                return true;
            if (!IsHousingMap(player->GetMapId()) && !IsNeighborhoodMap(player->GetMapId()))
                return true;
            WorldPacket copy(packet);
            ObjectGuid guid;
            copy >> guid;
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            if (!s_config.enabled || !s_loaded)
                return true;
            ViewCtx v;
            WorldObject* object = nullptr;
            if (!ServiceOf(player, guid, v, &object))
                return true;
            // the guild vault answers to the guild's ranks; everything else here also to the owner's choice
            bool const may = v.d->kind == ColGuildVault ? MayEnter(player, *v.house) : MayUse(player, *v.house, v.d->access);
            if (!may)
            {
                ChatHandler(session).SendNotification("The owner keeps this for their own household.");
                return false;
            }
            // a house's trainer is no creature_default_trainer: list and teach from the merged trainer
            if (op == CMSG_TRAINER_LIST || op == CMSG_TRAINER_BUY_SPELL)
            {
                Creature* npc = object->ToCreature();
                Profession const* p = npc ? ProfessionOf(v.p->decorId) : nullptr;
                auto t = p ? s_trainers.find(p->skill) : s_trainers.end();
                if (t == s_trainers.end() || !npc->IsWithinDistInMap(player, INTERACTION_DISTANCE))
                    return false;
                if (op == CMSG_TRAINER_LIST)
                    t->second->SendSpells(npc, player, session->GetSessionDbLocaleIndex());
                else if (copy.size() >= 12)
                {
                    uint32 spell = 0;
                    copy >> spell;
                    t->second->TeachSpell(npc, player, spell);
                }
                return false;
            }
            return true;
        }
    };

    // Crafting stations: a recipe that needs a focus finds a station's hidden one; the owner's choice decides if it counts.
    class EsteriaHousingHouseholdSpells : public AllSpellScript
    {
    public:
        EsteriaHousingHouseholdSpells() : AllSpellScript("EsteriaHousingHouseholdSpells", { ALLSPELLHOOK_ON_SPELL_CHECK_CAST }) { }

        void OnSpellCheckCast(Spell* spell, bool /*strict*/, SpellCastResult& res) override
        {
            if (res != SPELL_CAST_OK || !spell->GetSpellInfo()->RequiresSpellFocus)
                return;
            Player* player = spell->GetCaster() ? spell->GetCaster()->ToPlayer() : nullptr;
            if (!player || (!IsHousingMap(player->GetMapId()) && !IsNeighborhoodMap(player->GetMapId())))
                return;
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            if (!s_config.enabled || !s_loaded)
                return;
            uint32 const focus = spell->GetSpellInfo()->RequiresSpellFocus;
            bool near = false, allowed = false;
            for (auto const& [placed, e] : s_extras)
            {
                if (e.instance != player->GetInstanceId())
                    continue;
                for (ObjectGuid const& g : e.objects)
                {
                    GameObject* go = player->GetMap()->GetGameObject(g);
                    if (!go || go->GetGOInfo()->type != GAMEOBJECT_TYPE_SPELL_FOCUS || go->GetGOInfo()->spellFocus.focusId != focus
                        || !go->IsWithinDistInMap(player, float(go->GetGOInfo()->spellFocus.dist)))
                        continue;
                    near = true;
                    House* house = HouseOfPlaced(placed);
                    auto d = s_displays.find(placed);
                    if (house && (d == s_displays.end() || MayUse(player, *house, d->second.access)))
                        allowed = true;
                }
            }
            if (near && !allowed)
                res = SPELL_FAILED_REQUIRES_SPELL_FOCUS;
        }
    };
