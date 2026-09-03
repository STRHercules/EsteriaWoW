/*
 * Credits: silviu20092
 */

#ifndef _IMPROVED_BANK_H_
#define _IMPROVED_BANK_H_

#include <string>
#include <vector>
#include "SharedDefines.h"
#include "Player.h"

class ImprovedBank
{
public:
    enum PagedDataType
    {
        PAGED_DATA_TYPE_DEPOSIT_ALL,
        PAGED_DATA_TYPE_WITHDRAW_ALL,
        PAGED_DATA_TYPE_DEPOSIT_CLASS,
        PAGED_DATA_TYPE_DEPOSIT_SUBCLASS,
        PAGED_DATA_TYPE_WITHDRAW_CLASS,
        PAGED_DATA_TYPE_WITHDRAW_SUBCLASS,
        PAGED_DATA_TYPE_DEPOSIT_CATEGORIZED,
        PAGED_DATA_TYPE_WITHDRAW_CATEGORIZED,
        MAX_PAGED_DATA_TYPE
    };

    enum IdentifierType
    {
        BASE_IDENTIFIER,
        ITEM_IDENTIFIER
    };

    struct BaseIdentifier
    {
        uint32 id;
        std::string name;
        std::string uiName;

        BaseIdentifier() : id(0) {}

        virtual IdentifierType GetType() const
        {
            return BASE_IDENTIFIER;
        }
    };

    struct ItemIdentifier : public BaseIdentifier
    {
        uint32 entry;
        uint32 count;
        ObjectGuid guid;

        // item specific properties, used for withdraw
        int32 duration;
        std::string charges;
        uint32 flags;
        std::string enchants;
        int32 randomPropertyId;
        uint32 durability;
        uint32 depositTime;
        uint32 creatorGuid;
        uint32 giftCreatorGuid;

        // deposit info, for warnings
        bool tradeable;

        virtual IdentifierType GetType() const
        {
            return ITEM_IDENTIFIER;
        }
    };
    typedef std::vector<BaseIdentifier*> IdentifierContainer;

    struct PagedData
    {
        static constexpr int PAGE_SIZE = 12;
        uint32 totalPages = 0;
        uint32 currentPage = 0;
        IdentifierContainer data;
        PagedDataType type = MAX_PAGED_DATA_TYPE;
        uint32 itemClass = 0;
        uint32 itemSubClass = 0;

        void Reset();
        void CalculateTotals();
        void SortAndCalculateTotals();
        bool IsEmpty() const;

        const BaseIdentifier* FindIdentifierById(uint32 id) const;
    };
    typedef std::unordered_map<uint32, PagedData> PagedDataMap;

    struct ClassifiedItem
    {
        uint32 id; // either class or subclass ID
        std::string name; // class or subclass name
        std::vector<ClassifiedItem> subclasses;
    };
private:
    ImprovedBank();
    ~ImprovedBank();

    bool accountWide;
    bool searchBank;
    bool showDepositReagents;
    bool depositReagentsSearchBank;
    bool categorizedItemMenuDeposit;
    bool categorizedItemMenuWithdraw;
    std::set<int32> blacklistedSubclasses;

    std::vector<ClassifiedItem> itemClasses;

    PagedDataMap playerPagedData;

    static bool CompareIdentifier(const BaseIdentifier* a, const BaseIdentifier* b);

    std::string ItemIcon(uint32 entry, uint32 width, uint32 height, int x, int y) const;
    std::string ItemNameWithLocale(const Player* player, const ItemTemplate* itemTemplate, int32 randomPropertyId) const;
    std::string ItemLink(const Player* player, const ItemTemplate* itemTemplate, int32 randomPropertyId) const;

    void AddDepositItem(const Player* player, const Item* item, PagedData& pagedData, const std::string& from) const;
    void AddDepositItemToDatabase(const Player* player, const Item* item) const;
    void RemoveFromPagedData(uint32 id, PagedData& pagedData);
    void RemoveItemFromDatabase(uint32 id);

    bool DepositItem(ObjectGuid itemGuid, Player* player, uint32* count = nullptr);
    bool IsReagent(const Item* item) const;

    std::string GetItemCharges(const Item* item) const;
    std::string GetItemEnchantments(const Item* item) const;

    Item* CreateItem(Player* player, ItemPosCountVec const& dest, uint32 itemEntry, bool update, int32 randomPropertyId,
        uint32 duration, const std::string& charges, uint32 flags, const std::string& enchants, uint32 durability,
        uint32 creatorGuid, uint32 giftCreatorGuid);
    bool LoadDataIntoItemFields(Item* item, std::string const& data, uint32 startOffset, uint32 count);

    void BuildItemCatalogueFromInventory(const Player* player, PagedData& pagedData);
    void BuildItemClassesCatalogue(const Player* player, PagedData& pagedData, const std::vector<ClassifiedItem>& classifiedItems);
    void BuildItemCatalogueForDeposit(const Player* player, PagedData& pagedData, uint32 id);
    void BuildItemCatalogueForWithdraw(const Player* player, PagedData& pagedData, uint32 id);

    bool _AddPagedData(Player* player, const PagedData& pagedData, uint32 page) const;
    void NoPagedData(Player* player, const PagedData& pagedData) const;

    const ClassifiedItem* FindItemClass(uint32 id) const;
public:
    static ImprovedBank* instance();

    void SetAccountWide(bool value) { accountWide = value; }
    void SetSearchBank(bool value) { searchBank = value; }
    void SetShowDepositReagents(bool value) { showDepositReagents = value; }
    void SetDepositReagentsSearchBank(bool value) { depositReagentsSearchBank = value; }
    bool GetAccountWide() { return accountWide; }
    bool GetSearchBank() { return searchBank; }
    bool GetShowDepositReagents() { return showDepositReagents; }
    bool GetDepositReagentsSearchBank() { return depositReagentsSearchBank; }
    void SetBlacklistedSubclasses(const std::string& subclasses);
    bool IsBlacklistedSubclass(int32 subclass) const;
    void SetCategorizedItemMenuDeposit(bool value) { categorizedItemMenuDeposit = value; }
    bool GetCategorizedItemMenuDeposit() const { return categorizedItemMenuDeposit; }
    void SetCategorizedItemMenuWithdraw(bool value) { categorizedItemMenuWithdraw = value; }
    bool GetCategorizedItemMenuWithdraw() const { return categorizedItemMenuWithdraw; }

    std::string ItemIcon(uint32 entry) const;

    bool DepositItem(uint32 id, Player* player, const PagedData& pagedData);

    void BuildWithdrawItemCatalogue(const Player* player, PagedData& pagedData);
    void BuildWithdrawItemCatalogue(const Player* player);
    bool WithdrawItem(uint32 id, Player* player, PagedData& pagedData);

    void BuildDepositItemCatalogue(const Player* player);
    void BuildItemSubClassesCatalogue(const Player* player, PagedData& pagedData, PagedDataType type, uint32 id);

    void DepositAllReagents(Player* player, uint32* totalCount);

    PagedData& GetPagedData(const Player* player);

    bool AddPagedData(Player* player, Creature* creature, uint32 page);
    bool TakePagedDataAction(Player* player, Creature* creature, uint32 action);
};

#define sImprovedBank ImprovedBank::instance()

#endif
