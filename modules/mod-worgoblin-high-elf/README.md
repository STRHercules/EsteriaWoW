# Purpose
This repository is my attempt at merging the Worgoblin and AzerothCore High Elf modules, as well as some other DBC-reliant modules. Any two modules that rely on the same DBCs need to be merged manually, unfortunately. This requires making them compatible in certain ways, and at the end of the day, I had to make some editorial decisions that went beyond a simple merger.

## patch-J.MPQ
If you don't like these changes, the optional patch-J.MPQ is a simple patch that contains (client-side and, optionally, server-side) DBCs that disable my taxipath edits, Flying in Azeroth, ARAC's race/class additions, and even interface files that hide the extra races themselves from the character creation screen (but you can safely delete that Interface folder if you want to make them).

Another method is to delete my edited TaxiPath.dbc, TaxiPathNodes.dbc, and AreaTable.dbc from patch-A.MPQ – the ones in patch-J.MPQ are the default enUS ones anyway. However, ChrRaces.dbc is edited to include the custom races.

I also considered making a patch that would camouflage the extra races as existing ones (Worgen –> Night Elf, Goblin –> Orc, High Elf –> Human), but it would be too much work to make it work properly, e.g. not crashing as soon as you get too close to a barber shop. It would also be too much to work to maintain.

