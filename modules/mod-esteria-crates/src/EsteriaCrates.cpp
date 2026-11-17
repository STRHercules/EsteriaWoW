/*
 * Loot crates: server half of the EsteriaCrates addon (wowdecomp/Addons/EsteriaCrates).
 *
 * The addon talks over the addon channel like the other Esteria windows: an addon whisper to oneself, which reaches
 * OnPlayerBeforeSendChatMessage as LANG_ADDON. Every value the client sends is re-checked here; the client never
 * chooses a reward, a price or a roll.
 *
 *   client -> server  "ECRC\t<body>"      server -> client  "ECRS\t<body>"
 *
 * client -> server
 *   HI                                  the addon is loaded
 *   L                                   every crate on offer (LC..., LE)
 *   D:<crate>                           crate details (H, R..., RE)
 *   O:<crate>:<req>                     open one crate with one matching key
 *   B:<crate>:<qty>:<unitPrice>:<req>   buy keys for this crate at the price the client showed
 *   C:<crate>:<qty>:<unitPrice>:<req>   buy the crate itself, when its edition has a price
 *
 * server -> client
 *   OPEN:<crate>
 *   LC:<crate>:<key>:<keyPrice>:<cratePrice>:<crates>:<keys>:<pool>
 *   LE
 *   H:<crate>:<key>:<price>:<crates>:<keys>:<pool>:<total>:<rewards>:<maxBuy>:<cratePrice>
 *   R:<crate>:<idx>:<item>:<count>:<weight>:<rarity>:<known>
 *   RE:<crate>
 *   W:<req>:<crate>:<idx>:<item>:<count>:<where>      the committed result; where 0 bags, 1 mail, 2 storage,
 *                                                     3 mail because a Unique is already carried
 *   K:<req>:<crate>:<qty>:<copper>                    keys bought
 *   P:<req>:<crate>:<qty>:<copper>                    crates bought
 *   E:<req>:<code>                                    refused, nothing changed
 *
 * Before naming an item the server pushes its item query answer once per session, so the window never waits on the
 * client's item cache.
 *
 * An edition is a crate item pinned to one pool version; see data/sql/db-world/esteria_crates.sql.
 */
#include "CratePool.h"

#include "Chat.h"
#include "DatabaseEnv.h"
#include "Field.h"
#include "Item.h"
#include "ItemScript.h"
#include "Log.h"
#include "Mail.h"
#include "Opcodes.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "PlayerScript.h"
#include "Random.h"
#include "StringFormat.h"
#include "StringConvert.h"
#include "Tokenize.h"
#include "WorldPacket.h"
#include "WorldScript.h"
#include "WorldSession.h"

