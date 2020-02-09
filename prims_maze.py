from PySide import QtCore
from PySide import QtGui
import sys
import os
from time import sleep

import random
from random import shuffle, randint, getrandbits
import sys
from math import floor
from collections import deque

ROOTDIR = r'D:\_GAME_PROJECTS\diablo\_dev\maze_generator'
TEMPLATEDIR = r'D:\_GAME_PROJECTS\diablo\_dev\maze_generator\room_templates'
ROOMSDIR = r'D:\_GAME_PROJECTS\diablo\_dev\maze_generator\rooms'

# Fill room 0 list
room_0_rooms = []
ROOM0DIR = os.path.join(ROOMSDIR, 'room_0')
for room in os.listdir(ROOM0DIR):
	room_0_rooms.append(os.path.join(ROOM0DIR, room))

# Fill room 1 list
room_1_rooms = []
ROOM1DIR = os.path.join(ROOMSDIR, 'room_1')
for room in os.listdir(ROOM1DIR):
	room_1_rooms.append(os.path.join(ROOM1DIR, room))

# Fill room 2 list
room_2_rooms = []
ROOM2DIR = os.path.join(ROOMSDIR, 'room_2')
for room in os.listdir(ROOM2DIR):
	room_2_rooms.append(os.path.join(ROOM2DIR, room))


class Cell():
	#
	#   0/forward
	#2/left      3/right
	#   1/back
	# top: 4
	# bot: 5
	def __init__(self,):
		self.name = None
		self.index = None
		self.walls = [ {'broken': False, 'neighbor': None, 'n_name': None, 'cell':self, 'i': i, 'ni': self.inv_i(i)} for i in range(0,6)]
		self.visited = False
		self.start = False
		self.end = False
		self.walls_broken = 0
		self.edge = -1
		self.roomtype = 0
		self.roomdir = None
		self.visited_bfs = False
		self.pathmain = False
		self.pathdir = None
		self.inbranch = False
		self.ancestor = None
		self.keyroom = False
		self.keydoor = False
		self.switchroom = False
		self.switchdoor = False

	def wall(self,i):
		return self.walls[i]

	def visit(self,i):
		self.visited = True

	def inv_i(self,i):
		return [1,0,3,2,5,4][i]

	def remove(self,i):
		self.walls[i]['broken'] = True
		self.visit(i)
		self.walls_broken += 1

		ni = self.inv_i(i)

		assert(self == self.walls[i]['neighbor'].walls[ni]['neighbor'])
		self.walls[i]['neighbor'].walls[ni]['broken'] = True
		self.walls[i]['neighbor'].visit(ni)
		self.walls[i]['neighbor'].walls_broken += 1

	def set_neighbor(self, i, n):
		ni = self.inv_i(i)
		self.walls[i]['neighbor'] = n
		self.walls[i]['neighbor'].walls[ni]['neighbor'] = self
		self.walls[i]['n_name'] = n.name

	def get_neighbors(self):
		neighbors = []
		for i in self.walls:
			if i['neighbor']:
				neighbors.append(i['neighbor'])
		return neighbors

	def mat(self,):
		return [self.walls[0]['broken'],self.walls[1]['broken'],
				self.walls[2]['broken'],self.walls[3]['broken'],
				self.walls[4]['broken'], self.walls[5]['broken']]

	def is_connected(self, node):
		for i in self.walls:
			if i['broken']:
				if i['neighbor'] == node:
					return True

	def open_walls(self):
		openWalls = []
		for wall in self.walls:
			if wall['broken']:
				openWalls.append(wall)
		return len(openWalls)

