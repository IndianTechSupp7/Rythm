import time
import numpy as np
import pygame
from data.scripts.utilities import bezier, lerp, clamp
from data.scripts.sprite import Sprite
from .letter import RandLetter


class UI:
    def __init__(self, music):
        self.music = music
        self.game = self.music.game
        self.center = self.music.center
        self.surf = pygame.Surface(self.music.surf.get_size(), pygame.SRCALPHA)
        self.current_state = None

        self.rndl = RandLetter(self.music, 2)
        self.counter = 0
        self.base_text = self.music.current_song_name + ".mp3"
        self.index = int(len(self.base_text) * self.music.full_time)
        self.text = [
            ch if i <= self.index or ch == " " else "#"
            for i, ch in enumerate(self.base_text)
        ]
        # self.text_sprite = Sprite(self.rndl.render(self.text, "white"))
        self.secondary = None
        # self.rnd_sprite = Sprite(self.rndl.render(self.text[self.index :], "#751756"))

        self.text_buffer = {
            "title": {
                "text": self.text,
                "scale": 1,
                "color": "white",
                "pos": np.array((self.center[0], 15)),
                "opacity": 1,
            },
            "next": {
                "text": "Press Enter to continue",
                "scale": 0.5,
                "color": "white",
                "pos": np.array((self.center[0], self.center[0])),
                "opacity": 0,
                "anchor": (0, -1),
            },
        }

        # self.title_pos = np.array((self.center[0], 15))
        # self.target_title_pos = np.array((self.center[0], 15))
        # self.scale = 1

        self.music.on_finish.append(self.on_finish)

    def on_finish(self):
        self.ui_title_pos = self.text_buffer["title"]["pos"]
        self.t = time.time()

    def menu(self):
        pass

    def when_finish(self):
        t = bezier(0.833, 0.889, 0.089, 0.993, clamp(time.time() - self.t, 0, 1))[1]
        self.text_buffer["title"]["pos"] = lerp(self.ui_title_pos, self.center, t)
        self.text_buffer["title"]["scale"] = lerp(1, 3, t)
        self.text_buffer["next"]["opacity"] = lerp(0, 1, t)

    def update(self):
        self.surf.fill((0, 0, 0, 0))
        if self.music.finished:
            self.when_finish()
        self.counter += 1

        if self.counter % 10 == 0:
            self.text_buffer["title"]["text"] = self.text
            self.text_buffer["title"]["secondary"] = self.secondary

            # self.rnd_sprite.surf = self.rndl.render(self.text[self.index :], "#751756")
        self.index = int(len(self.base_text) * self.music.full_time)
        self.text = [
            ch if i <= self.index or ch == " " else "#"
            for i, ch in enumerate(self.base_text)
        ]

        # self.title_pos[0] = move_towards(
        #     self.title_pos[0], self.target_title_pos[0], 100, self.game.dt
        # )
        # self.title_pos[1] = move_towards(
        #     self.title_pos[1], self.target_title_pos[1], 100, self.game.dt
        # )
        # for text in self.text_buffer.values():
        #     # color = pygame.Color(text.get("color", "white"))
        #     print(text.get("opacity", 1))
        #     Sprite(
        #         self.rndl.render(
        #             text["text"],
        #             text.get("color", "white"),
        #             secoundary=text.get("secondary", "white"),
        #         )
        #     ).scale_nrom(text.get("scale", 1)).set_perPx_opacity(0).render(
        #         self.surf,
        #         text.get("pos", (0, 0)),
        #         text.get("anchor", (0, 0)),
        #     )

    def render(self, surf):
        # self.surf.set_alpha(0)
        # surf.blit(self.surf, (0, 0))
        for text in self.text_buffer.values():
            # color = pygame.Color(text.get("color", "white"))
            Sprite(
                self.rndl.render(
                    text["text"],
                    text.get("color", "white"),
                    secoundary=text.get("secondary", "white"),
                )
            ).scale_nrom(text.get("scale", 1)).render(
                surf, text.get("pos", (0, 0)), text.get("anchor", (0, 0)), opacity=0
            )

        # self.rnd_sprite.render(surf, (self.center[0], 15), (0, 0))
