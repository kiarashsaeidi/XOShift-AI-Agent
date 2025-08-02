import datetime
import json
import multiprocessing
import os
import queue
import sys
from typing import Optional, Callable, List, Dict, Any
import pygame

from agent_loader import load_agent
from game import XOShiftGame
from ui import XOShiftUI, REPLAYS_DIR
# <<< NEW: Import heuristic components for debugging >>>
from heuristic import evaluate_board
from your_agent import get_all_valid_moves, apply_move

AGENT_TIME_LIMIT = 2.0
MAX_TURNS = 250
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 850

# --- NEW: Debugging Helper ---
def print_board(board: List[List[Optional[str]]]):
    """Prints the board to the console for easy viewing."""
    print("-" * (len(board) * 4 + 1))
    for row in board:
        printable_row = [cell if cell is not None else '.' for cell in row]
        print(f"| {' | '.join(printable_row)} |")
    print("-" * (len(board) * 4 + 1))


def agent_process_wrapper(agent_fn: Callable, board_copy: List[List[Optional[str]]],
                          player_symbol: str, result_queue: multiprocessing.Queue):
    try:
        move = agent_fn(board_copy, player_symbol)
        result_queue.put(move)
    except Exception as e:
        result_queue.put(e)


def main_loop():
    pygame.init()
    multiprocessing.freeze_support()

    if not os.path.exists(REPLAYS_DIR):
        try:
            os.makedirs(REPLAYS_DIR)
            print(f"Created directory: {REPLAYS_DIR}")
        except OSError as e:
            print(f"Error creating directory {REPLAYS_DIR}: {e}. Replays may not save.")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("XOShift Game")
    clock = pygame.time.Clock()

    ui = XOShiftUI(screen)
    game: Optional[XOShiftGame] = None

    agent1: Optional[Callable] = None
    agent2: Optional[Callable] = None
    agent1_path_config = "your_agent.py"
    agent2_path_config = "agent2.py"

    # --- NEW: Flag to control heuristic analysis for human player ---
    human_turn_analysis_done = False

    # ... (other variables remain the same) ...
    current_move_history: List[Dict[str, Any]] = []
    should_record_current_game = False
    turn_count = 0
    loaded_replay_moves: List[Dict[str, Any]] = []
    current_replay_index = 0
    current_replay_filename: Optional[str] = None
    running = True
    while running:
        if game and not game.winner and turn_count >= MAX_TURNS:
            game.winner = "Draw"
            ui.state = XOShiftUI.STATE_GAME_OVER
            print(f"Game ended in a draw after reaching the maximum of {MAX_TURNS} turns.")

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                break
        if not running:
            continue

        ui_event_to_process = pygame.event.Event(pygame.NOEVENT)
        if events:
            mouse_down_events = [e for e in events if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1]
            if mouse_down_events:
                ui_event_to_process = mouse_down_events[0]
            else:
                key_down_events = [e for e in events if e.type == pygame.KEYDOWN]
                if key_down_events:
                    ui_event_to_process = key_down_events[0]

        action = ui.handle_event(ui_event_to_process)

        if action:
            if action["action"] == "quit":
                running = False
            elif action["action"] == "start_game":
                # ... (this block remains the same, but we reset the flag) ...
                human_turn_analysis_done = False
                board_size = action["size"]
                game_mode = action["mode"]
                should_record_current_game = action.get("record_replay", False) and game_mode != "replay-select-file"
                
                try:
                    game = XOShiftGame(size=board_size)
                    turn_count = 0
                except ValueError as e:
                    print(f"Error initializing game: {e}. Returning to menu.")
                    game = None
                    ui.set_game(None)
                    continue

                agent1_name = os.path.basename(agent1_path_config).replace(".py", "")
                agent2_name = os.path.basename(agent2_path_config).replace(".py", "")

                if game_mode == "human-human":
                    ui.player_types = {'X': 'human', 'O': 'human'}
                elif game_mode == "human-agent":
                    ui.player_types = {'X': agent1_name, 'O': 'human'}
                elif game_mode == "agent-agent":
                    ui.player_types = {'X': agent1_name, 'O': agent2_name}

                ui.set_game(game)
                current_move_history = []
                ui.replay_finished = False

                agent1, agent2 = None, None
                if game_mode == "human-agent":
                    try:
                        agent1 = load_agent(agent1_path_config)
                    except Exception as e:
                        print(f"Error loading agent 1: {e}.")
                elif game_mode == "agent-agent":
                    try:
                        agent1 = load_agent(agent1_path_config)
                        agent2 = load_agent(agent2_path_config)
                    except Exception as e:
                        print(f"Error loading agents: {e}.")

                if game:
                    ui.state = XOShiftUI.STATE_SELECT
                    is_first_player_agent = (game_mode == "agent-agent" and agent1) or \
                                            (game_mode == "human-agent" and game.current_player_index == 0 and agent1)
                    if is_first_player_agent:
                        ui.state = XOShiftUI.STATE_WAITING


            elif action["action"] == "apply_move" and game and ui.state != XOShiftUI.STATE_WAITING:
                # --- NEW: Reset the analysis flag after a human moves ---
                human_turn_analysis_done = False
                sr, sc, tr, tc = action["move"]
                player_making_move = game.current_player
                if game.apply_move(sr, sc, tr, tc, player_making_move):
                    turn_count += 1
                    if should_record_current_game:
                        current_move_history.append({
                            "player": player_making_move, "src_r": sr, "src_c": sc,
                            "tgt_r": tr, "tgt_c": tc
                        })
                    if not game.winner:
                        game.switch_player()
                        is_next_player_human = ui.player_types.get(game.current_player) == 'human'
                        ui.state = XOShiftUI.STATE_SELECT if is_next_player_human else XOShiftUI.STATE_WAITING
                    else:
                        ui.state = XOShiftUI.STATE_GAME_OVER
                    ui.selected_cell = None

            # ... (other actions like load_replay, return_to_menu remain the same) ...

        # <<< NEW: Block to perform and print heuristic analysis for the human player >>>
        if game and ui.state == XOShiftUI.STATE_SELECT and not human_turn_analysis_done:
            human_player_symbol = game.current_player
            opponent_symbol = 'O' if human_player_symbol == 'X' else 'X'
            
            print(f"\n--- Heuristic Analysis for Human Player ({human_player_symbol}) ---")
            possible_moves = get_all_valid_moves(game.board, human_player_symbol)
            
            if not possible_moves:
                print("No possible moves found.")
            else:
                move_scores = []
                for p_move in possible_moves:
                    temp_board = apply_move(game.board, p_move, human_player_symbol)
                    score = evaluate_board(temp_board, human_player_symbol, opponent_symbol)
                    move_scores.append((p_move, score))
                
                # Sort moves from best to worst based on the heuristic score
                move_scores.sort(key=lambda item: item[1], reverse=True)

                for p_move, score in move_scores:
                    print(f"\nPossible Move: {p_move}  |  Heuristic Score: {score}")
                    temp_board = apply_move(game.board, p_move, human_player_symbol)
                    print_board(temp_board)

            print("--------------------------------------------------")
            human_turn_analysis_done = True # Set flag to prevent re-printing every frame

        if game and not game.winner and ui.state == XOShiftUI.STATE_WAITING:
            # ... (agent turn logic remains the same) ...
            human_turn_analysis_done = False # Reset flag for the next human turn
            active_agent: Optional[Callable] = None
            player_whose_turn_is_it = game.current_player

            if game.current_player_index == 0 and agent1:
                active_agent = agent1
            elif game.current_player_index == 1 and agent2:
                active_agent = agent2

            if active_agent:
                # ... (the rest of the agent process logic is unchanged) ...
                ui.draw()
                pygame.display.flip()

                board_copy = [[cell for cell in row] for row in game.board]
                result_queue = multiprocessing.Queue()
                agent_process = multiprocessing.Process(target=agent_process_wrapper,
                                                        args=(active_agent, board_copy, player_whose_turn_is_it,
                                                              result_queue))
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
                except Exception as e:
                    agent_exception = e

                if agent_process.is_alive():
                    agent_process.terminate()
                agent_process.join(timeout=0.5)
                if agent_process.is_alive():
                    agent_process.kill()
                    agent_process.join()

                if agent_exception:
                    print(f"Agent {player_whose_turn_is_it} crashed: {agent_exception}. Opponent's turn.")
                    game.switch_player()
                elif timed_out:
                    print(f"Agent {player_whose_turn_is_it} timed out. Opponent's turn.")
                    turn_count += 1
                    game.switch_player()
                elif agent_move_coords:
                    sr, sc, tr, tc = agent_move_coords
                    if game.apply_move(sr, sc, tr, tc, player_whose_turn_is_it):
                        turn_count += 1
                        if should_record_current_game:
                            current_move_history.append({"player": player_whose_turn_is_it, "src_r": sr, "src_c": sc,
                                                         "tgt_r": tr, "tgt_c": tc})
                        if not game.winner:
                            game.switch_player()
                    else:
                        print(f"Agent {player_whose_turn_is_it} invalid move: {agent_move_coords}. Opponent's turn.")
                        game.switch_player()
                else:
                    print(f"Agent {player_whose_turn_is_it} no move/error. Opponent's turn.")
                    game.switch_player()

                if game.winner:
                    ui.state = XOShiftUI.STATE_GAME_OVER
                else:
                    is_next_human = ui.player_types.get(game.current_player) == 'human'
                    ui.state = XOShiftUI.STATE_SELECT if is_next_human else XOShiftUI.STATE_WAITING

        # ... (the rest of the main loop is unchanged) ...
        ui.draw()
        clock.tick(30)
    
    # ... (save on quit logic is unchanged) ...
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main_loop()
