/*
 * Copyright (C) 2016+ AzerothCore <www.azerothcore.org>, released under GNU AGPL v3 license: https://github.com/azerothcore/azerothcore-wotlk/blob/master/LICENSE-AGPL3
 * Author: AlsoNotMehh
 */

#include "Config.h"
#include "Language.h"
#include "MiscScript.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "Util.h"
#include "World.h"
#include "WorldScript.h"
#include <algorithm>
#include <string>
#include <string_view>
#include <vector>

namespace
{
    class TwoNamesConfig
    {
    public:
        static TwoNamesConfig* instance()
        {
            static TwoNamesConfig instance;
            return &instance;
        }

        void LoadConfig()
        {
            _enabled = sConfigMgr->GetOption<bool>("TwoNames.Enable", true);
            _requireTwoNames = sConfigMgr->GetOption<bool>("TwoNames.RequireTwoNames", false);
            _minNameLength = sConfigMgr->GetOption<uint32>("TwoNames.MinNameLength", 2);
            _maxNameLength = sConfigMgr->GetOption<uint32>("TwoNames.MaxNameLength", 25);
            _minPartLength = sConfigMgr->GetOption<uint32>("TwoNames.MinPartLength", 2);
            _maxPartLength = sConfigMgr->GetOption<uint32>("TwoNames.MaxPartLength", 12);
            _allowMultipleSpaces = sConfigMgr->GetOption<bool>("TwoNames.AllowMultipleSpaces", false);
            _strictPlayerNames = sConfigMgr->GetOption<int32>("TwoNames.StrictPlayerNames", -1);
        }

        [[nodiscard]] bool IsEnabled() const { return _enabled; }
        [[nodiscard]] bool IsTwoNamesRequired() const { return _requireTwoNames; }
        [[nodiscard]] uint32 GetMinNameLength() const { return _minNameLength; }
        [[nodiscard]] uint32 GetMaxNameLength() const { return _maxNameLength; }
        [[nodiscard]] uint32 GetMinPartLength() const { return _minPartLength; }
        [[nodiscard]] uint32 GetMaxPartLength() const { return _maxPartLength; }
        [[nodiscard]] bool AllowMultipleSpaces() const { return _allowMultipleSpaces; }
        [[nodiscard]] uint32 GetStrictMask() const
        {
            if (_strictPlayerNames >= 0)
                return static_cast<uint32>(_strictPlayerNames);
            return sWorld->getIntConfig(CONFIG_STRICT_PLAYER_NAMES);
        }

    private:
        bool _enabled = true;
        bool _requireTwoNames = false;
        uint32 _minNameLength = 2;
        uint32 _maxNameLength = 25;
        uint32 _minPartLength = 2;
        uint32 _maxPartLength = 12;
        bool _allowMultipleSpaces = false;
        int32 _strictPlayerNames = -1;
    };

    #define sTwoNamesConfig TwoNamesConfig::instance()

    enum LanguageType
    {
        LT_BASIC_LATIN    = 0x0000,
        LT_EXTENDED_LATIN = 0x0001,
        LT_CYRILLIC       = 0x0002,
        LT_EAST_ASIA      = 0x0004,
        LT_ANY            = 0xFFFF
    };

    static LanguageType GetRealmLanguageType(bool create)
    {
        switch (sWorld->getIntConfig(CONFIG_REALM_ZONE))
        {
            case REALM_ZONE_UNKNOWN:
            case REALM_ZONE_DEVELOPMENT:
            case REALM_ZONE_TEST_SERVER:
            case REALM_ZONE_QA_SERVER:
                return LT_ANY;
            case REALM_ZONE_UNITED_STATES:
            case REALM_ZONE_OCEANIC:
            case REALM_ZONE_LATIN_AMERICA:
            case REALM_ZONE_ENGLISH:
            case REALM_ZONE_GERMAN:
            case REALM_ZONE_FRENCH:
            case REALM_ZONE_SPANISH:
                return LT_EXTENDED_LATIN;
            case REALM_ZONE_KOREA:
            case REALM_ZONE_TAIWAN:
            case REALM_ZONE_CHINA:
                return LT_EAST_ASIA;
            case REALM_ZONE_RUSSIAN:
                return LT_CYRILLIC;
            default:
                return create ? LT_BASIC_LATIN : LT_ANY;
        }
    }

