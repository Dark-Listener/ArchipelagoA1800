# Anno 1800

## What do I need to do to randomize Anno 1800?

See full instructions on [the setup page](setup_en.md)<!--(/tutorial/Anno%201800/setup/en)-->.

## Where is the options page?

The player options page for this game would usually contain all the options you need to configure and export a config
file. However, this is a custom apworld, so you'll have to either generate the templates yourself or use the template
file in the download. See the setup page for details.

## What does randomization do to this game?

In Anno 1800, the building, expedition and certain recipe unlocks are shuffled, causing them to be unlocked in a
non-standard order. Frequently, luxury goods will be available later than usual. You might even have to import goods
from other sessions that you'd usually have available on location!

Note: Ornaments are currently excluded.

## What's the goal?

Your goal is to reach 5000 investors, 1500 obreros, 750 technicians, 7000 scholars and 4000 tourists at this stage of
the Archipelago world. This is, of course, configurable.

## What are locations?

Whenever you'd normally unlock a building in Anno 1800, you instead send a location check to the server. This often
means you send multiple checks at once at a certain population threshold, for example 5 checks at 100 farmers.

Additionally, each expedition that unlocks a new session is also a location check. Should you enable "The Passage", the
randomizer will expect you to have at least Artisans before you must make your trip to "The Arctic" due to the
difficulty of the expedition (Artisans unlock the Clipper).

Certain recipe buildings also have location checks for their recipe unlocks (specifically Restaurant, Cafe, Bar and
The Iron Tower). These have various interesting requirements and become available with the Tourist Season DLC.
RNG-heavy recipe unlocks are excluded from having progression items.

## What about DLCs?

The follwing DLCs are supported:
* Sunken Treasures
* Botanica
* The Passage
* Seat of Power
* Bright Harvest
* Land of Lions
* Docklands
* Tourist Season

Docklands is strongly discouraged as it would render the randomizer pointless. There is an option to toggle its logic
(default: no Docklands logic), that allows you to add it to your game without the randomizer intending you to get half
of your goods via Docklands.

If you enable unsupported DLCs in your savegame, the buildings will unlock as they would in without mods. For example,
the docklands complex will unlock at 250 artisans with Docklands enabled.

## What about incidents?

Currently, availability of institutions is guaranteed by the end of the population that usually unlocks the incidents.
For example, a fire station is guaranteed before you need to reach workers as fires usually unlock at 150 farmers.
Additionally, incidents can only occur once you unlocked the respective institution - which does not necessarily mean
you have the materials to build said institution.

## What about NPCs?

Currently, NPCs are not supported and ignored. This means you can get steel beams or other goods before the randomizer
expects you to.

## What about socketed items?

Currently, socketed items are not supported and ignored. This means you can use alternate production items to acquire
goods before the randomizer expects you to.

There are exeptions for some specific recipe unlocks where the vanilla requirements for the items are assumed.

## The game shows (strange) unlock requirements. Why and what do they mean?

Anno 1800 automatically shows the player how to unlock revealed but locked buildings. This is not preventable without
breaking local (=serverless) play. It is planned to show these revealed buildings as proper hints to Archipelago at
some point. Strange requirements, like empty strings, "continue your journey", or populations from disabled DLCs occur
when the building unlock is not located locally or at a non-standard locations.

Similarly, some location names in Archipelago may still include names from disabled DLCs.
