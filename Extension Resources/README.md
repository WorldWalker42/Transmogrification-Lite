## Table of Contents

- [Introduction](#introduction)
- [How to Use These Resources](#how-to-use-these-resources)
    * [Appearance-Only Support](https://github.com/WorldWalker42/Transmogrification-Lite/tree/main/Extension%20Resources/1.%20Appearance-Only%20Support)
    * [Basic Stats Support](https://github.com/WorldWalker42/Transmogrification-Lite/tree/main/Extension%20Resources/2.%20Basic%20Stats%20Support)
    * [Full Stats Support](https://github.com/WorldWalker42/Transmogrification-Lite/tree/main/Extension%20Resources/3.%20Full%20Stats%20Support)
- [Updating the Mod](#updating-the-mod)
- [Adding Support for Someone Else's Mod](#adding-support-for-someone-elses-mod)
- [Adding Class Compatibility](#adding-class-compatibility)
- [Can You Make Extensions on a Mac?](#can-you-make-extensions-on-a-mac)
- [Conclusion](#conclusion)

## Introduction

So, on a technical level, why does Transmogrification Lite need extensions? Well, there's a lot of information that we need about each piece of equipment in order to transmogrify it, and I don't know of a way to get this information at runtime using only the official modding tools. Instead, my solution with Transmogrification Lite is to create duplicate equipment with the same appearance but none of the stats, and then create a status that  mimics its stats and can be applied to any character no matter what they're wearing. These two components (and a few other things) are then plugged into an Osiris script I wrote that lets the player mix-and-match any appearance with any status boost.

This system works, but it means that every single item needs to be broken down into its components and recorded in a database for Transmogrification Lite to be able to work with it. I've already done this for equipment in the base game, but equipment added by other mods still can't be transmogrified. There are two solutions to this:

1. The equipment mod author adds built-in compatibility. This would be ideal because there are no dependencies or extra mods required, but it's completely up to them whether they want to. We shouldn't assume that anyone will, and we also shouldn't pester them to change their mind if they decide not to.

2. Someone gets permission to create a dependency for the equipment mod in order to extend / add support for it. ([More on this later.](#adding-support-for-someone-elses-mod))

For the rest of these guides, I will assume that you have some basic BG3 modding knowledge. However, I've done my best to be thorough about where to go and how to do most things.

## How to Use These Resources

This directory contains three snapshots of a simple equipment mod in the process of adding built-in compatibility with Transmogrification Lite. The first snapshot only adds support for using the appearance of the new equipment (which is pretty easy to do), and the last snapshot ends with adding custom stats support for the equipment's unique behaviors (which can get complicated).

Each snapshot contains the project files, a .pak file, and a detailed guide that explains how to add this level of support. Each snapshot / guide builds on the previous one, so it will be confusing if you skip straight to the full stats support guide.

**I recommend reading the three snapshot guides in order and then coming back here to read the remaining topics below.** If you'd prefer to read these guides all in one place, there's an [all-in-one version on mod.io](https://mod.io/g/baldursgate3/r/how-to-extend-transmogrification-lite).

## Updating the Mod

It's likely that you will need to update your mod at some point to add support for new equipment or to change / fix ones you've already added support for. When you release an update, most of the changes should work just fine for players when they download it. However, the INIT section of the Osiris script only runs when the mod is first added to a game, and does not run again when the mod is updated. This means that any changes you make to the INIT section (like adding new equipment to the primary database, changing spell cooldowns, etc.) won't be applied to players' already-modded games unless we add some extra logic to the Osiris script.

It's possible to do this because any changes we make to the KB section of the Osiris script _will_ be immediately applied, even to already-modded games. This lets us check if the INIT section is out-of-date and, if so, execute a rule to add and remove the facts missing from the update.

Note: If you want to keep your original script cleaner, you can add these rules to a different Osiris script that's just for handling updates. It will work exactly the same.

To start, add `DB_IDENTIFIER_Ver(_Version);` to the INIT section, where `IDENTIFIER` is replaced with your mod's identifier and `_Version` is replaced by the current version number (`1` probably makes the most sense to start). Note that version numbers in this context can only be integers (e.g. `1`, `2`, `3`, ...) and CANNOT be any other format like `1.0.2`.

Next, add these rules to the KB section:

```
// Check if there's an update as soon as the game starts
IF
LevelGameplayStarted(_,_)
THEN
PROC_IDENTIFIER_CheckForUpdate();

// Compare the version number stored in a database by the INIT section (which won't be automatically updated)
// with the hard-coded version number in this rule (which will be automatically updated when you change it)
PROC
PROC_IDENTIFIER_CheckForUpdate()
AND
DB_IDENTIFIER_Ver(_Ver)
AND
_Ver < [version number] // update with current version number (e.g. '_Ver < 1')
THEN
PROC_IDENTIFIER_UpdateModVersion(_Ver);

// When the version numbers don't match and so we're going to perform an update, increment the version number
// stored in the database for this particular game so that it won't be repeated the next time it's loaded.
PROC
PROC_IDENTIFIER_UpdateModVersion(_Ver)
AND
IntegerSum(_Ver,1,_NewVer)
THEN
NOT DB_IDENTIFIER_Ver(_Ver);
DB_IDENTIFIER_Ver(_NewVer);

//REGION Version updates

// [UPDATES GO HERE]

//END_REGION

// Repeat the check for an update in case the player skipped one or more upgrades
PROC
PROC_WW_TL_UpdateModVersion(_)
THEN
PROC_WW_TL_CheckForUpdate();
```

Make sure to at least replace every use of `IDENTIFIER` with your mod's unique identifier, as well as to replace `[version number]` in `PROC_IDENTIFIER_CheckForUpdate()` with the same version number you put in the database in the INIT section.

After publishing your mod, you need to do the following things whenever you make changes to a script's INIT section:

1. Keep track of the changes you're making.

2. Increment the version number in the INIT section (which only newly-modded games will receive).

3. Update the version number in the KB section to the same value (which newly-modded AND updated games will receive).

4. Add a new rule to the "Version updates" region that applies the changes you made to the INIT section.

For example, let's say I want to update my mod with a new piece of equipment. I would add another fact to `DB_WW_TL_ArmorComponents` in the INIT section, increment the current version number in the INIT section _and_ KB section to `2`, and then write this new rule:

```
PROC_IDENTIFIER_UpdateModVersion(1) // the PROC's argument 1 indicates that we're updating from version 1 to version 2
THEN
DB_WW_TL_ArmorComponents(ExampleItem_c97df1d0-3011-47f4-b859-3ea9e3664997, ExampleItem_AppearanceOnly_fa942a7b-ea01-4562-be3c-19854ae8a255, "WW_CE_TL_ExampleItem", 1, 12, "Breast", 0, 0);
```

Let's say that this example item grants the wearer a spell, and that I forgot until after I released the update to add this to its tooltip and to enforce its cooldown. To fix this, I'd follow the steps again and end up with this additional rule:

```
PROC_IDENTIFIER_UpdateModVersion(2) // the argument is now 2 to indicate that this rule should run when we're updating from v2 to v3
THEN
DB_WW_TL_TooltipStatuses("WW_CE_TL_ExampleItem", "SPELL");
DB_WW_TL_ArmorSpells("WW_CE_TL_ExampleItem", "Shout_ExampleSpell", "LONG");
```

Later, if I decide that a Long Rest cooldown is too much for this spell and I want to change it to a Short Rest, Transmogrification Lite won't let the player cast it again before a Long Rest unless I update its value in `DB_WW_TL_ArmorSpells`. Because we're now CHANGING an existing value instead of just adding a new one, it's extremely important to remove the old fact with `NOT` as well as adding the new fact, like this:

```
PROC_IDENTIFIER_UpdateModVersion(3) // updating from v3 to v4
THEN
NOT DB_WW_TL_ArmorSpells("WW_CE_TL_ExampleItem", "Shout_ExampleSpell", "LONG"); // get rid of Long Rest cooldown
DB_WW_TL_ArmorSpells("WW_CE_TL_ExampleItem", "Shout_ExampleSpell", "SHORT"); // add Short Rest cooldown instead
```

Other than adding or removing entire facts from `DB_WW_TL_ArmorComponents`, I recommend trying to avoid _changing values_ in facts for that database because it will cause problems with how transmogrifications and their tooltips are updated. I think it would be fine if players destroy any existing transmogrifications of that item and then re-make them, but I'd be prepared to get bug reports about it even if you try to make sure everyone knows that this is necessary.

For a complete example of updating the INIT section, I recommend referencing the actual Transmogrification Lite script ['GLO_Transmogrification_WW'](https://github.com/WorldWalker42/Transmogrification-Lite/blob/main/Project%20Files/Mods%20folder/Story/RawFiles/Goals/GLO_Transmogrification_WW.txt). The relevant code is at the top of the KB section, or you can search for `PROC_WW_TL_CheckForUpdate()` to jump straight to it. To better organize the bigger updates, I defined the PROC `PROC_WW_TL_UpdateInitFacts(_Ver)` in a different script, ['GLO_TransmogrificationUpdates_WW'](https://github.com/WorldWalker42/Transmogrification-Lite/blob/main/Project%20Files/Mods%20folder/Story/RawFiles/Goals/GLO_TransmogrificationUpdates_WW.txt).

## Adding Support for Someone Else's Mod

So far, we've been focused on adding built-in transmogrification compatibility with your own equipment mod. Now let's talk about creating a dependency that extends support to someone else's mod.

The process is fundamentally the same (you still need to create duplicate Root Templates, BOOST statuses, add facts to databases, etc.), but there are a few extra steps to turn a mod into a dependency. Also, the workflow is a little different because we probably won't have access to the equipment mod's editor files.

### Getting Permission

First and foremost, I think it's incredibly important to make sure you have the original mod author's permission to create a dependency, as well as to be respectful if they say no. I recommend checking their mod description and comment section to see if they've already given an answer about making dependencies before contacting them so that they don't get flooded with duplicate requests.

Also, even though we have the option on mod.io to not allow dependencies, be aware that the option defaults to being turned on, so it shouldn't be taken as implied permission. Or, the mod author might only be comfortable with dependencies that translate the mod to other languages, and not for anything else. I have personally encountered this situation, where a very popular equipment mod had the setting enabled to allow dependencies but the author has declined most requests to make them (including to add compatibility with Transmogrification Lite), so please always ask.

### Setting Up the Project

Before we get started, make sure the .pak files for all mod dependencies are in the game's mod folder (which is _not_ the same as the toolkit's mod folder that we've used for most of this guide). If you downloaded the mods through the in-game mod manager then you don't need to worry about this step because it will put them there automatically.

Next, create a new project in the toolkit. I recommend using a name like `[abbreviation for your username]_TransmogLite_[abbreviation for the mod you're adding support for]`. Then open Project -> Project Settings, click on the Dependencies tab, and find the mod dependencies in the list on the left. Select one and click the right-facing arrow in between the two columns to set it as a dependency. The first time you do this, it's normal for lots of other items to move to the column on the right, like the dice sets, ModBrowser, SharedDev, etc. Make sure that Transmogrification Lite is one of the dependencies you set. Press Save in the bottom right, and then accept the toolkit's request to reload the level.

Restart the toolkit after adding dependencies to be able to see their Root Templates and Osiris scripts. Statuses, spells, and other files in the Stats Editor won't appear because their editor files aren't included in the mod's .pak file. You'd have to ask the mod author to give them to you directly or to upload all the project files to something like a GitHub repository.

### Adding Support for Each Item

From here, the things you need to make for a standalone extension are almost exactly the same as what you need to add to an equipment mod for built-in compatibility. However, you can skip some steps now that Transmogrification Lite is a formal dependency, which means you don't have to recreate its blank armor stats or parent BOOST status, etc.

The biggest difference in the process is that you won't be able to use the Stats Editor to directly access the equipment's stats when you're making the BOOST statuses. Instead, you will probably need to use a tool like [LSLib](https://github.com/Norbyte/lslib) to unpack the mod and get the text file(s) from its Public folder (specifically in `Stats\Generated\Data`). Now you can copy from the text file, or feed it into my automation script to speed up the process.

### Publishing

When the mod is ready to share and has been uploaded to mod.io, it's important to also set the dependencies on its mod page. From the mod's Admin page, choose the General Settings tab and then Dependencies. Type the name of each dependency into the search field and save them so that they will appear on the mod page.

## Adding Class Compatibility

Most of this guide is about adding transmogrification compatibility to new equipment, but modded classes that change a character's core AC calculation (such as using an ability modifier other than DEX or raising the 'floor' above 10), or that add features which depend on (not) wearing armor, will also need custom support in order for Transmogrification Lite to work with it correctly.

For example, if a new caster class adds the character's INT modifier to their AC when not wearing armor, this can be done similar to [any other unarmored-only bonus](https://github.com/WorldWalker42/Transmogrification-Lite/tree/main/Extension%20Resources/3.%20Full%20Stats%20Support#enforcing-unarmored-only-bonuses). Or, if a new class replaces DEX with a different ability score for their primary AC bonus, Transmogrification Lite's normal AC calculations should be disabled for that character by applying the [`WW_TL_ALT_AC_MOD`](https://github.com/WorldWalker42/Transmogrification-Lite/tree/main/Extension%20Resources/3.%20Full%20Stats%20Support#tags) tag to them, and then they will need to be given new passives that perform the correct calculations.

For actual examples of custom class support, I recommend looking at Transmogrification Lite's compatibility script, [`GLO_TransmogrificationCompatibility_WW`](https://github.com/WorldWalker42/Transmogrification-Lite/blob/main/Project%20Files/Mods%20folder/Story/RawFiles/Goals/GLO_TransmogrificationCompatibility_WW.txt).

This script adds several procedures that can make it easier to apply tags when needed. Depending on which tag(s) you want, you can just add a new rule in your own script that satisfies any or all the following queries:

1. `QRY_WW_TL_Compatibility_UsesAltACModifier((GUIDSTRING)_Character)` will qualify `_Character` for the tag `WW_TL_ALT_AC_MOD`

2. `QRY_WW_TL_Compatibility_OverridesAC((GUIDSTRING)_Character)` will qualify `_Character` for the tag `WW_TL_CUSTOM_AC_OVERRIDE`

3. `QRY_WW_TL_Compatibility_IgnoresOtherArmor((GUIDSTRING)_Character)` will qualify `_Character` for the tag `WW_TL_IGNORE_WEARING_ARMOR`

4. `QRY_WW_TL_Compatibility_NeedsStandardArmorTracker((GUIDSTRING)_Character)` will qualify `_Character` to receive the status `WW_TL_COMPATIBILITY_WEARING_NORMAL_ARMOR` when wearing original, non-transmogrified armor

For example, if you want a character to receive the `WW_TL_ALT_AC_MOD` tag when they have a level in a particular class, you can just add another rule for `QRY_WW_TL_Compatibility_UsesAltACModifier` in your own script that will evaluate to true if they have the tag for this class:

```
QRY
QRY_WW_TL_Compatibility_UsesAltACModifier((GUIDSTRING)_Character)
AND
IsTagged(_Character, (TAG)MY_CLASS_TAG_00000000-1111-2222-3333-444444444444, 1)
THEN
DB_NOOP(1);
```

If needed, you can check for a passive or status or anything else instead of a tag, and you can add as many conditions as you want. Or, if it's easier to just ignore these queries and add or remove the tags yourself, feel free to do so.

## Can You Make Extensions on a Mac?

Maybe? I haven't tried it, but (I think) it's theoretically possible.

Some people have tried to get the toolkit set up on a virtual Windows machine that's running on a Mac, and it sounds like this is very difficult but not entirely without success. You should be able to find discussions / threads where people share what they've tried and whether it worked on various modding Discord channels - I know it has come up at least on the official Larian Studios Discord.

However, my guess is that you'll get better results from using modding techniques that existed before the toolkit / official mod support existed because the files you'll spend the most time working with to extend Transmogrification Lite can be opened in pretty much any text editor.

Of course, there are still a number of steps that, to the best of my knowledge, can't currently be done on macOS. For example:

1. Unpacking the equipment mod so that you can get its Root Template `.lsf` files, as well as the stats and passives files

2. Converting the `.lsf` files to `.lsx` so that a text editor can open them

3. Converting the `.lsx` files you make into `.lsf` files that the game can use

4. Packing your mod

These and other things can be done with third-party tools like [LSLib](https://github.com/Norbyte/lslib/tree/master) and the [Baldur's Gate 3 Modder's Multitool](https://github.com/ShinyHobo/BG3-Modders-Multitool). Compared to the toolkit, these are extremely lightweight programs that should be far, far easier to get set up on a virtual machine. Also, there are good [resources for third-party modding techniques](https://wiki.bg3.community) to help you navigate the process, such as [creating a `meta.lsx` file](https://wiki.bg3.community/Tutorials/General/creating_meta). This is the approach I personally would take to try to make simple mods like Transmogrification Lite extensions on a Mac.

Unfortunately, even if you get all of this to work, you still won't be able to publish to mod.io without the toolkit. The good news is that you can always upload it to Nexus Mods with the other third-party mods.

Good luck!

## Conclusion

If you're interested in extending Transmogrification Lite, I hope this guide helped. If you have any questions, you're welcome to ask and I'll try to answer when I can.

If you release an extension or compatible mod, I encourage you to reply to a pinned comment on Transmogrification Lite's mod page to let us know about it.

Happy modding!