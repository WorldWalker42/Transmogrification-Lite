# A script for modding Baldur's Gate 3 to extend compatibility with Transmogrification Lite to more equipment. It generates .lsx files for new Root Templates, as well as a basic INIT section for an Osiris goal.
# DISCLAIMER: This script is definitely NOT perfect, nor is it written with any particular elegance or efficiency. However, it can speed up a tedious process and requires relatively little supervision, and so
# I am making it available as-is in the hopes that someone else will find it helpful too.
# Last modified: 8/6/25

import sys
import os
import random
import re

# Stats that do not inherit from anything else and should be specifically added for each mod and then removed afterwards
ONETIME_BODY_NEW_STATS = []
ONETIME_BODY_CAMP_NEW_STATS = []
ONETIME_HELMET_NEW_STATS = []
ONETIME_CLOAK_NEW_STATS = []
ONETIME_GLOVE_NEW_STATS = []
ONETIME_FOOTWEAR_NEW_STATS = []
ONETIME_FOOTWEAR_CAMP_NEW_STATS = []

# Stats that are uncommon and should be specifically added for each mod and then removed afterwards
ONETIME_BODY_PARENT_STATS = []
ONETIME_BODY_CAMP_PARENT_STATS = []
ONETIME_HELMET_PARENT_STATS = []
ONETIME_CLOAK_PARENT_STATS = []
ONETIME_GLOVE_PARENT_STATS = []
ONETIME_FOOTWEAR_PARENT_STATS = []
ONETIME_FOOTWEAR_CAMP_PARENT_STATS = []

# Very common / shared stats that are inherited by many items that should not be removed
BODY_PARENT_STATS = ['_Body', 'ARM_Robe_Body','ARM_Padded_Body','ARM_ChainMail_Body','ARM_ChainShirt_Body','ARM_HalfPlate_Body','ARM_Plate_Body','ARM_StuddedLeather_Body','_Armor_Magic_Robe','ARM_Cloth_Body_1','ARM_Cloth_Body_2','ARM_Leather_Body']
BODY_CAMP_PARENT_STATS = ['ARM_Camp_Body']
HELMET_PARENT_STATS = ['_Head','_Head_Magic','_Head_Magic_Circlet','_Head_Magic_Leather','_Head_Magic_Metal','ARM_Circlet','ARM_Hat','ARM_Helmet_Metal','ARM_Hat_Wizard_A']
CLOAK_PARENT_STATS = ['_Back','_Back_Magic','ARM_Cloak','ARM_Cloak_Long_B']
GLOVE_PARENT_STATS = ['_Hand','_Hand_Magic','_Hand_Magic_Metal','ARM_Gloves_Leather','ARM_Gloves_Metal']
FOOTWEAR_PARENT_STATS = ['_Foot','_Foot_Magic','_Foot_Magic_Metal','ARM_Shoes','ARM_Magic_Shoes','ARM_Boots_Leather','ARM_Boots_Metal']
FOOTWEAR_CAMP_PARENT_STATS = ['ARM_Camp_Shoes']

TRANSMOG_STAT_VALUES = [
			('WW_TL_Base', 'Breast', 'WW_TL_AC_10', 0, 10, BODY_PARENT_STATS + ONETIME_BODY_PARENT_STATS, ONETIME_BODY_NEW_STATS), # body stats
			('WW_TL_Base', 'Breast', 'WW_TL_AC_10', -1, 10, BODY_CAMP_PARENT_STATS + ONETIME_BODY_CAMP_PARENT_STATS, ONETIME_BODY_CAMP_NEW_STATS), # camp body stats
			('WW_TL_Base_Helmet', 'Helmet', 'NULL', 0, 0, HELMET_PARENT_STATS + ONETIME_HELMET_PARENT_STATS, ONETIME_HELMET_NEW_STATS), # helmet stats
			('WW_TL_Base_Cloak', 'Cloak', 'NULL', 0, 0, CLOAK_PARENT_STATS + ONETIME_CLOAK_PARENT_STATS, ONETIME_CLOAK_NEW_STATS), # cloak stats
			('WW_TL_Base_Gloves', 'Gloves', 'NULL', 0, 0, GLOVE_PARENT_STATS + ONETIME_GLOVE_PARENT_STATS, ONETIME_GLOVE_NEW_STATS), # glove stats
			('WW_TL_Base_Boots', 'Boots', 'NULL', 0, 0, FOOTWEAR_PARENT_STATS + ONETIME_FOOTWEAR_PARENT_STATS, ONETIME_FOOTWEAR_NEW_STATS), # footwear stats
			('WW_TL_Base_Boots', 'Boots', 'NULL', -1, 0, FOOTWEAR_CAMP_PARENT_STATS + ONETIME_FOOTWEAR_CAMP_PARENT_STATS, ONETIME_FOOTWEAR_CAMP_NEW_STATS) # camp footwear stats
		]

