import pygame

from surfaces import main_screen, main_screen_width, main_screen_height

import math
import random
import angles
from vector import Vector
from typing import Self

BOID_SIZE = 30
BOID_SIGHT_DISTANCE = 90
BOID_PERSONAL_SPACE = 60
BOID_MAX_SPEED = 120  # per second
BOID_MAX_FORCE = 20
BOID_ACCELERATION_FACTOR = 80
BOID_MAX_VARIATION = math.radians(50)
BOID_VARIATION_PERCENTAGE_PER_SECOND = 0.5

BOID_IMAGE = pygame.transform.flip(
    pygame.transform.scale(pygame.image.load("sprites/arrow.png"),
                           (BOID_SIZE, BOID_SIZE)),
    True,
    False)
BOID_SIGHT_COLOR = (175, 255, 171)

COHESION_FACTOR = 0.5
SEPARATION_FACTOR = 1.0
ALIGNMENT_FACTOR = 1.0
WALL_FACTOR = 0.0
BARRIER_FACTOR = 10


class Boid:
    def __init__(self,
                 x=main_screen_width / 2,
                 y=main_screen_height / 2,
                 direction=Vector(), ):
        self.image = BOID_IMAGE
        self.sight_color = BOID_SIGHT_COLOR
        self.x: float = x
        self.y: float = y
        self.direction: Vector = direction

    @staticmethod
    def average_coordinates(boids):
        x = sum([boid.x for boid in boids]) / len(boids)
        y = sum([boid.y for boid in boids]) / len(boids)
        return x, y

    def __repr__(self):
        return f"X: {self.x}, Y: {self.y}, "

    def __eq__(self, other: Self) -> bool:

        return self.x == other.x and self.y == other.y and self.direction == other.direction

    def get_radians(self):
        return self.direction.get_radians()

    def get_coordinates(self):
        return self.x, self.y

    def move(self, dt: float):
        self.x += self.direction.x * dt
        self.y -= self.direction.y * dt

        self.x %= main_screen_width
        self.y %= main_screen_height

    def cohesion_force(self, seen_boids: list[Self]) -> Vector:
        if not seen_boids:
            return Vector(0, 0)

        avg_x = sum([boid.x for boid in seen_boids]) / len(seen_boids)
        avg_y = sum([boid.y for boid in seen_boids]) / len(seen_boids)
        to_average_position = Vector(avg_x - self.x, avg_y - self.y)
        cohesion_force = to_average_position - self.direction
        return cohesion_force * COHESION_FACTOR

    def alignment_force(self, seen_boids: list[Self]) -> Vector:
        if not seen_boids:
            return Vector(0, 0)

        average_direction = Vector.average([boid.direction for boid in seen_boids])
        alignment_force = average_direction - self.direction
        return alignment_force * ALIGNMENT_FACTOR

    def separation_force(self, seen_boids: list[Self]) -> Vector:
        if not seen_boids:
            return Vector(0, 0)

        personal_boids = [boid for boid in seen_boids
                          if math.dist(self.get_coordinates(), boid.get_coordinates()) < BOID_PERSONAL_SPACE]

        if not personal_boids:
            return Vector(0, 0)

        avg_x, avg_y = self.average_coordinates(personal_boids)
        to_average_position = Vector(avg_x - self.x, avg_y - self.y)
        away_from_average = to_average_position.get_opposite()
        separation_force = away_from_average - self.direction
        return separation_force * SEPARATION_FACTOR

    def barrier_force(self, barriers):
        pass

    def wall_force(self) -> Vector:

        left_dist = self.x
        right_dist = main_screen_width - self.x
        top_dist = self.y
        bottom_dist = main_screen_height - self.y

        left_mult = max(BOID_SIGHT_DISTANCE - left_dist, 0)
        right_mult = max(BOID_SIGHT_DISTANCE - right_dist, 0)
        top_mult = max(BOID_SIGHT_DISTANCE - top_dist, 0)
        bottom_mult = max(BOID_SIGHT_DISTANCE - bottom_dist, 0)

        desired_direction = Vector(left_mult - right_mult, top_mult - bottom_mult)
        desired_direction = Vector(right_mult - left_mult, bottom_mult - top_mult)
        wall_force = desired_direction - self.direction
        return wall_force * WALL_FACTOR



    def find_flock_direction(self, all_boids: list[Self], dt: float):
        seen_boids = [boid for boid in all_boids
                      if math.dist(self.get_coordinates(), boid.get_coordinates()) < BOID_SIGHT_DISTANCE
                      and boid != self]

        if not seen_boids:
            return

        force = Vector()
        force += self.alignment_force(seen_boids)
        force += self.cohesion_force(seen_boids)
        force += self.separation_force(seen_boids)
        force += self.wall_force()
        force.clamp_magnitude(BOID_MAX_FORCE)

        self.direction += force
        self.direction *= BOID_ACCELERATION_FACTOR * dt
        self.direction.clamp_magnitude(BOID_MAX_SPEED)

        if random.random() < BOID_VARIATION_PERCENTAGE_PER_SECOND * dt:
            self.variate()

    def variate(self):
        random_angle_variation = random.uniform(-BOID_MAX_VARIATION, BOID_MAX_VARIATION)
        self.direction.rotate(random_angle_variation)

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

        main_screen.blit(image, (left, top))

    def draw_sight(self):
        pygame.draw.circle(main_screen, self.sight_color, self.get_coordinates(), BOID_SIGHT_DISTANCE)
