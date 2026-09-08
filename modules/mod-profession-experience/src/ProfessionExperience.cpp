/*
 * AzerothCore module: mod-profession-experience
 * High-performance, balanced profession experience rewards for Wrath of the Lich King 3.3.5a (Level 1-80).
 */

#include "ProfessionExperience.h"
#include "Chat.h"
#include "Config.h"
#include "Log.h"
#include "Player.h"
#include "PlayerScript.h"
#include "ScriptMgr.h"
#include "World.h"
#include "WorldScript.h"

#include <algorithm>
#include <cmath>

ProfessionExperienceMgr* ProfessionExperienceMgr::instance()
{
    static ProfessionExperienceMgr inst;
    return &inst;
}

void ProfessionExperienceMgr::LoadConfig()
{
    _config.Enable = sConfigMgr->GetOption<bool>("ProfessionExperience.Enable", true, false);
    _config.MaxLevel = sConfigMgr->GetOption<uint32>("ProfessionExperience.MaxLevel", 80, false);
    _config.XPRate = sConfigMgr->GetOption<float>("ProfessionExperience.XPRate", 1.0f, false);
    _config.UseServerRate = sConfigMgr->GetOption<bool>("ProfessionExperience.UseServerRate", true, false);
    _config.AllowRestedBonus = sConfigMgr->GetOption<bool>("ProfessionExperience.AllowRestedBonus", true, false);
    _config.EnableLevelDeltaPenalty = sConfigMgr->GetOption<bool>("ProfessionExperience.EnableLevelDeltaPenalty", true, false);
    _config.AnnounceXP = sConfigMgr->GetOption<bool>("ProfessionExperience.AnnounceXP", false, false);

    // Difficulty multipliers
    _config.MultOrange = sConfigMgr->GetOption<float>("ProfessionExperience.Mult.Orange", 1.25f, false);
    _config.MultYellow = sConfigMgr->GetOption<float>("ProfessionExperience.Mult.Yellow", 1.00f, false);
    _config.MultGreen  = sConfigMgr->GetOption<float>("ProfessionExperience.Mult.Green", 0.50f, false);
    _config.MultGray   = sConfigMgr->GetOption<float>("ProfessionExperience.Mult.Gray", 0.00f, false);

    // Tier multipliers
    _config.MultApprentice  = sConfigMgr->GetOption<float>("ProfessionExperience.Mult.Apprentice", 1.0f, false);
    _config.MultJourneyman  = sConfigMgr->GetOption<float>("ProfessionExperience.Mult.Journeyman", 1.0f, false);
    _config.MultExpert      = sConfigMgr->GetOption<float>("ProfessionExperience.Mult.Expert", 1.0f, false);
    _config.MultArtisan     = sConfigMgr->GetOption<float>("ProfessionExperience.Mult.Artisan", 1.0f, false);
    _config.MultMaster      = sConfigMgr->GetOption<float>("ProfessionExperience.Mult.Master", 1.0f, false);
    _config.MultGrandMaster = sConfigMgr->GetOption<float>("ProfessionExperience.Mult.GrandMaster", 1.0f, false);

    // Gathering
    _config.HerbalismEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.Herbalism.Enable", true, false);
    _config.HerbalismRate = sConfigMgr->GetOption<float>("ProfessionExperience.Herbalism.Rate", 0.015f, false);
    _config.MiningEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.Mining.Enable", true, false);
    _config.MiningRate = sConfigMgr->GetOption<float>("ProfessionExperience.Mining.Rate", 0.015f, false);
    _config.SkinningEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.Skinning.Enable", true, false);
    _config.SkinningRate = sConfigMgr->GetOption<float>("ProfessionExperience.Skinning.Rate", 0.008f, false);
    _config.LockpickingEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.Lockpicking.Enable", false, false);
    _config.LockpickingRate = sConfigMgr->GetOption<float>("ProfessionExperience.Lockpicking.Rate", 0.005f, false);

    // Crafting
    _config.AlchemyEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.Alchemy.Enable", true, false);
    _config.AlchemyRate = sConfigMgr->GetOption<float>("ProfessionExperience.Alchemy.Rate", 0.010f, false);
    _config.BlacksmithingEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.Blacksmithing.Enable", true, false);
    _config.BlacksmithingRate = sConfigMgr->GetOption<float>("ProfessionExperience.Blacksmithing.Rate", 0.012f, false);
    _config.CookingEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.Cooking.Enable", true, false);
    _config.CookingRate = sConfigMgr->GetOption<float>("ProfessionExperience.Cooking.Rate", 0.005f, false);
    _config.EnchantingEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.Enchanting.Enable", true, false);
    _config.EnchantingRate = sConfigMgr->GetOption<float>("ProfessionExperience.Enchanting.Rate", 0.010f, false);
    _config.DisenchantingEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.Disenchanting.Enable", true, false);
    _config.DisenchantingRate = sConfigMgr->GetOption<float>("ProfessionExperience.Disenchanting.Rate", 0.005f, false);
    _config.EngineeringEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.Engineering.Enable", true, false);
    _config.EngineeringRate = sConfigMgr->GetOption<float>("ProfessionExperience.Engineering.Rate", 0.010f, false);
    _config.FirstAidEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.FirstAid.Enable", true, false);
    _config.FirstAidRate = sConfigMgr->GetOption<float>("ProfessionExperience.FirstAid.Rate", 0.004f, false);
    _config.InscriptionEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.Inscription.Enable", true, false);
    _config.InscriptionRate = sConfigMgr->GetOption<float>("ProfessionExperience.Inscription.Rate", 0.010f, false);
    _config.JewelcraftingEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.Jewelcrafting.Enable", true, false);
    _config.JewelcraftingRate = sConfigMgr->GetOption<float>("ProfessionExperience.Jewelcrafting.Rate", 0.010f, false);
    _config.LeatherworkingEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.Leatherworking.Enable", true, false);
    _config.LeatherworkingRate = sConfigMgr->GetOption<float>("ProfessionExperience.Leatherworking.Rate", 0.012f, false);
    _config.SmeltingEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.Smelting.Enable", true, false);
    _config.SmeltingRate = sConfigMgr->GetOption<float>("ProfessionExperience.Smelting.Rate", 0.005f, false);
    _config.TailoringEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.Tailoring.Enable", true, false);
    _config.TailoringRate = sConfigMgr->GetOption<float>("ProfessionExperience.Tailoring.Rate", 0.012f, false);

    // Secondary
    _config.FishingEnable = sConfigMgr->GetOption<bool>("ProfessionExperience.Fishing.Enable", true, false);
    _config.FishingRate = sConfigMgr->GetOption<float>("ProfessionExperience.Fishing.Rate", 0.005f, false);

    LOG_INFO("module.professionexperience", "ProfessionExperience: loaded configuration. Enabled={}, MaxLevel={}, XPRate={:.2f}, ServerRate={}, RestedBonus={}, LevelPenalty={}.",
        _config.Enable ? "on" : "off",
        _config.MaxLevel,
        _config.XPRate,
        _config.UseServerRate ? "on" : "off",
        _config.AllowRestedBonus ? "on" : "off",
        _config.EnableLevelDeltaPenalty ? "on" : "off");
}

