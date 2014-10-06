'''
Tri Peaks is a solitaire card game that is played with a 52-card standard deck.
The object is to clear 3 peaks made up of cards.
Over 90% of all the games dealt are completely solvable.

Rules:

1. Construction and layout.

The game starts with 18 dealt face-down on the tableau to form 3 pyramids
with 3 overlapping tiers each. Over these 3 pyramids are 10 face-up cards.
The arrangement is illustrated as follows:

     O     O     O
    O O   O O   O O
   O O O O O O O O O
  A A A A A A A A A A

The "O"s are the face-down cards and the "A"s are the face-up cards.
The 24 remaining cards make up the stock.

2. Building during play.

The first card from the stock is put in the waste pile. For a card in the
tableau to be moved to the waste pile, it must be a rank higher or lower
regardless of suit. This card becomes the new top card and the process is
repeated several times (e.g. 7-8-9-10-9-10-J, etc.) until the sequence stops.
Along the way, any face-down cards that are no longer overlapping are turned up.

3. Moves.

In case the sequence is stopped, i.e. no card on the tableau can be put over the
top card of the waste pile, a card is placed on the waste pile from the stock to
see if it can start a new sequence. Cards are transferred from the stock to the
waste pile one at a time as long as it does not begin a new sequence with the
cards on the tableau.

4. Victory.

The game is won if all three peaks are cleared.

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
RANK_NUM = len(RANKS)

# Cards
# Card_Index is defined as:
# suit + rank * SUIT_NUM
CARDS = [r + s for r in RANKS for s in SUITS]
CARD_NUM = SUIT_NUM * RANK_NUM

# form peaks as rows of cards
# pile_0   O . . O . . O
#          |\    |\    |\
# pile_1   O O . O O . O O
#          |\|\  |\|\  |\|\
# pile_2   O O O O O O O O O
#          |\|\|\|\|\|\|\|\|\
# pile_3   A A A A A A A A A A

PILE_NUM = 4    # rows that form peaks
DESK_SIZE = PILE_NUM + 1 # + stock pile

STOCK_SIZE = 24
STOCK_POS = 4

DESK_RANGE = range(DESK_SIZE)
PILE_RANGE = [3, 6, 9, 10, STOCK_SIZE]

EMPTY_CELL = -1

def new_desk():
  return [[] for x in DESK_RANGE]

def clone(desk):
  return [pile[:] for pile in desk]

def reset(desk):
  for pile in desk:
    del pile[:]

def split_peaks(desk):
  ''' inserts empty cells to make the peaks '''
  desk[0].insert(2, EMPTY_CELL)
  desk[0].insert(2, EMPTY_CELL)
  desk[0].insert(1, EMPTY_CELL)
  desk[0].insert(1, EMPTY_CELL)
  
  desk[1].insert(4, EMPTY_CELL)
  desk[1].insert(2, EMPTY_CELL)

def is_empty(desk):
  for c in desk[0]:
    if c != EMPTY_CELL:
      return False
  return True

def deal(desk, cascades):
  reset(desk)
  for src, dst in zip(cascades, desk):
    for i in range(0, len(src), 2):
      dst.append(CARDS.index(src[i:i+2]))
  split_peaks(desk)

def deal_by_number(desk, n):
  reset(desk)
  # use LCG algorithm to pick up cards from the deck
  # http://en.wikipedia.org/wiki/Linear_congruential_generator
  m = 2**31
  a = 1103515245
  c = 12345
  cards = range(CARD_NUM)
  for i in DESK_RANGE:
    while len(desk[i]) < PILE_RANGE[i]:
      n = (a * n + c) % m
      desk[i].append(cards.pop(n % len(cards)))
  split_peaks(desk)

def desk_to_str(desk):
  return ''.join(str(pile) for pile in desk)

# MOVE is defined as:
# move = stock_index + STOCK_SIZE * (src_pile + PILE_NUM * src_pile_index)

def move_card(desk, move):
  src = move // STOCK_SIZE
  dst = move  % STOCK_SIZE
  
  src_pile       = src // PILE_NUM
  src_pile_index = src  % PILE_NUM
  
  desk[STOCK_POS].insert(dst, desk[src_pile][src_pile_index])
  desk[src_pile][src_pile_index] = EMPTY_CELL

def move_cards(desk, moves):
  for move in moves:
    src = move // STOCK_SIZE
    dst = move  % STOCK_SIZE
    
    src_pile       = src // PILE_NUM
    src_pile_index = src  % PILE_NUM
      
    desk[STOCK_POS].insert(dst, desk[src_pile][src_pile_index])
    desk[src_pile][src_pile_index] = EMPTY_CELL

def move_cards_reverse(desk, moves):
  for move in moves[::-1]:
    dst = move // STOCK_SIZE
    src = move  % STOCK_SIZE
  
    dst_pile       = dst // PILE_NUM
    dst_pile_index = dst  % PILE_NUM
  
    desk[dst_pile][dst_pile_index] = desk[STOCK_POS][src]
    del desk[STOCK_POS][src]

def is_card_playable(desk, pile, index):
  card = desk[pile][index]
  if card == EMPTY_CELL:
    return False
  if pile + 1 == PILE_NUM:
    return True
  else:
    return (desk[pile + 1][index    ] == EMPTY_CELL and
            desk[pile + 1][index + 1] == EMPTY_CELL)

def get_moves(desk, stock_index):
  moves = []
  
  stock_card = desk[STOCK_POS][stock_index]
  stock_suit = stock_card  % SUIT_NUM
  stock_rank = stock_card // SUIT_NUM
  
  for p in range(PILE_NUM):
    for i in range(len(desk[i])):
      if is_card_playable(desk, p, i):
        card = desk[p][i]
        suit = card  % SUIT_NUM
        rank = card // SUIT_NUM
        
        if abs(stock_rank - rank) == 1:
          moves.append(stock_index + STOCK_SIZE * (p + PILE_NUM * i))
  return moves

def test_moves(desk, stock_index, src_moves, src_done, solution):
  dst_moves = []
  dst_done = src_done
    
  for moves in src_moves:
    move_cards(desk, moves)

    if solution == None or len(moves) < len(solution):
      if is_empty(desk):
        if _debug:
          print "Found %d moves solution" % len(moves)
        solution = moves
      else:
        desk_key = desk_to_str(desk)
        if desk_key not in dst_done:
          dst_done.add(desk_key)

          for move in get_moves(desk):
            new_moves = moves[:]
            new_moves.append(move)
            
            dst_moves.append(new_moves)
      
    move_cards_reverse(desk, moves) # restore our desk

  return solution, dst_moves, dst_done

def get_solution(desk):
  src_moves = [[move] for move in get_moves(desk)]
  src_done = set()
  
  solution = None
  
  while True:
    while src_moves:
      if _debug:
        print len(src_moves)

      solution, src_moves, src_done = test_moves(desk, src_moves, src_done, solution)
    
    if solution:
      break
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
