import re
import numpy as np
from data.scripts.sprite import Sprite


class Physics:
    GRAVITY = 50
    MAX_VELOCITY = 300

    def __init__(self, pos, vel, size, color="white"):
        self.pos = np.array(list(pos))
        self.vel = np.array(list(vel))
        self.size = size
        self.color = color

        self.sprite = Sprite(size)
        self.sprite.clear(self.color)
        self.life_time = 5

    def update(self, dt):
        self.vel[1] = min(self.vel[1] + self.GRAVITY * dt, self.MAX_VELOCITY * dt)
        self.pos += self.vel
        self.life_time = max(0, self.life_time - 1 * dt)
        if self.life_time <= 0:
            return True

    def render(self, surf, offset):
        self.sprite.render(surf, self.pos - offset)
