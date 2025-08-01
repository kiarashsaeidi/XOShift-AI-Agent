from typing import List, Optional, Tuple, Dict
import collections

# --- Heuristic Evaluation Function ---
# This is the main function you will call from your Minimax algorithm
# when you reach the maximum search depth (i.e., when depth == 0).


def _score_opponent_threats(board: List[List[Optional[str]]], player_symbol: str, opponent_symbol: str, n: int, WEIGHTS: Dict) -> int:
    """
    Scores the danger posed by the opponent.
    """
    all_lines = get_all_lines(board)
    score = 0
    for line in all_lines:
        opponent_count = line.count(opponent_symbol)
        empty_count = line.count(None)
        if opponent_count + empty_count == n:  # Not blocked by us
            if opponent_count == n - 1:
                score += WEIGHTS["THREE_IN_LINE"]  # Opponent is 1 move away from win
            elif opponent_count == n - 2:
                score += WEIGHTS["TWO_IN_LINE"]
    return score

def evaluate_board(board: List[List[Optional[str]]], my_symbol: str, opponent_symbol: str) -> int:
    """
    Calculates the heuristic value of a given board state.
    A positive score favors `my_symbol`, while a negative score favors `opponent_symbol`.
    """
    # The core of a good heuristic is to balance offense and defense.
    # We do this by scoring our position and subtracting the opponent's score.

    if check_win(board, my_symbol):
        return 1000000
    if check_win(board, opponent_symbol):
        return -1000000
    
    my_score = score_player_position(board, my_symbol, opponent_symbol)
    opponent_score = score_player_position(board, opponent_symbol, my_symbol)

    return my_score - opponent_score


def score_player_position(board: List[List[Optional[str]]], player_symbol: str, opponent_symbol: str) -> int:
    """
    Calculates a score for a single player based on various strategic factors.
    """
    # --- TUNABLE WEIGHTS ---
    # Adjust these values to change the agent's behavior and priorities.
    WEIGHTS = {
        "WIN": 100000,
        "FORK": 5000,
        "THREE_IN_LINE": 200, # For 4x4 or 5x5 boards
        "TWO_IN_LINE": 50,
        "CENTER_CONTROL": 15, # <<< NEW: Heuristic for controlling the center
        "CORNER_CONTROL": 10, # Adjusted weight to be less than center
        "MOBILITY": 1
    }

    n = len(board)
    total_score = 0

    # --- 1. Terminal State Check (Highest Priority) ---
    if check_win(board, player_symbol):
        return WEIGHTS["WIN"]

    # --- 2. Offensive and Positional Scoring ---
    all_lines = get_all_lines(board)
    
    # Score threats (N-in-a-row)
    threat_score, potential_fork_lines = _score_threats(all_lines, player_symbol, n, WEIGHTS)
    total_score += threat_score

    # Score forks
    total_score += _score_forks(potential_fork_lines, WEIGHTS)

    # Score corner control
    total_score += _score_corners(board, player_symbol, n, WEIGHTS)
    
    # <<< NEW: Score center control >>>
    total_score += _score_center_control(board, player_symbol, n, WEIGHTS)

    total_score -= _score_opponent_threats(board, player_symbol, opponent_symbol, n, WEIGHTS)

    
    # Score mobility (number of available moves)
    # total_score += len(get_all_valid_moves(board, player_symbol)) * WEIGHTS["MOBILITY"]

    return total_score


def _score_threats(all_lines: List[List[Optional[str]]], player_symbol: str, n: int, WEIGHTS: Dict) -> Tuple[int, int]:
    """Scores threats like two-in-a-row or three-in-a-row."""
    score = 0
    potential_fork_lines = 0
    
    for line in all_lines:
        player_pieces = line.count(player_symbol)
        empty_cells = line.count(None)

        if player_pieces + empty_cells == n:  # Line is not blocked by the opponent
            if player_pieces == n - 1:
                score += WEIGHTS["THREE_IN_LINE"] 
                potential_fork_lines += 1
            elif player_pieces == n - 2:
                score += WEIGHTS["TWO_IN_LINE"]
                potential_fork_lines += 1
    
    return score, potential_fork_lines


def _score_forks(potential_fork_lines: int, WEIGHTS: Dict) -> int:
    """Scores a fork opportunity (2 or more simultaneous threats)."""
    if potential_fork_lines >= 2:
        return WEIGHTS["FORK"]
    return 0


def _score_corners(board: List[List[Optional[str]]], player_symbol: str, n: int, WEIGHTS: Dict) -> int:
    """Scores having control of the corner positions."""
    score = 0
    corners = [(0, 0), (0, n - 1), (n - 1, 0), (n - 1, n - 1)]
    for r, c in corners:
        if board[r][c] == player_symbol:
            score += WEIGHTS["CORNER_CONTROL"]
    return score


def _score_center_control(board: List[List[Optional[str]]], player_symbol: str, n: int, WEIGHTS: Dict) -> int:
    """Scores having control of the center cell(s)."""
    score = 0
    # For odd-sized boards (3x3, 5x5), there is one center cell.
    if n % 2 == 1:
        center_idx = n // 2
        if board[center_idx][center_idx] == player_symbol:
            score += WEIGHTS["CENTER_CONTROL"]
    # For even-sized boards (4x4), there is a 2x2 block of center cells.
    else:
        center1 = n // 2 - 1
        center2 = n // 2
        center_cells = [(center1, center1), (center1, center2), (center2, center1), (center2, center2)]
        for r, c in center_cells:
            if board[r][c] == player_symbol:
                score += WEIGHTS["CENTER_CONTROL"]
    return score


# --- Utility Functions ---
# These helpers are needed for the heuristic to work.

def get_all_lines(board: List[List[Optional[str]]]) -> List[List[Optional[str]]]:
    """Returns a list of all rows, columns, and diagonals from the board."""
    n = len(board)
    lines = []
    lines.extend(board) # Rows
    for c in range(n): # Columns
        lines.append([board[r][c] for r in range(n)])
    lines.append([board[i][i] for i in range(n)]) # Main Diagonal
    lines.append([board[i][n - 1 - i] for i in range(n)]) # Anti-Diagonal
    return lines

def check_win(board: List[List[Optional[str]]], player_symbol: str) -> bool:
    """(Placeholder) Checks if the given player has won the game."""
    n = len(board)
    for line in get_all_lines(board):
        if all(cell == player_symbol for cell in line):
            return True
    return False
