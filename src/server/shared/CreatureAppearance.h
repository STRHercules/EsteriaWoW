// Generated from the selected race sources by tools/creature_race_pack.py.
#ifndef ACORE_CREATURE_APPEARANCE_H
#define ACORE_CREATURE_APPEARANCE_H

#include <array>
#include <cstdint>

namespace CreatureAppearance
{
    struct Option
    {
        unsigned field;
        unsigned count;
        unsigned factor;
    };

    inline constexpr std::array<Option, 5> NagaMale = {{
        {0, 25, 1},
        {1, 1, 1},
        {2, 5, 1},
        {3, 15, 1},
        {4, 96, 1},
    }};

    inline constexpr std::array<Option, 5> NagaFemale = {{
        {0, 255, 1},
        {1, 1, 1},
        {2, 5, 1},
        {3, 80, 1},
        {4, 240, 1},
    }};

    inline constexpr std::array<Option, 5> TuskarrMale = {{
        {0, 7, 1},
        {1, 1, 1},
        {2, 7, 1},
        {3, 7, 1},
        {4, 7, 1},
    }};

    inline constexpr std::array<Option, 5> VrykulMale = {{
        {0, 6, 1},
        {1, 1, 1},
        {2, 6, 1},
        {3, 5, 1},
        {4, 6, 1},
    }};

    inline constexpr std::array<Option, 5> ThinhumanMale = {{
        {0, 4, 1},
        {1, 1, 1},
        {2, 4, 1},
        {3, 4, 1},
        {4, 7, 1},
    }};

    constexpr bool Uses(unsigned race)
    {
        return race >= 54 && race <= 59;
    }

    constexpr bool GenderAllowed(unsigned race, unsigned gender)
    {
        return Uses(race) && (gender == 0 || (race == 54 && gender == 1));
    }

    constexpr std::array<Option, 5> const& Options(unsigned race, unsigned gender)
    {
        switch (race)
        {
            case 54:
                return gender ? NagaFemale : NagaMale;
            case 55:
                return TuskarrMale;
            case 56:
            case 57:
                return VrykulMale;
            case 58:
            case 59:
                return ThinhumanMale;
            default:
                return NagaMale;
        }
    }

    constexpr bool Validate(unsigned race, unsigned gender, std::array<std::uint8_t, 5> const& fields)
    {
        if (!GenderAllowed(race, gender))
            return false;
        auto const& options = Options(race, gender);
        for (unsigned i = 0; i < fields.size(); ++i)
            if (fields[i] >= options[i].count)
                return false;
        return true;
    }
}

#endif
