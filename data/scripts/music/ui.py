import time
import numpy as np
import pygame
from data.scripts.desktop.desktop import Menu, Table
from data.scripts.ui import Bar
from data.scripts.utilities import bezier, lerp, clamp
from data.scripts.sprite import Sprite
from data.scripts.ui import RandLetter


class UI:
    def __init__(self, music):
        self.music = music
        self.game = self.music.game
        self.center = self.music.center
        self.surf = pygame.Surface(self.music.surf.get_size(), pygame.SRCALPHA)
        self.current_state = None


        self.font = RandLetter(self.music, 2)
        self.counter = 0
        self.base_text = self.music.current_song_name + ".mp3"
        self.index = int(len(self.base_text) * self.music.full_time)
        self.text = "".join(
            [
                ch if i <= self.index or ch == " " else "#"
                for i, ch in enumerate(self.base_text)
            ]
        )
        # self.text_sprite = Sprite(self.rndl.render(self.text, "white"))
        self.secondary = None
        # self.rnd_sprite = Sprite(self.rndl.render(self.text[self.index :], "#751756"))
        self.font.add_text(
            name="title",
            text=self.text,
            scale=1,
            pos=np.array((self.center[0], 25)),
            opacity=1,
            anchor=(0, -1),
            speed=10,
        )
        self.font.add_text(
            name="next",
            text="Nyomja meg az Enter-t a kilépéshez",
            scale=0.5,
            pos=np.array((self.center[0], self.center[1] + self.center[1] / 4)),
            opacity=0,
            anchor=(0, -1),
            spacing=2,
        )

        self.t = 0
        # self.ui_title_pos = self.text_buffer["title"]["pos"]
        self.ui_title_pos = self.font["title"].pos.copy()
        # self.title_pos = np.array((self.center[0], 15))
        # self.target_title_pos = np.array((self.center[0], 15))
        # self.scale = 1

        self.bar = Bar(
            self.game,
            self.music.full_time,
            0,
            1,
            (60, 5),
            secondary=(255, 255, 255, 10),
        )
        self.fade = 0

        # self.music.on_finish.append(self.on_pause)

        self.music.on_finish.append(self.on_pause)
        self.music.on_pause.append(self.on_pause)
        self.music.on_unpause.append(self.on_pause)

    def on_pause(self):
        self.t = time.time()

    def menu(self, t):
        # self.text_buffer["title"]["pos"] = lerp(self.ui_title_pos, self.center, t)
        # self.text_buffer["title"]["scale"] = lerp(1, 1.4, t)
        # self.text_buffer["next"]["opacity"] = lerp(0, 1, t)
        self.font["title"].pos = lerp(self.ui_title_pos, self.center, t)
        self.font["title"].options["scale"] = lerp(1, 1.4, t)
        self.font["next"].options["opacity"] = lerp(0, 1, t)
        self.fade = lerp(0, 1, t)

    # def when_finish(self):
    #     t = bezier(0.833, 0.889, 0.089, 0.993, clamp(time.time() - self.t, 0, 1))[1]
    #     self.text_buffer["title"]["pos"] = lerp(self.ui_title_pos, self.center, t)
    #     self.text_buffer["title"]["scale"] = lerp(1, 1.4, t)
    #     self.text_buffer["next"]["opacity"] = lerp(0, 1, t)

    def update(self):
        if self.music.finished or self.music.is_paused:
            t = bezier(0.833, 0.889, 0.089, 0.993, clamp(time.time() - self.t, 0, 1))[1]
        else:
            t = (
                1
                - bezier(0.833, 0.889, 0.089, 0.993, clamp(time.time() - self.t, 0, 1))[
                    1
                ]
            )
        self.menu(t)

        self.counter += 1

        if self.counter % 10 == 0:
            # self.text_buffer["title"]["text"] = self.text
            # self.text_buffer["title"]["secondary"] = self.secondary
            self.font["title"].text = self.text
            self.font["title"].secondary = self.secondary

            # self.rnd_sprite.surf = self.rndl.render(self.text[self.index :], "#751756")
        self.index = int(
            len(self.base_text) * max(self.music.full_time, self.music.progress)
        )
        self.text = "".join(
            [
                ch if i <= self.index or ch == " " else "#"
                for i, ch in enumerate(self.base_text)
            ]
        )
        self.bar.value = self.music.full_time

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

    def render(self, surf, offset=np.array((0, 0))):
        # self.surf.set_alpha(0)
        # surf.blit(self.surf, (0, 0))
        self.surf.fill((0, 0, 0, self.fade * 180))
        surf.blit(self.surf, (0, 0))
        for name, text in self.font.texts.items():
            # color = pygame.Color(text.get("color", "white"))
            # s = self.rndl.render(
            #     text["text"],
            #     text.get("color", "white"),
            #     secoundary=text.get("secondary", "white"),
            # )
            # ms = pygame.Surface(s.get_size(), pygame.SRCALPHA)
            # # ms.fill((0, 0, 0, 0))
            # ms.blit(s, (0, 0))
            # # ms.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MULT)
            # surf.blit(ms, text.get("pos", (0, 0)))
            # surf.blit(ms, text.get("pos", (0, 0)))
            render = text.get_render()
            # if name == "title":
            #     render.clear("white")
            render.scale_norm_save(text.options["scale"]).render(
                surf=surf,
                pos=text.pos - offset,
                anchors=text.options.get("anchor", (0, 0)),
                opacity=text.options["opacity"],
            )
            self.bar.render(surf, (self.music.w - 10, 10), (-1, 1))
            # Sprite(
            #     self.rndl.render(
            #         text["text"],
            #         text.get("color", "white"),
            #         secoundary=text.get("secondary", "white"),
            #     )
            # ).scale_nrom(text.get("scale", 1)).render(
            #     surf,
            #     text.get("pos", (0, 0)) - offset,
            #     text.get("anchor", (0, 0)),
            #     opacity=text.get("opacity", 1),
            # )

        # self.rnd_sprite.render(surf, (self.center[0], 15), (0, 0))
