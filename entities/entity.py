
class Entity:
    def __init__(self,
                 x: float,
                 y: float,
                 ):
        self.y = y
        self.x = x

        self.current_chunk = None

    def intersects(self, other_coordinates):
        raise NotImplemented("Intersects method not implemented")

    def get_coordinates(self):
        return self.x, self.y

    def set_coordinates(self, coordinates):
        x, y = coordinates
        self.x = x
        self.y = y

    def draw(self):
        raise NotImplemented("Draw method not implemented")
