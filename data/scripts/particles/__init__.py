from .Circle import Circle
from .Spark import Spark
from .Physics import Physics
from .Bit import Bit


class Manager:
    def __init__(self, game):
        self.game = game

        self.particles = []

    def add_particle(self, particle):
        self.particles.append(particle)

    def update(self, dt):
        for i, p in sorted(enumerate(self.particles), reverse=True):
            if p.update(dt):
                self.particles.pop(i)

    def render(self, surf, offset=(0, 0)):
        for p in self.particles:
            p.render(surf, offset)
