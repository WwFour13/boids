import pygame
from pygame.locals import MOUSEBUTTONDOWN, KEYDOWN

import sys
from typing import Self

import random
import math
import vector
import angles

pygame.init()
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Birds!")  # Set the window caption
clock = pygame.time.Clock()  # Clock for controlling frame rate

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

BIRD_COUNT = 100
BIRD_SIZE = 20
BIRD_SIGHT_DISTANCE = 70
BIRD_MAX_SPEED = 50
BIRD_MAX_FORCE = 20

BIRD_IMAGE = pygame.transform.flip(
    pygame.transform.scale(pygame.image.load("sprites/bird.png"), (BIRD_SIZE, BIRD_SIZE)), True, False)
BIRD_SIGHT_COLOR = (175, 255, 171)
BIRD_PERSONAL_SPACE_COLOR = RED

WALL_WEIGHT = 100000
COHESION_WEIGHT = 0.5
ALIGNMENT_WEIGHT = 1
SEPARATION_WEIGHT = 0.1

FPS = 30


def clamp(num, cap):
    if num > cap:
        return cap
    elif num < -cap:
        return -cap
    else:
        return num


def expand(num, min):
    if -min < num < min:
        return min if num < 0 else -min
    else:
        return num


class Bird:
    def __init__(self,
                 x=screen_width / 2,
                 y=screen_height / 2,
                 direction=vector.Vector(), ):
        self.image = BIRD_IMAGE
        self.sight_color = BIRD_SIGHT_COLOR
        self.x: float = x
        self.y: float = y
        self.direction = direction

        self.rotate_image()

    def __repr__(self):
        return f"X: {self.x}, Y: {self.y}, "

    def __eq__(self, other: Self) -> bool:

        return self.x == other.x and self.y == other.y and self.direction == other.direction

    def get_radians(self):
        return self.direction.get_radians()

    def distance_to(self, other: Self):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def move(self, dt: float):
        self.x += self.direction.x * dt
        self.y -= self.direction.y * dt

        self.bounce()

    def bounce(self):
        if self.y > screen_height:
            self.y = screen_height
            self.direction.y *= -1
        elif self.y < 0:
            self.y = 0
            self.direction.y *= -1

        if self.x > screen_width:
            self.x = screen_width
            self.direction.x *= -1
        elif self.x < 0:
            self.x = 0
            self.direction.x *= -1

    def cohesion_force(self, seen_birds: list[Self]) -> vector.Vector:
        if not seen_birds:
            return vector.Vector(0, 0)

        center_x = sum(bird.x for bird in seen_birds) / len(seen_birds)
        center_y = sum(bird.y for bird in seen_birds) / len(seen_birds)
        direction_to_center = vector.Vector(center_x - self.x, center_y - self.y)
        return direction_to_center - self.direction


    def alignment_force(self, seen_birds: list[Self]) -> vector.Vector:
        if not seen_birds:
            return vector.Vector(0, 0)

        average_direction = vector.Vector.average([bird.direction for bird in seen_birds])
        return average_direction - self.direction

    def separation_force(self, seen_birds: list[Self]) -> vector.Vector:
        if not seen_birds:
            return vector.Vector(0, 0)
        personal_birds = [bird for bird in seen_birds if self.distance_to(bird) < BIRD_SIGHT_DISTANCE * SEPARATION_WEIGHT]

        if not personal_birds:
            return vector.Vector(0, 0)
        separation = vector.Vector.average([vector.Vector(self.x - bird.x, self.y - bird.y) for bird in personal_birds])
        return separation - self.direction

    def flock(self, all_birds: list[Self]):
        seen_birds = [bird for bird in all_birds if self.distance_to(bird) < BIRD_SIGHT_DISTANCE and bird != self]

        if not seen_birds:
            return

        force = self.cohesion_force(seen_birds) + self.alignment_force(seen_birds) + self.separation_force(seen_birds)
        force.clamp_magnitude(BIRD_MAX_FORCE)
        self.direction += force
        self.direction.clamp_magnitude(BIRD_MAX_SPEED)

    def rotate_image(self):
        rad = self.get_radians()
        quadrant = angles.get_quadrant(rad)

        if quadrant in (1, 4):
            self.image = pygame.transform.rotate(BIRD_IMAGE, math.degrees(rad))
        else:
            self.image = pygame.transform.flip(
                pygame.transform.rotate(BIRD_IMAGE, 180 - math.degrees(rad)), True, False)

    def update(self, dt: float, birds: list[Self]):

        self.flock(birds)
        self.rotate_image()
        self.move(dt)

    def draw(self):

        center_x = self.x - BIRD_SIZE / 2
        center_y = self.y - BIRD_SIZE / 2
        screen.blit(self.image, (center_x, center_y))


birds: list[Bird] = []


def add_birds():
    for _ in range(BIRD_COUNT):
        radians = random.uniform(0, 2 * math.pi) % (2 * math.pi)
        x = random.uniform(0, screen_width)
        y = random.uniform(0, screen_height)
        dx = math.cos(radians) * BIRD_MAX_SPEED
        dy = math.sin(radians) * BIRD_MAX_SPEED
        birds.append(Bird(x=x, y=y, direction=vector.Vector(dx, dy)))


def main():
    add_birds()

    while True:

        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                pass

        screen.fill((100, 100, 100))

        birds_snap = list(birds)
        for bird in birds:
            bird.update(1 / FPS, birds_snap)
            bird.draw()

        pygame.display.flip()

        clock.tick(FPS)


if __name__ == '__main__':
    main()
