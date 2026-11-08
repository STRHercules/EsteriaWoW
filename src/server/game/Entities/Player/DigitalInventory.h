/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under GNU AGPL v3 license.
 */

#ifndef ESTERIA_DIGITAL_INVENTORY_H
#define ESTERIA_DIGITAL_INVENTORY_H

#include "DatabaseEnvFwd.h"
#include "Define.h"
#include <chrono>
#include <map>
#include <string>
#include <vector>

class Item;
class Player;
class WorldPacket;

// These are virtual locations. Never return these items from slot-based inventory APIs.
class AC_GAME_API DigitalInventory
{
public:
    enum Scope : uint8
    {
        Carried, Bank
    };

    enum Action : uint8
    {
        Browse, Deposit, DepositAll, Withdraw, Split, Merge, Expand, Favorite, Activate, Use, Equip, Sell, SetTag, Unlock
    };

    // Guild bank (scope 2): tab sizes, expansion and prices ride on the same opcode as inventory snapshots.
    static void HandleGuild(Player& owner, WorldPacket& packet);

    explicit DigitalInventory(Player& owner, Scope scope = Carried) : _owner(owner), _scope(scope) { }
    ~DigitalInventory();
    static void LoadConfig();
    void Load(PreparedQueryResult metadata, PreparedQueryResult items);
    void Save(CharacterDatabaseTransaction trans);
    void Handle(WorldPacket& packet);
    void Update(uint32 diff);
    void ScheduleDeposit() { _scan = true; }
    uint32 Count(uint32 entry, Item const* skip = nullptr) const;
    uint32 CountLimit(uint32 category, Item const* skip) const;
    bool HasTool(uint32 category) const;
    uint32 Consume(uint32 entry, uint32 count);
    bool Failed() const { return _failed; }
    // Account bank only: lazy synchronous load, and moving items out of the stock bank slots.
    void LoadBank();
    bool MigrateLegacyBank();
    bool Unlocked() const { return _unlocked; }
    // Player shops: what is held here, and taking one out (it leaves with its whole virtual stack; the player save persists it).
    std::vector<Item*> Items() const;
    Item* TakeForShop(uint32 guid);

private:
    struct StoredItem
    {
        Item* item;
        bool favorite = false;
        bool dirty = true;
        std::string tag;
        bool split = false;
    };

    bool CanDeposit(Item const* item) const;
    bool DepositItem(Item* item);
    Item* WithdrawItem(uint32 guid);
    bool Persist();
    bool CanAct() const;
    void Changed();
    void Send(uint32 request, uint8 status, std::string const& message);
    void MergeStacks(bool manual);
    bool DepositFrom(uint32 guid);
    bool WithdrawTo(uint32 guid);
    uint32 UpgradePrice() const;
    uint32 UpgradeSlots() const;
    Item* CloneStack(Item* source, uint32 count);
    void PerformItemAction(uint8 action, Item* item, uint64 target);

    // This reference points only to the containing Player, never to another player's lifetime.
    Player& _owner;
    Scope _scope;
    std::map<uint32, StoredItem> _items;
    std::vector<Item*> _deleted;
    std::vector<uint32> _removedInventory;
    std::vector<uint32> _removedStorage;
    std::map<uint32, uint32> _pinned;
    uint32 _capacity = 256;
    uint32 _revision = 1;
    uint32 _elapsed = 0;
    uint32 _offset = 0;
    uint32 _pageSize = 20;
    uint32 _lastRequest = 0;
    uint32 _requestsInWindow = 0;
    std::chrono::steady_clock::time_point _requestWindow = std::chrono::steady_clock::now();
    uint8 _category = 0;
    uint8 _sort = 0;
    std::string _search;
    bool _loaded = false;
    bool _active = false;
    bool _dirty = false;
    bool _scan = false;
    bool _failed = false;
    bool _unlocked = false;
    bool _bankLoadAttempted = false;
};

#endif
