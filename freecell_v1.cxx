#include <iostream>
#include <vector>
#include <map>
#include <set>
#include <string>
#include <sstream>
#include <algorithm>
#include <iterator>
#include <ctime>

// Suits
const char SUITS[] = "SDCH";
enum { SPADES, DIAMONDS, CLUBS, HEARTS, SUIT_NUM };
// Ranks
const char RANKS[] = "A23456789TJQK";
enum { RANK_NUM = 13 };
// Cards
// Card_Index is defined as:
// suit + rank * SUIT_NUM
const int CARD_NUM = SUIT_NUM * RANK_NUM;
char CARDS[CARD_NUM][3]; // will be initialized in the main()

const int PILE_NUM = 8; // cascades
const int CELL_NUM = 4; // open cells
const int BASE_NUM = 4; // foundation piles
const int DESK_SIZE = PILE_NUM + CELL_NUM + BASE_NUM;

const int PILE_START = 0;
const int PILE_END = PILE_START + PILE_NUM;

const int CELL_START = PILE_END;
const int CELL_END = CELL_START + CELL_NUM;

const int BASE_START = CELL_END;
const int BASE_END = BASE_START + BASE_NUM;

template< class T>
std::string vector_to_string( const std::vector< T >& v ) {
  std::ostringstream os;
  std::copy( v.begin(), v.end() - 1, std::ostream_iterator< T > ( os, ", " ) );
  if( !v.empty() ) {
    os << v.back();
  }
  return '[' + os.str() + ']';
}

typedef std::vector< int >         IntArray;
typedef std::vector< IntArray >    IntArrays;
typedef std::set< std::string >    StringSet;
typedef std::map< int, StringSet > DeskMap;

struct Desk {
  IntArray mDesk[DESK_SIZE];

  void reset();
  void deal_by_number( int n );

  std::string to_string() const;
  
  int get_empty_cell() const;
  int get_empty_pile() const;
  int get_base_key() const;
  std::string get_pile_key() const;
  
  int count_empty_cells() const;
  int count_base_cards() const;
  bool is_empty() const;

  // MOVE is defined as:
  // move = source_pile_index * DESK_SIZE + destination_pile_index
  void move_card( int move );
  void move_cards( const IntArray& moves );
  void move_cards_reverse( const IntArray& moves );
  
  void auto_move_to_bases( IntArray& moves );

  IntArray get_moves() const;
  
  int get_progress() const;
};

void Desk::reset() {
  for( int i = 0; i < DESK_SIZE; i++ ) {
    mDesk[i].clear();
  }
}

void Desk::deal_by_number( int n ) {
  reset();
  // use LCG algorithm to pick up cards from the deck
  // http://en.wikipedia.org/wiki/Linear_congruential_generator
  long long m = 0x80000000;  // 2 ^ 31
  long long a = 1103515245;
  long long c = 12345;

  IntArray cards;
  for( int i = 0; i < CARD_NUM; i++ ) {
    cards.push_back( i );
  }
  while( !cards.empty() ) {
    for( int i = PILE_START; i < PILE_END; i++ ) {
      if( cards.empty() ) {
        break;
      } else {
        n = (int) ((a * n + c) % m);
        int j = n % cards.size();
        mDesk[i].push_back( cards[j] );
        cards.erase( cards.begin() + j );
      }
    }
  }
}

std::string Desk::to_string() const {
  std::string desk[DESK_SIZE];
  for( int i = 0; i < DESK_SIZE; i++ ) {
    desk[i] = vector_to_string( mDesk[i] );
  }

  // sort cascades and cells
  std::sort( desk + PILE_START, desk + PILE_END );
  std::sort( desk + CELL_START, desk + CELL_END );
  
  std::ostringstream os;
  std::copy( desk, desk + DESK_SIZE, std::ostream_iterator< std::string > ( os ) );
  return os.str();
}

int Desk::get_empty_pile() const {
  for( int i = PILE_START; i < PILE_END; i++ ) {
    if( mDesk[i].empty() ) {
      return i;
    }
  }
  return -1;
}

