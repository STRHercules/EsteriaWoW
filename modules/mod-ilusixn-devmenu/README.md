# ilusixn Dev Menu

**ilusixn Dev Menu** is an in-game world editor for **AzerothCore (WotLK 3.3.5a)**. It's a server module plus a client addon, and it works on any 3.3.5a (12340) client. Made by **ilusixn**.

Type `/dev` on a GM account to browse every NPC, preview it in 3D, spawn it, dress it, give it spells, paths, shops and quests, and place objects. Every change is saved to the world database and applied live: no restart, no `.reload`.

[![Dev Menu demo video](media/preview.jpg)](media/dev-menu-demo.mp4)

▶ **[Watch the demo video](media/dev-menu-demo.mp4)** (1 min 47 s)

## Install

**Full step-by-step guide: [INSTALL.md](INSTALL.md).** Ready-made zips are on the [Releases page](https://github.com/ilusixn/ilusixn-dev-menu/releases). Short version:

1. **Server:** clone or copy this repository into `azerothcore/modules/mod-ilusixn-devmenu`. The folder name matters, because AzerothCore finds the module's loader by it. Then re-run CMake and build `worldserver`.
   ```
   git clone https://github.com/ilusixn/ilusixn-dev-menu.git modules/mod-ilusixn-devmenu
   ```
   Optional: copy `conf/mod_ilusixn_devmenu.conf.dist` next to your other module confs as `mod_ilusixn_devmenu.conf`.
2. **Client:** copy `client/DevMenu` into `World of Warcraft/Interface/AddOns/`. Only GMs need it.
3. Log in on a GM account and type `/dev`.

It's a plain module: no core patches and no SQL to import. It creates its own table (`coa_npc_outfit`) on first start, and it only talks over addon whisper messages (prefix `CDEV`), so it runs next to any other addon.

| Config | Default | Meaning |
|---|---|---|
| `DevMenu.Enable` | 1 | Turn the module on or off |
| `DevMenu.MinSecurity` | 2 | Lowest account level allowed (2 = GM, 3 = admin) |
| `DevMenu.Items.FirstId` | 0 | First of the 9999 item ids used by *Create an item* (0 = 9400001) |

## What it does

- **Browse NPCs:** search every creature by name, title or id.
  - Filters: friendly, hostile, neutral, critters, services, custom.
  - Ctrl+click or double-click opens a 3D preview.
  - Right-click: spawn, favourites, categories, duplicate as a new NPC, rename, copy id.
- **Categories:** your own folders of NPCs, plus Favourites.
- **Selected NPC:** target an NPC and edit it.
  - **Placement:**
    - Move to me, and a d-pad that moves relative to where you face.
    - An editor-style X / Y / Z gizmo: drag an axis to slide, drag the ring to turn.
    - Exact facing in degrees.
  - **Actions:** stand, wander or walk a path; looping emotes (work, sit, sleep, dance…); play any emote.
  - **Role & faction:** vendor, trainer, innkeeper, banker, flight master… plus guard behaviour and faction.
  - **Identity:** name, title, level, model, make unique.
  - **Replace:** turn the spawn into any other NPC (all NPCs, the ones you made, or your favourites), with a 3D preview.
  - **Services:**
    - **Shop items:** each item's gold price, or a currency from the server (emblems, badges, honor, tokens…).
    - **Trainers.**
    - **Talk menus:** options and submenus.
  - **Combat:**
    - Set the auto-attack damage per hit and the attack speed.
    - Give the NPC any spell on your server. Search by name or id, or use `npc:<entry>` to copy what another mob casts.
    - Each spell has a timer, a target (current target, itself or a random enemy) and a chance.
    - Hostile and friendly NPCs both use them.
  - **Advanced:** every stat, flag, respawn time and kill reputation.
- **Path editor:** walk and press *Add point here* (or `/dev point`), or turn on *Every step* to drop a point each step while you move. Choose loop or back-and-forth, walk or run, and a wait at the ends.
  - *Show path* draws an NPC's saved route; *Edit path* loads it as your recording.
  - **Path map:** its own resizable window. Zoom with the wheel, drag to pan, pick a point and *Go to* (teleport), *Move here*, *Insert after* or *Delete*. Every path button is also under the map.
  - **Saved paths:** keep routes by name and load them on any NPC later.
- **Create an item:** build an item from A to Z (armor, weapon, consumable, other): name, quality, item level, required level, stats, prices, a spell (searchable by name), a description, a look and an icon from a picker. Heirlooms are supported: choose how much each stat grows per level. *Items created* lists everything you made with a Give button and favourites.
- **Your character:** powers (god mode, flying, instant cast, no cooldowns...), level, money, honor and arena points, all mounts, heirloom sets, gear sets with a level filter, bag presets that fill any character's bags in one click, every reputation, and Alliance / Neutral / Horde.
- **Morph:** morph into any model id with a live preview (reverts unless you press Apply), and walk through every model id.
- **Server:** time of day, weather, teleport places, holiday events, announcements, save all players, reload tables.
- Long lists (NPCs, objects, gear sets, models, places) scroll like normal lists and load more as you scroll.
- **Share as SQL:** every change you make is tracked. *Export SQL* writes `devmenu_sql/<date>_<name>.sql` next to worldserver: the rows as they are now (delete + insert, safe to run twice). Anyone runs it on their world database and gets the same NPCs in the same places. *Add area / zone / everything* pulls in older work.
- **Nearby spawns:** saved spawns around you, nearest first.
- **Quests:**
  - Create quests given by the selected NPC: text, objectives, rewards, rules and chains, plus who gives and finishes them.
  - Escort quests: the NPC walks a path you recorded.
  - An **AI helper** builds a prompt for any AI chat; paste the answer back and Apply fills the fields.
- **Objects & assets:**
  - Search object types or every object model, with a 3D preview.
  - Spawn, then click an object in the world to select it.
  - Move, rotate on 3 axes, duplicate, delete.
- **Create an NPC:**
  - Dress an NPC like a player character: race, gender, skin, face, hair and every armor slot and weapon.
  - A transmog-style **wardrobe**: 3D tiles, filters by material and weapon type, sort by color or quality. Ctrl+click an item to try it on yourself.
  - Live preview in front of you, then create it or apply it to the selected NPC.
  - Save looks (the whole NPC) and outfits (gear only, so many NPCs can wear the same thing), and share looks with a code.
- **Help:** in-game help page explaining everything above.

### About the Create an NPC tab

**The races you can pick are the playable races your own client and server have.** The list is read from the server's `ChrRaces` / `CharSections` data, so every race the server has is included automatically, with nothing to configure. That covers custom races, male-only and female-only races, and DBCs in any language:

- **Stock 3.3.5a:** the 10 classic races with their stock customisation.
- **Custom playable races:** they show up automatically, provided the client has their models and textures. Armor shows on every client.

Dressed NPCs use the same trick as the Mirror Image spell, so every unmodified 3.3.5a client shows them, no client patch needed. Weapons are normal NPC equipment.

### Sharing dressed NPCs without the module: baking

Dressed NPCs need this module on the server that shows them. To share them with servers that don't run it, bake them after *Export SQL*:

```
pip install pillow
python tools/bake/bake.py --data "<WoW folder>/Data" --exports "<server>/devmenu_sql" --user <mysql user> --password <mysql password>
```

It writes `<name>_baked.sql` (run it instead of the plain export, no module needed) and `patch-ZZZZZZ.MPQ` (players put it in their `Data` folder; it replaces the client's `CreatureDisplayInfo` and `CreatureDisplayInfoExtra` DBCs with yours plus the baked models). Skins are painted from the client's own files. Clients that draw faces differently can pass ready textures with `--capture <folder>`. `python tools/bake/bake.py -h` lists every option.

### Custom clients: look adapters

A stock client has 5 look rows: skin, face, hair style, hair color and facial hair. Custom clients that add more (tattoos, horns, extra palettes…) can plug in a small Lua **look adapter**, and its rows appear in Create an NPC. Clients without one simply ignore the extra values. The in-game Help page explains the API.

`client/DevMenu/DevMenu_CoA.lua` is the adapter for the custom races of the Conquest of Azeroth / Esteria client. On any other client those races don't exist, so the file does nothing and is safe to keep.

## Ids it creates

| What | Ids |
|---|---|
| NPC types (copies, dressed NPCs), trainers, object types | 9 980 001+ |
| Quests | 9 990 001 – 9 999 999 |
| Talk menus | 9 998 001 – 9 998 999 |
| NPC texts | 16 000 001+ |
| Escort paths | 99 800 000 + quest id |
| Baked models (bake tool) | after the highest display id in client and server |

Tables it adds to the world database: `coa_npc_outfit`, `coa_devmenu_changes` (the change set), `coa_npc_bake` (baked model ids, so re-baking keeps them).

If your server already uses these ranges, change the constants at the top of `src/DevMenu.cpp`.

## Good to know

- **NPC types are shared.** Name, level, look, faction, damage and combat spells belong to the NPC **type**, so every spawn of it shares them. Tick *Only this spawn* (or *Make unique*) to change just one.
- **Gold prices are per item.** The 3.3.5a client shows one gold price per item, so changing a price changes it at every vendor that sells that item.
- **Back up first.** Back up your world database before big sessions: edits are saved immediately.

## Credits

- Made by **ilusixn**.
- The look-adapter data for the Esteria custom races comes from the Esteria race work by Furioz, Corruption and the Eunoia team.
