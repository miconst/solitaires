_debug = not _NDEBUG

if _debug then
  job_time = os.time()
end

local push, pop, concat, sort = table.insert, table.remove, table.concat, table.sort

------------------------------------------------------------
-- binary math helpers:
------------------------------------------------------------
function tobits(number)
  local t = {}
  repeat
    local x = number % 2
    push(t, x)
    number = (number - x) / 2
  until number == 0
  return t
end

function bits_tostring(bin, i, j)
  return concat(bin, "", i, j):reverse()
end

function bits_tonumber(bin, i, j)
  return tonumber(bits_tostring(bin, i, j), 2)
end

function bits_add(a, b)
  local x = 0
  local c = {}
  for i = 1, math.max(#a, #b) do
    x = (a[i] or 0) + (b[i] or 0) + x
    c[i] = x % 2
    x = (x - c[i]) / 2
  end
  if x > 0 then
    push(a, x)
  end
  return c
end

function bits_mul(a, b)
  local c = {}
  
  for i = 1, #b do
    if not c[i] then
      c[i] = 0
    end
    if b[i] == 1 then
      local shift = i - 1
      local x = 0
      for j = 1, #a do
        x = a[j] + (c[j + shift] or 0) + x
        c[j + shift] = x % 2
        x = (x - c[j + shift]) / 2
      end
      if x > 0 then
        push(c, x)
      end
    end
  end  
  
  return c
end

-- Suits
SUITS = 'SDCH'
SUIT_NUM = 4
SPADES, DIAMONDS, CLUBS, HEARTS = 0, 1, 2, 3

-- Ranks
RANKS = 'A23456789TJQK'
RANK_NUM = 13

-- Cards
-- Card_Index is functionined as:
-- suit + rank * SUIT_NUM
CARDS = {}
for r = 1, RANK_NUM do
  for s = 1, SUIT_NUM do
    push(CARDS, RANKS:sub(r, r) .. SUITS:sub(s, s))
  end
end

CARD_NUM = SUIT_NUM * RANK_NUM

PILE_NUM = 8    -- cascades
CELL_NUM = 4    -- open cells
BASE_NUM = 4    -- foundation piles
DESK_SIZE = PILE_NUM + CELL_NUM + BASE_NUM

PILE_START = 1
PILE_END = PILE_START + PILE_NUM - 1

CELL_START = PILE_END + 1
CELL_END = CELL_START + CELL_NUM - 1

BASE_START = CELL_END + 1
BASE_END = BASE_START + BASE_NUM - 1


function new_desk()
  local t = {}
  for x = 1, DESK_SIZE do
    push(t, {})
  end
  return t
end

function reset(desk)
  for _, pile in ipairs(desk) do
    while #pile > 0 do
      pop(pile)
    end
  end
end

function range(n)
  local t = {}
  for i = 0, n - 1 do
    push(t, i)
  end
  return t
end

function deal_by_number(desk, n)
  reset(desk)
  -- use LCG algorithm to pick up cards from the deck
  -- http://en.wikipedia.org/wiki/Linear_congruential_generator
--~   local m = 2^31
  local a = tobits(1103515245)
  local c = tobits(12345)
  local cards = range(CARD_NUM)
  while #cards > 0 do
    for i = PILE_START, PILE_END do
      if #cards == 0 then
        break
      else
--~         n = (a * n + c) % m
        local bits_n = bits_add(bits_mul(a, tobits(n)), c)
        n = bits_tonumber(bits_n, 1, math.min(31, #bits_n))  -- modulus of 2^31
        push(desk[i], pop(cards, 1 + (n % #cards)))
      end
    end
  end
end

function desk_to_str(desk)
  -- sort cascades and cells
  local piles = {}
  for i = PILE_START, PILE_END do
    push(piles, '[' .. concat(desk[i], ", ") .. ']')
  end
  sort(piles)

  local cells = {}
  for i = CELL_START, CELL_END do
    push(cells, '[' .. concat(desk[i], ", ") .. ']')
  end
  sort(cells)

  local bases = {}
  for i = BASE_START, BASE_END do
    push(bases, '[' .. concat(desk[i], ", ") .. ']')
  end
  return concat(piles, ', ') .. ', ' .. concat(cells, ', ') .. ',' .. concat(bases, ', ')
end

function get_empty_pile(desk)
  for i = PILE_START, PILE_END do
    if #desk[i] == 0 then
      return i
    end
  end
end

function get_empty_cell(desk)
  for i = CELL_START, CELL_END do
    if #desk[i] == 0 then
      return i
    end
  end
end

function get_base_key(desk)
  local s = #desk[BASE_START +   SPADES]
  local d = #desk[BASE_START + DIAMONDS]
  local c = #desk[BASE_START +    CLUBS]
  local h = #desk[BASE_START +   HEARTS]
  return ((s * RANK_NUM + d) * RANK_NUM + c) * RANK_NUM + h
end

function get_pile_key(desk)
  local keys = {}
  for i = PILE_START, PILE_END do
    push(keys, '[' .. concat(desk[i], ",") .. ']')
  end
  sort(keys)
  
  return concat(keys)
end

function count_empty_cells(desk)
  local n = 0
  for i = PILE_START, CELL_END do
    if #desk[i] == 0 then
      n = n + 1
    end
  end
  return n
end

function count_base_cards(desk)
  local n = 0
  for i = BASE_START, BASE_END do
    n = n + #desk[i]
  end
  return n
end

function is_empty(desk)
  for i = PILE_START, CELL_END do
    if #desk[i] > 0 then
      return false
    end
  end
  return true
end

-- MOVE is defined as:
-- move = source_pile_index * DESK_SIZE + destination_pile_index

function move_card(desk, move)
  local dst = move % DESK_SIZE
  local src = (move - dst) / DESK_SIZE
  
  push(desk[dst + 1], (pop(desk[src + 1])))
end

function move_cards(desk, moves)
  for _, move in ipairs(moves) do
    local dst = move % DESK_SIZE
    local src = (move - dst) / DESK_SIZE
    
    push(desk[dst + 1], (pop(desk[src + 1])))
  end
end

function move_cards_reverse(desk, moves)
  local i = #moves
  while i > 0 do
    local move = moves[i]
    local src = move % DESK_SIZE
    local dst = (move - src) / DESK_SIZE
    
    push(desk[dst + 1], (pop(desk[src + 1])))
    
    i = i - 1
  end
end

function auto_move_to_bases(desk, moves)
  local ok = true
  while ok do
    ok = false
    for i = PILE_START, CELL_END do
      local l = #desk[i]
      if l > 0 then
        local card = desk[i][l]
        local suit = card % SUIT_NUM
        local rank = (card - suit) / SUIT_NUM

        local ro = #desk[BASE_START + suit]
        local rx, ry
        if suit == SPADES or suit == CLUBS then
          rx = #desk[BASE_START + DIAMONDS]
          ry = #desk[BASE_START +   HEARTS]
        else
          rx = #desk[BASE_START +   SPADES]
          ry = #desk[BASE_START +    CLUBS]
        end
        
        if rank == ro and rank < rx + 2 and rank < ry + 2 then
          ok = true
          -- move it to the base
          push(moves, (i - 1) * DESK_SIZE + BASE_START + suit - 1)
          push(desk[BASE_START + suit], (pop(desk[i])))
        end
      end
    end
  end
end

function get_moves(desk)
  local moves = {}
  local empty_pile = get_empty_pile(desk)
  local empty_cell = get_empty_cell(desk)
  
  for i = PILE_START, CELL_END do
    local l = #desk[i]
    if l > 0 then
      local card = desk[i][l]
      local suit = card % SUIT_NUM
      local rank = (card - suit) / SUIT_NUM
      -- 1. move to foundation
      if #desk[BASE_START + suit] == rank then
        push(moves, (i - 1) * DESK_SIZE + BASE_START + suit - 1)
      end
      -- 2. move to tableau
      local suit_clr = (suit == DIAMONDS or suit == HEARTS)
      for j = PILE_START, PILE_END do
        local n = #desk[j]
        if n > 0 then
          local c = desk[j][n]
          local s = c % SUIT_NUM
          local r = (c - s) / SUIT_NUM
          local s_clr = (s == DIAMONDS or s == HEARTS)
          -- Tableau should be built down in alternating colors.
          if r == rank + 1 and s_clr ~= suit_clr then
            push(moves, (i - 1) * DESK_SIZE + j - 1)
          end
        end
      end
      -- 3. move to an empty space
      if l > 1 then
        if empty_cell then push(moves, (i - 1) * DESK_SIZE + empty_cell - 1) end
        if empty_pile then push(moves, (i - 1) * DESK_SIZE + empty_pile - 1) end
      end
    end
  end
  return moves
end

function get_progress(desk)
  local n = 0
  for i = PILE_START, PILE_END do
    local pile = desk[i]
    for a = 1, #pile - 1 do
      local rank_a = math.floor(pile[a] / SUIT_NUM)
      for b = a + 1, #pile do
        local rank_b = math.floor(pile[b] / SUIT_NUM)
        if rank_a < rank_b then
          n = n + (rank_b - rank_a)
        end
      end
    end
  end
  return n
end

function add_to_set_at(src, i, j)
  if not src[i] then
    src[i] = { len = 0 }
  end
  if not src[i][j] then
    src[i][j] = true
    src[i].len = src[i].len + 1
  end
end

function split(desk, moves, threshold)
  local strategy = {}
  
  for i, m in ipairs(moves) do
    move_cards(desk, m)
    auto_move_to_bases(desk, m)
    
    local n_1 = count_empty_cells(desk)
    local n_2 = get_progress(desk)
    
    add_to_set_at(strategy, n_1 - n_2, i)

    move_cards_reverse(desk, m)
  end
  
  local keys = {}
  for k in pairs(strategy) do push(keys, k) end
  sort(keys)
  local mask_a = strategy[pop(keys)]
   
  while mask_a.len < threshold do
    for k, v in pairs(strategy[pop(keys)]) do
      if not mask_a[k] then
        mask_a[k] = true
        mask_a.len = mask_a.len + 1
      end
    end
  end
  
  local moves_a, moves_b = {}, {}
  for i, m in ipairs(moves) do
    push(mask_a[i] and moves_a or moves_b, m)
  end
  return moves_a, moves_b
end

function test_moves(desk, src_moves, src_done, solution)
  local dst_moves = {}
  local dst_done = {}

  for _, moves in ipairs(src_moves) do
    move_cards(desk, moves)
    auto_move_to_bases(desk, moves)
      
    if solution == nil or #moves < #solution then
      if is_empty(desk) then
        if _debug then
          print(string.format("Found %d moves solution", #moves))
        end
        solution = moves
      else
        local base_key = get_base_key(desk)
        if not dst_done[base_key] then
          if src_done[base_key] then
            dst_done[base_key] = src_done[base_key]
          else
            dst_done[base_key] = {}
          end
        end
      
        local pile_key = get_pile_key(desk)
        if not dst_done[base_key][pile_key] then
          dst_done[base_key][pile_key] = true

          for _, move in ipairs(get_moves(desk)) do
            local new_moves = {}
            for _, m in ipairs(moves) do
              push(new_moves, m)
            end
            push(new_moves, move)
            
            push(dst_moves, new_moves)
          end
        end
      end
    end
    move_cards_reverse(desk, moves) -- restore our desk
  end

  return solution, dst_moves, dst_done
end

DESK_NUM_MAX = 8000
DESK_NUM_MIN = 2000

function get_solution(desk)
  local src_moves = {}
  for _, move in ipairs(get_moves(desk)) do
    push(src_moves, { move })
  end
  
  local src_done = {}
  local reserve = {}
  local solution = nil
  
  while true do
    while #src_moves > 0 do
      if _debug then
        print(#src_moves)
        io.flush()
      end
      if #src_moves > DESK_NUM_MAX then
        if _debug then
          print "Splitting..."
        end
        local a, b = split(desk, src_moves, DESK_NUM_MIN)
        push(reserve, {b, src_done})
        src_moves = a
        if _debug then
          print(string.format("Split #%d -> %d+%d", #reserve, #a, #b))
        end
      end

      solution, src_moves, src_done = test_moves(desk, src_moves, src_done, solution)
    end
    if solution or #reserve == 0 then
      break
    else
      if _debug then
        print(string.format("Step back to %d split", #reserve))
      end
      src_moves, src_done = unpack(pop(reserve))
    end
  end
  return solution
end

if _debug then
  local x = new_desk()

  for i = PILE_START, PILE_END do
    deal_by_number(x, i - 1)
    print(desk_to_str(x))
  end

  local moves = get_solution(x)

  print("o" .. string.rep("-=", 25))
  print(string.format("| Total: %d playfield moves", #moves - CARD_NUM))
  print("o" .. string.rep("-=", 25))

  for i, move in ipairs(moves) do
    local b = move % DESK_SIZE
    local a = (move - b) / DESK_SIZE
    
    a = a + 1
    b = b + 1
    
    local card = CARDS[x[a][#x[a]] + 1]
    local dest = "BASE"
    if CELL_START <= b and b <= CELL_END then
      dest = "cell"
    elseif PILE_START <= b and b <= PILE_END then
      if #x[b] > 0 then
        dest = CARDS[x[b][#x[b]] + 1]
      else
        dest = "pile"
      end
    end

    print(string.format("%d: %s -> %s", i, card, dest))
    move_card(x, move)
  end

  job_time = os.time() - job_time
  print(string.format("Job has taken %d min %d sec.", math.floor(job_time / 60), job_time % 60))
end
