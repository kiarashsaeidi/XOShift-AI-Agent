import math
import copy
from typing import List, Optional, Tuple
from heuristic import evaluate_board
from agent_utils import get_all_valid_moves



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


def minimax(board: List[List[Optional[str]]], depth: int,alpha: float, beta: float, is_maximizing: bool, player_symbol: str, opponent_symbol: str) -> int:
    
    WIN_SCORE = 100000
    if check_win(board, opponent_symbol):
        return -WIN_SCORE 
    if check_win(board, player_symbol):
        return WIN_SCORE  
    if is_board_full(board):
        return 0  
    
    if depth == 0:
        return evaluate_board(board,player_symbol,opponent_symbol)

    if is_maximizing:
        best_score = -math.inf
        valid_moves = get_all_valid_moves(board, player_symbol)
        for move in valid_moves:
            new_board = apply_move(board, move, player_symbol)
            score = minimax(new_board, depth - 1,alpha, beta, False, player_symbol, opponent_symbol)
            best_score = max(score, best_score)
            alpha = max(alpha, score)

            if beta <= alpha:   break
        return best_score
    else:  
        best_score = math.inf
        valid_moves = get_all_valid_moves(board, opponent_symbol)
        for move in valid_moves:
            new_board = apply_move(board, move, opponent_symbol)
            score = minimax(new_board, depth - 1,alpha, beta, True, player_symbol, opponent_symbol)
            best_score = min(score, best_score)

            beta = min(beta, score)

            if beta <= alpha: break
        return best_score



def agent_move(board: List[List[Optional[str]]], player_symbol: str) -> Tuple[int, int, int, int]:
    
    valid_moves = get_all_valid_moves(board, player_symbol)
    
    opponent_symbol = 'O' if player_symbol == 'X' else 'X'
    
    best_score = -math.inf
    chosen_move = None

    if not valid_moves:
        return 0, 0, 0, 0
    
    search_depth = 2

    for move in valid_moves:
        new_board = apply_move(board, move, player_symbol)
        
        score = minimax(new_board, search_depth,-math.inf,math.inf,False, player_symbol, opponent_symbol)
            
        if score > best_score:
            best_score = score
            chosen_move = move

    if chosen_move is None:
        chosen_move = valid_moves[0]


    new_board = apply_move(board, chosen_move, player_symbol)
        
    score = minimax(new_board, search_depth,-math.inf,math.inf,False, player_symbol, opponent_symbol)
    
    return chosen_move
