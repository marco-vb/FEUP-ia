# Heuristic Search Methods for One-Player Solitaire Games: Drops of Light

## Artificial Intelligence, 2023/2024

### Group_A1_20

| Name             | Email             | Contribution (%) |
| ---------------- | ----------------- | ---------------- |
| Duarte Gonçalves | up202108772@up.pt | 50%              |
| Marco Vilas Boas | up202108774@up.pt | 50%              |

### Introduction

This project aims to implement and analyze heuristic search methods for solving the one-player solitaire game Drops of Light. It provides an applicable understanding and comparison of different, uninformed and informed, search algorithms. The project is developed in Python and uses the Pygame library for the graphical user interface.

### Game Description

Drops of Light is a one-player solitaire game played on an undirected 19-node graph. The player's goal is to reach the desired configuration of "drops" (colors) without running out of energy. Each level has different initial and objective states.

A quick overview of the game's rules:

- There are 3 primary colors: red, green, and blue.
- There are 4 secondary colors: cyan (green + blue), magenta (red + blue), yellow (red + green), and white (red + green + blue).
- Moving a primary color to a colored node results in the corresponding secondary color.
- The player can move from one node to another if they are connected by an edge.
- The player cannot move to a node that shares a primary component with the color being moved.
- Moving any color, primary or secondary, costs 1 energy.
- The player can split secondary colors into its primary components: splitting white costs 3 energy, splitting the other secondary colors costs 1 energy. The player can then choose where to move each color, costing 1 energy per move. The player can also choose not to move a color, which does not cost energy.
- There are pigments, which can be of any color and cannot be moved. The player can only move a color to a node with a pigment if they do not share a primary component.

### Instalation and Execution

You need to have Python installed on your machine. You can download it [here](https://www.python.org/downloads/).

Download the project's zip file, extract it and navigate to the project's root directory. Open the terminal and run the following command to install the required dependencies:

```bash
pip install -r requirements.txt
```

Finally, to run the application, execute the following commands:

```bash
cd src
python main.py
```

### Usage

The application's main menu allows the player to either start a new game or ask the AI to solve the currently selected level. The player can also select the level they want to play or solve.

The game's interface consists of 2 graphs side by side. The left graph represents the current state of the game, while the right graph represents the objective state. The player can interact with the game by mouse clicking on the left graph. The following actions are available:

- Left-clicking on a node selects it. The player can then move the selected color to another node by left-clicking on the destination node.
- Right-clicking on a node splits the color in the node into its primary components. The player can then move each color to a different node by left-clicking on the destination node.
- Pressing the "U" key undoes the last move.

When the user asks the AI to solve the level, they will be prompted to select the search algorithm. The AI will then solve the selected level and display the solution, as well as the time it took to find it. The user can navigate through the solution by pressing "Enter" to move to the next step or "Backspace" to move to the previous step.

By pressing the "Esc" key, the user can return to the main menu and reset the game state.

### Conclusion

In conclusion, the implemented heuristic search methods provide a good understanding of the game's complexity and the efficiency of different algorithms. The informed search is able to solve the various difficulty levels in a reasonable amount of time. The project also provides a user-friendly interface that allows the player to interact with the game and the AI.

