import pygame

import math

from surfaces import main_screen, main_screen_width, main_screen_height
from vector import Vector


class Balloon:
    def __init__(self,
                 x: float,
                 y: float,
                 radius: float = 0.0):

        self.radius = radius
        self.GROWTH_RATE = 50

        self.y = y
        self.x = x

        self.MIN_RADIUS = min(main_screen_width, main_screen_height) / 80
        self.MAX_RADIUS = min(main_screen_width, main_screen_height) / 15

    def get_coordinates(self) -> tuple[float, float]:
        return self.x, self.y

    def set_coordinates(self, coordinates):
        x, y = coordinates
        self.x = x
        self.y = y

    def get_radius(self):
        return self.radius

    def intersects(self, other_coordinates):
        return math.dist(self.get_coordinates(), other_coordinates) < self.radius

    def expand(self, dt):
        self.radius += self.GROWTH_RATE * dt
        self.radius = min(self.radius, self.MAX_RADIUS)

    def draw(self):
        raise NotImplementedError("Draw method not implemented")


class Barrier(Balloon):
    def __init__(self,
                 x: float,
                 y: float,
                 pop: bool,
                 radius: float = 0.0):

        self.pop = pop
        self.COLOR = (255, 0, 0)

        super().__init__(x, y, radius)

    def __repr__(self):
        return f"X: {self.x}, Y: {self.y}, Radius: {self.radius}, Pop: {self.pop}"

    def draw(self):
        pygame.draw.circle(main_screen, self.COLOR, (self.x, self.y), self.radius)


class Cloud(Balloon):

    IMAGE = pygame.image.load("sprites/cloud.png")

    def __init__(self,
                 x: float,
                 y: float,
                 direction: Vector = Vector(20, 0),
                 radius: float = 0.0):

        self.image = pygame.transform.scale(self.IMAGE, (0, 0))
        self.direction = direction
        super().__init__(x, y, radius)

    def move(self, dt):
        self.x += self.direction.dx * dt
        self.y += self.direction.dy * dt

        self.x %= main_screen_width
        self.y %= main_screen_height

    def draw(self):

        if self.radius == 0:
            return

        scale_factor = (self.radius * 2) / min(self.IMAGE.get_width(), self.IMAGE.get_height())
        w = int(self.IMAGE.get_width() * scale_factor)
        h = int(self.IMAGE.get_height() * scale_factor)
        self.image = pygame.transform.scale(self.IMAGE, (w, h))
        self.image.set_alpha(180)
        main_screen.blit(self.image, (self.x - (w / 2), self.y - (h / 2)))