source_uuid = None
source_name = None
stats = None

generated_transmog_stats = []
queued_tooltip_statuses = []

passive_file = None

# 8-4-4-4-12
def generateUUID():
	alphabet = '0123456789abcdef'
	uuid = ''
	for i in range(8):
		uuid += random.choice(alphabet)
	uuid += '-'
	for i in range(4):
		uuid += random.choice(alphabet)
	uuid += '-'
	for i in range(4):
		uuid += random.choice(alphabet)
	uuid += '-'
	for i in range(4):
		uuid += random.choice(alphabet)
	uuid += '-'
	for i in range(12):
		uuid += random.choice(alphabet)
	return uuid

def appendTooltipStatusToQueue(stat_name, tooltip_status):
	global queued_tooltip_statuses

	# Don't append this status to the queue if it's already been queued (which can happen if there are multiple effects in a single category)
	for queued_status in queued_tooltip_statuses:
		if queued_status[0] == stat_name and queued_status[1] == tooltip_status:
			return
		
	queued_tooltip_statuses.append((stat_name, tooltip_status))

def queueBonuses(boosts, stat_name):
	# Boost spell save DC
	if 'SpellSaveDC(' in boosts:
		appendTooltipStatusToQueue(stat_name,'SAVE_DC')
	# Boost all attack rolls
	if 'RollBonus(Attack,' in boosts or 'RollBonus(RangedWeaponAttack,' in boosts or 'RollBonus(RangedOffHandWeaponAttack, 1)' in boosts or 'Advantage(AttackRoll' in boosts:
		appendTooltipStatusToQueue(stat_name,'ATTACK')
	# Boost spell attack rolls
	if 'RollBonus(MeleeSpellAttack,' in boosts or 'RollBonus(RangedSpellAttack,' in boosts:
		appendTooltipStatusToQueue(stat_name,'ATTACK_SPELL')
	# damage bonuses
	if 'CharacterWeaponDamage(' in boosts or 'CharacterUnarmedDamage(' in boosts or 'DamageBonus(' in boosts or 'DealDamage(' in boosts or 'EntityThrowDamage(' in boosts:
		appendTooltipStatusToQueue(stat_name,'DAMAGE')
	# Boost ability scores
	if 'Ability(' in boosts or 'AbilityOverrideMinimum(' in boosts:
		appendTooltipStatusToQueue(stat_name,'ABILITY')
	# Boost saving throws
	if 'RollBonus(SavingThrow,' in boosts or 'Advantage(SavingThrow,' in boosts or 'Advantage(Concentration' in boosts or 'Advantage(AllSavingThrows' in boosts or 'ProficiencyBonus(SavingThrow,' in boosts:
		appendTooltipStatusToQueue(stat_name,'SAVE_THROW')
	# Boost damage resistance
	if re.search('(?<!Ignore)Resistance\(', boosts) is not None: # regex to match 'Resistance(' and discard 'IgnoreResistance('
		appendTooltipStatusToQueue(stat_name,'RESISTANCE')
	# Boost flat damage reduction
	if 'DamageReduction(' in boosts:
		appendTooltipStatusToQueue(stat_name,'REDUCE_DAMAGE')
	# Boost unlocking spells
	if 'UnlockSpell(' in boosts:
		appendTooltipStatusToQueue(stat_name,'SPELL')