## Modpaks
I'm trying out a system for handling DBC files as (idempotent) SQL, inspired by Justurn's [zpaks](https://github.com/ZepplinCore-Development/Zeppelin-Craft/tree/main). The idea is to make even DBC-reliant systems more modular and easier to bulk edit. For now, it's only the Worgoblin DBCs, but I'll try to incorporate all the mods I've used into the modpak format.

## ARAC (All Races All Classes)
Allows all races to be all classes. The updated version fixed some bugs in the original and adds a few spells. I noticed some missing combinations (e.g. Blood Elf Druid) were missing spells in some files, so I have added those in there as well as extending the module to cover Worgen, Goblins and High Elves.

## Worgoblin Module
[![core-build](https://github.com/benjymansy123/mod-worgoblin/actions/workflows/core-build.yml/badge.svg)](https://github.com/benjymansy123/mod-worgoblin/actions/workflows/core-build.yml)

This is a module for [AzerothCore](http://www.azerothcore.org) that adds Worgen, Goblins, and numerous features related to their playability.

### Features
- Worgen as a playable Alliance race and goblins as a playable Horde race
- Optional alpha Worgen models and Gilnean voices
- Mage and warlock class trainers in Teldrassil (I ought to extend this to give ARAC combinations access to trainers in their starting areas)
- Compatibility patches for PlayerBots and Individual Progression modules
- Worgen and Troll druid forms (Horde forms follow skin colour in AC, but the patch makes it so everyone but Tauren defaults to hair colour)
- Running Wild (w/o start animation)

#### NYI Features
- Mount vendors
- Vanilla goblin models
- Two Forms (currently requires lua support to work)

### Important Notes
This module makes *heavy* use of client patching and modification. Because of this, it is recommended to use a [clean, unmodified enUS WoW client](https://www.chromiecraft.com/downloads) as issues have been reported due to use of other clients, such as the one offered from Warmane. The HD patch included on the ChromieCraft website has been known to cause issues with this patch. It is for that reason that it's recommended for you to use the HD patch adapted to the Worgoblin module in particular, which can be found [here](https://github.com/benjymansy123/mod-worgoblin/releases/tag/hd-patch) with instructions on how to install it.

(It may not work with *this* module, however.)

## AzerothCore High Elf
Mod to add High Elves as playable characters on Azeroth Core with support for mod-playerbots. By Abracadaniel22.

### Features
- A new High Elf alliance race is added
- - It shares the same models as the Blood Elf race
- - It shares the same starting zone, reputation, skills as the humans (but Turtle WoW-based racials)
- - High Elves can be any class (except shaman or druid in the non-ARAC version)
- Compatible with HD models

# How to Install

## 1) Replace the DBC files in your AzerothCore Data directory with the ones provided in data/patch-A.MPQ/DBFilesClient

Copy the contents of the DBFilesClient folder (`mod-worgoblin-high-elf/data/patch-A.MPQ/DBFilesClient`) to your AzerothCore `Data/dbc` directory (defined by `DataDir` in `worldserver.conf`). I recommend backing up your DBC folder before overwriting these files.

If you're using the alpha models and/or Gilnean voice files, overwrite the relevant DBC files.

## 2) Copy patch-A.MPQ from (`mod-worgoblin-high-elf/data/patch-A.MPQ`) to your Data folder in your WoW client

Overwrite the relevant files in `patch-A.MPQ/DBFilesClient` if you're using the alpha models and/or Gilnean voice files.

## 2.5) Optional: compatibility patches

### AzerothCore

You can skip this, but certain things won't work, like Goblin racial discounts and Running Wild.

To apply the patch, copy whe-acore.patch to the root of your AzerothCore directory and run the following commands from there:

```
git apply --ignore-space-change --ignore-whitespace whe-acore.patch
git add .
git commit -m "Add worgoblin-high-elf acore patch"
```

### [Playerbots](https://github.com/liyunfan1223/mod-playerbots)

This patch fixes the problem of bots failing to recognize Worgen and High Elf as Alliance races and allows playerbots to spawn as Worgen, Goblins and High Elves.

To apply the patch, copy whe-playerbots.patch to the root of your Playerbots directory and run the following commands from there:

```
git apply --ignore-space-change --ignore-whitespace whe-playerbots.patch
git add .
git commit -m "Add worgoblin-high-elf playerbots patch"
```

There is also a patch for Individual Progression. I tried to merge it too, but I don't use that mod myself and so can't test it. Take it for what it's worth.

## 3) Compile and install AzerothCore

See AzerothCore's [official documentation](https://www.azerothcore.org/wiki/installing-a-module) for more details about compiling and installing modules. If you applied one of the compatibility patches after a previous installation, you will have to recompile AzerothCore.

## 4) Remove signature checks from your WoW executable
Windows users can use [this patcher](https://www.wowmodding.net/files/file/283-wow-335-patcher-custom-item-fix/) created by kebabstorm to patch Wow.exe file (also available from [this](https://github.com/anzz1/WoWPatcher335/releases) GitHub repository). macOS users can download this [pre-patched .app file](https://github.com/benjymansy123/custom-race-ac-12_6_21/releases/download/sig-check/WoW.app.zip), since no easy patcher exists for macOS.

Because WoW uses signature checks so as to not allow Interface files to be modified, we need to remove those checks in order to be able to use custom races. This is accomplished using the patcher included in the repo. Move the patcher into your WoW client directory and run it. Again, feel free to make a backup of your original executable.

There is a longstanding bug in WotLK that causes your mouse to reset to the center of the screen, resulting in frequent disorientation while playing. It requires a patched client executable to fix, which causes compatibility issues with this module. However, you can use the script provided [here](https://github.com/idempotentiation/mod-worgoblin/releases/tag/patched-client-merger) to merge the two patched executables, allowing you to use this module alongside the camera fix.

## 5) Run the provided SQL files against your world database

Some tables in the database override DBC files. I am not sure exactly how that works, but I know that sometimes things don't work until I change the DB to agree with the DBC.

Assuming you are using default names for your databases, log into MySQL and run, e.g.:

```
use acore_world;
source /path/to/modules/mod-worgoblin-high-elf/data/sql/base/world/mod-worgoblin-high-elf.sql;
```

You currently need to run one file at a time.

And with that, you are all done!

# Credits
* heyitsbench and Helias for the [Worgoblin]([url](https://github.com/heyitsbench/mod-worgoblin)) [modules]([url](https://github.com/Helias/mod-worgoblin))
* idempotentiation for the [Worgoblin fork]([url](https://github.com/idempotentiation/mod-worgoblin)) with patches
* abracadaniel22 for the [High Elf custom race]([url](https://github.com/abracadaniel22/azerothcore-highelf)) and [Fly Anywhere]([url](https://github.com/abracadaniel22/mod-fly-anywhere)) modules
* heyitsbench (again) for the original [ARAC]([url](https://github.com/heyitsbench/mod-arac)) module
* ChromWolf for the updated [ARAC]([url](https://github.com/ChromWolf/mod-arac-updated)) module
* gitdalisar for the [Faction Free]([url](https://github.com/gitdalisar/mod-Faction-Free)) module (which I may or may not implement in the future)
* Several people who helped on Discord
