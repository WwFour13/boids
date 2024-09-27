from GameObject import GameObject

from boid import SIGHT_DISTANCE


CHUNK_SIZE = SIGHT_DISTANCE * 2
chunk_data = {}


def add_to_chunks(*elems: GameObject):

    for elem in elems:

        try:
            chunk_data[elem.current_chunk].append(elem)

        except KeyError:
            chunk_data[elem.current_chunk] = [elem]


def update_chunks_data(*elems: GameObject):

    chunk_data.clear()

    for elem in elems:

        elem.current_chunk = ((elem.x // CHUNK_SIZE), (elem.y // CHUNK_SIZE))
        add_to_chunks(elem)


def get_chunk_data(elem: GameObject) -> list[GameObject]:
    ret = []
    try:
        ret = chunk_data[elem.current_chunk]
    except KeyError:
        pass

    return ret


def get_chunks_data(elem: GameObject, radius: int) -> list[GameObject]:

    chunks_data: list[GameObject] = []

    x, y = elem.current_chunk
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            chunks_data.extend(chunk_data.get((x + i, y + j), []))

    return chunks_data