def getPassiveBoosts(passive_file, stat_name, passive_name):
	with open(passive_file, 'r') as input:
		found_stat = False
		for line in input:
			if found_stat and line.startswith('new entry "'):
				break
			elif not found_stat and line == f'new entry "{passive_name}"\n':
				found_stat = True
			elif found_stat and line.startswith('data "Boosts"'):
				boosts = line[15:line.rindex('"')]
				if boosts != '':
					queueBonuses(boosts, stat_name)
			elif found_stat and line.startswith('data "StatsFunctors"'):
				functors = line[22:line.rindex('"')]
				if functors != '':
					queueBonuses(functors, stat_name)

def getTransmogStats(mod_identifier, armor_file, original_stats, boost_file):
	global passive_file, generated_transmog_stats
	stat_name = f'{mod_identifier}_{original_stats}'

	# if this status has already been generated, return it rather than re-generating it
	for generated_stats in generated_transmog_stats:
		new_stat, slot, generated_stat_name, item_type, default_ac = generated_stats
		if stat_name == generated_stat_name:
			return generated_stats

	return_val = None
	grants_other_bonuses = False
	with open(armor_file, 'r') as reference:
		boosts = None
		passives = None
		statuses = None
		found_stat = False
		for line in reference:
			if found_stat and line.startswith('new entry "'):
				break
			elif not found_stat and line == f'new entry "{original_stats}"\n':
				found_stat = True
				# check if this stat is a new top-level stat that won't have a "using" entry
				for transmog_stat_values in TRANSMOG_STAT_VALUES:
					new_stat, slot, default_boost, item_type, default_ac, using_candidates, new_stats_candidates = transmog_stat_values
					if original_stats in new_stats_candidates:
						return_val = (new_stat, slot, default_boost, item_type, default_ac)
			elif found_stat and line.startswith('using "'):
				using = line[7:line.rindex('"')]
				for transmog_stat_values in TRANSMOG_STAT_VALUES:
					new_stat, slot, default_boost, item_type, default_ac, using_candidates, new_stats_candidates = transmog_stat_values
					if using in using_candidates:
						return_val = (new_stat, slot, default_boost, item_type, default_ac)
			elif found_stat and return_val is not None and boost_file is not None and line.startswith('data "Boosts"'):
				boosts = line[15:line.rindex('"')]
				if boosts != '':
					grants_other_bonuses = True
					queueBonuses(boosts, stat_name)
			elif found_stat and return_val is not None and boost_file is not None and line.startswith('data "StatsFunctors"'):
				functors = line[22:line.rindex('"')]
				if functors != '':
					queueBonuses(functors, stat_name)
			elif found_stat and return_val is not None and boost_file is not None and line.startswith('data "PassivesOnEquip"'):
				passives = line[24:line.rindex('"')]
				if passives != '':
					grants_other_bonuses = True
					if passive_file is not None:
						passive_list = passives.split(';')
						for passive in passive_list:
							getPassiveBoosts(passive_file, stat_name, passive.strip())
			elif found_stat and return_val is not None and boost_file is not None and line.startswith('data "StatusOnEquip"'):
				statuses_full = line[22:line.rindex('"')]
				if statuses_full != '':
					statuses = statuses_full.split(';')
					if statuses is not None:
						grants_other_bonuses = True

	if return_val is not None and boost_file is not None and grants_other_bonuses:
		new_stat, slot, default_boost, item_type, default_ac = return_val

		boost_file.write(f'new entry "{stat_name}"\n')
		boost_file.write('type "StatusData"\n')
		boost_file.write('data "StatusType" "BOOST"\n')
		boost_file.write('using "WW_TL_ARMOR_STATS"\n')
		if (boosts is not None and boosts != '') or default_ac > 0:
			if default_ac > 0 and (boosts is None or 'AC(' not in boosts):
				boosts = f'AC({default_ac})' if boosts is None else f'AC({default_ac});{boosts}'
			boost_file.write(f'data "Boosts" "{boosts}"\n')
		if passives is not None and passives != '':
			boost_file.write(f'data "Passives" "{passives}"\n')
		if statuses is not None:
			apply_statuses = ''
			remove_statuses = ''
			for status in statuses:
				apply_statuses += f'ApplyStatus({status},100,-1);'
				remove_statuses += f'RemoveStatus({status});'
			boost_file.write(f'data "OnApplyFunctors" "{apply_statuses}"\n')
			boost_file.write(f'data "OnRemoveFunctors" "{remove_statuses}"\n')
		boost_file.write('\n')
		
		return_val = (new_stat, slot, f'{stat_name}', item_type, default_ac)
		generated_transmog_stats.append(return_val)
		return return_val
	else:
		return return_val
	
