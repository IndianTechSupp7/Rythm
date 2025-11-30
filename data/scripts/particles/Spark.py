import numpy as np
import pygame

from data.scripts.utilities import adjuts


class Spark:
    def __init__(self, pos, dir=0, size=10, speed=1, thickness=0.1, color="white"):
        self.pos = np.array(list(pos))
        self.dir = dir
        self.size = size
        self.color = color
        self.speed = speed
        self.thickness = thickness

    def get_points(self, offset):
        points = [
            adjuts(self.pos - offset, self.dir, self.size * self.thickness),
            adjuts(
                self.pos - offset, (np.pi / 2) + self.dir, self.size * self.thickness
            ),
            adjuts(self.pos - offset, np.pi + self.dir, self.size),
            adjuts(
                self.pos - offset, (-np.pi / 2) + self.dir, self.size * self.thickness
            ),
        ]
        return points

    def update(self, dt):
        self.pos = adjuts(self.pos, self.dir, self.size)
        self.size -= self.speed * dt
        if self.size <= 0:
            return True

    def render(self, surf, offset=(0, 0)):
        pygame.draw.polygon(surf, self.color, self.get_points(offset))
