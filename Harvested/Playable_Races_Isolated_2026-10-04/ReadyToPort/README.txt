PROJECT REFORGED PLAYABLE RACE ISOLATION

This folder contains the final client-side payload isolated for the custom playable Ogre, Furbolg, and Tuskarr races.

Furbolg: race 18, Alliance. Models 60591/60592 -> Character\Furbolg\FurbolgRace.m2. Classes: Warrior, Hunter, Shaman, Druid.
Tuskarr: race 23, Alliance. Displays 50009/50010 -> Character\ReforgedTuskarr\Male\TuskarrMale.mdx (actual extracted file is .m2). Both genders use the same mesh. Classes: Warrior, Hunter, Priest, Shaman, Mage.
Ogre: race 25, Horde. Displays 50013/50014 -> separate OgreMale/OgreFemale models. Classes: Warrior, Hunter, Priest, Shaman, Mage, Warlock.

Shared\DBFilesClient contains the latest race/customization DBCs, preferring patch-ZZ and falling back to patch-Z when patch-ZZ did not carry a table.
The parent extraction folder preserves every source archive copy and manifest for provenance.

Important: this is client-side data. Server-side race masks, character creation rules, starting coordinates, spells/racials, quests, and database rows are not recoverable from these MPQs alone.
