import sys

import pygame

from surfaces import main_screen

from UI.IO import update_current_balloon, is_holding_balloon, handle_event, action_buttons, sliders, toggle_drawing_buttons

from game_state import chunks, objects
from game_state.objects import boids, barriers, clouds


FPS = 30
dt = 1 / FPS
run_time_seconds = 0.0

pygame.init()

pygame.display.set_caption("Boids!")  # Set the window caption
pygame.display.set_icon(pygame.transform.rotozoom(pygame.image.load("sprites/arrow.png"), 0, 2.5))
clock = pygame.time.Clock()  # Clock for controlling frame rate

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)


def main():
    global run_time_seconds

    objects.init()
    chunks.update_chunks_data(*boids, *barriers, *clouds)

    while True:

        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            handle_event(event)

        main_screen.fill((30, 30, 30))

        update_current_balloon(dt)
        chunks.update_chunks_data(*boids, *barriers, *clouds)

        if not is_holding_balloon():
            objects.remove_small_balloons()

        # for boid in boids:
        #     boid.draw_trace()

        for boid in boids:
            boid.flock(chunks.get_chunks_data(boid, 1),
                       dt,
                       separation_factor=sliders[0].value,
                       alignment_factor=sliders[1].value,
                       cohesion_factor=sliders[2].value)
            boid.move(dt)
            if toggle_drawing_buttons[3].is_pressed:
                boid.draw_sight()

        for bar in barriers:
            if toggle_drawing_buttons[1].is_pressed:
                bar.draw()

        for boid in boids:
            if toggle_drawing_buttons[0].is_pressed:
                boid.draw()

        for cloud in clouds:
            cloud.drift(chunks.get_chunks_data(cloud, 1), dt)
            cloud.move(run_time_seconds=run_time_seconds, dt=dt)
            if toggle_drawing_buttons[2].is_pressed:
                cloud.draw()

        for b in action_buttons:
            b.update()
            b.draw()
            b.draw_outline()

        for b in toggle_drawing_buttons:
            b.update()
            b.draw()
            b.draw_outline()

        for s in sliders:
            s.update()
            s.draw()

        pygame.display.flip()

        clock.tick(FPS)
        run_time_seconds += dt


if __name__ == '__main__':
    main()
