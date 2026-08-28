import math

import pygame

from entities.entity import Entity

from entities.boid import SIGHT_DISTANCE
from surfaces import main_screen, main_screen_width, main_screen_height


CHUNK_SIZE = SIGHT_DISTANCE * 2
chunk_data = {}


def set_chunk_size(size: int):
    global CHUNK_SIZE
    CHUNK_SIZE = max(1, int(size))


def get_required_radius(distance: float) -> int:
    chunks_per_axis = math.ceil(distance / CHUNK_SIZE)
    return math.ceil(chunks_per_axis)



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

    for chunk in get_chunk_coordinates(elem, radius):
        chunks_data.extend(chunk_data.get(chunk, []))

    return chunks_data


def get_chunk_coordinates(elem: Entity, radius: int) -> list[tuple[int, int]]:
    x, y = elem.current_chunk
    pos_x, pos_y = elem.get_coordinates()
    search_radius = radius * CHUNK_SIZE

    def chunk_intersects_search_area(chunk_x: int, chunk_y: int) -> bool:
        left = chunk_x * CHUNK_SIZE
        right = left + CHUNK_SIZE
        top = chunk_y * CHUNK_SIZE
        bottom = top + CHUNK_SIZE

        closest_x = max(left, min(pos_x, right))
        closest_y = max(top, min(pos_y, bottom))
        distance_x = pos_x - closest_x
        distance_y = pos_y - closest_y
        return distance_x ** 2 + distance_y ** 2 <= search_radius ** 2

    return [
        (x + i, y + j)
        for i in range(-radius, radius + 1)
        for j in range(-radius, radius + 1)
        if chunk_intersects_search_area(x + i, y + j)
    ]


def draw_chunk_highlight(elem: Entity, radius: int):
    overlay = pygame.Surface((main_screen_width, main_screen_height), pygame.SRCALPHA)
    for x, y in get_chunk_coordinates(elem, radius):
        pygame.draw.rect(
            overlay,
            (120, 0, 0, 100),
            (x * CHUNK_SIZE, y * CHUNK_SIZE, CHUNK_SIZE, CHUNK_SIZE),
        )
    main_screen.blit(overlay, (0, 0))


def draw_grid():
    for x in range(0, main_screen_width + 1, CHUNK_SIZE):
        pygame.draw.line(main_screen, (65, 65, 65), (x, 0), (x, main_screen_height), 1)

    for y in range(0, main_screen_height + 1, CHUNK_SIZE):
        pygame.draw.line(main_screen, (65, 65, 65), (0, y), (main_screen_width, y), 1)
