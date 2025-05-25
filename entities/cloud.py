import math

import pygame

import random

from calculations.vector import Vector
from entities.balloon import Balloon
from entity import Entity
from surfaces import main_screen, main_screen_width, main_screen_height


class Cloud(Balloon):

    IMAGE = pygame.image.load("sprites/cloud.png")

    AMPLITUDE = 1
    CYCLE_SECONDS = 3
    WAVE_LENGTH = 2 * math.pi / CYCLE_SECONDS
    COLOR_ALPHA = 200

    def __init__(self,
                 x: float,
                 y: float,
                 direction: Vector = Vector(10, 3),
                 radius: float = 0.0):

        self.image = pygame.transform.scale(self.IMAGE, (0, 0))
        self.direction = direction
        super().__init__(x, y, radius)
        c = random.randint(210, 240)
        self.color = (c, c, c, Cloud.COLOR_ALPHA)
        self.MAX_RADIUS = 20

    def move(self,
             chunk: list[Entity],
             dt,
             run_time_seconds):

        self.x += self.direction.dx * dt

        wave_offset = math.sin(run_time_seconds * self.WAVE_LENGTH) * self.AMPLITUDE
        self.y += wave_offset

        forces = [f.pointer() for f in chunk
                  if f is not self
                  and f.pointer() is not None
                  and math.dist(self.get_coordinates(), f.get_coordinates()) < self.radius
                  ]

        force = Vector.get_sum(forces) / 20
        self.x += force.dx * dt
        self.y -= force.dy * dt

        self.x %= main_screen_width
        self.y %= main_screen_height

    def draw(self):

        if self.radius == 0:
            return

        circle_surface = pygame.Surface((main_screen_width, main_screen_height), pygame.SRCALPHA)

        pygame.draw.circle(circle_surface, self.color, (self.x, self.y), self.radius)

        x = (self.x + self.radius) % main_screen_width - self.radius
        y = (self.y + self.radius) % main_screen_height - self.radius

        pygame.draw.circle(circle_surface, self.color, (x, y), self.radius)

        x = (self.x - self.radius) % main_screen_width + self.radius
        y = (self.y - self.radius) % main_screen_height + self.radius

        pygame.draw.circle(circle_surface, self.color, (x, y), self.radius)

        main_screen.blit(circle_surface, (0, 0))

