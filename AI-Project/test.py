from agent2 import apply_move
from eval3 import print_board


board = [['O', 'O', 'X'], ['X', 'X', 'O'], [None, 'X', None]]

new_board = apply_move(board, (2,2,2,0),'O')

print_board(new_board)