int Desk::get_empty_cell() const {
  for( int i = CELL_START; i < CELL_END; i++ ) {
    if( mDesk[i].empty() ) {
      return i;
    }
  }
  return -1;
}

int Desk::get_base_key() const {
  int s = mDesk[BASE_START +   SPADES].size();
  int d = mDesk[BASE_START + DIAMONDS].size();
  int c = mDesk[BASE_START +    CLUBS].size();
  int h = mDesk[BASE_START +   HEARTS].size();
  return ((s * RANK_NUM + d) * RANK_NUM + c) * RANK_NUM + h;
}

std::string Desk::get_pile_key() const {
  std::string keys[PILE_NUM];
  for( int i = PILE_START; i < PILE_END; i++ ) {
    keys[i] = vector_to_string( mDesk[i] );
  }
  
  std::sort( keys, keys + PILE_NUM );
  
  std::ostringstream os;
  std::copy( keys, keys + PILE_NUM, std::ostream_iterator< std::string > ( os ) );
  return os.str();
}

int Desk::count_empty_cells() const {
  int n = 0;
  for( int i = PILE_START; i < CELL_END; i++ ) {
    if( mDesk[i].empty() ) {
      n += 1;
    }
  }
  return n;
}

int Desk::count_base_cards() const {
  int n = 0;
  for( int i = BASE_START; i < BASE_END; i++ ) {
    n += mDesk[i].size();
  }
  return n;
}

bool Desk::is_empty() const {
  for( int i = PILE_START; i < CELL_END; i++ ) {
    if( !mDesk[i].empty() ) {
      return false;
    }
  }
  return true;
}

void Desk::move_card( int move ) {
  int src = move / DESK_SIZE;
  int dst = move % DESK_SIZE;
  mDesk[dst].push_back( mDesk[src].back() );
  mDesk[src].pop_back();
}

void Desk::move_cards( const IntArray& moves ) {
  for( IntArray::const_iterator it = moves.begin(); it != moves.end(); ++it ) {
    int src = *it / DESK_SIZE;
    int dst = *it % DESK_SIZE;
    mDesk[dst].push_back( mDesk[src].back() );
    mDesk[src].pop_back();
  }
}

void Desk::move_cards_reverse( const IntArray& moves ) {
  for( IntArray::const_reverse_iterator it = moves.rbegin(); it != moves.rend(); ++it ) {
    int dst = *it / DESK_SIZE;
    int src = *it % DESK_SIZE;
    mDesk[dst].push_back( mDesk[src].back() );
    mDesk[src].pop_back();
  }
}

void Desk::auto_move_to_bases( IntArray& moves ) {
  bool ok = true;
  while( ok ) {
    ok = false;
    for( int i = PILE_START; i < CELL_END; i++ ) {
      if( !mDesk[i].empty() ) {
        int card = mDesk[i].back();
        int suit = card % SUIT_NUM;
        int rank = card / SUIT_NUM;

        int ro = mDesk[BASE_START + suit].size();
        int rx, ry;
        if( suit == SPADES || suit == CLUBS ) {
          rx = mDesk[BASE_START + DIAMONDS].size();
          ry = mDesk[BASE_START +   HEARTS].size();
        } else {
          rx = mDesk[BASE_START +   SPADES].size();
          ry = mDesk[BASE_START +    CLUBS].size();
        }

        if( rank == ro && rank < rx + 2 && rank < ry + 2 ) {
          ok = true;
          // move it to the base
          moves.push_back( i * DESK_SIZE + BASE_START + suit );
          mDesk[BASE_START + suit].push_back( mDesk[i].back() );
          mDesk[i].pop_back();
        }
      }
    }
  }
}

