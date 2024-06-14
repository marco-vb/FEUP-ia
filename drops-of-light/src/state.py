from itertools import permutations
from copy import deepcopy
from utils import *


# Represent the state of the game
class State:
    # Initialize the state
    def __init__(self, st=None):
        self.al = adjacency_list

        # Initialize the rest of the variables
        # If st is not None, copy the values from parameter st - used for deepcopy
        # Otherwise, initialize the variables with default values
        if st is not None:
            self.n = st.n
            self.graph = deepcopy(st.graph)
            self.initial_graph = deepcopy(st.graph)
            self.goal = deepcopy(st.goal)
            self.energy = st.energy
            self.initial_energy = st.initial_energy
            self.moves = st.moves
            self.apsp = st.apsp
            self.last_move = st.last_move
        else:
            self.n = 19
            self.graph = [set() for _ in range(self.n)]
            self.initial_graph = [set() for _ in range(self.n)]
            self.goal = [set() for _ in range(self.n)]
            self.energy = 0
            self.initial_energy = 0
            self.moves = 0
            self.apsp = self.floyd_warshall()
            self.last_move = (None, None, None, None)

        # Constants for the colors and pigments (negative values)
        self.RED = 1
        self.GREEN = 2
        self.BLUE = 3
        self.PRED = -1
        self.PGREEN = -2
        self.PBLUE = -3

    # Set the level of the game, read the initial and goal states from the files
    def set_level(self, level):
        # Initialize the graph with the colors
        # Read file 'initial.txt' from ./levels/level
        with open(f"./levels/{level}/initial.txt", "r") as f:
            for i, line in enumerate(f):
                if i == 0:
                    self.energy = int(line)  # First line is the energy
                    self.initial_energy = self.energy
                    continue
                for element in line.split():
                    if element != "0":
                        self.graph[i - 1].add(int(element))

        # Initialize the goal with the colors
        # Read file 'goal.txt' from ./levels/level
        with open(f"./levels/{level}/goal.txt", "r") as f:
            for i, line in enumerate(f):
                for element in line.split():
                    if element != "0":
                        self.goal[i].add(int(element))

    # Check if the move is valid
    def valid_move(self, u, v, colors):
        if u < 0 or u >= self.n or v < 0 or v >= self.n:
            return False

        # Filter the colors that are not pigments
        filtered = list(filter(lambda color: color > 0, self.graph[u]))

        if len(colors) == 2 and len(filtered) == 3:
            return False  # Cannot move two colors from a vertex with 3 colors

        if u == v:
            return True  # Simplifies code

        for color in colors:
            if color < 1 or color > 3 or v not in self.al[u]:
                return False

            # Check if the color or its pigment is not in the destination vertex
            if (
                color not in self.graph[u]
                or color in self.graph[v]
                or -color in self.graph[v]
            ):
                return False

        return True

    # Move the colors from vertex u to vertex v
    def move(self, u, v, colors):
        # Handle the case when the vertices are the same
        # This is a valid move, but it does not change the state (no energy is consumed)
        if u == v:
            return True

        if not self.valid_move(u, v, colors):
            return False

        filtered = list(filter(lambda color: color > 0, self.graph[u]))

        energy_before = self.energy

        # Moving from a vertex with 3 colors requires 3 energy to split the colors
        if len(colors) == 1 and len(filtered) == 3:
            self.energy -= 3

        # Moving from a vertex with 2 colors requires 1 energy to split the colors
        # Need to verify if is not an ongoing move (u had initially 3 colors and now has 2)
        # If it is, do not consume energy
        if len(colors) == 1 and len(filtered) == 2 and not u == self.last_move[0]:
            self.energy -= 1

        for color in colors:
            self.graph[u].remove(color)
            self.graph[v].add(color)
            
        self.energy -= 1
        self.moves += 1

        # Save the last move
        self.last_move = (u, v, colors, energy_before)

        return True

    # Undo the last move
    def undo(self):
        if self.last_move[0] is None:
            return False

        (u, v, colors, energy) = self.last_move

        for color in colors:
            self.graph[u].add(color)
            self.graph[v].remove(color)

        self.energy = energy
        self.last_move = None

        return True

    # Reverse a given move
    # Used to navigate through the solution path
    def reverse_move(self, u, v, colors, energy):
        for color in colors:
            self.graph[u].add(color)
            self.graph[v].remove(color)

        self.moves -= 1
        self.energy = energy

    # Reset the state to the initial state
    def reset(self):
        self.energy = self.initial_energy
        self.moves = 0
        self.last_move = None
        self.graph = deepcopy(self.initial_graph)

    # Check if the current state is the goal state
    def is_goal(self):
        return self.graph == self.goal

    # Generate all possible moves from the current state
    def gen_moves(self):
        moves = []
        for u in range(self.n):
            for v in self.al[u]:
                valid = filter(lambda color: color > 0, self.graph[u])
                subsets = all_substets(list(valid))

                for subset in subsets:
                    subset = list(subset)
                    if self.valid_move(u, v, subset):
                        moves.append((u, v, subset))
        return moves

    # Transform the state to a string
    def __str__(self):
        return str(self.graph)

    # Deepcopy the state to avoid reference issues
    def deepcopy(self):
        return State(self)

    # Hash the state
    def hash(self):
        return str(self.graph).__hash__()

    # Compare two states for equality
    def __eq__(self, other):
        return self.graph == other.graph

    # Floyd-Warshall algorithm to compute the all-pairs shortest path
    # Distance from vertex u to vertex v is stored in apsp[u][v]
    def floyd_warshall(self):
        apsp = [[0 for _ in range(self.n)] for _ in range(self.n)]
        for u in range(self.n):
            for v in range(self.n):
                if u == v:
                    continue
                if v in self.al[u]:
                    apsp[u][v] = 1
                else:
                    apsp[u][v] = 1e9

        for k in range(self.n):
            for u in range(self.n):
                for v in range(self.n):
                    apsp[u][v] = min(apsp[u][v], apsp[u][k] + apsp[k][v])

        return apsp

    # For a given color, find the minimum sum of distances from the vertices with that color in the current state
    # to the vertices with that color in the goal state
    def best_distance(self, color):
        # Color is a set of colors
        from_graph = []
        for i in range(self.n):
            if color.intersection(self.graph_copy[i]) == color:
                from_graph.append(i)

        from_goal = []
        for i in range(self.n):
            if color.intersection(self.goal_copy[i]) == color:
                from_goal.append(i)

        if len(from_graph) != len(from_goal):
            return 0

        # Remove common vertices
        for i in range(self.n):
            if i in from_graph and i in from_goal:
                from_graph.remove(i)
                from_goal.remove(i)

        # Find best mapping from from_graph to from_goal such that the sum of distances is minimized
        # Distances are stored in self.apsp
        # After finding pairs remove them from graph_copy and goal_copy

        best = 1e9
        for perm in permutations(from_goal):
            dist = 0
            for i in range(len(perm)):
                dist += self.apsp[from_graph[i]][perm[i]]
            best = min(best, dist)

        for i in range(len(from_graph)):
            for c in color:
                self.graph_copy[from_graph[i]].remove(c)
                self.goal_copy[from_goal[i]].remove(c)

        return best

    # Evaluate the state for the priority queue in the A* algorithm
    def eval(self):
        # g is the cost of the path from the initial state to the current state
        g = self.initial_energy - self.energy

        # h is the sum of the max distance from a color in the goal to the vertex with that color in current state
        h = 0

        colors = all_substets([1, 2, 3])
        colors = list(reversed(list(colors)))

        self.graph_copy = deepcopy(self.graph)
        self.goal_copy = deepcopy(self.goal)

        for color in colors:
            color = set(color)
            if color == set():
                continue
            h += self.best_distance(color)

        return g + 5 * h  # Weighted A* algorithm with weight 5

    # Define the less than operator for the priority queue
    def __lt__(self, other):
        return self.eval() < other.eval()
