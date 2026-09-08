#ifndef _PROFESSION_EXPERIENCE_H_
#define _PROFESSION_EXPERIENCE_H_

#include "Common.h"
#include "SharedDefines.h"

struct ProfessionExperienceConfig
{
    bool Enable = true;
    uint32 MaxLevel = 80;
    float XPRate = 1.0f;
    bool UseServerRate = true;
    bool AllowRestedBonus = true;
    bool EnableLevelDeltaPenalty = true;
    bool AnnounceXP = false;

    // Difficulty multipliers
    float MultOrange = 1.25f;
    float MultYellow = 1.00f;
    float MultGreen  = 0.50f;
    float MultGray   = 0.00f;

    // Tier multipliers
    float MultApprentice  = 1.0f;
    float MultJourneyman  = 1.0f;
    float MultExpert      = 1.0f;
    float MultArtisan     = 1.0f;
    float MultMaster      = 1.0f;
    float MultGrandMaster = 1.0f;

    // Gathering
    bool HerbalismEnable = true;
    float HerbalismRate = 0.015f;
    bool MiningEnable = true;
    float MiningRate = 0.015f;
    bool SkinningEnable = true;
    float SkinningRate = 0.008f;
    bool LockpickingEnable = false;
    float LockpickingRate = 0.005f;

    // Crafting
    bool AlchemyEnable = true;
    float AlchemyRate = 0.010f;
    bool BlacksmithingEnable = true;
    float BlacksmithingRate = 0.012f;
    bool CookingEnable = true;
    float CookingRate = 0.005f;
    bool EnchantingEnable = true;
    float EnchantingRate = 0.010f;
    bool DisenchantingEnable = true;
    float DisenchantingRate = 0.005f;
    bool EngineeringEnable = true;
    float EngineeringRate = 0.010f;
    bool FirstAidEnable = true;
    float FirstAidRate = 0.004f;
    bool InscriptionEnable = true;
    float InscriptionRate = 0.010f;
    bool JewelcraftingEnable = true;
    float JewelcraftingRate = 0.010f;
    bool LeatherworkingEnable = true;
    float LeatherworkingRate = 0.012f;
    bool SmeltingEnable = true;
    float SmeltingRate = 0.005f;
    bool TailoringEnable = true;
    float TailoringRate = 0.012f;

    // Secondary
    bool FishingEnable = true;
    float FishingRate = 0.005f;
};

class ProfessionExperienceMgr
{
public:
    static ProfessionExperienceMgr* instance();

    void LoadConfig();
    ProfessionExperienceConfig const& GetConfig() const { return _config; }

private:
    ProfessionExperienceMgr() = default;
    ProfessionExperienceConfig _config;
};

#define sProfessionExp ProfessionExperienceMgr::instance()

#endif // _PROFESSION_EXPERIENCE_H_
