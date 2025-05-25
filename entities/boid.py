import pygame

from surfaces import main_screen, main_screen_width, main_screen_height

import math
import random
from calculations import angles
from calculations.coloring import interpolate_color, replace_color
from calculations.vector import Vector
from typing import Self
from entities.entity import Entity

SIZE = 20
SIGHT_DISTANCE = 55
PERSONAL_SPACE = 20

MAX_SPEED = 165  # per second
MIN_SPEED = 140
MAX_FORCE = 40

TRACER_DURATION = 0.4
TRACES_PER_SECOND = 100
SECONDS_PER_TRACE = 1 / TRACES_PER_SECOND

MAX_VARIATION = math.radians(40)
VARIATION_PERCENTAGE_PER_SECOND = 0.5

IMAGE = pygame.transform.flip(
    pygame.transform.scale(pygame.image.load("sprites/arrow_white_center.png"),
                           (SIZE, SIZE)),
    True,
    False)
GRADIENT_COLORING = True

REPLACE_COLOR = (255, 255, 255)

TARGET_NEIGHBOUR_COUNT = 10
TOGETHER_COLOR = (89, 121, 181)
ALONE_COLOR = (166, 75, 126)

TRACER_COLOR = (255, 255, 255)
TRACER_FADE_OUT_COLOR = (255, 255, 255)

SIGHT_ALPHA = 30
SIGHT_COLOR = (175, 255, 171)
PERSONAL_SPACE_COLOR = (255, 142, 140)

COHESION_FACTOR = 1.5
SEPARATION_FACTOR = 5.0
ALIGNMENT_FACTOR = 1.5
WALL_FACTOR = 20.0


class Tracer:
    def __init__(self, x, y, color_main=TRACER_COLOR, max_traces=TRACES_PER_SECOND * TRACER_DURATION):
        self.max_traces = max_traces

        self.points = [(x, y)]
        self.color_main = color_main

    def add_line(self, x, y):
        self.points.append((x, y))

        if len(self.points) > self.max_traces:
            self.points.pop(0)

    def draw(self):
        for i, (p1, p2) in enumerate(zip(self.points, self.points[1:])):
            pygame.draw.line(main_screen, color=self.color_main, start_pos=p1, end_pos=p2, width=min(i//2, 4))


class Boid(Entity):
    def __init__(self, x=main_screen_width / 2, y=main_screen_height / 2, direction=Vector()):

        super().__init__(x, y)
        self.image = IMAGE

        self.neighbors_count = 0
        self.color = (0, 0, 0)
        self.coloring_pending_seconds = 0.0

        self.direction: Vector = direction

        self.tracer = Tracer(self.x, self.y)
        self.tracer_pending_seconds = 0.0

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

    def pusher_scale(self, coordinates: tuple, sight_distance: float) -> Vector:
        x, y = coordinates
        force = Vector(0, 0)
        if dist := (math.dist(self.get_coordinates(), coordinates)) < PERSONAL_SPACE:
            weight = (SIGHT_DISTANCE - dist) ** 2
            force.dx = x - self.x
            force.dy = self.y - y
            force.set_magnitude(weight)

        return force

    def puller_coordinate(self) -> tuple[float, float] | None:
        return self.get_coordinates()

    def pointer(self) -> Vector | None:
        return self.direction

    def cohesion_force(self, coheders: list[tuple[float, float] | None]) -> Vector:

        coheders = [c for c in coheders
                    if c is not None]

        if not coheders:
            return Vector(0, 0)

        avg_x = sum([c[0] for c in coheders]) / len(coheders)
        avg_y = sum([c[1] for c in coheders]) / len(coheders)
        to_average_position = Vector(avg_x - self.x, self.y - avg_y)
        cohesion_force = to_average_position - self.direction
        return cohesion_force

    def alignment_force(self, aligners: list[Vector | None]) -> Vector:

        aligners = [a for a in aligners
                    if a is not None]

        if not aligners:
            return Vector(0, 0)

        average_direction = Vector.get_average(aligners)
        alignment_force = average_direction - self.direction
        return alignment_force

    def separation_force(self, separators: list[Vector | None]) -> Vector:

        separators = [s for s in separators
                      if s is not None]

        if not separators:
            return Vector(0, 0)

        separation_force = Vector.get_sum(separators)
        return separation_force

    def wall_force(self):
        wall = [(0, self.y),
                (main_screen_width, self.y),
                (self.x, 0),
                (self.x, main_screen_height)]

        force = Vector(0, 0)

        for w in wall:
            if dist := math.dist(w, self.get_coordinates()) < SIGHT_DISTANCE:
                f = Vector(0, 0)
                weight = (SIGHT_DISTANCE - dist) ** 2
                f.dx = self.x - w[0]
                f.dy = w[1] - self.y
                f.set_magnitude(weight)
                force += f

        return force

    def flock(self, chunk: list[Entity],
              dt: float,
              alignment_factor: float = ALIGNMENT_FACTOR,
              separation_factor: float = SEPARATION_FACTOR,
              cohesion_factor: float = COHESION_FACTOR):

        # Getting the relevant information from each element in the chunk (Abstract base classes)
        # That information is the values which will be affecting "Self" in its flocking decision

        aligners = [] # data for the alignment behavior
        separators = [] # data for the separation behavior
        coheders = [] # data for the cohesion behavior

        count = 0
        for elem in chunk:
            if (elem != self
            and math.dist(elem.get_coordinates(), self.get_coordinates()) < SIGHT_DISTANCE):
                count += 1
                aligners.append(elem.pointer())
                coheders.append(elem.puller_coordinate())
                separators.append(elem.pusher_scale(self.get_coordinates(), SIGHT_DISTANCE))

        self.neighbors_count = count

        force = Vector()

        force += self.alignment_force(aligners) * alignment_factor
        force += self.cohesion_force(coheders) * cohesion_factor
        force += self.separation_force(separators) * separation_factor
        force += self.wall_force() * WALL_FACTOR

        force.clamp_magnitude(MAX_FORCE)

        self.direction += force

        self.direction.clamp_magnitude(MAX_SPEED, min_=MIN_SPEED)

        self.tracer_pending_seconds += dt
        if self.tracer_pending_seconds > SECONDS_PER_TRACE:
            self.tracer_pending_seconds = 0.0
            self.tracer.points.append((self.x, self.y))

        if len(self.tracer.points) > TRACER_DURATION * TRACES_PER_SECOND:
            self.tracer.points.pop(0)

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

        surface = pygame.Surface((SIGHT_DISTANCE * 2, SIGHT_DISTANCE * 2), pygame.SRCALPHA)
        (pygame.draw.circle
         (surface, color=(*SIGHT_COLOR, SIGHT_ALPHA), center=(SIGHT_DISTANCE, SIGHT_DISTANCE), radius=SIGHT_DISTANCE))
        main_screen.blit(surface, (self.x - SIGHT_DISTANCE, self.y - SIGHT_DISTANCE))

    def draw_personal_space(self):
        pygame.draw.circle(main_screen, PERSONAL_SPACE_COLOR, self.get_coordinates(), PERSONAL_SPACE)

    def draw_trace(self):
        self.tracer.draw()
