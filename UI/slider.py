import pygame

from surfaces import main_screen


class Slider:
    def __init__(self,
                 x,
                 y,
                 width,
                 height,

                 button_width=20,
                 button_height=None,

                 min_value=0.0,
                 max_value=1.0,
                 value_percentage=0.5,

                 image=None,
                 hover_color=(100, 100, 100)):

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.min_value = min_value
        self.max_value = max_value
        self.value = (value_percentage * (max_value - min_value)) + min_value

        if button_height is None:
            button_height = height

        self.background_offset = height / 3
        self.BASE_IMAGE = pygame.image.load("sprites/slider_bar.png")
        self.BASE_IMAGE = pygame.transform.scale(self.BASE_IMAGE, (width, height - self.background_offset * 2))

        self.BUTTON_BASE_IMAGE = pygame.transform.scale(image, (button_width, button_height))
        self.rect = self.BUTTON_BASE_IMAGE.get_rect()
        self.rect.topleft = (x + value_percentage * (width - button_width), y)
        self.hover_color = hover_color

        self.dragging = False

    def update_value(self):
        self.value = ((self.max_value - self.min_value) *
                      ((self.rect.x - self.x) / (self.width - self.rect.width)) +
                      self.min_value)

    def intersects(self, other_coordinates):
        return self.rect.collidepoint(other_coordinates)

    def release(self):
        self.dragging = False

    def handle_click(self, other_coordinates):
        if self.intersects(other_coordinates):
            self.dragging = True

    def move_handle(self, x):
        new_x = (max(self.x + self.rect.width / 2,
                 min(x, self.x + self.width - self.rect.width / 2))
                 - self.rect.width / 2)  # clamp x
        self.rect.x = new_x
        self.update_value()

    def update(self):
        if self.dragging:
            self.move_handle(pygame.mouse.get_pos()[0])

    def get_value(self):
        return self.value

    def draw(self):

        main_screen.blit(self.BASE_IMAGE, (self.x, self.y + self.background_offset))
        main_screen.blit(self.BUTTON_BASE_IMAGE,
                         (self.rect.x,
                          self.rect.y))
