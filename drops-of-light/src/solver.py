import heapq as pq
import time
from state import State
from utils import *


# Define the solver for the game
class Solver:
    # Initialize the solver with the given problem
    def __init__(self, problem: State):
        self.problem = problem
        self.solution = {}

    # Solve the game using A* algorithm
    def solve_astar(self):
        start = time.time()

        visited = set({self.problem.hash()})
        self.solution[self.problem.hash()] = (-1, -1)
        queue = [(self.problem.eval(), self.problem)]
        pq.heapify(queue)
        best = 1e9
        solution = None

        while queue:
            now = time.time()

            if now - start > 15:
                break  # Time limit exceeded

            eval, current = pq.heappop(queue)

            if eval > best:
                break

            if current.is_goal():
                best = min(best, eval)
                solution = current
                continue

            next_moves = current.gen_moves()

            for u, v, colors in next_moves:
                new_state = current.deepcopy()
                new_state.move(u, v, colors)
                hash = new_state.hash()
                new_eval = new_state.eval()

                if hash in visited or new_state.energy < 0:
                    continue

                if new_eval > best:  # Or new_state.min_distance > new_state.energy:
                    continue

                pq.heappush(queue, (new_eval, new_state))
                visited.add(hash)
                self.solution[hash] = (current.hash(), u, v, colors, new_state.energy)

        return solution

    # Solve the game using BFS algorithm
    def solve_bfs(self):
        start = time.time()

        visited = set({self.problem.hash()})
        self.solution[self.problem.hash()] = (-1, -1)
        queue = [self.problem]

        while queue:
            now = time.time()

            if now - start > 15:
                break

            current = queue.pop(0)

            if current.is_goal():
                return current

            next_moves = current.gen_moves()

            for u, v, colors in next_moves:
                new_state = current.deepcopy()
                new_state.move(u, v, colors)
                hash = new_state.hash()

                if hash in visited or new_state.energy < 0:
                    continue

                queue.append(new_state)
                visited.add(hash)
                self.solution[hash] = (current.hash(), u, v, colors, new_state.energy)

        return None

    # Solve the game using Iterative Deepening Search algorithm
    def solve_ids(self):
        start = time.time()
        depth = 0

        while depth < 1000:
            print(f"Depth: {depth}")

            visited = set({self.problem.hash()})
            depth_map = {self.problem.hash(): 0}
            self.solution[self.problem.hash()] = (-1, -1)
            stack = [self.problem]

            while stack:
                now = time.time()

                if now - start > 15:
                    break  

                current = stack.pop()  # Pop the last element (DFS)

                if current.is_goal():
                    return current

                if depth_map[current.hash()] >= depth:
                    continue

                next_moves = current.gen_moves()

                for u, v, colors in next_moves:
                    new_state = current.deepcopy()
                    new_state.move(u, v, colors)
                    hash = new_state.hash()

                    if hash in visited or new_state.energy < 0:
                        continue

                    depth_map[hash] = depth_map[current.hash()] + 1

                    stack.append(new_state)
                    visited.add(hash)
                    self.solution[hash] = (
                        current.hash(),
                        u,
                        v,
                        colors,
                        new_state.energy,
                    )

            depth += 1

        return None

    # Get the solution path from the solved state
    def get_solution(self, solved: State):
        if solved is None:
            return None

        current = solved.hash()
        path = []

        while current != -1:
            path.append(self.solution[current])
            current = self.solution[current][0]

        path.pop()
        return path[::-1]  # reverse the path

    # Print the solution path
    def print_solution(self, solved: State):
        path = self.get_solution(solved)

        for _, u, v, colors, energy in path:
            print(f"Move {get_color(colors)} from {u} to {v}   Energy: {energy}")
