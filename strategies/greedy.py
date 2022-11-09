import time
from objects.player import Player, eval_move


class Greedy(Player):
    """
    Greedy is a subclass of player that initializes with an additional parameter called weights.
    Weights is a list of ints that determines what preference the greedy player gives to components
    of our score function.
    """

    def __init__(self, label, name, strategy, weights):
        self.label = label
        self.name = name
        self.pieces = []
        self.corners = set()
        self.strategy = strategy
        self.score = 0
        self.weights = weights

    def do_move(self, game):
        """
        Generates a move according to the Player's
        strategy and current state of the board.
        """
        return self.strategy(self, game, self.weights)


# The Greedy algorithm uses the available Shape with the highest area every time.
# If the Shape with the highest area is not able to be placed, the algorithm moves
# to the second-largest Shape... and so on.

# weights[0] determines how important size of a piece is
# weights[1] determines how important maximizing the difference of my corners and opponent corners

def greedy_player(player, game, weights):
    """
    Takes in a Player object and Game object and returns a placement in the form of a
    single piece object with a proper flip, orientation, corners, and points.
    If no placement can be made, function should return None.
    """

    # create copy of player's pieces (no destructively altering player's pieces)
    shape_options = [p for p in player.pieces]
    board = game.board

    def greedy_move():
        """
        Returns the greediest move.
        """
        # create an empty list that will contain all the possible moves with their respective scores
        final_moves = []
        tic = time.perf_counter()
        # for each piece, calculate all possible placements, and for each placement, calculate the score
        # of the move; add (move, score) to the list of final moves
        for piece in shape_options:
            # calculate all possible placements for the current piece
            possibles = player.possible_moves([piece], game)
            # if there are possible placements for the current piece:
            if possibles:
                def map_eval(piece):
                    return eval_move(piece, player, game, weights)

                # calculate score for each move and store it in a temporary list
                tmp = list(map(map_eval, possibles))
                # add all the elements in the temporary list in the final moves lsit
                final_moves.extend(tmp)
            # if there are no possible placements for the current piece:
            else:
                # remove the piece from the list of pieces
                shape_options.remove(piece)

        toc = time.perf_counter()
        print(f"Greedy calculation: {toc - tic} seconds")

        # create score list that contains all Piece placements, sorted by their score
        by_score = sorted(final_moves, key=lambda move: move[1], reverse=True)
        # if the score list contains Piece placements (objects), return the highest scoring Piece placement
        if len(by_score) > 0:
            print(f"placed piece {by_score[0][0].ID} at {by_score[0][0].refpt}")
            return by_score[0][0]
        # else, return None (no Piece placement)
        else:
            print("out of moves")
            return None

    # while there are shapes to place down, perform a greedy move
    return greedy_move()

# For a particular placement $i$, we assign weights $W_0$, $W_1$ such that:
#
# $ size_i $ = size of placement
#
# $ cor_{my} $ = number of my corners
#
# $ cor_{opp} $ = number of opponent's corners
#
# $ n_{opp} $ = number of opponents
#
# then:
#
# $ GreedyEval_i = size_i W_0 + \frac{\sum{(cor_{my} - cor_{opp})}}{n_{opp}} W_1 $
#
# This returns a score for the placement.