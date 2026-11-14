/* Esteria backpack appearance tokens and the Cosmetics collection's server transport. */
#include "Transmogrification.h"
#include "CosmeticsPolicy.h"
#include "DatabaseEnv.h"
#include "ObjectMgr.h"
#include "SpellMgr.h"
#include "StringConvert.h"
#include "Tokenize.h"
#include "WorldPacket.h"
#include "WorldSession.h"

#include <chrono>
#include <map>
#include <mutex>
#include <unordered_map>

namespace
{
    constexpr char PREFIX[] = "ESTCOS\t";
    constexpr char ITEM_SCRIPT[] = "item_esteria_backpack_appearance";
    std::map<uint32, uint32> appearances; // source cloak -> consumable token, immutable after startup
    std::map<uint32, uint32> tokens;
    struct RequestWindow
    {
        std::chrono::steady_clock::time_point start = std::chrono::steady_clock::now();
        unsigned count = 0;
    };
    std::mutex requestLock;
    std::recursive_mutex learningLock;
    std::unordered_map<ObjectGuid, RequestWindow> requests;

    void Send(Player* player, std::string const& body)
    {
        WorldPacket packet;
        ChatHandler::BuildChatPacket(packet, CHAT_MSG_WHISPER, LANG_ADDON, player, player, PREFIX + body);
        player->SendDirectMessage(&packet);
    }

    bool Knows(Player* player, uint32 source)
    {
        std::lock_guard<std::recursive_mutex> guard(learningLock);
        auto found = sTransmogrification->collectionCache.find(player->GetSession()->GetAccountId());
        return found != sTransmogrification->collectionCache.end() && found->second.contains(source);
    }

    uint32 Selected(Player* player)
    {
        Item* cloak = player->GetItemByPos(INVENTORY_SLOT_BAG_0, EQUIPMENT_SLOT_BACK);
        uint32 source = cloak ? sTransmogrification->GetFakeEntry(cloak->GetGUID()) : 0;
        return appearances.contains(source) ? source : 0;
    }

    void SendCollection(Player* player)
    {
        Send(player, "reset");
        std::string chunk;
        for (auto const& [source, token] : appearances)
        {
            if (!Knows(player, source))
                continue;
            std::string id = std::to_string(source);
            if (chunk.size() + id.size() + 1 > 180)
            {
                Send(player, "known\t" + chunk);
                chunk.clear();
            }
            chunk += (chunk.empty() ? "" : ",") + id;
        }
        if (!chunk.empty())
            Send(player, "known\t" + chunk);
        Send(player, "selected\t" + std::to_string(Selected(player)));
        Send(player, "done");
    }

    bool AllowRequest(Player* player)
    {
        auto now = std::chrono::steady_clock::now();
        std::lock_guard<std::mutex> guard(requestLock);
        auto& window = requests[player->GetGUID()];
        if (now - window.start >= std::chrono::seconds(1))
        {
            window.start = now;
            window.count = 0;
        }
        return ++window.count <= 8;
    }

    class CosmeticsWorld final : public WorldScript
    {
    public:
        CosmeticsWorld() : WorldScript("EsteriaCosmeticsWorld") { }

        void OnStartup() override
        {
            uint32 script = sObjectMgr->GetScriptId(ITEM_SCRIPT);
            auto* statement = WorldDatabase.GetPreparedStatement(WORLD_SEL_ESTERIA_BACKPACK_APPEARANCES);
            if (PreparedQueryResult result = WorldDatabase.Query(statement))
            {
                do
                {
                    uint32 source = (*result)[0].Get<uint32>();
                    uint32 token = (*result)[1].Get<uint32>();
                    auto const* cloak = sObjectMgr->GetItemTemplate(source);
                    auto const* item = sObjectMgr->GetItemTemplate(token);
                    bool valid = source != token && cloak && item && script &&
                        cloak->Class == ITEM_CLASS_ARMOR && cloak->InventoryType == INVTYPE_CLOAK &&
                        item->InventoryType == INVTYPE_NON_EQUIP && item->ScriptId == script &&
                        item->Spells[0].SpellId > 0 && item->Spells[0].SpellTrigger == ITEM_SPELLTRIGGER_ON_USE &&
                        sSpellMgr->GetSpellInfo(item->Spells[0].SpellId) &&
                        !appearances.contains(source) && !tokens.contains(token);
                    if (!valid)
                    {
                        LOG_ERROR("module.cosmetics", "Rejected backpack source {} / token {}", source, token);
                        continue;
                    }
                    appearances.emplace(source, token);
                    tokens.emplace(token, source);
                } while (result->NextRow());
            }
            LOG_INFO("module.cosmetics", "Loaded {} collectible backpack appearances", appearances.size());
        }
    };

