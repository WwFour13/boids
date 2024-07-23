import sys

import pygame
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN

from surfaces import main_screen, main_screen_width, main_screen_height

from boid import Boid
from boid import MAX_SPEED
from balloon import Balloon
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

barrier_pop_key_binds = {
    1: True,   # This is the left mouse button. We just need to remember that for some reason...
    3: False,  # This is the right mouse button. 2 is middle,
}
is_growing = False
barriers: list[Balloon] = []


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


def main():
    global run_time_seconds, is_growing

    add_boids()

    while True:

        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                pass

            if event.type == MOUSEBUTTONDOWN:
                if event.button in barrier_pop_key_binds:
                    barriers.append(Balloon(x=event.pos[0],
                                            y=event.pos[1],
                                            pop=barrier_pop_key_binds[event.button],
                                            ))
                    is_growing = True

            if event.type == MOUSEBUTTONUP:

                if not barriers:
                    raise Exception("No barriers to pop")

                current_barrier = barriers[-1]
                is_growing = False

                if current_barrier.radius < current_barrier.MIN_RADIUS:
                    barriers.remove(current_barrier)
                    x, y = pygame.mouse.get_pos()
                    for bar in barriers:
                        if bar.intersects((x, y)):
                            barriers.remove(bar)
                            break

                elif current_barrier.pop:
                    barriers.remove(current_barrier)

        rgb = get_cyclical_rgb(run_time_seconds)
        main_screen.fill(rgb)

        if is_growing:
            barriers[-1].set_coordinates((pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]))
            barriers[-1].expand(dt)

        for boid in boids:
            boid.find_flock_direction(boids, dt)
        for boid in boids:
            boid.move(dt)
            boid.draw_sight()
        for bar in barriers:
            bar.draw()
        for boid in boids:
            boid.draw()

        pygame.display.flip()

        clock.tick(FPS)
        run_time_seconds += dt


if __name__ == '__main__':
    main()
