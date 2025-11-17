from tkinter import NO
import numpy as np
import pygame


class Sprite:
    def __init__(self, surf: pygame.Surface):
        self._surf = surf
        self._base_surf = surf
        self.rect = self._surf.get_rect()
        self.base_size = np.array(self._surf.get_size())

    def offset(self, anchor):
        return self.rect.center * np.array(anchor)

    def get(self) -> pygame.Surface:
        return self._surf

    @property
    def surf(self):
        return self._surf

    @surf.setter
    def surf(self, new):
        self._surf = new
        self.rect = self._surf.get_rect()

    def get_rect(self, pos=(0, 0)):
        return pygame.Rect((*pos, *self._surf.get_size()))

    def scale_nrom(self, scale):
        self._surf = pygame.transform.scale(self._base_surf, self.base_size * scale)
        self.rect = self._surf.get_rect()
        return self

    def copy(self):
        return Sprite(self._surf.copy())

    def render(self, surf: pygame.Surface, pos, anchors=(0, 0), flags=0):
        surf.blit(
            self._surf,
            np.array(pos) - self.rect.center + (self.rect.center * np.array(anchors)),
            special_flags=flags,
        )
