import copy
from typing import List, Optional, Tuple
from agent_utils import get_all_valid_moves


# --- Helper functions for move simulation and win detection ---

def _apply_move_to_board(board: List[List[Optional[str]]], move: Tuple[int, int, int, int], player_symbol: str) -> List[List[Optional[str]]]:
    """
    Applies a move to a given board state and returns the new board.
    This is used for simulating moves within the minimax search without altering the actual game state.
    """
    src_row, src_col, tgt_row, tgt_col = move
    new_board = copy.deepcopy(board)  # Work on a deep copy to avoid side effects

    # Perform the shift operation
    if src_row == tgt_row:  # Horizontal shift
        if tgt_col < src_col:
            for col_idx in range(src_col, tgt_col, -1):
                new_board[src_row][col_idx] = new_board[src_row][col_idx - 1]
        else:
            for col_idx in range(src_col, tgt_col):
                new_board[src_row][col_idx] = new_board[src_row][col_idx + 1]
    else:  # Vertical shift
        if tgt_row < src_row:
            for row_idx in range(src_row, tgt_row, -1):
                new_board[row_idx][src_col] = new_board[row_idx - 1][src_col]
        else:
            for row_idx in range(src_row, tgt_row):
                new_board[row_idx][src_col] = new_board[row_idx + 1][src_col]

    new_board[tgt_row][tgt_col] = player_symbol
    return new_board

def _check_winner_on_board(board: List[List[Optional[str]]]) -> Optional[str]:
    """Checks if there is a winner on the given board state. Returns 'X', 'O', or None."""
    n = len(board)
    players = ['X', 'O']

    for symbol in players:
        # Check rows for a win
        for r in range(n):
            if all(board[r][c] == symbol for c in range(n)):
                return symbol
        # Check columns for a win
        for c in range(n):
            if all(board[r][c] == symbol for r in range(n)):
                return symbol
        # Check main diagonal (top-left to bottom-right)
        if all(board[i][i] == symbol for i in range(n)):
            return symbol
        # Check anti-diagonal (top-right to bottom-left)
        if all(board[i][n - 1 - i] == symbol for i in range(n)):
            return symbol
    return None

def _evaluate_line(line: List[Optional[str]], player_symbol: str) -> int:
    opp_symbol = 'O' if player_symbol == 'X' else 'X'
    my_count = line.count(player_symbol)
    opp_count = line.count(opp_symbol)
    empty_count = line.count(None)
    n = len(line)

    if my_count == n - 1 and opp_count == 0:
        return 1000
    elif opp_count == n - 1 and my_count == 0:
        return -1000
    elif my_count > 0 and opp_count == 0:
        return my_count ** 2 + empty_count * 2  # Bonus for empty cells
    elif opp_count > 0 and my_count == 0:
        return -(opp_count ** 2) - empty_count * 2
    elif my_count > 0 and opp_count > 0:
        return (my_count - opp_count) * 5
    return empty_count  # Small score for empty lines

# --- Heuristic and Minimax Functions ---

def heuristic(board: List[List[Optional[str]]], player_symbol: str) -> int:
    """
    Calculates the heuristic value of a board state.
    A positive score is good for our agent, while a negative score is good for the opponent.
    The heuristic sums the scores of all rows, columns, and diagonals.
    """
    score = 0
    n = len(board)

    # Evaluate all rows
    for r in range(n):
        score += _evaluate_line(board[r], player_symbol)

    # Evaluate all columns
    for c in range(n):
        col = [board[r][c] for r in range(n)]
        score += _evaluate_line(col, player_symbol)

    # Evaluate the two main diagonals
    main_diag = [board[i][i] for i in range(n)]
    anti_diag = [board[i][n - 1 - i] for i in range(n)]
    score += _evaluate_line(main_diag, player_symbol)
    score += _evaluate_line(anti_diag, player_symbol)

    center = n // 2
    if n % 2 == 1:  # Odd-sized board (e.g., 3x3, 5x5)
        if board[center][center] == player_symbol:
            score += 10
        elif board[center][center] == ('O' if player_symbol == 'X' else 'X'):
            score -= 10
    else:  # Even-sized board (e.g., 4x4)
        for r in [center - 1, center]:
            for c in [center - 1, center]:
                if board[r][c] == player_symbol:
                    score += 5
                elif board[r][c] == ('O' if player_symbol == 'X' else 'X'):
                    score -= 5
    
    return score

def minimax(board: List[List[Optional[str]]], depth: int, alpha: float, beta: float, maximizing_player: bool, player_symbol: str) -> Tuple[Optional[Tuple[int, int, int, int]], int]:
    """
    Minimax algorithm with alpha-beta pruning to find the best move.
    Returns a tuple containing the best move and its evaluated score.
    """
    winner = _check_winner_on_board(board)
    if winner:
        # Base case: A player has won.
        score = float('inf') if winner == player_symbol else float('-inf')
        return None, score
    
    # The player whose turn it is to move
    current_turn_player = player_symbol if maximizing_player else ('O' if player_symbol == 'X' else 'X')
    valid_moves = get_all_valid_moves(board, current_turn_player)
    
    if not valid_moves:
        return None, 0  # Draw
    elif depth == 0:
        return None, heuristic(board, player_symbol)

    if maximizing_player:
        max_eval = float('-inf')
        best_move = valid_moves[0]  # Default to the first available move
        for move in valid_moves:
            temp_board = _apply_move_to_board(board, move, player_symbol)
            _, current_eval = minimax(temp_board, depth - 1, alpha, beta, False, player_symbol)
            if current_eval > max_eval:
                max_eval = current_eval
                best_move = move
            alpha = max(alpha, current_eval)
            if beta <= alpha:
                break  # Prune the remaining branches
        return best_move, max_eval
    else:  # Minimizing player
        min_eval = float('inf')
        best_move = valid_moves[0] # The minimizer's specific move isn't needed, just its score
        opp_symbol = 'O' if player_symbol == 'X' else 'X'
        for move in valid_moves:
            temp_board = _apply_move_to_board(board, move, opp_symbol)
            _, current_eval = minimax(temp_board, depth - 1, alpha, beta, True, player_symbol)
            if current_eval < min_eval:
                min_eval = current_eval
            beta = min(beta, current_eval)
            if beta <= alpha:
                break  # Prune the remaining branches
        return best_move, min_eval

# --- Main Agent Function ---

def agent_move(board: List[List[Optional[str]]], player_symbol: str) -> Tuple[int, int, int, int]:
    """
    The main entry point for the agent. It determines the best move by calling the minimax algorithm.
    """
    valid_moves = get_all_valid_moves(board, player_symbol)
    if not valid_moves:
        # This case is reached if no valid moves are possible.
        return 0, 0, 0, 0

    # Adjust search depth based on board size to manage complexity and avoid timeouts.
    # A 5x5 board has a much larger branching factor.
    board_size = len(board)
    if board_size == 3:
        search_depth = 5
    elif board_size == 4:
        search_depth = 3
    else:  # 5x5
        search_depth = 2

    # Start the minimax search from the current state for the maximizing player (our agent).
    chosen_move, score = minimax(board, 2, float('-inf'), float('inf'), True, player_symbol)

    # Fallback in case minimax doesn't return a move (shouldn't happen if valid_moves is not empty).
    return chosen_move if chosen_move else valid_moves[0]
