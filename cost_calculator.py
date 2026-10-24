import crops

# Global dictionary to keep track of current cost for one crop
current_crop_cost = {}

# Map items to their yield unlock
unlock_for_item = {
	Items.Hay: Unlocks.Grass,
	Items.Wood: Unlocks.Trees,
	Items.Carrot: Unlocks.Carrots,
	Items.Pumpkin: Unlocks.Pumpkins,
	Items.Cactus: Unlocks.Cactus,
}


def get_unlock_multiplier(item):
	# Each unlock level doubles yield: 2^(level-1)
	if item not in unlock_for_item:
		return 1
	unlock = unlock_for_item[item]
	level = num_unlocked(unlock)
	if level <= 1:
		return 1
	result = 1
	for i in range(level - 1):
		result = result * 2
	return result


def get_yield_per_planted(item):
	# Base yield from game mechanics + unlock multiplier
	unlock_mult = get_unlock_multiplier(item)
	n = get_world_size()

	# Pumpkin: nxn mega pumpkin yields n³ (n<6) or n²×6 (n>=6)
	# Yield per planted = n (n<6) or 6 (n>=6)
	# 20% death rate reduces effective yield to 80% (multiply by 4/5)
	# replanting multiple times means actually 50% yield in the limit since we require full pumpkin squares
	if item == Items.Pumpkin:
		if n < 6:
			base_yield = n
		else:
			base_yield = 6
		effective_yield = (base_yield * unlock_mult) // 2
		if effective_yield < 1:
			effective_yield = 1
		return effective_yield

	# Cactus: chain harvest of n² cacti gives (n²)² items
	# Yield per planted = n²
	if item == Items.Cactus:
		base_yield = n * n
		return base_yield * unlock_mult

	# Other crops: just the unlock multiplier
	return unlock_mult


def order_cost_list(cost_dict):
	ordered_list = []

	order_list = [
		Items.Hay,
		Items.Wood,
		Items.Carrot,
		Items.Pumpkin,
		Items.Cactus,
		Items.Weird_Substance,
		Items.Gold,
		Items.Bone,
	]

	for key in order_list:
		if key in cost_dict:
			ordered_list.append((key, cost_dict[key]))

	return ordered_list


def calculate_items_for_unlock_cost(target_unlock):
	totals = {}

	def expand(item, multiplier=1):
		cost = get_cost(item)

		if cost != None:
			new_cost = {}
			for k in cost:
				new_cost[k] = cost[k]
			current_crop_cost[item] = new_cost

		# Base item or maxed unlock
		if cost == None:
			return

		for sub_item in cost:
			amount = cost[sub_item] * multiplier

			if sub_item in totals:
				totals[sub_item] += amount
			else:
				totals[sub_item] = amount

			# For yield-multiplied crops, adjust the expansion multiplier
			if sub_item in crops.entity_for_item:
				entity = crops.entity_for_item[sub_item]
				yield_ratio = get_yield_per_planted(sub_item)
				if yield_ratio > 1:
					adjusted_amount = (amount // yield_ratio) + 1
				else:
					adjusted_amount = amount
				expand(entity, adjusted_amount)

	expand(target_unlock)
	return order_cost_list(totals)


def calculate_remaining_cost(target_unlock):
	# Returns only items we still need (subtracts current inventory)
	costs = calculate_items_for_unlock_cost(target_unlock)
	remaining = []
	for i in range(len(costs)):
		item, amount = costs[i]
		current = num_items(item)
		needed = amount - current
		if needed > 0:
			remaining.append((item, needed))
	return remaining
