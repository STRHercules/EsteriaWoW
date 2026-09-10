# This is a module for  ![logo](https://raw.githubusercontent.com/azerothcore/azerothcore.github.io/master/images/logo-github.png) AzerothCore
## Hunter and Warlock Starting Pet
[![core-build](https://github.com/dannydefeato/mod-starting-pet/actions/workflows/core-build.yml/badge.svg?branch=master)](https://github.com/dannydefeato/mod-starting-pet/actions/workflows/core-build.yml)
[![CodeFactor](https://www.codefactor.io/repository/github/dannydefeato/mod-starting-pet/badge)](https://www.codefactor.io/repository/github/dannydefeato/mod-starting-pet)

## Description
Module to enable hunters and warlocks to start with a pet/minion

## Features
- Enable/Disable module
- Announcement of enabled module on login
- Hunters start with a configurable race-themed pet
- Random pet name
- Hunters start with Call Pet, Revive Pet, Dismiss Pet, and Feed Pet
- Mend Pet, Eyes of the Beast, Beast Lore, and Tame Beast retain their normal
  class progression
- Hunter pets receive Growl rank 1 with autocast enabled
- Tame Beast remains part of the normal level-10 Hunter quest chain
- Warlocks start with an Imp by default; the minion mask remains configurable

### Default Hunter pets

| Race | Pet |
|---|---|
| Orc | Mottled Boar |
| Dwarf | Young Black Bear |
| Night Elf | Young Nightsaber |
| Tauren | Plainstrider |
| Troll | Bloodtalon Taillasher |
| Blood Elf | Feral Dragonhawk Hatchling |
| Draenei | Ravager Specimen |
| High Elf | Springpaw Cub |
| Broken | Warp Stalker |

Each creature entry can be changed or disabled in `mod_startingpet.conf`.

## Installation
```
1) Simply place the module under the `modules` directory of your AzerothCore source. 
2) Re-run cmake and launch a clean build of AzerothCore.
```

## Edit module configuration (optional)
If you need to change the module configuration, go to your server configuration folder (where your worldserver or worldserver.exe is), copy mod_startingpet.conf.dist to mod_startingpet.conf and edit that new file.

## Credits
- Module for AzerothCore created by [Gozzim](https://github.com/Gozzim)
- AzerothCore: [repository](https://github.com/azerothcore) - [website](http://azerothcore.org/)

## License
This code and content is released under the [GNU AGPL license](https://github.com/Gozzim/mod-starting-pet/blob/master/LICENSE).
