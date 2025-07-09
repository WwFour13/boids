import math

from surfaces import main_screen_width, main_screen_height

from entities.entity import Entity


class Balloon(Entity):
    def __init__(self, x: float, y: float, radius: float = 0.0):

        super().__init__(x, y)
        self.radius = radius
        self.GROWTH_RATE = 50

        self.MIN_RADIUS = min(main_screen_width, main_screen_height) / 80
        self.MAX_RADIUS = min(main_screen_width, main_screen_height) / 15

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y and self.radius == other.radius

    def __hash__(self):
        return hash((self.x, self.y, self.radius))

    def get_radius(self):
        return self.radius

    def intersects(self, other_coordinates):
        return math.dist(self.get_coordinates(), other_coordinates) < self.radius

    def expand(self, dt):
        self.radius += self.GROWTH_RATE * dt
        self.radius = min(self.radius, self.MAX_RADIUS)

    def draw(self):
        raise NotImplementedError("Draw method not implemented")
