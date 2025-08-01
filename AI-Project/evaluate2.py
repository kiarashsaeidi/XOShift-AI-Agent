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
except ImportError as e:
    print("--- ERROR ---")
    print("Could not import necessary files. Make sure this script is in the same directory as:")
    print("game.py, agent_loader.py, your_agent.py, and sample_agent.py")
    print(f"Details: {e}")
    sys.exit(1)

# --- Constants ---
# These are taken from your main.py to ensure consistency.
AGENT_TIME_LIMIT = 2.0
MAX_TURNS = 250


def agent_process_wrapper(agent_fn: Callable, board_copy: List[List[Optional[str]]],
                          player_symbol: str, result_queue: multiprocessing.Queue):
    """
    A wrapper to run the agent's function in a separate process.
    This allows for safe timeout and crash handling.
    The result (move or exception) is put into the queue.
    """
    try:
        move = agent_fn(board_copy, player_symbol)
        result_queue.put(move)
    except Exception as e:
        result_queue.put(e)


def play_one_game(agent_x_func: Callable, agent_o_func: Callable, board_size: int) -> Optional[str]:
    """
    Plays a single game of XOShift without a UI and returns the winner ('X', 'O', or 'Draw').
    """
    game = XOShiftGame(size=board_size)
    turn_count = 0
    agents = {'X': agent_x_func, 'O': agent_o_func}

    while game.winner is None:
        if turn_count >= MAX_TURNS:
            return "Draw"

        current_player = game.current_player
        active_agent = agents[current_player]

        # --- Agent Execution with Time Limit (from your main.py) ---
        board_copy = [row[:] for row in game.board]
        result_queue = multiprocessing.Queue()
        agent_process = multiprocessing.Process(target=agent_process_wrapper,
                                                args=(active_agent, board_copy, current_player, result_queue))
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
        
        # Clean up the agent process
        if agent_process.is_alive():
            agent_process.terminate()
        agent_process.join(timeout=0.5) # Give it a moment to close
        if agent_process.is_alive():
            agent_process.kill()
            agent_process.join()

        # --- Handle Agent's Output ---
        if agent_exception or timed_out or not agent_move_coords:
            # If agent crashes, times out, or returns nothing, it's a loss for that agent.
            print(f"\nPlayer {current_player} forfeits. Reason: {'Timeout' if timed_out else 'Crash/Invalid Output'}.")
            game.winner = 'O' if current_player == 'X' else 'X'
            break

        # Apply the valid move
        sr, sc, tr, tc = agent_move_coords
        if not game.apply_move(sr, sc, tr, tc, current_player):
            # If agent returns an illegal move, it's a loss.
            print(f"\nPlayer {current_player} made an invalid move {agent_move_coords}. Forfeits.")
            game.winner = 'O' if current_player == 'X' else 'X'
            break
        
        if game.winner is None:
            if game.is_board_full():
                return "Draw"
            game.switch_player()
        
        turn_count += 1

    return game.winner


def main():
    """
    Main function to run the agent vs. agent evaluation.
    """
    # --- Configuration ---
    AGENT1_PATH = "agent2.py"
    AGENT2_PATH = "sample_agent.py"
    NUM_GAMES = 20
    BOARD_SIZE = 3

    print("--- XOShift Agent Evaluation Script ---")
    print(f"Agent 1: {AGENT1_PATH}")
    print(f"Agent 2: {AGENT2_PATH}")
    print(f"Total Games: {NUM_GAMES}\n")

    try:
        agent1_func = load_agent(AGENT1_PATH)
        agent2_func = load_agent(AGENT2_PATH)
    except Exception as e:
        print(f"Fatal Error: Could not load agents. {e}")
        sys.exit(1)

    stats = {AGENT1_PATH: 0, AGENT2_PATH: 0, "Draw": 0}
    start_time = time.time()

    for i in range(NUM_GAMES):
        print(f"Playing game {i + 1}/{NUM_GAMES}...", end='\r')
        
        # Alternate who starts as 'X'
        # if i % 2 == 0:
        #     winner = play_one_game(agent1_func, agent2_func, BOARD_SIZE)
        #     if winner == 'X':
        #         stats[AGENT1_PATH] += 1
        #     elif winner == 'O':
        #         stats[AGENT2_PATH] += 1
        #     else:
        #         stats["Draw"] += 1
        # else:
        winner = play_one_game(agent2_func, agent1_func, BOARD_SIZE)
        if winner == 'X':
            stats[AGENT2_PATH] += 1
        elif winner == 'O':
            stats[AGENT1_PATH] += 1
        else:
            stats["Draw"] += 1

    end_time = time.time()
    total_time = end_time - start_time

    print("\n\n--- Evaluation Complete ---")
    print(f"Total time: {total_time:.2f} seconds")
    print("\nResults:")
    for agent, wins in stats.items():
        percentage = (wins / NUM_GAMES) * 100
        print(f"  - {agent}: {wins} wins ({percentage:.1f}%)")


if __name__ == "__main__":
    # This is required for multiprocessing to work correctly on some platforms
    multiprocessing.freeze_support()
    main()