IntArray Desk::get_moves() const {
  IntArray moves;
  int empty_pile = get_empty_pile();
  int empty_cell = get_empty_cell();

  for( int i = PILE_START; i < CELL_END; i++ ) {
    int l = mDesk[i].size();
    if( l > 0 ) {
      int card = mDesk[i].back();
      int suit = card % SUIT_NUM;
      int rank = card / SUIT_NUM;
      // 1. move to foundation
      if( mDesk[BASE_START + suit].size() == rank ) {
        moves.push_back( i * DESK_SIZE + BASE_START + suit );
      }
      // 2. move to tableau
      bool suit_clr = ( suit == DIAMONDS || suit == HEARTS );
      for( int j = PILE_START; j < PILE_END; j++ ) {
        if( !mDesk[j].empty() ) {
          int c = mDesk[j].back();
          int s = c % SUIT_NUM;
          int r = c / SUIT_NUM;
          bool s_clr = ( s == DIAMONDS || s == HEARTS );
          // Tableau should be built down in alternating colors.
          if( r == rank + 1 && s_clr != suit_clr ) {
            moves.push_back( i * DESK_SIZE + j );
          }
        }
      }
      // 3. move to an empty space
      if( l > 1 ) {
        if( empty_cell >= 0 ) moves.push_back( i * DESK_SIZE + empty_cell );
        if( empty_pile >= 0 ) moves.push_back( i * DESK_SIZE + empty_pile );
      }
    }
  }
  return moves;
}

int Desk::get_progress() const {
  int n = 0;
  for( int i = PILE_START; i < PILE_END; i++ ) {
    const IntArray& pile = mDesk[ i ];
    for( int a = 0; a < (int)pile.size() - 1; a++ ) {
      int rank_a = pile[ a ] / SUIT_NUM;
      for( int b = a + 1; b < pile.size(); b++ ) {
        int rank_b = pile[ b ] / SUIT_NUM;
        if( rank_a < rank_b ) {
          n = n + (rank_b - rank_a);
        }
      }
    }
  }
  return n;
}


int DESK_NUM_MAX = 8000;
int DESK_NUM_MIN = 2000;

bool _debug = false;

typedef std::set< int > IntSet;
typedef std::map< int, IntSet > StrategyMap;

template< class T >
void operator |=( std::set< T >& lhv, const std::set< int >& rhv ) {
  for( typename std::set< T >::const_iterator it = rhv.begin(); it != rhv.end(); ++it ) {
    lhv.insert( *it );
  }
}

void split( Desk& desk, IntArrays& moves, int threshold,
  IntArrays& moves_a, IntArrays& moves_b ) {

  StrategyMap strategy;

  int i = moves.size();
  while( i --> 0 ) {
    IntArray& m = moves[ i ];
    desk.move_cards( m );
    desk.auto_move_to_bases( m );

    int n_1 = desk.count_empty_cells();
    int n_2 = desk.get_progress();

    strategy[n_1 - n_2].insert( i );

    desk.move_cards_reverse( m );
  }

  IntSet mask_a;
  for( StrategyMap::reverse_iterator it = strategy.rbegin(); it != strategy.rend(); ++it ) {
    mask_a |= it->second;
    if( mask_a.size() > threshold ) {
      break;
    }
  }

  i = moves.size();
  while( i --> 0 ) {
    if( mask_a.find( i ) != mask_a.end() ) {
      moves_a.push_back( moves[ i ] );
    } else {
      moves_b.push_back( moves[ i ] );
    }
  }
}

