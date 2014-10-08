"""
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

"""

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
# |\    |\    |\
# pile_1   O O . O O . O O
# |\|\  |\|\  |\|\
# pile_2   O O O O O O O O O
# |\|\|\|\|\|\|\|\|\
# pile_3   A A A A A A A A A A

PILE_NUM = 4  # rows that form peaks
DESK_SIZE = PILE_NUM + 1  # peaks + a stock pile

STOCK_SIZE = 24
STOCK_POS = PILE_NUM

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


def make_peaks(desk):
    """ inserts empty cells to make the peaks """
    desk[0].insert(2, EMPTY_CELL)
    desk[0].insert(2, EMPTY_CELL)
    desk[0].insert(1, EMPTY_CELL)
    desk[0].insert(1, EMPTY_CELL)

    desk[1].insert(4, EMPTY_CELL)
    desk[1].insert(2, EMPTY_CELL)

    desk[STOCK_POS].insert(-1, EMPTY_CELL)  # stock pointer


def is_empty(desk):
    for c in desk[0]:
        if c != EMPTY_CELL:
            return False
    return True


def deal(desk, cascades):
    reset(desk)
    for src, dst in zip(cascades, desk):
        for i in range(0, len(src), 2):
            dst.append(CARDS.index(src[i:i + 2]))
    make_peaks(desk)


def deal_by_number(desk, n):
    reset(desk)
    # use LCG algorithm to pick up cards from the deck
    # http://en.wikipedia.org/wiki/Linear_congruential_generator
    m = 2 ** 31
    a = 1103515245
    c = 12345
    cards = range(CARD_NUM)
    for i in DESK_RANGE:
        while len(desk[i]) < PILE_RANGE[i]:
            n = (a * n + c) % m
            desk[i].append(cards.pop(n % len(cards)))
    make_peaks(desk)


def desk_to_str(desk):
    return ''.join(str(pile) for pile in desk)


def stock_to_str(desk):
    d = desk[STOCK_POS]
    return str(d[d.index(EMPTY_CELL) + 1:])


# MOVE is defined as:
# move = src_pile + DESK_SIZE * src_index

def move_card(desk, move):
    src_index = move // DESK_SIZE
    src_pile = move % DESK_SIZE

    s = desk[STOCK_POS]

    if src_pile == STOCK_POS:
        # move stock pointer to the left
        assert (s.index(EMPTY_CELL) == src_index + 1)
        s[src_index], s[src_index + 1] = s[src_index + 1], s[src_index]
    else:
        # move the card into the stock behind the stock pointer
        dst = s.index(EMPTY_CELL) + 1
        s.insert(dst, desk[src_pile][src_index])
        desk[src_pile][src_index] = EMPTY_CELL


def move_cards(desk, moves):
    s = desk[STOCK_POS]
    for move in moves:
        src_index = move // DESK_SIZE
        src_pile = move % DESK_SIZE

        if src_pile == STOCK_POS:
            # move stock pointer to the left
            assert (s.index(EMPTY_CELL) == src_index + 1)
            s[src_index], s[src_index + 1] = s[src_index + 1], s[src_index]
        else:
            # move the card into the stock behind the stock pointer
            dst = s.index(EMPTY_CELL) + 1
            s.insert(dst, desk[src_pile][src_index])
            desk[src_pile][src_index] = EMPTY_CELL


def move_cards_reverse(desk, moves):
    s = desk[STOCK_POS]
    for move in moves[::-1]:
        dst_index = move // DESK_SIZE
        dst_pile = move % DESK_SIZE

        if dst_pile == STOCK_POS:
            # move the stock pointer to the right
            assert (s.index(EMPTY_CELL) == dst_index)
            s[dst_index], s[dst_index + 1] = s[dst_index + 1], s[dst_index]
        else:
            # move the card behind the stock pointer into the peaks
            src = s.index(EMPTY_CELL) + 1
            desk[dst_pile][dst_index] = s.pop(src)


def is_card_playable(desk, pile, index):
    card = desk[pile][index]
    if card == EMPTY_CELL:
        return False
    if pile + 1 == PILE_NUM:
        return True
    else:
        return (desk[pile + 1][index] == EMPTY_CELL and
                desk[pile + 1][index + 1] == EMPTY_CELL)


def get_moves(desk):
    moves = []

    stock_index = desk[STOCK_POS].index(EMPTY_CELL) + 1
    stock_card = desk[STOCK_POS][stock_index]
    stock_suit = stock_card % SUIT_NUM
    stock_rank = stock_card // SUIT_NUM

    # get the next card from the stock, if there's any left
    if stock_index > 1:
        moves.append(STOCK_POS + DESK_SIZE * (stock_index - 2))

    for p in range(PILE_NUM):
        for i in range(len(desk[p])):
            if is_card_playable(desk, p, i):
                card = desk[p][i]
                suit = card % SUIT_NUM
                rank = card // SUIT_NUM

                x = abs(stock_rank - rank)
                if x == 1 or x + 1 == RANK_NUM:
                    moves.append(p + DESK_SIZE * i)
    return moves


