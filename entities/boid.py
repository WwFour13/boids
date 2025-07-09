import pygame

from surfaces import main_screen, main_screen_width, main_screen_height

import math
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
            pygame.draw.line(main_screen, color=self.color_main, start_pos=p1, end_pos=p2, width=min(i // 2, 4))


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

    def get_boid_repulsion_force(self, coordinates: tuple, sight_distance: float) -> Vector | None:
        x, y = coordinates
        force = Vector(0, 0)
        if dist := (math.dist(self.get_coordinates(), coordinates)) < PERSONAL_SPACE:
            weight = (SIGHT_DISTANCE - dist) ** 2
            force.dx = x - self.x
            force.dy = self.y - y
            force.set_magnitude(weight)

            return force

        return None

    def get_boid_attraction_point(self, coordinates: tuple, sight_distance: float) -> tuple[float, float] | None:
        if math.dist(self.get_coordinates(), coordinates) <= sight_distance:
            return self.get_coordinates()

        return None

    def get_boid_pointer_force(self, coordinates: tuple, sight_distance: float) -> Vector | None:
        if math.dist(self.get_coordinates(), coordinates) <= sight_distance:
            return self.direction

        return None

    def get_wall_avoidance_force(self):
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

        alignment_forces = []  # data for the alignment behavior
        separation_forces = []  # data for the separation behavior
        cohesion_points = []  # data for the cohesion behavior

        # Extracting information from the chunk elements
        for elem in chunk:
            if elem != self:

                if (f := elem.get_boid_pointer_force(self.get_coordinates(), SIGHT_DISTANCE)) is not None:
                    alignment_forces.append(f)

                if (p := elem.get_boid_attraction_point(self.get_coordinates(), SIGHT_DISTANCE)) is not None:
                    cohesion_points.append(p)

                if (f := elem.get_boid_repulsion_force(self.get_coordinates(), SIGHT_DISTANCE)) is not None:
                    separation_forces.append(f)

        self.neighbors_count = len(alignment_forces)

        force = Vector()

        # Alignment
        avg = Vector.get_average(alignment_forces)
        alignment_force = avg - self.direction
        force += alignment_force * alignment_factor

        # Cohesion
        avg = Vector.get_average([Vector(p[0], p[1]) for p in cohesion_points])
        to_average_position = Vector(avg.dx - self.x, self.y - avg.dy)
        cohesion_force = to_average_position - self.direction
        force += cohesion_force * cohesion_factor

        # Separation
        separation_force = Vector.get_sum(separation_forces)
        force += separation_force * separation_factor
        force += self.get_wall_avoidance_force() * WALL_FACTOR

        force.clamp_magnitude(MAX_FORCE)
        self.direction += force
        self.direction.clamp_magnitude(MAX_SPEED, min_=MIN_SPEED)

        self.tracer_pending_seconds += dt
        if self.tracer_pending_seconds > SECONDS_PER_TRACE:
            self.tracer_pending_seconds = 0.0
            self.tracer.points.append((self.x, self.y))

        if len(self.tracer.points) > TRACER_DURATION * TRACES_PER_SECOND:
            self.tracer.points.pop(0)

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
