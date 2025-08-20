Each of these folders are named for the location they need to be placed in the Baldur's Gate 3 Data folder (most likely `C:\Program Files (x86)\Steam\steamapps\common\Baldurs Gate 3\Data`). When you do so, replace the name of each of these folders with: `WW_CompatibilityExample_c4f7541a-36b5-1354-f8d9-e7fd62c517bf`

## How to Extend Basic Stats Support

#### Table of Contents

- [Introduction](#introduction)
- [BOOST Status](#boost-status)
    * [One-Time Setup](#one-time-setup)
    * [For Each Item](#for-each-item)
- [Finishing the Database Entries](#finishing-the-database-entries)
- [Complete Example](#complete-example)

### Introduction

Note: This guide assumes that you've already read the guide on [extending appearance-only support](https://github.com/WorldWalker42/Transmogrification-Lite/tree/main/Extension%20Resources/1.%20Appearance-Only%20Support).

To also be able to create transmogrifications that use your equipment's stats, we need to do a couple more things:
1. Create a status effect that mimics the equipment's stats
2. Fill out the remaining values in the line added to the Osiris script

### BOOST Status

Let's start with creating the status effect (specifically a BOOST type status) that mimics the original item's Armor stats. This will allow Transmogrification Lite to freely apply it to any character without them having to equip a specific item.

#### One-Time Setup

First, we should create a parent status that all of the others will inherit from. This lets us set certain technical details one time (like not removing the status after a long rest) and then not have to worry about it again. Also, if we ever need to change something for every single status, we can do so very easily through the parent status.

In your mod's `Status_BOOST` file (which is in the Stats Editor, if you haven't worked with one before), create a new status that has this EXACT name: `WW_TL_ARMOR_STATS`

Next, assign it the following values:
- `DisplayName` is "Transmogrified Equipment"
- `StatusPropertyFlags` are:
    * `IgnoreResting`
    * `DisableOverhead`
    * `DisableCombatlog`
    * `DisablePortraitIndicator`
    * `ApplyToDead`

If you're interested to know, the benefit of giving this status the exact same name as one that exists in Transmogrification Lite is that the mod that is loaded last will override the other versions of the status. So, Transmogrification Lite can be loaded after all equipment mods to have its most up-to-date version of the parent status be applied to all extensions automatically. This technically means you don't have to set the `StatusPropertyFlags` in your mod's version of the status, but I strongly recommend that you do because they're not strict dependencies and so it would be very easy to get the load order wrong, which would completely mess up the behavior of _every_ transmogrification without them being set.

#### For Each Item

Now you can create a BOOST status for each piece of equipment you want to add stats support for. This process is mostly a matter of copying and pasting cells between the `Armor` file and the `Status_BOOST` file:

1. Create a new status with the name of the armor stats you're recreating plus your mod's unique identifier (e.g. for the stats `MAG_DarkJusticiar_HalfPlate` I made the status `WW_TL_MAG_DarkJusticiar_HalfPlate`). If this is already the name for the armor stats, you need to add something else (like `TL` for Transmogrification Lite compatibility), because it won't work if they have the same name.

2. Set its parent to `WW_TL_ARMOR_STATS` that we created in the previous section

3. Copy-paste the original `Boosts` column into the one for this status. If it has a penalty to stealth from being medium or heavy armor, don't copy the penalty, because this is handled automatically somewhere else.

4. If the original stats has a value in the `ArmorClass` column (even if it's just inherited), add `AC(X);` to this status' `Boosts` column. For example, the Helldusk Armour has an AC 21 and the boost `UnlockSpell(Shout_MAG_Infernal_Fly)`, so the final boost for its status is `AC(21);UnlockSpell(Shout_MAG_Infernal_Fly)`.

5. Copy-paste the original `Passives` column into the one for this status.

6. If the original stats has a value in the `StatusOnEquip` column, then for each status is applies:

    * Add `ApplyStatus(STATUS_NAME, 100, -1);` in this status' `OnApplyFunctors` column (make sure to replace `STATUS_NAME` with the name of the status).

    * Add `RemoveStatus(STATUS_NAME);` in this status' `OnRemoveFunctors` column (again, replacing `STATUS_NAME`).

    * For example, the original armor stats for the Boots of Persistence has the `StatusOnEquip` column `MAG_FREEDOM_OF_MOVEMENT;MAG_END_GAME_LONGSTRIDER`, and so the status that I made for it has the `OnApplyFunctors` column `ApplyStatus(MAG_FREEDOM_OF_MOVEMENT,100,-1);ApplyStatus(MAG_END_GAME_LONGSTRIDER,100,-1)` and the `OnRemoveFunctors` column `RemoveStatus(MAG_FREEDOM_OF_MOVEMENT);RemoveStatus(MAG_END_GAME_LONGSTRIDER)`

7. I haven't seen any equipment stats using the StatsFunctor or other columns, but theoretically if one did then you should copy those too.

For a complete example, here's the original stats for the Armour of Persistence:

```
new entry "MAG_EndGame_Plate_Armor"
type "Armor"
using "ARM_Plate_Body_2"
data "RootTemplate" "fb2ff6d1-3096-4904-813c-a448e3fbec4d"
data "ValueUUID" "adfdafe5-f4da-4c64-a1e6-a33d626437d2"
data "Rarity" "VeryRare"
data "PassivesOnEquip" "ARM_MagicalPlate_2_Passive;MAG_MAG_EndGame_Plate_Armor_Passive"
data "StatusOnEquip" "MAG_BLADE_WARD;MAG_END_GAME_RESISTANCE"
data "Unique" "1"
```

And here's the status I made to mimic it:

```
new entry "WW_TL_MAG_EndGame_Plate_Armor"
type "StatusData"
data "StatusType" "BOOST"
using "WW_TL_ARMOR_STATS"
data "Boosts" "AC(20)"
data "Passives" "ARM_MagicalPlate_2_Passive;MAG_MAG_EndGame_Plate_Armor_Passive"
data "OnApplyFunctors" "ApplyStatus(MAG_BLADE_WARD,100,-1);ApplyStatus(MAG_END_GAME_RESISTANCE,100,-1)"
data "OnRemoveFunctors" "RemoveStatus(MAG_BLADE_WARD);RemoveStatus(MAG_END_GAME_RESISTANCE)"
```

Notice that the original stats doesn't have a `Boosts` column or an `ArmorClass` column, but for the status I had to add a `Boosts` column for the AC that the original inherits from `ARM_Plate_Body_2`.

If an item does nothing except provide a basic AC between 10-18, like the Simple Robe, then you can skip this step and use one of my pre-made statuses in the next step. If it adds an AC outside of this range, then you'll still need to make your own.

### Finishing the Database Entries

As before, in the INIT section of your Osiris script, you will need to have the following line with the values filled in for each piece of equipment:

```
DB_WW_TL_ArmorComponents(_Template, _AppearanceTemplate, _StatsStatusName, _ArmorType, _DisplayAC, _Slot, _Unique, _AdditionalAttributesTooltip);
```

If you already added this line for appearance-only support, don't add a second line for the same item - you just need to replace the default values with ones that are specific to this item's stats. This time, let's go over what every single value should be:

1. Replace `_Template` with the Name_GUID for the equipment's original Root Template.

2. Replace `_AppearanceTemplate` with the Name_GUID for the equipment's appearance-only Root Template.

3. Replace `_StatsStatusName` with the name of the BOOST status we created in the previous step. Enter the name as a string (that is, it should be surrounded by quotation marks - the status `WW_TL_MAG_EndGame_Metal_Boots` should be entered as `"WW_TL_MAG_EndGame_Metal_Boots"`). If this item just adds an AC between 10-18, you can use `"WW_TL_AC_10"`, `"WW_TL_AC_11"`, ..., `"WW_TL_AC_18"`. If this item does not do anything, not even adding some AC, then enter `"NULL"`.

4. Replace `_ArmorType` with a number indicating the type of armor it is:
    - `-1` for camp clothes and shoes
    - `0` for clothes
    - `1` for light armor
    - `2` for medium armor
    - `3` for medium armor that applies disadvantage on stealth
    - `4` for heavy armor
    - `5` for medium armor that lets the wearer add their full Dexterity modifier to their AC (such as the Armour of Agility)

5. Replace `_DisplayAC` with the number for its Armor Class bonus.

6. Replace `_Slot` with `"Breast"`, `"Helmet"`, `"Gloves"`, `"Boots"`, or `"Cloak"` depending on which equipment slot this item goes into.

7. Replace `_Unique` with `0` to let any number of copies of this item's stats be in use at the same time, or `1` to only let one of them be used at a time. The more items that are unique, the less that game balance is altered. At the very least, anything that grants a spell / ability with a cooldown should be set to unique or else there can be some weird behavior.

8. Replace `_AdditionalAttributesTooltip` with `0` to not add the "Additional Attributes" description to this item's tooltip, or `1` to add it. (More on this in the [Full Stats Support guide](https://github.com/WorldWalker42/Transmogrification-Lite/tree/main/Extension%20Resources/3.%20Full%20Stats%20Support). In the meantime, you can leave it at `0`.)

Now that we've covered what every value means, let's take another look at the example used in the appearance-only section:
```
DB_WW_TL_ArmorComponents(ARM_Robe_B_69302808-57a0-4fbb-9938-137bce5421d1, ARM_Robe_B_WW_TL_01f1643b-363b-42e0-84c4-44fe7851b2c7, "WW_TL_AC_10", 0, 10, "Breast", 0, 0);
```

Let's break it down:
- The status `WW_TL_AC_10` gives the character 10 AC but does not grant any other bonuses
- The armor type is 0 because these robes are clothes
- The display AC is 10 to match the BOOST status's effect
- The slot is "Breast"
- It does not enforce unique stats because it's such a basic item that won't mess with game balance even if everyone uses it
- It does not use the "Additional Attributes" tooltip option because everything it does is described by its AC value

Let's look at another example of the Steelwatcher Helmet:
```
DB_WW_TL_ArmorComponents(MAG_Helmet_Watcher_A_c2ef4013-e6d1-48da-99f0-db486c223a90, MAG_Helmet_Watcher_A_WW_TL_faba36f5-6293-41eb-8f71-c59ce9861443, "WW_TL_MAG_Helmet_Human_Watcher", 2, 0, "Helmet", 1, 1);
```

Breaking it down:
- It uses a custom BOOST status `WW_TL_MAG_Helmet_Human_Watcher` to give the character Darkvision, immunity to blindness, and advantage on CON saves
- Its armor type is `2` because it's medium armor
- Its display AC is `0` because it does not provide an AC boost
- It has the helmet slot
- It only allows one copy of its stats to be used at a time because it has more meaningful bonuses that could alter game balance
- It uses the "Additional Attributes" tooltip option because Transmogrification Lite doesn't have tooltip categories to describe the item's Darkvision and status immunity (more on this later), so we need to indicate that it does more stuff

### Complete Example

Now people can also use the stats of your equipment with the appearance of any other supported item!

I've added basic stats support to my example mod. The .pak and project files are available above.

Notice that when you take the stats of one of these items, the tooltips of the transmogrifications will only show the armor type, AC, and maybe "Additional Attributes", but nothing else specific. This will be added in the next section. You can also have any character equip the item that should be limited to just the avatar by taking its stats for a transmogrification, as well as a few other subtle issues.