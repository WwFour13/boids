import pygame
from surfaces import main_screen


class Button:

    def __init__(self, x, y, width, height, image, key=None, hover_color=(100, 100, 100), spring_up_on_update=True):
        self.key = key
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.BASE_IMAGE = pygame.transform.scale(image, (width, height))
        self.rect = self.BASE_IMAGE.get_rect()
        self.rect.topleft = (x, y)
        self.hover_color = hover_color

        self.is_pressed = False
        self.spring_up_on_update = spring_up_on_update

    def intersects(self, other_coordinates):
        return self.rect.collidepoint(other_coordinates)

    def update(self, click_coordinates: tuple | None = None):
        if self.spring_up_on_update:
            self.is_pressed = False
            if click_coordinates is not None and self.intersects(click_coordinates):
                self.is_pressed = True
        else:
            if self.intersects(click_coordinates):
                self.is_pressed = not self.is_pressed

    def draw(self):

        if self.is_pressed or self.intersects(pygame.mouse.get_pos()):
            image = self.BASE_IMAGE.copy()
            image.fill(self.hover_color, special_flags=pygame.BLEND_RGB_ADD)
        else:
            image = self.BASE_IMAGE
        main_screen.blit(image, (self.x, self.y))

    def draw_outline(self):
        pygame.draw.rect(main_screen, (0, 0, 0), self.rect, 2)
