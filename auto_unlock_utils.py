import cost_calculator
import crops
import movement
import coordinates

import hay
import trees
import carrots
import sunflowers
import pumpkins
import cactus
import weird_substance
import gold
import dinosaurs

farm_func_for_item = {
	Items.Hay: hay.farm,
	Items.Wood: trees.farm,
	Items.Carrot: carrots.farm,
	Items.Power: sunflowers.farm,
	Items.Pumpkin: pumpkins.farm,
	Items.Cactus: cactus.farm,
	Items.Weird_Substance: weird_substance.farm,
	Items.Gold: gold.farm,
	Items.Bone: dinosaurs.farm,
}

unlock_for_items = {
	Items.Hay: Unlocks.Grass,
	Items.Wood: Unlocks.Trees,
	Items.Carrot: Unlocks.Carrots,
	Items.Power: Unlocks.Sunflowers,
	Items.Pumpkin: Unlocks.Pumpkins,
	Items.Cactus: Unlocks.Cactus,
	Items.Weird_Substance: Unlocks.Fertilizer,
	Items.Gold: Unlocks.Mazes,
	Items.Bone: Unlocks.Dinosaurs
}


def get_area():
	size = get_world_size()
	return ((0, 0), (size, size))


def harvest_hay_early(amount):
	while num_items(Items.Hay) < amount:
		coords = coordinates.generate_coords(get_area(), "NORMAL")
		for pos in coords:
			if num_items(Items.Hay) >= amount:
				return
			movement.go_to(pos)
			if can_harvest():
				harvest()


def farm_wood_early(amount):
	while num_items(Items.Wood) < amount:
		coords = coordinates.generate_coords(get_area(), "NORMAL")
		for pos in coords:
			if num_items(Items.Wood) >= amount:
				return
			movement.go_to(pos)
			if get_entity_type() == Entities.Bush:
				if can_harvest():
					harvest()
			if get_ground_type() != Grounds.Grassland:
				till()
			plant(Entities.Bush)


def farm_carrots_early(amount):
	while num_items(Items.Carrot) < amount:
		coords = coordinates.generate_coords(get_area(), "NORMAL")
		for pos in coords:
			if num_items(Items.Carrot) >= amount:
				return
			movement.go_to(pos)
			if get_entity_type() == Entities.Carrot:
				if can_harvest():
					harvest()
			if get_ground_type() != Grounds.Soil:
				till()
			plant(Entities.Carrot)


def farm_item(item, amount):
	if num_unlocked(Unlocks.Plant) == 0:
		if item == Items.Hay:
			harvest_hay_early(amount)
		return

	if item == Items.Wood and num_unlocked(Entities.Tree) == 0:
		farm_wood_early(amount)
		return

	if item == Items.Carrot and num_unlocked(Unlocks.Grass) == 0:
		farm_carrots_early(amount)
		return

	if item == Items.Weird_Substance and num_unlocked(Unlocks.Fertilizer) == 0:
		return

	if item == Items.Gold and num_unlocked(Unlocks.Mazes) == 0:
		return

	if item in crops.entity_for_item:
		entity = crops.entity_for_item[item]
		if num_unlocked(entity) == 0:
			return

	if item in farm_func_for_item:
		farm_func = farm_func_for_item[item]
		farm_func(get_area(), amount)


def smart_unlock(unlock_item, tgt_amount=None):
	# unlocks all resource upgrades optimally for a given unlock
	quick_print("Unlock ", unlock_item, "lvl", num_unlocked(unlock_item))
	cost = get_cost(unlock_item)
	if cost == None:
		return True

	# recursive upgrade for all items farmed for an unlock
	items = cost_calculator.calculate_items_for_unlock_cost(unlock_item)
	for item, amount in items:
		# upgrades typically double production speed, so is always faster to upgrade then acquire material
		if tgt_amount == None:
			acceptable_upgrade_cost = amount/2
		else:
			acceptable_upgrade_cost = min(amount, tgt_amount)/2
		# upgrades for items needed to get target
		# upgrade until stable in case same item should be upgraded multiple times
		did_unlock=True
		while did_unlock:
			did_unlock = False
			sub_unlock = unlock_for_items[item]
			sub_costs = get_cost(sub_unlock)
			# get total cost to upgrade
			sub_cost = 0
			can_upgrade = True
			for sub_item in sub_costs:
				sub_amount = sub_costs[sub_item]
				if num_items(sub_item) < sub_amount:
					can_upgrade = False
				sub_cost += sub_amount
			# if its cheap enough or necessary for the upgrade then lets unlock it
			is_acceptable_cost = sub_cost <= acceptable_upgrade_cost
			is_needed = num_unlocked(sub_unlock) < 1 and item != Items.Wood  # wood unlocked with bushes not trees
			if can_upgrade or is_acceptable_cost or is_needed:
				if can_upgrade:
					did_unlock = unlock(sub_unlock)
				elif is_acceptable_cost or is_needed:
					did_unlock = smart_unlock(sub_unlock, acceptable_upgrade_cost)
				if did_unlock == False:
					while True:
						do_a_flip()
					return did_unlock


	# items needed to upgrade target

	# instead of insuring the order is correct, just make sure no crop was spent to farm another
	are_all_ok = False
	while not are_all_ok:
		# farm all
		for i in range(len(items)):
			item, amount = items[i]
			if num_items(item) >= amount:
				continue
			farm_item(item, amount)

		# check all
		are_all_ok = True
		for i in range(len(items)):
			item, amount = items[i]
			if num_items(item) < amount:
				are_all_ok = False
				break

	result = unlock(unlock_item)
	if result == False:
		while True:
			do_a_flip()  # something went wrong
	return result


def main(farm_func_for_item_override=None, unlock_order_override=None):
	global unlock_order
	global farm_func_for_item
	if farm_func_for_item_override != None:
		farm_func_for_item = farm_func_for_item_override
	if unlock_order_override != None:
		unlock_order = unlock_order_override
	total = len(unlock_order)

	last_time = get_time()
	for idx in range(total):
		unlock_item = unlock_order[idx]
		quick_print("[", idx + 1, "/", total, "] ", unlock_item)

		cost = get_cost(unlock_item)
		if cost == None:
			continue

		# instead of insuring the order is correct, just make sure no crop was spent to farm another
		result = smart_unlock(unlock_item)
		if not result:
			quick_print("FAILED: ", unlock_item)
			actual_cost = get_cost(unlock_item)
			if actual_cost != None:
				for cost_item in actual_cost:
					have = num_items(cost_item)
					need = actual_cost[cost_item]
					if have < need:
						quick_print("  Missing ", cost_item, ": ", have, "/", need)
			while True:
				do_a_flip()
		current_time = get_time()
		time_taken = current_time - last_time
		quick_print("\tUnlock Time: ", time_taken//60, "m ", time_taken %60, "s")
		last_time = current_time

	quick_print("=== COMPLETE === Time: ", get_time())
