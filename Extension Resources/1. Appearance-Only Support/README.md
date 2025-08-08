Each of these folders are named for the location they need to be placed in the Baldur's Gate 3 Data folder (most likely `C:\Program Files (x86)\Steam\steamapps\common\Baldurs Gate 3\Data`). When you do so, replace the name of each of these folders with: `WW_CompatibilityExample_c4f7541a-36b5-1354-f8d9-e7fd62c517bf`

## How to Extend Appearance-Only Support

Let's start adding transmogrification compatibility to new equipment. The easiest thing to do is to have your own equipment mod and add built-in support for creating transmogrifications with just the appearance (and not the stats) of your items. We'll add stats support in the next section.

At a high level, there are only two things you need to do for each item:
1. Create a duplicate Root Template that removes its stats
2. Fill out some values in a new line of an Osiris script

There's a little bit of one-time setup for each step, but once you're familiar with the process, it's all very easy to do. Let's go into more detail.

###Root Templates

The first step is to create new Root Templates that are identical to each piece of equipment that you want to support, except that their armor stats are replaced with ones that don't grant any bonuses.

####One-Time Setup

Before we can start making the duplicate Root Templates, we need to prepare the empty stats that will be assigned to them. Because of the way armor stats work, we need to make one for each equipment slot. You can make your own, but I recommend copying the ones made in Transmogrification Lite so that, if they ever get updated, putting the equipment mod earlier in the load order will cause its version of the stats to be overwritten by the newer, correct version.

The easiest way to copy Transmogrification Lite's armor stats is to close the toolkit, paste some values into your mod's `Armor.stats` editor file, and then relaunch the toolkit. The file is probably located somewhere like this: `C:\Program Files (x86)\Steam\steamapps\common\Baldurs Gate 3\Data\Editor\Mods\[your mod name]\Stats\Stats\`

Open the file with any text editor and scroll down to the bottom. I recommend pasting the new values in the third-to-last line:

```
    </stat_object>
    !PASTE NEW VALUES HERE!
  </stat_objects>
