import pygame


class DodgerSprite(pygame.sprite.Sprite):

    def __init__(self, x, y, surface):
        pygame.sprite.Sprite.__init__(self)
        self.image = surface
        self.rect = self.image.get_rect()
        self.abs_x = x
        self.abs_y = y
        self.rect.x = self.abs_x
        self.rect.y = self.abs_y

    def move(self, x_off, y_off):
        self.abs_x += x_off
        self.abs_y += y_off
        self.rect.x = self.abs_x
        self.rect.y = self.abs_y

    def clamp(self, x0, y0, x1, y1):
        """
        Adjust position based on screen size and image size
        :param x0: TOP-LEFT
        :param y0: TOP-LEFT
        :param x1: BOT-RIGHT
        :param y1: BOT-RIGHT
        :return:
        """
        if self.rect.x < x0:
            self.rect.x = x0
            self.abs_x = self.rect.x
        if self.rect.x > x1 - self.image.get_size()[0]:
            self.rect.x = x1 - self.image.get_size()[0]
            self.abs_x = self.rect.x
        if self.rect.y < y0:
            self.rect.y = y0
            self.abs_y = self.rect.y
        if self.rect.y > y1 - self.image.get_size()[1]:
            self.rect.y = y1 - self.image.get_size()[1]
            self.abs_y = self.rect.y
