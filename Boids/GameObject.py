
class GameObject:
    def __init__(self,
                 x: float,
                 y: float,
                 chunk_size: float = 1.0):
        self.y = y
        self.x = x

        self.current_chunk: tuple[float, float] = (x // chunk_size, y // chunk_size)
        self.old_chunk: tuple[float, float] | None = None

    def intersects(self, other_coordinates):
        raise NotImplemented("Intersects method not implemented")

    def get_coordinates(self):
        return self.x, self.y

    def set_coordinates(self, coordinates):
        x, y = coordinates
        self.x = x
        self.y = y

    def update_chunk(self, chunk_size: float):
        new_chunk = (self.x // chunk_size, self.y // chunk_size)

        if new_chunk != self.current_chunk:
            self.old_chunk = self.current_chunk
            self.current_chunk = new_chunk

    def wipe_old_chunk(self):
        self.old_chunk = None

    def draw(self):
        raise NotImplemented("Draw method not implemented")
