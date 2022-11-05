import math
import random
import numpy as np
import matplotlib.pyplot as plt
import copy
from matplotlib import rcParams

from shape_map import I1, I2, I3, I4, I5, V3, V5, L4, L5, Z4, Z5, O4, T4, T5, N, P, W, U, F, X, Y
from player import Player
from board import Board
from game import Game

rcParams['figure.figsize'] = (6, 6)
rcParams['figure.dpi'] = 150


# Here we inherit the Game class in order to
# create the Blokus game. Functions like "play" remain
# the same, but "valid_move" and "winner" are overwritten
# according to the rules of Blokus.

class Blokus(Game):
    """
    A class that takes a list of players, e.g. ['A','B','C'],
    and a board and plays moves, keeping track of the number
    of rounds that have been played.
    """

    def winner(self):
        """
        Checks the conditions of the game
        to see if the game has been won yet
        and returns "None" if the game has
        not been won, and the name of the
        player if it has been won.
        """

        moves = [p.possible_moves(p.pieces, self) for p in self.players]
        if False in [mv == [] for mv in moves]:
            return "None"
        else:
            cand = [(p.score, p.name) for p in self.players]
            return sorted(cand, reverse=True)[0][1]

    def valid_move(self, player, move):
        """
        Uses functions from the board to see whether
        a player's proposed move is valid.
        """
        if self.rounds < len(self.players):
            if ((False in [self.board.in_bounds(pt) for pt in move])
                    or self.board.overlap(move)
                    or not (True in [(pt in player.corners) for pt in move])):
                return False
            else:
                return True

        elif ((False in [self.board.in_bounds(pt) for pt in move])
              or self.board.overlap(move)
              or self.board.adj(player, move)
              or not self.board.corner(player, move)):
            return False

        else:
            return True


# Algorithms
# Here we implement three different algorithms which can be used as a Player's strategy.
# The first one is a naive Random strategy.
# The second is a Greedy algorithm.
# The third is a Minimax algorithm.


# GLOBAL VARIABLES:

All_Shapes = [I1(), I2(), I3(), I4(), I5(), \
              V3(), L4(), Z4(), O4(), L5(), \
              T5(), V5(), N(), Z5(), T4(), \
              P(), W(), U(), F(), X(), Y()]

All_Degrees = [0, 90, 180, 270]

All_Flip = ['h', "None"]


# THE RANDOM PLAYER
# The Random algorithm randomly chooses a Shape and then randomly
# chooses among its possible placements. If no placements are available
# it chooses a different Shape, randomly.

def random_player(player, game):
    """
    Takes in a Player object and Game object and returns a placement
    in the form of a single piece with a proper flip, orientation, corners,
    and points. If no placement can be made function should return None.
    """
    shape_options = [p for p in player.pieces]

    while len(shape_options) > 0:
        piece = random.choice(shape_options)
        possibles = player.possible_moves([piece], game)

        # if there are not possible placements for that piece,
        # remove the piece from out list of pieces
        if possibles:
            return random.choice(possibles)

        else:
            shape_options.remove(piece)

    # if the while loop finishes without returning a possible move,
    # there must be no possible moves left, return None
    return None


