import auto_unlock_utils
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

key_unlocks = [
	# max out speed
	Unlocks.Speed,        # 1
	Unlocks.Expand,       # 1
	Unlocks.Plant,
	Unlocks.Speed,        # 2
	Unlocks.Expand,       # 2
	Unlocks.Speed,        # 3
	Unlocks.Expand,       # 3
	Unlocks.Watering,     # 1
	Unlocks.Speed,        # 4
	Unlocks.Expand,       # 4
	Unlocks.Speed,        # 5 (MAX)
	# max out megafarm
	Unlocks.Expand,       # 5
	Unlocks.Fertilizer,   # 1
	Unlocks.Megafarm,     # 1  idx=21, good
	Unlocks.Megafarm,     # 2
	Unlocks.Expand,       # 6  idx 30, questionable  # 2hrs
	Unlocks.Megafarm,     # 3
	Unlocks.Expand,       # 7
	Unlocks.Megafarm,     # 4
	Unlocks.Expand,       # 8
	Unlocks.Expand,       # 9 (MAX)
	Unlocks.Megafarm,     # 5 (MAX)
	# get leaderboard
	Unlocks.Leaderboard,
]
# TODO:
# need to farm sunflowers when low, probably farm sunflower based on time estimate to finish task (need min(30, required amt))

auto_unlock_utils.main(farm_func_for_item, key_unlocks)