    static bool IsValidLanguageString(std::wstring_view wstr, uint32 strictMask, bool create)
    {
        if (isBasicLatinString(wstr, false))
            return true;

        if (strictMask == 0)
        {
            if (isExtendedLatinString(wstr, false))
                return true;
            if (isCyrillicString(wstr, false))
                return true;
            if (isEastAsianString(wstr, false))
                return true;
            return false;
        }

        if (strictMask & 0x2)
        {
            LanguageType lt = GetRealmLanguageType(create);
            if (lt == LT_BASIC_LATIN || (lt & LT_EXTENDED_LATIN) || lt == LT_ANY)
            {
                if (isExtendedLatinString(wstr, false))
                    return true;
            }
            if (lt & LT_CYRILLIC || lt == LT_ANY)
            {
                if (isCyrillicString(wstr, false))
                    return true;
            }
            if (lt & LT_EAST_ASIA || lt == LT_ANY)
            {
                if (isEastAsianString(wstr, false))
                    return true;
            }
        }

        if (strictMask & 0x1)
        {
            if (isBasicLatinString(wstr, false))
                return true;
        }

        return false;
    }

    class TwoNamesWorldScript : public WorldScript
    {
    public:
        TwoNamesWorldScript() : WorldScript("TwoNamesWorldScript") { }

        void OnAfterConfigLoad(bool /*reload*/) override
        {
            sTwoNamesConfig->LoadConfig();
        }
    };

    class TwoNamesMiscScript : public MiscScript
    {
    public:
        TwoNamesMiscScript() : MiscScript("TwoNamesMiscScript") { }

        bool CanNormalizePlayerName(std::string& name, bool& result) override
        {
            if (!sTwoNamesConfig->IsEnabled())
                return false;

            if (name.empty())
            {
                result = false;
                return true;
            }

            std::string trimmed = name;
            while (!trimmed.empty() && (trimmed.front() == ' ' || trimmed.front() == '\t' || trimmed.front() == '\r' || trimmed.front() == '\n'))
                trimmed.erase(trimmed.begin());
            while (!trimmed.empty() && (trimmed.back() == ' ' || trimmed.back() == '\t' || trimmed.back() == '\r' || trimmed.back() == '\n'))
                trimmed.pop_back();

            if (trimmed.empty())
            {
                result = false;
                return true;
            }

            size_t spaceCount = std::count(trimmed.begin(), trimmed.end(), ' ');
            if (spaceCount > 1 && !sTwoNamesConfig->AllowMultipleSpaces())
            {
                result = false;
                return true;
            }

            if (trimmed.find("  ") != std::string::npos)
            {
                result = false;
                return true;
            }

            std::wstring tmp;
            if (!Utf8toWStr(trimmed, tmp))
            {
                result = false;
                return true;
            }

            wstrToLower(tmp);

            bool capitalizeNext = true;
            for (size_t i = 0; i < tmp.size(); ++i)
            {
                if (tmp[i] == L' ')
                {
                    capitalizeNext = true;
                }
                else if (capitalizeNext)
                {
                    tmp[i] = wcharToUpper(tmp[i]);
                    capitalizeNext = false;
                }
            }

            if (!WStrToUtf8(tmp, name))
            {
                result = false;
                return true;
            }

            result = true;
            return true;
        }

