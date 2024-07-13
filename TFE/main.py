import os

import pygame
from pygame.locals import MOUSEBUTTONDOWN, KEYDOWN
import sys
import random
import numpy as np
import math
import copy

# Initialize Pygame
pygame.init()
screen_width = 640
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("2048")  # Set the window caption
clock = pygame.time.Clock()  # Clock for controlling frame rate

BOARD_LEFT_COORDINATE = 10
BOARD_TOP_COORDINATE = 10
BLOCK_LENGTH = 80
BLOCK_SEPARATION = 10


def get_coordinates(board_pos):
    board_x, board_y = board_pos
    return (board_x * (BLOCK_LENGTH + BLOCK_SEPARATION)) + BOARD_LEFT_COORDINATE, \
           (board_y * (BLOCK_LENGTH + BLOCK_SEPARATION)) + BOARD_TOP_COORDINATE


FPS = 30

image = {
    (2 ** i): pygame.transform.scale(pygame.image.load(f"sprites/sprite_{(2 ** i)}.jpg"), (BLOCK_LENGTH, BLOCK_LENGTH))
    for i in range(1, 18)
}

key_bindings = {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
}

movement_queue: list[tuple[int, int]] = []


class Block:
    def __init__(self, position, num):
        self.position = position
        self.coordinates = get_coordinates(position)
        self.num = num
        self.image = image[num]

        self.direction: tuple[int, int] | None = None
        self.speed = 10
        self.target_position: tuple[int, int] | None = None

    def set_direction(self, direction):
        self.direction = direction

    def get_velocity(self):
        return self.direction[0] * self.speed, self.direction[1] * self.speed

    def set_position(self, position):
        self.position = position
        self.coordinates = get_coordinates(position)

    def stop(self):
        self.direction = None
        self.target_position = None

    def merge(self):
        self.num *= 2
        self.image = image[self.num]
        self.draw()

    def shift(self):
        self.coordinates = (self.coordinates[0] + self.direction[0] * self.speed,
                            self.coordinates[1] + self.direction[1] * self.speed)

    def is_passed(self):
        target_position = self.position[0] + self.direction[0], self.position[1] + self.direction[1]
        target_coordinates = get_coordinates(target_position)

        # if isn't passed the target coordinates, should be the same sign (+ or -) as vector
        x_diff = target_coordinates[0] - self.coordinates[0]
        y_diff = target_coordinates[1] - self.coordinates[1]

        x_diff *= self.direction[0]
        y_diff *= self.direction[1]
        # if is positive, then block should continue moving

        if x_diff > 0 or y_diff > 0:
            return True
        else:
            return False

    def draw(self):
        screen.blit(self.image, self.coordinates)


board: list[list[Block | None]] = [[None for i in range(4)] for j in range(4)]


def get_open_positions():

    open_positions = []
    for x in range(4):
        for y in range(4):
            if board[x][y] is None:
                open_positions.append((x, y))
    return open_positions


def add_new_block():
    num = 2
    if random.randint(1, 10) == 1:
        num = 4

    open_positions = get_open_positions()
    if not open_positions:
        raise Exception("No open positions")
    x, y = random.choice(open_positions)
    board[x][y] = Block((x, y), num)


def print_blocks():
    print("------------------------------------------------")
    print("------------------------------------------------")


def get_target_path(direction, x, y):
    path = []
    while board[x][y] is not None and \
            x in range(4) and \
            y in range(4):
        path.append((x, y))
        x += direction[0]
        y += direction[1]
    return path


def set_direction(direction):
    for x in range(4):
        for y in range(4):
            if board[x][y] is not None:

                target_path = get_target_path(direction, x, y)
                if len(target_path) != 0:
                    board[x][y].set_direction(direction)
                    board[x][y].target_position = target_path[-1]



def update():
    global movement_queue
    if len(movement_queue) == 0:
        return

    for x in range(4):
        for y in range(4):

            if board[x][y] is not None and board[x][y].direction is not None:
                board[x][y].shift()

                if board[x][y].is_passed():

                    board[x][y].set_position(board[x][y].target_position)
                    board[x][y].stop()

                    target_x, target_y = board[x][y].target_position
                    board[target_x][target_y] = board[x][y]
                    board[x][y] = None


    movement_queue.pop(0)
    if len(movement_queue) > 0:
        set_direction(movement_queue[0])

def draw():
    for x in range(4):
        for y in range(4):
            if board[x][y] is not None:
                board[x][y].draw()


def main():
    global movement_queue

    add_new_block()
    add_new_block()
    while True:

        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key in key_bindings and len(key_bindings) <= 4:
                    direction = key_bindings[event.key]
                    movement_queue.append(direction)
                    if len(movement_queue) == 1:
                        set_direction(direction)

        update()

        screen.fill((0, 0, 0))

        draw()
        pygame.display.flip()

        print('\n'*20)
        print(*movement_queue, sep='\n')
        clock.tick(FPS)


if __name__ == '__main__':
    main()
