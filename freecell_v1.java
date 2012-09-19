import java.util.*;

interface FreecellConstants {
  // Suits
  static final String SUITS = "SDCH";
  static final int
    SUIT_NUM = 4,
    SPADES   = 0,
    DIAMONDS = 1,
    CLUBS    = 2,
    HEARTS   = 3;

  // Ranks
  static final String RANKS = "A23456789TJQK";
  static final int RANK_NUM = 13;

  // Cards
  // Card_Index is defined as:
  // suit + rank * SUIT_NUM
  static final int CARD_NUM = SUIT_NUM * RANK_NUM;
  static String[] CARDS = new String[CARD_NUM]; // will be initialized in the main class

  static final int
    PILE_NUM = 8, // cascades
    CELL_NUM = 4, // open cells
    BASE_NUM = 4, // foundation piles
    DESK_SIZE = PILE_NUM + CELL_NUM + BASE_NUM,

    PILE_START = 0,
    PILE_END = PILE_START + PILE_NUM,

    CELL_START = PILE_END,
    CELL_END = CELL_START + CELL_NUM,

    BASE_START = CELL_END,
    BASE_END = BASE_START + BASE_NUM;
};

@SuppressWarnings("unchecked")
class Desk implements FreecellConstants {
  Stack< Integer > mDesk[];

  Desk() {
    mDesk = new Stack[DESK_SIZE];
    for( int i = 0; i < DESK_SIZE; i++ ) {
      mDesk[i] = new Stack< Integer >();
    }
  }

  void reset() {
    for( Stack pile : mDesk ) {
      pile.clear();
    }
  }

  void deal_by_number( int n ) {
    reset();
    // use LCG algorithm to pick up cards from the deck
    // http://en.wikipedia.org/wiki/Linear_congruential_generator
    long m = 0x80000000;  // 2 ^ 31
    long a = 1103515245;
    long c = 12345;

    Vector< Integer > cards = new Vector< Integer >();
    for( int i = 0; i < CARD_NUM; i++ ) {
      cards.add( Integer.valueOf( i ) );
    }
    while( !cards.isEmpty() ) {
      for( int i = PILE_START; i < PILE_END; i++ ) {
        if( cards.isEmpty() ) {
          break;
        } else {
          n = (int) ((a * n + c) % m);
          mDesk[i].add( cards.remove( n % cards.size() ) );
        }
      }
    }
  }

  @ Override
  public String toString() {
    String[] desk = new String[ DESK_SIZE ];
    for( int i = 0; i < DESK_SIZE; i++ ) {
      desk[ i ] = mDesk[ i ].toString();
    }

    // sort cascades and cells
    Arrays.sort( desk, PILE_START, PILE_END );
    Arrays.sort( desk, CELL_START, CELL_END );
    return Arrays.toString( desk );
  }

  int get_empty_pile() {
    for( int i = PILE_START; i < PILE_END; i++ ) {
      if( mDesk[i].isEmpty() ) {
        return i;
      }
    }
    return -1;
  }

  int get_empty_cell() {
    for( int i = CELL_START; i < CELL_END; i++ ) {
      if( mDesk[i].isEmpty() ) {
        return i;
      }
    }
    return -1;
  }

  int get_base_key() {
    int s = mDesk[BASE_START +   SPADES].size();
    int d = mDesk[BASE_START + DIAMONDS].size();
    int c = mDesk[BASE_START +    CLUBS].size();
    int h = mDesk[BASE_START +   HEARTS].size();
    return ((s * RANK_NUM + d) * RANK_NUM + c) * RANK_NUM + h;
  }

  String get_pile_key() {
    String[] keys = new String[ PILE_NUM ];
    for( int i = PILE_START; i < PILE_END; i++ ) {
      keys[i] = mDesk[i].toString();
    }

    Arrays.sort( keys );
    return Arrays.toString( keys );
  }

  int count_empty_cells() {
    int n = 0;
    for( int i = PILE_START; i < CELL_END; i++ ) {
      if( mDesk[i].isEmpty() ) {
        n += 1;
      }
    }
    return n;
  }

  int count_base_cards() {
    int n = 0;
    for( int i = BASE_START; i < BASE_END; i++ ) {
      n += mDesk[i].size();
    }
    return n;
  }

  boolean is_empty() {
    for( int i = PILE_START; i < CELL_END; i++ ) {
      if( !mDesk[i].isEmpty() ) {
        return false;
      }
    }
    return true;
  }

  // MOVE is defined as:
  // move = source_pile_index * DESK_SIZE + destination_pile_index
  void move_card( int move ) {
    int src = move / DESK_SIZE;
    int dst = move % DESK_SIZE;
    mDesk[dst].add( mDesk[src].pop() );
  }

  void move_cards( Vector< Integer > moves ) {
    for( int move : moves ) {
      int src = move / DESK_SIZE;
      int dst = move % DESK_SIZE;
      mDesk[dst].add( mDesk[src].pop() );
    }
  }

