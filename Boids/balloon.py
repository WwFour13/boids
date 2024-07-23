import pygame

from surfaces import main_screen, main_screen_width, main_screen_height

class Balloon:
    def __init__(self, x: float, y: float, pop: bool, radius=0.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.pop = pop

        self.GROWTH_RATE = 5
        self.MAX_RADIUS = min(main_screen_width, main_screen_height) / 6
        self.COLOR = (255, 0, 0)

    def get_coordinates(self):
        return self.x, self.y

    def get_radius(self):
        return self.radius

    def expand(self, dt):
        self.radius += self.GROWTH_RATE * dt
        self.radius = min(self.radius, self.MAX_RADIUS)

    def draw(self):
        pygame.draw.circle(main_screen, self.COLOR, (self.x, self.y), self.radius)