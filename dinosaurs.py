# Dinosaur farming - Hamiltonian cycle (zigzag + row 0 return)

def get_direction():
	x, y = get_pos_x(), get_pos_y()
	size = get_world_size()

	if y == 0:
		if x > 0:
			return West
		return North
	if x == size - 1:
		return South
	if x % 2 == 0:
		if y < size - 1:
			return North
		return East
	if y > 1:
		return South
	return East


def farm_field(area):
	clear()
	set_world_size(32)
	change_hat(Hats.Dinosaur_Hat)

	while True:
		if get_entity_type() == Entities.Apple:
			target_x, target_y = measure()
			snake_size += 1
		safety_size = 1+(snake_size+get_world_size()-1) // (get_world_size()-1)
		target_direction = get_direction()
		x_dist = abs(get_pos_x() - target_x)
		if target_x < get_pos_x():
			x_dist = abs(get_world_size() + target_x - get_pos_x())
		can_skip = can_move(East) and get_pos_x() < get_world_size()-1
		if get_pos_y() != 0 and can_skip and x_dist > safety_size:
			# skip next row if we can move there
			target_direction = East
		did_move = move(target_direction)
		if not did_move:
			break

	change_hat(Hats.Straw_Hat)


def plant_field(area):
	farm_field(area)


def farm(area, amount):
	while num_items(Items.Bone) < amount:
		farm_field(area)
