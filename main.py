import sys

import pygame

from UI.IO import update_current_balloon, is_holding_balloon, handle_event, action_buttons, sliders, \
    toggle_drawing_buttons, pause_button, interaction_lines_button, get_interaction_line_mode, \
    get_interaction_line_mode_name, get_selected_boid
from game_state import chunks, objects
from game_state.objects import boids, barriers, clouds
from surfaces import main_screen, main_screen_height

FPS = 30
dt = 1 / FPS
run_time_seconds = 0.0

pygame.init()

pygame.display.set_caption("Boids!")  # Set the window caption
pygame.display.set_icon(pygame.transform.rotozoom(pygame.image.load("sprites/arrow.png"), 0, 2.5))
clock = pygame.time.Clock()  # Clock for controlling frame rate
interaction_line_font = pygame.font.Font(None, 18)

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

        if toggle_drawing_buttons[4].is_pressed:
            chunks.draw_grid()

        update_current_balloon(dt)
        chunks.update_chunks_data(*boids, *barriers, *clouds)

        if not is_holding_balloon():
            objects.remove_small_balloons()

        # for boid in boids:
        #     boid.draw_trace()

        for boid in boids:
            if not pause_button.is_pressed:
                boid.flock(chunks.get_chunks_data(boid, 1),
                           dt,
                           separation_factor=sliders[0].value,
                           alignment_factor=sliders[1].value,
                           cohesion_factor=sliders[2].value)
                boid.move(dt)
            if toggle_drawing_buttons[3].is_pressed:
                boid.draw_sight()
            if get_interaction_line_mode() == 1:
                boid.draw_interactions(draw_all=True)
            elif get_interaction_line_mode() == 2:
                boid.draw_interactions(selected_boid=get_selected_boid())
            elif get_interaction_line_mode() == 3:
                boid.draw_distance_checks(chunks.get_chunks_data(boid, 1))
            elif get_interaction_line_mode() == 4:
                boid.draw_distance_checks(chunks.get_chunks_data(boid, 1),
                                          selected_boid=get_selected_boid())

        for bar in barriers:
            if toggle_drawing_buttons[1].is_pressed:
                bar.draw()

        for boid in boids:
            if toggle_drawing_buttons[0].is_pressed:
                boid.draw()

        for cloud in clouds:
            if not pause_button.is_pressed:
                cloud.drift(chunks.get_chunks_data(cloud, 1), dt)
                cloud.move(run_time_seconds=run_time_seconds, dt=dt)
            if toggle_drawing_buttons[2].is_pressed:
                cloud.draw()

        pause_button.draw()

        for b in action_buttons:
            b.update()
            b.draw()
            b.draw_outline()

        for b in toggle_drawing_buttons:
            b.draw()
            b.draw_outline()

        interaction_lines_button.draw()
        interaction_lines_button.draw_outline()
        interaction_line_label = interaction_line_font.render(
            f"Lines: {get_interaction_line_mode_name()}", True, (220, 220, 220))
        main_screen.blit(interaction_line_label, (325, main_screen_height - 28))

        for s in sliders:
            s.update()
            s.draw()

        pygame.display.flip()

        clock.tick(FPS)
        run_time_seconds += dt


if __name__ == '__main__':
    main()
