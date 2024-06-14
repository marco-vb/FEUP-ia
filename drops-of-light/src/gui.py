import pygame
from playball import Playball
from state import State
from solver import Solver
from math import cos, sin, pi
from utils import *

# Initialize pygame
pygame.init()

# Constants
WIDTH = 1200
HEIGHT = WIDTH * 9 // 16

FPS = 60

BG_COLOR = (0, 0, 25)

LINE_WIDTH = 2
CIRCLE_RADIUS = 15


# Define the graphical user interface
class GUI:
    # Initialize the GUI with the given state and solver
    def __init__(self, state, solver):
        self.state = state
        self.solver = solver
        self.solution = None
        self.move = 0

        pygame.display.set_caption("Drops of Light")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        self.running = True
        self.clock = pygame.time.Clock()

        self.levels = [1, 2, 3, 4]
        self.algorithms = ["A*", "BFS", "IDS"]

        self.level = 1
        self.state.set_level(self.level)

        # Set the initial mode to the menu
        self.mode = "Menu"

        self.positions = self.generate_positions()
        self.playballs = [None for _ in range(19)]

        self.ball_selected = None

        # Handle splitting moves
        self.splitting_move = False
        self.splitting_buffer = []

        self.failed = False

        # Load the graph
        self.generate_graph()

    # Filter the real colors of a set, removing pigments
    def filtered(self, set):
        return list(filter(lambda x: x > 0, set))

    # Main loop
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.draw()

    # Event detection and handling
    def events(self):
        for event in pygame.event.get():
            # Quit the game
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                # Return to the menu when the escape key is pressed
                if event.key == pygame.K_ESCAPE:
                    self.mode = "Menu"
                    self.reset()

                self.failed = False
                
                # Handle the menu input
                if self.mode == "Menu":
                    if event.key == pygame.K_1:
                        self.mode = "Game"
                        self.reset()
                    elif event.key == pygame.K_2:
                        self.mode = "Algorithm"
                    elif event.key == pygame.K_3:
                        self.mode = "Level"
                    elif event.key == pygame.K_0:
                        self.running = False

                elif self.mode == "Game":
                    # Undo the last move when the u key is pressed
                    if event.key == pygame.K_u:
                        if self.state.undo():
                            self.move -= 1

                elif self.mode == "Solution":
                    # Move the state back when the backspace key is pressed
                    if event.key == pygame.K_BACKSPACE and self.move > 0:
                        self.move -= 1
                        move = self.solution[self.move]
                        energy = (
                            self.solution[self.move - 1][4]
                            if self.move > 0
                            else self.state.initial_energy
                        )
                        self.state.reverse_move(
                            move[1], move[2], move[3], energy)

                    # Move the state forward when the enter key is pressed
                    if event.key == pygame.K_RETURN:
                        if self.move < len(self.solution):
                            move = self.solution[self.move]
                            self.state.move(move[1], move[2], move[3])
                            self.move += 1

                # Handle the level select input
                elif self.mode == "Level":
                    for i, level in enumerate(self.levels):
                        if event.key == getattr(pygame, f"K_{i + 1}"):
                            self.level = level
                            self.reset()
                            self.mode = "Menu"

                # Handle the algorithm select input
                elif self.mode == "Algorithm":
                    for i, algorithm in enumerate(self.algorithms):
                        if event.key == getattr(pygame, f"K_{i + 1}"):
                            self.algorithm = algorithm
                            self.mode = "Solution"

                            self.draw_loading()
                            start = pygame.time.get_ticks()

                            if algorithm == "A*":
                                self.solution = self.solver.get_solution(
                                    self.solver.solve_astar())
                            elif algorithm == "BFS":
                                self.solution = self.solver.get_solution(
                                    self.solver.solve_bfs())
                            elif algorithm == "IDS":
                                self.solution = self.solver.get_solution(
                                    self.solver.solve_ids())

                            if self.solution is None:
                                self.mode = "Menu"
                                self.failed = True

                            end = pygame.time.get_ticks()
                            self.time = end - start

                            self.move = 0

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Handle the game input
                if self.mode == "Game" and not self.state.is_goal():
                    # Mouse cursor position
                    pos = pygame.mouse.get_pos()

                    # Left click
                    if event.button == 1:
                        for playball in self.playballs:
                            id = playball.handle_click(pos)

                            if id is None:
                                continue

                            if not self.splitting_move:
                                if self.ball_selected is not None:
                                    colors = self.filtered(
                                        self.state.graph[self.ball_selected])

                                    if self.state.move(self.ball_selected, id, colors) and not self.ball_selected == id:
                                        self.move += 1

                                    self.ball_selected = None

                                elif len(self.filtered(self.state.graph[id])) > 0:
                                    self.ball_selected = id

                            else:
                                colors = set({self.splitting_buffer[-1]})

                                if self.state.move(self.ball_selected, id, colors):
                                    if not self.ball_selected == id:
                                        self.move += 1

                                    self.splitting_buffer.pop()
                                    if len(self.splitting_buffer) == 0:
                                        self.ball_selected = None
                                        self.splitting_move = False

                    # Right click
                    if event.button == 3:
                        if self.ball_selected is not None:
                            self.ball_selected = None
                            self.splitting_move = False
                            self.splitting_buffer = []
                            continue

                        for playball in self.playballs:
                            id = playball.handle_click(pos)

                            if id is None:
                                continue

                            colors = self.filtered(self.state.graph[id])
                            if len(colors) < 2:
                                continue

                            self.ball_selected = id
                            self.splitting_move = True
                            self.splitting_buffer = colors

    # Draw the screen
    def draw(self):
        if self.mode == "Menu":
            self.draw_menu()
        elif self.mode == "Level":
            self.draw_level_select()
        elif self.mode == "Algorithm":
            self.draw_algorithm_select()
        elif self.mode == "Game":
            self.draw_game()
        elif self.mode == "Solution":
            self.draw_solution()

    # Draw the menu
    def draw_menu(self):
        self.screen.fill(BG_COLOR)

        self.draw_graph(self.state.graph, (350, HEIGHT // 2), 1)

        self.write_text("Drops of Light", 48,
                        (WIDTH // 2 + 100, 100), (255, 0, 255))
        self.write_text("1.     Play", 28,
                        (WIDTH // 2 + 100, HEIGHT // 2 - 50))
        self.write_text("2.     Solve", 28, (WIDTH // 2 + 100, HEIGHT // 2))
        self.write_text("3.     Select Level", 28,
                        (WIDTH // 2 + 100, HEIGHT // 2 + 50))

        self.write_text("0.     Quit", 28,
                        (WIDTH // 2 + 100, HEIGHT // 2 + 150))

        if self.failed:
            self.write_text(
                "Time Limit Exceeded", 28, (
                    WIDTH // 2 + 100, HEIGHT // 2 + 200), (128, 0, 0)
            )

        pygame.display.flip()

    # Draw the level select screen
    def draw_level_select(self):
        self.screen.fill(BG_COLOR)

        self.draw_graph(self.state.graph, (350, HEIGHT // 2), 1)

        self.write_text("Drops of Light", 48,
                        (WIDTH // 2 + 100, 100), (255, 0, 255))
        self.write_text("Choose a level", 36,
                        (WIDTH // 2 + 100, HEIGHT // 2 - 125))
        for i, level in enumerate(self.levels):
            color = (255, 255, 255) if level == self.level else (128, 128, 128)
            self.write_text(
                f"{i + 1}.     Level {level}",
                28,
                (WIDTH // 2 + 100, HEIGHT // 2 - 50 + 50 * i),
                color,
            )

        pygame.display.flip()

    # Draw the algorithm select screen
    def draw_algorithm_select(self):
        self.screen.fill(BG_COLOR)

        self.draw_graph(self.state.graph, (350, HEIGHT // 2), 1)

        self.write_text("Drops of Light", 48,
                        (WIDTH // 2 + 100, 100), (255, 0, 255))
        self.write_text(
            "Choose an algorithm", 36, (WIDTH // 2 + 100, HEIGHT // 2 - 125)
        )
        for i, algorithm in enumerate(self.algorithms):
            self.write_text(
                f"{i + 1}.     {algorithm}",
                28,
                (WIDTH // 2 + 100, HEIGHT // 2 - 50 + 50 * i),
            )

        pygame.display.flip()

    # Draw the loading screen
    def draw_loading(self):
        self.screen.fill(BG_COLOR)
        self.write_text(
            "Solving...", 48, (WIDTH // 2 - 100, HEIGHT //
                               2 - 50), (255, 0, 255)
        )
        self.write_text(
            "This may take a while", 36, (WIDTH // 2 - 170, HEIGHT // 2 + 50)
        )

        pygame.display.flip()

    # Draw the game
    def draw_solution(self):
        self.screen.fill(BG_COLOR)

        # Draw the current and goal states
        self.draw_graph(self.state.graph, (350, HEIGHT // 2), 1, True)
        self.draw_graph(self.state.goal, (675, HEIGHT // 2 - 150), 0.5)

        # Draw the energy, and the evaluation if the algorithm is an informed search
        self.write_text(f"Level {self.level}", 28, (600, HEIGHT // 2 + 75))
        self.write_text("Energy:", 28, (600, HEIGHT // 2 + 150))
        self.write_text(
            f"{self.state.energy}", 28, (750, HEIGHT // 2 + 150), (255, 255, 0)
        )

        if self.algorithm == "A*":
            self.write_text("Evaluation:", 28, (600, HEIGHT // 2 + 200))
            self.write_text(
                f"{self.state.eval()}", 28, (750, HEIGHT // 2 + 200), (0, 255, 0)
            )

        # Draw the solution and the time it took to solve the level
        self.write_text(
            f"Algorithm: {self.algorithm}", 24, (WIDTH //
                                                 2 + 275, 100), (255, 0, 255)
        )
        self.write_text(
            f"Took {self.time / 1000:.2f} seconds", 20, (WIDTH // 2 + 275, 150)
        )

        for i, move in enumerate(self.solution[max(0, self.move - 15): self.move]):
            self.write_text(
                f"{i + 1}.  {get_color(move[3])} from {move[1]} to {move[2]}",
                20,
                (WIDTH // 2 + 275, 200 + 25 * i),
            )

        pygame.display.flip()

    # Draw the game
    def draw_game(self):
        self.screen.fill(BG_COLOR)

        # Draw the current and goal states
        self.draw_playable_graph()
        self.draw_graph(self.state.goal, (WIDTH // 2 +
                        200, HEIGHT // 2 - 150), 0.5)

        # Draw the current level, move and energy
        self.write_text(f"Level {self.level}", 28,
                        (WIDTH // 2 + 150, HEIGHT // 2 + 75))
        self.write_text(
            "Move:", 28, (WIDTH // 2 + 150, HEIGHT // 2 + 150), (255, 255, 255)
        )

        self.write_text(
            f"{self.move}",
            28,
            (WIDTH // 2 + 250, HEIGHT // 2 + 150),
            (255, 255, 0),
        )

        self.write_text("Energy:", 28, (WIDTH // 2 + 150, HEIGHT // 2 + 200))

        self.write_text(
            f"{self.state.energy}",
            28,
            (WIDTH // 2 + 250, HEIGHT // 2 + 200),
            (255, 255, 0),
        )

        self.write_text("u: undo", 20, (WIDTH // 2 + 150,
                        HEIGHT // 2 + 250), (255, 255, 255))

        if self.ball_selected is not None:
            cursor = pygame.mouse.get_pos()

            if not self.splitting_move:
                color = rgb[get_color(self.filtered(
                    self.state.graph[self.ball_selected]))]

            else:
                color = rgb[get_color([self.splitting_buffer[-1]])]

            pygame.draw.circle(self.screen, color, cursor, 10)

        if self.state.is_goal() and self.state.energy >= 0:
            self.write_text(
                "You won!", 48, (WIDTH // 2 + 200,
                                 HEIGHT // 2 - 20), (255, 0, 255)
            )
            self.write_text(
                "Press ESC to go back", 28, (WIDTH //
                                             2 + 200, HEIGHT // 2 + 30), (255, 0, 255)
            )

        if self.state.energy < 0:
            self.write_text(
                "You spent all energy, you lost.", 30, (WIDTH // 2 + 200,
                                                        HEIGHT // 2 - 20), (255, 0, 255)
            )
            self.write_text(
                "Press ESC to go back or keep exploring", 20, (WIDTH //
                                                               2 + 200, HEIGHT // 2 + 30), (255, 0, 255)
            )

        pygame.display.flip()

    # Generate screen positions for each vertex in the graph

    # Takes an offset and scale as parameters to allow for multiple graphs
    # to be drawn on the same screen (i.e. the current and goal states)
    def generate_positions(self, offset=(0, 0), scale=1):
        positions = []

        radius = 120 * scale

        # Center of the graph
        center = (offset[0], offset[1])
        positions.append(center)

        # The inner circle has 12 vertices
        for i in range(12):
            angle = 2 * pi * i / 12
            x = center[0] + radius * cos(angle)
            y = center[1] + radius * -sin(angle)
            positions.append((int(x), int(y)))

        # The outer circle has 6 vertices
        for i in range(6):
            angle = 2 * pi * i / 6
            x = center[0] + 2 * radius * cos(angle)
            y = center[1] + 2 * radius * -sin(angle)
            positions.append((int(x), int(y)))

        return positions

    # Generate the playballs for the graph
    def generate_graph(self):
        self.positions = self.generate_positions((350, HEIGHT // 2), 1)

        for i, pos in enumerate(self.positions):
            self.playballs[i] = Playball(
                self.screen, i, pos, 1)

    # Draw the playable graph
    def draw_playable_graph(self):
        for i in range(19):
            for j in adjacency_list[i]:
                pygame.draw.line(
                    self.screen,
                    (128, 128, 128),
                    self.positions[i],
                    self.positions[j],
                    int(LINE_WIDTH),
                )

        for i, playball in enumerate(self.playballs):
            if i != self.ball_selected:
                color = rgb[get_color(self.state.graph[i])]
                r, g, b = color

                for c in self.state.graph[i]:
                    if c < 0:
                        color = (r // 2, g // 2, b // 2)
                        break

                playball.draw(color)

            else:
                negatives = list(filter(lambda x: x < 0, self.state.graph[i]))
                inverted = list(map(lambda x: -x, negatives))
                color = rgb[get_color(inverted)]
                r, g, b = color

                # if empty, set to gray
                if r == g == b == 64:
                    r, g, b = 128, 128, 128

                playball.draw((r // 2, g // 2, b // 2))

    # Draw the graph
    def draw_graph(self, graph, offset=(0, 0), scale=1, vertex=False):
        positions = self.generate_positions(offset, scale)

        for i in range(19):
            for j in adjacency_list[i]:
                pygame.draw.line(
                    self.screen,
                    (128, 128, 128),
                    positions[i],
                    positions[j],
                    int(LINE_WIDTH * scale),
                )

        for i, pos in enumerate(positions):
            pygame.draw.circle(self.screen, (192, 192, 192),
                               pos, CIRCLE_RADIUS * scale)

            color = rgb[get_color(graph[i])]
            r, g, b = color

            for c in graph[i]:
                if c < 0:
                    color = (r // 2, g // 2, b // 2)
                    break

            pygame.draw.circle(
                self.screen,
                color,
                pos,
                (CIRCLE_RADIUS - 1) * scale,
            )

            offx = 5 if i < 10 else 10

            if vertex:
                self.write_text(
                    str(i),
                    20,
                    (pos[0] - offx, pos[1] - 10),
                    (255 - r, 255 - g, 255 - b),
                )   # Write the vertex number

    # Write text to the screen
    def write_text(
        self,
        text,
        size,
        position,
        color=(255, 255, 255),
    ):
        font = pygame.font.Font(pygame.font.match_font("timesnewroman"), size)
        text = font.render(text, True, color)
        self.screen.blit(text, position)

    # Reset the state to the initial state
    def reset(self):
        self.state = State()
        self.state.set_level(self.level)
        self.solver = Solver(self.state)
        self.solution = None
        self.move = 0
        self.positions = self.generate_positions()
        self.playballs = [None for _ in range(19)]
        self.ball_selected = None
        self.splitting_move = False
        self.splitting_buffer = []
        self.generate_graph()