    class CosmeticsPlayer final : public PlayerScript
    {
    public:
        CosmeticsPlayer() : PlayerScript("EsteriaCosmeticsPlayer", {
            PLAYERHOOK_CAN_PLAYER_USE_PRIVATE_CHAT, PLAYERHOOK_ON_LOGOUT }) { }

        bool OnPlayerCanUseChat(Player* player, uint32 type, uint32 language, std::string& message,
            Player* receiver) override
        {
            if (language != LANG_ADDON || type != CHAT_MSG_WHISPER || receiver != player ||
                message.compare(0, sizeof(PREFIX) - 1, PREFIX))
                return true;
            if (message.size() > 64 || !AllowRequest(player))
                return false;
            auto fields = Acore::Tokenize(std::string_view(message).substr(sizeof(PREFIX) - 1), '\t', true);
            if (fields.size() == 1 && fields[0] == "sync")
                SendCollection(player);
            else if (fields.size() == 2 && fields[0] == "apply")
            {
                auto source = Acore::StringTo<uint32>(fields[1]);
                if (!source || (*source && (!appearances.contains(*source) || !Knows(player, *source))))
                    Send(player, "err\tYou have not collected that backpack.");
                else
                {
                    TransmogClient_ApplyAppearance(player, EQUIPMENT_SLOT_BACK, *source);
                    if (Selected(player) != *source)
                        Send(player, "err\tThe cloak appearance could not be changed. "
                            "Check your equipped cloak and transmog requirements.");
                    Send(player, "selected\t" + std::to_string(Selected(player)));
                }
            }
            return false;
        }

        void OnPlayerLogout(Player* player) override
        {
            std::lock_guard<std::mutex> guard(requestLock);
            requests.erase(player->GetGUID());
        }
    };

    class BackpackToken final : public ItemScript
    {
    public:
        BackpackToken() : ItemScript(ITEM_SCRIPT) { }

        bool OnUse(Player* player, Item* item, SpellCastTargets const&) override
        {
            // Serialize same-account uses across map workers through commit and cache publication.
            std::lock_guard<std::recursive_mutex> guard(learningLock);
            auto found = item ? tokens.find(item->GetEntry()) : tokens.end();
            bool valid = player && player->GetSession() && item && found != tokens.end() &&
                item->GetOwnerGUID() == player->GetGUID() && item->GetCount() &&
                player->IsAlive() && !player->IsInCombat() &&
                !player->GetDigitalInventory().Failed() &&
                sTransmogrification->IsEnabled() && sTransmogrification->GetUseCollectionSystem();
            uint32 source = found != tokens.end() ? found->second : 0;
            auto transaction = CharacterDatabase.BeginTransaction();
            auto result = EsteriaCosmetics::Learn(valid, valid && Knows(player, source), [&]
            {
                auto* statement = CharacterDatabase.GetPreparedStatement(CHAR_INS_ESTERIA_BACKPACK_APPEARANCE);
                statement->SetData(0, player->GetSession()->GetAccountId());
                statement->SetData(1, source);
                transaction->Append(statement);
                uint32 count = 1;
                player->DestroyItemCount(item, count, true);
            }, [&]
            {
                return player->GetDigitalInventory().Persist(transaction);
            }, [&]
            {
                sTransmogrification->AddCollectedAppearance(player->GetSession()->GetAccountId(), source);
                player->SendSystemMessage("Backpack appearance added to your account collection.");
                SendCollection(player);
            });
            if (player && result == EsteriaCosmetics::LearnResult::AlreadyKnown)
                player->SendSystemMessage("You already know this backpack appearance. The item was not consumed.");
            else if (player && result == EsteriaCosmetics::LearnResult::Invalid)
                player->SendSystemMessage("This appearance cannot be learned right now. The item was not consumed.");
            if (player && (result == EsteriaCosmetics::LearnResult::Invalid ||
                result == EsteriaCosmetics::LearnResult::AlreadyKnown) && item)
                player->SendEquipError(EQUIP_ERR_NONE, item, nullptr);
            return true;
        }
    };
}

void AddSC_esteria_cosmetics()
{
    new CosmeticsWorld();
    new CosmeticsPlayer();
    new BackpackToken();
}

bool IsEsteriaBackpackAppearance(uint32 entry)
{
    return appearances.contains(entry);
}
