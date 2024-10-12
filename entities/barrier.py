import pygame

from entities.balloon import Balloon
from surfaces import main_screen


class Barrier(Balloon):
    def __init__(self,
                 x: float,
                 y: float,
                 pop: bool,
                 radius: float = 0.0):

        self.pop = pop
        self.COLOR = (255, 0, 0)

        super().__init__(x, y, radius)

    def __repr__(self):
        return f"X: {self.x}, Y: {self.y}, Radius: {self.radius}, Pop: {self.pop}"

    def draw(self):
        pygame.draw.circle(main_screen, self.COLOR, (self.x, self.y), self.radius)

