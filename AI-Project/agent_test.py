import math
import copy
from typing import List, Optional, Tuple
# It is assumed that this utility is provided by the project environment.
from agent_utils import get_all_valid_moves


# --- Helper Functions for Game Logic ---

def apply_move(board: List[List[Optional[str]]], move: Tuple[int, int, int, int], symbol: str) -> List[List[Optional[str]]]:
    """
    Applies a given move to a copy of the board and returns the new board state.
    This is crucial for the Minimax algorithm to explore future states without
    altering the current game board.
    """
    r1, c1, r2, c2 = move
    new_board = copy.deepcopy(board)
    
    # Place the new piece conceptually at the starting position
    new_board[r1][c1] = symbol

    # Perform the shift operation
    if r1 == r2:  # Horizontal shift
        if c1 < c2:  # Shift left
            for c in range(c1, c2):
                new_board[r1][c] = new_board[r1][c + 1]
        else:  # Shift right
            for c in range(c1, c2, -1):
                new_board[r1][c] = new_board[r1][c - 1]
    elif c1 == c2:  # Vertical shift
        if r1 < r2:  # Shift up
            for r in range(r1, r2):
                new_board[r][c1] = new_board[r + 1][c1]
        else:  # Shift down
            for r in range(r1, r2, -1):
                new_board[r][c1] = new_board[r - 1][c1]
    
    # The piece from the start of the shift lands at the destination
    new_board[r2][c2] = symbol
    
    return new_board


def check_win(board: List[List[Optional[str]]], player_symbol: str) -> bool:
    """
    Checks if the given player has won the game.
    """
    n = len(board)
    # Check rows and columns
    for i in range(n):
        if all(board[i][j] == player_symbol for j in range(n)) or \
           all(board[j][i] == player_symbol for j in range(n)):
            return True
    # Check diagonals
    if all(board[i][i] == player_symbol for i in range(n)) or \
       all(board[i][n - 1 - i] == player_symbol for i in range(n)):
        return True
    return False


def is_board_full(board: List[List[Optional[str]]]) -> bool:
    """
    Checks if the board is full (which would result in a draw if no one has won).
    """
    for row in board:
        if None in row:
            return False
    return True

# --- Minimax Algorithm Implementation ---

def minimax(board: List[List[Optional[str]]], depth: int,alpha: float, beta: float, is_maximizing: bool, player_symbol: str, opponent_symbol: str) -> int:
    """
    The core Minimax function. It recursively explores the game tree to find the
    best possible score from the current board state.
    """
    WIN_SCORE = 100
    # Check for terminal states (win, loss, draw)
    if check_win(board, player_symbol):
        return WIN_SCORE  # AI wins
    if check_win(board, opponent_symbol):
        return -WIN_SCORE # Opponent wins
    if is_board_full(board):
        return 0  # Draw
    
    # If we reach the maximum search depth, we stop and return a neutral score
    if depth == 0:
        return 0

    if is_maximizing:
        best_score = -math.inf
        # The maximizer is our AI
        valid_moves = get_all_valid_moves(board, player_symbol)
        for move in valid_moves:
            # Create a new board state by applying the move
            new_board = apply_move(board, move, player_symbol)
            score = minimax(new_board, depth - 1,alpha, beta, False, player_symbol, opponent_symbol)
            best_score = max(score, best_score)
            alpha = max(alpha, score)

            if beta <= alpha:   break
        return best_score
    else:  # Minimizing player
        best_score = math.inf
        # The minimizer is the opponent
        valid_moves = get_all_valid_moves(board, opponent_symbol)
        for move in valid_moves:
            # Create a new board state by applying the move
            new_board = apply_move(board, move, opponent_symbol)
            score = minimax(new_board, depth - 1,alpha, beta, True, player_symbol, opponent_symbol)
            best_score = min(score, best_score)

            beta = min(beta, score)

            if beta <= alpha: break
        return best_score


# --- Main Agent Function ---

def agent_move(board: List[List[Optional[str]]], player_symbol: str) -> Tuple[int, int, int, int]:
    """
    This is the main function that the game calls to get the agent's move.
    It uses the Minimax algorithm to determine the best move.
    """
    valid_moves = get_all_valid_moves(board, player_symbol)
    
    # Determine the opponent's symbol
    opponent_symbol = 'O' if player_symbol == 'X' else 'X'
    
    best_score = -math.inf
    chosen_move = None

    # If there are no valid moves, return a default value
    if not valid_moves:
        return 0, 0, 0, 0
    
    # Set a depth for the search. Higher depth = stronger but slower AI.
    # A depth of 2 or 3 is a good starting point for a 3x3 board.
    search_depth = 2

    # Loop through all possible moves
    for move in valid_moves:
        # For each move, simulate it and call minimax to get its score
        new_board = apply_move(board, move, player_symbol)
        
        # We call minimax for the opponent's turn (minimizing player)
        score = minimax(new_board, search_depth,-math.inf,math.inf,False, player_symbol, opponent_symbol)
        
        # If this move has a better score than any we've seen, update our best move
        if score > best_score:
            best_score = score
            chosen_move = move

    if chosen_move is None:
        chosen_move = valid_moves[0]
        
    return chosen_move
