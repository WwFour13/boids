import pygame
from surfaces import main_screen


class Button:

    def __init__(self, x, y, width, height, image, key=None, hover_color=(100, 100, 100)):
        self.key = key
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.BASE_IMAGE = pygame.transform.scale(image, (width, height))
        self.rect = self.BASE_IMAGE.get_rect()
        self.rect.topleft = (x, y)
        self.hover_color = hover_color

        self.pressed = False

    def intersects(self, other_coordinates):
        return self.rect.collidepoint(other_coordinates)

    def handle_click(self, other_coordinates):
        if self.intersects(other_coordinates):
            self.pressed = True

    def release(self):
        self.pressed = False

    def draw(self):

        if self.pressed or self.intersects(pygame.mouse.get_pos()):
            image = self.BASE_IMAGE.copy()
            image.fill(self.hover_color, special_flags=pygame.BLEND_RGB_ADD)
        else:
            image = self.BASE_IMAGE
        main_screen.blit(image, (self.x, self.y))

    def draw_outline(self):
        pygame.draw.rect(main_screen, (0, 0, 0), self.rect, 2)