        bool OnCheckPlayerName(std::string_view name, bool create, uint8& result) override
        {
            if (!sTwoNamesConfig->IsEnabled())
                return false;

            std::wstring wname;

            if (!Utf8toWStr(name, wname))
            {
                result = CHAR_NAME_INVALID_CHARACTER;
                return true;
            }

            uint32 maxName = sTwoNamesConfig->GetMaxNameLength();
            if (wname.size() > maxName)
            {
                result = CHAR_NAME_TOO_LONG;
                return true;
            }

            uint32 minName = sTwoNamesConfig->GetMinNameLength();
            if (wname.size() < minName)
            {
                result = CHAR_NAME_TOO_SHORT;
                return true;
            }

            if (wname.front() == L' ' || wname.back() == L' ')
            {
                result = CHAR_NAME_INVALID_CHARACTER;
                return true;
            }

            if (wname.find(L"  ") != std::wstring::npos)
            {
                result = CHAR_NAME_INVALID_CHARACTER;
                return true;
            }

            std::vector<std::string> parts;
            std::string currentPart;
            std::string nameStr(name);
            for (char c : nameStr)
            {
                if (c == ' ')
                {
                    if (!currentPart.empty())
                    {
                        parts.push_back(currentPart);
                        currentPart.clear();
                    }
                }
                else
                {
                    currentPart += c;
                }
            }
            if (!currentPart.empty())
                parts.push_back(currentPart);

            if (parts.empty())
            {
                result = CHAR_NAME_TOO_SHORT;
                return true;
            }

            if (sTwoNamesConfig->IsTwoNamesRequired() && parts.size() < 2)
            {
                result = CHAR_NAME_TOO_SHORT;
                return true;
            }

            if (parts.size() > 2 && !sTwoNamesConfig->AllowMultipleSpaces())
            {
                result = CHAR_NAME_INVALID_CHARACTER;
                return true;
            }

            uint32 minPartLen = sTwoNamesConfig->GetMinPartLength();
            uint32 maxPartLen = sTwoNamesConfig->GetMaxPartLength();
            for (auto const& part : parts)
            {
                std::wstring wpart;
                if (!Utf8toWStr(part, wpart) || wpart.size() < minPartLen)
                {
                    result = CHAR_NAME_TOO_SHORT;
                    return true;
                }
                if (wpart.size() > maxPartLen)
                {
                    result = CHAR_NAME_TOO_LONG;
                    return true;
                }
            }

            uint32 strictMask = sTwoNamesConfig->GetStrictMask();
            for (auto const& part : parts)
            {
                std::wstring wpart;
                if (!Utf8toWStr(part, wpart))
                {
                    result = CHAR_NAME_INVALID_CHARACTER;
                    return true;
                }

                if (!IsValidLanguageString(wpart, strictMask, create))
                {
                    result = CHAR_NAME_MIXED_LANGUAGES;
                    return true;
                }
            }

            for (auto const& part : parts)
            {
                std::wstring wpart;
                if (Utf8toWStr(part, wpart))
                {
                    wstrToLower(wpart);
                    for (std::size_t i = 2; i < wpart.size(); ++i)
                    {
                        if (wpart[i] == wpart[i - 1] && wpart[i] == wpart[i - 2])
                        {
                            result = CHAR_NAME_THREE_CONSECUTIVE;
                            return true;
                        }
                    }
                }
            }

            if (sObjectMgr->IsReservedName(name))
            {
                result = CHAR_NAME_RESERVED;
                return true;
            }
            for (auto const& part : parts)
            {
                if (sObjectMgr->IsReservedName(part))
                {
                    result = CHAR_NAME_RESERVED;
                    return true;
                }
            }

            if (sObjectMgr->IsProfanityName(name))
            {
                result = CHAR_NAME_PROFANE;
                return true;
            }
            for (auto const& part : parts)
            {
                if (sObjectMgr->IsProfanityName(part))
                {
                    result = CHAR_NAME_PROFANE;
                    return true;
                }
            }

            result = CHAR_NAME_SUCCESS;
            return true;
        }
    };
}

void AddTwoNamesScripts()
{
    new TwoNamesWorldScript();
    new TwoNamesMiscScript();
}