class MazeFactory:

	def __init__(self, openParam):
		self.openParam = openParam
		self.openings = {}
		self.maze_attributes = {}
		self.grid = None
		self.maze(4,4,1, openParam)

	def maze(self, width, height, depth, openParam):

		grid = [[[Cell() for x in range(width)] for y in range(height)] for z in range(depth)]
		openParamList = [x for x in range(openParam)]

		# Set cell position names to match UE4 module position naming
		cellNum = 0
		for layer in grid:
			for row in layer:
				row.reverse()
				for cell in row:
					cell.name = 'B' + "{0:02}".format(cellNum)
					cellNum = cellNum + 1
				row.reverse()

		for z in range(0,depth):
			for y in range(0,height):
				for x in range(0,width):
					if y == 0:                  # forward
						grid[z][y][x].edge = 0
					if y == height - 1:         # backward
						grid[z][y][x].edge = 1

					if x == 0:                  # left
						grid[z][y][x].edge = 2
					if x == (width - 1):        # right
						grid[z][y][x].edge = 3

					if z == 0:                  # top
						grid[z][y][x].edge = 4
					if z == (depth - 1):        # bottem
						grid[z][y][x].edge = 5


					# forward (height)
					if (y+1) < height:
						grid[z][y][x].set_neighbor(0, grid[z][y+1][x])

					# backward (height)
					if (y-1) >= 0:
						grid[z][y][x].set_neighbor(1,grid[z][y-1][x])

					# right (width)
					if (x+1) > width:
						grid[z][y][x].set_neighbor(3, grid[z][y][x+1])

					# left (width)
					if (x-1) >=0:
						grid[z][y][x].set_neighbor(2, grid[z][y][x-1])

					# top (depth)
					if (z+1) < depth:
						grid[z][y][x].set_neighbor(4, grid[z+1][y][x])

					# bottom (depth)
					if (z-1) >=0:
						grid[z][y][x].set_neighbor(5, grid[z-1][y][x])

		def pickRandomStart():
			# prim's alg
			random.seed()
			#start = random.choice(random.choice( grid[0] ) )
			startsearch = True
			while startsearch:
				start = random.choice ([ grid[0][0][0], grid[0][0][1], grid[0][0][2], grid[0][0][3], grid[0][1][0],
									grid[0][1][3], grid[0][2][0], grid[0][2][3], grid[0][3][0], grid[0][3][1],
									grid[0][3][2], grid[0][3][3] ])
				if start.visited == False:
					return start

		start = pickRandomStart()
		start.visited = True
		start.start = True
		wall_list = [] + start.walls
		startCell = start


	#	print 'running Prim\'s alg on potentially %d walls.' % (6 * height * width * depth)
		while len(wall_list):
			w = random.choice(wall_list)

			if w['neighbor']:
				if w['neighbor'].visited ^ w['cell'].visited:
					wall_list = wall_list + w['neighbor'].walls
					w['cell'].remove(w['i'])

			wall_list.remove(w)

		# depth-first-search to find the hardest path to determine end node, i.e. longest path
		def dfs(node, edge = None, depth = 0):
			walls = [] + node.walls
			children = []

			if edge is not None: del walls[edge]

			for x in walls:
				if x['broken']:
					children += dfs(x['neighbor'], x['ni'], depth + 1)

			return children + [(node, depth)]

		paths = dfs(start)
		end = paths[0]

		for i in paths:
			if i[0].edge  == 5:
				if i[1] > end[1]:
					end = i

		print 'correct path is %d nodes long' % end[1]
		end = end[0]

		end.end = True
		endCell = end.name
		#print( 'Possible start locations: ' + grid[0][0][0].name, grid[0][2][2].name, grid[0][2][0].name )

		# Get direction from i[ni]
		def direction(ni):
			if ni == 0:
				return 'N'
			elif ni == 1:
				return 'S'
			elif ni == 2:
				return 'W'
			elif ni == 3:
				return 'E'
			elif ni == 4:
				return 'T'
			elif ni == 5:
				return 'B'

		roomtype_0 = []
		roomtype_1 = []
		roomtype_2 = []
		roomtype_3 = []
		roomtype_4 = []
		roomtype_5 = []

		def removeCell(cell):
			cell.roomtype = 0


		# Remove dead ends
		for layer in grid:
			for row in layer:
				for cell in row:
					if cell.start == False and cell.end == False:
						openWalls = []
						for wall in cell.walls:
							if wall['broken']:
								openWalls.append(wall)
						# Room type 0 (dead end)
						if len(openWalls) == 1:
							openWalls[0]['neighbor'].walls[openWalls[0]['ni']]['broken'] = False
							openWalls[0]['broken'] = False
							cell.visited = False

		def getBranchStartNode(paths):

			midnode = paths[int(floor(len(paths)/2))][0]

			#print('branch off node: {}'.format(midnode.name))
			closedneighbors = [i['neighbor'] for i in midnode.walls if i['broken'] == False]
			# Filter only to valid nodes we can branch to
			filternodes = [i for i in closedneighbors if i]
			try:
				branchnode = random.choice([i for i in filternodes if i.end == False])
				#print('open to random neighbor: {}'.format(branchnode.name))
				return midnode, branchnode
			except IndexError:
				print('NO VALID PATH! try to get another')
				return

		paths = dfs(start)

		pathdict = {}
		startpathlist = []
		for path in paths:
			pathdict[path[0].name] = path[1]
		for key, value in sorted(pathdict.items(), key=lambda item: item[1]):
			startpathlist.append(key)
		print('dfs startpath sort: {}'.format([i for i in startpathlist]))

		#print('dfs startpath: {}, depth value: {}'.format([i[0].name for i in paths], [i[1] for i in paths]))
		endpaths = dfs(end)

		endpathdict = {}
		endpathlist = []
		for path in endpaths:
			endpathdict[path[0].name] = path[1]
		for key, value in sorted(endpathdict.items(), key=lambda item: item[1]):
			endpathlist.append(key)
		#print('dfs endpath sort: {}'.format([i for i in endpathlist]))
		print('End loop: end {} to {}, {}, {}'.format(endpathlist[0], endpathlist[-1], endpathlist[-2],
													  endpathlist[-3]))

		def shortestpath(paths, start, end):
			# keep track of explored nodes
			explored = []
			# keep track of all the paths to be checked
			queue = [[start]]
			# keeps looping until all possible paths have been checked
			while queue:
				# pop the first path from the queue
				path = queue.pop(0)
				# get the last node from the path
				node = path[-1]
				if node not in explored:
					neighbors = node.get_neighbors()
					# go through all neighbour nodes, construct a new path and
					# push it into the queue
					for neighbor in neighbors:
						if neighbor.visited and neighbor.is_connected(node):
							new_path = list(path)
							new_path.append(neighbor)
							queue.append(new_path)
							# return path if neighbour is goal
							if neighbor == end:
								return new_path
		solution_path = shortestpath(paths, start, end)

		def set_solution_path_node_index(solution_path):
			for i in range(0, len(solution_path)):
				solution_path[i].index = i
		set_solution_path_node_index(solution_path)

		# Set solution path direction
		def set_solution_path(solution_path):
			q = deque(solution_path)
			visited = []
			while q:
				current = q.popleft()
				#print('visiting...{}'.format(current.name))
				current.pathmain = True
				for wall in current.walls:
					if wall['broken']:
						if wall['neighbor'] in solution_path and wall['neighbor'] not in visited:
							current.pathdir = direction(wall['ni'])
							visited.append(current)

		set_solution_path(solution_path)
		print('solution path: {}'.format([i.name for i in solution_path]))

		def walk_branch(node, children=[]):
			node.visited_bfs = True
			#print('walking branch...')
			for neighbor in node.get_neighbors():
				if neighbor.is_connected(node) and neighbor not in solution_path and neighbor.visited_bfs == False:
					#print('add neighbor: {}'.format(neighbor.name))
					children.append(neighbor)
					neighbor.visited_bfs = True
					walk_branch(neighbor, children)
			return children

		def get_connected_components(solution_path):
			connected_components = []
			component_dict = {}
			for node in solution_path:
				connected_components = []
				for neighbor in node.get_neighbors():

					if neighbor.is_connected(node) and neighbor not in solution_path:
						#print('Found connected branch head: {}'.format(neighbor.name))
						branch = []

						branch_ancestor = node
						branch.append(neighbor)
						#print('branch starting at {}'.format([i.name for i in branch]))
						# Walk down branch and add to branch list
						children = walk_branch(neighbor, [])
						#print('children to be appended: {}'.format([i.name for i in children]))
						for child in children:
							branch.append(child)
							child.inbranch = True
							child.ancestor = branch_ancestor
						#children = []
						connected_components.append(branch)
						component_dict[branch_ancestor] = list(connected_components)
			return component_dict, connected_components


		connected_components = get_connected_components(solution_path)
		ancestors = [a for a in connected_components[0].keys()]

		#print(connected_components)
		for ancestor in connected_components[0].keys():
			print('Comp ancestor: {}'.format(ancestor.name), 'Branch: {}'.format([[i.name for i in b] for b in connected_components[0][ancestor]]))
			for branch in connected_components[0][ancestor]:
				for node in branch:
					if node.open_walls() == 3:
						print('COMP JUNCTION')
						# Try to connect nodes connected to this junction
						#choice = random.choice([i for i in branch if i.open_walls() == 1])
						print('CONNECTING JUNCT NODES ONLY IF THEY ARE CLOSE: {}'.format([i.name for i in branch if i.open_walls() == 1]))
				for node in branch:
					if ancestor in node.get_neighbors() and node != branch[0]:
						print('COMP ANCESTOR NEIGHBOR {}'.format(node.name))
			for n in ancestor.get_neighbors():
				if n in ancestors:
					print('COMP ADJACENT ANCESTORS')
					# If components are neighbors, connect them, bias for first in branch for tighter loop
					# If not, one could have a key that unlocks the other for a special item
			for i.index in ancestors:
				if i.index == ancestor.index + 2 or i.index == ancestor.index - 2:
					print('COMP ADJACENT + NEIGHBOR ANCESTORS')
			# If ancestor has two components, try to connect them
			if len(connected_components[0][ancestor]) == 2:
				print('2 COMP ANCESTOR')
				# If an ancestor has 2 components connected, if they have neighboring cells connect them
				# If they are not neighbors, one can hold a switch that unlocks the other for
				# a special item





		#	print('are components with length {}'.format(len(connected_components)))
			#for ancestor, components in connected_components.items():
			#	print('Component ancestor {}'.format(ancestor.name),
			#	  'Components: {}'.format([ [i.name for i in branch] for branch in components]))
		#	for key in connected_components:
		#		print('components: {}'.format(connected_components[key]))




		def get_valid_key_room(connected_components, locked_path):
			valid_dead_ends = []
			for ancestor, branch in connected_components[0].items():
				if ancestor.index <= locked_path.index:
					for b in branch:
						valid_dead_ends.append(b[-1])
			return valid_dead_ends
		'''
		def component_cycles(connected_components):
			if len(connected_components[0]):
				#for component in connected_components[0]:
				for ancestor, branch in connected_components[1].items():
					branchnode = random.choice(branch)
					print('component cycle selected {}'.format(branchnode.name))
					for neighbor in branchnode.get_neighbors():
						if neighbor.visited == False:
							for n in neighbor.get_neighbors():
								if n.pathmain:
									print('Connect component from {} to {}'.format(branchnode.name, n.name))
									if n.index <= ancestor.index:
										print('Cycle connects upstream')
									elif n.index >= ancestor.index:
										#print('Cycle connects downstream, add lock at {}'.format(n.name))
										if n.end:
											print('Cycle connects to end!')
									return
								elif n.visited == False and len(branch)>1:
									print('Create a one way reward from {} to {}'.format(branchnode.name, branch[-1].name))
									return
						elif neighbor.visited == True:
							if branchnode.is_connected(neighbor):
								#print('already connected, continue')
								pass
							else:
								print('connect visited {} to {}'.format(branchnode.name, neighbor.name))

		component_cycles(connected_components)
		'''

		def add_cycle(component):
			if len(component) == 1:
				component



		'''
		Function to find junctions in maze and add lock / keys
		Will get random junction and add a locked door on the solution path opening.
		Adds a key at random dead end earlier in the path
		'''

		def find_junctions(solution_path):
			junctions = []
			for node in solution_path:
				if node.open_walls() == 3 or node.open_walls() == 4:
					print('Junction at: {}'.format(node.name))
					junctions.append(node)
			if len(junctions):
				locked_path = random.choice(junctions)
				dead_ends = get_valid_key_room(connected_components, locked_path)
				if len(dead_ends):
					key_room = random.choice(dead_ends)
					locked_path.keydoor = True
					key_room.keyroom = True
					print('Success! Locked door at junction {}, key at {}'.format(locked_path.name, key_room.name))
					#carve_path(key_room, locked_path)
				else:
					print('Abort: no valid dead ends to place key')

		'''
		def carve_path(src, dest):
			# Filter only to valid nodes we can branch to
			closedneighbors = [i['neighbor'] for i in src.walls if i['broken'] == False]
			filternodes = [i for i in closedneighbors if i]
			validnodes = []
			print('dest index to check against: {}'.format(dest.index))
			for node in filternodes:
				if node.index:
					if node.index <= dest.index:
						print('appending node {} with index value {}'.format(node.name, node.index))
						validnodes.append(node)
				elif node.inbranch and node.ancestor.index <= dest:
					print('appending branch node {} with ancestor index value {}'.format(node.name, node.ancestor.index))
					validnodes.append(node)
				else:
					# If it doesn't have an index and it's not in a branch, check if its a closed node adjacent
					# to path or valid branch
					for neighbor in node.get_neighbors():
						for wall in neighbor.walls:
							# Is it the main path?
							if wall['neighbor']:
								if wall['neighbor'].pathmain and wall['neighbor'].index <= dest.index and wall['neighbor'] != src:
									if wall['neighbor'] not in validnodes:
										print('appending valid main path node {}'.format(wall['neighbor'].name))
										validnodes.append(wall['neighbor'])
								# Is it a valid branch?
								elif wall['neighbor'].inbranch and wall['neighbor'].ancestor.index <= dest.index:
									print('appending valid branch node {}'.format(neighbor.name))
									validnodes.append(node)

			print('using valid nodes {}'.format([i.name for i in validnodes]))
			try:
				# First get neighbors of closed node
				for node in validnodes:
					for neighbor in node.get_neighbors():
						for wall in neighbor.walls:
							if wall['neighbor'] == dest:
								print('path looks valid, do final checks before carve')
								# Final checks

								for wall in src.walls:
									if wall['neighbor'] == node:
										src.remove(wall['i'])
										node.remove(wall['ni'])
										print('successful carve! from {} to {}'.format(src.name, node.name))
										return

							else:
								print('abort, path not valid')

						#for wall in node.walls:



						#for wall in node.walls:
						#	# If we are next to dest, carve a path to it
						#	if wall['neighbor'] == dest:
						#		node.remove(wall['i'])
						#		dest.remove(node.walls[wall['ni']['i']])
						#		print('Success! Carved path from src ( {} ) to dest ( {} )'.format(src.name, dest.name))
					else:
						#branchnode = random.choice([i for i in filternodes if i.end == False])
						print('abort - dest is not close enough to src')
			except IndexError:
				print('abort - tried to carve from src {} to dest {}, but no valid path found'.format(src.name, dest.name))
				return
		'''


		find_junctions(solution_path)

		'''
		createdcycle = False
		midnode = None
		try:
			midnode, branchnode = getBranchStartNode(paths)
			print('Success! from midnode: {}, to branchnode: {}'.format(midnode.name, branchnode.name))
			for wall in midnode.walls:
				if wall['neighbor'] == branchnode:
					#wall['broken'] = True
					midnode.remove(wall['i'])
					#branchnode.walls[wall['ni']]['broken'] = True
					branchnode.remove(branchnode.walls[wall['ni']['i']])
					if branchnode in [i[0] for i in paths]:
						print('Created cycle! Branch node in paths')
						createdcycle = True
		except TypeError:
			print('Couldnt get branch node, abort carve path')

		# Carve a path to create a cycle, starting at branchnode
		branchLimit = 4
		def carvePath(branchnode, branchlimit):
			branchlimit = branchlimit
			# First, get neighbors
			neighbors = []
			for wall in branchnode.walls:
				if wall['broken'] == False:
					neighbors.append(wall['neighbor'])
			neighbors = [i for i in neighbors if i]
			neighbors = [i for i in neighbors if i.pathmain == False]
			if len(neighbors) != 0:
				#print('found neighbors: {}'.format([i.name for i in neighbors]))
				neighbor = random.choice(neighbors)
			else:
				print('no neighbors found, abort carve path')
				return
			# Found a valid neighbor to carve path to, now connect it to branch node
			if branchlimit != 0:
				for wall in neighbor.walls:
					if wall['neighbor'] == branchnode:
						#wall['broken'] = True
						neighbor.remove(wall['i'])
						#branchnode.walls[wall['ni']]['broken'] = True
						branchnode.remove(wall['ni'])
						print('carved from: {}, to: {}'.format(branchnode.name, neighbor.name))
						branchlimit = branchlimit - 1
						carvePath(neighbor, branchlimit)

		if createdcycle == False and midnode:
			carvePath(branchnode, branchLimit)


		'''
		#print('after carving dfs: {}, depth value: {}'.format([i[0].name for i in endpath], [i[1] for i in endpath]))
		'''
		for layer in grid:
			for row in layer:
				for cell in row:
					openWalls = []
					for wall in cell.walls:
						if wall['broken']:
							pass
						else:
							r = random.choice(openParamList)
							if r == 1:
								wall['broken'] = True if wall['neighbor'] is not None else False
								if not wall['neighbor'] is None:
									wall['neighbor'].walls[wall['ni']]['broken'] = True
							else:
								continue

		'''
		'''
		Label room types and direction
		For template placement

		attr: cell.roomtype

		0 : 1 opening, dead end
		1 : 2 openings, hallway
		2 : 2 openings, corner
		3 : 3 openings
		4 : 4 openings
		5 : Closed?

		attr: cell.roomdir
		N, S, E, W
		'''
		# Walk through maze and label each cell as a room type
		# based on open wall amount and orientation
		for layer in grid:
			for row in layer:
				for cell in row:
					#if cell.start == False and cell.end == False:
					if cell.name:
						openWalls = []
						for wall in cell.walls:
							if wall['broken']:
								openWalls.append(wall)
						# Room type 0 (dead end)
						if len(openWalls) == 1:
							cell.roomtype = 0
							cell.roomdir = direction(openWalls[0]['ni'])
							roomtype_5.append(cell)
						# Room type 1 (hallway)
						if len(openWalls) == 2:
							walldirs = [direction(x['ni']) for x in openWalls]
							if all(x in walldirs for x in ['N', 'S']):
								cell.roomtype = 1
								cell.roomdir = 'N'
								roomtype_1.append(cell)
							elif all(x in walldirs for x in ['E', 'W']):
								cell.roomtype = 1
								cell.roomdir = 'E'
								roomtype_1.append(cell)
							# Room type 2 (corner openings)
							elif all(x in walldirs for x in ['N', 'E']):
								cell.roomtype = 2
								cell.roomdir = 'N'
								roomtype_2.append(cell)
							elif all(x in walldirs for x in ['S', 'E']):
								cell.roomtype = 2
								cell.roomdir = 'E'
								roomtype_2.append(cell)
							elif all(x in walldirs for x in ['S', 'W']):
								cell.roomtype = 2
								cell.roomdir = 'S'
								roomtype_2.append(cell)
							elif all(x in walldirs for x in ['N', 'W']):
								cell.roomtype = 2
								cell.roomdir = 'W'
								roomtype_2.append(cell)
						# Room type 3
						if len(openWalls) == 3:
							walldirs = [direction(x['ni']) for x in openWalls]
							roomtype_3.append(cell)
							if all(x in walldirs for x in ['W', 'N', 'E']):
								cell.roomtype = 3
								cell.roomdir = 'N'
							elif all(x in walldirs for x in ['N', 'E', 'S']):
								cell.roomtype = 3
								cell.roomdir = 'E'
							elif all(x in walldirs for x in ['E', 'S', 'W']):
								cell.roomtype = 3
								cell.roomdir = 'S'
							elif all(x in walldirs for x in ['S', 'W', 'N']):
								cell.roomtype = 3
								cell.roomdir = 'W'
						# Room type 4
						if len(openWalls) == 4:
							roomtype_4.append(cell)
							cell.roomtype = 4
							cell.roomdir = 'N'
						if len(openWalls) == 0:
							cell.roomtype = 5
						if cell.keydoor:
							print('Key door at: {}, {}'.format(cell.name, cell.keydoor))

		self.maze_attributes = {'room_type_0' : len(roomtype_0), 'room_type_1' : len(roomtype_1), 'room_type_2' : len(roomtype_2), 'room_type_3' : len(roomtype_3), 'room_type_4' : len(roomtype_4), 'start' : startCell, 'end' : endCell }

		def set_openings(grid):

			openings = {
						# Top/Bottom Openings
						'D00' : False,
						'D01' : False,
						'D02' : False,
						'D03' : False,
						'D04' : False,
						'D05' : False,
						'D06' : False,
						'D07' : False,
						'D08' : False,

						# Wall Openings
						'C00' : False,
						'C01' : False,
						'C02' : False,
						'C03' : False,
						'C04' : False,
						'C05' : False,
						'C06' : False,
						'C07' : False,
						'C08' : False,
						'C09' : False,
						'C10' : False,
						'C11' : False,
						'C12' : False,
						'C13' : False,
						'C14' : False,
						'C15' : False,
						'C16' : False,
						'C17' : False,
						'C18' : False,
						'C19' : False,
						'C20' : False,
						'C21' : False,
						'C22' : False,
						'C23' : False,
}
			# Set openings
			grid = grid
			for layer in grid:
				for row in layer:
					for cell in row:
						if cell.name == 'B00':
							openings['D00'] = True if cell.walls[4]['broken'] else False
							openings['C00'] = True if cell.walls[0]['broken'] else False
							openings['C01'] = True if cell.walls[2]['broken'] else False
						if cell.name == 'B01':
							openings['D01'] = True if cell.walls[4]['broken'] else False
							openings['C02'] = True if cell.walls[0]['broken'] else False
							openings['C03'] = True if cell.walls[2]['broken'] else False
						if cell.name == 'B02':
							openings['D02'] = True if cell.walls[4]['broken'] else False
							openings['C04'] = True if cell.walls[0]['broken'] else False
						if cell.name == 'B03':
							openings['D03'] = True if cell.walls[4]['broken'] else False
							openings['C05'] = True if cell.walls[0]['broken'] else False
							openings['C06'] = True if cell.walls[2]['broken'] else False
						if cell.name == 'B04':
							openings['D04'] = True if cell.walls[4]['broken'] else False
							openings['C07'] = True if cell.walls[0]['broken'] else False
							openings['C08'] = True if cell.walls[2]['broken'] else False
						if cell.name == 'B05':
							openings['D05'] = True if cell.walls[4]['broken'] else False
							openings['C09'] = True if cell.walls[0]['broken'] else False
						if cell.name == 'B06':
							openings['D06'] = True if cell.walls[4]['broken'] else False
							openings['C10'] = True if cell.walls[2]['broken'] else False
						if cell.name == 'B07':
							openings['D07'] = True if cell.walls[4]['broken'] else False
							openings['C11'] = True if cell.walls[2]['broken'] else False
						if cell.name == 'B08':
							openings['D08'] = True if cell.walls[4]['broken'] else False
						if cell.name == 'B09':
							openings['C12'] = True if cell.walls[0]['broken'] else False
							openings['C13'] = True if cell.walls[2]['broken'] else False
						if cell.name == 'B10':
							openings['C14'] = True if cell.walls[0]['broken'] else False
							openings['C15'] = True if cell.walls[2]['broken'] else False
						if cell.name == 'B11':
							openings['C16'] = True if cell.walls[0]['broken'] else False
						if cell.name == 'B12':
							openings['C17'] = True if cell.walls[0]['broken'] else False
							openings['C18'] = True if cell.walls[2]['broken'] else False
						if cell.name == 'B13':
							openings['C19'] = True if cell.walls[0]['broken'] else False
							openings['C20'] = True if cell.walls[2]['broken'] else False
						if cell.name == 'B14':
							openings['C21'] = True if cell.walls[0]['broken'] else False
						if cell.name == 'B15':
							openings['C22'] = True if cell.walls[2]['broken'] else False
						if cell.name == 'B16':
							openings['C23'] = True if cell.walls[2]['broken'] else False
			return openings

		self.openings = set_openings(grid)
		self.grid = grid

