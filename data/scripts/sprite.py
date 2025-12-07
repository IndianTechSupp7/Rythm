import numpy as np
import pygame
from window import Window

from data.scripts.utilities import clamp


class Sprite:
    def __init__(self, surf: pygame.Surface | tuple = (0, 0), *, flags=0):
        if type(surf) == pygame.Surface:
            self._surf = surf.copy()
        elif type(surf) == Sprite:
            self._surf = surf.surf.copy()
        else:
            w = surf[0] or Window.w
            h = surf[1] or Window.h
            self._surf = pygame.Surface((w, h), flags)
            # self._surf.fill((0, 0, 0))

        self._base_surf = self._surf.copy()
        self.rect = self._surf.get_rect()
        self.w, self.h = self._surf.get_size()
        self.base_size = np.array(self._surf.get_size())
        self.on_surf_change = []  # callbacks for surfchange

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
        self._base_surf = new
        self.rect = self._surf.get_rect()
        self.w, self.h = self._surf.get_size()
        for func in self.on_surf_change:
            func()

    def blit(self, surf, pos, **kwargs):
        self._surf.blit(surf, pos, **kwargs)
        self._base_surf.blit(surf, pos, **kwargs)

    def get_rect(self, pos=(0, 0)):
        return pygame.Rect((*pos, *self._surf.get_size()))

    def clear(self, color=(0, 0, 0, 0)):
        self._surf.fill(color)
        self._base_surf.fill(color)
        return self

    def scale_nrom(self, scale):
        self._surf = pygame.transform.scale(self._base_surf, self.base_size * scale)
        self.rect = self._surf.get_rect()
        self.w, self.h = self._surf.get_size()
        return self

    def scale_norm_save(self, scale):
        _surf = pygame.transform.scale(self._surf, self.base_size * scale)
        return Sprite(_surf)

    def copy(self):
        return Sprite(self._surf.copy())

    def set_perPx_opacity(self, opacity=1):
        c_surf = self._surf.copy()
        c_surf.fill(
            (255, 255, 255, clamp(opacity, 0, 1) * 255),
            special_flags=pygame.BLEND_RGBA_MULT,
        )
        return Sprite(c_surf)

    def render(self, surf: pygame.Surface, pos, anchors=(0, 0), flags=0, opacity=1):
        surf_c = self._surf.copy()
        surf_c.set_alpha(clamp(opacity, 0, 1) * 255)
        surf.blit(
            surf_c,
            np.array(pos) - self.rect.center + (self.rect.center * np.array(anchors)),
            special_flags=flags,
        )
