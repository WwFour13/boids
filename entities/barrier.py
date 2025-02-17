import math

import pygame

from entities.balloon import Balloon
from surfaces import main_screen
from vector import Vector


class Barrier(Balloon):

    IMAGE = pygame.image.load("sprites/barrier.png")

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
        image = pygame.transform.scale(self.IMAGE, (self.radius * 2, self.radius * 2))
        main_screen.blit(image, (self.x - self.radius, self.y - self.radius))

    def boid_pusher_scale(self, coordinates: tuple, sight_distance: float) -> Vector:
        x, y = coordinates
        force = Vector(0, 0)
        if dist := (math.dist(self.get_coordinates(), coordinates) - self.radius) < sight_distance:
            weight = (sight_distance - dist) ** 2
            force.dx = x - self.x
            force.dy = self.y - y
            force.set_magnitude(weight)

        return force * 100
