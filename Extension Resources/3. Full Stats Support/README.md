Each of these folders are named for the location they need to be placed in the Baldur's Gate 3 Data folder (most likely `C:\Program Files (x86)\Steam\steamapps\common\Baldurs Gate 3\Data`). When you do so, replace the name of each of these folders with: `WW_CompatibilityExample_c4f7541a-36b5-1354-f8d9-e7fd62c517bf`

## How to Extend Full Stats Support

#### Table of Contents

- [Introduction](#introduction)
- [Descriptions in Transmog Tooltips](#descriptions-in-transmog-tooltips)
- [Enforcing Spell Cooldowns](#enforcing-spell-cooldowns)
    * [Container Spells](#container-spells)
- [Enforcing Unarmored-Only Bonuses](#enforcing-unarmored-only-bonuses)
- [Custom Behaviors](#custom-behaviors)
    * [All Transmogrifications Database](#all-transmogrifications-database)
    * [Equipped Transmogrifications Database](#equipped-transmogrifications-database)
    * [Transmogrification Sources Database](#transmogrification-sources-database)
    * [Other Databases](#other-databases)
    * [Tags](#tags)
    * [Examples](#examples)
- [Complete Example](#complete-example)
- [Automating This Process](#automating-this-process)

### Introduction

Although the stats from our equipment can now be used with a transmogrification, the tooltip still doesn't describe anything it does (which in my experience will make players think that it isn't working), and some types of stats won't work correctly in all circumstances without more customized support.

For example, one of the items in my example mod unlocks a spell with a Short Rest cooldown, but you can easily avoid the cooldown by re-transmogrifying it unless you hook the item up to Transmogrification Lite's cooldown enforcement system. Also, another item in my example should only be able to be equipped by avatars, but without adding special support for this restriction, anyone will be able to equip a transmogrification that uses its stats.

In this section, we'll discuss how to add full support for the most common issues with stats I've seen, and then I'll also describe some of the tools I've built into the core mod that you can use to make your own solutions to things not included here.

### Descriptions in Transmog Tooltips

Because we can't extract much information from an item with the official toolkit, we're also very limited in what we can do to recreate an item's descriptions for transmogrifications. Based on what we've done so far, the tooltip for transmogrified items will only show whether it's clothing or light/medium/heavy armor, its Armor Class, and it might also say "Additional Attributes" depending on the value you set for it in `DB_WW_TL_ArmorComponents`.

To be able to describe more of a transmogrification's stats, I built a system that applies descriptive statuses to the item so that they will appear in its tooltip. For example, the transmogrification's tooltip still can't say "Reduces Fire damage by 3", but it can show a status named "Damage Reduction" in order to broadly describe what it does.

![Tooltips comparison for original item, basic transmog, and complete transmog](https://github.com/WorldWalker42/Transmogrification-Lite/blob/5dc1c8760cdb27241f30ecbc310b55155ede1de8/Extension%20Resources/Assets/TooltipsComparisons.jpg)

Adding these descriptors to the tooltip is very easy - we just need to add a couple values to a much simpler database in the INIT section of the Osiris script that we've already created.

The database we're going to be using this time is:

```
DB_WW_TL_TooltipStatuses(_StatsStatusName, _TooltipName);
```

Replace `_StatsStatusName` with the name of the BOOST status (in quotation marks) that applies the equipment's stats. It should match the third value used for this equipment's entry in the original database (`DB_WW_TL_ArmorComponents`).

Replace `_TooltipName` with the name of the category (in quotation marks) that you want applied to it. The following categories are available by default:
- `AC_CONDITIONAL` - the wearer receives a bonus to their AC that changes or is only applied in certain situations.
- `SAVE_DC` - the wearer's spell save DC is increased.
- `ATTACK` - the wearer's attack rolls (melee or ranged, but NOT spell-based) are increased or made with advantage.
- `ATTACK_SPELL` - the wearer's spell attack rolls (melee or ranged) are increased.
- `DAMAGE` - the wearer deals additional damage or causes damage in new situations.
- `ABILITY` - one or more of the wearer's ability scores are increased.
- `SAVE_THROW` - one or more of the wearer's saving throws (including concentration checks) are increased.
- `RESISTANCE` - the wearer becomes resistant to one or more types of damage.
- `REDUCE_DAMAGE` - damage to the wearer is reduced (separate from being Resistant to a particular damage type).
- `SPELL` - the wearer is granted one or more spells or abilities.

For example, the Gloves of Dexterity give +1 to attack rolls and set the wearer's Dexterity score to 18, so I used this for its tooltip:

```
DB_WW_TL_TooltipStatuses("WW_TL_MAG_BG_OfDexterity_Gloves", "ATTACK");
DB_WW_TL_TooltipStatuses("WW_TL_MAG_BG_OfDexterity_Gloves", "ABILITY");
```

And, because these two attributes fully describe the Gloves of Dexterity's stats, I set its line in `DB_WW_TL_ArmorComponents` to _not_ apply the "Additional Attributes" description.

Note: Each category can only be applied to an item one time, so even if it unlocks two spells when equipped, you should only add one line for it in this database with the `SPELL` category.

Also, the order of the facts in the database will be used for the order of the category descriptions in the tooltip. For consistency, I recommend keeping them in the order that I listed the categories above, but you're of course free to do otherwise.

If you want to create your own category, all you need to do is create a new BOOST status with:

1. A name that starts with `WW_TL_ARMOR_DISPLAY_` and ends with the name of the category (which I recommend to include your mod's identifier)
2. `StatusPropertyFlags` set to `IgnoreResting;DisableOverhead;DisableCombatlog`
3. A `DisplayName` and `Description` that lets the player know what this category describes.
4. It's very nice, but not required, to add a relevant icon.

Now you can use the name of your category with `DB_WW_TL_TooltipStatuses` and it should appear in the item tooltip!

### Enforcing Spell Cooldowns

It's common for equipment to grant the wearer a spell or ability with a cooldown. However, because transmogrification can be used to share equipment stats between lots of items, it's possible to trick the game into letting the player use the spell again before its cooldown is finished. This probably won't happen without intentionally trying to take advantage of it, but because it could be used to significantly alter game balance, I built a system into Transmogrification Lite that keeps track of spell cooldowns and interrupts an attempt to use something before it should be able to be.

In order to activate this system for a piece of equipment, we need to add a fact to 1-2 databases in the INIT section of the Osiris script that we've already made. Only do this for items that have their `_Unique` value set to `1` in `DB_WW_TL_ArmorComponents` because the spell cooldown is shared between all copies of the item, so if multiple copies can be in use at once then it's better not to enforce the cooldown.

The database you need to add to is:

```
DB_WW_TL_ArmorSpells(_StatsStatusName, _SpellName, _CooldownType);
```

Replace `_StatsStatusName` with the name of the BOOST status (in quotation marks) that applies the equipment's stats. It should match the third value used for this equipment's entry in the original database (`DB_WW_TL_ArmorComponents`). For example, I made the status `WW_TL_MAG_Martial_Exertion_Gloves` to recreate the bonuses from the Martial Exertion Gloves, so I would use the name of that status here to enforce its cooldown.

Replace `_SpellName` with the full technical name of the spell/ability (in quotation marks) that needs a cooldown. For example, the Martial Exertion Gloves grant the ability Martial Exertion that has the technical name `Shout_MAG_Martial_Exertion`.

Replace `_CooldownType` with the kind of cooldown this spell or ability has (also in quotation marks). The currently supported options are:
- Once per turn: `TURN`
- Once per combat: `COMBAT`
- Once per Short Rest: `SHORT`
- Once per Long Rest: `LONG`

Here's a complete example for the Martial Exertion ability, which can only be used once per Short Rest:

```
DB_WW_TL_ArmorSpells("WW_TL_MAG_Martial_Exertion_Gloves", "Shout_MAG_Martial_Exertion", "SHORT");
```

A couple of notes about this:

1. If a single piece of equipment unlocks multiple spells/abilities, then you would need to add a fact to the database for each one. The name of the BOOST status will be the same for all of them, but the spell name will be different, and the cooldown might need to change too.

2. Even if multiple pieces of equipment use the same BOOST status for their transmogrification stats, you don't need to add duplicate facts to this database for each one. This is because the cooldown enforcement systems looks for the status being used and not the specific item that's equipped.

#### Container Spells

Enforcing the cooldown for spells and abilities in a container has one more step. For example, Gortash's Gauntlet of the Tyrant unlocks Command, which is a container including five separate spells that can be cast. Casting any one of them needs to activate the cooldown for all of them.

For a spell container, follow the previous steps for JUST the spell container (NOT for any of the spells inside it), like this:

```
DB_WW_TL_ArmorSpells("WW_TL_MAG_Gortash_Gloves", "Target_MAG_Tyrant_Command_Container", "LONG");
```

Next, for each spell inside the container, we need to add a fact to this database: 

```
DB_WW_TL_ArmorSpellContainers(_SpellContainerName, _ChildSpellName);
```

Replace `_SpellContainerName` with the full technical name of the container (in quotation marks) that we used for the other cooldown database. For this example, it would still be `"Target_MAG_Tyrant_Command_Container"`.

Replace `_ChildSpellName` with the full technical name of one of the spells/abilities inside the container (also in quotation marks).

For this example, the final result looks like this:

```
// Container spell cooldown:
DB_WW_TL_ArmorSpells("WW_TL_MAG_Gortash_Gloves", "Target_MAG_Tyrant_Command_Container", "LONG");

// A list of the actual spells that might be used to trigger the container cooldown:
DB_WW_TL_ArmorSpellContainers("Target_MAG_Tyrant_Command_Container", "Target_MAG_Tyrant_Command_Halt");
DB_WW_TL_ArmorSpellContainers("Target_MAG_Tyrant_Command_Container", "Target_MAG_Tyrant_Command_Approach");
DB_WW_TL_ArmorSpellContainers("Target_MAG_Tyrant_Command_Container", "Target_MAG_Tyrant_Command_Drop");
DB_WW_TL_ArmorSpellContainers("Target_MAG_Tyrant_Command_Container", "Target_MAG_Tyrant_Command_Flee");
DB_WW_TL_ArmorSpellContainers("Target_MAG_Tyrant_Command_Container", "Target_MAG_Tyrant_Command_Grovel");
```

Now the cooldown should be properly enforced.

### Enforcing Unarmored-Only Bonuses

Some equipment should only grant AC or another kind of bonus when its wearer does not have any armor equipped. However, the game thinks every transmogrification is clothing even if it's using stats from heavy armor, and so by default the character can receive the unarmored-only bonuses when they're not supposed to.

To solve this, Transmogrification Lite applies the status `WW_TL_WEARING_ARMOR` to characters wearing a transmogrification with stats for light, medium, or heavy armor. We can use this two different ways to correctly enforce unarmored-only bonuses:

1. Anytime `not WearingArmor(context.Source)` is a boost condition, add `and not HasStatus('WW_TL_WEARING_ARMOR',context.Source)`. This is the cleanest solution, but if I would have to override a passive/status in the base game or another mod then I try to avoid it, because overriding resources limits compatibility with other mods that override the same resources.

2. Give the character a new passive whenever they have the status `WW_TL_WEARING_ARMOR` that will counteract the bonus if they're not wearing any normal armor that would disable it. That is, if you can't stop the equipment from giving them +3 AC, then you just need to also give them -3 AC so that 10 + 3 - 3 = 10. This is not a very clean solution and can't undo everything, but it has the broadest compatibility.

Let's look at the second solution in more detail.

First, we need to make the debuff passive, which can be used to undo more than one bonus. It needs to have the following settings:

1. `Properties` is `IsHidden` because the player shouldn't see this passive.

2. `BoostContext` is `OnEquip;OnCreate` so that the debuff is reevaluated every time the character (un)equips something.

3. `BoostConditions` is `not WearingArmor(context.Source)` so that we don't undo the buff if it's already been disabled by the character _also_ wearing normal armor. We only want to undo the buff if all the armor that the character is wearing has been transmogrified.

4. `Boosts` checks whether the character has one or more unarmored-only bonuses and does the opposite to cancel them out.

For example, this debuff passive undoes an imaginary +1 unarmored AC granted by the passive `IDENTIFIER_UnarmoredBonus` as well as a +3 unarmored AC granted by the passive `IDENTIFIER_UnarmoredBonus_Greater`:

```
new entry "IDENTIFIER_ArmorDebuff"
type "PassiveData"
data "DisplayName" "hc81bdb92gb598g1751g9302g0cc4872aa860;3"
data "Properties" "IsHidden"
data "BoostContext" "OnEquip;OnCreate"
data "BoostConditions" "not WearingArmor(context.Source)"
data "Boosts" "IF(HasPassive('IDENTIFIER_UnarmoredBonus', context.Source)):AC(-1); IF(HasPassive('IDENTIFIER_UnarmoredBonus_Greater', context.Source)):AC(-3);"
```

As always, replace `IDENTIFIER` with your mod's unique identifier. Although, in this case you might want to completely rename the debuff passive to be more descriptive.

Next, you need to give the debuff passive to characters in your mod's Osiris script with these rules:

```
IF
StatusApplied(_Character,"WW_TL_WEARING_ARMOR",_,_)
THEN
AddPassive(_Character,"IDENTIFIER_ArmorDebuff");

IF
StatusRemoved(_Character,"WW_TL_WEARING_ARMOR",_,_)
THEN
RemovePassive(_Character,"IDENTIFIER_ArmorDebuff");
```

Now the transmogrification's unarmored-only bonuses should _actually_ be limited to only unarmored characters.

### Custom Behaviors

Of course, part of why modded equipment is so much fun is because it can do entirely new and unexpected things. Unfortunately for adding transmogrification support, this means that I can't provide guidance on everything that might come up. However, I can tell you about some tools that are available for you to use and provide a couple of examples.

Most issues can probably be solved with Osiris scripting (either by doing something directly or by applying extra statuses / passives). If you don't have much experience with this kind of scripting and want to learn more, I recommend reading the official guide [Introduction to Osiris](https://mod.io/g/baldursgate3/r/introduction-to-osiris) and my guide [Understanding Osiris Rules](https://mod.io/g/baldursgate3/r/understanding-osiris-rules).

Transmogrification Lite maintains a handful of Osiris databases that you might find useful in your own script, the definitions of which are described below.

Note: The first time you reference each database in your own script, you will need to include the type of any values you leave unbound. Please see the [Examples](#examples) subsection below for reference.

#### All Transmogrifications Database

First, there's a database that tracks every transmogrified item that currently exists. It's important to remember that each transmogrification has a stats source and an appearance source, and they probably (but don't _have to_) come from different items.

```
DB_WW_TL_TransmogrifiedArmors((GUIDSTRING)_Item, (INTEGER)_Heaviness, (GUIDSTRING)_OriginalTemplateForStats, (STRING)_StatsBoost)
```

`_Item` is the Name_GUID of the transmogrification's game object. This is an instantiation of the appearance source's Root Template.

`_Heaviness` is the same value as the stat source's `_ArmorType` in `DB_WW_TL_ArmorComponents`.

`_OriginalTemplateForStats` is the Name_GUID of the stat source's Root Template (which will match the first column in `DB_WW_TL_ArmorComponents` for the stats source, and which can be used to get more information about it from that database).

`_StatsBoost` is the name of the BOOST status that applies the item's stats (it will match the third column in `DB_WW_TL_ArmorComponents` for the stats source).

In order to determine the appearance source of a transmogrification, use the `GetTemplate` Osiris query with `_Item` and match the result to the second column in `DB_WW_TL_ArmorComponents`.

#### Equipped Transmogrifications Database

There's also a database that tracks which transmogrifications each character has equipped:

```
DB_WW_TL_EquippedTransmogrifications((GUIDSTRING)_Character, (ITEM)_Item)
```

`_Character` is the Name_GUID of the character who has equipped the transmogrification `_Item`. Each character might have multiple facts in this database if they have transmogrifications equipped in multiple slots at once.

Note that `_Item` should match a value for `_Item` in the previous database (`DB_WW_TL_TransmogrifiedArmors`).

Another important thing to know about this database is that there's a short delay between when a character equips a transmogrified item (which will trigger events like `Equipped(_Item, _Character)`) and when a fact is added to this database (which is also when the BOOST status with the item's stats is applied to the character). This means that, depending on the use case, you might want to use the normal event `Equipped` or a database condition for `DB_WW_TL_EquippedTransmogrifications` to trigger a rule, but you probably never want to use them both in a rule together because it's likely to cause issues.

#### Transmogrification Sources Database

Finally, there's a database that keeps a record of the original game object that a transmogrification used as its stats source. You can use `DB_WW_TL_TransmogrifiedArmors` to get the Root Template of a transmogrification's stats source, but not the specific item, so you'd need to use this database for that.

```
DB_WW_TL_TransmogrificationStatsSources((GUIDSTRING)_Source, (GUIDSTRING)_Transmogrification)
```

`_Source` is the Name_GUID of the original game object used as the stats source.

`_Transmogrification` is the Name_GUID of the transmogrified game object, which has been called `_Item` in the previous databases.

Note that if a transmogrification was made without a stats source (which happens when a character takes the appearance of an item for a slot they don't have anything equipped in), then it won't have a fact in this database.

Also, if a transmogrification is created with stats taken from another transmogrification, the new item's stats source is still considered to be the original non-transmogrified item.

#### Other Databases

There are two more databases you might want to know about, but they're used differently. Rather than writing Osiris rules that use these databases, instead you just need to add new facts to them in the INIT section of your own script.

For example, some statuses should be removed when a character is wearing armor, but this won't happen by default with transmogrified armor because the game doesn't recognize it as such. You could resolve this as described in the **Enforcing Unarmored-Only Bonuses** section, but using a status or passive to remove another status is kind of overkill when it can be removed directly by the Osiris rule instead. The rule to do this is already written in Transmogrification Lite's script, and so all you need to do is qualify another status to be removed by transmogrified armor by addding `DB_WW_TL_UnarmoredOnlyStatuses(_Status);` to the init section of your script, where `_Status` is replaced with the name of the status in quotation marks (e.g. `DB_WW_TL_UnarmoredOnlyStatuses("MAGE_ARMOR");`).

Similarly, most polymorph shapes are supposed to disable armor bonuses, but if you want to make one an exception to this behavior then you can also add a fact to the INIT section for the database `DB_WW_TL_PolymorphStatusExceptionsForAC(_PolymorphStatus)` where you replace `_PolymorphStatus` with the name of the polymorph status in quotation marks.

#### Tags

Because the AC calculations in Transmogrification Lite are so deeply woven into the mod, I made it so that you can turn certain parts of it on or off by applying different tags to a character.

This is mostly only helpful for supporting equipment that uses the `ACOverrideFormula(...)` boost, which will cause the normal AC calculation to stack on top of the transmog AC calculation unless we alert Transmogrification Lite that the AC is being overridden by using the tag(s).

Equipment can apply the following tags to its wearer:

1. `WW_TL_CUSTOM_AC_OVERRIDE` (UUID: `44ca0460-b271-4118-a5a9-4c8756905d72`): This character will receive -10 AC to undo the base AC given from the formula override, and they will not receive a duplicate DEX bonus. If they are wearing armor, some or all of their DEX bonus will be undone.

2. `WW_TL_MONK_AC_OVERRIDE` (UUID: `020c9b7b-dd2b-4ce5-a88b-9f42c7c5aa1a`): This character currently has a modded equivalent to Unarmoured Defense for Monks. They will receive the same debuffs as `WW_TL_CUSTOM_AC_OVERRIDE`, except their WIS bonus will also be undone if they are wearing armor.

3. `WW_TL_BARB_AC_OVERRIDE` (UUID: `a0381c58-d848-4c6d-a4a4-f014eb056d77`): This character currently has a modded equivalent to Unarmoured Defense for Barbarians. They will receive the same debuffs as `WW_TL_CUSTOM_AC_OVERRIDE`, except their CON bonus will also be undone if they are wearing armor.

4. `WW_TL_ALT_AC_MOD` (UUID: `fd51851b-3d8d-4e2e-baf6-e8fd0c480e91`): This character is currently using a different ability modifier than DEX for their primary AC bonus. This does not need to be used if another ability modifier is added on top of DEX, only if DEX shouldn't be added at all. Tagging a character with this basically disables all of the AC calculation passives so that you have a blank slate with which to work.

#### Examples

Let's take a look at a really quick example of adding support for an item that should only be able to be equipped by an avatar (even if its stats are being used in a transmogrification):

```
IF
Equipped(_Item, _Character) // this rule is triggered for evaluation when _Character equips _Item
AND
DB_WW_TL_TransmogrifiedArmors((GUIDSTRING)_Item, (INTEGER)_, WW_CE_ARM_Breastplate_WalkersPlate_c97df1d0-3011-47f4-b859-3ea9e3664997, (STRING)_) // _Item is a transmogrification using the stats we want to limit
AND
IsTagged((GUIDSTRING)_Character, (TAG)AVATAR_306b9b05-1057-4770-aa17-01af21acd650, 0) // _Character is NOT an avatar
AND
ResolveTranslatedString("WW_CE_AvatarOnlyErrorMessage", _ErrorMessage) // get an error message from a localization file
THEN
Unequip((CHARACTER)_Character, (ITEM)_Item); // unequip _Item from _Character because they shouldn't be able to use it
OpenMessageBox(_Character, _ErrorMessage); // put the error message on screen so the player understands what happens
```

This rule is fairly simple Osiris logic to unequip an item after a character equips it, but it can only know which items to unequip by checking the database `DB_WW_TL_TransmogrifiedArmors` to see whether the stats come from the restricted equipment.

Let's look at another example of how to implement set bonuses, where a character receives a status if they're wearing every piece of equipment in a set. This can usually be done just by checking that the character has equipped items instantiated from the Root Templates we want, but transmogrifying the equipment means that the Root Template will only correspond to the item's appearance, and we only care about its stats.

Instead, we can set up a custom query that checks whether a character is using a Root Template's stats by either having the original item or a transmogrification of it equipped:

```
// One way to satisfy the query is if _Character is wearing an item instantiated from the original Root Template
QRY
QRY_WW_CE_UsingStatsFromTemplate((CHARACTER)_Character, (GUIDSTRING)_Template)
AND
DB_WW_TL_ArmorComponents(_Template, _, _, _, _, _Slotname, _, _) // get the _Slotname that corresponds to _Template
AND
GetEquippedItem(_Character, _Slotname, _Item) // get the item currently equipped in that slot
AND
GetTemplate(_Item, _Template) // and then require that item to have been instantiated from _Template (i.e. it's the original item)
THEN
DB_NOOP(1);

// Another way to satisfy the query is if _Character is wearing a transmogrification using the stats that correspond to the original Root Template
QRY
QRY_WW_CE_UsingStatsFromTemplate((CHARACTER)_Character, (GUIDSTRING)_Template)
AND
DB_WW_TL_TransmogrifiedArmors(_Item, _, _Template, _) // get all the existing transmogrifications using _Template as its stats source
AND
DB_WW_TL_EquippedTransmogrifications((GUIDSTRING)_Character, (ITEM)_Item) // and then check if _Character has equipped any of them
THEN
DB_NOOP(1);
```

We can now use the custom query `QRY_WW_CE_UsingStatsFromTemplate` to easily check for what we want. For example, if there are two items in our equipment set, we can check for having them both equipped (regardless of whether they've been transmogrified) as follows:

```
QRY
QRY_WW_CE_EntireSetEquipped((CHARACTER)_Character)
AND
QRY_WW_CE_UsingStatsFromTemplate(_Character, WW_CE_ARM_Breastplate_WalkersPlate_c97df1d0-3011-47f4-b859-3ea9e3664997)
AND
QRY_WW_CE_UsingStatsFromTemplate(_Character, WW_CE_ARM_Boots_WalkersPlate_39001a4c-8a06-47d9-8e22-5b5a9b545a5b)
THEN
DB_NOOP(1);
```

All that's left to do is hook the custom query `QRY_WW_CE_EntireSetEquipped` into the relevant events and then apply/remove the set bonus status as needed. For a complete example, I recommend looking at my [example script for full stats support](https://github.com/WorldWalker42/Transmogrification-Lite/blob/main/Extension%20Resources/3.%20Full%20Stats%20Support/Mods%20folder/Story/RawFiles/Goals/GLO_Transmogrification_WW_CE.txt).

### Complete Example

As before, a complete example that has full stats support is available above.

Note that the set bonus added to this version of my example mod does not actually apply any bonuses, it's just a visual effect to demonstrate that it's working.

### Automating This Process

The Python script [discussed before](https://github.com/WorldWalker42/Transmogrification-Lite/tree/main/Extension%20Resources/1.%20Appearance-Only%20Support#automating-this-process) can also do a decent job at generating the BOOST statuses and tooltips database, but it's far from perfect at these tasks, so its output should be double-checked and probably needs to be manually completed.

Also, the script can't make the editor files for the BOOST statuses. It only makes the final / generated text file that gets packaged with the mod. If your mod doesn't have any other BOOST statuses, you will need to add `Stats\Generated\Data\Status_BOOST.txt` to your mod's Public directory. If this file already exists, you can just copy and paste the script's output into it, but be aware that whatever you paste in will be lost the next time you reload the project's stats in the toolkit because these statuses don't exist in the editor file. If you're still in active development, I recommend making these statuses manually in the toolkit to avoid them being overwritten.

To tell the script to generate stats, you just need to enter `1` after the previously described arguments in the console command to run it. Also, to get more complete tooltips, it's preferable to also give it a relative file path to a Passives file if the armor stats reference one.

The full console command to run the script with stats support ends up something like this:

```
python3 script.py IDENTIFIER relative/path/to/lsx/files relative/path/to/armor/stats output_directory 1 relative/path/to/passives
```

Make sure to read the script's console output for directions on how to review and complete its work.