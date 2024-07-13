# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys

import pygame
from pygame.locals import MOUSEBUTTONDOWN
import random
import math
import copy

FPS = 30

# Color constants
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SNAKE_COLOR = BLUE
ENEMY_SNAKE_COLOR = RED
WALL_COLOR = GRAY

# Initialize Pygame
pygame.init()
screen_width = 640
screen_height = 360
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Snake")  # Set the window caption
clock = pygame.time.Clock()  # Clock for controlling frame rate

# Board
board_width = 10
board_height = 8

# Border
border_thickness = 8
border_color = GRAY

# Tiles
tile_color_dark = (0, 150, 0)
tile_color_light = (0, 200, 0)
tile_size = 40

full_board_width = board_width * tile_size + border_thickness * 2
full_board_height = board_height * tile_size + border_thickness * 2

directional_keys = {pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_w, pygame.K_s, pygame.K_a,
                    pygame.K_d}


def index_to_coordinate(index):
    return tile_size * index + border_thickness


def draw_border():
    pygame.draw.rect(screen, border_color, (0, 0, border_thickness, full_board_height))  # Left border
    pygame.draw.rect(screen, border_color, (0, 0, full_board_width, border_thickness))  # Top border
    pygame.draw.rect(screen, border_color,
                     (full_board_width - border_thickness, 0, border_thickness, full_board_height))  # Right border
    pygame.draw.rect(screen, border_color,
                     (0, full_board_height - border_thickness, full_board_width, border_thickness))  # Bottom border


def draw_tile(x, y):
    tile_color = tile_color_dark
    if (x + y) % 2 == 0:
        tile_color = tile_color_light

    pygame.draw.rect(screen, tile_color, (index_to_coordinate(x), index_to_coordinate(y), tile_size, tile_size))


def draw_board_background():
    screen.fill(BLACK)
    draw_border()
    for x in range(board_width):
        for y in range(board_height):
            draw_tile(x, y)
    pygame.display.flip()


class Button:

    def __init__(self, surface, x, y, width, height, text,
                 idle_color, hover_color, click_color,
                 font=None, font_size=20, spring_up=True):

        self.surface = surface
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.idle_color = idle_color
        self.hover_color = hover_color
        self.click_color = click_color
        self.font = font or pygame.font.SysFont(None, font_size)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.is_pressed = False
        self.spring_up = spring_up

    def draw(self):
        color = self.idle_color
        if self.is_pressed:
            color = self.click_color
        elif self.rect.collidepoint(pygame.mouse.get_pos()):
            color = self.hover_color

        pygame.draw.rect(self.surface, color, self.rect)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.center = self.rect.center
        self.surface.blit(text_surface, text_rect)

    def update(self, events=None, position=None):

        if position is not None:
            if self.rect.collidepoint(position):
                self.is_pressed = True
                return

        if events is None:
            events = pygame.event.get()

        if self.spring_up:
            self.is_pressed = False
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.is_pressed = True
                    break

    def is_clicked(self):
        return self.is_pressed


