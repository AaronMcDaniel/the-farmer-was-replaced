import movement
import crops
import weird_substance

direction_to_right = {North: East, East: South, South: West, West: North}
direction_to_left = {North: West, West: South, South: East, East: North}


def get_substance_per_maze(maze_size):
	if maze_size == None:
		maze_size = get_world_size()
	return maze_size * 2 ** (num_unlocked(Unlocks.Mazes) - 1)


def get_gold_per_maze(maze_size):
	# Treasure gives gold equal to the maze side length
	# Maze side length = weird substance used
	return get_substance_per_maze(maze_size)

def move_no_loop(target_pos):
	while get_pos_x() > target_pos[0]:
		move(West)
	while get_pos_x() < target_pos[0]:
		move(East)
	while get_pos_y() > target_pos[1]:
		move(South)
	while get_pos_y() < target_pos[1]:
		move(North)

def initialize_maze(area):
	maze_pos, maze_size = area
	if maze_size == None:
		maze_size = (get_world_size(), get_world_size())
	harvest()
	move_no_loop((maze_pos[0]+maze_size[0]//2, maze_pos[1]+maze_size[0]//2))
	harvest()
	# don't loop because of maze walls
	crops.plant_crop(Entities.Bush)

	substance = maze_size [0]* 2 ** (num_unlocked(Unlocks.Mazes) - 1)
	use_item(Items.Weird_Substance, substance)

def arg_sort(my_list):
	sorted_is = []
	init_size = len(my_list)
	max_val = max(my_list)
	for i in range(init_size):
		min_i = 0
		min_val = max_val
		current_size = len(my_list)
		for j in range(current_size):
			cur_val = my_list[j]
			if cur_val <= min_val:
				min_val = cur_val
				min_i = j
		my_list[min_i] = max_val+1
		sorted_is.append(min_i)

	return sorted_is

def traverse_maze_left(should_harvest):
	current_dir = North
	found_treasure = False
	num_steps = 0

	while get_entity_type() == Entities.Hedge and found_treasure == False:
		right_dir = direction_to_right[current_dir]
		left_dir = direction_to_left[current_dir]
		back_dir = direction_to_right[right_dir]

		if can_move(left_dir):
			current_dir = left_dir
		elif can_move(current_dir):
			current_dir = current_dir
		elif can_move(right_dir):
			current_dir = right_dir
		else:
			current_dir = back_dir
		move(current_dir)
		num_steps+=1

		if get_entity_type() == Entities.Treasure:
			found_treasure = True
			if should_harvest:
				harvest()
			else:
				use_item(Items.Weird_Substance, get_substance_per_maze())

def get_traverse_maze(current_dir, is_left=True):
	right_dir = direction_to_right[current_dir]
	left_dir = direction_to_left[current_dir]
	back_dir = direction_to_right[right_dir]

	if is_left:
		first_dir = left_dir
		last_dir = right_dir
	else:
		first_dir = right_dir
		last_dir = left_dir

	if can_move(first_dir):
		current_dir = first_dir
	elif can_move(current_dir):
		current_dir = current_dir
	elif can_move(last_dir):
		current_dir = last_dir
	else:
		current_dir = back_dir

	return current_dir

def traverse_maze_right(should_harvest):
	current_dir = North
	found_treasure = False

	num_steps = 0

	while get_entity_type() == Entities.Hedge and found_treasure == False:
		right_dir = direction_to_right[current_dir]
		left_dir = direction_to_left[current_dir]
		back_dir = direction_to_right[right_dir]

		if can_move(right_dir):
			current_dir = right_dir
		elif can_move(current_dir):
			current_dir = current_dir
		elif can_move(left_dir):
			current_dir = left_dir
		else:
			current_dir = back_dir
		move(current_dir)
		num_steps += 1

		if get_entity_type() == Entities.Treasure:
			found_treasure = True
			if should_harvest:
				harvest()
			else:
				use_item(Items.Weird_Substance, get_substance_per_maze())

def apply_direction(pos, direction, num=1):
	if direction == North:
		return pos[0],pos[1]+num
	elif direction == South:
		return pos[0],pos[1]-num
	elif direction == East:
		return pos[0]+num, pos[1]
	else:
		return pos[0]-num, pos[1]

def update_map(world_map):
	scan_val = [can_move(North), can_move(South), can_move(East), can_move(West)]
	x,y = get_pos_x(), get_pos_y()
	world_map_x = x*2+1
	world_map_y = y*2+1
	if world_map_y < len(world_map) - 1:
		# North
		world_map[world_map_x][world_map_y+1] = scan_val[0]
	if world_map_y > 0:
		# South
		world_map[world_map_x][world_map_y-1] = scan_val[1]
	if world_map_x < len(world_map) - 1:
		# West
		world_map[world_map_x+1][world_map_y] = scan_val[2]
	if world_map_x > 0:
		# West
		world_map[world_map_x-1][world_map_y] = scan_val[3]

def build_graph(area):
	maze_pos, maze_size = area
	if maze_size == None:
		maze_size = (get_world_size(), get_world_size())
	world_graph = {}

	start_x, start_y = maze_pos[0] + maze_size[0]//2, maze_pos[1] + maze_size[1]//2
	movement.go_to((start_x, start_y))
	last_dir = South
	num_spaces = maze_size[0] ** 2
	found_spaces = None

	# traverse maze until loop is formed
	while True:
		directions = [North, South, East, West]
		x,y = get_pos_x(), get_pos_y()
		for dir in directions:
			if can_move(dir):
				next_pos = apply_direction((x,y), dir)
				if (x,y) not in world_graph:
					world_graph[(x,y)] = []
				if (next_pos, dir) not in world_graph[(x,y)]:
					world_graph[(x,y)].append((next_pos, dir))
		if found_spaces == None:
			found_spaces = {(x,y)}
		else:
			found_spaces.add((x,y))
		next_dir = get_traverse_maze(last_dir)
		move(next_dir)
		last_dir = next_dir
		if len(found_spaces) >= num_spaces and start_x == get_pos_x() and start_y == get_pos_y():
			break
	return world_graph

def construct_graph_from_world_map(world_map, maze_size):
	if maze_size == None:
		maze_size = get_world_size()
	world_graph = {}  # maps locations to adjacent locations
	for x in range(maze_size):
		for y in range(maze_size):
			world_graph[(x,y)] = []
			world_x = x*2 + 1
			world_y = y*2 + 1
			for direction in [North, South, East, West]:
				pos_wall = apply_direction((world_x, world_y), direction)
				is_free = world_map[pos_wall[0]][pos_wall[1]]
				if is_free:
					# add vertex
					pos_next = apply_direction((x,y), direction)
					world_graph[(x,y)].append((pos_next, direction))
	return world_graph

def dijkstras(start_x, start_y, target_x, target_y, world_graph, reverse=True):
	#algorithm to find shortest path from all points in graph to source
	#used to get from base location to all treasure locations

	#reverses paths so that paths start at start and end at each position

	shortest_paths = {(start_x, start_y): (0,[])}  # maps position to (distance, optimal path)
	open = []
	# initialize open set to adjacent nodes
	for adjacent in world_graph[(start_x, start_y)]:
		adj_pos, adj_dir = adjacent
		# position, total cost, path_here
		adj_entry = (adj_pos, 1, [adj_dir])
		open.append(adj_entry)
	closed = {(start_x, start_y)}


	while len(open) > 0:  # loop until no remaining nodes to explore
		current_pos, current_cost, path_here = open.pop()
		# check if is shortest
		is_shortest = False
		if current_pos not in shortest_paths:
			shortest_paths[current_pos] = (current_cost, path_here)
			is_shortest = True
		else:
			best_cost = shortest_paths[current_pos][0]
			if current_cost <= best_cost:
				# allow ties so we can explore more paths
				is_shortest = True
				shortest_paths[current_pos] = (current_cost, path_here)

		if is_shortest:
			# add adjacents to the open set if is good path and new vertex
			for adjacent in world_graph[current_pos]:
				adj_pos, adj_dir = adjacent
				# don't add duplicates
				if (adj_pos[0], adj_pos[1], adj_dir) not in closed:
					adj_entry = (adj_pos, current_cost + 1, [adj_dir] + path_here)
					open.append(adj_entry)

		# close the current node
		closed.add((current_pos[0], current_pos[1], path_here[-1]))

	#for key in shortest_paths:
	#	cost, path = shortest_paths[key]
	#	shortest_paths[key] = (cost, reverse_path(path))

	return shortest_paths

def travel(path):
	for dir in path:
		move(dir)

def travel_and_harvest(path, should_reuse, substance_per_maze):
	# travels the given path and  harvests or reuses the maze as requested
	travel(path)
	if should_reuse:
		use_item(Items.Weird_Substance, substance_per_maze)
	else:
		harvest()

def reverse_path(path):
	reversed_path = []
	for i in range(len(path)-1, -1, -1):
		dir = path[i]
		if dir == North:
			reversed_path.append(South)
		elif dir == South:
			reversed_path.append(North)
		elif dir == East:
			reversed_path.append(West)
		else:
			reversed_path.append(East)
	return reversed_path

def reuse_traverse(shortest_paths, should_reuse, area, single_threaded):
	substance_per_maze = get_substance_per_maze(area[1][0])
	if shortest_paths == None:
		world_graph = build_graph(area)
		start_x, start_y = get_pos_x(), get_pos_y()
		target_x, target_y = measure()
		shortest_paths = dijkstras(start_x, start_y, target_x, target_y, world_graph)

	target_pos = measure()
	dist, shortest_path = shortest_paths[target_pos]
	shortest_path = shortest_path[::-1]
	if single_threaded:
		reversed_shortest_path = reverse_path(shortest_path)
		travel_and_harvest(shortest_path, should_reuse, substance_per_maze)
		travel(reversed_shortest_path)
	else:
		spawn_drone(travel_and_harvest, shortest_path, should_reuse, substance_per_maze)

	return shortest_paths


def farm_maze(single_threaded, area):
	initialize_maze(area)

	# If Megafarm not unlocked, use single drone traversal
	if single_threaded or num_unlocked(Unlocks.Megafarm) == 0:
		traverse_maze_left(True)
		return

	# With Megafarm, race two drones (left and right wall-following)
	# Spawn one drone for left traversal, main drone does right traversal
	leftDrone = spawn_drone(traverse_maze_left, True)
	traverse_maze_right(True)  # Main drone traverses too

	# Wait for the other drone if it hasn't finished
	if not has_finished(leftDrone):
		wait_for(leftDrone)


def farm_subplot(area, amount, reuse):
	# farms gold in subplot region until the target amount is reached
	# intended for fast multithreaded farming since smaller mazes are solved faster
	def has_enough_gold():
			return num_items(Items.Gold) >= amount

	if has_enough_gold():
		return

	maze_size = area[1][0]
	substance_per_maze = get_substance_per_maze(maze_size)
	gold_per_maze = get_gold_per_maze(maze_size)

	while not has_enough_gold():
		# Calculate how many mazes we need to reach goal
		gold_needed = amount - num_items(Items.Gold)
		mazes_needed = (gold_needed // gold_per_maze) + 1

		# Farm weird substance in batches (enough for 10 mazes or remaining, whichever is smaller)
		batch_size = min(mazes_needed, 300)
		substance_needed = batch_size * substance_per_maze
		treasure_value = substance_needed
		current_substance = num_items(Items.Weird_Substance)

		if current_substance < substance_needed:
			weird_substance.farm(area, substance_needed)

		# Run mazes until we run out of substance or have enough gold
		num_treasures = 0
		initialize_maze(area)
		shortest_paths = None
		while num_items(Items.Weird_Substance) >= substance_per_maze and not has_enough_gold():
			if reuse:
				should_harvest = num_items(Items.Gold) + treasure_value >= amount or num_treasures >= 300
				shortest_paths = reuse_traverse(shortest_paths, should_harvest==False, area, True)
				num_treasures += 1
				treasure_value = num_treasures * gold_per_maze
				if should_harvest:
					# harvest and collect money
					initialize_maze(area)
					shortest_paths = None
					num_treasures = 0
			else:
				farm_maze(parallel==False, area)
	harvest()  # always clear plot

# Farm gold until we have at least 'amount'
# Note: area param is used for farming weird substance
# Most efficient gold farm uses multiple drones in small plots
def farm(area, amount, reuse=True, parallel=True, size=5):
	def has_enough_gold():
		return num_items(Items.Gold) >= amount

	if has_enough_gold():
		return

	# farm all weird substance first
	substance_per_maze = get_substance_per_maze(area[1][0])
	gold_per_maze = get_gold_per_maze(area[1][0])
	# Calculate how many mazes we need to reach goal
	gold_needed = amount - num_items(Items.Gold)
	mazes_needed = (gold_needed // gold_per_maze) + 1

	# Farm weird substance in batches (enough for 10 mazes or remaining, whichever is smaller)
	substance_needed = mazes_needed * substance_per_maze
	treasure_value = substance_needed
	current_substance = num_items(Items.Weird_Substance)

	if current_substance < substance_needed:
		weird_substance.farm(area, substance_needed)

	if parallel:
		# use subplot farming, one thread per subplot
		area_pos, area_size = area
		is_good_size = False
		prev_score = 0
		# find size that maximizes farming area
		while is_good_size == False:
			num_plots = area_size[0]//size * area_size[1]//size
			# can't have more plots than drones
			num_plots = min(num_plots, max_drones())
			plot_area = min(num_plots * size**2, area_size[0] * area_size[1])
			plot_score = plot_area * num_plots
			if plot_score <= prev_score:
				is_good_size = True
				size -= 2
			else:
				size += 2
				prev_score = plot_score

		if size > area_size[0]//2 and size > area_size[1]//2:
			# just use the whole area
			size = min(area_size)

		x_plots = area_size[0]//size
		y_plots = area_size[1]//size
		movement.go_to((size//2, size//2))
		# spawn in reverse order so drones have no trouble arriving
		should_stop = False
		running_drones = []
		for x_plot in range(x_plots-1, -1, -1):
			# convert plot number to world coords
			x = area_pos[0] + x_plot * size
			for y_plot in range(y_plots-1, -1, -1):
				y = area_pos[1] + y_plot * size
				if (y==0 and x==0) or num_drones() == max_drones():
					should_stop = True
					break
				subplot_area = ((x,y),(size,size))
				subplot_drone = spawn_drone(farm_subplot, subplot_area, amount, reuse)
				running_drones.append(subplot_drone)
			if should_stop:
				break
		# main drone runs bottom left plot
		subplot_area = ((0,0),(size,size))
		farm_subplot(subplot_area, amount, reuse)
		# wait for all drones to finish
		while len(running_drones) > 0:
			current_drone = running_drones.pop(0)
			if not has_finished(current_drone):
				wait_for(current_drone)

	else:
		substance_per_maze = get_substance_per_maze(area[1][0])
		gold_per_maze = get_gold_per_maze(area[1][0])

		while not has_enough_gold():
			# Calculate how many mazes we need to reach goal
			gold_needed = amount - num_items(Items.Gold)
			mazes_needed = (gold_needed // gold_per_maze) + 1

			# Farm weird substance in batches (enough for 10 mazes or remaining, whichever is smaller)
			batch_size = min(mazes_needed, 300)
			substance_needed = batch_size * substance_per_maze
			treasure_value = substance_needed
			current_substance = num_items(Items.Weird_Substance)

			if current_substance < substance_needed:
				weird_substance.farm(area, substance_needed)

			# Run mazes until we run out of substance or have enough gold
			num_treasures = 0
			initialize_maze(area)
			shortest_paths = None
			while num_items(Items.Weird_Substance) >= substance_per_maze and not has_enough_gold():
				if reuse:
					should_harvest = num_items(Items.Gold) + treasure_value >= amount or num_treasures >= 300
					shortest_paths = reuse_traverse(shortest_paths, should_harvest==False, area, True)
					num_treasures += 1
					treasure_value = num_treasures * gold_per_maze
					if should_harvest:
						# harvest and collect money
						initialize_maze(area)
						shortest_paths = None
						num_treasures = 0
				else:
					farm_maze(parallel==False, area)
		harvest()  # always clear plot