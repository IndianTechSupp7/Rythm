import time
import numpy as np
import pygame
from data.scripts.sprite import Sprite
from data.scripts.utilities import Font, lerp_color, rplc_color
import random


class RandLetter(Font):
    def __init__(self, game, font_size=1, speed=1):
        self.game = game
        super().__init__(
            font_img=self.game.assets.images["font.png"], font_size=font_size
        )
        self.speed = speed
        self.is_fixed = 0
        self.texts = {}

    def add_text(
        self,
        name,
        color="white",
        secondary="gray",
        alpha=255,
        spacing=1,
        speed=1,
        anchors=(0, 0),
        pos=np.array((0, 0)),
        **options,
    ):
        self.texts[name] = Text(
            font=self,
            name=name,
            color=color,
            secondary=secondary,
            alpha=alpha,
            spacing=spacing,
            speed=speed,
            anchors=anchors,
            pos=pos,
            **options,
        )
        return self.texts[name]

    def __getitem__(self, name):
        return self.texts[name]

    def __setitem__(self, name, value):
        self.texts[name] = value

    # def render(self, text, color="white", secondary="#751756", alpha=255, spacing=1):
    #     for text in self.texts:
    #         text.render()  # x_offset = 0
    # secondary = secondary or "#751756"
    # text = str(text)

    # full_width = sum(
    #     [
    #         (
    #             (self.characters[char].get_width() + spacing)
    #             if char != " " and char != "#"
    #             else self.space_width + spacing
    #         )
    #         for char in str(text)
    #     ]
    # )

    # surf = pygame.Surface(
    #     (full_width, self.characters["A"].get_height()), pygame.SRCALPHA
    # )
    # for data in self.texts:
    #     for i, char in enumerate(data.text):
    #         if char == "#":
    #             # choice = random.choice(self.character_order)
    #             choice = data.get_offset(i)
    #             cr = rplc_color(self.characters[choice], "red", secondary)
    #             surf.blit(cr, (x_offset, 0))
    #             x_offset += self.characters[choice].get_width() + spacing
    #         if char != " ":
    #             surf.blit(self.characters[char], (x_offset, 0))
    #             x_offset += self.characters[char].get_width() + spacing
    #         else:
    #             x_offset += self.space_width + spacing

    # surf = rplc_color(surf, "red", color)
    # # surf.set_colorkey("black")
    # surf.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    # return surf


