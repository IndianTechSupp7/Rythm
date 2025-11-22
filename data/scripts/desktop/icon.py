"""
{
  "pos" : (0, 0) # grid_pos
  "img" : <Sprite> # the "icon img" of the icon
  "to" : "Scene Name" # the name of the target Scene
}
"""

import numpy as np

from data.scripts.sprite import Sprite

PADDING = np.array((3, 3))
TILE_WIDTH = 32 - PADDING[0] * 2
TILE_HEIGTH = 32 - PADDING[1] * 2


class Icon:
    selected = []

    def __init__(self, scene, settings):
        self.scene = scene
        self.settings = settings

        self.tile_pos = self.settings.get("pos", (0, 0))
        self.img: Sprite = self.settings.get("img", Sprite((TILE_WIDTH, TILE_HEIGTH)))
        self.pos = np.array((0, 0))

    def activate(self): ...

    def update(self, w, h):
        self.pos = np.array((w, h)) * self.tile_pos

    def render(self, surf):
        render_pos = self.pos + np.array((16, 16))
        self.img.render(surf, render_pos, (0, 0))
