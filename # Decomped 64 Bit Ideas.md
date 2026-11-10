# Decomped 64 Bit Ideas

# Ability to places houses anywhere*
* Within reason - perhaps not cities - also need to make sure the houses do not overlap/interfere with quests, events, existing buildings, cave entrances, etc etc.

# Housing Quick Ideas
- Add 'Sales' profession 
    - Gain experience by making sales
    - Offer incentives such as increased profit, more items for sale, etc
- Add 'Homemaker'/'Landlord' profession
- Add 'Woodworking' profession
- Add ability to rent out houses to other players
    - `Player A` constructs house, adds decor, customized it and can then 'list' it on an internal 'real estate' browser
    - `Player B` must pay `X` (set by player A) per `Y` (day/week/month - set by `Player A`)


# Proximity Voice Chat
- Addon settings include settings such as:
    * Audio Device
    * Audio Quality
    * PTT / Toggle / Always on / Voice Detection
    * Rebind PTT/Toggle keys
    * Access (Everyone can hear, Faction can hear, Party can hear, Guild can hear, friends can hear, off)
- Applies a 'now speaking' animation above the character that is speaking
    - Also shows the player who is speaking a live 'now speaking' with audio visualizer bar
- Players with similar Access settings can hear eachother when speaking

# Battlemon
- Configure Spawns to make more sense
    - Add server admin addon panel with knobs
- Configure move learning
    - Have mon learn moves like they would in the mainline games
- Add following pokemon
    - Ability to have a select pokemon follow the player around in the world
- Configure stats to be appropriate
    - Base stats, curves, etc
- Include IV/EV
- Breeding
- Pokemon Trainer Profession
    - In src, not implemented
- Pokemon Item Vendors
- Pokemon Items
    - Potions, balls, berries, etc
- PokeCenter
- Poke Box
    - 'Digital' Pokemon Storage
- Trading
    - Ability to trade players directly or remotely
- Battling
    - Ability to battle players directly or remotely
- Pokemon converted to WoW Items
    - Pokeball containing pokemon
    - Ability to be sold on AH 

## Scaling
- Option in Char Creation
    - Item Scaling
    - World Scaling

## Add ability to save and share builds
- export to code
- upload to server
    - server browser for builds
* This is added directly into the character advancement screen

## Balance all CoA abilities/talents to 80

## Develop NEW starting zones
- Naga Zone
- Tuskarr Zone
- Troll Zone
- Gobline Zone
- Worgen Zone
- Look at future xpac cores to potentially extract starting zone data/maps for;
    - Allied Races
        - Pandaren, etc
    - Skyborne

## Investigate if we need to integrate anything for new custom CoA resources, such as UI etc

## Investigate why it is marking all classless characters as 'paladin', perhaps change that to 'Hero'

## Finish Centaur/Ethereal Racials
- Utilize ethereal after image

## CoA Manastorm in its' entirety 

## Two-way Discord hook for in-game world chat

# Character Creation Overhaul
- Experience Rate (Scaling Toggle?)
- Challenge Modes

## Faction Wars around the world

## Traveling Caravans
- Has gaurds
- Sells basic items, can be attacked

## Traveling Merchants
- Cannot be attacked
- Sells exclusive stuff

## Random Encounters in the Wild
- Bounty Hunters
- Assassins
- Camps
- Monsters (Beasts/Demons)
- Roaming Bosses

## Ad-Hoc Quests 
- Procedural quests
- Quest board

## Camping / Survival
- Hunger / Thirst
- Temperature
- Disease/Sickness

## Farming
- Ability to grow/harvest crops

## Professions
- Farming
- Woodcutting
- 

## CoA
- Challenges and dungeon difficulty, Manastorm, Bazaar, item scaling, mystic enchants, Warcraft Reborn “Hero” classes and spell twins, the Wildcard cards, prestige, XP hotspots and tuning multipliers.