void test_moves( Desk& desk,
  IntArrays& src_moves, DeskMap& src_done,
  IntArray* solution,
  IntArrays& dst_moves, DeskMap& dst_done ) {

  for( IntArrays::iterator moves = src_moves.begin(); moves != src_moves.end(); ++moves ) {
    desk.move_cards( *moves );
    desk.auto_move_to_bases( *moves );

    if( solution->empty() || moves->size() < solution->size() ) {
      if( desk.is_empty() ) {
        if( _debug ) {
          std::cout << "Found " << moves->size() << " moves solution\n";
        }
        *solution = *moves;
      } else {
        int base_key = desk.get_base_key();
        if( dst_done.find( base_key ) == dst_done.end() ) {
          if( src_done.find( base_key ) != src_done.end() ) {
            dst_done[base_key] = src_done[base_key];
          }
        }

        std::string pile_key = desk.get_pile_key();
        if( dst_done[base_key].find( pile_key ) == dst_done[base_key].end() ) {
          dst_done[base_key].insert( pile_key );

          IntArray next_moves = desk.get_moves();
          for( IntArray::const_iterator move = next_moves.begin(); move != next_moves.end(); ++move ) {
            IntArray new_moves = *moves;
            new_moves.push_back( *move );

            dst_moves.push_back( new_moves );
          }
        }
      }
    }

    desk.move_cards_reverse( *moves ); // restore our desk
  }
}


IntArray get_solution( Desk& desk ) {
  IntArrays src_moves;
  IntArray moves = desk.get_moves();
  for( IntArray::const_iterator it = moves.begin(); it != moves.end(); ++it ) {
    IntArray m;
    m.push_back( *it );
    src_moves.push_back( m );
  }
  DeskMap src_done;

  std::vector< std::pair< IntArrays, DeskMap > > reserve;

  IntArray solution;

  while( true ) {
    while( !src_moves.empty() ) {
      if( _debug ) {
        std::cout << src_moves.size() << std::endl;
      }
      if( src_moves.size() > DESK_NUM_MAX ) {
        if( _debug ) {
          std::cout << "Splitting...\n";
        }
        IntArrays a, b;
        split( desk, src_moves, DESK_NUM_MIN, a, b );
        reserve.push_back( std::pair< IntArrays, DeskMap >( b, src_done ) );
        src_moves = a;
        if( _debug ) {
          std::cout << "Split #" << reserve.size() << " -> " << a.size() << "+" << b.size() << std::endl;
        }
      }

      IntArrays dst_moves;
      DeskMap dst_done;

      test_moves( desk, src_moves, src_done, &solution, dst_moves, dst_done );
      src_moves = dst_moves;
      src_done  = dst_done;
    }

    if( !solution.empty() || reserve.empty() ) {
      break;
    } else {
      if( _debug ) {
        std::cout << "Step back to " << reserve.size() << " split\n";
      }
      src_done = reserve.back().second;
      src_moves = reserve.back().first;
      reserve.pop_back();
    }
  }

  return solution;
}

int main(int argc, char **argv)
{
  _debug = true;
  
  time_t job_time = time( 0 );
  
  for( int r = 0; r < RANK_NUM; r++ ) {
      for( int s = 0; s < SUIT_NUM; s++ ) {
          int i = s + r * SUIT_NUM;
          CARDS[i][0] = RANKS[r];
          CARDS[i][1] = SUITS[s];
      }
  }
  
  Desk x;
  for( int i = PILE_START; i < PILE_END; i++ ) {
    x.deal_by_number( i );
    std::cout << x.to_string() << std::endl;
  }
  
  IntArray moves = get_solution( x );

  std::cout << "o-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n";
  std::cout << "| Total: " << moves.size() - CARD_NUM << " playfield moves\n";
  std::cout << "o-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n";

  for( int i = 0; i < moves.size(); i++ ) {
    int a = moves[i] / DESK_SIZE;
    int b = moves[i] % DESK_SIZE;
    const char* card = CARDS[ x.mDesk[a].back() ];
    const char* dest = "BASE";
    if( CELL_START <= b && b < CELL_END ){
      dest = "cell";
    } else if ( PILE_START <= b && b < PILE_END ) {
      if( !x.mDesk[b].empty() ) {
        dest = CARDS[ x.mDesk[b].back() ];
      } else {
        dest = "pile";
      }
    }

    std::cout << i + 1 << ": " << card << " -> " << dest << std::endl;
    x.move_card( moves[i] );
  }

  job_time = time(0) - job_time;
  std::cout << "Job has taken " << job_time / 60 << " min " << job_time % 60 << " sec." << std::endl;
	return 0;
}
