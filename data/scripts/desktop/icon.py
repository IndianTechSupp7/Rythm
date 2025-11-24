"""
{
  "pos" : (0, 0) # grid_pos
  "img" : <Sprite> # the "icon img" of the icon
  "on_press" : <func> # callback func for pressing the icon
  "title" : "Title" # title :)
}
"""

import py_compile
import numpy as np
import pygame

from data.scripts.sprite import Sprite
from data.scripts.ui.letter import RandLetter

PADDING = np.array((3, 3))
TILE_WIDTH = 32 - PADDING[0] * 2
TILE_HEIGTH = 32 - PADDING[1] * 2


class Icon:
    selected = []

    def __init__(self, scene, settings):
        self.scene = scene
        self.settings = settings

        self.tile_pos = self.settings.get("pos", (0, 0))
        self.on_press = self.settings.get("on_press", lambda: ...)
        self.title = self.settings.get("title", "No Name")
        self.img: Sprite = self.settings.get("img", Sprite((TILE_WIDTH, TILE_HEIGTH)))

        self.pos = np.array((0, 0))
        self.font = RandLetter(self.scene, 1)
        self.text_sprite = Sprite(self.font.render(self.title, "white"))
        self.rect = self.img.get_rect().inflate(10, 10)

    def activate(self): ...

    def update(self, w, h):
        self.pos = np.array((w, h)) * self.tile_pos
        self.rect.center = self.pos + np.array((16, 16))
        if self.rect.collidepoint(self.scene.mouse["pos"]):
            if self.scene.mouse["press"][0]:
                if self in Icon.selected:
                    self.on_press()
                else:
                    if not pygame.key.get_pressed()[pygame.K_LSHIFT]:
                        Icon.selected = []
                    Icon.selected.append(self)

    def render(self, surf):
        render_pos = self.pos + np.array((16, 16))
        if self in Icon.selected:
            pygame.draw.rect(
                surf,
                ("#aee3ff81"),
                (
                    *(self.pos),
                    32 + PADDING[0],
                    32 + PADDING[1] + 5,
                ),
            )
            # pygame.draw.rect(surf, ("#aee3ff81"), self.rect)
        self.img.render(surf, render_pos, (0, 0))
        self.text_sprite.render(surf, render_pos, (0, 4))