namespace
{
void AwardProfessionXP(Player* player, uint32 currentSkill, uint32 gray, uint32 green, uint32 yellow, uint32 minSkill, float baseRate, char const* professionName)
{
    ProfessionExperienceConfig const& cfg = sProfessionExp->GetConfig();

    if (!cfg.Enable || !player || baseRate <= 0.0f)
        return;

    if (player->GetLevel() >= cfg.MaxLevel || player->GetLevel() >= sWorld->getIntConfig(CONFIG_MAX_PLAYER_LEVEL))
        return;

    if (player->HasFlag(PLAYER_FLAGS, PLAYER_FLAGS_NO_XP_GAIN))
        return;

    // Difficulty multiplier based on recipe / node color
    float multDifficulty = cfg.MultOrange;
    if (currentSkill >= gray)
        multDifficulty = cfg.MultGray;
    else if (currentSkill >= green)
        multDifficulty = cfg.MultGreen;
    else if (currentSkill >= yellow)
        multDifficulty = cfg.MultYellow;

    if (multDifficulty <= 0.0f)
        return;

    // Tier multiplier based on required skill rank
    float multTier = cfg.MultApprentice;
    if (minSkill > 375)
        multTier = cfg.MultGrandMaster;
    else if (minSkill > 300)
        multTier = cfg.MultMaster;
    else if (minSkill > 225)
        multTier = cfg.MultArtisan;
    else if (minSkill > 150)
        multTier = cfg.MultExpert;
    else if (minSkill > 75)
        multTier = cfg.MultJourneyman;

    if (multTier <= 0.0f)
        return;

    // Level Delta Penalty: Prevents Level 70-80 players from spamming Level 1 nodes for high XP
    float penalty = 1.0f;
    if (cfg.EnableLevelDeltaPenalty)
    {
        uint32 const expectedLevel = std::clamp(uint32(1 + (minSkill * 79) / 450), 1u, 80u);
        if (player->GetLevel() > expectedLevel + 10)
        {
            int32 const delta = int32(player->GetLevel()) - int32(expectedLevel);
            penalty = std::max(0.0f, 1.0f - (delta - 10) * 0.10f);
        }
    }

    if (penalty <= 0.0f)
        return;

    // Server rate scaling
    float const serverRate = cfg.UseServerRate ? sWorld->getRate(RATE_XP_QUEST) : 1.0f;

    uint32 const nextLevelXP = player->GetUInt32Value(PLAYER_NEXT_LEVEL_XP);
    if (nextLevelXP == 0)
        return;

    float const rawXP = float(nextLevelXP) * baseRate * cfg.XPRate * multDifficulty * multTier * penalty * serverRate;
    uint32 xpToGive = static_cast<uint32>(std::round(rawXP));

    if (xpToGive == 0)
        return;

    // Apply Rested bonus if enabled
    if (cfg.AllowRestedBonus && player->GetRestBonus() > 0.0f)
    {
        float const restBonus = std::min(static_cast<float>(xpToGive), player->GetRestBonus());
        player->SetRestBonus(player->GetRestBonus() - restBonus);
        xpToGive += static_cast<uint32>(std::round(restBonus));
    }

    sScriptMgr->OnPlayerGiveXP(player, xpToGive, nullptr, PlayerXPSource(42));
    player->GiveXP(xpToGive, nullptr);

    if (cfg.AnnounceXP && player->GetSession())
        ChatHandler(player->GetSession()).PSendSysMessage("Gained {} experience from {}.", xpToGive, professionName);
}
}

