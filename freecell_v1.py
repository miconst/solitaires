'''
FreeCell is a solitaire-based card game played with a 52-card standard deck.
Nearly all deals can be solved.

Rules:

1. Construction and layout.

One standard 52-card deck is used.
There are 4 open cells and 4 open bases.
Cards are dealt into 8 cascades.

2. Building during play.

The top card of each cascade begins a tableau.
Tableaux must be built down by alternating colors.
Bases are built up by suit.

3. Moves.

Any cell card or top card of any cascade may be moved to build on a tableau,
or moved to an empty cell, an empty cascade, or its base.

4. Victory.

The game is won after all cards are moved to their base piles.

'''

_debug = __name__ == '__main__'

if _debug:
  import time
  job_time = time.clock()

# Suits
SUITS = 'SDCH'
SUIT_NUM = 4
SPADES, DIAMONDS, CLUBS, HEARTS = range(SUIT_NUM)

# Ranks
RANKS = 'A23456789TJQK'
RANK_NUM = 13

# Cards
# Card_Index is defined as:
# suit + rank * SUIT_NUM
CARDS = [r + s for r in RANKS for s in SUITS]
CARD_NUM = SUIT_NUM * RANK_NUM

PILE_NUM = 8    # cascades
CELL_NUM = 4    # open cells
BASE_NUM = 4    # foundation piles
DESK_SIZE = PILE_NUM + CELL_NUM + BASE_NUM

PILE_START = 0
PILE_END = PILE_START + PILE_NUM

CELL_START = PILE_END
CELL_END = CELL_START + CELL_NUM

BASE_START = CELL_END
BASE_END = BASE_START + BASE_NUM

PILE_RANGE = range(PILE_START, PILE_END)
CELL_RANGE = range(CELL_START, CELL_END)
BASE_RANGE = range(BASE_START, BASE_END)
PLAY_RANGE = range(PILE_START, CELL_END)
DESK_RANGE = range(DESK_SIZE)

def new_desk():
  return [[] for x in DESK_RANGE]

def clone(desk):
  return [pile[:] for pile in desk]

def reset(desk):
  for pile in desk:
    del pile[:]

def deal(desk, cascades):
  reset(desk)
  for src, dst in zip(cascades, desk):
    for i in range(0, len(src), 2):
      dst.append(CARDS.index(src[i:i+2]))

def deal_by_number(desk, n):
  reset(desk)
  # use LCG algorithm to pick up cards from the deck
  # http://en.wikipedia.org/wiki/Linear_congruential_generator
  m = 2**31
  a = 1103515245
  c = 12345
  cards = range(CARD_NUM)
  while cards:
    for i in PILE_RANGE:
      if not cards:
        break
      else:
        n = (a * n + c) % m
        desk[i].append(cards.pop(n % len(cards)))

def desk_to_str(desk):
  # sort cascades and cells
  d = sorted(desk[PILE_START:PILE_END]) + sorted(desk[CELL_START:CELL_END]) + desk[BASE_START:BASE_END]
  return ''.join(str(pile) for pile in d)

def get_empty_pile(desk):
  for i in PILE_RANGE:
    if not desk[i]:
      return i

def get_empty_cell(desk):
  for i in CELL_RANGE:
    if not desk[i]:
      return i

def get_base_key(desk):
  s = len(desk[BASE_START +   SPADES])
  d = len(desk[BASE_START + DIAMONDS])
  c = len(desk[BASE_START +    CLUBS])
  h = len(desk[BASE_START +   HEARTS])
  return ((s * RANK_NUM + d) * RANK_NUM + c) * RANK_NUM + h

def get_pile_key(desk):
  keys = [str(desk[i]) for i in PILE_RANGE]
  keys.sort()
  return "".join(keys)

def count_empty_cells(desk):
  n = 0
  for i in PLAY_RANGE:
    if not desk[i]:
      n += 1
  return n

def count_base_cards(desk):
  n = 0
  for i in BASE_RANGE:
    n += len(desk[i])
  return n

def is_empty(desk):
  for i in PLAY_RANGE:
    if desk[i]:
      return False
  return True

# MOVE is defined as:
# move = source_pile_index * DESK_SIZE + destination_pile_index

def move_card(desk, move):
  src = move // DESK_SIZE
  dst = move  % DESK_SIZE
  desk[dst].append(desk[src].pop(-1))

def move_cards(desk, moves):
  for move in moves:
    src = move // DESK_SIZE
    dst = move  % DESK_SIZE
    desk[dst].append(desk[src].pop(-1))

def move_cards_reverse(desk, moves):
  for move in moves[::-1]:
    dst = move // DESK_SIZE
    src = move  % DESK_SIZE
    desk[dst].append(desk[src].pop(-1))

def auto_move_to_bases(desk, moves):
  ok = True
  while ok:
    ok = False
    for i in PLAY_RANGE:
      if desk[i]:
        card = desk[i][-1]
        suit = card  % SUIT_NUM
        rank = card // SUIT_NUM

        ro = len(desk[BASE_START + suit])
        if suit == SPADES or suit == CLUBS:
          rx = len(desk[BASE_START + DIAMONDS])
          ry = len(desk[BASE_START +   HEARTS])
        else:
          rx = len(desk[BASE_START +   SPADES])
          ry = len(desk[BASE_START +    CLUBS])
        
        if rank == ro and rank < rx + 2 and rank < ry + 2:
          ok = True
          # move it to the base
          moves.append(i * DESK_SIZE + BASE_START + suit)
          desk[BASE_START + suit].append(desk[i].pop(-1))

