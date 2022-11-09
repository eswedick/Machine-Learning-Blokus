import copy
import numpy as np


# Players play according to a certain strategy,  as
# specified by a function that takes in the current
# state of the game's interface and returns a placement.

class Player:
    def __init__(self, label, name, strategy, weights):
        self.label = label
        self.name = name
        self.pieces = []
        self.corners = set()
        self.strategy = strategy
        self.score = 0
        self.weights = weights

    def add_pieces(self, pieces):
        """
        Gives a player the initial set of pieces.
        """
        self.pieces = pieces

    def start_corner(self, p):
        """
        Gives a player an initial starting corner.
        """
        self.corners = set([p])

    def remove_piece(self, piece):
        """
        Removes a given piece (Shape object) from
        the list of pieces a player has.
        """
        self.pieces = [s for s in self.pieces if s.ID != piece.ID]

    def update_player(self, placement, board):
        """
        Updates the variables that the player is keeping track
        of, e.g. their score and their available corners.
        Placement should be in the form of a Shape object.
        """
        self.score = self.score + placement.size
        for c in placement.corners:
            if board.in_bounds(c) and (not board.overlap([c])):
                self.corners.add(c)

    def possible_moves(self, pieces, game):
        """
        Returns a unique list of placements, i.e. Shape objects
        with a particular flip, orientation, corners, and points.
        It uses a list of pieces (Shape objects) and the game, which includes
        its rules and valid moves, in order to find the placements.
        """

        def check_corners(game):
            """
            Updates the corners of the player, in case the
            corners have been covered by another player's pieces.
            """
            self.corners = set([(i, j) for (i, j) in self.corners if game.board.state[j][i] == game.board.null])

        # Check the corners before proceeding.
        check_corners(game)

        # This list of placements will be updated with valid ones.
        placements = []
        visited = []

        # Loop through every available corner.
        for cr in self.corners:
            # Look through every piece offered. (This will be restricted according
            # to certain algorithms.)
            for sh in pieces:
                # Create a new shape so that the one in the player's
                # list of shapes is not overwritten.
                try_out = copy.deepcopy(sh)
                # Loop over every potential refpt the piece could have.
                for num in range(try_out.size):
                    try_out.create(num, cr)
                    # And every possible flip.
                    for fl in ["h", "None"]:
                        try_out.flip(fl)
                        # And every possible orientation.
                        for rot in [90] * 4:
                            try_out.rotate(rot)
                            candidate = copy.deepcopy(try_out)
                            if game.valid_move(self, candidate.points):
                                if not (set(candidate.points) in visited):
                                    placements.append(candidate)
                                    visited.append(set(candidate.points))

        return placements

    def do_move(self, game, weights):
        """
        Generates a move according to the Player's
        strategy and current state of the board.
        """
        return self.strategy(self, game, weights)


def eval_move(piece, player, game, weights):
    """
    Takes in a single Piece object and a Player object and returns a integer score that
    evaluates how "good" the Piece move is. Defined here because used by both Greedy and Minimax.
    """

    def check_corners(player):
        """
        Updates the corners of the player in the test board (copy), in case the
        corners have been covered by another player's pieces.
        """
        player.corners = set([(i, j) for (i, j) in player.corners if test_board.state[j][i] == game.board.null])

    # get board
    board = game.board
    # create a copy of the players in the game
    test_players = copy.deepcopy(game.players)
    # create a list of the opponents in the game
    opponents = [opponent for opponent in test_players if opponent.label != player.label]
    # create a copy of the board
    test_board = copy.deepcopy(board)
    # update the copy of the board with the Piece placement
    test_board.update(player, piece.points)
    # create a copy of the player currently playing
    test_player = copy.deepcopy(player)
    # update the current player (update corners) with the current Piece placement
    test_player.update_player(piece, test_board)
    # calculate how many corners the current player has
    my_corners = len(test_player.corners)
    # update the corners for all opponents
    list(map(check_corners, opponents))
    # calculate the mean of the corners of the opponents
    opponent_corners = [len(opponent.corners) for opponent in opponents]
    # find the difference between the number of corners the current player has and and the
    # mean number of corners the opponents have
    corner_difference = np.mean([my_corners - opponent_corner for opponent_corner in opponent_corners])
    # return the score = size + difference in the number of corners
    return piece, weights[0] * piece.size + weights[1] * corner_difference