def resetEntry(remainder = None):
	global source_uuid, source_name, stats

	if remainder is not None and (source_name is not None or source_uuid is not None or stats is not None):
		remainder.write(f'Incomplete or rejected template:\n- Name: {source_name}\n- UUID: {source_uuid}\n- Stats: {stats}\n\n')

	source_uuid = None
	source_name = None
	stats = None

def addEntry(mod_identifier, armor_file, output_dir, database, boost_file, remainder):
	global source_uuid, source_name, stats

	transmog_stats = getTransmogStats(mod_identifier, armor_file, stats, boost_file)
	if transmog_stats is None:
		resetEntry(remainder)
	else:
		new_stats, slot, boost, item_type, default_ac,  = transmog_stats
		name = source_name + '_' + mod_identifier
		uuid = generateUUID()
		enforce_unique = 1 if boost_file is not None else 0

		with open(f'{output_dir}/templates/{uuid}.lsx', 'w') as destination:
			destination.write('<?xml version="1.0" encoding="utf-8"?>\n')
			destination.write('<save>\n')
			destination.write('\t<version major="1" minor="0" revision="0" build="1" lslib_meta="v1,bswap_guids,lsf_keys_adjacency" />\n')
			destination.write('\t<region id="Templates">\n')
			destination.write('\t\t<node id="Templates">\n')
			destination.write('\t\t\t<children>\n')

			destination.write('\t\t\t\t<node id="GameObjects">\n')
			destination.write(f'\t\t\t\t\t<attribute id="MapKey" type="FixedString" value="{uuid}" />\n')
			destination.write(f'\t\t\t\t\t<attribute id="Name" type="LSString" value="{name}" />\n')
			destination.write('\t\t\t\t\t<attribute id="LevelName" type="FixedString" value="" />\n')
			destination.write('\t\t\t\t\t<attribute id="Type" type="FixedString" value="item" />\n')
			destination.write(f'\t\t\t\t\t<attribute id="ParentTemplateId" type="FixedString" value="{source_uuid}" />\n')
			destination.write(f'\t\t\t\t\t<attribute id="Stats" type="FixedString" value="{new_stats}" />\n')
			destination.write('\t\t\t\t</node>\n')

			destination.write('\t\t\t</children>\n')
			destination.write('\t\t</node>\n')
			destination.write('\t</region>\n')
			destination.write('</save>\n')

		# DB_WW_TL_ArmorComponents(_Template, _AppearanceTemplate, _StatsBoost, _Type, _AC, _SlotName, _Unique);
		database.write(f'DB_WW_TL_ArmorComponents({source_name}_{source_uuid},{name}_{uuid},"{boost}",{item_type},{default_ac},"{slot}",{enforce_unique},0);\n')
		resetEntry()

def processTemplateFile(input_file, database, boost_file, remainder):
	global source_uuid, source_name, stats
	with open(input_file, 'r') as source:
		for line in source:
			if '<node id="GameObjects">' in line:
				resetEntry(remainder)
			
			if source_uuid is None and '<attribute id="MapKey" type="FixedString" value=' in line:
				start = line.index('value')
				candidate = line[start+7:line.rindex('"')]
				if candidate != '02 Colour':
					source_uuid = candidate
			elif source_name is None and '<attribute id="Name" type="LSString" value=' in line:
				start = line.index('value')
				source_name = line[start+7:line.rindex('"')]
			elif stats is None and '<attribute id="Stats" type="FixedString" value=' in line:
				start = line.index('value')
				stats = line[start+7:line.rindex('"')]

			if source_uuid is not None and source_name is not None and stats is not None:
				addEntry(mod_identifier, armor_file, output_dir, database, boost_file, remainder)