def get_moves(desk):
  moves = []
  empty_pile = get_empty_pile(desk)
  empty_cell = get_empty_cell(desk)
  
  for i in PLAY_RANGE:
    l = len(desk[i])
    if l > 0:
      card = desk[i][-1]
      suit = card  % SUIT_NUM
      rank = card // SUIT_NUM
      # 1. move to foundation
      if len(desk[BASE_START + suit]) == rank:
        moves.append(i * DESK_SIZE + BASE_START + suit)
      # 2. move to tableau
      suit_clr = (suit == DIAMONDS or suit == HEARTS)
      for j in PILE_RANGE:
        if desk[j]:
          c = desk[j][-1]
          s = c  % SUIT_NUM
          r = c // SUIT_NUM
          s_clr = (s == DIAMONDS or s == HEARTS)
          # Tableau should be built down in alternating colors.
          if r == rank + 1 and s_clr != suit_clr:
            moves.append(i * DESK_SIZE + j)
      # 3. move to an empty space
      if l > 1:
        if empty_cell != None: moves.append(i * DESK_SIZE + empty_cell)
        if empty_pile != None: moves.append(i * DESK_SIZE + empty_pile)
  return moves

def get_progress(desk):
  n = 0
  for i in PILE_RANGE:
    pile = desk[i]
    for a in range(len(pile) - 1):
      rank_a = pile[a] // SUIT_NUM
      for b in range(a + 1, len(pile)):
        rank_b = pile[b] // SUIT_NUM
        if rank_a < rank_b:
          n = n + (rank_b - rank_a)
  return n

def add_to_set_at(src, i, j):
  if i not in src:
    src[i] = set()
  src[i].add(j)

def split(desk, moves, threshold):
  strategy = {}
  
  for i, m in enumerate(moves):
    move_cards(desk, m)
    auto_move_to_bases(desk, m)
    
    n_1 = count_empty_cells(desk)
    n_2 = get_progress(desk)
    
    add_to_set_at(strategy, n_1 - n_2, i)

    move_cards_reverse(desk, m)
  
  keys = strategy.keys()
  keys.sort()
  mask_a = strategy.pop(keys.pop(-1))
   
  while len(mask_a) < threshold:
    mask_a |= strategy.pop(keys.pop(-1))
  
  mask_b = set(xrange(len(moves))) - mask_a
  return [moves[i] for i in mask_a], [moves[i] for i in mask_b]

def test_moves(desk, src_moves, src_done, solution):
  dst_moves = []
  dst_done = {}
    
  for moves in src_moves:
    move_cards(desk, moves)
    auto_move_to_bases(desk, moves)
      
    if solution == None or len(moves) < len(solution):
      if is_empty(desk):
        if _debug:
          print "Found %d moves solution" % len(moves)
        solution = moves
      else:
        base_key = get_base_key(desk)
        if base_key not in dst_done:
          if base_key in src_done:
            dst_done[base_key] = src_done[base_key]
          else:
            dst_done[base_key] = set()
      
        pile_key = get_pile_key(desk)
        if pile_key not in dst_done[base_key]:
          dst_done[base_key].add(pile_key)

          for move in get_moves(desk):
            new_moves = moves[:]
            new_moves.append(move)
            
            dst_moves.append(new_moves)
      
    move_cards_reverse(desk, moves) # restore our desk

  return solution, dst_moves, dst_done

DESK_NUM_MAX = 8000
DESK_NUM_MIN = 2000

def get_solution(desk):
  src_moves = [[move] for move in get_moves(desk)]
  src_done = {}
  
  reserve = []
  
  solution = None
  
  while True:
    while src_moves:
      if _debug:
        print len(src_moves)
      if len(src_moves) > DESK_NUM_MAX:
        if _debug:
          print "Splitting..."
        a, b = split(desk, src_moves, DESK_NUM_MIN)
        reserve.append((b, src_done))
        src_moves = a
        if _debug:
          print "Split #%d -> %d+%d" % (len(reserve), len(a), len(b))

      solution, src_moves, src_done = test_moves(desk, src_moves, src_done, solution)
    
    if solution or not reserve:
      break
    else:
      if _debug:
        print "Step back to %d split" % len(reserve)
      src_moves, src_done = reserve.pop(-1)
  return solution

if _debug:
  x = new_desk()

  #~ deal(x, (s.rstrip().upper() for s in file("deal_001.txt")))
  for i in PILE_RANGE:
    deal_by_number(x, i)
    print(desk_to_str(x))

  moves = get_solution(x)

  print "o" + "-=" * 25
  print "| Total: %d playfield moves" % (len(moves) - CARD_NUM)
  print "o" + "-=" * 25

  for i, move in enumerate(moves):
    a = move // DESK_SIZE
    b = move  % DESK_SIZE
    card = CARDS[x[a][-1]]
    dest = "BASE"
    if CELL_START <= b < CELL_END:
      dest = "cell"
    elif PILE_START <= b < PILE_END:
      if x[b]:
        dest = CARDS[x[b][-1]]
      else:
        dest = "pile"

    print "%d: %s -> %s" % (i + 1, card, dest)
    move_card(x, move)  

  job_time = int(time.clock() - job_time)
  print "Job has taken %d min %d sec." % (job_time // 60, job_time % 60)
