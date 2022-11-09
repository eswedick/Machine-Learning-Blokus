import copy
import time
from objects.player import eval_move

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
        candidate_moves = list(map(eval_map, possibles))
        # create list of tuples (piece, score), sorted by score
        by_score = sorted(candidate_moves, key=lambda move: move[1], reverse=True)

        # take at most the n highest scoring moves
        if len(by_score) > weights[2]:
            top_choices = by_score[:weights[2]]
        else:
            top_choices = by_score

        tic = time.perf_counter()
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

            list(map(check_cor_map, opponents))

            # create a copy of the pieces that the current player has
            piece_copies = copy.deepcopy(shape_options)
            # remove the Piece that was just placed on the board
            piece_copies = [p for p in piece_copies if p.ID != piece.ID]

            # OPPONENTS' TURN TO PLACE PIECE

            # for each opponent:
            for opponent in opponents:
                # create a list of tuples (size, piece) for the opponent, sorted by size
                by_size_op = sorted([(shape.size, shape) for shape in opponent.pieces], key=lambda tup: tup[0], reverse=True)
                # extract pieces from by_size_op list
                by_size_op_pieces = [piece_by_size[1] for piece_by_size in by_size_op]
                # create a list of all the opponent's possible moves
                possibles_op = opponent.possible_moves(by_size_op_pieces, game_copy)
                # if there are possible moves left:
                if possibles_op:
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
                    list(map(check_cor_map, test_players))
                # if there are no possible moves left for the opponent, return the piece
                else:
                    return piece

            # BOARD HAS BEEN UPDATED; OPPONENTS HAVE FINISHED THEIR TURNS

            # create list of all possible moves
            possibles_2 = test_player.possible_moves(piece_copies, game_copy)
            # if there are possible moves left:
            if possibles_2:
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

        toc = time.perf_counter()
        print(f"minimax calculation: {toc - tic} seconds")
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