def test_moves(desk, src_moves, solution):
    dst_moves = []
#    dst_done = src_done

    for moves in src_moves:
        move_cards(desk, moves)

        if solution == None or len(moves) < len(solution):
            if is_empty(desk):
                if _debug:
                    print "Found %d moves solution" % len(moves)
                solution = moves
            else:
#                desk_key = stock_to_str(desk)
#                if desk_key not in dst_done:
#                    dst_done.add(desk_key)

                    for move in get_moves(desk):
                        new_moves = moves[:]
                        new_moves.append(move)

                        dst_moves.append(new_moves)
#                else:
#                    print "apoj"

        move_cards_reverse(desk, moves)  # restore our desk

    return solution, dst_moves  #, dst_done


DESK_NUM_MAX = 10000
DESK_NUM_MIN = 1000


def add_to_set_at(src, i, j):
    if i not in src:
        src[i] = set()
    src[i].add(j)


def split(desk, moves, threshold):
    strategy = {}

    for i, m in enumerate(moves):
        move_cards(desk, m)

        # the less cards from the stock is used the better
        n = desk[STOCK_POS].index(EMPTY_CELL)
        add_to_set_at(strategy, n, i)

        move_cards_reverse(desk, m)

    keys = strategy.keys()
    keys.sort()

    mask_a = strategy.pop(keys.pop())
    while len(mask_a) < threshold:
        mask_a |= strategy.pop(keys.pop())

    mask_b = set(xrange(len(moves))) - mask_a
    return [moves[i] for i in mask_a], [moves[i] for i in mask_b]


def get_solution(desk):
    """

    :param desk:
    :return solution:
    """
    src_moves = [[move] for move in get_moves(desk)]
    #src_done = set()

    reserve = []

    solution = None

    while True:
        while src_moves:
            if _debug:
                print len(src_moves)
            if len(src_moves) > DESK_NUM_MAX:
                if _debug:
#                    print "done: ", len(src_done)
                    print "Splitting..."

                a, b = split(desk, src_moves, DESK_NUM_MIN)
                reserve.append(b)
                src_moves = a
                if _debug:
                    print "Split #%d -> %d+%d" % (len(reserve), len(a), len(b))
                    move_cards(desk, a[0])
                    print(desk_to_str(desk))
                    print stock_to_str(desk)
                    move_cards_reverse(desk, a[0])

            solution, src_moves = test_moves(desk, src_moves, solution)

        if solution or not reserve:
            break
        else:
            if _debug:
                print "Step back to %d split" % len(reserve)
            src_moves = reserve.pop()
    return solution


if _debug:
    x = new_desk()

    # ~ deal(x, (s.rstrip().upper() for s in file("deal_001.txt")))
    deal_by_number(x, 22)
    deal(x, ("2C2H7C", "2D3SQS8H2S5H", "TD3D5STC8SAHTHTS4S", "3C4H6D8D8CAC9SKSAD9D",
             "KH9HJC6C9C6S3HKD4D5DQCJDJS7DQH5C7S7HJHKCQD4CAS6H"))
    deal(x, ("5CKD9D", "TD2CTH8H6D9S", "4CKHAHACQH4D8CTS3H", "6H2SQCADJSKS7CJCTC5D",
             "4S3D9H6S2DJH4H5SJD8SQS3CQD7D9C3SAS7SKC2H8D7H5H6C"))
    deal(x, ("AC4HQS", "9CJC7D9H5HJH", "KHKC2C8C4SAD3HTS2S", "6C9S3SQDTH7C4D4CAH8H",
             "JD6D7HTDJS5DKD6HQH9DASTC8S6S5C5S2H8D3D7SKS2DQC3C"))

    print(desk_to_str(x))

    moves = get_solution(x)

    print "o" + "-=" * 25
    print "| Total: %d moves" % (len(moves))
    print "o" + "-=" * 25

    for i, move in enumerate(moves):
        index = move // DESK_SIZE
        pile = move % DESK_SIZE
        card = CARDS[x[pile][index]]
        dest = "stock" if pile == STOCK_POS else "peak"

        print "%d: %s -> %s" % (i + 1, card, dest)
        move_card(x, move)

    print desk_to_str(x)

    job_time = int(time.clock() - job_time)
    print "Job has taken %d min %d sec." % (job_time // 60, job_time % 60)
