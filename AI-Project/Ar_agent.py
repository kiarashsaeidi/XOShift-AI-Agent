from typing import List, Optional, Tuple
from agent_utils import get_all_valid_moves
import copy
import time

TIME_LIMIT = 1.9


def agent_move(board: List[List[Optional[str]]], player_symbol: str) -> Tuple[int, int, int, int]:
    valid_moves = get_all_valid_moves(board, player_symbol)
    opponent_symbol = 'O' if player_symbol == 'X' else 'X'
    start_time = time.time()

    if not valid_moves:
        return 0, 0, 0, 0

    
    for move in valid_moves:
        sim_board = simulate_move(copy_board(board), move, player_symbol)
        if check_win(sim_board, player_symbol):
            return move

    # for move in valid_moves:
    #     sim_board = simulate_move(copy_board(board), move, player_symbol)
    #     if cause_opponent_win(sim_board, opponent_symbol):
    #         return move 

    best_move = valid_moves[0]
    best_score = float('-inf')

    depth = 1
    while True:
        time_spent = time.time() - start_time
        if time_spent >= TIME_LIMIT:
            break

        scores = []
        for move in valid_moves:
            sim_board = simulate_move(copy_board(board), move, player_symbol)
            score = minimax(sim_board, depth - 1, False, player_symbol, opponent_symbol, float('-inf'), float('inf'), start_time)
            scores.append((score, move))

        scores.sort(reverse=True)

        cur_best = None
        cur_best_score = float('-inf')

        for _, move in scores:
            sim_board = simulate_move(copy_board(board), move, player_symbol)
            score = minimax(sim_board, depth - 1, False, player_symbol, opponent_symbol, float('-inf'), float('inf'), start_time)
            
            if score > cur_best_score:
                cur_best_score = score
                cur_best = move

            if time.time() - start_time >= TIME_LIMIT:
                break

        if cur_best_score > best_score:
            best_score = cur_best_score
            best_move = cur_best

        depth += 1
    
    return best_move

def minimax(board, depth, is_maximizing, player, opponent, alpha, beta, start_time):
    if time.time() - start_time > TIME_LIMIT:
        return evaluate_score(board, player, opponent)
    
    if check_win(board, player):
        return 10000 + depth
    
    if check_win(board, opponent):
        return -10000 - depth
    
    if depth == 0 or is_full(board):
        return evaluate_score(board, player, opponent)
    
    if is_maximizing:
        max_val = float('-inf')
        for move in get_all_valid_moves(board, player):
            simulated = simulate_move(copy_board(board), move, player)
            val = minimax(simulated, depth-1, False, player, opponent, alpha, beta, start_time)
            max_val = max(max_val, val)
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return max_val
    else:
        min_val = float('inf')
        for move in get_all_valid_moves(board, opponent):
            simulated = simulate_move(copy_board(board), move, opponent)
            val = minimax(simulated, depth-1, True, player, opponent, alpha, beta, start_time)
            min_val = min(min_val, val)
            beta = min(beta, val)
            if beta <= alpha:
                break
        return min_val
    

def evaluate_score(board: List[List[Optional[str]]], player: str, opponent: str) -> int:
    size = len(board)
    score = 0

    center = size // 2
    for r in range(size):
        for c in range(size):
            cell = board[r][c]
            if cell == player:
                score += 5 - abs(r - center) - abs(c - center)
            elif board[r][c] == opponent:
                score -= 4 - abs(r - center) - abs(c - center)

    lines = []

    for i in range(size):
        lines.append([board[i][j] for j in range(size)])
        lines.append([board[j][i] for j in range(size)])

    lines.append([board[i][i] for i in range(size)])
    lines.append([board[i][size-1-i] for i in range(size)])

    for line in lines:
        p = line.count(player)
        o = line.count(opponent)
        e = line.count(None)

        if p == size:                   score += 10000
        elif o == size:                 score -= 10000
        elif p == size - 1 and e == 1:  score += 1000
        elif o == size - 1 and e == 1:  score -= 800
        elif p == size - 2 and e == 2:  score += 100
        elif o == size - 2 and e == 2:  score -= 80
        elif p > 0 and o == 0:          score += p * 20
        elif o > 0 and p == 0:          score -= o * 18
        

    return score


def simulate_move(board: List[List[Optional[str]]], move: Tuple[int, int, int, int], player: str) -> List[List[Optional[str]]]:
    sr, sc, tr, tc = move
    size = len(board)

    if sr == tr:
        if tc < sc:
            for i in range(sc, tc, -1):
                board[sr][i] = board[sr][i - 1]
        else:
            for i in range(sc, tc):
                board[sr][i] = board[sr][i + 1]
    else:
        if tr < sr:
            for i in range(sr, tr, -1):
                board[i][sc] = board[i - 1][sc]
        else:
            for i in range(sr, tr):
                board[i][sc] = board[i + 1][sc]

    board[tr][tc] = player
    return board


def check_win(board: List[List[Optional[str]]], player: str) -> bool:
    size = len(board)

    for i in range(size):
        if (all(board[i][j] == player for j in range(size))):
            return True
        if (all(board[j][i] == player for j in range(size))):
            return True
        
    if all(board[i][i] == player for i in range(size)):
        return True
    if all(board[i][size-i-1] == player for i in range(size)):
        return True
    
    return False


def cause_opponent_win(board: List[List[Optional[str]]], opponent: str) -> bool:
    opponents_move = get_all_valid_moves(board, opponent)

    for move in opponents_move:
        simulated = simulate_move(copy_board(board), move, opponent)
        if check_win(simulated, opponent):
            return True
    return False


def copy_board(board: List[List[Optional[str]]]) -> List[List[Optional[str]]]:
    return [row.copy() for row in board]

def is_full(board: List[List[Optional[str]]]) -> bool:
    return all(cell is not None for row in board for cell in row)