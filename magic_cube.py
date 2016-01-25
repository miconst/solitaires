import random
import itertools

# Directions
UP    = 0
RIGHT = 1
DOWN  = 2
LEFT  = 3
NUM_OF_DIRECTIONS = 4

def rotate(direction, rotate_to):
	return (direction + rotate_to) % NUM_OF_DIRECTIONS

assert(rotate(UP, RIGHT) == RIGHT)
assert(rotate(RIGHT, RIGHT) == DOWN)
assert(rotate(DOWN, LEFT) == RIGHT)
assert(rotate(LEFT, DOWN) == RIGHT)
assert(rotate(RIGHT, DOWN) == LEFT)
assert(rotate(DOWN, RIGHT) == LEFT)

class Cell:
	def __init__(self, color):
		self.color = color

class CornerCell(Cell):
	pass

class EdgeCell(Cell):
	pass
	
class Face:
	def __init__(self, color):
		self.color = color
		self.edges = [EdgeCell(color) for i in range(NUM_OF_DIRECTIONS)]
		self.corners = [CornerCell(color) for i in range(NUM_OF_DIRECTIONS)]
		self.neighbours = [None for i in range(NUM_OF_DIRECTIONS)]

	def rotate(self, clockwise):
		ring = []
		for f in self.neighbours:
			d = f.getDirection(self)
			ring.append((
				f.corners[rotate(d, LEFT)],
				f.edges[d],
				f.corners[d]
			))

		if clockwise:
			ring.insert(0, ring.pop(-1))
			self.edges.insert(0, self.edges.pop(-1))
			self.corners.insert(0, self.corners.pop(-1))
		else:
			ring.append(ring.pop(0))
			self.edges.append(self.edges.pop(0))
			self.corners.append(self.corners.pop(0))

		for i in range(NUM_OF_DIRECTIONS):
			f = self.neighbours[i]
			d = f.getDirection(self)
			f.corners[rotate(d, LEFT)] = ring[i][0]
			f.edges[d] = ring[i][1]
			f.corners[d] = ring[i][2]

	def getDirection(self, neighbour):
		return self.neighbours.index(neighbour)

	def isSolved(self):
		for e in self.edges:
			if e.color != self.color:
				return False
		for c in self.corners:
			if c.color != self.color:
				return False
		return True

	def getKey(self, key):
		#~ key |= (self.color + 1)
		#~ key <<= 3
		for e in self.edges:
			key |= (e.color + 1)
			key <<= 3
		for c in self.corners:
			key |= (c.color + 1)
			key <<= 3
		return key

# cube sides
F = 0  # Front
B = 1  # Back
U = 2  # Up (top)
D = 3  # Down (bottom)
L = 4  # Left
R = 5  # Right
FACE_NUM = 6

cube = [Face(color) for color in range(FACE_NUM)]

def isSolved(cube):
	for f in cube:
		if not f.isSolved():
			return False
	return True

def getKey(cube):
	#~ keys = set()
	#~ for mask in itertools.permutations(range(1, FACE_NUM + 1)):
	key = 0
	for f in cube:
		key = f.getKey(key)

	# normalize
	mask = []
	key_norm = 0
	while key:
		n = (key & 7)
		key >>= 3
		if n not in mask:
			mask.append(n)
		key_norm |= (mask.index(n) + 1)
		key_norm <<= 3
		#~ keys.add(k)
	#~ assert(len(keys) == 720)	# 6!
	return key_norm

MOVES = [
	(F, True), (F, False),
	(B, True), (B, False),
	(U, True), (U, False),
	(D, True), (D, False),
	(L, True), (L, False),
	(R, True), (R, False)]

done = set()

def nextMove(cube, moves):
	solution = None
	next_moves = []
	for m in MOVES:
		cube[m[0]].rotate(m[1])
		key = getKey(cube)
		if key not in done:
			done.add(key)
			n = moves[:]
			n.append(m)
			next_moves.append(n)
			if isSolved(cube):
				solution = n
		cube[m[0]].rotate(not m[1])  # restore
	return solution, next_moves

def solve(cube):
	key = getKey(cube)
	solution, next_moves = nextMove(cube, [])
	while not solution:
		print len(next_moves[0]), len(next_moves), len(done)
		accum = []
		for moves in next_moves:
			for m in moves:
				cube[m[0]].rotate(m[1])

			s, n = nextMove(cube, moves)
			accum += n
			if s:
				solution = s

			for m in moves[::-1]:	#restore
				cube[m[0]].rotate(not m[1])

			assert(key == getKey(cube))
		next_moves = accum
	return solution

