import math

import pygame

import random

from calculations.vector import Vector

from entities.balloon import Balloon
from entity import Entity
from surfaces import main_screen, main_screen_width, main_screen_height


class Cloud(Balloon):

    IMAGE = pygame.image.load("sprites/cloud.png")

    HORIZONTAL_DRIFT_SPEED = 20
    AMPLITUDE = 2
    CYCLE_SECONDS = 3
    WAVE_LENGTH = 2 * math.pi / CYCLE_SECONDS
    BORDER_THICKNESS = 3
    OVERLAP_BLOCK_PERCENT = 0.8

    def __init__(self,
                 x: float,
                 y: float,
                 direction: Vector = Vector(0,0),
                 radius: float = 0.0):

        self.image = pygame.transform.scale(self.IMAGE, (0, 0))
        self.direction = direction
        super().__init__(x, y, radius)
        c = random.randint(235, 255)
        self.color = (c, c, c)
        self.MAX_RADIUS = 20
        self.MIN_RADIUS = 6


    def get_cloud_merge_point(self, cloud_coordinates: tuple, cloud_radius: float) -> tuple[float, float] | None:
        direction_to_self = Vector(
            self.x - cloud_coordinates[0],
            cloud_coordinates[1] - self.y
            )

        mag = direction_to_self.get_magnitude()
        direction_to_self.set_magnitude(mag - (cloud_radius + self.radius) * self.OVERLAP_BLOCK_PERCENT)

        merge_point = cloud_coordinates[0] + direction_to_self.dx, cloud_coordinates[1] + direction_to_self.dy
        return merge_point


    def move(self,
             dt,
             run_time_seconds):

        #self.x += self.direction.dx
        #self.y -= self.direction.dy

        self.x += self.HORIZONTAL_DRIFT_SPEED * dt
        self.y += math.sin(run_time_seconds * self.WAVE_LENGTH) * self.AMPLITUDE

        self.x %= main_screen_width
        self.y %= main_screen_height


    def drift(self,
              chunk: list[Entity],
              dt,):

        points = [elem.get_cloud_merge_point for elem in chunk]



    def draw(self):

        if self.radius == 0:
            return

        circle_surface = pygame.Surface((2 * self.radius, 2 * self.radius), pygame.SRCALPHA)

        pygame.draw.circle(circle_surface, self.color, (self.radius, self.radius), self.radius)
        pygame.draw.circle(circle_surface, tuple((v-20) for v in self.color), (self.radius, self.radius), self.radius, self.BORDER_THICKNESS)
        main_screen.blit(circle_surface, (self.x - self.radius, self.y - self.radius))

        if self.x + self.radius >= main_screen_width:
            main_screen.blit(circle_surface, (self.x - self.radius - main_screen_width, self.y - self.radius))

        if self.x - self.radius <= 0:
            main_screen.blit(circle_surface, (self.x - self.radius + main_screen_width, self.y - self.radius))

        if self.y + self.radius >= main_screen_height:
            main_screen.blit(circle_surface, (self.x - self.radius, self.y - self.radius - main_screen_height))

        if self.y - self.radius <= 0:
            main_screen.blit(circle_surface, (self.x - self.radius, self.y - self.radius + main_screen_height))
