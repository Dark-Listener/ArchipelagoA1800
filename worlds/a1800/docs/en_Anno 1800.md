# Anno 1800

## What do I need to do to randomize Anno 1800?

See full instructions on [the setup page](setup_en.md)<!--(/tutorial/Anno%201800/setup/en)-->.

## Where is the options page?

The player options page for this game would usually contain all the options you need to configure and export a config
file. However, this is a custom apworld, so you'll have to either generate the templates yourself or use the template
file in the download. See the setup page for details.

## What does randomization do to this game?

In Anno 1800, the building unlocks are shuffled, causing buildings to be unlocked in a non-standard order. Frequently,
luxury goods will be available later than usual. You might even have to import goods from other sessions that you'd
usually have available on location!

Note: Ornaments are currently excluded.

## What's the goal?

Your goal is to reach 1 artisan at this early stage of the Archipelago world.

## What are locations?

Whenever you'd normally unlock a building in Anno 1800, you instead send a location check to the server. This often
means you send multiple checks at once at a certain population threshold, for example 5 checks at 100 farmers.

Additionally, each expedition that unlocks a new session is also a location check.

## What about DLCs?

The follwing DLCs are supported:
* Sunken Treasures
* Botanica
* Seat of Power
* Bright Harvest

If you enable unsupported DLCs in your savegame, the buildings will unlock as they would in without mods. For example,
the docklands complex will unlock at 250 artisans with Docklands enabled.

## What about incidents?

Currently, availability of institutions is guaranteed by the end of the population that usually unlocks the incidents.
For example, a fire station is guaranteed before you need to reach workers as fires usually unlock at 150 farmers.
Additionally, incidents can only occur once you unlocked the respective institution.

## What about NPCs?

Currently, NPCs are not supported and ignored. This means you can get steel beams or other goods before the randomizer
expects you to.

## What about town hall items?

Currently, townhall items are not supported and ignored. This means you can use alternate prouciton items to acquire
goods before the randomizer expects you to.

## The game shows (strange) unlock requirements. Why and what do they mean?

 Anno 1800 automatically shows the player how to unlock revealed but locked buildings. This is not preventable unless
 without breaking local (=serverless) play. It is planned to show these revealed buildings as proper hints to
 Archipelago at some point. Starnge requirements, like empty strings, "continue your journey", or populations from
 disabled DLCs occur when the building unlock is not located locally.

 Similarly, some location names in Archipelago may still include names from disabled DLCs.