# connect faces
cube[F].neighbours = [cube[U], cube[R], cube[D], cube[L]]
cube[B].neighbours = [cube[L], cube[D], cube[R], cube[U]]
cube[U].neighbours = [cube[F], cube[L], cube[B], cube[R]]
cube[D].neighbours = [cube[R], cube[B], cube[L], cube[F]]
cube[L].neighbours = [cube[B], cube[U], cube[F], cube[D]]
cube[R].neighbours = [cube[D], cube[F], cube[U], cube[B]]

def print_cube(c):
	for f in c:
		print f.corners[LEFT].color, ',', f.edges[UP].color, ',', f.corners[UP].color
		print f.edges[LEFT].color, ',', f.color, ',', f.edges[RIGHT].color
		print f.corners[DOWN].color, ',', f.edges[DOWN].color, ',', f.corners[RIGHT].color
		print "----"
		
print_cube(cube)
print(isSolved(cube), getKey(cube))

moves = []
for x in range(17):
	face = random.randint(0, FACE_NUM - 1)
	clockwise = (random.randint(0, 1) > 0)
	cube[face].rotate(clockwise)

	if isSolved(cube):
		print "APOJ!"

	moves.insert(0, (face, not clockwise))
	
print "+"*8
print_cube(cube)
print(isSolved(cube), getKey(cube))
print(solve(cube))

for m in moves:
	cube[m[0]].rotate(m[1])
print(isSolved(cube), getKey(cube))

print "+"*8
print_cube(cube)

#~ cube[L].rotate(True)
#~ print "+"*8
#~ print_cube(cube)
#~ 
#~ cube[R].rotate(False)
#~ print "+"*8
#~ print_cube(cube)
#~ 
#~ cube[F].rotate(False)
#~ print "+"*8
#~ print_cube(cube)

layout = [
  [U, R, D, L],  # Front
  [L, D, R, U],  # Back
  [F, L, B, R],  # Up
  [R, B, L, F],  # Down
  [B, U, F, D],  # Left
  [D, F, U, B],  # Right
]

#~ print layout

def RotateFace(face_name, clockwise=True):
	order = layout[face_name][:]
	print order
	cells = []

	for d in range(NUM_OF_DIRECTIONS):
		face = cube[order[d]]
		cells.append((
			face.corners[rotate(d, RIGHT)],
			face.edges[rotate(d, DOWN)],
			face.corners[rotate(d, DOWN)]
		))
		
	if clockwise:
		order.append(order.pop(0))
	else:
		order.insert(0, order.pop(-1))

	for d in range(NUM_OF_DIRECTIONS):
		face = cube[order[d]]
		face.corners[rotate(d, RIGHT)] = cells[d][0]
		face.edges[rotate(d, DOWN)]    = cells[d][1]
		face.corners[rotate(d, DOWN)]  = cells[d][2]


#~ print "!"
#~ RotateFace(F)
#~ print_cube(cube)
#~ print "!"
#~ RotateFace(F)
#~ print_cube(cube)
#~ print "!"
#~ RotateFace(F)
#~ print_cube(cube)
#~ print "!"
#~ RotateFace(F)
#~ print_cube(cube)


ROW_NUM = 3
COL_NUM = 3

SIDE_NUM = ROW_NUM * COL_NUM  # Number of elements in one side

cube = []
for color in range(FACE_NUM):
	cube += [color] * SIDE_NUM
print cube

def get_cube_side(cube, side_name):
	start = side_name * SIDE_NUM
	return cube[start: start + SIDE_NUM]

#~ print get_cube_side(cube, B)
#~ print get_cube_side(cube, L)
#~ print get_cube_side(cube, R)

def rotate(cube, side_name, clockwise=True):
	pattern = (6,3,0,
	           7,4,1,
	           8,5,2)
	side = get_cube_side(cube, side_name)
	start = side_name * SIDE_NUM

	# rotate the side
	for i in range(SIDE_NUM):
		cube[start + i] = side[pattern[i if clockwise else -1 - i]]

	# and its neighbours
	neighbours = layout[side_name]
	#~ 
	

#~ rotate(cube, F)
#~ rotate(cube, R, False)

#~ print cube

