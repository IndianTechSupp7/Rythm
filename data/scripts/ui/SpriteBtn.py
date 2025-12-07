import numpy as np
import pygame
import pygame.draw
from data.scripts.sprite import Sprite


class SpriteBtn(Sprite):
    def __init__(
        self,
        scene,
        pos,
        surf,
        anchors=(0, 0),
    ):
        super().__init__(surf)
        self.scene = scene
        self.pos = np.array(pos)
        self.anchors = anchors
        self.callbacks = {
            "hover": [],
            "press": [],
            "release": [],
        }
        self.state = set()
        self.hold = False

        self.o = (0, 0)
    
    def add_callback(self, func, mode="press"):
        self.callbacks[mode].append(func)
        return self

    def set(self, name, value):
        if getattr(self, name, None):
            setattr(self, name, value)

    def render(self, surf, flags=0, opacity=1):
        super().render(
            surf=surf, pos=self.pos, flags=flags, opacity=opacity, anchors=self.anchors
        )

    def update(self, offset):
        self.state = set()
        self.o = self.pos + offset + self.offset(self.anchors - np.array((1, 1)))
        if self.get_rect(
            self.pos + offset + self.offset(self.anchors - np.array((1, 1)))
        ).collidepoint(self.scene.mouse["pos"]):
            self.state.add("hover")
            for cb in self.callbacks["hover"]:
                cb(self)
            if self.scene.mouse["press"][0]:
                self.state.add("press")
                self.hold = True
                for cb in self.callbacks["press"]:
                    cb(self)
        if self.scene.mouse["release"][0] and self.hold:
            self.hold = False
            self.state.add("release")
            for cb in self.callbacks["release"]:
                cb(self)
