from sys import flags
import numpy as np
import pygame
from data.scripts.sprite import Sprite
from data.scripts.utilities import clamp, lerp


class Circle:
    def __init__(
        self,
        pos,
        min_r=10,
        max_r=120,
        color="white",
        speed=1,
        width=10,
        easing=lambda x: x,
    ):
        self.pos = np.array(list(pos))
        self.max_r = max_r
        self.radius = self.min_r = min_r
        self.speed = speed
        self.easing = easing
        self.width = width
        self.color = pygame.Color(color)
        self.sprite = Sprite((self.max_r * 2, self.max_r * 2), flags=pygame.SRCALPHA)

        self.t = 0

    def update(self, dt):
        self.t = clamp(self.t + self.speed * dt)
        t = self.easing(self.t)
        self.radius = lerp(self.min_r, self.max_r, t)
        if self.radius <= self.min_r:
            return True

    def render(self, surf, offset):
        self.sprite.clear()
        pygame.draw.circle(
            self.sprite.surf,
            self.color,
            (self.max_r, self.max_r),
            self.radius,
            int(max(1, ((self.radius / (self.max_r - self.min_r))) * self.width)),
        )
        self.sprite.render(surf, self.pos - offset, flags=pygame.BLEND_RGBA_ADD)
