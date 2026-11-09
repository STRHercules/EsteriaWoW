// Player shops and crafting commissions (Esteria_Housing_Main_Updated.md section 2). Included inside the anonymous namespace
// of mod_esteria_housing.cpp. The addon talks text: CMSG_ACTION ActionCommerce carries one tab-separated command, and
// SMSG_COMMERCE one newline-separated answer (HousingWire.h). Every change of items or gold commits with the player's
// inventory and money in one transaction, the way AuctionHouseHandler does.
//
// Merchants, signs, cases, shelves, racks, counters and commission boards are decor (catalog rows ServiceDecorBase + kind),
// so placing, moving, budget and the chest are the decor editor's. Each placed one except a board is its own shop, keyed by
// placed_id. An account's earnings and ledger are pooled across all its shops.

    using Fields = std::vector<std::string>;

    Fields Split(std::string const& text)
    {
        Fields out(1);
        for (char c : text)
            if (c == '\t') out.emplace_back(); else out.back() += c;
        return out;
    }

    // Text a player typed: it travels inside the tab format and is shown in other players' windows.
    std::string Clean(std::string const& text, size_t max)
    {
        std::string out;
        for (unsigned char c : text)
            if (c >= 32 && c != '|' && c != 127 && out.size() < max)
                out += char(c);
        while (!out.empty() && (uint8(out.back()) & 0xC0) == 0x80) // never leave half a UTF-8 character at the cut
            out.pop_back();
        if (!out.empty() && uint8(out.back()) >= 0xC0)
            out.pop_back();
        return out;
    }

    uint32 Num(Fields const& f, size_t i)
    {
        if (i >= f.size() || f[i].empty() || f[i].size() > 10 || f[i].find_first_not_of("0123456789") != std::string::npos)
            return 0;
        return uint32(std::min<uint64>(std::stoull(f[i]), UINT32_MAX));
    }

    std::string Sql(std::string text)
    {
        CharacterDatabase.EscapeString(text);
        return text;
    }

    constexpr uint32 BoardGo = 9506000;
    constexpr uint32 MerchantEntryFirst = 9501000, MerchantEntryLast = 9504999;
    constexpr size_t MaxListings = 80;
    constexpr float ServiceRange = 15.0f;
    constexpr float ServiceRangeOwner = 80.0f; // the owner places things with the cursor, from across the room
    constexpr uint32 BankDepositPrice = 10000000; // copper: 1000 g, once per account
    constexpr char const* DefaultShopName[] = { "", "Shopkeeper", "", "Shop Sign", "Display Case", "Display Shelf", "Display Rack", "Shop Counter" };

    // Equipment a merchant wears: the server holds the real item, keyed by its character slot number.
    constexpr uint8 GearMainHand = 15, GearOffHand = 16, GearRanged = 17, GearNone = 255;
    // SMSG_MIRRORIMAGE_DATA's armor slots, in the order the packet carries them.
    constexpr uint8 MirrorSlots[] = { 0, 2, 3, 4, 5, 6, 7, 8, 9, 14, 18 };

    uint8 GearSlotOf(ItemTemplate const* p)
    {
        switch (p->InventoryType)
        {
            case INVTYPE_HEAD: return 0;
            case INVTYPE_SHOULDERS: return 2;
            case INVTYPE_BODY: return 3;
            case INVTYPE_CHEST: case INVTYPE_ROBE: return 4;
            case INVTYPE_WAIST: return 5;
            case INVTYPE_LEGS: return 6;
            case INVTYPE_FEET: return 7;
            case INVTYPE_WRISTS: return 8;
            case INVTYPE_HANDS: return 9;
            case INVTYPE_CLOAK: return 14;
            case INVTYPE_TABARD: return 18;
            case INVTYPE_WEAPON: case INVTYPE_WEAPONMAINHAND: case INVTYPE_2HWEAPON: return GearMainHand;
            case INVTYPE_SHIELD: case INVTYPE_WEAPONOFFHAND: case INVTYPE_HOLDABLE: return GearOffHand;
            case INVTYPE_RANGED: case INVTYPE_RANGEDRIGHT: case INVTYPE_THROWN: return GearRanged;
            default: return GearNone;
        }
    }

    struct Gear { Item* item = nullptr; uint32 ownerGuid = 0; };

    struct Listing
    {
        uint32 id = 0, entry = 0, bundle = 1, price = 0;
        uint64 shop = 0;
        bool published = true;
        Item* item = nullptr; // held by the server; null when sold out
        uint32 Stock() const { return item ? item->GetCount() : 0; }
    };
    struct Shop
    {
        uint64 placed = 0;
        uint32 house = 0, account = 0, ownerGuid = 0, entry = 0;
        uint8 kind = 0, race = 1, sex = 0, symbol = 0, border = 0;
        std::string lookHex, bodyHex; // a merchant's saved appearance, as the client sent it
        std::map<uint8, Gear> gear;
        std::string name, theme = "General Goods", greeting = "Welcome! Have a look.", thanks = "Thank you!", farewell = "Safe travels.", sign;
        float labelHeight = 2.4f; // yd above a case's, shelf's, rack's, counter's or sign's base that its name floats
    };
    struct ShopAccount { uint64 treasury = 0; bool bankDeposit = false; };
    struct Recipe
    {
        uint32 spell = 0, item = 0;
        char const* skill = "";
        std::string lowerName;
        std::vector<std::pair<uint32, uint32>> reagents;
    };
    struct Order
    {
        uint32 id = 0, spell = 0, item = 0, quantity = 1, fee = 0, crafter = 0, customer = 0, expires = 0, finished = 0;
        uint8 state = EsteriaHousing::OrderOpen;
        std::vector<std::pair<uint32, uint32>> materials;
    };
    // What the player last opened; every command re-checks that it is still there and close.
    struct View { uint64 shop = 0; ObjectGuid object; };

    std::unordered_map<uint64, Shop> s_shops;
    std::unordered_map<uint32, ShopAccount> s_shopAccounts;
    std::map<uint32, Listing> s_listings;
    std::map<uint32, Order> s_orders;
    std::unordered_map<uint32, Recipe> s_recipes;
    std::unordered_map<ObjectGuid, View> s_shopView, s_boardView;
    std::unordered_map<ObjectGuid, uint64> s_labelPlaced;                        // a shop's floating label -> the shop
    std::unordered_map<uint64, std::pair<uint32, ObjectGuid>> s_shopLabel;      // shop -> its label's instance and guid
    uint32 s_nextListing = 1, s_nextOrder = 1, s_nextMerchantEntry = MerchantEntryFirst;
    uint32 s_orderSweep = 0;

    void SendCommerce(Player* player, std::string const& text)
    {
        WorldPacket data(SMSG_ESTERIA_HOUSING_COMMERCE, text.size() + 1);
        data << text;
        player->SendDirectMessage(&data);
    }

    void NameTemplate(Shop const& shop)
    {
        // The client shows a creature's name from its entry, so each merchant gets a pooled template of its own.
        auto* t = const_cast<CreatureTemplate*>(sObjectMgr->GetCreatureTemplate(shop.entry));
        if (!t)
        {
            LOG_ERROR("module", "housing: merchant template {} is missing (housing_commerce_world.sql)", shop.entry);
            return;
        }
        t->Name = shop.name;
        t->SubName = shop.theme;
        for (CreatureModel& m : t->Models) // a merchant at full size; any other shop's entry is its floating label, a speck
            m.DisplayScale = shop.kind == ServiceMerchant ? 1.0f : 0.01f;
        t->InitializeQueryData();
    }

    // shortcut: a rename takes the next pooled entry because clients cache names by entry; the 4000-entry pool wraps, so
    // a client could show a stale name after 4000 renames. Clear WDB or widen the pool if that ever happens.
    uint32 NextMerchantEntry()
    {
        for (uint32 tries = 0; tries <= MerchantEntryLast - MerchantEntryFirst; ++tries)
        {
            uint32 const entry = s_nextMerchantEntry;
            s_nextMerchantEntry = entry == MerchantEntryLast ? MerchantEntryFirst : entry + 1;
            CharacterDatabase.Execute("REPLACE INTO housing_counter (name, value) VALUES ('merchant_entry', {})", s_nextMerchantEntry);
            if (std::none_of(s_shops.begin(), s_shops.end(), [entry](auto const& s) { return s.second.entry == entry; }))
                return entry;
        }
        return 0;
    }

    void SaveShop(Shop const& s, CharacterDatabaseTransaction trans)
    {
        trans->Append("REPLACE INTO housing_shop (placed_id, house_id, account_id, owner_guid, kind, creature_entry, race, sex, look_hex, body_hex, "
            "symbol, border, name, theme, greeting, thanks, farewell, sign, label_height) VALUES ({}, {}, {}, {}, {}, {}, {}, {}, '{}', '{}', {}, {}, "
            "'{}', '{}', '{}', '{}', '{}', '{}', {})",
            s.placed, s.house, s.account, s.ownerGuid, s.kind, s.entry, s.race, s.sex, Sql(s.lookHex), Sql(s.bodyHex), s.symbol, s.border, Sql(s.name),
            Sql(s.theme), Sql(s.greeting), Sql(s.thanks), Sql(s.farewell), Sql(s.sign), s.labelHeight);
    }

    void SaveShopAccount(uint32 account, CharacterDatabaseTransaction trans)
    {
        ShopAccount const& a = s_shopAccounts[account];
        trans->Append("REPLACE INTO housing_shop_account (account_id, treasury, bank_deposit) VALUES ({}, {}, {})", account, a.treasury,
            uint8(a.bankDeposit));
    }

    void SaveListing(Listing const& l, CharacterDatabaseTransaction trans)
    {
        trans->Append("REPLACE INTO housing_shop_listing (listing_id, placed_id, item_entry, item_guid, bundle, price, published) "
            "VALUES ({}, {}, {}, {}, {}, {}, {})", l.id, l.shop, l.entry, l.item ? l.item->GetGUID().GetCounter() : 0, l.bundle, l.price,
            uint8(l.published));
    }

    void SaveOrder(Order const& o, CharacterDatabaseTransaction trans)
    {
        std::string materials;
        for (auto const& [item, count] : o.materials)
            materials += std::to_string(item) + ":" + std::to_string(count) + ",";
        trans->Append("REPLACE INTO housing_commission (order_id, customer_guid, crafter_guid, spell_id, item_entry, quantity, fee, "
            "state, materials, expires_at, finished_at) VALUES ({}, {}, {}, {}, {}, {}, {}, {}, '{}', {}, {})", o.id, o.customer, o.crafter,
            o.spell, o.item, o.quantity, o.fee, o.state, materials, o.expires, o.finished);
    }

    char const* SkillName(uint32 skill)
    {
        switch (skill)
        {
            case SKILL_BLACKSMITHING: return "Blacksmithing";
            case SKILL_TAILORING: return "Tailoring";
            case SKILL_LEATHERWORKING: return "Leatherworking";
            case SKILL_ALCHEMY: return "Alchemy";
            case SKILL_ENGINEERING: return "Engineering";
            case SKILL_JEWELCRAFTING: return "Jewelcrafting";
            case SKILL_ENCHANTING: return "Enchanting";
            default: return nullptr;
        }
    }

    constexpr uint32 ArmorVellumIII = 43145, WeaponVellumIII = 43146;

    void LoadRecipes()
    {
        s_recipes.clear();
        for (uint32 i = 0; i < sSkillLineAbilityStore.GetNumRows(); ++i)
        {
            SkillLineAbilityEntry const* ability = sSkillLineAbilityStore.LookupEntry(i);
            char const* skill = ability ? SkillName(ability->SkillLine) : nullptr;
            SpellInfo const* spell = skill ? sSpellMgr->GetSpellInfo(ability->Spell) : nullptr;
            // shortcut: recipes on a cooldown (transmutes and the like) are left out rather than sharing the crafter's timer.
            if (!spell || spell->RecoveryTime || spell->CategoryRecoveryTime)
                continue;
            Recipe r;
            r.spell = spell->Id;
            r.skill = skill;
            bool enchant = false;
            for (uint8 e = 0; e < MAX_SPELL_EFFECTS && !r.item; ++e)
                if (spell->Effects[e].ItemType && (spell->Effects[e].Effect == SPELL_EFFECT_CREATE_ITEM
                    || spell->Effects[e].Effect == SPELL_EFFECT_ENCHANT_ITEM))
                {
                    r.item = spell->Effects[e].ItemType;
                    enchant = spell->Effects[e].Effect == SPELL_EFFECT_ENCHANT_ITEM; // delivered as the scroll a vellum makes
                }
            ItemTemplate const* product = r.item ? sObjectMgr->GetItemTemplate(r.item) : nullptr;
            if (!product)
                continue;
            bool usable = true;
            for (uint8 k = 0; k < MAX_SPELL_REAGENTS; ++k)
                if (spell->Reagent[k] > 0 && spell->ReagentCount[k] > 0)
                {
                    ItemTemplate const* reagent = sObjectMgr->GetItemTemplate(spell->Reagent[k]);
                    // a bound reagent would come back unbound if the order were cancelled
                    usable = usable && reagent && reagent->Bonding != BIND_WHEN_PICKED_UP && reagent->Bonding != BIND_QUEST_ITEM;
                    r.reagents.push_back({ uint32(spell->Reagent[k]), spell->ReagentCount[k] });
                }
            if (!usable)
                continue;
            if (enchant) // shortcut: always the top vellum, which every enchant accepts; cheaper tiers are not offered.
                r.reagents.push_back({ spell->EquippedItemClass == ITEM_CLASS_WEAPON ? WeaponVellumIII : ArmorVellumIII, 1 });
            r.lowerName = product->Name1;
            std::transform(r.lowerName.begin(), r.lowerName.end(), r.lowerName.begin(), ::tolower);
            s_recipes[r.spell] = std::move(r);
        }
    }

    std::vector<std::pair<uint32, uint32>> ParseMaterials(std::string const& text)
    {
        std::vector<std::pair<uint32, uint32>> out;
        std::istringstream in(text);
        for (std::string part; std::getline(in, part, ',');)
            if (auto colon = part.find(':'); colon != std::string::npos)
                out.push_back({ uint32(std::stoul(part.substr(0, colon))), uint32(std::stoul(part.substr(colon + 1))) });
        return out;
    }

    void LoadCommerce()
    {
        for (auto& [id, l] : s_listings)
            delete l.item;
        for (auto& [id, shop] : s_shops)
            for (auto& [slot, gear] : shop.gear)
                delete gear.item;
        s_shops.clear(); s_shopAccounts.clear(); s_listings.clear(); s_orders.clear();
        LoadRecipes();
        if (QueryResult r = CharacterDatabase.Query("SELECT placed_id, house_id, account_id, owner_guid, kind, creature_entry, race, symbol, border, "
            "name, theme, greeting, thanks, farewell, sign, sex, look_hex, body_hex, label_height FROM housing_shop"))
            do
            {
                Field* f = r->Fetch();
                Shop s;
                s.placed = f[0].Get<uint64>(); s.house = f[1].Get<uint32>(); s.account = f[2].Get<uint32>(); s.ownerGuid = f[3].Get<uint32>();
                s.kind = f[4].Get<uint8>(); s.entry = f[5].Get<uint32>(); s.race = f[6].Get<uint8>();
                s.symbol = f[7].Get<uint8>(); s.border = f[8].Get<uint8>(); s.name = f[9].Get<std::string>(); s.theme = f[10].Get<std::string>();
                s.greeting = f[11].Get<std::string>(); s.thanks = f[12].Get<std::string>(); s.farewell = f[13].Get<std::string>();
                s.sign = f[14].Get<std::string>();
                s.sex = f[15].Get<uint8>(); s.lookHex = f[16].Get<std::string>(); s.bodyHex = f[17].Get<std::string>();
                s.labelHeight = f[18].Get<float>();
                if (s.entry)
                {
                    s_nextMerchantEntry = std::max(s_nextMerchantEntry, std::min(s.entry + 1, MerchantEntryLast));
                    NameTemplate(s);
                }
                s_shops[s.placed] = std::move(s);
            } while (r->NextRow());
        // where the pool left off: a restart must not hand out an entry clients already cached under an older name
        if (QueryResult r = CharacterDatabase.Query("SELECT value FROM housing_counter WHERE name = 'merchant_entry'"))
            s_nextMerchantEntry = std::clamp(r->Fetch()[0].Get<uint32>(), MerchantEntryFirst, MerchantEntryLast);
        // shops placed before every shop was named get their entry now
        for (auto& [placed, s] : s_shops)
            if (!s.entry && (s.entry = NextMerchantEntry()))
            {
                NameTemplate(s);
                CharacterDatabase.Execute("UPDATE housing_shop SET creature_entry = {} WHERE placed_id = {}", s.entry, placed);
            }
        if (QueryResult r = CharacterDatabase.Query("SELECT account_id, treasury, bank_deposit FROM housing_shop_account"))
            do
                s_shopAccounts[r->Fetch()[0].Get<uint32>()] = { r->Fetch()[1].Get<uint64>(), r->Fetch()[2].Get<uint8>() != 0 };
            while (r->NextRow());
        // The first eleven columns are the order Item::LoadFromDB reads.
        if (QueryResult r = CharacterDatabase.Query("SELECT i.creatorGuid, i.giftCreatorGuid, i.count, i.duration, i.charges, i.flags, "
            "i.enchantments, i.randomPropertyId, i.durability, i.playedTime, i.text, l.item_guid, l.item_entry, l.listing_id, l.placed_id, "
            "l.bundle, l.price, l.published FROM housing_shop_listing l LEFT JOIN item_instance i ON i.guid = l.item_guid"))
            do
            {
                Field* f = r->Fetch();
                Listing l;
                l.entry = f[12].Get<uint32>(); l.id = f[13].Get<uint32>(); l.shop = f[14].Get<uint64>(); l.bundle = f[15].Get<uint32>();
                l.price = f[16].Get<uint32>(); l.published = f[17].Get<uint8>();
                s_nextListing = std::max(s_nextListing, l.id + 1);
                if (uint32 const guid = f[11].Get<uint32>())
                    if (ItemTemplate const* proto = sObjectMgr->GetItemTemplate(l.entry))
                    {
                        Item* item = NewItemOrBag(proto);
                        if (item->LoadFromDB(guid, ObjectGuid::Empty, f, l.entry))
                            l.item = item;
                        else
                        {
                            LOG_ERROR("module", "housing: listing {} could not load item {}", l.id, guid);
                            delete item;
                        }
                    }
                s_listings[l.id] = l;
            } while (r->NextRow());
        if (QueryResult r = CharacterDatabase.Query("SELECT i.creatorGuid, i.giftCreatorGuid, i.count, i.duration, i.charges, i.flags, "
            "i.enchantments, i.randomPropertyId, i.durability, i.playedTime, i.text, g.item_guid, i.itemEntry, g.placed_id, g.slot, g.owner_guid "
            "FROM housing_shop_gear g JOIN item_instance i ON i.guid = g.item_guid"))
            do
            {
                Field* f = r->Fetch();
                auto shop = s_shops.find(f[13].Get<uint64>());
                ItemTemplate const* proto = sObjectMgr->GetItemTemplate(f[12].Get<uint32>());
                if (shop == s_shops.end() || !proto)
                    continue;
                Item* item = NewItemOrBag(proto);
                if (item->LoadFromDB(f[11].Get<uint32>(), ObjectGuid::Empty, f, f[12].Get<uint32>()))
                    shop->second.gear[f[14].Get<uint8>()] = { item, f[15].Get<uint32>() };
                else
                    delete item;
            } while (r->NextRow());
        uint32 const recent = uint32(GameTime::GetGameTime().count()) - 3 * DAY;
        if (QueryResult r = CharacterDatabase.Query("SELECT MAX(order_id) FROM housing_commission"))
            s_nextOrder = r->Fetch()[0].Get<uint32>() + 1;
        if (QueryResult r = CharacterDatabase.Query("SELECT order_id, customer_guid, crafter_guid, spell_id, item_entry, quantity, fee, state, "
            "materials, expires_at, finished_at FROM housing_commission WHERE state < 2 OR finished_at > {}", recent))
            do
            {
                Field* f = r->Fetch();
                Order o;
                o.id = f[0].Get<uint32>(); o.customer = f[1].Get<uint32>(); o.crafter = f[2].Get<uint32>(); o.spell = f[3].Get<uint32>();
                o.item = f[4].Get<uint32>(); o.quantity = f[5].Get<uint32>(); o.fee = f[6].Get<uint32>(); o.state = f[7].Get<uint8>();
                o.materials = ParseMaterials(f[8].Get<std::string>()); o.expires = f[9].Get<uint32>(); o.finished = f[10].Get<uint32>();
                s_orders[o.id] = std::move(o);
            } while (r->NextRow());
        LOG_INFO("module", "housing: {} shops, {} listings, {} open commissions, {} commissionable recipes", s_shops.size(),
            s_listings.size(), s_orders.size(), s_recipes.size());
    }

    // ---------------------------------------------------------------- the objects in the world

    void SendLook(Player* to, ObjectGuid guid, Shop const& s);

    void SpawnMerchant(Map* map, Placed const& p)
    {
        auto shop = s_shops.find(p.id);
        if (shop == s_shops.end())
            return;
        if (Creature* c = map->SummonCreature(shop->second.entry, Position(p.pos[0], p.pos[1], p.pos[2], p.yaw)))
        {
            Shop const& s = shop->second;
            ChrRacesEntry const* race = sChrRacesStore.LookupEntry(s.race);
            uint32 const display = race ? (s.sex ? race->model_f : race->model_m) : 0;
            if (display)
            {
                c->SetDisplayId(display);
                c->SetNativeDisplayId(display);
                c->SetByteValue(UNIT_FIELD_BYTES_0, 0, s.race);
                c->SetByteValue(UNIT_FIELD_BYTES_0, 1, CLASS_WARRIOR);
                c->SetByteValue(UNIT_FIELD_BYTES_0, 2, s.sex);
                c->SetFlag(UNIT_FIELD_FLAGS_2, UNIT_FLAG2_MIRROR_IMAGE); // the client asks for the look (MerchantMirrorImage)
            }
            c->SetObjectScale(p.scale);
            for (uint8 i = 0; i < 3; ++i)
                if (auto gear = s.gear.find(uint8(GearMainHand + i)); gear != s.gear.end())
                    c->SetUInt32Value(UNIT_VIRTUAL_ITEM_SLOT_ID + i, gear->second.item->GetEntry());
            s_spawned[map->GetInstanceId()][p.id] = c->GetGUID();
            // its saved look, to everyone here now: the client keeps looks by guid and applies one as soon as the model is
            // built, so it does not hang on the mirror-image request (which a client may not make for a fresh spawn)
            ObjectGuid const guid = c->GetGUID();
            map->DoForAllPlayers([&](Player* player) { SendLook(player, guid, s); });
        }
    }

    Placed const* FindPlaced(House const& house, uint64 id)
    {
        if (auto it = house.placed.find(id); it != house.placed.end())
            return &it->second;
        for (auto const& [hood, decor] : house.outdoor)
            if (auto it = decor.find(id); it != decor.end())
                return &it->second;
        return nullptr;
    }

    // A placed shop or board was just created.
    void ShopPlaced(House const& house, Placed const& p, Player* player, CharacterDatabaseTransaction trans)
    {
        uint8 const kind = ServiceKindOf(p.decorId);
        if (!kind || kind == ServiceBoard)
            return;
        Shop shop;
        shop.placed = p.id; shop.house = house.id; shop.account = house.account; shop.ownerGuid = player->GetGUID().GetCounter(); shop.kind = kind;
        shop.name = kind < std::size(DefaultShopName) ? DefaultShopName[kind] : "Shop";
        if ((shop.entry = NextMerchantEntry())) // every shop is named: the merchant itself, the others by a floating label
            NameTemplate(shop);
        SaveShop(shop, trans);
        s_shops[p.id] = std::move(shop);
    }

    // Mails a held item to its shop's owner, in stacks a bag can hold.
    void MailHeld(Item* item, uint32 receiver, CharacterDatabaseTransaction trans)
    {
        ObjectGuid const guid = ObjectGuid::Create<HighGuid::Player>(receiver);
        uint32 const maxStack = item->GetTemplate()->GetMaxStackSize();
        Player* online = ObjectAccessor::FindConnectedPlayer(guid);
        auto const mail = [&](Item* piece) {
            piece->SetOwnerGUID(guid);
            if (piece->GetState() != ITEM_NEW)
                piece->FSetState(ITEM_CHANGED);
            piece->SaveToDB(trans);
            MailDraft("Your shop's stock", "This shop was taken down. Here is what it still held.").AddItem(piece)
                .SendMailTo(trans, MailReceiver(online, receiver), MailSender(MAIL_CREATURE, 9500100));
        };
        while (item->GetCount() > maxStack)
        {
            Item* piece = item->CloneItem(maxStack, online);
            item->SetCount(item->GetCount() - maxStack);
            if (piece)
                mail(piece);
        }
        mail(item);
    }

    // Whether a placed shop still holds goods for sale.
    bool HasStockForSale(uint64 placedId)
    {
        for (auto const& [id, l] : s_listings)
            if (l.shop == placedId && l.Stock())
                return true;
        return false;
    }

    // A placed shop is being taken down: unsold stock goes home by mail.
    void ShopRemoved(uint64 placedId, CharacterDatabaseTransaction trans)
    {
        auto shop = s_shops.find(placedId);
        if (shop == s_shops.end())
            return;
        for (auto it = s_listings.begin(); it != s_listings.end();)
        {
            if (it->second.shop != placedId)
            {
                ++it;
                continue;
            }
            if (it->second.item)
                MailHeld(it->second.item, shop->second.ownerGuid, trans);
            it = s_listings.erase(it);
        }
        for (auto& [slot, gear] : shop->second.gear)
            MailHeld(gear.item, gear.ownerGuid, trans);
        trans->Append("DELETE FROM housing_shop_gear WHERE placed_id = {}", placedId);
        trans->Append("DELETE FROM housing_shop_listing WHERE placed_id = {}", placedId);
        trans->Append("DELETE FROM housing_shop WHERE placed_id = {}", placedId);
        s_shops.erase(shop);
    }

    // ---------------------------------------------------------------- the shop window

    std::string ItemLink(Item const* item, uint32 entry)
    {
        std::ostringstream link;
        link << "item:" << entry;
        if (!item)
        {
            link << ":0:0:0:0:0:0:0:80";
            return link.str();
        }
        link << ':' << item->GetEnchantmentId(PERM_ENCHANTMENT_SLOT);
        for (uint8 s = SOCK_ENCHANTMENT_SLOT; s < SOCK_ENCHANTMENT_SLOT + 3; ++s)
            link << ':' << item->GetEnchantmentId(EnchantmentSlot(s));
        link << ":0:" << item->GetItemRandomPropertyId() << ':' << item->GetItemSuffixFactor() << ":80";
        return link.str();
    }

    void SendShop(Player* player, std::string const& message = "")
    {
        auto view = s_shopView.find(player->GetGUID());
        auto shop = view == s_shopView.end() ? s_shops.end() : s_shops.find(view->second.shop);
        if (shop == s_shops.end())
            return;
        Shop const& s = shop->second;
        bool const owner = s.account == player->GetSession()->GetAccountId();
        ShopAccount const& account = s_shopAccounts[s.account];
        std::ostringstream out;
        out << "shop\t" << int(owner) << '\t' << s.name << '\t' << s.theme << '\t' << s.greeting << '\t' << message << '\t'
            << (owner ? account.treasury : 0) << '\t' << int(s.kind) << '\t' << 0 << '\t' << s.thanks << '\t' << s.farewell << '\t'
            << s.sign << '\t' << int(s.symbol) << '\t' << int(s.border) << '\t' << int(owner && account.bankDeposit) << '\t' << BankDepositPrice
            << '\t' << s.labelHeight << '\n';
        for (auto const& [id, l] : s_listings)
        {
            if (l.shop != s.placed || (!owner && !l.published))
                continue;
            ItemTemplate const* proto = sObjectMgr->GetItemTemplate(l.entry);
            out << "L\t" << id << '\t' << l.entry << '\t' << (proto ? proto->Name1 : "?") << '\t' << l.bundle << '\t' << l.price << '\t'
                << l.Stock() << '\t' << ItemLink(l.item, l.entry) << '\t' << int(l.published) << '\t' << (proto ? proto->Quality : 1) << '\n';
        }
        SendCommerce(player, out.str());
    }

    // The shop the player has open, if they are still beside what they opened it from.
    Shop* ViewedShop(Player* player, WorldObject** object = nullptr)
    {
        auto view = s_shopView.find(player->GetGUID());
        if (view == s_shopView.end())
            return nullptr;
        WorldObject* near = ObjectAccessor::GetWorldObject(*player, view->second.object);
        auto shop = s_shops.find(view->second.shop);
        if (!near || shop == s_shops.end()
            || !player->IsWithinDistInMap(near, shop->second.account == player->GetSession()->GetAccountId() ? ServiceRangeOwner : ServiceRange))
            return nullptr;
        if (object)
            *object = near;
        return &shop->second;
    }

    void SpeakTo(Player* player, WorldObject* object, std::string const& text)
    {
        if (Creature* c = object ? object->ToCreature() : nullptr; c && !text.empty())
            c->Whisper(text, LANG_UNIVERSAL, player);
    }

    // Takes `amount` out of a listing into the player's bags. "" on success, else why not; nothing changes on failure.
    std::string TakeFromListing(Listing& l, uint32 amount, Player* player)
    {
        if (!l.item || amount > l.Stock())
            return "That is sold out.";
        Item* moved = amount < l.Stock() ? l.item->CloneItem(amount, player) : l.item;
        if (!moved)
            return "That item could not be moved.";
        ObjectGuid const previous = moved->GetOwnerGUID();
        moved->SetOwnerGUID(player->GetGUID());
        ItemPosCountVec dest;
        if (player->CanStoreItem(NULL_BAG, NULL_SLOT, dest, moved, false) != EQUIP_ERR_OK)
        {
            if (moved == l.item)
                moved->SetOwnerGUID(previous);
            else
                delete moved;
            return "Your bags are full.";
        }
        if (moved == l.item)
            l.item = nullptr; // MoveItemToInventory may merge and delete it
        else
        {
            l.item->SetCount(l.item->GetCount() - amount);
            l.item->FSetState(ITEM_CHANGED);
        }
        player->MoveItemToInventory(dest, moved, true);
        return "";
    }

    Listing* OwnedListing(Shop const& s, uint32 id)
    {
        auto it = s_listings.find(id);
        return it != s_listings.end() && it->second.shop == s.placed ? &it->second : nullptr;
    }

    // Everything but bound, conjured, timed and refundable goods may be sold.
    bool Sellable(Item const* item)
    {
        return item && !item->IsSoulBound() && !item->IsNotEmptyBag() && !item->m_lootGenerated && !item->IsRefundable() && !item->IsBOPTradable()
            && !item->GetTemplate()->HasFlag(ITEM_FLAG_CONJURED) && !item->GetUInt32Value(ITEM_FIELD_DURATION) && !item->IsBoundAccountWide();
    }

    enum StockSource : uint8 { SourceBags = 0, SourceInventory = 1, SourceBank = 2 };

    template <typename Fn> void ForEachBagItem(Player* player, Fn fn)
    {
        for (uint8 slot = INVENTORY_SLOT_ITEM_START; slot < INVENTORY_SLOT_ITEM_END; ++slot)
            if (Item* item = player->GetItemByPos(INVENTORY_SLOT_BAG_0, slot))
                fn(item);
        for (uint8 bag = INVENTORY_SLOT_BAG_START; bag < INVENTORY_SLOT_BAG_END; ++bag)
            if (Bag* container = player->GetBagByPos(bag))
                for (uint32 slot = 0; slot < container->GetBagSize(); ++slot)
                    if (Item* item = container->GetItemByPos(uint8(slot)))
                        fn(item);
    }

    // The Add Items tab: every sellable item the owner can reach, bags and Esteria Inventory, and the bank once unlocked.
    void SendStockable(Player* player, Shop const& s)
    {
        std::ostringstream out;
        out << "stockable\t" << int(s_shopAccounts[s.account].bankDeposit) << '\n';
        auto const row = [&out](uint8 source, Item const* item) {
            if (!Sellable(item))
                return;
            ItemTemplate const* p = item->GetTemplate();
            out << "I\t" << int(source) << '\t' << item->GetGUID().GetCounter() << '\t' << item->GetEntry() << '\t' << p->Name1 << '\t' << item->GetCount()
                << '\t' << ItemLink(item, item->GetEntry()) << '\t' << p->Quality << '\n';
        };
        ForEachBagItem(player, [&](Item* item) { row(SourceBags, item); });
        for (Item const* item : player->GetDigitalInventory().Items())
            row(SourceInventory, item);
        if (s_shopAccounts[s.account].bankDeposit)
        {
            player->GetDigitalBank().LoadBank();
            for (Item const* item : player->GetDigitalBank().Items())
                row(SourceBank, item);
        }
        SendCommerce(player, out.str());
    }

    // Pulls the chosen item out of where it is; the caller's transaction saves the player and so the inventories.
    Item* TakeStock(Player* player, Shop const& s, uint8 source, uint32 guid, CharacterDatabaseTransaction trans, bool anyItem = false)
    {
        if (source == SourceInventory)
            return player->GetDigitalInventory().TakeForShop(guid);
        if (source == SourceBank)
            return s_shopAccounts[s.account].bankDeposit ? player->GetDigitalBank().TakeForShop(guid) : nullptr;
        Item* found = nullptr;
        ForEachBagItem(player, [&](Item* item) { if (item->GetGUID().GetCounter() == guid) found = item; });
        if (!found || (!anyItem && !Sellable(found)))
            return nullptr;
        player->MoveItemFromInventory(found->GetBagSlot(), found->GetSlot(), true);
        found->DeleteFromInventoryDB(trans);
        return found;
    }

    std::string Deposit(Player* player, Shop& s, Fields const& f)
    {
        if (player->GetTradeData())
            return "Finish your trade first.";
        uint8 const source = uint8(Num(f, 1));
        uint32 const guid = Num(f, 2), bundle = Num(f, 3), price = Num(f, 4), restock = Num(f, 5);
        if (source > SourceBank || (source == SourceBank && !s_shopAccounts[s.account].bankDeposit))
            return "Unlock deposits from your bank first.";
        // Look before taking: a refused deposit must leave the item where it was.
        Item const* look = nullptr;
        auto const peek = [&](Item const* item) { if (item->GetGUID().GetCounter() == guid) look = item; };
        if (source == SourceBags)
            ForEachBagItem(player, peek);
        else
        {
            if (source == SourceBank)
                player->GetDigitalBank().LoadBank();
            for (Item const* item : (source == SourceBank ? player->GetDigitalBank() : player->GetDigitalInventory()).Items())
                peek(item);
        }
        if (!Sellable(look))
            return "That item cannot be sold.";
        uint32 const maxStack = look->GetTemplate()->GetMaxStackSize();
        Listing* l = restock ? OwnedListing(s, restock) : nullptr;
        if (restock && (!l || l->entry != look->GetEntry()))
            return "That is not the same item.";
        if (restock && l->item && maxStack < 2)
            return "Only stackable items can be added to a listing that still has stock.";
        if (!restock && !EsteriaHousing::ValidListing(bundle, look->GetCount(), maxStack, price))
            return "Check the price and the bundle size.";
        if (!restock && std::count_if(s_listings.begin(), s_listings.end(), [&](auto const& e) { return e.second.shop == s.placed; })
            >= std::ptrdiff_t(MaxListings))
            return "This shop has as many listings as it can hold.";

        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        Item* item = TakeStock(player, s, source, guid, trans);
        if (!item)
            return "That item is not available.";
        if (!l)
        {
            Listing fresh;
            fresh.id = s_nextListing++; fresh.shop = s.placed; fresh.entry = item->GetEntry(); fresh.bundle = bundle; fresh.price = price;
            l = &(s_listings[fresh.id] = fresh);
        }
        if (l->item) // merge a plain stack into what the listing already holds
        {
            l->item->SetCount(l->item->GetCount() + item->GetCount());
            l->item->FSetState(ITEM_CHANGED);
            l->item->SaveToDB(trans);
            item->FSetState(ITEM_REMOVED);
            item->SaveToDB(trans);
            delete item;
        }
        else
        {
            item->SetOwnerGUID(ObjectGuid::Empty); // deleting the character must not delete shop stock
            if (item->GetState() != ITEM_NEW)
                item->FSetState(ITEM_CHANGED);
            item->SaveToDB(trans);
            l->item = item;
        }
        SaveListing(*l, trans);
        player->SaveInventoryAndGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);
        return "";
    }

    std::string Retrieve(Player* player, Listing& l)
    {
        if (!l.item) // sold out: nothing to hand back, the row just goes
        {
            CharacterDatabase.Execute("DELETE FROM housing_shop_listing WHERE listing_id = {}", l.id);
            s_listings.erase(l.id);
            return "";
        }
        uint32 const amount = std::min(l.Stock(), l.item->GetTemplate()->GetMaxStackSize());
        std::string error = TakeFromListing(l, amount, player);
        if (!error.empty())
            return error;
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        if (l.item)
        {
            l.item->SaveToDB(trans);
            SaveListing(l, trans);
        }
        else
            trans->Append("DELETE FROM housing_shop_listing WHERE listing_id = {}", l.id);
        player->SaveInventoryAndGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);
        if (!l.item)
            s_listings.erase(l.id);
        return "";
    }

    std::string Buy(Player* player, Shop& s, Listing& l, uint32 seenPrice, WorldObject* object)
    {
        House const& house = s_houses[s.house];
        if (s.account == player->GetSession()->GetAccountId())
            return "This is your own shop.";
        if (!MayEnter(player, house))
            return "The owner has closed this shop to you.";
        if (!l.published || l.price != seenPrice) // the price changed under the buyer
            return "That listing just changed. Check it and try again.";
        if (l.Stock() < l.bundle)
            return "That is sold out.";
        if (!player->HasEnoughMoney(l.price))
            return "You don't have enough money.";
        uint32 const bought = l.bundle, price = l.price, entry = l.entry;
        std::string error = TakeFromListing(l, bought, player);
        if (!error.empty())
            return error;
        player->ModifyMoney(-int32(price));
        s_shopAccounts[s.account].treasury += price;
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        if (l.item)
            l.item->SaveToDB(trans);
        SaveListing(l, trans);
        SaveShopAccount(s.account, trans);
        trans->Append("INSERT INTO housing_shop_sale (account_id, shop_name, item_entry, count, price, buyer_guid, buyer_name, sold_at) "
            "VALUES ({}, '{}', {}, {}, {}, {}, '{}', {})", s.account, Sql(s.name), entry, bought, price, player->GetGUID().GetCounter(),
            Sql(player->GetName()), uint32(GameTime::GetGameTime().count()));
        player->SaveInventoryAndGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);
        SpeakTo(player, object, s.thanks);
        return "";
    }

    // Every shop of the account, in one ledger.
    void SendLedger(Player* player, Shop const& s)
    {
        std::ostringstream out;
        uint64 sales = 0, gross = 0;
        if (QueryResult r = CharacterDatabase.Query("SELECT COUNT(*), COALESCE(SUM(price), 0) FROM housing_shop_sale WHERE account_id = {}", s.account))
        {
            sales = r->Fetch()[0].Get<uint64>();
            gross = uint64(r->Fetch()[1].Get<double>());
        }
        out << "ledger\t" << sales << '\t' << gross << '\t' << s_shopAccounts[s.account].treasury << '\n';
        auto const name = [](uint32 entry) { ItemTemplate const* p = sObjectMgr->GetItemTemplate(entry); return p ? p->Name1 : std::string("?"); };
        if (QueryResult r = CharacterDatabase.Query("SELECT item_entry, SUM(count), SUM(price) FROM housing_shop_sale WHERE account_id = {} "
            "GROUP BY item_entry ORDER BY SUM(price) DESC LIMIT 5", s.account))
            do
                out << "B\t" << name(r->Fetch()[0].Get<uint32>()) << '\t' << uint64(r->Fetch()[1].Get<double>()) << '\t'
                    << uint64(r->Fetch()[2].Get<double>()) << '\n';
            while (r->NextRow());
        uint32 const now = uint32(GameTime::GetGameTime().count());
        if (QueryResult r = CharacterDatabase.Query("SELECT item_entry, count, price, buyer_name, sold_at, shop_name FROM housing_shop_sale "
            "WHERE account_id = {} ORDER BY sale_id DESC LIMIT 30", s.account))
            do
                out << "T\t" << name(r->Fetch()[0].Get<uint32>()) << '\t' << r->Fetch()[1].Get<uint32>() << '\t' << r->Fetch()[2].Get<uint32>() << '\t'
                    << r->Fetch()[3].Get<std::string>() << '\t' << (now - std::min(now, r->Fetch()[4].Get<uint32>())) << '\t'
                    << r->Fetch()[5].Get<std::string>() << '\n';
            while (r->NextRow());
        SendCommerce(player, out.str());
    }

    // ---------------------------------------------------------------- what a merchant looks like and wears

    std::string GuidHex(ObjectGuid guid)
    {
        char text[20];
        std::snprintf(text, sizeof(text), "%llx", static_cast<unsigned long long>(guid.GetRawValue()));
        return text;
    }

    template <size_t N> bool FromHex(std::string const& text, std::array<uint8, N>& out)
    {
        if (text.size() != N * 2 || text.find_first_not_of("0123456789abcdefABCDEF") != std::string::npos)
            return false;
        for (size_t i = 0; i < N; ++i)
            out[i] = uint8(std::stoul(text.substr(i * 2, 2), nullptr, 16));
        return true;
    }

    // The race's default retail look (every option at its first choice). A character with no look at all is drawn as the
    // stock 3.3.5 body, which the customizer cannot edit; with this one it is a retail character from the start.
    std::string DefaultLookHex(uint8 race, uint8 sex)
    {
        CharacterRetailLook::Look look;
        look.race = race;
        look.sex = sex;
        std::array<uint8, CharacterRetailLook::PayloadSize> raw;
        CharacterRetailLook::WritePayload(raw.data(), look);
        static char const digits[] = "0123456789abcdef";
        std::string out;
        for (uint8 b : raw) { out += digits[b >> 4]; out += digits[b & 15]; }
        return out;
    }

    bool PlayableRace(uint8 race)
    {
        if (!sChrRacesStore.LookupEntry(race))
            return false;
        for (uint8 cls = 1; cls < MAX_CLASSES; ++cls)
            if (sObjectMgr->GetPlayerInfo(race, cls))
                return true;
        return false;
    }

    // A case's, shelf's, rack's, counter's or sign's name and title: objects show no name, so an invisible creature named
    // for the shop floats above it (clicking it opens the shop, as the object does).
    void SpawnShopLabel(Map* map, Placed const& p)
    {
        auto shop = s_shops.find(p.id);
        if (shop == s_shops.end() || shop->second.kind == ServiceMerchant || !shop->second.entry)
            return;
        DespawnShopLabel(map, p.id);
        // a real model shrunk to a speck (its template's scale, NameTemplate: it is created that small, never seen shrinking);
        // the client draws no name over the invisible stalker's empty model
        if (Creature* c = map->SummonCreature(shop->second.entry, Position(p.pos[0], p.pos[1], p.pos[2] + shop->second.labelHeight,
            p.yaw)))
        {
            c->SetFlag(UNIT_FIELD_FLAGS, UNIT_FLAG_NON_ATTACKABLE | UNIT_FLAG_IMMUNE_TO_PC | UNIT_FLAG_IMMUNE_TO_NPC);
            c->SetReactState(REACT_PASSIVE);
            c->SetDisableGravity(true);
            c->SetControlled(true, UNIT_STATE_ROOT);
            s_labelPlaced[c->GetGUID()] = p.id;
            s_shopLabel[p.id] = { map->GetInstanceId(), c->GetGUID() };
            LOG_INFO("module", "housing: shop {} label '{}' spawned in instance {}", p.id, shop->second.name, map->GetInstanceId());
        }
        else
            LOG_ERROR("module", "housing: shop {} label (entry {}) could not spawn", p.id, shop->second.entry);
    }

    void DespawnShopLabel(Map* map, uint64 placedId)
    {
        auto it = s_shopLabel.find(placedId);
        if (it == s_shopLabel.end())
            return;
        if (it->second.first == map->GetInstanceId())
            if (Creature* c = map->GetCreature(it->second.second))
                c->DespawnOrUnsummon();
        s_labelPlaced.erase(it->second.second);
        s_shopLabel.erase(it);
    }

    // The names of the shops in a map, and its merchants' looks, sent to a player arriving there: clients cache creature
    // names by entry (the pool's entries are reused, so a cached one may be stale), and keep looks by guid.
    void PushMerchantNames(Player* player, Map* map)
    {
        for (auto const& [placed, guid] : s_spawned[map->GetInstanceId()])
            if (auto shop = s_shops.find(placed); shop != s_shops.end() && shop->second.entry)
            {
                if (CreatureTemplate const* t = sObjectMgr->GetCreatureTemplate(shop->second.entry))
                {
                    WorldPacket name = t->queryData;
                    player->SendDirectMessage(&name);
                }
                if (shop->second.kind == ServiceMerchant) // and a merchant's saved look (SpawnMerchant)
                    SendLook(player, guid, shop->second);
            }
    }

    void RespawnMerchant(Player* player, Shop const& s)
    {
        Placed const* p = FindPlaced(s_houses[s.house], s.placed);
        if (!p)
            return;
        Map* map = player->GetMap();
        Despawn(map, s.placed);
        SpawnMerchant(map, *p);
        auto const& spawned = s_spawned[map->GetInstanceId()];
        if (auto now = spawned.find(s.placed); now != spawned.end())
            s_shopView[player->GetGUID()].object = now->second;
    }

    void SendLookHex(Player* to, ObjectGuid guid, std::string const& lookHex, std::string const& bodyHex);
    void SendLook(Player* to, ObjectGuid guid, Shop const& s) { SendLookHex(to, guid, s.lookHex, s.bodyHex); }

    // A saved customization (a merchant's, a mannequin's), to one client: it keeps looks by guid.
    void SendLookHex(Player* to, ObjectGuid guid, std::string const& lookHex, std::string const& bodyHex)
    {
        std::array<uint8, CharacterRetailLook::PayloadSize> look;
        if (FromHex(lookHex, look))
        {
            WorldPacket data(SMSG_ESTERIA_RETAIL_LOOK, 8 + look.size());
            data << guid.GetRawValue();
            data.append(look.data(), look.size());
            to->SendDirectMessage(&data);
        }
        std::array<uint8, CharacterBodyShape::PayloadSize> body;
        if (FromHex(bodyHex, body))
        {
            WorldPacket data(SMSG_ESTERIA_BODY_SHAPE, 8 + body.size());
            data << guid.GetRawValue();
            data.append(body.data(), body.size());
            to->SendDirectMessage(&data);
        }
    }

    // The client asks when a merchant comes into view; it answers with the appearance, then the stock mirror-image packet.
    bool MerchantMirrorImage(Player* player, Unit* unit)
    {
        std::lock_guard<std::recursive_mutex> guard(s_lock);
        Creature* creature = unit->ToCreature();
        if (!creature || creature->GetEntry() < MerchantEntryFirst || creature->GetEntry() > MerchantEntryLast)
            return DisplayMirrorImage(player, unit); // a mannequin
        Shop const* shop = nullptr;
        for (auto const& [id, guid] : s_spawned[unit->GetInstanceId()])
            if (guid == unit->GetGUID())
                if (auto it = s_shops.find(id); it != s_shops.end())
                    shop = &it->second;
        if (!shop)
            return false;
        SendLook(player, unit->GetGUID(), *shop);
        WorldPacket data(SMSG_MIRRORIMAGE_DATA, 68);
        data << unit->GetGUID() << uint32(unit->GetDisplayId()) << uint8(shop->race) << uint8(shop->sex) << uint8(CLASS_WARRIOR);
        data << uint8(0) << uint8(0) << uint8(0) << uint8(0) << uint8(0) << uint32(0); // the look carries these
        for (uint8 slot : MirrorSlots)
        {
            auto gear = shop->gear.find(slot);
            data << uint32(gear == shop->gear.end() ? 0 : gear->second.item->GetTemplate()->DisplayInfoID);
        }
        player->SendDirectMessage(&data);
        return true;
    }

    // Opens the customizer on the merchant: the addon edits the real NPC, so the world is the preview.
    void SendCustomize(Player* player, Shop const& s)
    {
        auto view = s_shopView.find(player->GetGUID());
        if (view == s_shopView.end())
            return;
        std::ostringstream out;
        out << "customize\t" << GuidHex(view->second.object) << '\t' << int(s.race) << '\t' << int(s.sex) << '\t' << s.bodyHex << '\n';
        for (uint32 i = 0; i < sChrRacesStore.GetNumRows(); ++i)
            if (ChrRacesEntry const* race = sChrRacesStore.LookupEntry(i); race && PlayableRace(uint8(i)))
                out << "R\t" << i << '\t' << race->name[0] << '\n';
        SendCommerce(player, out.str());
    }

    void MerchantJustPlaced(Player* player, Placed const& p)
    {
        auto shop = s_shops.find(p.id);
        auto const& spawned = s_spawned[player->GetInstanceId()];
        auto object = spawned.find(p.id);
        if (shop == s_shops.end() || shop->second.kind != ServiceMerchant || object == spawned.end())
            return;
        s_shopView[player->GetGUID()] = { p.id, object->second };
        SendShop(player);
        SendCustomize(player, shop->second);
    }

    std::string SaveLook(Player* player, Shop& s, std::string const& lookHex, std::string const& bodyHex)
    {
        std::array<uint8, CharacterRetailLook::PayloadSize> raw;
        CharacterRetailLook::Look look;
        if (!FromHex(lookHex, raw) || !CharacterRetailLook::ReadPayload(raw.data(), raw.size(), look) || look.race != s.race || look.sex != s.sex)
            return "That appearance could not be saved.";
        std::array<uint8, CharacterBodyShape::PayloadSize> rawBody;
        CharacterBodyShape::Values body{};
        if (!FromHex(bodyHex, rawBody) || !CharacterBodyShape::ReadPayload(rawBody.data(), rawBody.size(), body))
            return "Those body sliders could not be saved.";
        s.lookHex = lookHex;
        s.bodyHex = bodyHex;
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        SaveShop(s, trans);
        CharacterDatabase.CommitTransaction(trans);
        Map* map = player->GetMap();
        auto const& spawned = s_spawned[map->GetInstanceId()];
        if (auto now = spawned.find(s.placed); now != spawned.end())
            map->DoForAllPlayers([&](Player* other) { SendLook(other, now->second, s); });
        return "";
    }

    bool Wearable(Item const* item)
    {
        return item && GearSlotOf(item->GetTemplate()) != GearNone && !item->IsNotEmptyBag() && !item->m_lootGenerated && !item->IsRefundable()
            && !item->IsBOPTradable() && !item->GetTemplate()->HasFlag(ITEM_FLAG_CONJURED) && !item->GetUInt32Value(ITEM_FIELD_DURATION);
    }

    void SendGear(Player* player, Shop const& s, std::string const& message = "")
    {
        std::ostringstream out;
        out << "gear\t" << message << '\n';
        for (auto const& [slot, gear] : s.gear)
        {
            ItemTemplate const* p = gear.item->GetTemplate();
            out << "W\t" << int(slot) << '\t' << gear.item->GetEntry() << '\t' << p->Name1 << '\t' << ItemLink(gear.item, gear.item->GetEntry()) << '\t' << p->Quality << '\n';
        }
        auto const row = [&out](uint8 source, Item const* item) {
            if (!Wearable(item))
                return;
            ItemTemplate const* p = item->GetTemplate();
            out << "G\t" << int(source) << '\t' << item->GetGUID().GetCounter() << '\t' << item->GetEntry() << '\t' << p->Name1 << '\t'
                << ItemLink(item, item->GetEntry()) << '\t' << p->Quality << '\n';
        };
        ForEachBagItem(player, [&](Item* item) { row(SourceBags, item); });
        for (Item const* item : player->GetDigitalInventory().Items())
            row(SourceInventory, item);
        if (s_shopAccounts[s.account].bankDeposit)
        {
            player->GetDigitalBank().LoadBank();
            for (Item const* item : player->GetDigitalBank().Items())
                row(SourceBank, item);
        }
        SendCommerce(player, out.str());
    }

    std::string Unequip(Player* player, Shop& s, uint8 slot)
    {
        auto gear = s.gear.find(slot);
        if (gear == s.gear.end())
            return "The merchant isn't wearing that.";
        Item* item = gear->second.item;
        if (item->IsSoulBound() && gear->second.ownerGuid != player->GetGUID().GetCounter())
            return "Only the character who gave it can take that back.";
        item->SetOwnerGUID(player->GetGUID());
        ItemPosCountVec dest;
        if (player->CanStoreItem(NULL_BAG, NULL_SLOT, dest, item, false) != EQUIP_ERR_OK)
        {
            item->SetOwnerGUID(ObjectGuid::Empty);
            return "Your bags are full.";
        }
        s.gear.erase(gear);
        player->MoveItemToInventory(dest, item, true);
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        trans->Append("DELETE FROM housing_shop_gear WHERE placed_id = {} AND slot = {}", s.placed, slot);
        player->SaveInventoryAndGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);
        return "";
    }

    std::string Equip(Player* player, Shop& s, Fields const& f)
    {
        if (player->GetTradeData())
            return "Finish your trade first.";
        uint8 const source = uint8(Num(f, 1));
        uint32 const guid = Num(f, 2);
        if (source > SourceBank || (source == SourceBank && !s_shopAccounts[s.account].bankDeposit))
            return "Unlock your bank first.";
        Item const* look = nullptr;
        auto const peek = [&](Item const* item) { if (item->GetGUID().GetCounter() == guid) look = item; };
        if (source == SourceBags)
            ForEachBagItem(player, peek);
        else
        {
            if (source == SourceBank)
                player->GetDigitalBank().LoadBank();
            for (Item const* item : (source == SourceBank ? player->GetDigitalBank() : player->GetDigitalInventory()).Items())
                peek(item);
        }
        if (!Wearable(look))
            return "The merchant can't wear that.";
        uint8 const slot = GearSlotOf(look->GetTemplate());
        if (s.gear.count(slot))
        {
            std::string error = Unequip(player, s, slot);
            if (!error.empty())
                return error;
        }
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        Item* item = TakeStock(player, s, source, guid, trans, true);
        if (!item)
            return "That item is not available.";
        item->SetOwnerGUID(ObjectGuid::Empty);
        if (item->GetState() != ITEM_NEW)
            item->FSetState(ITEM_CHANGED);
        item->SaveToDB(trans);
        uint32 const owner = player->GetGUID().GetCounter();
        s.gear[slot] = { item, owner };
        trans->Append("REPLACE INTO housing_shop_gear (placed_id, slot, item_guid, owner_guid) VALUES ({}, {}, {}, {})", s.placed, slot,
            item->GetGUID().GetCounter(), owner);
        player->SaveInventoryAndGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);
        RespawnMerchant(player, s);
        return "";
    }

    // ---------------------------------------------------------------- commissions

    void MailOut(uint32 receiver, std::string const& subject, std::string const& body, std::vector<std::pair<uint32, uint32>> const& items,
        uint32 money, ObjectGuid::LowType creator, CharacterDatabaseTransaction trans)
    {
        ObjectGuid const guid = ObjectGuid::Create<HighGuid::Player>(receiver);
        Player* online = ObjectAccessor::FindConnectedPlayer(guid);
        MailDraft draft(subject, body);
        uint8 attached = 0;
        bool sent = false;
        auto const send = [&]() {
            draft.AddMoney(sent ? 0 : money);
            draft.SendMailTo(trans, MailReceiver(online, receiver), MailSender(MAIL_CREATURE, 9500100));
            sent = true;
            attached = 0;
            draft = MailDraft(subject, body);
        };
        for (auto const& [entry, total] : items)
        {
            ItemTemplate const* proto = sObjectMgr->GetItemTemplate(entry);
            if (!proto)
                continue;
            for (uint32 left = total; left;)
            {
                uint32 const n = std::min(left, proto->GetMaxStackSize());
                left -= n;
                Item* item = Item::CreateItem(entry, n);
                if (!item)
                    continue;
                if (creator)
                    item->SetGuidValue(ITEM_FIELD_CREATOR, ObjectGuid::Create<HighGuid::Player>(creator));
                item->SaveToDB(trans);
                draft.AddItem(item);
                if (++attached == MAX_MAIL_ITEMS)
                    send();
            }
        }
        if (attached || !sent)
            send();
    }

    // The order ends without being made: its materials and fee go back to the customer by mail.
    void ReturnOrder(Order& o, uint8 state, char const* why)
    {
        o.state = state;
        o.finished = uint32(GameTime::GetGameTime().count());
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        SaveOrder(o, trans);
        MailOut(o.customer, "Your commission", why, o.materials, o.fee, 0, trans);
        CharacterDatabase.CommitTransaction(trans);
    }

    void SweepOrders()
    {
        uint32 const now = uint32(GameTime::GetGameTime().count());
        for (auto it = s_orders.begin(); it != s_orders.end();)
        {
            Order& o = it->second;
            if (o.state < EsteriaHousing::OrderCompleted && now >= o.expires)
                ReturnOrder(o, EsteriaHousing::OrderExpired, "Your commission expired before anyone finished it. Here are your materials and payment.");
            if (o.state >= EsteriaHousing::OrderCompleted && now >= o.finished + 3 * DAY)
                it = s_orders.erase(it);
            else
                ++it;
        }
    }

    void SendBoard(Player* player, std::string const& message = "")
    {
        std::ostringstream out;
        uint32 const me = player->GetGUID().GetCounter();
        out << "board\t" << message << '\n';
        auto const nameOf = [](uint32 guid) {
            std::string name;
            return guid && sCharacterCache->GetCharacterNameByGuid(ObjectGuid::Create<HighGuid::Player>(guid), name) ? name : std::string();
        };
        size_t rows = 0;
        for (auto it = s_orders.rbegin(); it != s_orders.rend() && rows < 60; ++it)
        {
            Order const& o = it->second;
            bool const mine = o.customer == me, crafting = o.crafter == me;
            if (!mine && !crafting && o.state != EsteriaHousing::OrderOpen)
                continue;
            ++rows;
            ItemTemplate const* proto = sObjectMgr->GetItemTemplate(o.item);
            out << "O\t" << o.id << '\t' << int(o.state) << '\t' << o.item << '\t' << (proto ? proto->Name1 : "?") << '\t' << o.quantity << '\t'
                << o.fee << '\t' << nameOf(o.customer) << '\t' << nameOf(o.crafter) << '\t' << (mine ? 1 : crafting ? 2 : 0) << '\t'
                << int(player->HasSpell(o.spell)) << '\t' << s_recipes[o.spell].skill << '\t';
            for (auto const& [item, count] : o.materials)
            {
                ItemTemplate const* m = sObjectMgr->GetItemTemplate(item);
                out << count << "x " << (m ? m->Name1 : "?") << ", ";
            }
            out << '\n';
        }
        SendCommerce(player, out.str());
    }

    void SendRecipes(Player* player, std::string query)
    {
        std::transform(query.begin(), query.end(), query.begin(), ::tolower);
        std::ostringstream out;
        out << "recipes\n";
        size_t rows = 0;
        std::vector<Recipe const*> found;
        if (query.size() >= 2)
            for (auto const& [spell, r] : s_recipes)
                if (r.lowerName.find(query) != std::string::npos)
                    found.push_back(&r);
        std::sort(found.begin(), found.end(), [](Recipe const* a, Recipe const* b) { return a->lowerName < b->lowerName; });
        for (Recipe const* r : found)
        {
            if (++rows > 30)
                break;
            ItemTemplate const* proto = sObjectMgr->GetItemTemplate(r->item);
            out << "R\t" << r->spell << '\t' << r->item << '\t' << proto->Name1 << '\t' << r->skill << '\t';
            for (auto const& [item, count] : r->reagents)
            {
                ItemTemplate const* m = sObjectMgr->GetItemTemplate(item);
                out << count << "x " << (m ? m->Name1 : "?") << ", ";
            }
            out << '\n';
        }
        SendCommerce(player, out.str());
    }

    std::string PostOrder(Player* player, uint32 spell, uint32 quantity, uint32 fee)
    {
        auto recipe = s_recipes.find(spell);
        if (recipe == s_recipes.end() || quantity < 1 || quantity > 20 || fee > 1000000000)
            return "Pick a recipe and a quantity from 1 to 20.";
        uint32 const me = player->GetGUID().GetCounter();
        if (std::count_if(s_orders.begin(), s_orders.end(), [me](auto const& o) { return o.second.customer == me && o.second.state < EsteriaHousing::OrderCompleted; }) >= 10)
            return "You already have 10 commissions open.";
        if (!player->HasEnoughMoney(fee))
            return "You don't have enough money for that payment.";
        std::map<uint32, uint32> totals;
        for (auto const& [item, count] : recipe->second.reagents)
            totals[item] += count * quantity;
        for (auto const& [item, count] : totals)
            if (!player->HasItemCount(item, count))
            {
                ItemTemplate const* m = sObjectMgr->GetItemTemplate(item);
                return std::string("You need ") + std::to_string(count) + " " + (m ? m->Name1 : "materials") + " in your bags.";
            }
        Order o;
        o.id = s_nextOrder++; o.customer = me; o.spell = spell; o.item = recipe->second.item; o.quantity = quantity; o.fee = fee;
        o.materials.assign(totals.begin(), totals.end());
        o.expires = uint32(GameTime::GetGameTime().count()) + 7 * DAY;
        for (auto const& [item, count] : totals)
            player->DestroyItemCount(item, count, true);
        player->ModifyMoney(-int32(fee));
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        SaveOrder(o, trans);
        player->SaveInventoryAndGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);
        s_orders[o.id] = std::move(o);
        return "";
    }

    std::string CompleteOrder(Player* player, Order& o)
    {
        if (!EsteriaHousing::OrderCan(o.state, EsteriaHousing::OrderCompleted) || o.crafter != player->GetGUID().GetCounter())
            return "That commission is not yours to finish.";
        if (!player->HasSpell(o.spell))
            return "You no longer know that recipe.";
        if (uint64(player->GetMoney()) + o.fee > MAX_MONEY_AMOUNT)
            return "You are carrying too much gold to be paid.";
        SpellInfo const* spell = sSpellMgr->GetSpellInfo(o.spell);
        if (!spell)
            return "That recipe no longer exists.";
        uint32 made = 0;
        for (uint8 e = 0; e < MAX_SPELL_EFFECTS && !made; ++e)
            if (spell->Effects[e].ItemType == o.item)
                made = spell->Effects[e].Effect == SPELL_EFFECT_ENCHANT_ITEM ? o.quantity
                    : o.quantity * std::max(1, spell->Effects[e].CalcValue(player));
        o.state = EsteriaHousing::OrderCompleted;
        o.finished = uint32(GameTime::GetGameTime().count());
        player->ModifyMoney(int32(o.fee));
        player->UpdateCraftSkill(o.spell);
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        SaveOrder(o, trans);
        MailOut(o.customer, "Your commission is ready", player->GetName() + " finished your commission.", { { o.item, made } }, 0,
            player->GetGUID().GetCounter(), trans);
        player->SaveInventoryAndGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);
        return "";
    }

    // ---------------------------------------------------------------- commands

    bool NearBoard(Player* player)
    {
        auto view = s_boardView.find(player->GetGUID());
        if (view == s_boardView.end())
            return false;
        WorldObject* board = ObjectAccessor::GetWorldObject(*player, view->second.object);
        return board && player->IsWithinDistInMap(board, ServiceRange);
    }

    void HandleBoardCommand(Player* player, Fields const& f)
    {
        std::string const& verb = f[0];
        if (verb == "search")
            return SendRecipes(player, f.size() > 1 ? Clean(f[1], 60) : "");
        std::string error;
        uint32 const me = player->GetGUID().GetCounter();
        auto it = s_orders.find(Num(f, 1));
        Order* o = it == s_orders.end() ? nullptr : &it->second;
        using namespace EsteriaHousing;
        if (verb == "post")
            error = PostOrder(player, Num(f, 1), Num(f, 2), Num(f, 3));
        else if (verb == "board")
            ;
        else if (!o)
            error = "That commission is gone.";
        else if (verb == "accept")
        {
            if (!OrderCan(o->state, OrderAccepted))
                error = "Someone already took that commission.";
            else if (o->customer == me)
                error = "That is your own commission.";
            else if (!player->HasSpell(o->spell))
                error = "You don't know that recipe.";
            else if (std::count_if(s_orders.begin(), s_orders.end(), [me](auto const& e) { return e.second.crafter == me && e.second.state == OrderAccepted; }) >= 5)
                error = "Finish one of your 5 accepted commissions first.";
            else
            {
                o->state = OrderAccepted;
                o->crafter = me;
                CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
                SaveOrder(*o, trans);
                CharacterDatabase.CommitTransaction(trans);
            }
        }
        else if (verb == "drop") // the crafter gives it back to the board
        {
            if (o->state != OrderAccepted || o->crafter != me)
                error = "That commission is not yours.";
            else
            {
                o->state = OrderOpen;
                o->crafter = 0;
                CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
                SaveOrder(*o, trans);
                CharacterDatabase.CommitTransaction(trans);
            }
        }
        else if (verb == "complete")
            error = CompleteOrder(player, *o);
        else if (verb == "cancel")
        {
            if (o->customer != me || !OrderCan(o->state, OrderCancelled))
                error = "That commission cannot be cancelled.";
            else
                ReturnOrder(*o, OrderCancelled, "Your commission was cancelled. Here are your materials and payment.");
        }
        SendBoard(player, error);
    }

    void HandleCommerce(Player* player, std::string const& text)
    {
        Fields const f = Split(text);
        std::string const& verb = f[0];
        for (char const* boardVerb : { "board", "search", "post", "accept", "drop", "complete", "cancel" })
            if (verb == boardVerb)
            {
                if (NearBoard(player))
                    HandleBoardCommand(player, f);
                return;
            }

        WorldObject* object = nullptr;
        Shop* shop = ViewedShop(player, &object);
        if (!shop)
            return;
        Shop& s = *shop;
        Listing* l = OwnedListing(s, Num(f, 1));
        std::string message;
        if (verb == "close")
        {
            SpeakTo(player, object, s.farewell);
            s_shopView.erase(player->GetGUID());
            return;
        }
        if (verb == "buy")
        {
            message = l ? Buy(player, s, *l, Num(f, 2), object) : "That listing is gone.";
            SendShop(player, message);
            return;
        }
        if (s.account != player->GetSession()->GetAccountId())
            return; // everything below is the owner's
        if (verb == "ledger")
            return SendLedger(player, s);
        if (verb == "stockable")
            return SendStockable(player, s);
        if (verb == "withdraw")
        {
            ShopAccount& account = s_shopAccounts[s.account];
            uint64 const room = MAX_MONEY_AMOUNT - std::min<uint64>(MAX_MONEY_AMOUNT, player->GetMoney());
            int32 const amount = int32(std::min<uint64>({ account.treasury, room, uint64(INT32_MAX) }));
            if (amount <= 0)
                message = "There is nothing you can take.";
            else
            {
                account.treasury -= amount;
                player->ModifyMoney(amount);
                CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
                SaveShopAccount(s.account, trans);
                player->SaveInventoryAndGoldToDB(trans);
                CharacterDatabase.CommitTransaction(trans);
            }
        }
        else if (verb == "unlockbank")
        {
            ShopAccount& account = s_shopAccounts[s.account];
            if (account.bankDeposit)
                message = "Your bank is already unlocked.";
            else if (!player->HasEnoughMoney(BankDepositPrice))
                message = "You don't have enough money.";
            else
            {
                player->ModifyMoney(-int32(BankDepositPrice));
                account.bankDeposit = true;
                CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
                SaveShopAccount(s.account, trans);
                player->SaveInventoryAndGoldToDB(trans);
                CharacterDatabase.CommitTransaction(trans);
                SendStockable(player, s);
            }
        }
        else if (verb == "deposit")
        {
            message = Deposit(player, s, f);
            if (message.empty())
                SendStockable(player, s);
        }
        else if (verb == "retrieve")
            message = l ? Retrieve(player, *l) : "That listing is gone.";
        else if (verb == "price" && l)
        {
            uint32 const bundle = Num(f, 2), price = Num(f, 3);
            if (!EsteriaHousing::ValidListing(bundle, l->item ? l->Stock() : bundle, sObjectMgr->GetItemTemplate(l->entry)->GetMaxStackSize(), price))
                message = "Check the price and the bundle size.";
            else
            {
                l->bundle = bundle;
                l->price = price;
                CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
                SaveListing(*l, trans);
                CharacterDatabase.CommitTransaction(trans);
            }
        }
        else if (verb == "publish" && l)
        {
            l->published = Num(f, 2) != 0;
            CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
            SaveListing(*l, trans);
            CharacterDatabase.CommitTransaction(trans);
        }
        else if (verb == "appearance")
            return SendCustomize(player, s);
        else if (verb == "race" && s.kind == ServiceMerchant)
        {
            if (!PlayableRace(uint8(Num(f, 1))))
                message = "That race is not available.";
            else
            {
                s.race = uint8(Num(f, 1)); s.sex = Num(f, 2) ? 1 : 0;
                s.lookHex = DefaultLookHex(s.race, s.sex); s.bodyHex.clear();
                CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
                SaveShop(s, trans);
                CharacterDatabase.CommitTransaction(trans);
                RespawnMerchant(player, s);
                return SendCustomize(player, s);
            }
        }
        else if (verb == "look" && s.kind == ServiceMerchant && f.size() >= 3)
            message = SaveLook(player, s, f[1], f[2]);
        else if (verb == "lookreset" && s.kind == ServiceMerchant)
        {
            RespawnMerchant(player, s); // the saved look comes back with the new NPC
            return;
        }
        else if (verb == "gear" && s.kind == ServiceMerchant)
            return SendGear(player, s);
        else if (verb == "equip" && s.kind == ServiceMerchant)
        {
            message = Equip(player, s, f);
            if (message.empty())
                return SendGear(player, s);
        }
        else if (verb == "unequip" && s.kind == ServiceMerchant)
        {
            message = Unequip(player, s, uint8(Num(f, 1)));
            if (message.empty())
            {
                RespawnMerchant(player, s);
                return SendGear(player, s);
            }
        }
        else if (verb == "setup" && f.size() >= 10)
        {
            std::string const name = Clean(f[1], 40), theme = Clean(f[2], 40);
            // every save renames a merchant onto a fresh entry and respawns it, so its name and title show at once, even
            // for a client that cached an older name under its current entry
            bool const named = true;
            bool const respawn = true;
            if (!name.empty())
                s.name = name;
            s.theme = theme;
            s.greeting = Clean(f[4], 200);
            s.thanks = Clean(f[5], 200);
            s.farewell = Clean(f[6], 200);
            s.sign = Clean(f[7], 40);
            s.symbol = uint8(std::min<uint32>(Num(f, 8), 15));
            s.border = uint8(std::min<uint32>(Num(f, 9), 3));
            if (f.size() > 10) // the name's height above a case's base, in yards (0 to 10)
                if (float const h = std::strtof(f[10].c_str(), nullptr); std::isfinite(h))
                    s.labelHeight = std::clamp(h, 0.0f, 10.0f);
            if (named)
            {
                if (uint32 const entry = NextMerchantEntry())
                    s.entry = entry;
                NameTemplate(s);
                // and tell everyone here the name at once, so even a client that cached this entry before shows the new one
                if (CreatureTemplate const* t = sObjectMgr->GetCreatureTemplate(s.entry))
                {
                    WorldPacket name = t->queryData;
                    player->GetMap()->DoForAllPlayers([&](Player* p) { p->SendDirectMessage(&name); });
                }
            }
            CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
            SaveShop(s, trans);
            CharacterDatabase.CommitTransaction(trans);
            if (respawn && s.kind == ServiceMerchant)
                RespawnMerchant(player, s);
            else if (respawn) // a case, shelf, rack, counter or sign: its label takes the new name
                if (Placed const* p = FindPlaced(s_houses[s.house], s.placed))
                {
                    DespawnShopLabel(player->GetMap(), s.placed);
                    SpawnShopLabel(player->GetMap(), *p);
                }
        }
        if (ViewedShop(player)) // Retrieve can erase what `l` pointed at; nothing below uses it
            SendShop(player, message);
    }

    bool OpenService(Player* player, WorldObject* object)
    {
        if (!s_config.enabled || !s_loaded || !s_hasUi.count(player->GetSession()->GetAccountId()))
            return false;
        uint64 placed = 0;
        for (auto const& [id, guid] : s_spawned[player->GetInstanceId()])
            if (guid == object->GetGUID())
                placed = id;
        if (auto label = s_labelPlaced.find(object->GetGUID()); label != s_labelPlaced.end()) // a shop's name, clicked
            placed = label->second;
        if (!placed)
            return false;
        if (object->GetEntry() == BoardGo)
        {
            s_boardView[player->GetGUID()] = { placed, object->GetGUID() };
            SendBoard(player);
            return true;
        }
        auto shop = s_shops.find(placed);
        if (shop == s_shops.end())
            return false;
        if (!MayEnter(player, s_houses[shop->second.house]))
        {
            SendCommerce(player, "note\tThe owner has closed this shop to you.");
            return true;
        }
        s_shopView[player->GetGUID()] = { placed, object->GetGUID() };
        SendShop(player);
        return true;
    }

    class npc_esteria_housing_merchant : public CreatureScript
    {
    public:
        npc_esteria_housing_merchant() : CreatureScript("npc_esteria_housing_merchant") { }
        bool OnGossipHello(Player* player, Creature* creature) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            ClearGossipMenuFor(player);
            if (OpenService(player, creature))
                return true;
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "This shop needs the Esteria housing client.", 0, 0);
            SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature);
            return true;
        }
    };

    class go_esteria_housing_service : public GameObjectScript
    {
    public:
        go_esteria_housing_service() : GameObjectScript("go_esteria_housing_service") { }
        bool OnGossipHello(Player* player, GameObject* go) override
        {
            std::lock_guard<std::recursive_mutex> guard(s_lock);
            ClearGossipMenuFor(player);
            if (OpenService(player, go))
                return true;
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "This needs the Esteria housing client.", 0, 0);
            SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, go->GetGUID());
            return true;
        }
    };
