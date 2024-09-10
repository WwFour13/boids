import sys

import pygame
# from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN, KEYUP

from surfaces import main_screen

from boid import Boid
from balloon import Barrier, Cloud

from coloring import get_cyclical_rgb

from IO import update_current_balloon, is_holding_balloon, handle_event

import GameObjects as Go

boids: list[Boid] = Go.boids
barriers: list[Barrier] = Go.barriers
clouds: list[Cloud] = Go.clouds


FPS = 20
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


def main():
    global run_time_seconds, barriers, clouds

    Go.init()

    while True:

        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            handle_event(event)

        main_screen.fill(get_cyclical_rgb(run_time_seconds))

        update_current_balloon(dt)

        for boid in boids:
            boid.find_flock_direction(boids, barriers, dt)
            boid.move(dt)
            boid.draw_sight()
            # boid.draw_tracers()

        if not is_holding_balloon():
            Go.remove_small_balloons()

        for bar in barriers:
            bar.draw()
        for boid in boids:
            boid.draw()

        for cloud in clouds:
            cloud.move(dt, run_time_seconds)
            cloud.draw()

        pygame.display.flip()

        clock.tick(FPS)
        run_time_seconds += dt


if __name__ == '__main__':
    main()
