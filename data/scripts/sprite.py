from tkinter import NO
import numpy as np
import pygame
from window import ShaderWindow


class Sprite:
    def __init__(self, surf: pygame.Surface | tuple = (0, 0), *, flags=0):
        if type(surf) == pygame.Surface:
            self._surf = surf
        else:
            w = surf[0] or ShaderWindow.w
            h = surf[1] or ShaderWindow.h
            self._surf = pygame.Surface((w, h), flags)
            # self._surf.fill((0, 0, 0))

        self._base_surf = surf
        self.rect = self._surf.get_rect()
        self.w, self.h = self._surf.get_size()
        self.base_size = np.array(self._surf.get_size())

    def offset(self, anchor=(0, 0)):
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
        self.w, self.h = self._surf.get_size()

    def get_rect(self, pos=(0, 0)):
        return pygame.Rect((*pos, *self._surf.get_size()))

    def scale_nrom(self, scale):
        _surf = pygame.transform.scale(self._base_surf, self.base_size * scale)
        # self.rect = self._surf.get_rect()
        # self.w, self.h = self._surf.get_size()
        return Sprite(_surf)

    def copy(self):
        return Sprite(self._surf.copy())

    def render(self, surf: pygame.Surface, pos, anchors=(0, 0), flags=0):
        surf.blit(
            self._surf,
            np.array(pos) - self.rect.center + (self.rect.center * np.array(anchors)),
            special_flags=flags,
        )