'''
		for layer in grid:
			for row in layer:
				for cell in row:
					if cell.start:
						print('Starting cell is at: ' + cell.name )
						startCell = cell.name
					if cell.end:
						print( 'Ending cell is at: ' + cell.name )
						endCell = cell.name
					if cell.deadEnd:
						deadEndTotal.append(cell)
					if cell.pit:
						pitTotal.append(cell.name)
						print( 'PIT AT: ' + cell.name )
					if cell.drop:
						dropTotal.append(cell.name)
						print( 'DROP AT: ' + cell.name )
					if cell.vault:
						vaultTotal.append(cell.name)
						print( 'VAULT AT: ' + cell.name )
						print( 'VAULT OPENING WALL: ' + cell.vaultDirection )



	def maze_iteration_stats(self, amount):

		dead_end_counter = 0
		drop_counter = 0
		pit_counter = 0
		vault_counter = 0
		end_spawn_top_counter = 0
		end_spawn_bot_mid_counter = 0

		print('Ran ' + str(amount) + ' iterations.')
		for i in range(0, amount):
			m = self.maze(3,3,2,self.openParam)
			print(m)
			drop_counter = drop_counter + m['drops']
			pit_counter = pit_counter + m['pits']
			vault_counter = vault_counter + m['vaults']


		# Calculate percentage of dead ends and types
		total_cells = 18.0
		vault_percent = round ( (( float(vault_counter) / (total_cells * float(amount)) )*100.0 ) )
		drop_percent = round ( (( float(drop_counter) / (total_cells * float(amount)) )*100.0 ) )
		pit_percent = round ( (( float(pit_counter) / (total_cells * float(amount)) )*100.0 ) )

		print ('Total vaults: ' + str(vault_counter)  + ' / Percent: ' + str(vault_percent) )
		print ('Total drops: ' + str(drop_counter)  + ' / Percent: ' + str(drop_percent) )
		print ('Total pits: ' + str(pit_counter)  + ' / Percent: ' + str(pit_percent) )
'''
class MazeViewer(QtGui.QDialog):

	def __init__(self, parent=None):
		QtGui.QDialog.__init__(self, parent)

		self.openParameter = 0

		self.setWindowTitle('Prims maze visualizer')
		self.setMinimumSize(QtCore.QSize(750*2, 1044))
		#self.setMinimumSize(QtCore.QSize(950, 1050))
		self.mainLayout = QtGui.QHBoxLayout()
		self.sideWidget = QtGui.QFrame()
		self.sideWidget.setMinimumSize(QtCore.QSize(200, 0))
		self.sideLayout = QtGui.QVBoxLayout()
		self.sideWidget.setLayout(self.sideLayout)

		self.setLayout(self.mainLayout)
		self.mazeView = MazeView()

		self.generateButton = QtGui.QPushButton('Generate')
		self.generateButton.clicked.connect(self.generate)

		self.openSlider = QtGui.QSlider()
		self.openSlider.setOrientation(QtCore.Qt.Horizontal)
		self.openSlider.setMinimum(2)
		self.openSlider.setMaximum(20)
		self.openSlider.valueChanged.connect(self.setOpenParameter)
		self.openParameter = 6# Default 6
		self.statsButton = QtGui.QPushButton('Iteration stats')
		self.statsButton.clicked.connect(self.stats)

		#Update tableview
		self.tableView = QtGui.QTableWidget(5, 2)
		self.tableView.setMinimumSize(QtCore.QSize(200, 0))
		self.tableView.setVerticalHeaderLabels(['Start', 'End', 'Vaults', 'Pits', 'Drops'])
		self.tableView.setHorizontalHeaderLabels(['Location', 'Total'])

		# Locations
		self.tableView.setItem(0, 0, QtGui.QTableWidgetItem(""))
		self.tableView.setItem(1, 0, QtGui.QTableWidgetItem(""))
		self.tableView.setItem(2, 0, QtGui.QTableWidgetItem(""))
		self.tableView.setItem(3, 0, QtGui.QTableWidgetItem(""))
		self.tableView.setItem(4, 0, QtGui.QTableWidgetItem(""))
		# Totals
		self.tableView.setItem(1, 0, QtGui.QTableWidgetItem(""))
		self.tableView.setItem(1, 1, QtGui.QTableWidgetItem(""))
		self.tableView.setItem(1, 1, QtGui.QTableWidgetItem(""))
		self.tableView.setItem(2, 1, QtGui.QTableWidgetItem(""))
		self.tableView.setItem(3, 1, QtGui.QTableWidgetItem(""))
		self.tableView.setItem(4, 1, QtGui.QTableWidgetItem(""))

		self.splitter = QtGui.QSplitter()

		self.sideLayout.addWidget(self.generateButton)
		self.sideLayout.addWidget(self.tableView)
		self.sideLayout.addWidget(self.openSlider)
		self.sideLayout.addWidget(self.statsButton)

		self.splitter.addWidget(self.mazeView)
		self.splitter.addWidget(self.sideWidget)

		self.mainLayout.addWidget(self.splitter)

	def updateTable(self, maze_attributes):

		maze_attr = maze_attributes
		# Locations
		self.tableView.item(0, 0).setText(maze_attr['start'])
		self.tableView.item(1, 0).setText(maze_attr['end'])
		#self.tableView.item(2, 0).setText(' ,'.join(sorted(maze_attr['vaults'])))
		#self.tableView.item(3, 0).setText(' ,'.join(sorted(maze_attr['pits'])))
		#self.tableView.item(4, 0).setText(' ,'.join(sorted(maze_attr['drops'])))
		# Totals
		#self.tableView.item(2, 1).setText(str(len(maze_attr['vaults'])) )
		#self.tableView.item(3, 1).setText(str(len(maze_attr['pits'])) )
		#self.tableView.item(4, 1).setText(str(len(maze_attr['drops'])) )
		#self.tableView.resizeColumnToContents(0)

	def direction(self,ni):
		if ni == 0:
			return 'N'
		elif ni == 1:
			return 'S'
		elif ni == 2:
			return 'W'
		elif ni == 3:
			return 'E'
		elif ni == 4:
			return 'T'
		elif ni == 5:
			return 'B'

	# Get state of maze instance to draw
	def generate(self):

		self.maze = MazeFactory(self.openParameter)
		self.mazeView.QS.clear()
		self.mazeView.QS.update_maze(self.maze, self.mazeView.QS.NUM_BLOCKS_X, self.mazeView.QS.NUM_BLOCKS_Y, self.mazeView.QS.WIDTH, self.mazeView.QS.HEIGHT )


		#if self.maze.maze_attributes['lifts'] != 1:
		#	print('0 or more than 3, re-running... (found %d lifts this generation)' % self.maze.maze_attributes['lifts'])
		#	self.generate()
		#else:
		#	print('success! (found %d lifts this generation)' % self.maze.maze_attributes['lifts'])


		#self.updateTable(self.maze.maze_attributes)

		#print(self.maze.openings)
		#print(self.maze.maze_attributes)
		print('generated')

	def stats(self):
		MazeFactory(self.openParameter).maze_iteration_stats(100)

	def setOpenParameter(self):
		self.openParameter = self.openSlider.value()
		print(self.openParameter)

