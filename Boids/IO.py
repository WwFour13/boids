import pygame
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN, KEYUP

from boid import Boid
from balloon import Balloon, Barrier, Cloud

import GameObjects as GO

boids: list[Boid] = GO.boids
barriers: list[Barrier] = GO.barriers
clouds: list[Cloud] = GO.clouds

current_balloon: Balloon | None = None
last_key = None


def reset_balloon():
    global current_balloon
    current_balloon = None


def is_holding_balloon():
    return current_balloon is not None


def get_key():
    return last_key


def set_key(key):
    global last_key
    last_key = key


def update_current_balloon(dt):

    global current_balloon

    if current_balloon is None:
        return

    current_balloon.set_coordinates((pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]))
    current_balloon.expand(dt)


def add_cloud(x, y):
    global current_balloon
    c = Cloud(x=x, y=y)
    current_balloon = c
    clouds.append(c)


def add_barrier(x, y, pop=False):
    global current_balloon
    b = Barrier(x=x, y=y, pop=pop)
    current_balloon = b
    barriers.append(b)


def add_barrier_pop(x, y):
    add_barrier(x, y, True)


def add_boid(x, y):
    b = Boid(x=x, y=y)
    boids.append(b)


default_bind = add_barrier_pop
key_binds: dict[int | None, callable] = {
    pygame.K_c: add_cloud,
    pygame.K_b: add_boid,
    pygame.K_p: add_barrier,
    pygame.K_BACKSPACE: GO.remove_element,
}


def handle_event(event):
    global default_bind

    if event.type == KEYDOWN:
        set_key(event.key)

    if event.type == KEYUP:
        if event.key == get_key():
            set_key(None)

    if event.type == MOUSEBUTTONDOWN:
        action: callable = key_binds.get(get_key(), default_bind)
        x, y = pygame.mouse.get_pos()
        action(x, y)

    if event.type == MOUSEBUTTONUP:
        reset_balloon()
