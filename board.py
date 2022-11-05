from matplotlib import pyplot as plt


class Board:
    """
    Creates a board that has n rows and
    m columns with an empty space represented
    by a character string according to null of
    character length one.
    """

    def __init__(self, n, m, null):
        self.size = (n, m)
        self.null = null
        self.empty = [[self.null] * m for i in xrange(n)]
        self.state = self.empty

    def update(self, player, move):
        """
        Takes in a Player object and a move as a
        list of integer tuples that represent the piece.
        """
        for row in xrange(len(self.state)):
            for col in xrange(len(self.state[1])):
                if (col, row) in move:
                    self.state[row][col] = player.label

    def in_bounds(self, point):
        """
        Takes in a tuple and checks if it is in the bounds of
        the board.
        """
        return (0 <= point[0] <= (self.size[1] - 1)) & (0 <= point[1] <= (self.size[0] - 1))

    def overlap(self, move):
        """
        Returns a boolean for whether a move is overlapping
        any pieces that have already been placed on the board.
        """
        if False in [(self.state[j][i] == self.null) for (i, j) in move]:
            return (True)
        else:
            return (False)

    def corner(self, player, move):
        """
        Note: ONLY once a move has been checked for adjacency, this
        function returns a boolean; whether the move is cornering
        any pieces of the player proposing the move.
        """
        validates = []

        for (i, j) in move:
            if self.in_bounds((j + 1, i + 1)):
                validates.append((self.state[j + 1][i + 1] == player.label))

            if self.in_bounds((j - 1, i - 1)):
                validates.append((self.state[j - 1][i - 1] == player.label))

            if self.in_bounds((j - 1, i + 1)):
                validates.append((self.state[j - 1][i + 1] == player.label))

            if self.in_bounds((j + 1, i - 1)):
                validates.append((self.state[j + 1][i - 1] == player.label))

        if True in validates:
            return True
        else:
            return False

    def adj(self, player, move):
        """
        Checks if a move is adjacent to any squares on
        the board which are occupied by the player
        proposing the move and returns a boolean.
        """
        validates = []

        for (i, j) in move:
            if self.in_bounds((j, i + 1)):
                validates.append((self.state[j][i + 1] == player.label))

            if self.in_bounds((j, i - 1)):
                validates.append((self.state[j][i - 1] == player.label))

            if self.in_bounds((j - 1, i)):
                validates.append((self.state[j - 1][i] == player.label))

            if self.in_bounds((j + 1, i)):
                validates.append((self.state[j + 1][i] == player.label))

        if True in validates:
            return True
        else:
            return False

    def print_board(self, num=None, fancy=False):
        if not fancy:
            print_board(self.state)
        else:
            fancy_board(self, num)


def print_board(board):
    n = 2
    assert (len(set([len(board[i]) for i in xrange(len(board))])) == 1)
    print ' ' * n,
    for i in range(len(board[1])):
        print str(i) + ' ' * (n - len(str(i))),
    print
    for i, row in enumerate(board):
        print str(i) + ' ' * (n - len(str(i))), (' ' * n).join(row)


# This function uses MatplotLib to create a fancy image
# of the board that opens in a separate window.

def fancy_board(board, num):
    a_points = []
    b_points = []

    for y in enumerate(board.state):
        for x in enumerate(y[1]):
            if x[1] == "A":
                a_points.append((x[0], (board.size[0] - 1) - y[0]))
            if x[1] == "B":
                b_points.append((x[0], (board.size[0] - 1) - y[0]))

    # fig = plt.figure(frameon=False)
    ax = plt.subplot(111, xlim=(0, board.size[0]), ylim=(0, board.size[1]))

    for i in xrange(board.size[0] + 1):
        for j in xrange(board.size[1] + 1):
            polygon = plt.Polygon([[i, j], [i + 1, j], [i + 1, j + 1], [i, j + 1], [i, j]])
            if (i, j) in a_points:
                polygon.set_facecolor('red')
                ax.add_patch(polygon)
            elif (i, j) in b_points:
                polygon.set_facecolor('blue')
                ax.add_patch(polygon)
            else:
                polygon.set_facecolor('lightgrey')
                ax.add_patch(polygon)

    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_formatter(plt.NullFormatter())
        axis.set_major_locator(plt.NullLocator())

    plt.savefig("random" + str(num) + ".png")
    plt.show()
    # return ax