class MazeView(QtGui.QGraphicsView):
	photoClicked = QtCore.Signal(QtCore.QPoint)
	def __init__(self, parent=None):
		QtGui.QGraphicsView.__init__(self, parent)

		self.setMinimumSize(1200, 1024)
		self.QS = QS(4, 4, 512, 512)
		self.setScene(self.QS)
		self.setSceneRect(0, 0, 2048, 2048)
		self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
	# Mouse wheel zoom function
	def wheelEvent(self, event):
		# Zoom Factor
		zoomInFactor = 1.25
		zoomOutFactor = 1 / zoomInFactor

		# Set Anchors
		self.setTransformationAnchor(QtGui.QGraphicsView.NoAnchor)
		self.setResizeAnchor(QtGui.QGraphicsView.NoAnchor)

		# Save the scene pos
		oldPos = self.mapToScene(event.pos())

		# Zoom
		if event.delta() > 0:
		    zoomFactor = zoomInFactor
		else:
		    zoomFactor = zoomOutFactor
		self.scale(zoomFactor, zoomFactor)

		# Get the new position
		newPos = self.mapToScene(event.pos())

		# Move scene to old position
		delta = newPos - oldPos
		self.translate(delta.x(), delta.y())

	def mousePressEvent(self, event):
		self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
		super(MazeView, self).mousePressEvent(event)

