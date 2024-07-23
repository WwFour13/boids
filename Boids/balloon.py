import pygame

import math

from surfaces import main_screen, main_screen_width, main_screen_height


class Balloon:
    def __init__(self,
                 x: float,
                 y: float,
                 pop: bool,
                 radius: float = 0.0):

        self.x = x
        self.y = y
        self.radius = radius
        self.pop = pop

        self.GROWTH_RATE = 50
        self.MAX_RADIUS = min(main_screen_width, main_screen_height) / 15
        self.COLOR = (255, 0, 0)

    def get_coordinates(self) -> tuple[float, float]:
        return self.x, self.y

    def set_coordinates(self, coordinates):
        x, y = coordinates
        self.x = x
        self.y = y

    def get_radius(self):
        return self.radius

    def intersects(self, *other_coordinates):
        return math.dist(self.get_coordinates(), other_coordinates) < self.radius

    def expand(self, dt):
        self.radius += self.GROWTH_RATE * dt
        self.radius = min(self.radius, self.MAX_RADIUS)

    def draw(self):
        pygame.draw.circle(main_screen, self.COLOR, (self.x, self.y), self.radius)
