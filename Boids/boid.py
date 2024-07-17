import pygame

import math
import angles
from vector import Vector
from typing import Self


BOID_SIZE = 30
BOID_SIGHT_DISTANCE = 70
BOID_MAX_SPEED = 50
BOID_MAX_FORCE = 20

BOID_IMAGE = pygame.transform.flip(
    pygame.transform.scale(pygame.image.load("sprites/arrow.png"),
                           (BOID_SIZE, BOID_SIZE)),
    True,
    False)
BOID_SIGHT_COLOR = (175, 255, 171)


class Boid:
    def __init__(self,
                 x,
                 y,
                 direction=Vector(),):
        self.image = BOID_IMAGE
        self.sight_color = BOID_SIGHT_COLOR
        self.x: float = x
        self.y: float = y
        self.direction = direction

    def __repr__(self):
        return f"X: {self.x}, Y: {self.y}, "

    def __eq__(self, other: Self) -> bool:

        return self.x == other.x and self.y == other.y and self.direction == other.direction

    def get_radians(self):
        return self.direction.get_radians()

    def distance_to(self, other: Self):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def move(self, dt: float):
        self.x += self.direction.x * dt
        self.y -= self.direction.y * dt

    def cohesion_force(self, seen_boids: list[Self]) -> Vector:
        if not seen_boids:
            return Vector(0, 0)

        center_x = sum(boid.x for boid in seen_boids) / len(seen_boids)
        center_y = sum(boid.y for boid in seen_boids) / len(seen_boids)
        direction_to_center = Vector(center_x - self.x, center_y - self.y)
        return direction_to_center - self.direction

    def alignment_force(self, seen_boids: list[Self]) -> Vector:
        if not seen_boids:
            return Vector(0, 0)

        average_direction = Vector.average([boid.direction for boid in seen_boids])
        return average_direction - self.direction

    def find_flock_direction(self, all_boids: list[Self]):
        seen_boids = [boid for boid in all_boids if self.distance_to(boid) < BOID_SIGHT_DISTANCE and boid != self]

        if not seen_boids:
            return

    def get_image_with_top_left(self):
        rad = self.get_radians()
        quadrant = angles.get_quadrant(rad)

        if quadrant in (1, 4):
            image = pygame.transform.rotate(BOID_IMAGE, math.degrees(rad))
        else:
            image = pygame.transform.flip(
                pygame.transform.rotate(BOID_IMAGE, 180 - math.degrees(rad)), True, False)

        w = image.get_width()
        h = image.get_height()
        left = self.x - w / 2
        top = self.y - h / 2

        return image, (left, top)

    def get_coordinates(self):
        return self.x, self.y

    def draw(self):
        rad = self.get_radians()
        quadrant = angles.get_quadrant(rad)

        if quadrant in (1, 4):
            image = pygame.transform.rotate(BOID_IMAGE, math.degrees(rad))
        else:
            image = pygame.transform.flip(
                pygame.transform.rotate(BOID_IMAGE, 180 - math.degrees(rad)), True, False)

        w = image.get_width()
        h = image.get_height()
        left = self.x - w / 2
        top = self.y - h / 2