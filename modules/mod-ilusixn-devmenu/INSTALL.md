# Installing ilusixn Dev Menu on your server

Dev Menu has two parts:

| Part | Where it goes | Who needs it |
|---|---|---|
| **Server module** (`mod-ilusixn-devmenu`) | your AzerothCore source, built into `worldserver` | the server, once |
| **Client addon** (`DevMenu`) | `World of Warcraft/Interface/AddOns/` | every GM who uses `/dev` (players don't need it) |

**Requirements:**
- AzerothCore 3.3.5a (WotLK, client 12340) built from source, with a recent master that has the module script hooks (`WorldScript`, `ServerScript::CanPacketReceive`, `PlayerScript` hook lists).
- A C++ build environment that already builds your `worldserver`.
- No core patch, no SQL file, no DBC or client patch.

## 1. Add the server module

**Option A, from the release zip:**
1. Download `mod-ilusixn-devmenu-v1.2.zip` from the [Releases page](https://github.com/ilusixn/ilusixn-dev-menu/releases).
2. Unzip it into the `modules` folder of your AzerothCore **source** (the folder that already holds `mod-eluna`, `mod-playerbots`, etc. if you use any), so you get `azerothcore/modules/mod-ilusixn-devmenu/src/DevMenu.cpp`.

**Option B, with git** (from your AzerothCore folder):
```
git clone https://github.com/ilusixn/ilusixn-dev-menu.git modules/mod-ilusixn-devmenu
```

> **Keep the folder name `mod-ilusixn-devmenu`.** AzerothCore finds a module's loader by its folder name (`Addmod_ilusixn_devmenuScripts`). With another folder name the build fails at link time.

## 2. Build

1. Re-run CMake so it picks up the new module, the same way you configured your server.
2. Rebuild `worldserver`.

The module only adds code. It compiles into the normal `modules` library, with nothing to enable in CMake.

## 3. Config (optional)

Copy `conf/mod_ilusixn_devmenu.conf.dist` to your server's module config folder (usually `configs/modules/`) as `mod_ilusixn_devmenu.conf`. Without it the defaults are used, and the server log reminds you about the missing file.

| Setting | Default | Meaning |
|---|---|---|
| `DevMenu.Enable` | 1 | 0 turns the menu off for everyone |
| `DevMenu.MinSecurity` | 2 | lowest account level allowed: 2 = GM, 3 = admin |

## 4. Start the server

On first start the module creates its tables in the world database (`coa_npc_outfit`, `coa_devmenu_changes`, `coa_npc_bake`). There is nothing to import.

## 5. Install the addon (each GM)

1. Download `DevMenu-addon-v1.2.zip` (or take `client/DevMenu` from the repo).
2. Unzip it into `World of Warcraft/Interface/AddOns/` so you get `Interface/AddOns/DevMenu/DevMenu.toc`.
3. Restart the game (not just `/reload`, since the addon is new) and enable it on the character screen's AddOns list if needed.
4. Log in on a GM account and type **`/dev`**.

## 6. Check it works

- **Header:** it shows **Connected – GM level N**. If it says it is waiting, the server module isn't answering: check that `worldserver` was rebuilt and that `DevMenu.Enable = 1`.
- **"Dev menu needs a GM account":** raise the account level (`.account set gmlevel`) or lower `DevMenu.MinSecurity`.

## Your races in Create an NPC

You don't have to configure races. When the tab opens, the server reads its own `ChrRaces.dbc` and `CharSections.dbc`, so the list includes every race your server has:

- **Covered:** the stock races, plus any custom race you added to those DBCs, including male-only and female-only races and DBCs in any language.
- **Look counts:** skin, face, hair and so on are counted from your `CharSections`.
- **Your clients:** they draw a race if they have its model files (the same files your players need to play it). Armor and weapons show on every client.

A custom race whose extra customisation (tattoos, horns…) needs a modified client can get named rows through a **look adapter** (see the Help page in game, and `client/DevMenu/DevMenu_CoA.lua` for an example). Without one, its 5 standard rows still work.

## Id ranges

The menu creates new rows in these ranges. If your database already uses them, change the constants at the top of `src/DevMenu.cpp` before building.

| What | Ids |
|---|---|
| NPC types (copies, dressed NPCs), trainers, object types | 9 980 001+ |
| Quests | 9 990 001 – 9 999 999 |
| Talk menus | 9 998 001 – 9 998 999 |
| NPC texts | 16 000 001+ |
| Escort paths | 99 800 000 + quest id |

## Updating

1. Replace the module folder (or run `git pull` inside it) and rebuild `worldserver`.
2. Replace the addon folder and restart the game.

Saved looks, outfits and categories are kept: they live in the world database and in each GM's SavedVariables.

## Uninstalling

1. Remove the `mod-ilusixn-devmenu` folder, re-run CMake and rebuild.
2. NPCs, quests and objects you created stay in your world database as normal rows.
3. Dressed NPCs need the module to show their look. Without it they keep their race's base model.