class Selectable:
    def __init__(self,
                 full_width: int = 0,
                 center: int = None,
                 is_vertical: bool = False,
                 buttons: list[Button] = None,
                 selected_index: int = None, ):

        if buttons is not None:
            self.buttons = buttons
            for button in self.buttons:
                button.spring_up = False
        else:
            raise Exception("Buttons must be specified")

        if center is not None:
            self.center = center
        else:
            self.center = sum([button.width for button in self.buttons]) // 2

        self.min_width = sum([button.width for button in self.buttons])
        self.full_width = max(self.min_width, full_width)

        self.is_vertical = is_vertical
        self.selected_index = selected_index
        self.selected = None
        self.set_selection(index=self.selected_index)

        self.align_buttons()

    def align_buttons(self):
        button_widths = sum([button.width for button in self.buttons])
        empty_space = self.full_width - button_widths
        if empty_space < 0:
            raise Exception("Not enough space to display all the buttons")
        offset = empty_space // len(self.buttons)
        current_x = self.center - (self.full_width // 2)
        for button in self.buttons:
            button.x = current_x
            current_x += button.width + offset

    def set_selection(self, button: Button = None, index: int = None):

        for button in self.buttons:
            button.is_pressed = False

        if (index is not None) and (button is None):
            self.set_selection(button=self.buttons[index])
        elif button is not None:
            self.selected = button
            self.selected.is_pressed = True

        self.draw()

    def draw(self):
        for button in self.buttons:
            button.draw()

    def update(self, events=None, position=None):

        for button in self.buttons:

            was_pressed = button.is_pressed
            button.update(events=events, position=position)
            if (not was_pressed) and button.is_pressed:
                self.set_selection(button=button)
                return

    def get_selected(self):
        return self.selected


class Vector:

    def __init__(self, key=0, x=0, y=0):
        self.x = x
        self.y = y
        self.set(key, x, y)

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return (other[0] + self.x), (other[1] + self.y)

    def set(self, key=0, x=0, y=0):

        if key not in directional_keys:
            self.x = x
            self.y = y
            return

        if key == pygame.K_UP or key == pygame.K_w:
            self.y = -1
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.y = 1
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.x = -1
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.x = 1

    def is_perpendicular(self, other):
        return self.x * other.x + self.y * other.y == 0

    def get_opposite(self):
        return Vector(x=-self.x, y=-self.y)

    def angle_to(self, other):
        """Calculates the angle between two vectors in radians."""
        dot_product = self.x * other.x + self.y * other.y
        magnitude_product = (self.magnitude() * other.magnitude())

        if magnitude_product == 0:
            # If either vector has zero magnitude, their angle is undefined
            return 0.0  # Because it is close

        return math.acos(dot_product / magnitude_product)

    def magnitude(self):
        """Calculates the magnitude (length) of the vector."""
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def closest_vector_by_angle(self, vectors):
        """Finds the vector in a list that is closest to this vector by angle."""
        closest_vector = None
        closest_angle = math.pi  # Initialize with the largest angle
        for other in vectors:
            angle = self.angle_to(other)
            if angle < closest_angle:
                closest_angle = angle
                closest_vector = other
        return closest_vector

    @staticmethod
    def smallest_magnitude(vectors):
        """Returns the vector with the smallest magnitude in a list."""
        smallest_vector = None
        smallest_magnitude = float('inf')  # Initialize with a large magnitude
        for vector in vectors:
            magnitude = vector.magnitude()
            if magnitude < smallest_magnitude:
                smallest_magnitude = magnitude
                smallest_vector = vector
        return smallest_vector


SNAKE_VECTORS = [Vector(pygame.K_UP), Vector(pygame.K_RIGHT), Vector(pygame.K_DOWN), Vector(pygame.K_LEFT)]

WASD_KEY_BINDS = {
    pygame.K_w: Vector(pygame.K_w),
    pygame.K_s: Vector(pygame.K_s),
    pygame.K_a: Vector(pygame.K_a),
    pygame.K_d: Vector(pygame.K_d),
}
ARROW_KEY_BINDS = {
    pygame.K_UP: Vector(pygame.K_UP),
    pygame.K_DOWN: Vector(pygame.K_DOWN),
    pygame.K_LEFT: Vector(pygame.K_LEFT),
    pygame.K_RIGHT: Vector(pygame.K_RIGHT),
}
ALL_KEY_BINDS = {**WASD_KEY_BINDS, **ARROW_KEY_BINDS}


def get_random_open_tile(filled_coordinates):
    not_filled = []
    for w in range(board_width):
        for h in range(board_height):
            if (w, h) not in filled_coordinates:
                not_filled.append((w, h))
    return random.choice(not_filled)


class Snake:

    def __init__(self, key_binds=None):

        if key_binds is None:
            key_binds = ARROW_KEY_BINDS

        self.COLOR = SNAKE_COLOR
        self.snake_full_sprite = pygame.image.load("sprites/snake_full.png")
        self.snake_full_sprite = pygame.transform.scale(self.snake_full_sprite, (tile_size, tile_size))
        self.snake_side_sprite = pygame.image.load("sprites/snake_side.png")
        self.snake_side_sprite = pygame.transform.scale(self.snake_side_sprite, (tile_size, tile_size))
        self.tile_margin_pixels = 2
        self.EYE_RADIUS = 10
        self.EYE_MARGIN = 4
        self.SPEED_SECONDS_PER_TILE = .5
        self.START_LENGTH = 3
        self.KEY_BINDS = copy.deepcopy(key_binds)

        self.direction = Vector(pygame.K_RIGHT)
        self.body = []
        self.seconds_left = self.SPEED_SECONDS_PER_TILE
        self.is_alive = True

    def get_tile_cross_percent(self):
        return self.seconds_left / self.SPEED_SECONDS_PER_TILE

    def has_passed_half_tile(self):
        return self.get_tile_cross_percent() > 0.5

    def get_length(self):
        return len(self.body)

    def get_throat(self):
        return self.body[self.get_length() - 2]

    def get_head_x(self):
        return self.body[len(self.body) - 1][0]

    def get_head_y(self):
        return self.body[len(self.body) - 1][1]

    def get_tail_x(self):
        return self.body[0][0]

    def get_tail_y(self):
        return self.body[0][1]

    def get_next_movement(self, vector=None):
        if vector is None:
            vector = self.direction
        new_head_x = self.get_head_x() + vector.x
        new_head_y = self.get_head_y() + vector.y
        new_head = (new_head_x, new_head_y)
        return new_head

    def move_to(self, new_head: (int, int)):
        self.seconds_left = self.SPEED_SECONDS_PER_TILE
        self.body.append(new_head)

    def remove_tail(self):
        self.body.pop(0)

    def test_draw2(self):
        for (x, y) in self.body:
            screen.blit(self.snake_full_sprite,
                        (index_to_coordinate(x), index_to_coordinate(y), tile_size, tile_size))

        for current, next_item in zip(self.body, self.body[1:]):
            self.draw_side_connector(current, next_item)
            self.draw_side_connector(next_item, current)

    def draw_side_connector(self, current, next_item):
        direction = Vector(x=(next_item[0] - current[0]), y=-(next_item[1] - current[1]))
        theta = Vector(x=1, y=0).angle_to(direction)
        rotated_image = pygame.transform.rotate(self.snake_side_sprite, theta)
        screen.blit(rotated_image,
                    (index_to_coordinate(current[0]), index_to_coordinate(current[1]), tile_size, tile_size))

    def test_draw1(self):
        frame_offset = self.get_tile_cross_percent() * tile_size

        x_offset = 0
        width_offset = 0
        if self.direction.x == 0:
            x_offset = self.tile_margin_pixels
            width_offset = 2 * self.tile_margin_pixels

        y_offset = 0
        height_offset = 0
        if self.direction.y == 0:
            y_offset = self.tile_margin_pixels
            height_offset = 2 * self.tile_margin_pixels

        head_x_offset = x_offset
        head_width_offset = width_offset
        if self.direction.x < 0:
            head_x_offset = frame_offset
        elif self.direction.x != 0:
            head_width_offset = frame_offset

        head_y_offset = y_offset
        head_height_offset = height_offset
        if self.direction.y < 0:
            head_y_offset = frame_offset
        elif self.direction.y != 0:
            head_height_offset = frame_offset

        for (x, y) in self.body:
            if (x, y) == (self.get_head_x(), self.get_head_y()):
                # Adjust width and height for head, accounting for margins:
                rect = pygame.Rect(
                    index_to_coordinate(x) + head_x_offset,
                    index_to_coordinate(y) + head_y_offset,
                    tile_size - head_width_offset,
                    tile_size - head_height_offset,
                )
            else:
                # Adjust width and height for body segments:
                rect = pygame.Rect(
                    index_to_coordinate(x) + x_offset,
                    index_to_coordinate(y) + y_offset,
                    tile_size - width_offset,
                    tile_size - height_offset,
                )
            pygame.draw.rect(screen, self.COLOR, rect)

    def draw(self):

        frame_offset = self.get_tile_cross_percent() * tile_size
        for (x, y) in self.body:
            if (x, y) != (self.get_head_x(), self.get_head_y()):
                pygame.draw.rect(screen, self.COLOR,
                                 (index_to_coordinate(x), index_to_coordinate(y), tile_size, tile_size))
        self.draw_head()

    def draw_head(self):

        x = self.get_head_x()
        y = self.get_head_y()
        frame_offset = self.get_tile_cross_percent() * tile_size
        x_offset = -frame_offset * min(self.direction.x, 0)
        y_offset = -frame_offset * min(self.direction.y, 0)
        width_offset = frame_offset * max(self.direction.x, 0)
        height_offset = frame_offset * max(self.direction.y, 0)

        pygame.draw.rect(screen, self.COLOR, (index_to_coordinate(x) + x_offset,
                                              index_to_coordinate(y) + y_offset,
                                              tile_size - width_offset,
                                              tile_size - height_offset))
        pupil_color = WHITE
        if isinstance(self, EnemySnake):
            if self.decision_seconds_left < 0.1 * self.DECISION_TIME_SECONDS:
                pupil_color = GREEN
        pygame.draw.circle(screen, pupil_color, (index_to_coordinate(x), index_to_coordinate(y)), 5)


class EnemySnake(Snake):

    def __init__(self):
        super().__init__()
        self.KEY_BINDS = []
        self.COLOR = ENEMY_SNAKE_COLOR
        self.DECISION_TIME_SECONDS = self.SPEED_SECONDS_PER_TILE / 3
        self.decision_seconds_left = self.DECISION_TIME_SECONDS
        self.direction = Vector(pygame.K_LEFT)

    def get_move_decision(self, open_coordinates, apple_coordinates):
        self.decision_seconds_left = self.DECISION_TIME_SECONDS

        options = []
        for v in SNAKE_VECTORS.copy():

            new_head = self.get_next_movement(v)
            if ((new_head in open_coordinates or new_head in apple_coordinates) and
                    (self.direction.is_perpendicular(v) or v == self.direction)):
                options.append(v)

        if not options:
            return self.direction

        if (self.get_head_x(), self.get_head_y()) in apple_coordinates:
            apple_coordinates.remove((self.get_head_x(), self.get_head_y()))

        if not apple_coordinates:
            return random.choice(options)

        vectors_to_apples = [Vector(x=(c[0] - self.get_head_x()),
                                    y=(c[1] - self.get_head_y())) for c in apple_coordinates]
        closest_vector_to_apples_by_distance = Vector.smallest_magnitude(vectors_to_apples)

        return closest_vector_to_apples_by_distance.closest_vector_by_angle(options)


class Apple:

    def __init__(self, c=(0, 0)):
        self.coordinate = c
        self.apple_sprite = pygame.image.load("sprites/apple.png")
        self.apple_sprite = pygame.transform.scale(self.apple_sprite, (tile_size, tile_size))

    def get_x(self):
        return self.coordinate[0]

    def get_y(self):
        return self.coordinate[1]

    def move_to(self, c):
        self.coordinate = c

    def draw(self):
        screen.blit(self.apple_sprite, (
            index_to_coordinate(self.coordinate[0]), index_to_coordinate(self.coordinate[1]), tile_size, tile_size))


class Game:

    def __init__(self, start_apples=1, players=1, enemies=1):

        self.in_game = False

        self.player_count = players
        if players not in [0, 1, 2]:
            raise Exception("must have 0, 1, or 2 players")

        # key binds
        self.snakes = []
        if players == 1:
            self.snakes = [Snake(key_binds=ALL_KEY_BINDS)]
        elif players == 2:
            self.snakes = [Snake(key_binds=WASD_KEY_BINDS), Snake(key_binds=ARROW_KEY_BINDS)]

        # enemies
        self.snakes.extend([EnemySnake() for _ in range(enemies)])

        # snake position values
        player_spread = 2 * self.player_count - 1
        player_start_y = (board_height - player_spread) // 2
        enemy_spread = 2 * self.get_enemy_count() - 1
        enemy_start_y = (board_height - enemy_spread) // 2

        for i, snake in enumerate(self.snakes):
            y = (player_start_y + (2 * i))
            body = [(x, y) for x in range(self.snakes[i].START_LENGTH)]
            if isinstance(snake, EnemySnake):
                y = (enemy_start_y + (2 * i))
                body = [(x, y) for x in range(board_width - 1, board_width - 1 - self.snakes[i].START_LENGTH, -1)]

            snake.body = body

        # apples
        self.apples = [Apple() for _ in range(start_apples)]
        for apple in self.apples:
            coord = get_random_open_tile(self.get_object_coordinates())  # Anything to avoid
            apple.move_to(coord)
            apple.draw()

        # buttons
        self.restart_button = Button(screen, full_board_width, 10, 50, 50, "Restart",
                                     (255, 255, 255), (255, 255, 200), (100, 100, 100))

    def is_running(self):
        return self.in_game

    def start(self):
        self.in_game = True

    def get_snake_coordinates(self):
        coordinates = []
        for snake in self.snakes:
            coordinates.extend(snake.body)
        return coordinates

    def get_apple_coordinates(self):
        return [apple.coordinate for apple in self.apples]

    def get_object_coordinates(self):
        coordinates = []
        coordinates.extend(self.get_snake_coordinates())
        coordinates.extend(self.get_apple_coordinates())
        return coordinates

    def get_open_coordinates(self):
        open_coordinates = []
        occupied_coordinates = self.get_object_coordinates()
        for x in range(board_width):
            for y in range(board_height):
                if (x, y) not in occupied_coordinates:
                    open_coordinates.append((x, y))
        return open_coordinates

    def get_enemy_count(self):
        return len(self.snakes) - self.player_count

    def handle_interactions(self, snake):

        head_x = snake.get_head_x()
        head_y = snake.get_head_y()

        if (head_x, head_y) not in self.get_apple_coordinates():
            snake.remove_tail()

        throat = snake.get_throat()
        for apple in self.apples:
            if apple.coordinate == throat:
                coord = random.choice(self.get_open_coordinates())  # Anything to avoid
                apple.move_to(coord)

    def try_move(self, snake):
        if not snake.is_alive:
            return

        snake.seconds_left = 0
        new_head = snake.get_next_movement()
        new_head_x = new_head[0]
        new_head_y = new_head[1]

        if new_head in self.get_snake_coordinates():
            snake.is_alive = False
            return
        elif new_head_x < 0 or new_head_x >= board_width or new_head_y < 0 or new_head_y >= board_height:
            snake.is_alive = False
            return

        snake.move_to(new_head)
        self.handle_interactions(snake)

    def tick(self, delta_seconds, events=None):

        for snake in self.snakes:
            if snake.is_alive:

                snake.seconds_left -= delta_seconds
                if snake.seconds_left <= 0:
                    snake.seconds_left = 0
                    self.try_move(snake)

                if snake.has_passed_half_tile():

                    for apple in self.apples:
                        snake_head = (snake.get_head_x(), snake.get_head_y())
                        if apple.coordinate == snake_head:
                            print(snake.seconds_left)
                            coord = random.choice(self.get_open_coordinates())  # Anything to avoid
                            apple.move_to(coord)

                if isinstance(snake, EnemySnake):
                    snake.decision_seconds_left -= delta_seconds
                    if snake.decision_seconds_left <= 0:
                        snake.decision_seconds_left = 0
                        v = snake.get_move_decision(self.get_open_coordinates(), self.get_apple_coordinates())

                        if v is not None and v != snake.direction:
                            snake.direction = v
                            self.try_move(snake)
        self.restart_button.update(events=events)

        life = False
        for snake in self.snakes:
            if snake.is_alive:
                life = True
        if not life or self.restart_button.is_pressed:
            self.in_game = False
            return

    def draw(self):

        draw_board_background()

        for apple in self.apples:
            apple.draw()

        for snake in self.snakes:
            snake.draw()
        self.restart_button.draw()
        pygame.display.flip()

    def turn_snakes(self, event):
        for snake in self.snakes:
            if snake.is_alive and event.key in snake.KEY_BINDS:
                new_vector = snake.KEY_BINDS[event.key]
                if new_vector.is_perpendicular(snake.direction):
                    snake.direction = new_vector
                    self.try_move(snake)


enemy_count_slider_buttons = [
    Button(screen, 0, 0, 50, 50, "1", (255, 255, 255), (255, 255, 200), (100, 100, 100)),
    Button(screen, 50, 0, 50, 50, "2", (255, 255, 255), (255, 255, 200), (100, 100, 100)),
    Button(screen, 100, 0, 50, 50, "3", (255, 255, 255), (255, 255, 200), (100, 100, 100)),
    Button(screen, 150, 0, 50, 50, "4", (255, 255, 255), (255, 255, 200), (100, 100, 100)),
]

enemy_count_slider = Selectable(full_width=screen_width - 10, center=screen_width // 2, is_vertical=False,
                                buttons=enemy_count_slider_buttons, selected_index=0)
enemy_count_slider.set_selection(index=0)


def set_menu():
    draw_board_background()
    enemy_count_slider.draw()
    pygame.display.flip()


def main():
    set_menu()
    current_game = Game()

    while True:

        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:

                if not current_game.is_running():

                    was_selected = enemy_count_slider.get_selected()
                    print(was_selected.text)
                    enemy_count_slider.update(events=events, position=pygame.mouse.get_pos())
                    if was_selected == enemy_count_slider.get_selected():
                        continue
                        #current_game = Game(start_apples=1, enemies=0, players=1)
                        #current_game.in_game = True

            if current_game.is_running():
                if event.type == pygame.KEYDOWN:
                    current_game.turn_snakes(event)

        if current_game.is_running():
            current_game.tick(FPS ** -1, events=events)
            current_game.draw()
        else:
            set_menu()

        clock.tick(FPS)


if __name__ == '__main__':
    main()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
