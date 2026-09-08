# ![logo](https://raw.githubusercontent.com/azerothcore/azerothcore.github.io/master/images/logo-github.png) AzerothCore Module: mod-profession-experience

[![AzerothCore Module](https://img.shields.io/badge/AzerothCore-Module-red?style=flat-square&logo=github)](https://github.com/azerothcore/azerothcore-wotlk)
[![C++20](https://img.shields.io/badge/Language-C++20-00599C?style=flat-square&logo=c%2B%2B)](https://isocpp.org/)
[![Branch 3.3.5a](https://img.shields.io/badge/Branch-3.3.5a-orange?style=flat-square)](https://github.com/azerothcore/azerothcore-wotlk)
[![License GPLv3](https://img.shields.io/badge/License-GPLv3-blue?style=flat-square)](LICENSE)

A balanced, highly configurable experience system for **AzerothCore (WotLK 3.3.5a)** that rewards character XP for gathering, crafting, and fishing across all progression brackets from Level 1 to Level 80.

### 💡 Why this module?
In vanilla Wrath of the Lich King, gathering herbs, mining ore nodes, and crafting gear yields no character experience, forcing players to grind quests or dungeons exclusively to level up. 

**`mod-profession-experience`** modernizes progression by rewarding proportional XP for trade skill actions, fully balanced to prevent exploits while making professions a viable, rewarding leveling path.

### 🌟 Key Features

- **Full Level 1 to 80 Progression:** Dynamically scales experience rewards across all level brackets.
- **Anti-Exploit Level-Delta Protection:** Prevents max-level or high-level characters from farming low-level starter nodes (e.g. Peacebloom, Copper) for massive XP gains.
- **Difficulty Multipliers:** Rewards more XP for challenging recipes (Orange/Yellow) and reduced/zero XP for green and gray recipes.
- **Skill Tier Modifiers:** Granular multiplier support for Apprentice, Journeyman, Expert, Artisan, Master, and Grand Master ranks.
- **Rested XP Integration:** Optional support for rested bonus XP on profession actions.
- **Server Rate Compatibility:** Automatically scales with server XP rates (`Rate.XP.Quest` / `Rate.XP.Kill`) or custom module multipliers.
- **Individual Profession Toggles:** Configure enabled status and XP rates independently for every gathering, crafting, and secondary profession.

### 📊 Supported Professions

| Category | Professions Included |
| :--- | :--- |
| **Gathering** | Herbalism, Mining, Skinning, Lockpicking |
| **Crafting** | Alchemy, Blacksmithing, Cooking, Enchanting, Disenchanting, Engineering, First Aid, Inscription, Jewelcrafting, Leatherworking, Smelting, Tailoring |
| **Secondary** | Fishing, Cooking, First Aid |

### 📋 Configuration Reference (`profession_experience.conf`)

| Setting | Default | Description |
| :--- | :---: | :--- |
| `ProfessionExperience.Enable` | `1` | Master switch for profession experience rewards. |
| `ProfessionExperience.MaxLevel` | `80` | Maximum player level to grant profession XP. |
| `ProfessionExperience.XPRate` | `1.0` | Global multiplier for all module experience gains. |
| `ProfessionExperience.UseServerRate` | `1` | Scale XP gains with server rate multipliers. |
| `ProfessionExperience.AllowRestedBonus` | `1` | Allow rested XP bonus to apply to profession actions. |
| `ProfessionExperience.EnableLevelDeltaPenalty` | `1` | Diminish XP when player level exceeds node/recipe level. |
| `ProfessionExperience.AnnounceXP` | `0` | Print chat notifications when profession XP is earned. |
| `ProfessionExperience.Mult.Orange` | `1.25` | XP multiplier for orange recipes (guaranteed skillup). |
| `ProfessionExperience.Mult.Yellow` | `1.00` | XP multiplier for yellow recipes. |
| `ProfessionExperience.Mult.Green` | `0.50` | XP multiplier for green recipes. |
| `ProfessionExperience.Mult.Gray` | `0.00` | XP multiplier for gray recipes (trivial). |

### 🛠️ Installation

1. Clone or place the module folder into `azerothcore-wotlk/modules/`:
   ```bash
   cd azerothcore-wotlk/modules
   git clone https://github.com/AlsoNotMehh/mod-profession-experience.git
   ```

2. Re-run CMake and compile your server:
   ```bash
   cmake -B build
   cmake --build build --config Release
   ```

3. Copy `conf/profession_experience.conf.dist` to your `worldserver` configs directory as `profession_experience.conf` and adjust values to your liking.

### ⭐ Show your support

If you find this module helpful for your server, please consider giving it a star on GitHub!

### 🤝 Credits

- **Author & Enhancements:** [AlsoNotMehh](https://github.com/AlsoNotMehh) ([Discord](https://discord.com/users/1063304041419001966) / [Email](mailto:itsbrayanrodriguez@gmail.com))
- **Original Concept:** Tereneckla
- **Framework:** [AzerothCore](https://www.azerothcore.org)

### 📜 License

This project is licensed under the [GPL-3.0 License](LICENSE).