# THE GREEDY PLAYER

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
    map(check_corners, opponents)
    # calculate the mean of the corners of the opponents
    opponent_corners = [len(opponent.corners) for opponent in opponents]
    # find the difference between the number of corners the current player has and and the 
    # mean number of corners the opponents have
    corner_difference = np.mean([my_corners - opponent_corner for opponent_corner in opponent_corners])
    # return the score = size + difference in the number of corners
    return (piece, weights[0] * piece.size + weights[1] * corner_difference)


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
        # for each piece, calculate all possible placements, and for each placement, calculate the score
        # of the move; add (move, score) to the list of final moves
        for piece in shape_options:
            # calculate all possible placements for the current piece
            possibles = player.possible_moves([piece], game)
            # if there are possible placements for the current piece:
            if possibles != []:
                def map_eval(piece):
                    return eval_move(piece, player, game, weights)

                # calculate score for each move and store it in a temporary list
                tmp = map(map_eval, possibles)
                # add all the elements in the temporary list in the final moves lsit
                final_moves.extend(tmp)
            # if there are no possible placements for the current piece:
            else:
                # remove the piece from the list of pieces
                shape_options.remove(piece)

        # create score list that contains all Piece placements, sorted by their score        
        by_score = sorted(final_moves, key=lambda move: move[1], reverse=True)
        # if the score list contains Piece placements (objects), return the highest scoring Piece placement
        if len(by_score) > 0:
            return by_score[0][0]
        # else, return None (no Piece placement)
        else:
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

# THE MINIMAX PLAYER
# weights[0] determines how important size of a piece is
# weights[1] determines how important maximizing the difference of my corners and opponent corners
# weights[2] decides how many of the best placements we choose to look ahead with
# weights[3] decides how important the score of the second move is
# weights[4] decides how important the score of the first move is

def minimax_player(player, game, weights):
    # takes in a player and a board, and updates the player's corners depending on the state of the board
    def check_corners(player, board):
        """
        Updates the corners of the player in the test board (copy), in case the
        corners have been covered by another player's pieces.
        """
        player.corners = set([(i, j) for (i, j) in player.corners if board.state[j][i] == game.board.null])

    # create a copy of the player's pieces
    shape_options = [p for p in player.pieces]
    # determine all possible moves
    possibles = player.possible_moves(shape_options, game)
    final_choices = []
    # if there are possible moves:
    if possibles:
        # function for evaluating moves (for mapping purposes)
        def eval_map(piece):
            return eval_move(piece, player, game, weights)

        # evaluate every possible move
        candidate_moves = map(eval_map, possibles)
        # create list of tuples (piece, score), sorted by score
        by_score = sorted(candidate_moves, key=lambda move: move[1], reverse=True)

        # take at most the n highest scoring moves
        if len(by_score) > weights[2]:
            top_choices = by_score[:weights[2]]
        else:
            top_choices = by_score

        for (piece, score) in top_choices:
            # create a copy of the game
            game_copy = copy.deepcopy(game)
            # get board from the game copy (we will be playing on this board)
            board = game_copy.board
            # create a copy of the players in the game
            test_players = copy.deepcopy(game.players)
            # create a list of the opponents in the game
            opponents = [opponent for opponent in test_players if opponent.label != player.label]
            # create a copy of the player currently playing
            test_player = copy.deepcopy(player)
            # update the copy of the board with the Piece placement
            board.update(test_player, piece.points)
            # update the current player (update corners) with the current Piece placement
            test_player.update_player(piece, board)

            # update the corners for all opponents 
            def check_cor_map(opponent):
                return check_corners(opponent, board)

            map(check_cor_map, opponents)

            # create a copy of the pieces that the current player has
            piece_copies = copy.deepcopy(shape_options)
            # remove the Piece that was just placed on the board
            piece_copies = [p for p in piece_copies if p.ID != piece.ID]

            # OPPONENTS' TURN TO PLACE PIECE

            # for each opponent:
            for opponent in opponents:
                # create a list of tuples (size, piece) for the opponent, sorted by size
                by_size_op = sorted([(shape.size, shape) for shape in opponent.pieces], reverse=True)
                # extract pieces from by_size_op list
                by_size_op_pieces = [piece_by_size[1] for piece_by_size in by_size_op]
                # create a list of all the opponent's possible moves
                possibles_op = opponent.possible_moves(by_size_op_pieces, game_copy)
                # if there are possible moves left:
                if possibles_op != []:
                    # create an empty list to store evaluations of possible moves
                    final_moves_op = []
                    # evaluate every possible move; store in final_moves_op
                    for poss in possibles_op:
                        final_moves_op.append(eval_move(poss, opponent, game_copy, weights))
                    # create list of tuples (piece, score), sorted by score
                    by_score_op = sorted(final_moves_op, key=lambda move: move[1], reverse=True)
                    # take the highest scoring move
                    best_move = by_score_op[0][0]
                    # update the board with the highest scoring move
                    board.update(opponent, best_move.points)
                    # create a list of the other opponents
                    # other_opponents = [enemy for enemy in game_copy.players if enemy.label != opponent.label]
                    # update the corners of the other opponents
                    map(check_cor_map, test_players)
                # if there are no possible moves left for the opponent, return the piece
                else:
                    return piece

            # BOARD HAS BEEN UPDATED; OPPONENTS HAVE FINISHED THEIR TURNS

            # create list of all possible moves
            possibles_2 = test_player.possible_moves(piece_copies, game_copy)
            # if there are possible moves left:
            if possibles_2 != []:
                final_moves_2 = []
                # evaluate each move; append to list of tuples (piece, score)
                for possible in possibles_2:
                    final_moves_2.append(eval_move(possible, test_player, game_copy, weights))
                # create a list of tuples (piece, score), sorted by score
                by_score_2 = sorted(final_moves_2, key=lambda move: move[1], reverse=True)
                # calculate the best score for each initial piece (can be weighted differently)
                best_score = weights[3] * by_score_2[0][1] + weights[4] * score
                # append initial piece plus potential score to final_choices
                final_choices.append((piece, best_score))
            # if there are no possible moves left, add the first played piece to the final_choices list
            else:
                final_choices.append((piece, score))

        # sort the list of final_choices by score
        final_choices = sorted(final_choices, key=lambda move: move[1], reverse=True)
        # return the highest scoring move
        return final_choices[0][0]

    # if there are no possible moves left, return None
    else:
        return None


