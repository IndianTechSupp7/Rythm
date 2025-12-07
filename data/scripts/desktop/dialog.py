from math import pi
from pydoc import text
import numpy as np
import pygame
from data.scripts.sprite import Sprite
from data.scripts.ui import Btn
from data.scripts.ui.letter import RandLetter


class Dialog(Sprite):
    def __init__(
        self, scene, pos, size, msg="", title="error", on_press=lambda: ..., max_width=0
    ):
        self.scene = scene
        self.pos = pos
        self.size = size
        self.on_press = on_press
        super().__init__(self.size)
        self.clear("white")
        self.header = pygame.Surface((self.w, 10), pygame.SRCALPHA)
        self.header.fill((0, 0, 0, 50))
        self.font = RandLetter(self.scene)

        self.title = self.font.add_text(
            name="title",
            text=title,
            pos=(0, 5),
            anchors=(1.2, 0),
            color=(0, 0, 0, 100),
        )
        self.msg = self.font.add_text(
            name="msg",
            text=msg,
            color="black",
            pos=self.offset((1, 1)),
            max_width=max_width,
        )

        self.ok = Btn(
            self.scene,
            self.size,
            self.font.add_text(name="ok", text="ok", color="black"),
            size=(30, 10),
            anchors=(-1.5, -2.5),
            bg=(0, 0, 0, 30),
        )
        self.X = Btn(
            self.scene,
            (self.size[0], 0),
            self.font.add_text(name="X", text="X", color="black"),
            size=(10, 10),
            anchors=(-1, 1),
            bg=(0, 0, 0, 0),
        )
        self._grab_offset = (0, 0)
        self._grap = False
        self.r = self.header.get_rect()

        self.ok.callbacks["press"].append(self._on_ok_press)
        self.ok.callbacks["release"].append(self._on_ok_release)

        self.X.callbacks["press"].append(self._on_exit)
        self.X.callbacks["release"].append(self._on_exit_r)

    def setup(self):
        pygame.mixer.Sound(self.scene.assets.sfx["error.mp3"]).play()
        return self

    def _on_ok_press(self, btn):
        self.ok.bg = (0, 0, 0, 60)

    def _on_ok_release(self, btn):
        self.ok.bg = (0, 0, 0, 30)
        self.scene.dialogs.remove(self)
        self.on_press()

    def _on_exit(self, btn):
        self.X.bg = (0, 0, 0, 30)

    def _on_exit_r(self, btn):
        self.X.bg = (0, 0, 0, 0)
        self.scene.dialogs.remove(self)
        self.on_press()

    def update(self):
        p = self.pos - self.offset((1, 1))
        self.ok.update(p)
        self.X.update(p)
        self.r.centerx = self.pos[0]
        self.r.y = ((self.pos + self.offset((0, -1))))[1]
        if self.scene.mouse["press"][0]:
            if self.r.collidepoint(self.scene.mouse["pos"]):
                self._grap = True
                self._grab_offset = np.array(self.pos - self.scene.mouse["pos"])
        if self._grap:
            self.pos = np.array(self.scene.mouse["pos"]) + self._grab_offset
        if self.scene.mouse["release"][0]:
            self._grap = False

    def render(self, surf):
        self.clear("white")
        self.header.fill((200, 200, 200))
        self.title.render(self.header)
        self.blit(self.header, (0, 0))
        self.msg.render(self)
        self.ok.render(self)
        self.X.render(self)
        super().render(surf, self.pos, (0, 0))
