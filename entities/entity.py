from vector import Vector


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

    def get_boid_attraction_point(self, boid_coordinates: tuple, sight_distance: float) -> tuple[float, float] | None:
        return None

    def get_boid_repulsion_force(self, boid_coordinates: tuple, sight_distance: float) -> Vector | None:
        return None

    def get_boid_pointer_force(self, boid_coordinates: tuple, sight_distance: float) -> Vector | None:
        return None

    def get_cloud_repulsion_force(self, cloud_coordinates: tuple, cloud_radius: float) -> Vector | None:
        return None

    def get_cloud_merge_point(self, cloud_coordinates: tuple, cloud_radius: float) -> tuple[float, float] | None:
        return None

