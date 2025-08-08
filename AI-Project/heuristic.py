from typing import List, Optional, Tuple, Dict
import collections


def evaluate_board(board: List[List[Optional[str]]], my_symbol: str, opponent_symbol: str) -> int:
    my_score = score_player_position(board, my_symbol, opponent_symbol)
    opponent_score = score_player_position(board, opponent_symbol, my_symbol)

    return my_score - opponent_score


def score_player_position(board: List[List[Optional[str]]], player_symbol: str, opponent_symbol: str) -> int:
    WEIGHTS = {
        "WIN": 100000,
        "FORK": 5000,
        "THREE_IN_LINE": 200,
        "TWO_IN_LINE": 50,
        "CENTER_CONTROL": 15,
        "CORNER_CONTROL": 10, 
        "MOBILITY": 1
    }

    n = len(board)
    total_score = 0

    if check_win(board, player_symbol):
        return WEIGHTS["WIN"]

    all_lines = get_all_lines(board)
    
    threat_score, potential_fork_lines = _score_threats(all_lines, player_symbol, n, WEIGHTS)
    total_score += threat_score

    total_score += _score_forks(potential_fork_lines, WEIGHTS)

    total_score += _score_corners(board, player_symbol, n, WEIGHTS)
    
    total_score += _score_center_control(board, player_symbol, n, WEIGHTS)
    

    return total_score


def _score_threats(all_lines: List[List[Optional[str]]], player_symbol: str, n: int, WEIGHTS: Dict) -> Tuple[int, int]:
    """Scores threats like two-in-a-row or three-in-a-row."""
    score = 0
    potential_fork_lines = 0
    
    for line in all_lines:
        player_pieces = line.count(player_symbol)
        empty_cells = line.count(None)

        # if player_pieces + empty_cells == n:  # Line is not blocked by the opponent
        if n == 3 : 
            if player_pieces == n - 1:
                score += WEIGHTS["THREE_IN_LINE"] 
                potential_fork_lines += 1
        elif n > 3: 
            if player_pieces == n - 1:
                score += WEIGHTS["THREE_IN_LINE"] 
                potential_fork_lines += 1
            elif player_pieces == n - 2:
                score += WEIGHTS["TWO_IN_LINE"]
                potential_fork_lines += 1
    
    return score, potential_fork_lines


def _score_forks(potential_fork_lines: int, WEIGHTS: Dict) -> int:
    if potential_fork_lines >= 2:
        return WEIGHTS["FORK"]
    return 0


def _score_corners(board: List[List[Optional[str]]], player_symbol: str, n: int, WEIGHTS: Dict) -> int:
    score = 0
    corners = [(0, 0), (0, n - 1), (n - 1, 0), (n - 1, n - 1)]
    for r, c in corners:
        if board[r][c] == player_symbol:
            score += WEIGHTS["CORNER_CONTROL"]
    return score


def _score_center_control(board: List[List[Optional[str]]], player_symbol: str, n: int, WEIGHTS: Dict) -> int:
    score = 0
    if n % 2 == 1:
        center_idx = n // 2
        if board[center_idx][center_idx] == player_symbol:
            score += WEIGHTS["CENTER_CONTROL"]
    else:
        center1 = n // 2 - 1
        center2 = n // 2
        center_cells = [(center1, center1), (center1, center2), (center2, center1), (center2, center2)]
        for r, c in center_cells:
            if board[r][c] == player_symbol:
                score += WEIGHTS["CENTER_CONTROL"]
    return score



def get_all_lines(board: List[List[Optional[str]]]) -> List[List[Optional[str]]]:
    n = len(board)
    lines = []
    lines.extend(board) 
    for c in range(n):
        lines.append([board[r][c] for r in range(n)])
    lines.append([board[i][i] for i in range(n)]) 
    lines.append([board[i][n - 1 - i] for i in range(n)]) 
    return lines

def check_win(board: List[List[Optional[str]]], player_symbol: str) -> bool:
    n = len(board)
    for line in get_all_lines(board):
        if all(cell == player_symbol for cell in line):
            return True
    return False
