import copy
import sys

import pygame
from pygame.locals import MOUSEBUTTONDOWN, KEYDOWN

from boid import Boid
from boid import BOID_MAX_SPEED

import random
import math
from vector import Vector
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
        x = random.uniform(0, screen_width)
        y = random.uniform(0, screen_height)
        dx = math.cos(radians)
        dy = math.sin(radians)
        v = Vector()
        v.set_radians(radians)
        v.set_magnitude(BOID_MAX_SPEED)
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
        screen.fill(rgb)

        for boid in boids:
            boid.find_flock_direction(boids)
        for boid in boids:
            boid.move(dt)
            screen.blit(boid.get_image(),
                        boid.get_top_left_coordinates())
            pygame.draw.circle(screen, RED, boid.get_coordinates(), 5)

        pygame.display.flip()

        clock.tick(FPS)
        run_time_seconds += dt


if __name__ == '__main__':
    main()
