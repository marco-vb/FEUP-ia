import pygame
from utils import *

CIRCLE_RADIUS = 15

BACKGROUND = (192, 192, 192)


# Define the GUI's playball/vertex
class Playball:
    # Initialize the playball, set the screen, id, position and scale
    def __init__(self, screen, id, pos, scale):
        self.screen = screen
        self.id = id
        self.x = pos[0]
        self.y = pos[1]
        self.pos = pos
        self.scale = scale
        self.selected = False

    # Draw the playball on the screen with the given color
    def draw(self, color):
        pygame.draw.circle(
            self.screen, BACKGROUND, self.pos, CIRCLE_RADIUS * self.scale
        )

        pygame.draw.circle(
            self.screen,
            color,
            self.pos,
            (CIRCLE_RADIUS - 1) * self.scale,
        )

    # Handle the click on the playball
    def handle_click(self, pos):
        x, y = pos

        if (x - self.x) ** 2 + (y - self.y) ** 2 <= CIRCLE_RADIUS**2:
            if self.selected:
                self.selected = False

            return self.id

        return None
