# USER INPUT
def user_player(player, game, weights):
    """
    User Player should input 2 things: piece and coordinate for the reference pt.
    """

    def get_input():
        s = True
        while s:
            try:
                s = list(map(int, input("Please input a reference point: ").split()))
                while len(s) != 2:
                    s = list(map(int, input("Please input a valid reference point (x,y): ").split()))
                else:
                    return s
            except:
                print("Invalid coordinate input.")
                s = True

    if not player.pieces:
        print("\nSorry! You can't play any more moves since you have placed all your pieces.\n")
        return None

    possibles = player.possible_moves(player.pieces, game)
    options = []

    if not possibles:
        print("\nSorry! There are no more possible moves for you.\n")
        return None

    while not options:
        shape = (input("Choose a shape: ")).upper().strip()
        while not (shape in [p.ID for p in player.pieces]):
            print(("\nPlease enter a valid piece ID. Remember these are the pieces available to you: "
                   + str([p.ID for p in player.pieces]) + "\n"))
            shape = (input("Choose a shape: ")).upper().strip()

        reference_pt = get_input()
        while not game.board.in_bounds((reference_pt[0], reference_pt[1])):
            print(("\nPlease enter a point that is in bounds. Remember the dimensions of the board: " + str(
                game.board.size) + "\n"))
            reference_pt = get_input()
        while game.board.overlap([(reference_pt[0], reference_pt[1])]):
            print("\nIt appears the point you chose overlaps with another piece! Please choose an empty square.\n")
            reference_pt = get_input()

        for piece in possibles:
            if piece.ID == shape and piece.points[0][0] == reference_pt[0] and piece.points[0][1] == reference_pt[1]:
                options.append(piece)

        if not options:
            print("\nOh no! You have chosen an invalid shape and reference point combination. Please try again!\n")

    if len(options) == 1:
        return options[0]

    if len(options) > 1:
        print("\nIt appears you have multiple placement options! Please choose one.\n")
        for i in range(len(options)):
            print((str(i) + str(" : ") + str(options[i].points) + "\n"))

        pick = int(eval(input("Your pick: ")))
        while not (pick in range(len(options))):
            print("\nOops! Try a valid pick again.\n")
            for i in range(len(options)):
                print((str(i) + str(" : ") + str(options[i].points) + "\n"))
            pick = int(eval(input("Your pick: ")))
        return options[pick]