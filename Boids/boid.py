import pygame

import math
import angles
import vector
from typing import Self


BOID_SIZE = 30
BOID_SIGHT_DISTANCE = 70
BOID_MAX_SPEED = 50
BOID_MAX_FORCE = 20

BOID_IMAGE = pygame.transform.flip(
    pygame.transform.scale(pygame.image.load("sprites/arrow.png"), (BOID_SIZE, BOID_SIZE)), True, False)
BOID_SIGHT_COLOR = (175, 255, 171)



class Boid:
    def __init__(self,
                 x,
                 y,
                 direction=vector.Vector(), ):
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

    def cohesion_force(self, seen_boids: list[Self]) -> vector.Vector:
        if not seen_boids:
            return vector.Vector(0, 0)

        center_x = sum(boid.x for boid in seen_boids) / len(seen_boids)
        center_y = sum(boid.y for boid in seen_boids) / len(seen_boids)
        direction_to_center = vector.Vector(center_x - self.x, center_y - self.y)
        return direction_to_center - self.direction

    def alignment_force(self, seen_boids: list[Self]) -> vector.Vector:
        if not seen_boids:
            return vector.Vector(0, 0)

        average_direction = vector.Vector.average([boid.direction for boid in seen_boids])
        return average_direction - self.direction

    def find_flock_direction(self, all_boids: list[Self]):
        seen_boids = [boid for boid in all_boids if self.distance_to(boid) < BOID_SIGHT_DISTANCE and boid != self]

        if not seen_boids:
            return

        force = self.cohesion_force(seen_boids) + self.alignment_force(seen_boids)# + self.separation_force(seen_boids)
        force.clamp_magnitude(BOID_MAX_FORCE)
        self.direction += force
        self.direction.clamp_magnitude(BOID_MAX_SPEED)

    def get_image(self):
        rad = self.get_radians()
        quadrant = angles.get_quadrant(rad)

        if quadrant in (1, 4):
            return pygame.transform.rotate(BOID_IMAGE, math.degrees(rad))
        else:
            return pygame.transform.flip(
                pygame.transform.rotate(BOID_IMAGE, 180 - math.degrees(rad)), True, False)

    def get_coordinates(self):
        return self.x, self.y

    def get_top_left_coordinates(self):
        left = self.x - BOID_SIZE / 2
        top = self.y - BOID_SIZE / 2
        return (left, top)
