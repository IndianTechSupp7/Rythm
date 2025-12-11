"""
{
  "pos" : (0, 0) # grid_pos
  "img" : <Sprite> # the "icon img" of the icon
  "on_press" : <func> # callback func for pressing the icon
  "title" : "Title" # title :)
}
"""

from turtle import color
import numpy as np
import pygame

from data.scripts.sprite import Sprite
from data.scripts.ui.letter import RandLetter
from data.scripts.ui.progressbar import Bar, SmoothBar

PADDING = np.array((3, 3))
TILE_WIDTH = 32
TILE_HEIGTH = 42
TILE_PADDING = (TILE_WIDTH - PADDING[0] * 2, TILE_HEIGTH - PADDING[1] * 2)


class Icon:
    selected = []
    icons = []
    scene = None
    ipos = set()

    def __init__(self, scene, settings):
        self.scene = scene
        self.settings = settings

        self.tile_pos = self.settings.get("pos", (0, 0))
        self.on_press = self.settings.get("on_press", lambda: ...)
        self.title = self.settings.get("title", "No Name")
        self.progress = self.settings.get("progress", 0)

        self.font = RandLetter(self.scene)

        self.dm_title = self.title

        if len(self.dm_title) > 15 and " " in self.dm_title:
            text: list = self.dm_title.split(" ")
            text.insert(int(len(text) / 2), "\n")
            self.dm_title = " ".join(text)
        self.locked_txt = "".join(
            ["#" if i not in [" ", "\n"] else i for i in self.dm_title]
        )

        p = int(self.progress * len(self.dm_title))
        render_title = self.dm_title[:p] + self.locked_txt[p:]
        self.img: Sprite = self.settings.get("img", Sprite(TILE_PADDING))

        self.pos = np.array((TILE_WIDTH, TILE_HEIGTH)) * self.tile_pos
        self.font.add_text(
            "title", text=render_title, speed=10, secondary=(255, 255, 255, 50)
        )
        # if self.font["title"].full_size[0] > TILE_WIDTH and " " in render_title:
        #     text: list = render_title.split(" ")
        #     text.insert(int(len(text) / 2), "\n")
        #     self.font["title"].text = " ".join(text)

        self.rect = self.img.get_rect().inflate(10, 10)

        self.dragging = False
        self.offset = np.array((0.0, 0.0))
        self.double_clikc = 0
        self.hold_offset = np.array((0, 0))

    def update(self, dt):
        p = int(self.progress * len(self.dm_title))
        render_title = self.dm_title[:p] + self.locked_txt[p:]
        # if self.font["title"].full_size[0] > TILE_WIDTH and " " in render_title:
        #     text: list = render_title.split(" ")
        #     text.insert(int(len(text) / 2), "\n")
        #     self.font["title"].text = " ".join(text)
        # else:
        self.font["title"].text = render_title

        self.double_clikc = max(0, self.double_clikc - 2 * dt)
        self.pos = np.array((TILE_WIDTH, TILE_HEIGTH)) * self.tile_pos
        self.rect.center = self.pos + np.array((16, 16))
        pressed = False
        if self.rect.collidepoint(self.scene.mouse["pos"]) or self.dragging:
            if self.scene.mouse["press"][0]:
                self.offset = self.scene.mouse["pos"] - self.pos
                if self in Icon.selected:
                    self.double_clikc += 2
                else:
                    if not pygame.key.get_pressed()[pygame.K_LSHIFT]:
                        Icon.selected = []
                    Icon.selected.append(self)
                    self.double_clikc += 2
                pressed = True
            if self in Icon.selected:
                if self.scene.mouse["hold"][0]:
                    if (np.abs(self.hold_offset) > (1, 1)).all():
                        self.dragging = True
                    else:
                        self.hold_offset += self.scene.mouse["rel"]

        if self.dragging:
            self.pos = self.scene.mouse["pos"] - self.offset
            self.hold_offset = np.array((0, 0))
            self.double_clikc = 0

        if self.scene.mouse["release"][0]:
            self.dragging = False

            tile_pos = tuple([round(i) for i in self.pos / (TILE_WIDTH, TILE_HEIGTH)])
            if not tile_pos in Icon.ipos:
                # print(tile_pos, Icon.ipos)
                Icon.ipos.remove(self.tile_pos)
                self.tile_pos = tile_pos
                Icon.ipos.add(self.tile_pos)
                data = self.scene.assets.configs["level"]
                data["songs"][".".join(self.title.split(".")[:-1])][0] = self.tile_pos[0]
                data["songs"][".".join(self.title.split(".")[:-1])][1] = self.tile_pos[1]
                self.scene.assets.save_config("level", data)
                # write_json(
                #     self.scene.assets.BASE_ASSETS_FOLDER + "/config/level.json", data
                # )
        if self.double_clikc > 3:
            self.on_press()
        return pressed

    def render(self, surf):
        render_pos = self.pos + np.array((16, 16))
        if self in Icon.selected:
            pygame.draw.rect(
                surf,
                (174, 227, 255, 100),
                (
                    *(self.pos),
                    32,
                    42,
                ),
            )
            # pygame.draw.rect(surf, ("#aee3ff81"), self.rect)
        self.img.render(surf, render_pos, (0, 0))
        self.font["title"].pos = render_pos + (0, 16)
        self.font["title"].render(surf, (0, 1))
        # pygame.draw.circle(surf, "red", self.font["title"].pos, 4)

    @classmethod
    def reset(cls):
        for icon in cls.icons:
            icon.dragging = False
            icon.offset = np.array((0.0, 0.0))
            icon.double_clikc = 0
            icon.hold_offset = np.array((0, 0))
        cls.selected = []

    @classmethod
    def add_icon(cls, **settings):
        cls.icons.append(Icon(cls.scene, settings))
        cls.ipos.add(settings["pos"])

    @classmethod
    def update_icons(cls, dt):
        for icon in cls.icons:
            icon.update(dt)

    @classmethod
    def render_icons(cls, surf):
        for icon in cls.icons:
            icon.render(surf)


class ProgressIcon(Icon):
    def __init__(self, scene, **settings):
        super().__init__(scene, settings)
        self.load_progress = self.scene.game.current_progress
        self.bar = SmoothBar(self.scene, scale=(32, 5), value=self.load_progress)

    def update(self, dt):
        super().update(dt)
        if self.load_progress != 1:
            self.load_progress = self.scene.game.current_progress
        self.bar.value = self.load_progress
        self.bar.update(dt)

    def render(self, surf):
        render_pos = self.pos + np.array((16, 16))
        if self in Icon.selected:
            pygame.draw.rect(
                surf,
                (174, 227, 255, 100),
                (
                    *(self.pos),
                    32,
                    42,
                ),
            )
            # pygame.draw.rect(surf, ("#aee3ff81"), self.rect)
        self.img.render(surf, render_pos, (0, 0))
        if not self.load_progress or self.load_progress % 1:
            self.bar.render(surf, render_pos + (0, 16), anchors=(0, 1))
        else:
            self.font["title"].pos = render_pos + (0, 16)
            self.font["title"].render(surf, (0, 1))