class QS(QtGui.QGraphicsScene):

	def __init__(self, NUM_BLOCKS_X, NUM_BLOCKS_Y, WIDTH_BLOCK, HEIGHT_BLOCK):
		QtGui.QGraphicsScene.__init__(self, NUM_BLOCKS_X, NUM_BLOCKS_Y, WIDTH_BLOCK, HEIGHT_BLOCK)

		self.NUM_BLOCKS_X = NUM_BLOCKS_X
		self.NUM_BLOCKS_Y = NUM_BLOCKS_Y
		self.WIDTH = WIDTH_BLOCK
		self.HEIGHT = HEIGHT_BLOCK

		padding = 20
		width = (self.NUM_BLOCKS_X * WIDTH_BLOCK) + padding
		height = self.NUM_BLOCKS_Y * HEIGHT_BLOCK


		self.setSceneRect(0, 0, width, height)
		self.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
		self.bgBrush = QtGui.QBrush(QtGui.QColor(50,50,50))
		self.setBackgroundBrush(self.bgBrush)
		self.drawBaseGrid()

	def drawBaseGrid(self):

		NUM_BLOCKS_X = self.NUM_BLOCKS_X
		NUM_BLOCKS_Y = self.NUM_BLOCKS_Y
		WIDTH_BLOCK = self.WIDTH
		HEIGHT_BLOCK = self.HEIGHT

		padding = 20
		width = (self.NUM_BLOCKS_X * WIDTH_BLOCK) + padding
		height = self.NUM_BLOCKS_Y * HEIGHT_BLOCK

		# Draw vertical grid lines
		offset = 0
		subdiv = 3
		for i in range(0, 3):
			for x in range(0, NUM_BLOCKS_X+1):
				xc = x * WIDTH_BLOCK + offset
				self.addLine(xc, 0, xc, height)

			# Draw horizontal subgrid lines
			for y in range(0, NUM_BLOCKS_Y+1):
				yc = y * HEIGHT_BLOCK
				self.addLine(0 + offset, yc, (width-padding) + offset, yc)

			# Draw vertical subgrid lines
			for x in range(0, (NUM_BLOCKS_X*subdiv)+1):
				xc = x * WIDTH_BLOCK/subdiv + offset
				self.addLine(xc, 0, xc, height, QtGui.QPen(QtGui.QColor(50,50,50)) )
			# Draw horizontal grid lines
			for y in range(0, (NUM_BLOCKS_Y*subdiv)+1):
				yc = y * HEIGHT_BLOCK/subdiv
				self.addLine(0 + offset, yc, (width-padding) + offset, yc, QtGui.QPen(QtGui.QColor(50,50,50)) )
			#offset+=605

	def update_maze(self, maze, NUM_BLOCKS_X, NUM_BLOCKS_Y, WIDTH_BLOCK, HEIGHT_BLOCK):

		self.drawBaseGrid()
		offset = 0
		for layer in maze.grid:
			y = 0
			for row in layer:
				row.reverse()
				x = 0
				for cell in row:
					cell_item = CellItem(x*WIDTH_BLOCK+offset, y*HEIGHT_BLOCK, cell.name, cell.walls)
					cell_item.name = cell.name
					cell_item.start = cell.start
					cell_item.end = cell.end
					cell_item.roomtype = cell.roomtype
					cell_item.roomdir = cell.roomdir
					cell_item.pathmain = cell.pathmain
					cell_item.pathdir = cell.pathdir
					cell_item.keyroom = cell.keyroom
					cell_item.keydoor = cell.keydoor
					cell_item.switchroom = cell.switchroom
					cell_item.switchdoor = cell.switchdoor
					self.addItem(cell_item)
					# print('adding cell item with roomtype: {} / roomdir: {}'.format(cell.roomtype, cell.roomdir))
					if cell_item.keyroom:
						print('Key is at cell item {}'.format(cell_item.name))
					x+=1
				y+=1
			offset+=475
		self.update()