  void move_cards_reverse( Vector< Integer > moves ) {
    int i = moves.size();
    while( i --> 0 ) {
      int move = moves.get( i );
      int dst = move / DESK_SIZE;
      int src = move % DESK_SIZE;
      mDesk[dst].add( mDesk[src].pop() );
    }
  }

  void auto_move_to_bases( Vector< Integer > moves ) {
    boolean ok = true;
    while( ok ) {
      ok = false;
      for( int i = PILE_START; i < CELL_END; i++ ) {
        if( !mDesk[i].isEmpty() ) {
          int card = mDesk[i].peek();
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
            moves.add( Integer.valueOf( i * DESK_SIZE + BASE_START + suit ) );
            mDesk[BASE_START + suit].add( mDesk[i].pop() );
          }
        }
      }
    }
  }

  Vector< Integer > get_moves() {
    Vector< Integer > moves = new Vector< Integer >();
    int empty_pile = get_empty_pile();
    int empty_cell = get_empty_cell();

    for( int i = PILE_START; i < CELL_END; i++ ) {
      int l = mDesk[i].size();
      if( l > 0 ) {
        int card = mDesk[i].peek();
        int suit = card % SUIT_NUM;
        int rank = card / SUIT_NUM;
        // 1. move to foundation
        if( mDesk[BASE_START + suit].size() == rank ) {
          moves.add( Integer.valueOf( i * DESK_SIZE + BASE_START + suit ) );
        }
        // 2. move to tableau
        boolean suit_clr = ( suit == DIAMONDS || suit == HEARTS );
        for( int j = PILE_START; j < PILE_END; j++ ) {
          if( !mDesk[j].isEmpty() ) {
            int c = mDesk[j].peek();
            int s = c % SUIT_NUM;
            int r = c / SUIT_NUM;
            boolean s_clr = ( s == DIAMONDS || s == HEARTS );
            // Tableau should be built down in alternating colors.
            if( r == rank + 1 && s_clr != suit_clr ) {
              moves.add( Integer.valueOf( i * DESK_SIZE + j ) );
            }
          }
        }
        // 3. move to an empty space
        if( l > 1 ) {
          if( empty_cell >= 0 ) moves.add( Integer.valueOf( i * DESK_SIZE + empty_cell ) );
          if( empty_pile >= 0 ) moves.add( Integer.valueOf( i * DESK_SIZE + empty_pile ) );
        }
      }
    }
    return moves;
  }

  int get_progress() {
    int n = 0;
    for( int i = PILE_START; i < PILE_END; i++ ) {
      Stack< Integer > pile = mDesk[ i ];
      for( int a = 0; a < pile.size() - 1; a++ ) {
        int rank_a = pile.get( a ) / SUIT_NUM;
        for( int b = a + 1; b < pile.size(); b++ ) {
          int rank_b = pile.get( b ) / SUIT_NUM;
          if( rank_a < rank_b ) {
            n = n + (rank_b - rank_a);
          }
        }
      }
    }
    return n;
  }

};

@SuppressWarnings("unchecked")
public class freecell_v1 implements FreecellConstants {

  static int DESK_NUM_MAX = 8000;
  static int DESK_NUM_MIN = 2000;

  static boolean _debug = false;

  static {
    for( int r = 0; r < RANK_NUM; r++ ) {
      for( int s = 0; s < SUIT_NUM; s++ ) {
        CARDS[ r * SUIT_NUM + s ] = "" + RANKS.charAt( r ) + SUITS.charAt( s );
      }
    }
  }

  static void add_to_set_at( Map< Integer, Set< Integer > > src, Integer i, Integer j ) {
    if( !src.containsKey( i ) ) {
      src.put( i, new HashSet< Integer >() );
    }
    src.get( i ).add( j );
  }

  static void split( Desk desk, Vector< Vector< Integer > > moves, int threshold,
    Vector< Vector< Integer > > moves_a, Vector< Vector< Integer > > moves_b ) {

    Map< Integer, Set< Integer > > strategy = new HashMap< Integer, Set< Integer > >();

    int i = moves.size();
    while( i --> 0 ) {
      Vector< Integer > m = moves.get( i );
      desk.move_cards( m );
      desk.auto_move_to_bases( m );

      int n_1 = desk.count_empty_cells();
      int n_2 = desk.get_progress();

      add_to_set_at( strategy, n_1 - n_2, i );

      desk.move_cards_reverse( m );
    }

    Object[] keys = strategy.keySet().toArray();
    Arrays.sort( keys );

    i = keys.length;
    Set< Integer > mask_a = strategy.remove( keys[ --i ] );

    while( mask_a.size() < threshold ) {
      mask_a.addAll( strategy.remove( keys[ --i ] ) );
    }

    i = moves.size();
    while( i --> 0 ) {
      if( mask_a.contains( Integer.valueOf( i ) ) ) {
        moves_a.add( moves.get( i ) );
      } else {
        moves_b.add( moves.get( i ) );
      }
    }
  }