class Text:
    def __init__(self, font, name, **options):
        self._text = str(options.get("text", ""))
        self.color = options.get("color", "white")
        self.secondary = options.get("secondary", "gray")
        self.opacity = options.get("opacity", 1)
        self._spacing = options.get("spacing", 1)
        self.speed = options.get("speed", 1)
        self.anchors = options.get("anchors", (0, 0))
        self.pos = np.array(options.get("pos", (0, 0)))
        self.name = name

        self.options = options

        self._characters = font.characters
        self._char_order = font.character_order
        self._space_width = self._characters["A"].get_width()
        self.rows = self.text.split("\n")
        self.offsets = [[random.random() for _ in i] for i in self.rows]
        self.encoded = [
            [i if i != "#" else random.choice(self._char_order) for i in r]
            for r in self.rows
        ]
        # self.encoded = [
        #     i if i != "#" else random.choice(self._char_order) for i in self._text
        # ]

        self._full_size = (0, 0)
        self._set_full_size()
        self.sprite = Sprite(
            self._full_size,
            flags=pygame.SRCALPHA,
        )

        # self.text_rows = [
        #     " ".join(
        #         self.words[
        #             i : min(len(self.words) - 1, int(len(self.words) / self.y_offset))
        #             + i
        #         ]
        #     )
        #     for i in range(0, self.y_offset)
        # ]

        # self.sprite.on_surf_change.append(lambda: self._set_full_width)

    def _set_full_size(self):
        self.full_size = self._get_full_size()

    def get_txt_size(self, txt):
        return sum(
            [
                (
                    (self._characters[char].get_width() + self._spacing)
                    if char != " " and char != "#"
                    else self._space_width + self._spacing
                )
                for char in str(txt)
            ]
        )

    def _get_full_size(self):
        w = self.get_txt_size(max(self.rows, key=lambda x: len(x)))
        h = len(self.rows) * self._characters["A"].get_height()
        return w, h

    @property
    def spacing(self):
        return self.spacing

    @spacing.setter
    def spacing(self, value):
        self._spacing = value
        self._set_full_size()

    @property
    def full_size(self):
        return self._full_size

    @full_size.setter
    def full_size(self, value):
        if self._full_size != value:
            self._full_size = value
            self.sprite = Sprite(
                self._full_size,
                flags=pygame.SRCALPHA,
            )

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new):
        if len(new) != len(self._text):
            self._text = str(new)
            self.rows = self._text.split("\n")
            self.encoded = [
                [i if i != "#" else random.choice(self._char_order) for i in r]
                for r in self.rows
            ]
        else:
            self._text = str(new)
            self.rows = self._text.split("\n")

        # w = self._get_full_width()
        # if self._full_width != w:
        #     self._set_full_width()
        #     self.sprite = Sprite(
        #         (self._full_width, self._characters["A"].get_height()),
        #         flags=pygame.SRCALPHA,
        #     )
        # self.rows = self.text.split("\n")
        self.offsets = [[random.random() for _ in i] for i in self.rows]
        self._set_full_size()

    def get_offset(self, index, y):
        if int((time.time() % (self.offsets[y][index] + self.speed))) == 0:
            self.encoded[y][index] = random.choice(self._char_order)
        return self.encoded[y][index]

    def get_render(self):
        x_offset = 0
        self.sprite.clear()

        for y, row in enumerate(self.rows):
            x_offset = 0
            row_width = self.get_txt_size(row)
            for i, char in enumerate(row):
                if char == "#":
                    # choice = random.choice(self.character_order)
                    choice = self.get_offset(i, y)
                    cr = rplc_color(self._characters[choice], "red", self.secondary)
                    self.sprite.blit(
                        cr,
                        (
                            self.sprite.w / 2 - row_width / 2 + x_offset,
                            y * self._characters["A"].get_height(),
                        ),
                    )
                    x_offset += self._characters[choice].get_width() + self._spacing
                elif char != " ":
                    self.sprite.blit(
                        self._characters[char],
                        (
                            self.sprite.w / 2 - row_width / 2 + x_offset,
                            y * self._characters["A"].get_height(),
                        ),
                    )
                    x_offset += self._characters[char].get_width() + self._spacing
                else:
                    x_offset += self._space_width + self._spacing
        self.sprite.surf = rplc_color(self.sprite.surf, "red", self.color)
        return self.sprite

    def render(self, surf: pygame.Surface, anchors=None, flags=0, pos=None):
        if anchors:
            self.anchors = anchors
        if pos:
            self.pos = np.array(pos)
        self.sprite.clear()
        for y, row in enumerate(self.rows):
            x_offset = 0
            row_width = self.get_txt_size(row)
            for i, char in enumerate(row):
                if char == "#":
                    # choice = random.choice(self.character_order)
                    choice = self.get_offset(i, y)
                    cr = rplc_color(self._characters[choice], "red", self.secondary)
                    self.sprite.blit(
                        cr,
                        (
                            self.sprite.w / 2 - row_width / 2 + x_offset,
                            y * self._characters["A"].get_height(),
                        ),
                    )
                    x_offset += self._characters[choice].get_width() + self._spacing
                elif char != " ":
                    self.sprite.blit(
                        self._characters[char],
                        (
                            self.sprite.w / 2 - row_width / 2 + x_offset,
                            y * self._characters["A"].get_height(),
                        ),
                    )
                    x_offset += self._characters[char].get_width() + self._spacing
                else:
                    x_offset += self._space_width + self._spacing
        self.sprite.surf = rplc_color(self.sprite.surf, "red", self.color)
        self.sprite.render(
            surf, self.pos, anchors=self.anchors, flags=flags, opacity=self.opacity
        )