class CellItem(QtGui.QGraphicsItem):

	def __init__(self, x, y, name, walls=[]):
		QtGui.QGraphicsItem.__init__(self,)
		#self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)
		self.borderWidth = 6.0
		self.cellWidth = 512.0
		self.setPos(x,y)
		self.name = QtGui.QGraphicsTextItem(name, parent=self)
		self.walls = walls

		self.start = False
		self.end = False

		self.roomtype = None
		self.roomdir = None
		self.label = None
		self.pathmain = False
		self.pathdir = None

		self.keyroom = False
		self.keydoor = False
		self.switchroom = False
		self.switchdoor = False

		# Pixmaps
		#pixmap_room_0 = QtGui.QPixmap(TEMPLATEDIR + r'/0_512.png')
		self.room_0 = QtGui.QPixmap(random.choice(room_0_rooms))
		self.room_1 = QtGui.QPixmap(random.choice(room_1_rooms))
		self.room_2 = QtGui.QPixmap(random.choice(room_2_rooms))
		self.room_3 = QtGui.QPixmap(TEMPLATEDIR + r'/3_512.png')
		self.room_4 = QtGui.QPixmap(TEMPLATEDIR + r'/4_512.png')

		self.path_line = QtGui.QPixmap(ROOTDIR + r'/resources/path_arrow.png' )
		self.icon_key = QtGui.QPixmap(ROOTDIR + r'/resources/icon_key.png' )
		self.icon_keydoor = QtGui.QPixmap(ROOTDIR + r'/resources/icon_keydoor.png' )
		self.icon_switch = QtGui.QPixmap(ROOTDIR + r'/resources/icon_switch.png' )
		self.icon_switchdoor = QtGui.QPixmap(ROOTDIR + r'/resources/icon_switchdoor.png' )

	def boundingRect(self):
		penWidth = self.borderWidth
		return QtCore.QRectF(-75 - penWidth/2, -75 - penWidth/2,
				512 + penWidth, 512 + penWidth)

	def paint(self, painter, option, widget):

		penWidth = self.borderWidth
		cellWidth = self.cellWidth
		pen = QtGui.QPen(QtGui.QColor(1,1,1), penWidth)
		painter.setPen(pen)
		painter.drawRect(penWidth/2, penWidth/2 , cellWidth - penWidth, cellWidth - penWidth)
		fillOpening = QtGui.QColor(75,75,75)
		self.font = QtGui.QFont()
		self.font.setPointSize(24)
		self.dirFont = QtGui.QFont()
		self.dirFont.setPointSize(36)

		originx, originy = cellWidth/2, cellWidth/2

		# Draw room type 0 (dead end)
		if self.roomtype == 0:
			self.img = QtGui.QGraphicsPixmapItem(self.room_0, parent=self)
			self.img.setTransformOriginPoint(originx, originy)
			self.label = QtGui.QGraphicsTextItem('{} / 0 / {}'.format(self.name, self.roomdir), parent=self)
			self.label.setFont(self.font)
			self.label.setPos(originx-230,originy+-235)
			if self.roomdir == 'N':
				pass
			elif self.roomdir == 'S':
				self.img.setScale(-1)
			elif self.roomdir == 'E':
				self.img.setTransform(QtGui.QTransform().translate(originx, originy).rotate(90).translate(-originx, -originy))
			elif self.roomdir == 'W':
				self.img.setTransform(QtGui.QTransform().translate(originx, originy).rotate(-90).translate(-originx, -originy))

		# Draw room type 1 (hallway)
		if self.roomtype == 1:
			self.img = QtGui.QGraphicsPixmapItem(self.room_1, parent=self)
			self.img.setTransformOriginPoint(originx, originy)
			self.label = QtGui.QGraphicsTextItem('{} / 1 / {}'.format(self.name, self.roomdir), parent=self)
			self.label.setFont(self.font)
			self.label.setPos(originx - 230, originy + -235)
			if self.roomdir == 'N':
				pass
			if self.roomdir == 'E':
				self.img.setTransform(QtGui.QTransform().translate(originx, originy).rotate(90).translate(-originx, -originy))

		# Draw room type 2 (corner)
		if self.roomtype == 2:
			self.img = QtGui.QGraphicsPixmapItem(self.room_2, parent=self)
			self.img.setTransformOriginPoint(originx, originy)
			self.label = QtGui.QGraphicsTextItem('{} / 2 / {}'.format(self.name, self.roomdir), parent=self)
			self.label.setFont(self.font)
			self.label.setPos(originx - 230, originy + -235)
			if self.roomdir == 'N':
				pass
			elif self.roomdir == 'S':
				self.img.setTransform(QtGui.QTransform().translate(originx, originy).rotate(180).translate(-originx, -originy))
			elif self.roomdir == 'E':
				self.img.setTransform(QtGui.QTransform().translate(originx, originy).rotate(90).translate(-originx, -originy))
			elif self.roomdir == 'W':
				self.img.setTransform(QtGui.QTransform().translate(originx, originy).rotate(-90).translate(-originx, -originy))

		# Draw room type 3 (3-way junction)
		if self.roomtype == 3:
			self.img = QtGui.QGraphicsPixmapItem(self.room_3, parent=self)
			self.img.setTransformOriginPoint(originx, originy)
			self.label = QtGui.QGraphicsTextItem('{} / 3 / {}'.format(self.name, self.roomdir), parent=self)
			self.label.setFont(self.font)
			self.label.setPos(originx - 230, originy + -235)
			if self.roomdir == 'N':
				pass
			elif self.roomdir == 'S':
				self.img.setTransform(QtGui.QTransform().translate(originx, originy).rotate(180).translate(-originx, -originy))
			elif self.roomdir == 'E':
				self.img.setTransform(QtGui.QTransform().translate(originx, originy).rotate(90).translate(-originx, -originy))
			elif self.roomdir == 'W':
				self.img.setTransform(QtGui.QTransform().translate(originx, originy).rotate(-90).translate(-originx, -originy))

		# Draw room type 4 (4-way junction)
		if self.roomtype == 4:
			self.img = QtGui.QGraphicsPixmapItem(self.room_4, parent=self)
			self.img.setTransformOriginPoint(originx, originy)
			self.label = QtGui.QGraphicsTextItem('{} / 4 / {}'.format(self.name, self.roomdir), parent=self)
			self.label.setFont(self.font)
			self.label.setPos(originx - 230, originy + -235)

		# Draw room type 5 (4-way junction)
		if self.roomtype == 5:
			#self.img = QtGui.QGraphicsPixmapItem(pixmap_room_4, parent=self)
			#self.img.setTransformOriginPoint(originx, originy)
			#self.label = QtGui.QGraphicsTextItem('{} / 4 / {}'.format(self.name, self.roomdir), parent=self)
			#self.label.setFont(self.font)
			#self.label.setPos(originx - 230, originy + -235)
			#print('removed cell {}'.format(self.name))
			pass

		# Set start / end labels
		if self.start == True:
			painter.fillRect(penWidth/2, penWidth/2 , cellWidth - penWidth, cellWidth - penWidth, QtGui.QColor(125,125,150))
			self.font = QtGui.QFont()
			self.font.setPointSize(42)
			self.label = QtGui.QGraphicsTextItem('START', parent=self)
			self.label.setFont(self.font)
			self.label.setPos(cellWidth / 2 - 75, cellWidth / 3 - 50)
		if self.end == True:
			painter.fillRect(penWidth/2, penWidth/2 , cellWidth - penWidth, cellWidth - penWidth, QtGui.QColor(100,100,125))
			self.font = QtGui.QFont()
			self.font.setPointSize(42)
			self.label = QtGui.QGraphicsTextItem('END', parent=self)
			self.label.setFont(self.font)
			self.label.setPos(cellWidth/2-75, cellWidth/3-50)

		# Draw openings
		for wall in self.walls:
			if self.direction(wall['ni']) == 'T' or self.direction(wall['ni']) == 'B':
				if wall['broken'] == True:
					pen = QtGui.QPen(fillOpening, penWidth/2)
					pen.setStyle(QtCore.Qt.DotLine)
					painter.setPen(pen)
					painter.drawRect(penWidth/2 + cellWidth/3, penWidth/2 + cellWidth/3, cellWidth/3 - penWidth, cellWidth/3 - penWidth)
			if self.direction(wall['ni']) == 'S':
				if wall['broken'] == True:
					pen = QtGui.QPen(QtGui.QColor(75,75,75), penWidth/2)
					pen.setStyle(QtCore.Qt.SolidLine)
					painter.setPen(pen)
					painter.fillRect(penWidth/2 + cellWidth/3, penWidth + cellWidth-12, cellWidth/3 - penWidth, penWidth, fillOpening)
			if self.direction(wall['ni']) == 'N':
				if wall['broken'] == True:
					pen = QtGui.QPen(QtGui.QColor(75,75,75), penWidth/2)
					pen.setStyle(QtCore.Qt.SolidLine)
					painter.setPen(pen)
					painter.fillRect(penWidth/2 + cellWidth/3, 0, cellWidth/3 - penWidth, penWidth, fillOpening)
			if self.direction(wall['ni']) == 'E':
				if wall['broken'] == True:
					pen = QtGui.QPen(QtGui.QColor(75,75,75), penWidth/2)
					pen.setStyle(QtCore.Qt.SolidLine)
					painter.setPen(pen)
					painter.fillRect(cellWidth-penWidth, penWidth/2 + cellWidth/3, penWidth, cellWidth/3 - penWidth, fillOpening)
			if self.direction(wall['ni']) == 'W':
				if wall['broken'] == True:
					pen = QtGui.QPen(QtGui.QColor(75,75,75), penWidth/2)
					pen.setStyle(QtCore.Qt.SolidLine)
					painter.setPen(pen)
					painter.fillRect(0, penWidth/2 + cellWidth/3, penWidth, cellWidth/3 - penWidth, fillOpening)

		# Draw path arrows and icons
		if self.pathmain:
			self.path_label = QtGui.QGraphicsPixmapItem(self.path_line, parent=self)
			if self.pathdir == 'N':
				if self.keydoor:
					self.keydoor_label = QtGui.QGraphicsPixmapItem(self.icon_keydoor, parent=self)
					self.keydoor_label.setTransform(QtGui.QTransform().translate(originx - 25, originy - 250))
				if self.keyroom:
					self.keyroom_label = QtGui.QGraphicsPixmapItem(self.icon_key, parent=self)
					#self.keyroom_label.setTransform(QtGui.QTransform().translate(originx - 25, originy - 250))
				pass
			elif self.pathdir == 'E':
				self.path_label.setTransform(QtGui.QTransform().translate(originx, originy).rotate(90).translate(-originx, -originy))
				if self.keydoor:
					self.keydoor_label = QtGui.QGraphicsPixmapItem(self.icon_keydoor, parent=self)
					self.keydoor_label.setTransform(QtGui.QTransform().translate(originx + 200, originy - 25))
				if self.keyroom:
					self.keyroom_label = QtGui.QGraphicsPixmapItem(self.icon_key, parent=self)
					self.keyroom_label.setTransform(QtGui.QTransform().translate(originx + 200, originy - 25))
			elif self.pathdir == 'S':
				self.path_label.setTransform(QtGui.QTransform().translate(originx, originy).rotate(180).translate(-originx, -originy))
				if self.keydoor:
					self.keydoor_label = QtGui.QGraphicsPixmapItem(self.icon_keydoor, parent=self)
					self.keydoor_label.setTransform(QtGui.QTransform().translate(originx - 25, originy + 200))
				if self.keyroom:
					self.keyroom_label = QtGui.QGraphicsPixmapItem(self.icon_key, parent=self)
					#self.keyroom_label.setTransform(QtGui.QTransform().translate(originx - 25, originy + 200))
			elif self.pathdir == 'W':
				self.path_label.setTransform(QtGui.QTransform().translate(originx, originy).rotate(-90).translate(-originx, -originy))
				if self.keydoor:
					self.keydoor_label = QtGui.QGraphicsPixmapItem(self.icon_keydoor, parent=self)
					self.keydoor_label.setTransform(QtGui.QTransform().translate(originx - 250, originy - 25))
				if self.keyroom:
					self.keyroom_label = QtGui.QGraphicsPixmapItem(self.icon_key, parent=self)
					#self.keyroom_label.setTransform(QtGui.QTransform().translate(originx - 250, originy - 25))
		if self.keyroom:
			self.keyroom_label = QtGui.QGraphicsPixmapItem(self.icon_key, parent=self)
			self.keyroom_label.setTransform(QtGui.QTransform().translate(originx, originy))









	def direction(self,ni):
		if ni == 0:
			return 'N'
		elif ni == 1:
			return 'S'
		elif ni == 2:
			return 'W'
		elif ni == 3:
			return 'E'
		elif ni == 4:
			return 'T'
		elif ni == 5:
			return 'B'

def main():

	app = QtGui.QApplication(sys.argv)
	viewer = MazeViewer()
	viewer.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
    main()

sys.exit(app.exec_())