class ProfessionExperienceWorldScript : public WorldScript
{
public:
    ProfessionExperienceWorldScript() : WorldScript("ProfessionExperienceWorldScript", {
        WORLDHOOK_ON_AFTER_CONFIG_LOAD
    }) { }

    void OnAfterConfigLoad(bool /*reload*/) override
    {
        sProfessionExp->LoadConfig();
    }
};

class ProfessionExperiencePlayerScript : public PlayerScript
{
public:
    ProfessionExperiencePlayerScript() : PlayerScript("ProfessionExperiencePlayerScript", {
        PLAYERHOOK_ON_UPDATE_CRAFTING_SKILL,
        PLAYERHOOK_ON_UPDATE_GATHERING_SKILL,
        PLAYERHOOK_ON_UPDATE_FISHING_SKILL
    }) { }

    bool OnPlayerUpdateFishingSkill(Player* player, int32 skill, int32 zoneSkill, int32 /*chance*/, int32 /*roll*/) override
    {
        ProfessionExperienceConfig const& cfg = sProfessionExp->GetConfig();
        if (!cfg.Enable || !cfg.FishingEnable || !player)
            return true;

        if (zoneSkill < 1)
            zoneSkill = 1;

        uint32 const currentSkill = skill > 0 ? uint32(skill) : 1u;
        uint32 const gray = uint32(zoneSkill + 100);
        uint32 const green = uint32(zoneSkill + 50);
        uint32 const yellow = uint32(zoneSkill + 25);
        uint32 const minSkill = uint32(zoneSkill);

        AwardProfessionXP(player, currentSkill, gray, green, yellow, minSkill, cfg.FishingRate, "Fishing");
        return true;
    }

