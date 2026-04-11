import pygame
from surfaces import main_screen


class Button:

    def __init__(self, x, y, width, height, image, key=None,
                 spring_up_on_update=True,
                 pressed_image=None):
        self.key = key
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.base_image = pygame.transform.scale(image, (width, height))
        self.rect = self.base_image.get_rect()
        self.rect.topleft = (x, y)
        self.outline_color = (200, 200, 200)
        self.outline_color_pressed = (240, 232, 10)
        self.outline_color_hover = (100, 100, 100)

        self.is_pressed = False
        self.pressed_image = None
        if pressed_image:
            self.pressed_image = pygame.transform.scale(pressed_image, (width, height))
        self.spring_up_on_update = spring_up_on_update

    def intersects(self, other_coordinates):
        return self.rect.collidepoint(other_coordinates)

    def update(self, click_coordinates: tuple | None = None):
        if self.spring_up_on_update:
            self.is_pressed = False
            if click_coordinates is not None and self.intersects(click_coordinates):
                self.is_pressed = True
        else:
            if click_coordinates is not None and self.intersects(click_coordinates):
                self.is_pressed = not self.is_pressed

    def draw(self):

        image = self.base_image
        if self.is_pressed and self.pressed_image is not None:
            image = self.pressed_image
        main_screen.blit(image, (self.x, self.y))

    def draw_outline(self):
        color = self.outline_color
        if self.is_pressed or self.intersects(pygame.mouse.get_pos()):
            color = self.outline_color_hover
        if (not self.spring_up_on_update) and self.is_pressed:
            color = self.outline_color_pressed
        pygame.draw.rect(main_screen, color, self.rect, 2)
