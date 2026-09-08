# mod-loyal-steed

A race-specific persistent companion module for AzerothCore WoW 3.3.5a.

Every player can bond with a Loyal Steed — a persistent companion that follows them through the world, carries their supplies, sets up camp, and remembers the paths they have traveled.

---

## Features

### Race-Specific Companions
Each race bonds with their own mount type:
| Race | Companion |
|------|-----------|
| Human | Warhorse |
| Dwarf | Alterac Ram |
| Gnome | Mechanostrider |
| Night Elf | Nightsaber |
| Draenei | Elekk |
| Orc | Wolf |
| Troll | Raptor |
| Tauren | Kodo |
| Undead | Skeletal Horse |
| Blood Elf | Hawkstrider |

### Companion Behaviors
- **Follow Me** — Your steed follows at a natural pace
- **Wait Here** — Your steed stays permanently at its current position
- **Mount Up** — Mount your steed and ride
- **Change Appearance** — Choose from your learned mounts

### Camp System
- **Set Up Camp** — Your steed sets up a full campsite including fire, tent, lantern, bow, pack and mug
- Camp persists across zone changes
- Your steed waits at camp while you adventure

### Ranger's Saddlebags
- Full item storage powered by mod-improved-bank
- Deposit and withdraw items by category
- Quick deposit all reagents
- Full item preservation — enchants, durability, and charges all maintained

### Fast Travel
- **Remember this location** — Your steed memorizes any location you choose
- Up to 20 saved locations per player
- Continental travel only — encourages use of ships and zeppelins for cross-continent travel
- **Forget a location** — Remove saved locations you no longer need

---

## Requirements
- AzerothCore WoW 3.3.5a
- [mod-improved-bank](https://github.com/silviu20092/mod-improved-bank) — Required for saddlebag storage

---

## Installation

### Server Installation

1. Clone this repository into your AzerothCore modules folder:
```bash
git clone https://github.com/Cliffutubius/mod-loyal-steed.git
```

2. Clone mod-improved-bank into your modules folder:
```bash
git clone https://github.com/silviu20092/mod-improved-bank.git
```

3. Re-run cmake and rebuild:
```bash
cmake ..
make -j$(nproc)
```

4. Apply the SQL files manually if not auto-imported:
```bash
mysql -u root -p acore_world < data/sql/db-world/base/loyal_steed_world.sql
mysql -u root -p acore_characters < data/sql/db-characters/base/loyal_steed_characters.sql
```

5. Copy the config file:
```bash
cp conf/mod_loyal_steed.conf.dist /path/to/your/server/etc/modules/
```

6. Edit `mod_loyal_steed.conf` to configure features.

---

### Client Installation

The module includes a patched `Spell.dbc` that adds the Loyal Steed companion spell to the correct spellbook tab. Without this patch the spell will still work, but it will not appear correctly in your Companions tab.

**You will need:**
- [Ladik's MPQ Editor](https://www.zezula.net/en/mpq/download.html) — free tool for editing WoW MPQ archives
- The file `client/Spell.dbc` from this repository

**Steps:**

1. Download and install Ladik's MPQ Editor.

2. Locate your WoW client's `Data\enUS\` folder (or `Data\enGB\` depending on your locale).

3. Check whether a file named `patch-enUS-6.mpq` already exists in that folder.
   - **If it does not exist:** Create a new MPQ archive named `patch-enUS-6.mpq` in `Data\enUS\` using Ladik's MPQ Editor (File → New).
   - **If it already exists:** Open the existing file.

4. Inside the MPQ archive, create the folder path `DBFilesClient\` if it does not already exist.

5. Add `Spell.dbc` from this repository's `client/` folder into `DBFilesClient\` inside the MPQ.

6. Save and close the MPQ Editor.

7. Launch your WoW client. The patch will load automatically — no further steps required.

> **Note:** The patch file must load after `patch-enUS-5.MPQ`. Naming it `patch-enUS-6.mpq` ensures correct load order. If you already have a `patch-enUS-6.mpq` with other content, you can add the `Spell.dbc` directly into your existing file rather than creating a new one. Alternatively, the included `client/patch-LoyalSteed.mpq` can be placed directly in `Data\enUS\` as a ready-made patch — rename it to fit your load order if needed.

---

## Getting Started (In-Game)

1. Visit your racial mount vendor and purchase the **Loyal Steed Deed**
2. Use the deed to bond with your steed
3. Find the companion spell in your **Spellbook → Companions** tab
4. Cast the spell to summon your steed
5. Right-click your steed to access all features

### Racial Mount Vendors
| Race | Vendor | Location |
|------|--------|----------|
| Human | Katie Hunter | Elwynn Forest — Eastvale Logging Camp |
| Dwarf | Veron Amberstill | Dun Morogh — Amberstill Ranch |
| Gnome | Milli Featherwhistle | Dun Morogh — Steelgrill's Depot |
| Night Elf | Lelanai | Teldrassil — Dolanaar |
| Draenei | Torallius the Pack Handler | Azuremyst Isle — Azure Watch |
| Orc | Ogunaro Wolfrunner | Orgrimmar — Valley of Honor |
| Troll | Zjolnir | Durotar — Sen'jin Village |
| Tauren | Harb Clawhoof | Mulgore — Bloodhoof Village |
| Undead | Zachariah Post | Tirisfal Glades — Brill |
| Blood Elf | Winaestra | Eversong Woods — Silvermoon City |

---

## Configuration

See `conf/mod_loyal_steed.conf.dist` for all available options:

- Enable/disable the entire module
- Enable/disable individual features (storage, fast travel, camp, appearance)
- Set maximum saved locations (default: 20)
- Toggle continent-only fast travel restriction

---

## Known Issues
- The **Mount Up** feature uses the player's currently selected mount appearance. Use **Change Appearance** to select a race-appropriate mount before mounting.
- Fast travel may occasionally cause minor fall damage at some locations. If this happens, dismiss your steed, reposition to a safer spot, and re-save the location.

---

## Author
**Cliffutubius**

## License
GNU General Public License v3.0 — see [LICENSE](LICENSE) for details.

## Credits
See [CREDITS.md](CREDITS.md) for third-party attributions.
