import random

# --- Project Imports ---
# Import the main Game class and the agent functions
try:
    # This will now use the XOShiftGame class you provided
    from game import XOShiftGame
    import sample_agent 
    import your_agent
    import agent2
except ImportError as e:
    print("--- ERROR ---")
    print("Could not import necessary files. Make sure this script is in the same directory as:")
    print("game.py, your_agent.py, and sample_agent.py")
    print(f"Details: {e}")
    exit()


def play_game(agent_x_func, agent_o_func, board_size=3) -> float:
    """
    Plays one game between agent_x as 'X' and agent_o as 'O' by using the XOShiftGame class.
    Returns 1.0 if X wins, 0.0 if O wins, 0.5 on draw.
    """
    # --- 1. Instantiate the Game Class from your game.py ---
    game = XOShiftGame(size=board_size)

    # --- 2. Main Game Loop ---
    # The loop continues as long as the game's winner attribute is None.
    while game.winner is None:
        # Determine the current agent's function and symbol
        current_player_symbol = game.current_player
        current_agent_func = agent_x_func if current_player_symbol == 'X' else agent_o_func
        
        # Get the current board state from the game object
        board_state = game.board
        board_copy = [row[:] for row in board_state] # Pass a copy to the agent

        # Get the move from the current agent
        move = current_agent_func(board_copy, current_player_symbol)
        
        # Unpack the move for the apply_move method
        src_row, src_col, tgt_row, tgt_col = move

        # --- 3. Use the Game's Internal Methods ---
        # Call the game's method to apply the move.
        move_successful = game.apply_move(src_row, src_col, tgt_row, tgt_col, current_player_symbol)

        if not move_successful:
            # This can happen if the agent returns an invalid move.
            # We'll consider this a loss for the current player.
            game.winner = 'O' if current_player_symbol == 'X' else 'X'
            break

        # Check for a draw condition using the game's method
        if game.is_board_full() and game.winner is None:
            # The game is a draw
            return 0.5
        
        # Switch to the next player for the next turn
        game.switch_player()


    # --- 4. Return the Result ---
    # After the loop ends, check the winner attribute on the game object.
    if game.winner == 'X':
        return 1.0
    elif game.winner == 'O':
        return 0.0
    else: # Draw
        return 0.5


def evaluate_agent(my_agent_func, opponent_func, games: int = 100, board_size: int = 3) -> float:
    """
    Plays `games` matches between my_agent_func vs opponent_func.
    (This function remains the same as the previous version)
    """
    total_points = 0.0
    for i in range(games):
        # if random.randint(0, 1) == 0:
            # Your agent plays as 'X'
        # result = play_game(my_agent_func, opponent_func, board_size)
        # total_points += result
        # winner = 'my_agent' if result == 1.0 else ('opponent' if result == 0.0 else 'draw')
        # else:
            # Your agent plays as 'O'
        result = play_game(opponent_func, my_agent_func, board_size)
        total_points += 1.0 - result
        winner = 'my_agent' if result == 0.0 else ('opponent' if result == 1.0 else 'draw')
        
        print(f"Game {i+1}/{games} complete. Result: {winner}")

    return 100.0 * total_points / games


if __name__ == "__main__":
    my_agent = your_agent.agent_move
    agent2 = agent2.agent_move
    random_agent = sample_agent.agent_move

    win_pct = evaluate_agent(agent2, random_agent, games=30, board_size=3)
    print(f"\nYour agent scored {win_pct:.2f}% of the total possible points.")