#include <cctype>
#include <chrono>
#include <deque>
#include <limits>
#include <mutex>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace
{
    constexpr char PREFIX_IN[] = "ECRC\t";
    constexpr size_t PREFIX_LEN = sizeof(PREFIX_IN) - 1;
    constexpr char PREFIX_OUT[] = "ECRS\t";
    constexpr char ITEM_SCRIPT[] = "item_esteria_crate";
    constexpr size_t REPLAY_DEPTH = 8;
    constexpr auto MIN_REQUEST_GAP = std::chrono::milliseconds(200);

    struct Reward
    {
        uint32 item;
        uint32 count;
        uint32 weight;
        uint8 rarity;
    };

    struct Edition
    {
        uint32 crate;
        uint32 key;
        uint32 pool;
        uint32 price; // copper per crate, 0 when crates are not sold
        std::vector<Reward> rewards;
        std::vector<uint32> weights;
        uint32 total;
    };

    struct Key
    {
        uint32 price;
        uint32 maxPerPurchase;
    };

    // Filled once in OnStartup, read-only afterwards.
    std::unordered_map<uint32, Edition> editions;
    std::unordered_map<uint32, Key> keys;

    struct Session
    {
        bool addon = false;
        std::chrono::steady_clock::time_point last;
        std::deque<std::pair<std::string, std::vector<std::string>>> replies;
        std::unordered_set<uint32> cached; // items whose query answer this session already received
    };

    std::mutex sessionLock;
    std::unordered_map<ObjectGuid, Session> sessions;

    void Send(Player* player, std::string const& body)
    {
        WorldPacket data;
        ChatHandler::BuildChatPacket(data, CHAT_MSG_WHISPER, LANG_ADDON, player, player, PREFIX_OUT + body);
        player->SendDirectMessage(&data);
    }

    bool ValidRequest(std::string_view req)
    {
        if (req.empty() || req.size() > 16)
            return false;
        for (char c : req)
            if (!std::isalnum(static_cast<unsigned char>(c)))
                return false;
        return true;
    }

    bool Knows(Player* player, ItemTemplate const* proto)
    {
        for (auto const& spell : proto->Spells)
            if (spell.SpellTrigger == ITEM_SPELLTRIGGER_LEARN_SPELL_ID && spell.SpellId > 0 &&
                player->HasSpell(spell.SpellId))
                return true;
        return false;
    }

    // Answers the client's item query before it has to ask, once per session per item.
    void PushItems(Player* player, std::vector<uint32> const& items)
    {
        std::vector<uint32> fresh;
        {
            std::lock_guard<std::mutex> guard(sessionLock);
            auto& cached = sessions[player->GetGUID()].cached;
            for (uint32 item : items)
                if (cached.insert(item).second)
                    fresh.push_back(item);
        }
        for (uint32 item : fresh)
        {
            WorldPacket query(CMSG_ITEM_QUERY_SINGLE, 4);
            query << item;
            player->GetSession()->HandleItemQuerySingleOpcode(query);
        }
    }

    void SendDetails(Player* player, Edition const& edition)
    {
        Key const& key = keys.at(edition.key);
        std::vector<uint32> items{ edition.crate, edition.key };
        for (Reward const& reward : edition.rewards)
            items.push_back(reward.item);
        PushItems(player, items);
        Send(player, Acore::StringFormat("H:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}", edition.crate, edition.key, key.price,
            player->GetItemCount(edition.crate), player->GetItemCount(edition.key), edition.pool, edition.total,
            edition.rewards.size(), key.maxPerPurchase, edition.price));
        for (size_t i = 0; i < edition.rewards.size(); ++i)
        {
            Reward const& reward = edition.rewards[i];
            Send(player, Acore::StringFormat("R:{}:{}:{}:{}:{}:{}:{}", edition.crate, i, reward.item, reward.count,
                reward.weight, reward.rarity, Knows(player, sObjectMgr->GetItemTemplate(reward.item)) ? 1 : 0));
        }
        Send(player, Acore::StringFormat("RE:{}", edition.crate));
    }

    void SendList(Player* player)
    {
        for (auto const& [crate, edition] : editions)
        {
            PushItems(player, { crate, edition.key });
            Send(player, Acore::StringFormat("LC:{}:{}:{}:{}:{}:{}:{}", crate, edition.key,
                keys.at(edition.key).price, edition.price, player->GetItemCount(crate),
                player->GetItemCount(edition.key), edition.pool));
        }
        Send(player, "LE");
    }

    // Replays the stored answer to a request already handled, so a resent packet never opens or buys twice.
    bool Replay(Player* player, std::string const& req)
    {
        std::vector<std::string> answer;
        {
            std::lock_guard<std::mutex> guard(sessionLock);
            for (auto const& [id, replies] : sessions[player->GetGUID()].replies)
                if (id == req)
                    answer = replies;
        }
        for (std::string const& reply : answer)
            Send(player, reply);
        return !answer.empty();
    }

    void Answer(Player* player, std::string const& req, std::string const& reply)
    {
        {
            std::lock_guard<std::mutex> guard(sessionLock);
            auto& replies = sessions[player->GetGUID()].replies;
            replies.emplace_back(req, std::vector<std::string>{ reply });
            if (replies.size() > REPLAY_DEPTH)
                replies.pop_front();
        }
        Send(player, reply);
    }

    void Refuse(Player* player, std::string const& req, char const* code)
    {
        // Refusals change nothing, so they are not stored: the same request may be retried once the cause is fixed.
        Send(player, Acore::StringFormat("E:{}:{}", req, code));
    }

    bool CanAct(Player* player)
    {
        return player->IsAlive() && !player->IsInCombat() && !player->GetDigitalInventory().Failed();
    }

    // Where a new item ended up. The values are also the `mailed` column and the W message's last field.
    enum class Delivered : uint8
    {
        Bags = 0,
        Mail = 1,
        Storage = 2,
        Unique = 3,  // mailed: the player already carries as many as the item allows
        Nowhere = 4
    };

    // Puts a new item in the bags, else in the player's Esteria (digital) storage, else, when allowed, in the mailbox.
    // An item the player may not carry more of (a Unique already owned) skips storage and waits in the mail.
    Delivered Deliver(Player* player, uint32 entry, uint32 count, bool mail, CharacterDatabaseTransaction trans)
    {
        ItemPosCountVec dest;
        InventoryResult const result = player->CanStoreNewItem(NULL_BAG, NULL_SLOT, dest, entry, count);
        if (result == EQUIP_ERR_OK)
        {
            Item* item = player->StoreNewItem(dest, entry, true, Item::GenerateItemRandomPropertyId(entry));
            player->SendNewItem(item, count, true, false);
            return Delivered::Bags;
        }
        bool const unique = result == EQUIP_ERR_CANT_CARRY_MORE_OF_THIS;
        if (unique && !mail)
            return Delivered::Nowhere;
        Item* item = Item::CreateItem(entry, count, player);
        if (!item)
            return Delivered::Nowhere;
        if (!unique && player->GetDigitalInventory().Store(item))
            return Delivered::Storage;
        if (!mail)
        {
            delete item;
            return Delivered::Nowhere;
        }
        MailDraft("Loot crate reward", unique
            ? "You already carry as many of this item as you may, so this one waits here until you use or remove one."
            : "Your bags and storage were full, so your crate reward was sent here.")
            .AddItem(item)
            .SendMailTo(trans, MailReceiver(player), MailSender(MAIL_NORMAL, 0, MAIL_STATIONERY_GM),
                MAIL_CHECK_MASK_COPIED);
        return unique ? Delivered::Unique : Delivered::Mail;
    }

    void Open(Player* player, Edition const& edition, std::string const& req)
    {
        if (!CanAct(player))
            return Refuse(player, req, "state");
        if (!player->GetItemCount(edition.crate))
            return Refuse(player, req, "nocrate");
        if (!player->GetItemCount(edition.key))
            return Refuse(player, req, "nokey");

        uint32 const roll = urand(1, edition.total);
        size_t const index = EsteriaCrates::Pick(edition.weights, roll);
        Reward const& reward = edition.rewards[index];

        // Consumption, the reward and the receipt commit together, so a crash leaves all of them or none.
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        player->DestroyItemCount(edition.crate, 1, true);
        player->DestroyItemCount(edition.key, 1, true);

        uint8 const where = uint8(Deliver(player, reward.item, reward.count, true, trans));

        trans->Append(Acore::StringFormat(
            "INSERT INTO `esteria_crate_opening` (`guid`, `account`, `request`, `crate`, `key_item`, `pool`, `reward`, "
            "`count`, `roll`, `mailed`) VALUES ({}, {}, '{}', {}, {}, {}, {}, {}, {}, {})",
            player->GetGUID().GetCounter(), player->GetSession()->GetAccountId(), req, edition.crate, edition.key,
            edition.pool, reward.item, reward.count, roll, where));
        player->SaveInventoryAndGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);

        LOG_INFO("module.crates", "{} opened crate {} (pool {}): roll {}/{} -> item {} x{} (delivery {})",
            player->GetName(), edition.crate, edition.pool, roll, edition.total, reward.item, reward.count, where);
        Answer(player, req, Acore::StringFormat("W:{}:{}:{}:{}:{}:{}", req, edition.crate, index, reward.item,
            reward.count, where));
        SendDetails(player, edition);
    }

    // Buys keys (crate = false) or the crate itself. The gold leaves the economy.
    void Buy(Player* player, Edition const& edition, bool crate, uint32 quantity, uint32 shownPrice,
        std::string const& req)
    {
        Key const& key = keys.at(edition.key);
        uint32 const entry = crate ? edition.crate : edition.key;
        uint32 const price = crate ? edition.price : key.price;
        if (!price)
            return Refuse(player, req, "notsold");
        if (!CanAct(player))
            return Refuse(player, req, "state");
        if (!quantity || quantity > key.maxPerPurchase)
            return Refuse(player, req, "quantity");
        if (shownPrice != price)
        {
            Refuse(player, req, "price");
            return SendDetails(player, edition);
        }

        uint64 const total = uint64(price) * quantity;
        if (total > uint64(std::numeric_limits<int32>::max()) || !player->HasEnoughMoney(uint32(total)))
            return Refuse(player, req, "money");

        // Purchases go to the bags or storage, never the mail: with both full nothing is charged.
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        if (Deliver(player, entry, quantity, false, trans) == Delivered::Nowhere)
            return Refuse(player, req, "bags");
        player->ModifyMoney(-int32(total));
        trans->Append(Acore::StringFormat(
            "INSERT INTO `esteria_crate_purchase` (`guid`, `account`, `request`, `item`, `quantity`, `unit_price`, "
            "`total`) VALUES ({}, {}, '{}', {}, {}, {}, {})",
            player->GetGUID().GetCounter(), player->GetSession()->GetAccountId(), req, entry, quantity, price, total));
        player->SaveInventoryAndGoldToDB(trans);
        CharacterDatabase.CommitTransaction(trans);

        LOG_INFO("module.crates", "{} bought {} x item {} for {} copper (destroyed)", player->GetName(), quantity,
            entry, total);
        Answer(player, req, Acore::StringFormat("{}:{}:{}:{}:{}", crate ? "P" : "K", req, edition.crate, quantity,
            total));
        SendDetails(player, edition);
    }

    void HandleMessage(Player* player, std::string const& body)
    {
        std::vector<std::string_view> args = Acore::Tokenize(body, ':', true);
        if (args.empty())
            return;

        if (args[0] == "HI")
        {
            std::lock_guard<std::mutex> guard(sessionLock);
            sessions[player->GetGUID()].addon = true;
            return;
        }
        if (args[0] == "L")
            return SendList(player);

        uint32 const crate = args.size() > 1 ? Acore::StringTo<uint32>(args[1]).value_or(0) : 0;
        auto const found = editions.find(crate);
        if (found == editions.end())
            return;
        Edition const& edition = found->second;

        if (args[0] == "D" && args.size() == 2)
            return SendDetails(player, edition);

        bool const open = args[0] == "O" && args.size() == 3;
        bool const buy = (args[0] == "B" || args[0] == "C") && args.size() == 5;
        if (!open && !buy)
            return;

        std::string const req(args.back());
        if (!ValidRequest(req) || Replay(player, req))
            return;

        {
            std::lock_guard<std::mutex> guard(sessionLock);
            auto& last = sessions[player->GetGUID()].last;
            auto const now = std::chrono::steady_clock::now();
            if (now - last < MIN_REQUEST_GAP)
                return Refuse(player, req, "busy");
            last = now;
        }

        if (open)
            return Open(player, edition, req);
        Buy(player, edition, args[0] == "C", Acore::StringTo<uint32>(args[2]).value_or(0),
            Acore::StringTo<uint32>(args[3]).value_or(0), req);
    }

    class CratesWorld final : public WorldScript
    {
    public:
        CratesWorld() : WorldScript("EsteriaCratesWorld", { WORLDHOOK_ON_STARTUP }) { }

        void OnStartup() override
        {
            if (QueryResult result = WorldDatabase.Query(
                "SELECT `item`, `price`, `max_per_purchase` FROM `esteria_crate_key`"))
            {
                do
                {
                    Field* fields = result->Fetch();
                    uint32 const item = fields[0].Get<uint32>();
                    ItemTemplate const* proto = sObjectMgr->GetItemTemplate(item);
                    uint32 const price = fields[1].Get<uint32>();
                    uint32 const max = fields[2].Get<uint32>();
                    if (!proto || !price || !max || proto->Bonding != NO_BIND || max > proto->GetMaxStackSize())
                    {
                        LOG_ERROR("module.crates", "Key {} rejected: missing template, zero price or limit, bound, "
                            "or limit above stack size", item);
                        continue;
                    }
                    keys[item] = { price, max };
                } while (result->NextRow());
            }

            std::unordered_map<uint32, std::vector<Reward>> pools;
            if (QueryResult result = WorldDatabase.Query(
                "SELECT `pool`, `item`, `count`, `weight`, `rarity` FROM `esteria_crate_reward` "
                "ORDER BY `pool`, `idx`"))
            {
                do
                {
                    Field* fields = result->Fetch();
                    pools[fields[0].Get<uint32>()].push_back({ fields[1].Get<uint32>(),
                        fields[2].Get<uint32>(), fields[3].Get<uint32>(), fields[4].Get<uint8>() });
                } while (result->NextRow());
            }

            uint32 const script = sObjectMgr->GetScriptId(ITEM_SCRIPT);
            if (QueryResult result = WorldDatabase.Query(
                "SELECT `crate`, `key_item`, `pool`, `price` FROM `esteria_crate_edition` WHERE `enabled` = 1"))
            {
                do
                {
                    Field* fields = result->Fetch();
                    Edition edition{ fields[0].Get<uint32>(), fields[1].Get<uint32>(), fields[2].Get<uint32>(),
                        fields[3].Get<uint32>(), {}, {}, 0 };
                    ItemTemplate const* crate = sObjectMgr->GetItemTemplate(edition.crate);
                    auto const pool = pools.find(edition.pool);
                    bool valid = crate && crate->ScriptId == script && keys.contains(edition.key) &&
                        pool != pools.end();
                    if (valid)
                    {
                        edition.rewards = pool->second;
                        for (Reward const& reward : edition.rewards)
                        {
                            ItemTemplate const* proto = sObjectMgr->GetItemTemplate(reward.item);
                            valid = valid && proto && reward.count && reward.count <= proto->GetMaxStackSize();
                            edition.weights.push_back(reward.weight);
                        }
                        edition.total = EsteriaCrates::TotalWeight(edition.weights);
                        valid = valid && edition.total;
                    }
                    if (!valid)
                    {
                        LOG_ERROR("module.crates", "Crate edition {} (pool {}) rejected: check the crate script, "
                            "key, reward items, counts and weights", edition.crate, edition.pool);
                        continue;
                    }
                    editions[edition.crate] = std::move(edition);
                } while (result->NextRow());
            }
            LOG_INFO("module.crates", "Loaded {} crate editions and {} key types", editions.size(), keys.size());
        }
    };

    class CratesPlayer final : public PlayerScript
    {
    public:
        CratesPlayer() : PlayerScript("EsteriaCratesPlayer", {
            PLAYERHOOK_ON_BEFORE_SEND_CHAT_MESSAGE,
            PLAYERHOOK_ON_LOGOUT
        }) { }

        void OnPlayerBeforeSendChatMessage(Player* player, uint32& /*type*/, uint32& lang, std::string& msg) override
        {
            if (!player || lang != LANG_ADDON || msg.size() <= PREFIX_LEN ||
                msg.compare(0, PREFIX_LEN, PREFIX_IN) != 0)
                return;
            HandleMessage(player, msg.substr(PREFIX_LEN));
        }

        void OnPlayerLogout(Player* player) override
        {
            std::lock_guard<std::mutex> guard(sessionLock);
            sessions.erase(player->GetGUID());
        }
    };

    class CrateItem final : public ItemScript
    {
    public:
        CrateItem() : ItemScript(ITEM_SCRIPT) { }

        bool OnUse(Player* player, Item* item, SpellCastTargets const& /*targets*/) override
        {
            // Using a crate never consumes it; it only opens the window. Release the client's item lock.
            player->SendEquipError(EQUIP_ERR_NONE, item, nullptr);
            auto const found = editions.find(item->GetEntry());
            if (found == editions.end())
            {
                player->SendSystemMessage("This crate cannot be opened right now.");
                return true;
            }

            bool addon;
            {
                std::lock_guard<std::mutex> guard(sessionLock);
                addon = sessions[player->GetGUID()].addon;
            }
            if (!addon)
            {
                player->SendSystemMessage("Opening crates needs the EsteriaCrates interface, which is not loaded.");
                return true;
            }

            Send(player, Acore::StringFormat("OPEN:{}", found->first));
            SendDetails(player, found->second);
            return true;
        }
    };
}

void AddSC_esteria_crates()
{
    new CratesWorld();
    new CratesPlayer();
    new CrateItem();
}
