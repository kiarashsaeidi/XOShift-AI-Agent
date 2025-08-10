import math
import copy
import time
from typing import List, Optional, Tuple
from agent_utils import get_all_valid_moves

class SearchTimeout(Exception):
    pass

def apply_move(board: List[List[Optional[str]]], move: Tuple[int, int, int, int], symbol: str) -> List[List[Optional[str]]]:
    r1, c1, r2, c2 = move
    new_board = copy.deepcopy(board)
    new_board[r1][c1] = symbol

    if r1 == r2:
        if c1 < c2:
            for c in range(c1, c2):
                new_board[r1][c] = new_board[r1][c + 1]
        else:
            for c in range(c1, c2, -1):
                new_board[r1][c] = new_board[r1][c - 1]
    elif c1 == c2:
        if r1 < r2:
            for r in range(r1, r2):
                new_board[r][c1] = new_board[r + 1][c1]
        else:
            for r in range(r1, r2, -1):
                new_board[r][c1] = new_board[r - 1][c1]
    
    new_board[r2][c2] = symbol
    return new_board

def check_win(board: List[List[Optional[str]]], player_symbol: str) -> bool:
    n = len(board)
    for i in range(n):
        if all(board[i][j] == player_symbol for j in range(n)) or \
           all(board[j][i] == player_symbol for j in range(n)):
            return True
    if all(board[i][i] == player_symbol for i in range(n)) or \
       all(board[i][n - 1 - i] == player_symbol for i in range(n)):
        return True
    return False

def is_board_full(board: List[List[Optional[str]]]) -> bool:
    for row in board:
        if None in row:
            return False
    return True

def minimax(board: List[List[Optional[str]]], depth: int, alpha: float, beta: float, is_maximizing: bool, player_symbol: str, opponent_symbol: str, start_time: float, time_limit: float) -> int:
    if time.time() - start_time > time_limit:
        raise SearchTimeout

    WIN_SCORE = float('inf')
    if check_win(board, opponent_symbol):
        return -WIN_SCORE
    if check_win(board, player_symbol):
        return WIN_SCORE
    if is_board_full(board):
        return 0
    
    if depth == 0:
        return evaluate_board(board, player_symbol, opponent_symbol)

    if is_maximizing:
        best_score = -math.inf
        valid_moves = get_all_valid_moves(board, player_symbol)
        for move in valid_moves:
            new_board = apply_move(board, move, player_symbol)
            score = minimax(new_board, depth - 1, alpha, beta, False, player_symbol, opponent_symbol, start_time, time_limit)
            best_score = max(score, best_score)
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return best_score
    else:
        best_score = math.inf
        valid_moves = get_all_valid_moves(board, opponent_symbol)
        for move in valid_moves:
            new_board = apply_move(board, move, opponent_symbol)
            score = minimax(new_board, depth - 1, alpha, beta, True, player_symbol, opponent_symbol, start_time, time_limit)
            best_score = min(score, best_score)
            beta = min(beta, score)
            if beta <= alpha:
                break
        return best_score

def agent_move(board: List[List[Optional[str]]], player_symbol: str) -> Tuple[int, int, int, int]:
    start_time = time.time()
    time_limit = 1.9  
    
    valid_moves = get_all_valid_moves(board, player_symbol)
    opponent_symbol = 'O' if player_symbol == 'X' else 'X'
    
    if not valid_moves:
        return (0, 0, 0, 0)
    
    if len(valid_moves) == 1:
        return valid_moves[0]
    
    best_move = valid_moves[0]
    depth = 1
    max_depth = 100
    
    while depth <= max_depth:
        if time.time() - start_time > time_limit:
            break
            
        moves_with_eval = []
        for move in valid_moves:
            new_board = apply_move(board, move, player_symbol)
            eval_score = evaluate_board(new_board, player_symbol, opponent_symbol)
            moves_with_eval.append((eval_score, move))
        
        moves_with_eval.sort(key=lambda x: x[0], reverse=True)
        sorted_moves = [move for (_, move) in moves_with_eval]
        
        current_best_move = None
        current_best_score = -math.inf
        
        for move in sorted_moves:
            if time.time() - start_time > time_limit:
                break
                
            new_board = apply_move(board, move, player_symbol)
            try:
                score = minimax(new_board, depth - 1, -math.inf, math.inf, False, player_symbol, opponent_symbol, start_time, time_limit)
            except SearchTimeout:
                break
                
            if score > current_best_score:
                current_best_score = score
                current_best_move = move
                
        if current_best_move is not None:
            best_move = current_best_move
        else:
            break
            
        depth += 1
        
    return best_move





# heuristic codes ...

from typing import List, Optional, Tuple, Dict


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
    score = 0
    potential_fork_lines = 0
    
    for line in all_lines:
        player_pieces = line.count(player_symbol)
        empty_cells = line.count(None)

        
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
