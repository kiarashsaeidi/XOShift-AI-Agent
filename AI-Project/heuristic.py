from typing import List, Optional, Tuple, Dict
import collections

# --- Heuristic Evaluation Function ---
# This is the main function you will call from your Minimax algorithm
# when you reach the maximum search depth (i.e., when depth == 0).

def evaluate_board(board: List[List[Optional[str]]], my_symbol: str, opponent_symbol: str) -> int:
    """
    Calculates the heuristic value of a given board state.
    A positive score favors `my_symbol`, while a negative score favors `opponent_symbol`.
    """
    # The core of a good heuristic is to balance offense and defense.
    # We do this by scoring our position and subtracting the opponent's score.
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
        "CORNER_CONTROL": 25,
        "MOBILITY": 1
    }

    n = len(board)
    total_score = 0

    # --- 1. Terminal State Check (Highest Priority) ---
    if check_win(board, player_symbol):
        return WEIGHTS["WIN"]
    # We don't need a loss check here, as it will be caught when evaluating the opponent.

    # --- 2. Offensive and Positional Scoring ---
    all_lines = get_all_lines(board)
    
    # Score threats (N-in-a-row)
    threat_score, potential_fork_lines = _score_threats(all_lines, player_symbol, n, WEIGHTS)
    total_score += threat_score

    # Score forks
    total_score += _score_forks(potential_fork_lines, WEIGHTS)

    # Score corner control
    total_score += _score_corners(board, player_symbol, n, WEIGHTS)
    
    # Score mobility (number of available moves)
    # This is a good tie-breaker for otherwise equal positions.
    # NOTE: This can be slow. If your agent is too slow, you can disable this.
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
                score += WEIGHTS["THREE_IN_LINE"] # This is for a 4x4 or 5x5 almost-win
                potential_fork_lines += 1
            elif player_pieces == n - 2:
                score += WEIGHTS["TWO_IN_LINE"] # This is for a 3x3 almost-win
                potential_fork_lines += 1
    
    return score, potential_fork_lines


def _score_forks(potential_fork_lines: int, WEIGHTS: Dict) -> int:
    """
    Scores a fork opportunity. A fork is a move that creates two threats at once.
    We approximate this by checking if there are 2 or more potential winning lines.
    """
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


# --- Utility Functions ---
# These helpers are needed for the heuristic to work. You should have similar
# functions in your project already.

def get_all_lines(board: List[List[Optional[str]]]) -> List[List[Optional[str]]]:
    """Returns a list of all rows, columns, and diagonals from the board."""
    n = len(board)
    lines = []
    # Rows
    lines.extend(board)
    # Columns
    for c in range(n):
        lines.append([board[r][c] for r in range(n)])
    # Diagonals
    lines.append([board[i][i] for i in range(n)])
    lines.append([board[i][n - 1 - i] for i in range(n)])
    return lines

def check_win(board: List[List[Optional[str]]], player_symbol: str) -> bool:
    """(Placeholder) Checks if the given player has won the game."""
    n = len(board)
    for line in get_all_lines(board):
        if all(cell == player_symbol for cell in line):
            return True
    return False
