/*
 * mod-wxl-dbc — registry mapping base DBC filenames to store injectors.
 */

#include "WxlDbcRegistry.h"

#include "WxlDbcInject.h"
#include "DBCStores.h"
#include "DBCStructure.h"
#include "Log.h"

#include <cctype>
#include <unordered_map>

// Loaded in DBCStores.cpp but not declared in DBCStores.h on all cores.
extern DBCStorage<LightEntry> sLightStore;
extern DBCStorage<MapDifficultyEntry> sMapDifficultyStore;
extern DBCStorage<PvPDifficultyEntry> sPvPDifficultyStore;
extern DBCStorage<SkillRaceClassInfoEntry> sSkillRaceClassInfoStore;
extern DBCStorage<TransportAnimationEntry> sTransportAnimationStore;
extern DBCStorage<TransportRotationEntry> sTransportRotationStore;
extern DBCStorage<WorldMapAreaEntry> sWorldMapAreaStore;

namespace ModWxlDbc
{
    namespace
    {
        std::unordered_map<std::string, ContinuationInjector> sRegistry;
        bool sInitialized = false;

        std::string NormalizeKey(std::string value)
        {
            for (char& c : value)
                c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
            return value;
        }

        template<typename T>
        void RegisterStore(char const* baseDbcFile, DBCStorage<T>& store)
        {
            sRegistry[NormalizeKey(baseDbcFile)] = [&store](char const* path) -> uint32
            {
                return InjectContinuationFile(store, path, store.GetFormat());
            };
        }
    }

