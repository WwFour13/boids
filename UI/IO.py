import pygame
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN, KEYUP

from surfaces import main_screen_width, main_screen_height

from entities.boid import Boid
from entities.balloon import Balloon
from entities.barrier import Barrier
from entities.cloud import Cloud

from game_state.objects import boids, barriers, clouds, remove_element

from UI.button import Button
from UI.slider import Slider

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
    pygame.K_BACKSPACE: remove_element,
}

action_buttons = [
    Button(main_screen_width - 60, main_screen_height - 60, 50, 50,
           pygame.image.load("sprites/backspace.png"),
           key=pygame.K_BACKSPACE),

    Button(main_screen_width - 120, main_screen_height - 60, 50, 50,
           pygame.image.load("sprites/arrow.png"),
           key=pygame.K_b),
    Button(main_screen_width - 180, main_screen_height - 60, 50, 50,
           pygame.image.load("sprites/barrier.png"),
           key=pygame.K_p),

    Button(main_screen_width - 240, main_screen_height - 60, 50, 50,
           pygame.image.load("sprites/cloud.png"),
           key=pygame.K_c),
]

sliders = [
    Slider(30, main_screen_height - 40, 100, 30,

           min_value=0.0,
           max_value=0.1,
           value_percentage=5.0 / 10.0,
           image=pygame.image.load("sprites/S.png"),
           ),

    Slider(30, main_screen_height - 80, 100, 30,

           min_value=0.0,
           max_value=5.0,
           value_percentage=1.5 / 5.0,
           image=pygame.image.load("sprites/A.png"),
           ),

    Slider(30, main_screen_height - 120, 100, 30,

           min_value=0.0,
           max_value=5.0,
           value_percentage=1.5 / 5.0,
           image=pygame.image.load("sprites/C.png"),
           ),
]


def handle_event(event):
    global default_bind

    if event.type == KEYDOWN:
        for b in action_buttons:
            b.update()
        set_key(event.key)

    if event.type == KEYUP:
        if event.key == get_key():
            set_key(None)

    if event.type == MOUSEBUTTONDOWN:

        for s in sliders:
            s.handle_click(event.pos)
            if s.dragging:
                return

        for b in action_buttons:
            b.update(event.pos)
            if b.is_pressed:
                set_key(b.key)

        if True not in [b.is_pressed for b in action_buttons]:
            action: callable = key_binds.get(get_key(), default_bind)
            x, y = pygame.mouse.get_pos()
            action(x, y)

    if event.type == MOUSEBUTTONUP:
        reset_balloon()
        for s in sliders:
            s.release()
