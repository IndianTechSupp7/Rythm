import numpy as np
from data.scripts.sprite import Sprite
from data.scripts.ui.letter import RandLetter
from . import Physics
import random


class Bit(Physics):
    def __init__(self, scene, pos, vel, scale, color="white"):
        self.scene = scene
        self.pos = np.array(list(pos))
        self.vel = np.array(list(vel))
        self.scale = scale
        self.color = color

        self.font = RandLetter(self.scene)
        self.sprite = Sprite(
            self.font.render(random.randint(0, 1), color=self.color)
        ).scale_nrom(self.scale)
        self.life_time = 5