    void OnPlayerUpdateGatheringSkill(Player* player, uint32 skillId, uint32 currentLevel, uint32 gray, uint32 green, uint32 yellow, uint32& /*gain*/) override
    {
        ProfessionExperienceConfig const& cfg = sProfessionExp->GetConfig();
        if (!cfg.Enable || !player)
            return;

        float rate = 0.0f;
        char const* name = "";

        switch (skillId)
        {
            case SKILL_HERBALISM:
                if (!cfg.HerbalismEnable)
                    return;
                rate = cfg.HerbalismRate;
                name = "Herbalism";
                break;
            case SKILL_MINING:
                if (!cfg.MiningEnable)
                    return;
                rate = cfg.MiningRate;
                name = "Mining";
                break;
            case SKILL_SKINNING:
                if (!cfg.SkinningEnable)
                    return;
                rate = cfg.SkinningRate;
                name = "Skinning";
                break;
            case SKILL_LOCKPICKING:
                if (!cfg.LockpickingEnable)
                    return;
                rate = cfg.LockpickingRate;
                name = "Lockpicking";
                break;
            default:
                return;
        }

        uint32 const minSkill = yellow > 25 ? yellow - 25 : 1;
        AwardProfessionXP(player, currentLevel, gray, green, yellow, minSkill, rate, name);
    }

    void OnPlayerUpdateCraftingSkill(Player* player, SkillLineAbilityEntry const* skill, uint32 currentLevel, uint32& /*gain*/) override
    {
        ProfessionExperienceConfig const& cfg = sProfessionExp->GetConfig();
        if (!cfg.Enable || !player || !skill)
            return;

        float rate = 0.0f;
        char const* name = "";

        switch (skill->SkillLine)
        {
            case SKILL_ALCHEMY:
                if (!cfg.AlchemyEnable)
                    return;
                rate = cfg.AlchemyRate;
                name = "Alchemy";
                break;
            case SKILL_BLACKSMITHING:
                if (!cfg.BlacksmithingEnable)
                    return;
                rate = cfg.BlacksmithingRate;
                name = "Blacksmithing";
                break;
            case SKILL_COOKING:
                if (!cfg.CookingEnable)
                    return;
                rate = cfg.CookingRate;
                name = "Cooking";
                break;
            case SKILL_ENCHANTING:
                if (skill->Spell == 13262) // Disenchanting
                {
                    if (!cfg.DisenchantingEnable)
                        return;
                    rate = cfg.DisenchantingRate;
                    name = "Disenchanting";
                }
                else
                {
                    if (!cfg.EnchantingEnable)
                        return;
                    rate = cfg.EnchantingRate;
                    name = "Enchanting";
                }
                break;
            case SKILL_ENGINEERING:
                if (!cfg.EngineeringEnable)
                    return;
                rate = cfg.EngineeringRate;
                name = "Engineering";
                break;
            case SKILL_FIRST_AID:
                if (!cfg.FirstAidEnable)
                    return;
                rate = cfg.FirstAidRate;
                name = "First Aid";
                break;
            case SKILL_INSCRIPTION:
                if (!cfg.InscriptionEnable)
                    return;
                rate = cfg.InscriptionRate;
                name = "Inscription";
                break;
            case SKILL_JEWELCRAFTING:
                if (!cfg.JewelcraftingEnable)
                    return;
                rate = cfg.JewelcraftingRate;
                name = "Jewelcrafting";
                break;
            case SKILL_LEATHERWORKING:
                if (!cfg.LeatherworkingEnable)
                    return;
                rate = cfg.LeatherworkingRate;
                name = "Leatherworking";
                break;
            case SKILL_MINING: // Smelting
                if (!cfg.SmeltingEnable)
                    return;
                rate = cfg.SmeltingRate;
                name = "Smelting";
                break;
            case SKILL_TAILORING:
                if (!cfg.TailoringEnable)
                    return;
                rate = cfg.TailoringRate;
                name = "Tailoring";
                break;
            default:
                return;
        }

        uint32 const gray = skill->TrivialSkillLineRankHigh;
        uint32 const green = (skill->TrivialSkillLineRankHigh + skill->TrivialSkillLineRankLow) / 2;
        uint32 const yellow = skill->TrivialSkillLineRankLow;
        uint32 const minSkill = skill->MinSkillLineRank;

        AwardProfessionXP(player, currentLevel, gray, green, yellow, minSkill, rate, name);
    }
};

void Addmod_profession_experienceScripts()
{
    new ProfessionExperienceWorldScript();
    new ProfessionExperiencePlayerScript();
}
