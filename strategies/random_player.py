import random


# The Random algorithm randomly chooses a Shape and then randomly
# chooses among its possible placements. If no placements are available
# it chooses a different Shape, randomly.

def random_player(player, game, weights):
    """
    Takes in a Player object and Game object and returns a placement
    in the form of a single piece with a proper flip, orientation, corners,
    and points. If no placement can be made function should return None.
    """
    shape_options = [p for p in player.pieces]

    while len(shape_options) > 0:
        piece = random.choice(shape_options)
        possibles = player.possible_moves([piece], game)

        # if there are no possible placements for that piece,
        # remove the piece from out list of pieces
        if possibles:
            return random.choice(possibles)

        else:
            shape_options.remove(piece)

    # if the while loop finishes without returning a possible move,
    # there must be no possible moves left, return None
    return None
