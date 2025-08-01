import multiprocessing
import queue
import sys
import time
from typing import Optional, Callable, List

# --- Project Imports ---
# This script uses your existing project files.
try:
    from agent_loader import load_agent
    from game import XOShiftGame
    # <<< MODIFIED: Import the heuristic function for debugging >>>
    from heuristic import evaluate_board 
    # <<< NEW: Import utilities to simulate agent's thinking process >>>
    from your_agent import get_all_valid_moves, apply_move
except ImportError as e:
    print("--- ERROR ---")
    print("Could not import necessary files. Make sure this script is in the same directory as:")
    print("game.py, agent_loader.py, heuristic.py, your_agent.py, and sample_agent.py")
    print(f"Details: {e}")
    sys.exit(1)

# --- Constants ---
AGENT_TIME_LIMIT = 2.0
MAX_TURNS = 250

# --- Debugging Helper ---
def print_board(board: List[List[Optional[str]]]):
    """Prints the board to the console for easy viewing."""
    print("-" * (len(board) * 4 + 1))
    for row in board:
        printable_row = [cell if cell is not None else '.' for cell in row]
        print(f"| {' | '.join(printable_row)} |")
    print("-" * (len(board) * 4 + 1))


def agent_process_wrapper(agent_fn: Callable, board_copy: List[List[Optional[str]]],
                          player_symbol: str, result_queue: multiprocessing.Queue):
    """A wrapper to run the agent's function in a separate process."""
    try:
        move = agent_fn(board_copy, player_symbol)
        result_queue.put(move)
    except Exception as e:
        result_queue.put(e)


def play_one_game(agent_x_func: Callable, agent_o_func: Callable, board_size: int, 
                  heuristic_func: Optional[Callable] = None, debug_agent_name: Optional[str] = None) -> Optional[str]:
    """
    Plays a single game of XOShift. If debug mode is enabled, it prints heuristic scores.
    """
    game = XOShiftGame(size=board_size)
    turn_count = 0
    agents = {'X': agent_x_func, 'O': agent_o_func}
    agent_names = {'X': "sample_agent", 'O': "your_agent"} # Customize for clarity

    if debug_agent_name:
        print("\n--- NEW DEBUG GAME ---")
        print_board(game.board)

    while game.winner is None:
        if turn_count >= MAX_TURNS:
            return "Draw"

        current_player = game.current_player
        active_agent_func = agents[current_player]
        current_agent_name = agent_names[current_player]

        # <<< NEW: Detailed analysis block for the debugged agent's turn >>>
        if debug_agent_name and current_agent_name == debug_agent_name and heuristic_func:
            print(f"\n--- Analyzing all possible moves for {current_agent_name} (as {current_player}) ---")
            possible_moves = get_all_valid_moves(game.board, current_player)
            if not possible_moves:
                print("No possible moves found.")
            for p_move in possible_moves:
                # Simulate the move on a temporary board
                temp_board = apply_move(game.board, p_move, current_player)
                # Calculate the heuristic score for the resulting board
                opponent_symbol = 'O' if current_player == 'X' else 'X'
                score = heuristic_func(temp_board, current_player, opponent_symbol)
                
                print(f"\nIF move is {p_move}:")
                print_board(temp_board)
                print(f"  Resulting Heuristic Score would be: {score}")
            print("\n--- End of Analysis ---")


        board_copy = [row[:] for row in game.board]
        result_queue = multiprocessing.Queue()
        agent_process = multiprocessing.Process(target=agent_process_wrapper,
                                                args=(active_agent_func, board_copy, current_player, result_queue))
        agent_process.start()
        
        agent_move_coords, agent_exception, timed_out = None, None, False
        try:
            agent_output = result_queue.get(timeout=AGENT_TIME_LIMIT)
            if isinstance(agent_output, Exception):
                agent_exception = agent_output
            else:
                agent_move_coords = agent_output
        except queue.Empty:
            timed_out = True
        
        if agent_process.is_alive():
            agent_process.terminate()
            agent_process.join(0.5)
            if agent_process.is_alive():
                agent_process.kill()
                agent_process.join()

        if agent_exception or timed_out or not agent_move_coords:
            game.winner = 'O' if current_player == 'X' else 'X'
            break

        sr, sc, tr, tc = agent_move_coords
        if not game.apply_move(sr, sc, tr, tc, current_player):
            game.winner = 'O' if current_player == 'X' else 'X'
            break
        
        if debug_agent_name:
            print(f"\n>>> Turn {turn_count + 1}: {current_agent_name} (as {current_player}) chose move {agent_move_coords}")
            print_board(game.board)
            print("-" * 40)


        if game.winner is None:
            if game.is_board_full():
                return "Draw"
            game.switch_player()
        
        turn_count += 1

    return game.winner


def main():
    """Main function to run the agent vs. agent evaluation."""
    # --- Configuration ---
    AGENT1_PATH = "sample_agent.py" # The "opponent"
    AGENT2_PATH = "your_agent.py"   # The agent you want to test
    
    # <<< SET DEBUG MODE HERE >>>
    # True: Plays one game with detailed printouts for AGENT2.
    # False: Runs many games fast for statistical evaluation.
    DEBUG_MODE = True
    
    NUM_GAMES = 1 if DEBUG_MODE else 100
    BOARD_SIZE = 3

    print("--- XOShift Agent Evaluation Script ---")
    if DEBUG_MODE:
        print(f"!!! DEBUG MODE ON: Analyzing moves for {AGENT2_PATH} !!!")

    try:
        agent1_func = load_agent(AGENT1_PATH)
        agent2_func = load_agent(AGENT2_PATH)
        # Load the heuristic function only if needed for debugging
        heuristic_to_debug = evaluate_board if DEBUG_MODE else None
    except Exception as e:
        print(f"Fatal Error: Could not load agents/heuristic. {e}")
        sys.exit(1)

    stats = {AGENT1_PATH: 0, AGENT2_PATH: 0, "Draw": 0}
    start_time = time.time()

    for i in range(NUM_GAMES):
        if not DEBUG_MODE:
            print(f"Playing game {i + 1}/{NUM_GAMES}...", end='\r')
        
        # In debug mode, we always want your_agent to go second to analyze its defensive play
        if DEBUG_MODE:
             # agent1 (sample) is 'X', agent2 (your_agent) is 'O'
            winner = play_one_game(agent1_func, agent2_func, BOARD_SIZE, heuristic_to_debug, "your_agent")
            if winner == 'X': stats[AGENT1_PATH] += 1
            elif winner == 'O': stats[AGENT2_PATH] += 1
            else: stats["Draw"] += 1
        else:
            # In normal mode, alternate who starts
            if i % 2 == 0:
                winner = play_one_game(agent1_func, agent2_func, BOARD_SIZE)
                if winner == 'X': stats[AGENT1_PATH] += 1
                elif winner == 'O': stats[AGENT2_PATH] += 1
                else: stats["Draw"] += 1
            else:
                winner = play_one_game(agent2_func, agent1_func, BOARD_SIZE)
                if winner == 'X': stats[AGENT2_PATH] += 1
                elif winner == 'O': stats[AGENT1_PATH] += 1
                else: stats["Draw"] += 1

    end_time = time.time()
    total_time = end_time - start_time

    print("\n\n--- Evaluation Complete ---")
    print(f"Total time: {total_time:.2f} seconds")
    print("\nResults:")
    for agent, wins in stats.items():
        percentage = (wins / NUM_GAMES) * 100 if NUM_GAMES > 0 else 0
        print(f"  - {agent}: {wins} wins ({percentage:.1f}%)")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