# For a particular placement $i$, we assign weights $W_0$, $W_1$, $W_2$, $W_3$, $W_4$ such that:
# 
# $ size_{j,i} $ = size of $j$th placement
# 
# $ cor_{j,my} $ = number of my corners at $j$th placement
# 
# $ cor_{j,opp} $ = number of opponent's corners at $j$th placement
# 
# $ n_{opp} $ = number of opponents
# 
# $ W_2 $ = number of best placements from initial move that are chosen to run Minimax
# 
# then:
# 
# $ MinimaxEval_{W_2, i} = W_4 \left [ size_{1,i} W_1 + \frac{\sum{(cor_{1,my} - cor_{1,opp})}}{n_{opp}} W_2 \right ]
# + W_3 \left [ size_{2,i} W_1 + \frac{\sum{(cor_{2,my} - cor_{2,opp})}}{n_{opp}} W_2 \right ]$
# 
# This returns a score for the placement.

# USER INPUT
def user_player(player, game):
    """
    User Player should input 2 things: piece and coordinate for the refpt.
    """

    def get_input():
        s = True
        while s:
            try:
                s = map(int, raw_input("Please input a reference point: ").split())
                while len(s) != 2:
                    s = map(int, raw_input("Please input a valid reference point (x,y): ").split())
                else:
                    return s
            except:
                print "Invalid coordinate input."
                s = True

    if not player.pieces:
        print "\nSorry! You can't play any more moves since you have placed all your pieces.\n"
        return None

    possibles = player.possible_moves(player.pieces, game)
    options = []

    if not possibles:
        print "\nSorry! There are no more possible moves for you.\n"
        return None

    while not options:
        shape = (raw_input("Choose a shape: ")).upper().strip()
        while not (shape in [p.ID for p in player.pieces]):
            print ("\nPlease enter a valid piece ID. Remember these are the pieces available to you: "
                   + str([p.ID for p in player.pieces]) + "\n")
            shape = (raw_input("Choose a shape: ")).upper()

        refpt = get_input()
        while not game.board.in_bounds((refpt[0], refpt[1])):
            print ("\nPlease enter a point that is in bounds. Remember the dimensions of the board: " + str(
                game.board.size) + "\n")
            refpt = get_input()
        while game.board.overlap([(refpt[0], refpt[1])]):
            print "\nIt appears the point you chose overlaps with another piece! Please choose an empty square.\n"
            refpt = get_input()

        for piece in possibles:
            if piece.ID == shape and piece.points[0][0] == refpt[0] and piece.points[0][1] == refpt[1]:
                options.append(piece)

        if not options:
            print "\nOh no! It appears you have chosen an invalid shape and reference point combination. Please try again!\n"

    if len(options) == 1:
        return options[0]

    if len(options) > 1:
        print "\nIt appears you have multiple placement options! Please choose one.\n"
        for i in xrange(len(options)):
            print (str(i) + str(" : ") + str(options[i].points) + "\n")
        pick = int(raw_input("Your pick: "))
        while not (pick in xrange(len(options))):
            print "\nOops! Try a valid pick again.\n"
            for i in xrange(len(options)):
                print (str(i) + str(" : ") + str(options[i].points) + "\n")
            pick = int(raw_input("Your pick: "))
        return options[pick]


