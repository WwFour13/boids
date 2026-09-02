import sys
import time

import pygame

from entities.boid import SIGHT_DISTANCE
from UI.IO import update_current_balloon, is_holding_balloon, handle_event, action_buttons, sliders, \
    toggle_drawing_buttons, pause_button, interaction_lines_button, get_interaction_line_mode, \
    get_interaction_line_mode_name, get_selected_boid, select_random_boid
from game_state import chunks, objects
from game_state.objects import boids, barriers, clouds
from surfaces import main_screen, main_screen_height

FPS = 30
dt = 1 / FPS
run_time_seconds = 0.0
rtsint = 0

pygame.init()

pygame.display.set_caption("Boids!")  # Set the window caption
pygame.display.set_icon(pygame.transform.rotozoom(pygame.image.load("sprites/arrow.png"), 0, 2.5))
clock = pygame.time.Clock()  # Clock for controlling frame rate
interaction_line_font = pygame.font.Font(None, 18)
stats_font = pygame.font.Font(None, 18)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

def main():
    global run_time_seconds, dt, rtsint, frame_elapsed_save, total_interactions_handled_save

    target_dt = 1 / FPS
    objects.init()
    select_random_boid()
    chunks.set_chunk_size(sliders["chunk_size"].get_value())
    chunks.update_chunks_data(*boids, *barriers, *clouds)

    frame_elapsed_save = 0.0
    total_interactions_handled_save = 0

    while True:
        frame_start = time.perf_counter()

        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            handle_event(event)

        main_screen.fill((30, 30, 30))

        chunks.set_chunk_size(sliders["chunk_size"].get_value())
        chunk_radius = chunks.get_required_radius(SIGHT_DISTANCE)

        if toggle_drawing_buttons["grid"].is_pressed:
            chunks.draw_grid()

        update_current_balloon(dt)
        chunks.update_chunks_data(*boids, *barriers, *clouds)

        if not is_holding_balloon():
            objects.remove_small_balloons()

        total_interactions_handled = 0

        for boid in boids:
            selected_boid = get_selected_boid()
            chunks_data = chunks.get_chunks_data(boid, chunk_radius)
            total_interactions_handled += len(chunks_data)
            if (toggle_drawing_buttons["grid"].is_pressed and
                    get_interaction_line_mode() != 0 and selected_boid is boid):
                chunks.draw_chunk_highlight(boid, chunk_radius)
            if not pause_button.is_pressed:
                boid.flock(chunks_data,
                           dt,
                           separation_factor=sliders["separation"].value,
                           alignment_factor=sliders["alignment"].value,
                           cohesion_factor=sliders["cohesion"].value)
                boid.move(dt)
            if (toggle_drawing_buttons["sight"].is_pressed and
                    (get_interaction_line_mode() == 0 or selected_boid is boid)):
                boid.draw_sight()
            if get_interaction_line_mode() == 1:
                boid.draw_interactions(selected_boid=get_selected_boid())
            elif get_interaction_line_mode() == 2:
                boid.draw_distance_checks(chunks_data,
                                          selected_boid=get_selected_boid())

        for bar in barriers:
            if toggle_drawing_buttons["barriers"].is_pressed:
                bar.draw()

        for boid in boids:
            if toggle_drawing_buttons["boids"].is_pressed:
                boid.draw()

        for cloud in clouds:
            cloud_chunks_data = chunks.get_chunks_data(cloud, chunk_radius)
            total_interactions_handled += len(cloud_chunks_data)
            if not pause_button.is_pressed:
                cloud.drift(cloud_chunks_data, dt)
                cloud.move(run_time_seconds=run_time_seconds, dt=dt)
            if toggle_drawing_buttons["clouds"].is_pressed:
                cloud.draw()

        pause_button.draw()

        for b in action_buttons.values():
            b.update()
            b.draw()
            b.draw_outline()

        for b in toggle_drawing_buttons.values():
            b.draw()
            b.draw_outline()

        interaction_lines_button.draw()
        interaction_lines_button.draw_outline()
        interaction_line_label = interaction_line_font.render(
            f"Lines: {get_interaction_line_mode_name()}", True, (220, 220, 220))
        main_screen.blit(interaction_line_label, (325, main_screen_height - 28))

        for s in sliders.values():
            s.update()
            s.draw()

        frame_elapsed = time.perf_counter() - frame_start
        dt = max(frame_elapsed, target_dt)

        if int(run_time_seconds) != rtsint:
            rtsint = int(run_time_seconds)
            frame_elapsed_save = frame_elapsed
            total_interactions_handled_save = total_interactions_handled

        stats_lines = [
            f"Boids: {len(boids)}",
            f"Frame Elapsed ({target_dt:.4f}s): {frame_elapsed_save:.4f}s",
            f"Interactions ({len(boids)**2}): {total_interactions_handled_save}",
        ]
        for line_index, line in enumerate(stats_lines):
            stats_label = stats_font.render(line, True, (220, 220, 220))
            main_screen.blit(
                stats_label,
                (pause_button.x, pause_button.y + pause_button.height + 12 + line_index * 18),
            )

        pygame.display.flip()

        clock.tick(FPS)
        run_time_seconds += dt


if __name__ == '__main__':
    main()