</stats>
```

Here are the values to copy-paste:

```
    <stat_object is_substat="false">
      <fields>
        <field name="UUID" type="IdTableFieldDefinition" value="297dcf73-2dfc-4a16-85b2-b9279b8fb5f3" />
        <field name="Name" type="NameTableFieldDefinition" value="WW_TL_Base" />
        <field name="Using" type="BaseClassTableFieldDefinition" value="17fbd33d-6377-4ec4-b642-5c6e9b063366" />
        <field name="Weight" type="FloatTableFieldDefinition" value="0" />
        <field name="MinAmount" type="IntegerTableFieldDefinition" value="1" />
        <field name="MaxAmount" type="IntegerTableFieldDefinition" value="1" />
        <field name="Priority" type="IntegerTableFieldDefinition" value="1" />
        <field name="MinLevel" type="IntegerTableFieldDefinition" value="1" />
        <field name="Slot" type="EnumerationTableFieldDefinition" value="Breast" enumeration_type_name="Itemslot" version="1" />
        <field name="ValueUUID" type="GuidObjectTableFieldDefinition" value="8b2ad47c-891e-4a19-bab8-43cd5e964cb1" />
        <field name="Tags" type="StringTableFieldDefinition" value="WW_TL_TRANSMOGRIFIED" />
        <field name="RootTemplate" type="RootTemplateTableFieldDefinition" value="02ae5d88-8044-43df-8363-02a2900776db" />
        <field name="ArmorType" type="EnumerationTableFieldDefinition" value="Padded" enumeration_type_name="ArmorType" version="1" />
        <field name="Proficiency Group" type="EnumerationListTableFieldDefinition" value="None" enumeration_type_name="ProficiencyGroupFlags" version="1" />
      </fields>
    </stat_object>
    <stat_object is_substat="false">
      <fields>
        <field name="UUID" type="IdTableFieldDefinition" value="217b943a-e4bf-4ec8-81ae-48df9a495a26" />
        <field name="Name" type="NameTableFieldDefinition" value="WW_TL_Base_Helmet" />
        <field name="Using" type="BaseClassTableFieldDefinition" value="297dcf73-2dfc-4a16-85b2-b9279b8fb5f3" />
        <field name="Slot" type="EnumerationTableFieldDefinition" value="Helmet" enumeration_type_name="Itemslot" version="1" />
        <field name="RootTemplate" type="RootTemplateTableFieldDefinition" clear_inherited_value="true" value="" />
        <field name="ArmorClass" type="IntegerTableFieldDefinition" clear_inherited_value="true" value="" />
        <field name="ArmorType" type="EnumerationTableFieldDefinition" clear_inherited_value="true" value="" enumeration_type_name="ArmorType" version="1" />
      </fields>
    </stat_object>
    <stat_object is_substat="false">
      <fields>
        <field name="UUID" type="IdTableFieldDefinition" value="817a383b-23af-4595-81d7-8fdb46800a88" />
        <field name="Name" type="NameTableFieldDefinition" value="WW_TL_Base_Boots" />
        <field name="Using" type="BaseClassTableFieldDefinition" value="297dcf73-2dfc-4a16-85b2-b9279b8fb5f3" />
        <field name="RootTemplate" type="RootTemplateTableFieldDefinition" clear_inherited_value="true" value="" />
        <field name="Slot" type="EnumerationTableFieldDefinition" value="Boots" enumeration_type_name="Itemslot" version="1" />
        <field name="ArmorClass" type="IntegerTableFieldDefinition" clear_inherited_value="true" value="" />
        <field name="ArmorType" type="EnumerationTableFieldDefinition" clear_inherited_value="true" value="" enumeration_type_name="ArmorType" version="1" />
      </fields>
    </stat_object>
    <stat_object is_substat="false">
      <fields>
        <field name="UUID" type="IdTableFieldDefinition" value="ad252c9e-0353-40e4-9421-41340d3f502d" />
        <field name="Name" type="NameTableFieldDefinition" value="WW_TL_Base_Gloves" />
        <field name="Using" type="BaseClassTableFieldDefinition" value="297dcf73-2dfc-4a16-85b2-b9279b8fb5f3" />
        <field name="RootTemplate" type="RootTemplateTableFieldDefinition" clear_inherited_value="true" value="" />
        <field name="Slot" type="EnumerationTableFieldDefinition" value="Gloves" enumeration_type_name="Itemslot" version="1" />
        <field name="ArmorClass" type="IntegerTableFieldDefinition" clear_inherited_value="true" value="" />
        <field name="ArmorType" type="EnumerationTableFieldDefinition" clear_inherited_value="true" value="" enumeration_type_name="ArmorType" version="1" />
      </fields>
    </stat_object>
    <stat_object is_substat="false">
      <fields>
        <field name="UUID" type="IdTableFieldDefinition" value="bb8d47dd-7914-4901-bc0f-01aa32604434" />
        <field name="Name" type="NameTableFieldDefinition" value="WW_TL_Base_Cloak" />
        <field name="Using" type="BaseClassTableFieldDefinition" value="297dcf73-2dfc-4a16-85b2-b9279b8fb5f3" />
        <field name="RootTemplate" type="RootTemplateTableFieldDefinition" clear_inherited_value="true" value="" />
        <field name="Slot" type="EnumerationTableFieldDefinition" value="Cloak" enumeration_type_name="Itemslot" version="1" />
        <field name="ArmorClass" type="IntegerTableFieldDefinition" clear_inherited_value="true" value="" />
        <field name="ArmorType" type="EnumerationTableFieldDefinition" clear_inherited_value="true" value="" enumeration_type_name="ArmorType" version="1" />
      </fields>
    </stat_object>
