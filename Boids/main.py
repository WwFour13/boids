import copy
import sys

import pygame
from pygame.locals import MOUSEBUTTONDOWN, KEYDOWN

from surfaces import main_screen, main_screen_width, main_screen_height

from boid import Boid
from boid import MAX_SPEED

import random
import math
from vector import Vector
import background

pygame.init()


pygame.display.set_caption("Boids!")  # Set the window caption
pygame.display.set_icon(pygame.transform.rotozoom(pygame.image.load("sprites/arrow.png"), 135, 2))
clock = pygame.time.Clock()  # Clock for controlling frame rate

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

BOID_COUNT = 30

FPS = 30
dt = 1 / FPS

run_time_seconds = 0.0


def clamp(num, cap):
    if num > cap:
        return cap
    elif num < -cap:
        return -cap
    else:
        return num


boids: list[Boid] = []


def add_boids():
    for _ in range(BOID_COUNT):
        radians = random.uniform(0, 2 * math.pi) % (2 * math.pi)
        x = random.uniform(0, main_screen_width)
        y = random.uniform(0, main_screen_height)

        dx = math.cos(radians)
        dy = math.sin(radians)
        v = Vector(1, 1)
        v.set_radians(radians)
        v.set_magnitude(MAX_SPEED)
        boids.append(
            Boid(x=x, y=y, direction=v)
        )


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
        main_screen.fill(rgb)

        for boid in boids:
            boid.find_flock_direction(boids, dt)
        for boid in boids:
            boid.move(dt)
            boid.draw_sight()
        for boid in boids:
            boid.draw()

        pygame.display.flip()

        clock.tick(FPS)
        run_time_seconds += dt


if __name__ == '__main__':
    main()
