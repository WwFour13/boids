import sys

import pygame
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN, KEYUP

from surfaces import main_screen, main_screen_width, main_screen_height

from boid import Boid
from boid import MAX_SPEED
from balloon import Balloon, Barrier, Cloud
from vector import Vector

import random
import math
from background import get_cyclical_rgb

FPS = 30
dt = 1 / FPS
run_time_seconds = 0.0

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
boids: list[Boid] = []

wall_barrier_separation = 10
barriers: list[Barrier] = []

clouds: list[Cloud] = []

current_balloon: Balloon | None = None
last_key = None

default_bind = (lambda x, y: barriers.append(Barrier(x=x, y=y, pop=True)), barriers)
key_binds = {
    pygame.K_c: (lambda x, y: clouds.append(Cloud(x=x, y=y)), clouds),
    pygame.K_b: (lambda x, y: boids.append(Boid(x=x, y=y)), None),
    pygame.K_p: (lambda x, y: barriers.append(Barrier(x=x, y=y, pop=False)), barriers),
    pygame.K_BACKSPACE: (lambda x, y: remove_element((x, y)), None),

}


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


def add_wall_barriers():
    for x in range(0, main_screen_width, wall_barrier_separation):
        barriers.append(Barrier(x=x, y=-wall_barrier_separation, pop=False, radius=wall_barrier_separation))
        barriers.append(Barrier(x=x, y=main_screen_height + wall_barrier_separation,
                                pop=False, radius=wall_barrier_separation))

    for y in range(0, main_screen_height, wall_barrier_separation):
        barriers.append(Barrier(x=-wall_barrier_separation, y=y, pop=False, radius=wall_barrier_separation))
        barriers.append(Barrier(x=main_screen_width + wall_barrier_separation, y=y,
                                pop=False, radius=wall_barrier_separation))


def remove_element(mouse_pos: tuple[int, int]):
    x, y = mouse_pos
    for bar in barriers:
        if bar.intersects((x, y)):
            barriers.remove(bar)
            return

    for cloud in clouds:
        if cloud.intersects((x, y)):
            clouds.remove(cloud)
            return

    for boid in boids:
        if boid.in_personal_space((x, y)):
            boids.remove(boid)
            return


def main():
    global run_time_seconds, current_balloon, last_key, barriers, clouds

    add_boids()
    add_wall_barriers()

    while True:

        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                last_key = event.key

            if event.type == KEYUP:
                if event.key == last_key:
                    last_key = None

            if event.type == MOUSEBUTTONDOWN:

                action, holder = key_binds.get(last_key, default_bind)
                x, y = pygame.mouse.get_pos()
                action(x, y)
                if holder is not None:
                    current_balloon = holder[-1]

            if event.type == MOUSEBUTTONUP:
                current_balloon = None

        rgb = get_cyclical_rgb(run_time_seconds)
        main_screen.fill(rgb)

        if current_balloon is not None:
            current_balloon.set_coordinates((pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]))
            current_balloon.expand(dt)

        for boid in boids:
            boid.find_flock_direction(boids, barriers, dt)
        for boid in boids:
            boid.move(dt)
            boid.draw_sight()

        if current_balloon is None:
            for i in range(len(barriers) - 1, -1, -1):
                bar = barriers[i]
                if bar.pop or bar.radius < bar.MIN_RADIUS:
                    del barriers[i]

            for i in range(len(clouds) - 1, -1, -1):
                cloud = clouds[i]
                if cloud.radius < cloud.MIN_RADIUS:
                    del clouds[i]

        for bar in barriers:
            bar.draw()
        for boid in boids:
            boid.draw()

        for cloud in clouds:
            cloud.move(dt)
            cloud.draw()

        pygame.display.flip()

        clock.tick(FPS)
        run_time_seconds += dt


if __name__ == '__main__':
    main()
