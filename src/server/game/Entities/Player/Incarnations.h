/*
 * Incarnations: the body a character wears in each druid form and Metamorphosis, and the body each of its warlock
 * demons is summoned with. The looks come from Eclipse's catalogue (Tools/EclipseImport/eclipse_incarnations.py in
 * wowdecomp), which also writes the three world tables read here:
 *
 *   esteria_incarnation_category  id, kind (1 form, 2 summon), key (form id / creature entry), class_mask, slug, name
 *   esteria_incarnation_form      every shapeshift form that wears a category (Dire Bear wears Bear, ...)
 *   esteria_incarnation           the displays a category may be given
 *
 * A choice is a display from that catalogue, saved per character (character_incarnation). The server applies it, so
 * everyone sees it: forms through Unit::GetModelForForm, demons when they become this player's minion.
 *
 * Transport: the EsteriaIncarnations addon whispers itself addon messages, as FreebornClaim does:
 *   ESTINC\tlist                     -> ESTINC\tlist\t<category>:<display>,...
 *   ESTINC\tset\t<category>\t<display>  -> ESTINC\tok\t<category>\t<display>  or  ESTINC\terr\t<category>
 *   (display 0 clears the choice)
 */

#ifndef ESTERIA_INCARNATIONS_H
#define ESTERIA_INCARNATIONS_H

#include "Define.h"

#include <string>

class Player;

namespace Incarnations
{
    enum Kind : uint8
    {
        KIND_FORM   = 1,
        KIND_SUMMON = 2,
    };

    inline constexpr char const* AddonPrefix = "ESTINC";

    void LoadFromDB();

    /// The category a shapeshift form wears, or 0.
    uint32 CategoryForForm(uint32 form);
    /// The category a summoned creature entry belongs to, or 0.
    uint32 CategoryForCreature(uint32 entry);
    /// Whether `display` is one of `category`'s looks and the category is open to `playerClass`.
    bool IsLook(uint32 category, uint32 display, uint8 playerClass);
    /// Handles one ESTINC envelope; true when the message was ours (the caller must not treat it as chat).
    bool HandleAddonMessage(Player* player, std::string const& msg);
}

#endif