  static Vector< Integer > test_moves( Desk desk,
    Vector< Vector< Integer > > src_moves, Map< Integer, Set< String > > src_done,
    Vector< Integer > solution,
    Vector< Vector< Integer > > dst_moves, Map< Integer, Set< String > > dst_done ) {

    for( Vector< Integer > moves : src_moves ) {
      desk.move_cards( moves );
      desk.auto_move_to_bases( moves );

      if( solution == null || moves.size() < solution.size() ) {
        if( desk.is_empty() ) {
          if( _debug ) {
            System.out.println( String.format( "Found %d moves solution", moves.size() ) );
          }
          solution = moves;
        } else {
          Integer base_key = desk.get_base_key();
          if( !dst_done.containsKey( base_key ) ) {
            if( src_done.containsKey( base_key ) ) {
              dst_done.put( base_key, src_done.get( base_key ) );
            } else {
              dst_done.put( base_key, new HashSet< String >() );
            }
          }

          String pile_key = desk.get_pile_key();
          if( !dst_done.get( base_key ).contains( pile_key ) ) {
            dst_done.get( base_key ).add( pile_key );

            for( Integer move : desk.get_moves() ) {
              Vector< Integer > new_moves = (Vector< Integer >) moves.clone();
              new_moves.add( move );

              dst_moves.add( new_moves );
            }
          }
        }
      }

      desk.move_cards_reverse( moves ); // restore our desk
    }

    return solution;
  }

  static Vector< Integer > get_solution( Desk desk ) {
    Vector< Vector < Integer > > src_moves = new Vector< Vector < Integer > >();
    for( Integer move : desk.get_moves() ) {
      Vector< Integer > m = new Vector< Integer >();
      m.add( move );
      src_moves.add( m );
    }
    Map< Integer, Set< String > > src_done = new HashMap< Integer, Set< String > >();

    Stack reserve = new Stack();

    Vector< Integer > solution = null;

    while( true ) {
      while( !src_moves.isEmpty() ) {
        if( _debug ) {
          System.out.println( src_moves.size() );
        }
        if( src_moves.size() > DESK_NUM_MAX ) {
          if( _debug ) {
            System.out.println( "Splitting..." );
          }
          Vector< Vector< Integer > >
            a = new Vector< Vector< Integer > >(),
            b = new Vector< Vector< Integer > >();
          split( desk, src_moves, DESK_NUM_MIN, a, b );
          reserve.add( b );
          reserve.add( src_done );
          src_moves = a;
          if( _debug ) {
            System.out.println( String.format( "Split #%d -> %d+%d" , reserve.size() / 2, a.size(), b.size() ) );
          }
        }

        Vector< Vector < Integer > > dst_moves = new Vector< Vector < Integer > >();
        Map< Integer, Set< String > > dst_done = new HashMap< Integer, Set< String > >();

        solution  = test_moves( desk, src_moves, src_done, solution, dst_moves, dst_done );
        src_moves = dst_moves;
        src_done  = dst_done;
      }

      if( solution != null || reserve.isEmpty() ) {
        break;
      } else {
        if( _debug ) {
          System.out.println( String.format( "Step back to %d split", reserve.size() ) );
        }
        src_done = (Map< Integer, Set< String > >) reserve.pop();
        src_moves = (Vector< Vector < Integer > >) reserve.pop();
      }
    }

    return solution;
  }

  public static void main( String[] args ) {
    _debug = true;
    long job_time = System.currentTimeMillis();

    Desk x = new Desk();
    for( int i = PILE_START; i < PILE_END; i++ ) {
      x.deal_by_number( i );
      System.out.println( x.get_pile_key() );
    }

    Vector< Integer > moves = get_solution( x );

    System.out.println( "o-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=" );
    System.out.println( String.format( "| Total: %d playfield moves", moves.size() - CARD_NUM ) );
    System.out.println( "o-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=" );

    for( int i = 0; i < moves.size(); i++ ) {
      int move = moves.get( i );
      int a = move / DESK_SIZE;
      int b = move % DESK_SIZE;
      String card = CARDS[ x.mDesk[a].peek() ];
      String dest = "BASE";
      if( CELL_START <= b && b < CELL_END ){
        dest = "cell";
      } else if ( PILE_START <= b && b < PILE_END ) {
        if( !x.mDesk[b].isEmpty() ) {
          dest = CARDS[ x.mDesk[b].peek() ];
        } else {
          dest = "pile";
        }
      }

      System.out.println( String.format( "%d: %s -> %s", i + 1, card, dest ) );
      x.move_card( move );
    }

    job_time = (System.currentTimeMillis() - job_time) / 1000;
    System.out.println( String.format( "Job has taken %d min %d sec." , job_time / 60, job_time % 60 ) );
  }
};
