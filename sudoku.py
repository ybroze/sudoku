"""
Some methods to solve Sudoku problems pulled from
the interwebs.
"""
from itertools import product
from random import randint, sample
from urllib2 import urlopen

from lxml import html


def to_square(position):
    """Convert a position tuple to a square number as an int,
       0 through 8, corresponding to the square on the
       sudoku board.
    """
    x, y = position
    hyper_row = x / 3
    hyper_column = y / 3

    return (hyper_row * 3) + hyper_column


def new_board():
    """Make a new blank board dict."""
    return { (x,y): None for x, y in product(range(9), range(9)) }


def print_board(board):
    """Pretty-print a board."""
    for row in range(9):
        tokens = [ board[row, col] or '.' for col in range(9) ]
        print ' '.join( str(t) for t in tokens )


def new_possible():
    """Make a new blank possibilities dict."""
    return { position: set(range(1, 10))
             for position in product(range(9), range(9)) }


def fetch_new_puzzle(difficulty):
    """Get a new puzzle from the online source.
       Difficulties are from 1 to 5 maybe? Integers.
       Boards are indexed x and y, where x is the row
       number and y is the column number.
    """
    page_text = urlopen("http://www.free-sudoku.com/sudoku.php?mode=%s" % 
                   difficulty ).read()
    tree = html.fromstring(page_text)

    board = new_board()
    for x, y in product(range(9), range(9)):
        element_id = (x * 9) + y + 1
        text_content = tree.get_element_by_id(element_id).text_content()
        value = int(text_content) if text_content else None
        board[(x,y)] = value

    return board


def deterministic_solve(board, possible):
    """Solve the board with a simple technique, looking for
       completely deterministic squares.

       Raise ValueError if the puzzle is unsolvable.

    @param board: A board dict to solve.
    @param possible: A dict of possibility sets.

    @return: updated board, possibile tuple.
    """
    # Make copies of the input.
    board = dict(board)
    possible = dict(possible)

    # Keep trying till we make no progress.
    last_board = None
    while board != last_board:
        last_board = dict(board)

        # Show us our board, for funsies.
        print '================='
        print_board(board)

        # Check every cell to see what its possibilities are.
        for cell in product(range(9), range(9)):

            # Solved cells have one possibility.
            if board[cell]:
                possible[cell] = set([ board[cell] ])

            else:
                square_num = to_square(cell)
                others = [ value for othercell, value in board.items()
                           if value is not None
                           and othercell != cell
                           and (othercell[0] == cell[0]
                                or othercell[1] == cell[1]
                                or to_square(othercell) == square_num) ]

                possible[cell] = possible[cell].difference(others)

        # Now update our board appropriately.
        for cell in product(range(9), range(9)):

            # We must have some possibilities for each.
            if len(possible[cell]) == 0:
                print 'Cell %s has no more possibilities.' % str(cell)
                raise ValueError(possible[cell])

            # Check the singletons for conflicts.
            if len(possible[cell]) == 1:
                square_num = to_square(cell)
                others = [ options for othercell, options in possible.items()
                           if len(options) == 1
                           and othercell != cell
                           and (othercell[0] == cell[0]
                                or othercell[1] == cell[1]
                                or to_square(othercell) == square_num) ]

                # If we're in the clear, we can assign the value.
                if possible[cell] not in others:
                    board[cell] = list(possible[cell])[0]
                else:
                    print 'Cell %s conflicts with another.' % str(cell)
                    raise ValueError(possible[cell])

    return board, possible
        

_recursion_steps = 0
def completely_solve(board, possible):
    """Completely solve a puzzle by trying different
       possibilities, recursively.
    """
    # Keep track of the number of steps.
    global _recursion_steps

    # Work only on copies.
    board = dict(board)
    possible = dict(possible)

    # First deterministically solve once.
    board, possible = deterministic_solve(board, possible)

    # If we're not solved, then recursively guess.
    if None in board.values():
        # Prioritize by fewest options first.
        none_cells = [ cell for cell, value in board.items()
                       if value is None ]
        none_cells.sort(key=lambda cell: possible[cell])
        cell = none_cells[0]

        # Try each possibility for the cell.
        for trial in possible[cell]:
            trial_board = dict(board)
            trial_board[cell] = trial
            trial_possible = dict(possible)

            try:
                print '\nAttempting %s in cell %s.' % (trial, cell)
                _recursion_steps += 1
                board, possible = completely_solve(
                    trial_board, trial_possible)
                break

            # Catch errors until all possibilities
            # for the cell are tested.
            except ValueError:
                pass

        # If we're stuck, raise an error.
        if None in board.values():
            print "Recursion path is a dead end."
            raise ValueError

    # If it worked, we're all done!
    else:
        print "Yatta!"
        print "Finished in %d recursions." % _recursion_steps
        _recursion_steps = 0

    return board, possible


def make_puzzle():
    """Make a new sudoku puzzle."""
    # Seed a new board and solve it.
    board = new_board()
    x = randint(0,9)
    y = randint(0,9)
    value = randint(1,9)

    board, _ = completely_solve(board, new_possible())

    # Randomly remove elements.
    for x, y in sample(board, 60):
        board[x,y] = None

    # Print.
    print 'Created new puzzle:'
    print_board(board)

    return board
    

def doit(difficulty):
    """Do the entire routine on a new puzzle of the
       provided difficulty.
    """
    completely_solve(fetch_new_puzzle(difficulty), new_possible())

if __name__ == '__main__':
   doit(3)
