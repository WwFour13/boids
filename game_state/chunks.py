import pygame

from entities.entity import Entity

from entities.boid import SIGHT_DISTANCE
from surfaces import main_screen, main_screen_width, main_screen_height


CHUNK_SIZE = SIGHT_DISTANCE * 2
chunk_data = {}


def add_to_chunks(*elements: Entity):

    for elem in elements:

        try:
            chunk_data[elem.current_chunk].append(elem)

        except KeyError:
            chunk_data[elem.current_chunk] = [elem]


def update_chunks_data(*elements: Entity):

    chunk_data.clear()

    for elem in elements:

        elem.current_chunk = ((elem.x // CHUNK_SIZE), (elem.y // CHUNK_SIZE))
        add_to_chunks(elem)


def get_chunk_data(elem: Entity) -> list[Entity]:
    ret = []
    try:
        ret = chunk_data[elem.current_chunk]
    except KeyError:
        pass

    return ret


def get_chunks_data(elem: Entity, radius: int) -> list[Entity]:

    chunks_data: list[Entity] = []

    x, y = elem.current_chunk
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            chunks_data.extend(chunk_data.get((x + i, y + j), []))

    return chunks_data


def draw_grid():
    for x in range(0, main_screen_width + 1, CHUNK_SIZE):
        pygame.draw.line(main_screen, (65, 65, 65), (x, 0), (x, main_screen_height), 1)

    for y in range(0, main_screen_height + 1, CHUNK_SIZE):
        pygame.draw.line(main_screen, (65, 65, 65), (0, y), (main_screen_width, y), 1)
