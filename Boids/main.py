import pygame
from pygame.locals import MOUSEBUTTONDOWN, KEYDOWN

import sys
from typing import Self

import random
import math
import vector
import angles
import background

pygame.init()
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Boids!")  # Set the window caption
clock = pygame.time.Clock()  # Clock for controlling frame rate

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

BOID_COUNT = 100
BOID_SIZE = 30
BOID_SIGHT_DISTANCE = 70
BOID_MAX_SPEED = 50
BOID_MAX_FORCE = 20

BOID_IMAGE = pygame.transform.flip(
    pygame.transform.scale(pygame.image.load("sprites/arrow.png"), (BOID_SIZE, BOID_SIZE)), True, False)
BOID_SIGHT_COLOR = (175, 255, 171)
BOID_PERSONAL_SPACE_COLOR = RED

COHESION_WEIGHT = 0.5
ALIGNMENT_WEIGHT = 1
SEPARATION_WEIGHT = 0.1

FPS = 30

run_time_seconds = 0.0


def clamp(num, cap):
    if num > cap:
        return cap
    elif num < -cap:
        return -cap
    else:
        return num


class Boid:
    def __init__(self,
                 x=screen_width / 2,
                 y=screen_height / 2,
                 direction=vector.Vector(), ):
        self.image = BOID_IMAGE
        self.sight_color = BOID_SIGHT_COLOR
        self.x: float = x
        self.y: float = y
        self.direction = direction

        self.rotate_image()

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

        self.bounce()

    def bounce(self):
        if self.y > screen_height:
            self.y = screen_height
            self.direction.y *= -1
        elif self.y < 0:
            self.y = 0
            self.direction.y *= -1

        if self.x > screen_width:
            self.x = screen_width
            self.direction.x *= -1
        elif self.x < 0:
            self.x = 0
            self.direction.x *= -1

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

    def flock(self, all_boids: list[Self]):
        seen_boids = [boid for boid in all_boids if self.distance_to(boid) < BOID_SIGHT_DISTANCE and boid != self]

        if not seen_boids:
            return

        force = self.cohesion_force(seen_boids) + self.alignment_force(seen_boids)# + self.separation_force(seen_boids)
        force.clamp_magnitude(BOID_MAX_FORCE)
        self.direction += force
        self.direction.clamp_magnitude(BOID_MAX_SPEED)

    def rotate_image(self):
        rad = self.get_radians()
        quadrant = angles.get_quadrant(rad)

        if quadrant in (1, 4):
            self.image = pygame.transform.rotate(BOID_IMAGE, math.degrees(rad))
        else:
            self.image = pygame.transform.flip(
                pygame.transform.rotate(BOID_IMAGE, 180 - math.degrees(rad)), True, False)

    def update(self, dt: float, all_boids: list[Self]):

        self.flock(all_boids)
        self.rotate_image()
        self.move(dt)

    def draw(self):

        center_x = self.x - BOID_SIZE / 2
        center_y = self.y - BOID_SIZE / 2
        screen.blit(self.image, (center_x, center_y))


boids: list[Boid] = []


def add_boids():
    for _ in range(BOID_COUNT):
        radians = random.uniform(0, 2 * math.pi) % (2 * math.pi)
        x = random.uniform(0, screen_width)
        y = random.uniform(0, screen_height)
        dx = math.cos(radians) * BOID_MAX_SPEED
        dy = math.sin(radians) * BOID_MAX_SPEED
        boids.append(Boid(x=x, y=y, direction=vector.Vector(dx, dy)))


def main():

    global run_time_seconds

    add_boids()

    while True:

        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                pass

        rgb = background.get_rgb(run_time_seconds)
        print(rgb)
        screen.fill(rgb)

        boids_snap = list(boids)
        for boid in boids:
            boid.update(1 / FPS, boids_snap)
            boid.draw()

        pygame.display.flip()

        clock.tick(FPS)
        run_time_seconds += 1 / FPS


if __name__ == '__main__':
    main()
