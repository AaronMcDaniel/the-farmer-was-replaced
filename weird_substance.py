import movement
import crops
import utils
import multi


def plant_field(area, options=None):
	# options = {"secondary_entity": Entities.Grass}
	secondary_entity = Entities.Grass
	if options:
		if "secondary_entity" in options:
			secondary_entity = options["secondary_entity"]

	def plant_in_checkerboard(dest):
		movement.go_to(dest)
		if (dest[0] + dest[1]) % 2 == 0:
			if num_items(Items.Weird_Substance) > 1:
				use_item(Items.Weird_Substance)
			elif num_items(Items.Fertilizer) > 1:
				use_item(Items.Fertilizer)
			crops.plant_crop(Entities.Tree)
		else:
			crops.plant_crop(secondary_entity)

	utils.map_over_area(area, plant_in_checkerboard)


# Farm weird substance until we have at least 'amount'
# Uses parallel drones if Megafarm is unlocked, otherwise single-threaded
def farm(area, amount):
	def has_enough():
		return num_items(Items.Weird_Substance) >= amount

	if has_enough():
		return

	if num_unlocked(Unlocks.Megafarm) > 0:
		multi.run_func_until(area, plant_field, {"should_stop": has_enough})
	else:
		while not has_enough():
			plant_field(area)
