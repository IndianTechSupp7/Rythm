import re
import pygame
from data.scripts.sprite import Sprite
from data.scripts.utilities import clamp


class Bar(Sprite):
    def __init__(
        self,
        scene,
        value,
        min,
        max,
        scale,
        color="white",
        secondary=(255, 255, 255, 30),
    ):
        super().__init__(scale, flags=pygame.SRCALPHA)
        self.scale = scale
        self.scene = scene
        self._value = value
        self.min = min
        self.max = max
        self.color = color
        self.secondary = secondary
        self.t = self._get_value()
        self.srf = pygame.Surface((int(self.scale[0] * self.t), self.scale[1]))
        self.srf.fill(self.color)

    def _get_value(self):
        return self.value / (self.max - self.min)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = clamp(val, self.min, self.max)
        self.t = self._get_value()
        self.srf = pygame.Surface((int(self.scale[0] * self.t), self.scale[1]))
        self.srf.fill(self.color)

    def render(self, surf, pos, anchors=(0, 0), flags=0, opacity=1):
        self.clear(self.secondary)
        self.blit(self.srf, (0, 0))
        return super().render(surf, pos, anchors, flags, opacity)
