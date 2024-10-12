import math

import pygame

from calculations.vector import Vector
from entities.balloon import Balloon
from surfaces import main_screen, main_screen_width, main_screen_height


class Cloud(Balloon):

    IMAGE = pygame.image.load("sprites/cloud.png")

    AMPLITUDE = 1
    CYCLE_SECONDS = 3
    WAVE_LENGTH = 2 * math.pi / CYCLE_SECONDS

    def __init__(self,
                 x: float,
                 y: float,
                 direction: Vector = Vector(20, 0),
                 radius: float = 0.0):

        self.image = pygame.transform.scale(self.IMAGE, (0, 0))
        self.direction = direction
        super().__init__(x, y, radius)

    def move(self, dt, run_time_seconds):

        self.x += self.direction.dx * dt

        wave_offset = math.sin(run_time_seconds * self.WAVE_LENGTH) * self.AMPLITUDE
        self.y += wave_offset

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

        left = self.x - (w / 2)
        top = self.y - (h / 2)
        right = left + w
        bottom = top + h

        main_screen.blit(self.image, (left, top))

        if right > main_screen_width:
            main_screen.blit(self.image, (left - main_screen_width, top))
        if left < 0:
            main_screen.blit(self.image, (left + main_screen_width, top))

        if bottom > main_screen_height:
            main_screen.blit(self.image, (left, top - main_screen_height))
        if top < 0:
            main_screen.blit(self.image, (left, top + main_screen_height))
