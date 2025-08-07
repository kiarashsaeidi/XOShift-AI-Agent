AI Agent for XOShift
This repository contains an intelligent AI agent for XOShift, a complex variant of Tic-Tac-Toe, developed as the final project for the "Artificial Intelligence and Expert Systems" course at Shahid Beheshti University.

The agent uses the Minimax algorithm with Alpha-Beta Pruning and a sophisticated heuristic evaluation function to analyze the game state and make strategic decisions. The project includes the complete game environment, multiple agents for testing, and a headless evaluation script for performance analysis.

🎮 About the Game: XOShift
XOShift is played on a 3x3, 4x4, or 5x5 grid. While the goal is to get N-in-a-row like Tic-Tac-Toe, the piece placement is unique and strategic, involving a "shift" mechanic.

How to Play
A move consists of two steps:

Select the First Cell (Source):

If any empty cells exist on the outer perimeter of the board, you must select one of them.

If the perimeter is full, you must select one of your own pieces on the perimeter.

Select the Second Cell (Target):

You must select a cell at the beginning or end of the row or column of your source cell.

The source and target cells cannot be the same.

Perform the Shift:

The piece from the source cell moves to the target cell.

All other pieces in that line slide over one space to fill the vacated spot.

🧠 The AI Agent
The core of this project is the intelligent agent (your_agent.py) designed to play XOShift strategically.

Algorithm: Minimax with Alpha-Beta Pruning
The agent's decision-making is powered by the Minimax algorithm, a classic adversarial search algorithm perfect for two-player, zero-sum games.

Game Tree Search: It explores future possible moves to a certain depth.

Maximizer vs. Minimizer: It assumes the agent will always try to maximize its score, while the opponent will always try to minimize it.

Alpha-Beta Pruning: To meet the 2-second time limit per move, the algorithm uses Alpha-Beta Pruning. This optimization safely prunes large portions of the game tree that cannot influence the final decision, allowing for a deeper and more efficient search.

Heuristic Evaluation Function
When the search reaches its maximum depth, a heuristic function (heuristic.py) evaluates the board's strategic value. The final score is calculated as My Score - (Opponent's Score * Defense Multiplier), rewarding moves that improve our position while penalizing those that allow the opponent an advantage.

The heuristic considers several factors:

Winning/Losing States: Assigns a near-infinite score for guaranteed wins or losses.

N-in-a-Row Threats: Scores potential winning lines (e.g., 2-in-a-row on a 3x3 board).

Forks: Gives a very high score for creating two threats simultaneously.

Positional Control: Assigns value to controlling strategically important corners and center squares.

🚀 How to Run
Prerequisites
Python 3.x

PyGame

Installation
Clone the repository:

git clone <your-repository-url>

Navigate to the project directory:

cd XOShift-AI-Agent

Install the required library:

pip install pygame

Running the Game with UI
To play the game with the graphical interface, run main.py:

python main.py

From the main menu, you can select:

Game Mode: Human vs. Agent, Agent vs. Agent, etc.

Board Size: 3x3, 4x4, or 5x5.

Agent Configuration: The main.py file can be configured to load different agent files (your_agent.py, sample_agent.py, etc.).

Running the Headless Evaluation
To evaluate your agent's performance against another agent without a UI, use the evaluation script. This script runs a set number of games and reports the win/loss/draw statistics.

python evaluate.py

You can configure the agents to compete and the number of games directly within the evaluate.py file.

📂 Project Structure
.
├── your_agent.py       # Your primary intelligent agent with Minimax
├── heuristic.py        # The heuristic evaluation function
├── sample_agent.py     # A simple agent that plays randomly
├── game.py             # Contains the core XOShiftGame class and rules
├── main.py             # The main entry point for the UI game
├── ui.py               # Handles all PyGame rendering and UI logic
├── evaluate.py         # Headless script for performance testing
└── agent_loader.py     # Utility to dynamically load agent files
