from matplotlib import rcParams

from objects.shape_map import I1, I2, I3, I4, I5, V3, V5, L4, L5, Z4, Z5, O4, T4, T5, N, P, W, U, F, X, Y
from objects.player import Player
from objects.board import Board
from objects.game import Game
from strategies.user import  user_player
from strategies.greedy import greedy_player
from strategies.minimax import minimax_player
from strategies.random_player import random_player

rcParams['figure.figsize'] = (6, 6)
rcParams['figure.dpi'] = 150


class Blokus(Game):

    def winner(self):
        moves = [p.possible_moves(p.pieces, self) for p in self.players]
        if False in [mv == [] for mv in moves]:
            return "None"
        else:
            cand = [(p.score, p.name) for p in self.players]
            return sorted(cand, reverse=True)[0][1]

    def valid_move(self, player, move):
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


# GLOBAL VARIABLES:
All_Shapes = [I1(), I2(), I3(), I4(), I5(),
              V3(), L4(), Z4(), O4(), L5(),
              T5(), V5(), N(), Z5(), T4(),
              P(), W(), U(), F(), X(), Y()]


a_weights = [2, 1]
b_weights = [1, 2]
minimax_weights = [2, 1, 5, 1, 1]

first = Player("A", "Computer_Red", greedy_player, a_weights)
second = Player("B", "Computer_Blue", user_player, b_weights)
third = Player("C", "Computer_Green", minimax_player, minimax_weights)
fourth = Player("D", "Computer_Yellow", random_player, a_weights)

standard_size = Board(20, 20, "_")

ordering = [first, second, third, fourth]
# random.shuffle(ordering)
user_blokus = Blokus(ordering, standard_size, All_Shapes)

user_blokus.board.print_board(num=user_blokus.rounds, fancy=True)
user_blokus.play()
user_blokus.board.print_board(num=user_blokus.rounds, fancy=True)

while user_blokus.winner() == "None":
    user_blokus.play()
    user_blokus.board.print_board(num=user_blokus.rounds, fancy=True)
    for p in user_blokus.players:
        # print(f"{p.name} ( {str(p.score)}) : {str([s.ID for s in p.pieces])}")
        print(f"{p.name} ({str(p.score)})")
    print("=======================================================================")

print("The final scores are...")

by_name = sorted(user_blokus.players, key=lambda player: player.name)

for p in by_name:
    print(f"{p.name} : {str(p.score)}")
