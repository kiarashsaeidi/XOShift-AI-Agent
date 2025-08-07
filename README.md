# 🤖 AI Agent for XOShift

This repository hosts an intelligent AI agent designed to play **XOShift**, a strategic and dynamic variant of Tic-Tac-Toe. Developed as the final project for the *Artificial Intelligence and Expert Systems* course at **Shahid Beheshti University**, this project combines game theory, adversarial search, and heuristic design into a complete, playable system.

---

## 🎮 About the Game: XOShift

**XOShift** is played on a 3x3, 4x4, or 5x5 grid. While the objective remains to get `N-in-a-row` like in classic Tic-Tac-Toe, XOShift introduces a *shift mechanic* that adds strategic depth:

### 🔁 Move Rules:

Each move has **two steps**:

1. **Select the Source Cell:**

   * If empty cells exist on the outer perimeter, you *must* select one of them.
   * If the perimeter is full, you must select *one of your own pieces* on the perimeter.

2. **Select the Target Cell:**

   * Must be at the **beginning or end** of the same row or column as the source.
   * Source and target cells *cannot* be the same.

3. **Perform the Shift:**

   * The piece in the source cell moves to the target cell.
   * All pieces in that line shift by one space to fill the gap.

---

## 🧠 The AI Agent

The heart of the project is the intelligent agent in `your_agent.py`, which plays strategically using:

### 🧮 Algorithm: Minimax with Alpha-Beta Pruning

* **Game Tree Search:** Explores possible moves to a limited depth.
* **Maximizing vs. Minimizing:** Agent maximizes its own score while assuming the opponent minimizes it.
* **Alpha-Beta Pruning:** Efficiently cuts out unpromising branches of the game tree to stay within a 2-second per-move limit.

### 📊 Heuristic Evaluation (`heuristic.py`)

When the search depth is reached, the heuristic function evaluates the board state based on:

* **Winning or Losing States:** Near-infinite scores for guaranteed outcomes.
* **N-in-a-Row Threats:** Rewards creating or blocking potential winning lines.
* **Forks:** Rewards moves that create multiple threats.
* **Positional Control:** Prioritizes central and corner positions.

Final score formula:

```
My Score - (Opponent's Score × Defense Multiplier)
```

---

## 🚀 How to Run

### ✅ Prerequisites

* Python 3.x
* PyGame

### 📦 Installation

```bash
git clone <your-repository-url>
cd XOShift-AI-Agent
pip install pygame
```

---

### 🎲 Running the Game (UI)

To launch the graphical version of the game:

```bash
python main.py
```

From the menu, choose:

* **Game Mode:** Human vs. Agent, Agent vs. Agent, etc.
* **Board Size:** 3x3, 4x4, or 5x5
* **Agent File:** Easily switch between `your_agent.py`, `sample_agent.py`, or others via `main.py`.

---

### 🧪 Headless Evaluation

To benchmark your agent without a UI:

```bash
python evaluate.py
```

Configure the agents and number of rounds directly in `evaluate.py` to test performance, win/loss rates, and reliability.

---

## 📁 Project Structure

```
.
├── your_agent.py       # Main AI agent using Minimax + Alpha-Beta
├── heuristic.py        # Heuristic function for board evaluation
├── sample_agent.py     # Random-move agent for testing
├── game.py             # Core XOShiftGame logic and rules
├── main.py             # Entry point for graphical game
├── ui.py               # PyGame-based UI rendering
├── evaluate.py         # Script for agent benchmarking without UI
└── agent_loader.py     # Utility to load agents dynamically
```

---

## 🏁 License

This project is developed for academic purposes. Contributions, feedback, and forks are welcome!