```

Make sure to save these changes to the editor file. Now, when you reopen the toolkit, you will be able to see and use the armor stats like normal. Each of the stats corresponds with an equipment slot:

Chest: "WW_TL_Base"
Helmet: "WW_TL_Base_Helmet"
Cloak: "WW_TL_Base_Cloak"
Gloves:"WW_TL_Base_Gloves"
Footwear: "WW_TL_Base_Boots"

####For Each Item

We're now ready to create new Root Templates for each item we want to support:

1. In the main toolkit window's Root Templates pane, right click on one of the items and choose "Create inherited from selected..."

2. In the popup window, add something to the end of the new template's name to indicate that it's the appearance-only version of the item.

3. Still in the popup, scroll down to the Item category and open the Stats field. Type `WW_TL_Base` into the filter and then choose the stats that correspond to this item's equipment slot.

4. Click "Create" to finalize this new template.

5. I recommend saving the project after creating each one, because it's _really_ not fun when the toolkit crashes and you lose a bunch of them at once.

If there are more pieces of equipment than you want to duplicate by hand, then make sure to read the **[Automating This Process](#automating-this-process)** section below.

###Database Entries

Now that we have templates for the equipment's appearance, we just need to connect them to the transmogrification system so that they can be used. This is done in an Osiris script, but don't worry if you haven't done anything with Osiris before - it's pretty easy to do.

####One-Time Setup

First, we need to create an Osiris script. Open the Story Editor with this button in the main toolkit window:

![Button to open Story Editor](/Extension Resources/Assets/StoryEditorButton.JPG)

Next, create a new top-level script by right-clicking on one of the items in the list and choosing "Add New Item".

![Menu item to create new Osiris script](/Extension Resources/Assets/AddNewScript.JPG)

I recommend naming the script something like `GLO_Transmogrification_IDENTIFIER` where you replace `IDENTIFIER` with an abbreviation of your username and/or the mod's name (for example, the identifier I use for Transmogrification Lite is `WW_TL`, and the one I use for this Compatibility Example is `WW_CE`).

When you create the script, it should automatically open three text boxes on the right side of the window. If this doesn't happen automatically, you can find the name of your script in the list on the left (it probably went to the bottom) and double-click it.

####For Each Item

In the topmost text box (called the INIT section), you will need to add the following line once for each piece of equipment and then fill in its values:

```
DB_WW_TL_ArmorComponents(_Template, _AppearanceTemplate, _StatsStatusName, _ArmorType, _DisplayAC, _Slot, _Unique, _AdditionalAttributesTooltip);
```

A lot of these values have to do with recreating equipment stats, which we don't care about right now. Instead, we can use the values for default stats (e.g. clothes with 10 AC for the chest slot and nothing for every other slot). To keep things simple, you can start with one of the following lines that are already mostly filled in:

For equipment in the chest slot: `DB_WW_TL_ArmorComponents(_Template, _AppearanceTemplate, "WW_TL_AC_10", 0, 10, "Breast", 0, 0);`

For equipment in any other slot: `DB_WW_TL_ArmorComponents(_Template, _AppearanceTemplate, "NULL", 0, 0, _Slot, 0, 0);`

Replace `_Template` with the Name_GUID for the original item's Root Template (which you can get by right-clicking on it in the main window's Root Templates pane and select "Copy Name_GUID to clipboard").

Replace `_AppearanceTemplate` with the Name_GUID for the item's appearance-only Root Template that we created in the previous step.

If `_Slot` hasn't been filled in yet, replace it with `"Helmet"`, `"Gloves"`, `"Boots"`, or `"Cloak"` as appropriate for this item.

For example, here's what I did for a basic robe in the base game for Transmogrification Lite:
```
DB_WW_TL_ArmorComponents(ARM_Robe_B_69302808-57a0-4fbb-9938-137bce5421d1, ARM_Robe_B_WW_TL_01f1643b-363b-42e0-84c4-44fe7851b2c7, "WW_TL_AC_10", 0, 10, "Breast", 0, 0);
```

####Finalizing the Script

Once you've added everything to your script, you MUST finalize it by 'building' the script so that it takes effect in the game. Do this by opening the "File" menu and choosing "Generate Definitions, Build and Reload".

The first time you do this after opening the toolkit, you will get a popup warning about orphan queries - this just means that you're adding facts to a database that isn't used anywhere, and it's letting you know about it in case this was a mistake. Because the database will be used by another mod - Transmogrification Lite - we want to ignore this warning.

To do this, close both popups and click on the "Ignore Orphan Queries" button toward the bottom of the window.

![The buttons to click on to resolve orphan queries warning](/Extension Resources/Assets/OrphanQueriesWarning.JPG)

A new window will open to let you choose which orphan queries you want to ignore. There should only be one for `DB_WW_TL_ArmorComponents`, so toggle on the checkbox next to it and press "OK" to finalize your choice.

![The correct state for the orphan queries resolution window](/Extension Resources/Assets/OrphanQueriesSelector.JPG)

Now that we've told the Story Editor to ignore this possible problem, choose "Generate Definitions, Build and Reload" again. Until the next time you close the toolkit, the process should complete without any warnings and your script is ready to work.

If you ever get tired of doing this, you can add a rule in the KB section that references the database but will never execute, like this:

```
IF
LevelGameplayStarted(_, _)
AND
1 == 2 // always evaluates to false, which guarantees this rule will never execute
AND
DB_WW_TL_ArmorComponents(_,_,_,1000,_,_,_,_) // references the database
//AND
//[add more databases as needed]
THEN
DB_NOOP(1);
```

I recommend taking one last (optional) step to reduce the file size of your mod. For some reason, building any Osiris script will also put a copy of the entire game's scripts into your mod's project files, and unless you manually delete it before publishing the mod, it will add about 17 MB. (However, you also need to be aware that your script won't do anything _inside the toolkit_ after you delete the copy of the base game scripts. Without the copy, it will only work as a published .pak file being used with the actual game. So, only delete the files after testing in the toolkit and before you're ready to publish.)

To reduce your mod's size, navigate to your toolkit project files (most likely `C:\Program Files (x86)\Steam\steamapps\common\Baldurs Gate 3\Data` and then find this mod's Story files in `Mods\[mod_guid]\Story`. There will be a folder "RawFiles" and a bunch of other files. You MUST keep "RawFiles" but it should be safe to delete everything else.

###Complete Example

That's everything you need to do so that people can use the appearance of your equipment with the stats of any other supported item! It's perfectly fine to leave it this way if you don't want to add stats support - which gets more complicated - but I do recommend making it very clear in your mod description that the transmogrification support is appearance-only.

I've made a simple mod that just adds a few pieces of equipment with built-in appearance transmogrification support if you want to look at a complete example. The .pak and all project files for this example are available above.

An important thing to note: If you release an update to this mod that changes equipment that already has support (or if you add support for more equipment in the update), some of these changes might not apply to transmogrifications unless the player starts a new game OR you update the INIT section in a special way. For more information about this, see the **Updating Transmogrification Databases** section in another part of this guide.

###Automating This Process

To make creating extensions easier, I wrote a Python script that can do everything we've covered so far automatically. It's available in this GitHub repository: https://github.com/WorldWalker42/Transmogrification-Lite/blob/main/Extension%20Resources/script.py

DISCLAIMER: I've found the script to be very helpful, but I DO NOT make any promises that it is perfect. Also, it was not written with any particular elegance or efficiency in mind - it's just something I threw together to help me, and I'm sharing it as-is. I do not plan to provide detailed support or troubleshooting for it.

That being said, if you have Python installed, all you should have to do is run the script and give it the mod's identifier and a few relative file paths. If the equipment has stats that the script doesn't recognize (and therefore doesn't know what equipment slot it goes into), then you might have to open the script in a text editor and add those stats to a list it uses.

Here's the process to use the script in more detail:

1. Use something like the [LSLib package](https://github.com/Norbyte/lslib/tree/master) to convert all of the equipment mod's Root Template `.lsf` files (which will be in the mod's Public -> RootTemplates directory) into `.lsx` files. Put these `.lsx` files into a different folder (which can be anywhere, like your desktop) and make sure the original `.lsf` files are still in the mod folder.

2. Create another folder where the script's output can go.

3. Open the terminal or command line application and change the directory to the location where you put the Python script. Run it with: `python3 script.py IDENTIFIER relative/path/to/lsx/files relative/path/to/armor/stats relative/path/to/output/directory` where you replace `IDENTIFIER` with your mod's unique identifier and the placeholder filepaths with the actual relative filepaths to the described location or file.

4. In the output directory, check the "remainder.txt" file to see if any Root Templates were rejected by the script. Depending on the mod, it might be totally normal for there to be LOTS of rejected templates for things like weapons, containers, dyes, summons, etc. If any equipment that should have been supported was rejected, then refer to the script's output for the most up-to-date instructions on how to troubleshoot the problem.

5. Copy the contents of "script_init.txt" in the script output directory and paste it into your mod's Osiris script INIT section that you should create but not fill in as described above. Make sure to build and reload.

6. Convert the `.lsx` files in the output directory's "templates" subdirectory back into `.lsf` files, and then move them into the project's Public -> RootTemplates directory along with the original `.lsf` files.

Keep in mind that every time you run the script, it generates new random GUIDs for each item. This means you need to be mindful of not keeping a Root Template from one time the script ran with the `DB_WW_TL_ArmorComponents` entry for the same item from another time the script ran, because they won't match.