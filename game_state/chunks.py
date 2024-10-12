from entities.entity import Entity

from entities.boid import SIGHT_DISTANCE


CHUNK_SIZE = SIGHT_DISTANCE * 2
chunk_data = {}


def add_to_chunks(*elems: Entity):

    for elem in elems:

        try:
            chunk_data[elem.current_chunk].append(elem)

        except KeyError:
            chunk_data[elem.current_chunk] = [elem]


def update_chunks_data(*elems: Entity):

    chunk_data.clear()

    for elem in elems:

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


