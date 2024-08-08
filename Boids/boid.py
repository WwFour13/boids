import pygame

from surfaces import main_screen, main_screen_width, main_screen_height

import math
import random
import angles
from balloon import Barrier
from vector import Vector
from typing import Self

SIZE = 30
SIGHT_DISTANCE = 80
PERSONAL_SPACE = 25

MAX_SPEED = 120  # per second
MAX_FORCE = 20
ACCELERATION_FACTOR = 80

MAX_VARIATION = math.radians(50)
VARIATION_PERCENTAGE_PER_SECOND = 0.5

IMAGE = pygame.transform.flip(
    pygame.transform.scale(pygame.image.load("sprites/arrow.png"),
                           (SIZE, SIZE)),
    True,
    False)

SIGHT_COLOR = (175, 255, 171)
PERSONAL_SPACE_COLOR = (255, 142, 140)

COHESION_FACTOR = 1.0
SEPARATION_FACTOR = 10.0
ALIGNMENT_FACTOR = 1.5
BARRIER_FACTOR = 500.0


class Boid:
    def __init__(self,
                 x=main_screen_width / 2,
                 y=main_screen_height / 2,
                 direction=Vector(), ):
        self.image = IMAGE
        self.sight_color = SIGHT_COLOR
        self.personal_space_color = PERSONAL_SPACE_COLOR
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

    def in_personal_space(self, other: tuple) -> bool:
        return math.dist((self.x, self.y), other) < PERSONAL_SPACE

    def move(self, dt: float):
        self.x += self.direction.dx * dt
        self.y -= self.direction.dy * dt

        if self.x < 0:
            self.direction.dx *= -1
            self.x = 0

        if self.y < 0:
            self.direction.dy *= -1
            self.y = 0

        if self.x > main_screen_width:
            self.direction.dx *= -1
            self.x = main_screen_width

        if self.y > main_screen_height:
            self.direction.dy *= -1
            self.y = main_screen_height

    def cohesion_force(self, seen_boids: list[Self]) -> Vector:
        if not seen_boids:
            return Vector(0, 0)

        avg_x, avg_y = self.average_coordinates(seen_boids)
        to_average_position = Vector(avg_x - self.x, self.y - avg_y)
        cohesion_force = to_average_position - self.direction
        return cohesion_force * COHESION_FACTOR

    def alignment_force(self, seen_boids: list[Self]) -> Vector:
        if not seen_boids:
            return Vector(0, 0)

        average_direction = Vector.get_average([boid.direction for boid in seen_boids])
        alignment_force = average_direction - self.direction
        return alignment_force * ALIGNMENT_FACTOR

    def separation_force(self, seen_boids: list[Self]) -> Vector:
        if not seen_boids:
            return Vector(0, 0)

        personal_boids = [boid for boid in seen_boids
                          if math.dist(self.get_coordinates(), boid.get_coordinates()) < PERSONAL_SPACE]

        if not personal_boids:
            return Vector(0, 0)

        separation_force = self.cohesion_force(personal_boids).get_opposite()
        return separation_force * SEPARATION_FACTOR

    def barrier_force(self, barriers: list[Barrier]) -> Vector:
        barrier_force = Vector(0, 0)

        for bar in barriers:

            if (dist := ((math.dist(self.get_coordinates(), bar.get_coordinates())) - bar.radius)
                    < SIGHT_DISTANCE):
                weight = (SIGHT_DISTANCE - dist) ** 2
                force = Vector()
                dx, dy = self.x - bar.x, bar.y - self.y
                force.set(dx, dy)
                force.set_magnitude(weight)

                barrier_force += (force.dx, force.dy)

        return barrier_force * BARRIER_FACTOR

    def find_flock_direction(self, all_boids: list[Self], barriers: list[Barrier], dt: float):

        if random.random() < VARIATION_PERCENTAGE_PER_SECOND * dt:
            self.variate()

        force = Vector()
        force += self.barrier_force(barriers)

        seen_boids = [boid for boid in all_boids
                      if math.dist(self.get_coordinates(), boid.get_coordinates()) < SIGHT_DISTANCE
                      and boid != self]

        force += self.alignment_force(seen_boids)
        force += self.cohesion_force(seen_boids)
        force += self.separation_force(seen_boids)

        force.clamp_magnitude(MAX_FORCE)

        self.direction += force
        self.direction *= ACCELERATION_FACTOR * dt
        self.direction.clamp_magnitude(MAX_SPEED)

    def variate(self):
        random_angle_variation = random.uniform(-MAX_VARIATION, MAX_VARIATION)
        self.direction.rotate(random_angle_variation)

    def draw(self):
        rad = self.get_radians()
        quadrant = angles.get_quadrant(rad)

        if quadrant in (1, 4):
            image = pygame.transform.rotate(IMAGE, math.degrees(rad))
        else:
            image = pygame.transform.flip(
                pygame.transform.rotate(IMAGE, 180 - math.degrees(rad)), True, False)

        w = image.get_width()
        h = image.get_height()
        left = self.x - w / 2
        top = self.y - h / 2

        main_screen.blit(image, (left, top))

    def draw_sight(self):

        circle = pygame.Surface((SIGHT_DISTANCE * 2, SIGHT_DISTANCE * 2), pygame.SRCALPHA)
        pygame.draw.circle(circle, color=self.sight_color, center=(SIGHT_DISTANCE, SIGHT_DISTANCE), radius=SIGHT_DISTANCE)
        circle.set_alpha(50)
        main_screen.blit(circle, (self.x - SIGHT_DISTANCE, self.y - SIGHT_DISTANCE))

    def draw_personal_space(self):
        pygame.draw.circle(main_screen, self.personal_space_color, self.get_coordinates(), PERSONAL_SPACE)