argc = len(sys.argv)
if argc < 5:
	print("Usage: python3 script.py <mod identifier> <input templates file or directory> <input armor file>  <output directory> [OPTIONAL: 1 to recreate stats] [OPTIONAL: passives file]")
else:
	mod_identifier = sys.argv[1]
	input_path = sys.argv[2]
	armor_file = sys.argv[3]
	output_dir = sys.argv[4]
	boost_file = open(f'{output_dir}/Status_BOOST.txt', 'w') if (argc >= 6 and sys.argv[5] == '1') else None
	if argc >= 7:
		passive_file = sys.argv[6]

	with open(f'{output_dir}/script_init.txt', 'w') as database, open(f'{output_dir}/remainder.txt', 'w') as remainder:
		try:
			os.mkdir(f'{output_dir}/templates')
		except FileExistsError:
			pass
		except Exception as e:
			print(f'Exception: {e}')

		if os.path.isdir(input_path):
			for root, dirs, files in os.walk(input_path):
				for file in files:
					absolute_path = os.path.join(root, file)
					processTemplateFile(absolute_path, database, boost_file, remainder)
				break
		else:
			processTemplateFile(input_path, database, boost_file, remainder)
		
		if queued_tooltip_statuses:
			database.write('\n')
			for tooltip_status in queued_tooltip_statuses:
				transmog_stats, status = tooltip_status
				database.write(f'DB_WW_TL_TooltipStatuses("{transmog_stats}","{status}");\n')

	print('**************************************************************************************************')
	print('IMPORTANT NOTE: The following components might be incomplete and should get your direct attention.')
	print('\nItems might have been rejected by this script (see "remainder.txt" in the output directory) if:')
	print('- They use stats that inherit from or use stats this script does not recognize. To fix, add the\n  unrecognized stat to the corresponding "ONETIME_[slot]_PARENT_STATS" list at the top of this\n  script.')
	print('- They use stats that don\'t inherit from anything. To fix, add the name of this stat to the\n  corresponding "ONETIME_[slot]_NEW_STATS" list at the top of this script.')
	print('- They use stats from the base game that are not included in the armour file provided to this\n  script. These items need to be added completely by hand.')

	if boost_file is not None:
		boost_file.close()
		
		print('\nFor each fact / row in DB_WW_TL_ArmorComponents in "script_init.txt":')
		print('- The equipment type (column #4) is correctly assigned -1 for camp clothes but defaults to 0\n  (clothing) for everything else.')
		print('- The AC display number (column #5) defaults to 10 for items in the chest slot and 0 for\n  everything else.')
		print('- The enforce unique stats boolean (column #7) defaults to 1 (true) for all items (i.e. only one\n  copy of the item\'s stats can be in use at a time).')
		print('- The additional tooltip attributes boolean (column #8) defaults to 0 (false) for all items.')
		print('\nDB_WW_TL_ArmorSpells was not created at all in "script_init.txt"')
		print('- Needs a row for each spell that is unlocked by transmogrified equipment and has a cooldown.')
		print('\nDB_WW_TL_TooltipStatuses might not be perfect for every item in "script_init.txt"')
		print('\nFor each new status that recreates an item\'s stats in "Status_BOOST.txt":')
		print('- "AC(10);" is added to the Boost column for items in the chest slot (unless it already has an AC\n  bonus) and might need to be changed to match the item\'s actual total AC.')
		print('- StatsFunctorContext and StatsFunctors columns were not copied because they\'re never used in\n  armour stats so far as I\'ve seen, so if for some reason they are, they need to be manually\n  copied over.')
		print('\nFinally, be aware that this script has generated a unique status for each and every item, regardless\nof whether two or more items share identical stats. If many items share stats, I recommend\nkeeping only one copy and assigning it to all of the items in the script\'s INIT section.\nDB_WW_TL_TooltipStatuses will also have duplicates for each status and should be cleaned as well.')
	
	print('\n**************************************************************************************************')
