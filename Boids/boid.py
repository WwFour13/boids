import pygame

from surfaces import main_screen, main_screen_width, main_screen_height

import math
import random
import angles
from coloring import interpolate_color, replace_color
from balloon import Barrier
from vector import Vector
from typing import Self
from GameObject import GameObject

SIZE = 30
SIGHT_DISTANCE = 65
PERSONAL_SPACE = 25

MAX_SPEED = 120  # per second
MAX_FORCE = 40
ACCELERATION_FACTOR = 800

TRACER_DURATION = 1
TRACES_PER_SECOND = 8
SECONDS_PER_TRACE = 1 / TRACES_PER_SECOND

MAX_VARIATION = math.radians(40)
VARIATION_PERCENTAGE_PER_SECOND = 0.5

IMAGE = pygame.transform.flip(
    pygame.transform.scale(pygame.image.load("Boids/sprites/arrow_white_center.png"),
                           (SIZE, SIZE)),
    True,
    False)
GRADIENT_COLORING = True

REPLACE_COLOR = (255, 255, 255)

TARGET_NEIGHBOUR_COUNT = 10
TOGETHER_COLOR = (84, 135, 229)
ALONE_COLOR = (216, 26, 172)

TRACER_COLOR = (255, 199, 0)
TRACER_FADE_OUT_COLOR = (255, 255, 255)

SIGHT_ALPHA = 50
SIGHT_COLOR = (175, 255, 171)
PERSONAL_SPACE_COLOR = (255, 142, 140)

COHESION_FACTOR = 1.5
SEPARATION_FACTOR = 5.0
ALIGNMENT_FACTOR = 1.5
BARRIER_FACTOR = 50000.0


class Boid(GameObject):
    def __init__(self, x=main_screen_width / 2, y=main_screen_height / 2, direction=Vector()):

        super().__init__(x, y)
        self.image = IMAGE

        self.neighbors_count = 0
        self.color = (0, 0, 0)
        self.coloring_pending_seconds = 0.0

        self.direction: Vector = direction

        self.tracer_points = []
        self.tracer_pending_seconds = 0.0

    @staticmethod
    def average_coordinates(boids):
        x = sum([boid.x for boid in boids]) / len(boids)
        y = sum([boid.y for boid in boids]) / len(boids)
        return x, y

    def __repr__(self):
        return f"X: {self.x}, Y: {self.y}, "

    def __eq__(self, other: Self) -> bool:
        return (self.x == other.x and
                self.y == other.y and
                self.direction.dx == other.direction.dx and
                self.direction.dy == other.direction.dy)

    def __hash__(self):
        return hash((self.x,
                     self.y,
                     self.direction.dx,
                     self.direction.dy))

    def get_radians(self):
        return self.direction.get_radians()

    def intersects(self, other: tuple) -> bool:
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

            if dist := (math.dist(self.get_coordinates(), bar.get_coordinates())) - bar.radius < SIGHT_DISTANCE:
                weight = (SIGHT_DISTANCE - dist) ** 2
                force = Vector()
                dx, dy = self.x - bar.x, bar.y - self.y
                force.set(dx, dy)
                force.set_magnitude(weight)

                barrier_force += (force.dx, force.dy)

        return barrier_force * BARRIER_FACTOR

    def find_flock_direction(self, boids: list[Self], barriers: list[Barrier], dt: float):

        if random.random() < VARIATION_PERCENTAGE_PER_SECOND * dt:
            self.variate()
            #return

        seen_boids = [b for b in boids
                      if math.dist(self.get_coordinates(), b.get_coordinates()) < SIGHT_DISTANCE
                      and b != self]

        self.neighbors_count = len(seen_boids)

        force = Vector()
        force += self.barrier_force(barriers)
        force += self.alignment_force(seen_boids)
        force += self.cohesion_force(seen_boids)
        force += self.separation_force(seen_boids)

        force.clamp_magnitude(MAX_FORCE)

        self.direction += force
        self.direction *= ACCELERATION_FACTOR * dt
        self.direction.clamp_magnitude(MAX_SPEED)

        self.tracer_pending_seconds += dt
        if self.tracer_pending_seconds > SECONDS_PER_TRACE:
            self.tracer_pending_seconds = 0.0
            self.tracer_points.append((self.x, self.y))

        if len(self.tracer_points) > TRACER_DURATION * TRACES_PER_SECOND:
            self.tracer_points.pop(0)

    def flock_from_chunk(self, chunk: list[GameObject], dt: float):
        boids = []
        barriers = []
        for elem in chunk:
            if isinstance(elem, Boid):
                boids.append(elem)
            if isinstance(elem, Barrier):
                barriers.append(elem)
        self.find_flock_direction(boids, barriers, dt)

    def variate(self):
        random_angle_variation = random.uniform(-MAX_VARIATION, MAX_VARIATION)
        self.direction.rotate(random_angle_variation)

    def draw(self):
        rad = self.get_radians()
        quadrant = angles.get_quadrant(rad)

        image = IMAGE

        if GRADIENT_COLORING:
            neighbor_percentage = min((self.neighbors_count / TARGET_NEIGHBOUR_COUNT), 1)
            self.color = interpolate_color(ALONE_COLOR, TOGETHER_COLOR, neighbor_percentage)
            image = replace_color(image, old_color=REPLACE_COLOR, new_color=self.color)

        if quadrant in (1, 4):
            image = pygame.transform.rotate(image, math.degrees(rad))
        else:
            image = pygame.transform.flip(
                pygame.transform.rotate(image, 180 - math.degrees(rad)), True, False)

        w = image.get_width()
        h = image.get_height()
        left = self.x - w / 2
        top = self.y - h / 2

        main_screen.blit(image, (left, top))

    def draw_sight(self):

        circle = pygame.Surface((SIGHT_DISTANCE * 2, SIGHT_DISTANCE * 2), pygame.SRCALPHA)
        (pygame.draw.circle
         (circle, color=(*SIGHT_COLOR, SIGHT_ALPHA), center=(SIGHT_DISTANCE, SIGHT_DISTANCE), radius=SIGHT_DISTANCE))
        main_screen.blit(circle, (self.x - SIGHT_DISTANCE, self.y - SIGHT_DISTANCE))

    def draw_personal_space(self):
        pygame.draw.circle(main_screen, PERSONAL_SPACE_COLOR, self.get_coordinates(), PERSONAL_SPACE)

    def draw_tracers(self):

        for i, (p1, p2) in enumerate(zip(self.tracer_points[:-1], self.tracer_points[1:])):
            color = interpolate_color(TRACER_FADE_OUT_COLOR, TRACER_COLOR, i / len(self.tracer_points))
            alpha = int(255 * (len(self.tracer_points) - i) / len(self.tracer_points))
            color = (color[0], color[1], color[2], alpha)
            pygame.draw.line(main_screen, color, p1, p2, 2)
