import re
import numpy as np
import pygame
from data.scripts.sprite import Sprite


class Btn(Sprite):
    def __init__(
        self,
        scene,
        pos,
        text=None,
        anchors=(0, 0),
        bg=(0, 0, 0, 0),
        size=(0, 0),
    ):
        s = size[0] or text.sprite.w, size[1] or text.sprite.h
        super().__init__(s, flags=pygame.SRCALPHA)
        self.text = text
        self.anchors = anchors
        self.bg = bg
        # self.text.render(self, self.offset((1, 1)), (0, 0))
        self.scene = scene
        self.pos = np.array(pos)
        self.callbacks = {
            "hover": [],
            "press": [],
            "release": [],
        }
        self.state = ()
        self.text.render(self, anchors=(1, 1))
        self.text.pos = self.offset((1, 1))

        self.hold = False

    def add_callback(self, func, mode="press"):
        self.callbacks[mode].append(func)
        return self

    def render(self, surf, flags=0, opacity=1):
        super().render(
            surf=surf, pos=self.pos, flags=flags, opacity=opacity, anchors=self.anchors
        )
        # pygame.draw.rect(
        #     surf,
        #     "red",
        #     self.get_rect(self.pos + self.o),
        # )

    def update(self, offset):
        self.state = set()
        self.text.pos = self.offset((1, 1))

        self.clear(self.bg)
        self.text.render(self, anchors=(0, 0))
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
