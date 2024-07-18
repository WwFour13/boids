import math
from typing import Self


class Vector:

    def __init__(self, dx=0.0, dy=0.0):
        self.x = dx
        self.y = dy

    def __repr__(self):
        return f"X: {self.x}, Y: {self.y}, "

    def __eq__(self, other) -> bool:
        if isinstance(other, Vector):
            other = (other.x, other.y)
        return self.x == other[0] and self.y == other[1]

    def __add__(self, other) -> Self:
        if isinstance(other, Vector):
            other = (other.x, other.y)
        return Vector((other[0] + self.x), (other[1] + self.y))

    def __sub__(self, other) -> Self:
        if isinstance(other, Vector):
            other = (other.x, other.y)
        return Vector((self.x - other[0]), (self.y - other[1]))

    def __mul__(self, other: float) -> Self:

        return Vector((self.x * other), (self.y * other))

    def __truediv__(self, other: float) -> Self:

        return Vector((self.x / other), (self.y / other))

    def set(self, x=0, y=0):
        self.x = x
        self.y = y

    def set_radians(self, radians):
        magnitude = self.get_magnitude()
        self.x = math.cos(radians)
        self.y = math.sin(radians)

        self.set_magnitude(magnitude)

    def get_radians(self):
        return math.atan2(self.y, self.x) % (2 * math.pi)

    def set_magnitude(self, magnitude):
        radians = self.get_radians()
        self.x = math.cos(radians) * magnitude
        self.y = math.sin(radians) * magnitude

    def get_magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def clamp_magnitude(self, cap):
        if self.get_magnitude() > cap:
            self.set_magnitude(cap)
        elif self.get_magnitude() < -cap:
            return self.set_magnitude(-cap)

    def get_opposite(self):
        return Vector(dx=-self.x, dy=-self.y)

    @staticmethod
    def sum(vectors):
        x = 0
        y = 0
        for vector in vectors:
            x += vector.x
            y += vector.y
        return Vector(x, y)

    @staticmethod
    def average(vectors):
        sum = Vector.sum(vectors)
        x = sum.x / len(vectors)
        y = sum.y / len(vectors)
        return Vector(x, y)