# PLAYING INSTRUCTIONS
print "\n \n Welcome to Blokus! \n \n \n Blokus is a geometrically abstract, strategy board game. It can be a two- or four-player game. Each player has 21 pieces of a different color. The two-player version of the board has 14 rows and 14 columns. \n \n You will be playing a two-player version against an algorithm of your choice: Random, Greedy, or Minimax. In case you need to review the rules of Blokus, please follow this link: http://en.wikipedia.org/wiki/Blokus. \n \n This is how choosing a move is going to work: after every turn, we will display the current state of the board, as well as the scores of each player and the pieces available to you. We have provided you with a map of the names of the pieces, as well as their reference points, denoted by red dots. When you would like to place a piece, we will prompt you for the name of the piece and the coordinate (column, row) of the reference point. If multiple placements are possible, we will let you choose which one you would like to play. \n \n Good luck! \n \n"

# img = Image.open('Images/Blokus_Tiles.png')
# img.show()

# print "Please choose an algorithm to play against: \n A. Random \n B. Greedy \n C. Minimax \n"

# choice = raw_input().upper()

# while not (choice in ["A", "B", "C"]):
#    choice = raw_input("\n Please choose a valid algorithm: \n").upper()
#
# if choice == "A":
#    computer = Player("A", "Computer", Random_Player)
# elif choice == "B":
#    computer = Greedy("A", "Computer", Greedy_Player, [2, 1, 5, 1, 1])
# else:
#    computer = Greedy("A", "Computer", Minimax_Player, [2, 1, 5, 1, 1])

first = Player("A", "Computer_A", random_player)
second = Player("B", "Computer_B", random_player)
third = Player("C", "Computer_C", random_player)
fourth = Player("D", "Computer_D", user_player)

standard_size = Board(14, 14, "_")

ordering = [first, second, third, fourth]
random.shuffle(ordering)
user_blokus = Blokus(ordering, standard_size, All_Shapes)

# <codecell>

user_blokus.board.print_board(num=user_blokus.rounds, fancy=True)
print "\n"
user_blokus.play()
user_blokus.board.print_board(num=user_blokus.rounds, fancy=True)
print "\n"

while user_blokus.winner() == "None":
    user_blokus.play()
    user_blokus.board.print_board(num=user_blokus.rounds, fancy=True)
    print "\n"
    for p in user_blokus.players:
        print p.name + " (" + str(p.score) + ") : " + str([s.ID for s in p.pieces])
        print
    print "======================================================================="

print
user_blokus.board.print_board()
print
user_blokus.play()

print "The final scores are..."

by_name = sorted(user_blokus.players, key=lambda player: player.name)

for p in by_name:
    print p.name + " : " + str(p.score)
