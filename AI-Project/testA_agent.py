import copy
import random
import time
from typing import List, Optional, Tuple

from agent_utils import get_all_valid_moves

random.seed(time.time())
transposition_table = {}

def agent_move(board: List[List[Optional[str]]], player_symbol: str) -> Tuple[int, int, int, int]:
    board_size = len(board)
    opponent_symbol = 'O' if player_symbol == 'X' else 'X'
    if board_size == 3:
        for move in get_all_valid_moves(board, player_symbol):
            temp_board = copy.deepcopy(board)
            _simulate_move(temp_board, move, player_symbol)
            if _get_winner(temp_board) == player_symbol:
                return move
        for my_move in get_all_valid_moves(board, player_symbol):
            my_board_copy = copy.deepcopy(board)
            _simulate_move(my_board_copy, my_move, player_symbol)
            is_safe_move = True
            for opponent_move in get_all_valid_moves(my_board_copy, opponent_symbol):
                opponent_board_copy = copy.deepcopy(my_board_copy)
                _simulate_move(opponent_board_copy, opponent_move, opponent_symbol)
                if _get_winner(opponent_board_copy) == opponent_symbol:
                    is_safe_move = False
                    break
            if is_safe_move:
                pass

    return run_minimax_search(board, player_symbol)

def run_minimax_search(board: List[List[Optional[str]]], player_symbol: str) -> Tuple[int, int, int, int]:
    transposition_table.clear()
    board_size = len(board)
    if board_size == 3: search_depth = 100
    elif board_size == 4: search_depth = 5
    else: search_depth = 4

    valid_moves = get_all_valid_moves(board, player_symbol)
    if not valid_moves: return 0, 0, 0, 0

    scores = {}
    opponent_symbol = 'O' if player_symbol == 'X' else 'X'
    for move in valid_moves:
        temp_board = copy.deepcopy(board)
        _simulate_move(temp_board, move, player_symbol)
        scores[move] = minimax(temp_board, search_depth - 1, float('-inf'), float('inf'), False, player_symbol, opponent_symbol)

    max_score = max(scores.values())
    best_moves = [move for move, score in scores.items() if score == max_score]
    return random.choice(best_moves)

def minimax(board: List[List[Optional[str]]], depth: int, alpha: float, beta: float, is_maximizing_player: bool, player_symbol: str, opponent_symbol: str) -> int:
    board_key = tuple(map(tuple, board))
    if board_key in transposition_table: return transposition_table[board_key]
    winner = _get_winner(board)
    if depth == 0 or winner is not None: return _evaluate_board(board, player_symbol)
    current_player = player_symbol if is_maximizing_player else opponent_symbol
    valid_moves = get_all_valid_moves(board, current_player)
    if not valid_moves: return _evaluate_board(board, player_symbol)
    scored_moves = []
    for move in valid_moves:
        temp_board = copy.deepcopy(board)
        _simulate_move(temp_board, move, current_player)
        scored_moves.append((_evaluate_board(temp_board, player_symbol), move))
    scored_moves.sort(key=lambda item: item[0], reverse=is_maximizing_player)
    if is_maximizing_player:
        max_eval = float('-inf')
        for _, move in scored_moves:
            board_copy = copy.deepcopy(board)
            _simulate_move(board_copy, move, current_player)
            evaluation = minimax(board_copy, depth - 1, alpha, beta, False, player_symbol, opponent_symbol)
            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, evaluation)
            if beta <= alpha: break
        transposition_table[board_key] = max_eval
        return max_eval
    else:
        min_eval = float('inf')
        for _, move in scored_moves:
            board_copy = copy.deepcopy(board)
            _simulate_move(board_copy, move, current_player)
            evaluation = minimax(board_copy, depth - 1, alpha, beta, True, player_symbol, opponent_symbol)
            min_eval = min(min_eval, evaluation)
            beta = min(beta, evaluation)
            if beta <= alpha: break
        transposition_table[board_key] = min_eval
        return min_eval

def _get_winner(board: List[List[Optional[str]]]) -> Optional[str]:
    size = len(board)
    players = ['X', 'O']
    for symbol in players:
        for r in range(size):
            if all(board[r][c] == symbol for c in range(size)): return symbol
        for c in range(size):
            if all(board[r][c] == symbol for r in range(size)): return symbol
        if all(board[i][i] == symbol for i in range(size)): return symbol
        if all(board[i][size - 1 - i] == symbol for i in range(size)): return symbol
    return None

def _simulate_move(board: List[List[Optional[str]]], move: Tuple[int, int, int, int], player_symbol: str):
    src_row, src_col, tgt_row, tgt_col = move
    if src_row == tgt_row:
        if tgt_col < src_col:
            for c in range(src_col, tgt_col, -1): board[src_row][c] = board[src_row][c - 1]
        else:
            for c in range(src_col, tgt_col): board[src_row][c] = board[src_row][c + 1]
    else:
        if tgt_row < src_row:
            for r in range(src_row, tgt_row, -1): board[r][src_col] = board[r - 1][src_col]
        else:
            for r in range(src_row, tgt_row): board[r][src_col] = board[r + 1][src_col]
    board[tgt_row][tgt_col] = player_symbol

def _evaluate_board(board: List[List[Optional[str]]], player_symbol: str) -> int:
    score = 0
    size = len(board)
    opponent_symbol = 'O' if player_symbol == 'X' else 'X'
    lines = []
    for r in range(size): lines.append(board[r])
    for c in range(size): lines.append([board[r][c] for r in range(size)])
    lines.append([board[i][i] for i in range(size)])
    lines.append([board[i][size - 1 - i] for i in range(size)])
    for line in lines:
        score += _evaluate_line(line, player_symbol, opponent_symbol, size)
    return score

def _evaluate_line(line: List[Optional[str]], player: str, opponent: str, size: int) -> int:
    score = 0
    player_count = line.count(player)
    opponent_count = line.count(opponent)
    empty_count = line.count(None)
    BALANCE_WEIGHT = 13
    if player_count > opponent_count: score += (player_count - opponent_count) * BALANCE_WEIGHT
    elif opponent_count > player_count: score -= (opponent_count - player_count) * BALANCE_WEIGHT
    if player_count == size: score += 10000
    if player_count == size - 1 and empty_count == 1: score += 500
    if player_count == size - 2 and empty_count == 2: score += 50
    if player_count == size - 2 and empty_count == 1 and opponent_count == 1: score += 25
    if opponent_count == size: score -= 10000
    if opponent_count == size - 1 and empty_count == 1: score -= 1000
    if opponent_count == size - 2 and empty_count == 2: score -= 100
    if opponent_count == size - 2 and empty_count == 1 and player_count == 1: score -= 75
    return score