    void InitDbcRegistry()
    {
        if (sInitialized)
            return;

        sInitialized = true;

#define WXL_DBC(store, file) RegisterStore(file, store)

        WXL_DBC(sAreaTableStore, "AreaTable.dbc");
        WXL_DBC(sAchievementStore, "Achievement.dbc");
        WXL_DBC(sAchievementCategoryStore, "Achievement_Category.dbc");
        WXL_DBC(sAchievementCriteriaStore, "Achievement_Criteria.dbc");
        WXL_DBC(sAreaGroupStore, "AreaGroup.dbc");
        WXL_DBC(sAreaPOIStore, "AreaPOI.dbc");
        WXL_DBC(sAuctionHouseStore, "AuctionHouse.dbc");
        WXL_DBC(sBankBagSlotPricesStore, "BankBagSlotPrices.dbc");
        WXL_DBC(sBattlemasterListStore, "BattlemasterList.dbc");
        WXL_DBC(sBarberShopStyleStore, "BarberShopStyle.dbc");
        WXL_DBC(sCharStartOutfitStore, "CharStartOutfit.dbc");
        WXL_DBC(sCharSectionsStore, "CharSections.dbc");
        WXL_DBC(sCharTitlesStore, "CharTitles.dbc");
        WXL_DBC(sChatChannelsStore, "ChatChannels.dbc");
        WXL_DBC(sChrClassesStore, "ChrClasses.dbc");
        WXL_DBC(sChrRacesStore, "ChrRaces.dbc");
        WXL_DBC(sCinematicCameraStore, "CinematicCamera.dbc");
        WXL_DBC(sCinematicSequencesStore, "CinematicSequences.dbc");
        WXL_DBC(sCreatureDisplayInfoStore, "CreatureDisplayInfo.dbc");
        WXL_DBC(sCreatureDisplayInfoExtraStore, "CreatureDisplayInfoExtra.dbc");
        WXL_DBC(sCreatureFamilyStore, "CreatureFamily.dbc");
        WXL_DBC(sCreatureModelDataStore, "CreatureModelData.dbc");
        WXL_DBC(sCreatureSpellDataStore, "CreatureSpellData.dbc");
        WXL_DBC(sCreatureTypeStore, "CreatureType.dbc");
        WXL_DBC(sCurrencyTypesStore, "CurrencyTypes.dbc");
        WXL_DBC(sDestructibleModelDataStore, "DestructibleModelData.dbc");
        WXL_DBC(sDungeonEncounterStore, "DungeonEncounter.dbc");
        WXL_DBC(sDurabilityCostsStore, "DurabilityCosts.dbc");
        WXL_DBC(sDurabilityQualityStore, "DurabilityQuality.dbc");
        WXL_DBC(sEmotesStore, "Emotes.dbc");
        WXL_DBC(sEmotesTextStore, "EmotesText.dbc");
        WXL_DBC(sEmotesTextSoundStore, "EmotesTextSound.dbc");
        WXL_DBC(sFactionStore, "Faction.dbc");
        WXL_DBC(sFactionTemplateStore, "FactionTemplate.dbc");
        WXL_DBC(sGameObjectArtKitStore, "GameObjectArtKit.dbc");
        WXL_DBC(sGameObjectDisplayInfoStore, "GameObjectDisplayInfo.dbc");
        WXL_DBC(sGemPropertiesStore, "GemProperties.dbc");
        WXL_DBC(sGlyphPropertiesStore, "GlyphProperties.dbc");
        WXL_DBC(sGlyphSlotStore, "GlyphSlot.dbc");
        WXL_DBC(sGtBarberShopCostBaseStore, "gtBarberShopCostBase.dbc");
        WXL_DBC(sGtCombatRatingsStore, "gtCombatRatings.dbc");
        WXL_DBC(sGtChanceToMeleeCritBaseStore, "gtChanceToMeleeCritBase.dbc");
        WXL_DBC(sGtChanceToMeleeCritStore, "gtChanceToMeleeCrit.dbc");
        WXL_DBC(sGtChanceToSpellCritBaseStore, "gtChanceToSpellCritBase.dbc");
        WXL_DBC(sGtChanceToSpellCritStore, "gtChanceToSpellCrit.dbc");
        WXL_DBC(sGtNPCManaCostScalerStore, "gtNPCManaCostScaler.dbc");
        WXL_DBC(sGtOCTClassCombatRatingScalarStore, "gtOCTClassCombatRatingScalar.dbc");
        WXL_DBC(sGtOCTRegenHPStore, "gtOCTRegenHP.dbc");
        WXL_DBC(sGtRegenHPPerSptStore, "gtRegenHPPerSpt.dbc");
        WXL_DBC(sGtRegenMPPerSptStore, "gtRegenMPPerSpt.dbc");
        WXL_DBC(sHolidaysStore, "Holidays.dbc");
        WXL_DBC(sItemStore, "Item.dbc");
        WXL_DBC(sItemBagFamilyStore, "ItemBagFamily.dbc");
        WXL_DBC(sItemDisplayInfoStore, "ItemDisplayInfo.dbc");
        WXL_DBC(sItemExtendedCostStore, "ItemExtendedCost.dbc");
        WXL_DBC(sItemLimitCategoryStore, "ItemLimitCategory.dbc");
        WXL_DBC(sItemRandomPropertiesStore, "ItemRandomProperties.dbc");
        WXL_DBC(sItemRandomSuffixStore, "ItemRandomSuffix.dbc");
        WXL_DBC(sItemSetStore, "ItemSet.dbc");
        WXL_DBC(sLFGDungeonStore, "LFGDungeons.dbc");
        WXL_DBC(sLightStore, "Light.dbc");
        WXL_DBC(sLiquidTypeStore, "LiquidType.dbc");
        WXL_DBC(sLockStore, "Lock.dbc");
        WXL_DBC(sMailTemplateStore, "MailTemplate.dbc");
        WXL_DBC(sMapStore, "Map.dbc");
        WXL_DBC(sMapDifficultyStore, "MapDifficulty.dbc");
        WXL_DBC(sMovieStore, "Movie.dbc");
        WXL_DBC(sNamesReservedStore, "NamesReserved.dbc");
        WXL_DBC(sNamesProfanityStore, "NamesProfanity.dbc");
        WXL_DBC(sOverrideSpellDataStore, "OverrideSpellData.dbc");
        WXL_DBC(sPowerDisplayStore, "PowerDisplay.dbc");
        WXL_DBC(sPvPDifficultyStore, "PvpDifficulty.dbc");
        WXL_DBC(sQuestXPStore, "QuestXP.dbc");
        WXL_DBC(sQuestFactionRewardStore, "QuestFactionReward.dbc");
        WXL_DBC(sQuestSortStore, "QuestSort.dbc");
        WXL_DBC(sRandomPropertiesPointsStore, "RandPropPoints.dbc");
        WXL_DBC(sScalingStatDistributionStore, "ScalingStatDistribution.dbc");
        WXL_DBC(sScalingStatValuesStore, "ScalingStatValues.dbc");
        WXL_DBC(sSkillLineStore, "SkillLine.dbc");
        WXL_DBC(sSkillLineAbilityStore, "SkillLineAbility.dbc");
        WXL_DBC(sSkillRaceClassInfoStore, "SkillRaceClassInfo.dbc");
        WXL_DBC(sSkillTiersStore, "SkillTiers.dbc");
        WXL_DBC(sSoundEntriesStore, "SoundEntries.dbc");
        WXL_DBC(sSpellStore, "Spell.dbc");
        WXL_DBC(sSpellCastTimesStore, "SpellCastTimes.dbc");
        WXL_DBC(sSpellCategoryStore, "SpellCategory.dbc");
        WXL_DBC(sSpellDifficultyStore, "SpellDifficulty.dbc");
        WXL_DBC(sSpellDurationStore, "SpellDuration.dbc");
        WXL_DBC(sSpellFocusObjectStore, "SpellFocusObject.dbc");
        WXL_DBC(sSpellItemEnchantmentStore, "SpellItemEnchantment.dbc");
        WXL_DBC(sSpellItemEnchantmentConditionStore, "SpellItemEnchantmentCondition.dbc");
        WXL_DBC(sSpellRadiusStore, "SpellRadius.dbc");
        WXL_DBC(sSpellRangeStore, "SpellRange.dbc");
        WXL_DBC(sSpellRuneCostStore, "SpellRuneCost.dbc");
        WXL_DBC(sSpellShapeshiftFormStore, "SpellShapeshiftForm.dbc");
        WXL_DBC(sSpellVisualStore, "SpellVisual.dbc");
        WXL_DBC(sStableSlotPricesStore, "StableSlotPrices.dbc");
        WXL_DBC(sSummonPropertiesStore, "SummonProperties.dbc");
        WXL_DBC(sTalentStore, "Talent.dbc");
        WXL_DBC(sTalentTabStore, "TalentTab.dbc");
        WXL_DBC(sTaxiNodesStore, "TaxiNodes.dbc");
        WXL_DBC(sTaxiPathStore, "TaxiPath.dbc");
        // TaxiPathNode.dbc: sTaxiPathNodeStore is static inside DBCStores.cpp (not injectable)
        WXL_DBC(sTeamContributionPointsStore, "TeamContributionPoints.dbc");
        WXL_DBC(sTotemCategoryStore, "TotemCategory.dbc");
        WXL_DBC(sTransportAnimationStore, "TransportAnimation.dbc");
        WXL_DBC(sTransportRotationStore, "TransportRotation.dbc");
        WXL_DBC(sVehicleStore, "Vehicle.dbc");
        WXL_DBC(sVehicleSeatStore, "VehicleSeat.dbc");
        WXL_DBC(sWMOAreaTableStore, "WMOAreaTable.dbc");
        WXL_DBC(sWorldMapAreaStore, "WorldMapArea.dbc");
        WXL_DBC(sWorldMapOverlayStore, "WorldMapOverlay.dbc");

#undef WXL_DBC
    }

    uint32 InjectContinuationByTable(char const* baseDbcFile, char const* path)
    {
        if (!baseDbcFile || !path)
            return 0;

        auto const found = sRegistry.find(NormalizeKey(baseDbcFile));
        if (found == sRegistry.end())
        {
            LOG_ERROR("module.wxl-dbc", "No server store registered for {} (continuation: {})", baseDbcFile, path);
            return 0;
        }

        return found->second(path);
    }
}
