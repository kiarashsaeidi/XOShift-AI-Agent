XOShift AI Agent
This repository contains an intelligent agent for the game XOShift, a challenging variant of Tic-Tac-Toe. The agent uses the Minimax algorithm to analyze the game state and select the optimal move.

This project was developed for the "Artificial Intelligence and Expert Systems" course at Shahid Beheshti University.

About the Game: XOShift
XOShift expands on classic Tic-Tac-Toe with a unique "shift" mechanic for placing pieces. The objective remains the same: be the first to form a complete row, column, or diagonal with your pieces.

Key Rules:
Board Size: The game can be played on a 3x3, 4x4, or 5x5 grid.

Making a Move: A move consists of two selections:

First Cell: You must select an empty cell on the perimeter of the board. If the perimeter is full, you must select one of your own pieces on the perimeter.

Second Cell: You must select a cell at the beginning or end of the row/column of your first selected cell.

The Shift: The piece from the first cell moves to the second cell's position, and all other pieces in that line shift over to fill the vacated spot.

The AI Agent
The agent is implemented in Python and decides its moves by thinking ahead and anticipating the opponent's actions.

Core Algorithm: Minimax
The agent's logic is built on the Minimax algorithm, a classic decision-making algorithm for two-player games. It works by:

Building a tree of possible future moves.

Assuming the agent (the "Maximizer") will always choose the move with the best possible outcome.

Assuming the opponent (the "Minimizer") will always choose the move that is worst for the agent.

Evaluating the board states at a certain depth and propagating the scores back up the tree to find the optimal move at the current state.

Evaluation Function
For this implementation, a simple evaluation function is used to score the outcome of a game tree branch:

+1: If the move leads to a win for the AI.

-1: If the move leads to a loss for the AI.

0: For a draw or an inconclusive game state at the maximum search depth.

Potential Enhancements
Alpha-Beta Pruning: A crucial optimization to the Minimax algorithm that would significantly speed up the search by pruning branches of the game tree that don't need to be evaluated.

Heuristic Evaluation: Implementing a more advanced heuristic function to score intermediate board states would make the AI much stronger. This function could evaluate factors like the number of potential winning lines, center control, and blocking opponent's threats.

How to Run the Project
The game environment is built using PyGame.

1. Prerequisites
   Python 3

2. Installation
   Install the necessary package using pip:

pip install pygame

3. Configuration
   Place your agent file (e.g., your_student_id.py) in the project directory.

Open the main.py file.

Set the agent1_path_config or agent2_path_config variable to the name of your agent file so the game can load it.

4. Execution
   Run the main script from your terminal to start the game:

python main.py

You can then select the game mode (e.g., Human vs Agent) and board size from the main menu.