## Skateboarding
- https://github.com/LANCommander/TonyWasAProSkater
- https://github.com/mchughalex/skate3recomp


## Cars
- https://github.com/codepdbh/nfsmwpc-recompiled
- https://github.com/HarbourMasters/SpaghettiKart


## Pokemon
- https://github.com/bryanthaboi/gen1recomp


## DRUGS
- Impl

## Gambling

## Housing


Build the classless resource bars into the dragonUI natively (mana, energy, rage)

Make all reputation account-wide











## Mount: creature/kareshfox/kareshfox.m2;6051323

# Character select is a live map of Azeroth, with a visible heatmap/icons showing where all of your characters currently are in Azeroth when they were logged out
    - Picking a character will zoom in on the world to where that respective character is, zooming in to be over the shoulder of the character - then becomes playable
    - I want a seamless transition between logging in, clicking a character and walking around in game. 

## Ability to have multiple pets at once
- New families to be tamed
- Ride hunter pet ability

## Built-In Addon Repository
- In-game browser accessible from the char select screen
    - Browser will link to a github repository of addons and list them all
    - Browser GUI will have tabs for categories
    - Browser GUI will have a search bar
    - Addons will be able to be clicked, and when clicked - prompts the user if they want to download and install - which will do in real-time and refresh the LUA making sure the addon is present and ready for use, automatically enabled
    - The default addon window will allow users to uninstall addons installed from the browser completely
* The user should still be able to manually install addons the traditional way 

## Native controller Support

## Mobile Client 

## Gambling/Casinos
-  Ingame minigames like chess, checkers, cards

## Companion Pet Overhaul
    * Usefulness
        - Loots corpses
        - Acts as target dummy/distracts enemies
        - Must keep happy/fed/watered (tamagatchi)
        - Levels up with experience
            - Experience gained from acts like looting, playing, maintaining happiness

## Journey Companion
    - NPC in Capital City (Stomwind, Orgrimmar, Dalaran) will allow the player to Hire a companion to adventure with them.
        - The NPC will ask the player what race they would like to hire, presenting the player will all availalble playable race as options
        - The player will then be able to customize the companion as if it were a player, hair color, hair style, etc. this appearance saves and remains persistent. 
        - The player can return to the capital city NPC to retrieve their companion should they ever lose them (at a small fee).
    - Upon hiring, the companion matches their masters's level and gains relative stats
    - Companions will have unique stats - just like players
    - Companions will have unique levels, and will gain experience/level along with their master
    - Companions will be able to equip gear such as Armor, Trinkets, Weapons, etc - gaining the bonuses of them as if they were a player. 
    - Companions will have their own dedicated GUI, just like the player has for their 'Character' screen - it will have stat display, model displauy, equipment paperdoll etc that the player can access to change their armor
    - Companions will have spellbooks, and talents - just like players
    - Companions can be revived by right-clicking when they die, or revived with a spell (Resurrect, etc if the player has it)
    - The Companion can Loot Corpses for the player
    - The Companion can distract enemies (Tank/aggro style or training dummy style)
    - Happiness/Hunger/Thirst/Rest levels for the companion
    - Companions mount up when the player does, and dismounts when they do as well
        - Companion gets into passenger seat of any 2+ seater their owner mounts up on 
    - Companions have their own respective inventories which the player can access
    - Companions follow their master into dungeons, raids and do not effect player party count
    - Companions have configuable combat AI (Melee DPS, Ranged DPS, Magic User, Healer/Assist, Tank) where they use appropriate skills/talents
    - Companion can auto-pick their own abilities/talents or the player can set them themselves (player override takes priority)
    - When a player has a hired companion, show the companion on the character select screen as if they were a hunter pet 
    - The companion will have periodic and incidental dialogue
        - random chatter, coughs, sneezes, sighs, etc
        - calls out enemies that may have aggroed
        - enters combat
        - new enemies enter combat
        - low health
        - low food
        - low water
        - tired
        - leaves combat
        - loots corpses