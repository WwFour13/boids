import math
import random
from vector import Vector

from boid import Boid, MAX_SPEED
from balloon import Barrier, Cloud
from surfaces import main_screen_width, main_screen_height

BOID_COUNT = 130
boids: list[Boid] = []

wall_barrier_separation = 10
barriers: list[Barrier] = []

clouds: list[Cloud] = []


def same_instance_filter(x: list, remove_condition: callable):
    for i in range(len(x) - 1, -1, -1):
        if remove_condition(x[i]):
            del x[i]


def remove_element(*mouse_pos: tuple[int, int]):

    x, y = mouse_pos
    same_instance_filter(barriers, lambda b: b.intersects((x, y)))
    same_instance_filter(clouds, lambda c: c.intersects((x, y)))
    same_instance_filter(boids, lambda b: b.intersects((x, y)))


def remove_small_balloons():
    same_instance_filter(barriers, lambda b: b.pop or b.radius < b.MIN_RADIUS)
    same_instance_filter(clouds, lambda c: c.radius < c.MIN_RADIUS)


def add_boids():
    for _ in range(BOID_COUNT):
        radians = random.uniform(0, 2 * math.pi) % (2 * math.pi)
        x = random.uniform(0, main_screen_width)
        y = random.uniform(0, main_screen_height)

        v = Vector(1, 1)
        v.set_radians(radians)
        v.set_magnitude(MAX_SPEED)
        boids.append(
            Boid(x=x, y=y, direction=v)
        )


def init():
    add_boids()
