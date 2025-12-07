from pydoc import text
import time
from turtle import color
import numpy as np
import pygame
from sympy import sec
from window import Window
from data.scripts.desktop.icon import Icon
from data.scripts.scene import Scene
from data.scripts.sprite import Sprite
from data.scripts.ui import Slider, SpriteBtn
from data.scripts.ui.TextBtn import Btn
from data.scripts.ui.checkbox import CheckBox
from data.scripts.ui.letter import RandLetter, Text
from data.scripts.utilities import clamp, get_json, lerp, move_towards, write_json


class DesktopGrid:
    def __init__(self, scene: Scene):
        self.scene = scene
        self.mouse = self.scene.mouse
        self.assets = self.scene.assets

        Icon.scene = self.scene

        # self.surf = Sprite(
        #     tuple(np.array(self.scene.size) * 0.5), flags=pygame.SRCALPHA
        # )

        for song, data in self.scene.assets.configs["level"]["songs"].items():
            Icon.add_icon(
                **{
                    "title": song + ".mp3",
                    "pos": (data[0], data[1]),
                    "progress": data[2],
                    "on_press": lambda song=song: self.open_music(song),
                    "img": Sprite(self.scene.assets.images["ext"]["mp3.png"]),
                }
            )

        self._prev_selected = Icon.selected.copy()

    def update_song_progress(self):
        data = self.scene.assets.configs["level"]["songs"]
        for song in Icon.icons:
            song.progress = data["".join(song.title.split(".")[:-1])][2]

    def open_music(self, music):
        self.scene.game.current_song_name = music
        Icon.reset()
        Scene.change_scene("Music")

    # def add_icon(self, **settings):
    #     self.icons.append(Icon(self.scene, settings))

    def update(self, dt):
        # for icon in self.icons:
        #     icon.update(TILE_WIDTH, TILE_HEIGTH)
        # self.mouse = self.scene.mouse
        # self.mouse["pos"] = np.array(self.mouse["pos"]) * 0.5
        Icon.update_icons(dt)
        if self.mouse["press"][0] and self._prev_selected == Icon.selected:
            Icon.selected = []
        self._prev_selected = Icon.selected.copy()

    def render(self, surf):
        # for icon in self.icons:
        #     icon.render(surf)
        # self.surf.clear((0, 0, 0, 0))
        Icon.render_icons(surf)
        # pygame.transform.scale(self.surf.surf, surf.get_size(), surf)


class Table:
    def __init__(self, scene):
        self.scene = scene
        self.sprite = Sprite((self.scene.w, 20))
        self.center = np.array(self.sprite.get_rect().center)

        self.menu_btn = SpriteBtn(
            self.scene,
            (self.center[0] - (self.center[0] / 3), self.center[1]),
            surf=self.scene.assets.images["menu.png"],
        )

        self.menu_btn.callbacks["hover"].append(
            lambda x: self.menu_btn.set("bg", (0, 0, 0, 200))
        )
        self.menu_btn.callbacks["press"].append(lambda x: self.scene.menu.switch())

    def update(self):
        self.menu_btn.update(
            offset=np.array((0, self.scene.h)) - self.sprite.offset((0, 2))
        )

    def render(self, surf):
        self.sprite.clear("#0a0a2e")
        self.menu_btn.render(self.sprite)

        self.sprite.render(surf, (0, self.scene.h), (1, -1))
        # pygame.draw.circle(surf, "red", self.menu.o, 5)

        # pygame.draw.circle(
        #     surf, "red", np.array((0, self.scene.h) + self.sprite.offset((1, -1))), 4
        # )


class Menu:
    def __init__(self, scene: Scene):
        self.scene = scene
        self.sprite = Sprite((self.scene.w / 2.5, 300))
        self.pos = self.scene.center[0], self.scene.h

        self.offset = np.array((0, 0))
        self._slide = [-300, 0]
        self.is_open = False

        self.font = RandLetter(self.scene)
        # self.font.add_text(name="display_mode", text="Képernyő Mód")
        # self.font.add_text(name="volume_label", text="Hangerő")

        self.current_mode = self.scene.assets.configs["settings"]["display_mode"]
        self.t = 0
        self.seperators = []
        self.gap = 30

        self.sections = {
            "Hangerő": {
                "volume": Slider(
                    self.scene,
                    (10, 0),
                    start_value=self.scene.game.master_volume * 100,
                    scale=(100, 10),
                    secondary=(100, 100, 100),
                    anchors=(1, 0),
                )
                .add_callback(self._save_volume_change, "on_fix_change")
                .add_callback(self._on_volume_change, "on_change"),
                "volume_value": self.font.add_text(
                    name="volume",
                    text=int(self.scene.game.master_volume * 100),
                    pos=(120, 0),
                    anchors=(1, 0),
                ),
            },
            "Képernyő Mód": {
                "fullscreen": Btn(
                    self.scene,
                    pos=(10, 0),
                    anchors=(1, 0),
                    text=self.font.add_text(
                        name="fullscreen",
                        text="Fullscreen",
                        color="white" if self.current_mode == "fullscreen" else "gray",
                    ),
                )
                .add_callback(
                    lambda x: [
                        setattr(self.scene.game, "fullscreen", True),
                        setattr(self, "current_mode", "fullscreen"),
                        self.scene.assets.save_config(
                            "settings", {"display_mode": "fullscreen"}
                        ),
                    ]
                )
                .add_callback(self._on_display_mode_change),
                "windowed": Btn(
                    self.scene,
                    pos=(70, 0),
                    anchors=(1, 0),
                    text=self.font.add_text(
                        name="windowed",
                        text="Windowed",
                        color="white" if self.current_mode == "windowed" else "gray",
                    ),
                )
                .add_callback(
                    lambda x: [
                        setattr(self.scene.game, "fullscreen", False),
                        setattr(self, "current_mode", "windowed"),
                        self.scene.assets.save_config(
                            "settings", {"display_mode": "windowed"}
                        ),
                    ]
                )
                .add_callback(self._on_display_mode_change),
            },
            "Grafika": {
                "shardes": CheckBox(
                    self.scene,
                    pos=(80, 0),
                    anchors=(1, 0),
                    default=self.scene.assets.configs["settings"]["shaders"],
                ).add_callback(
                    lambda x: [
                        setattr(self.scene.game, "shaders", x.is_enabled),
                        self.scene.assets.save_config(
                            "settings", {"shaders": x.is_enabled}
                        ),
                    ]
                ),
                "shardes_label": self.font.add_text(
                    pos=(20, 0),
                    name="hitline",
                    text="Shaderek",
                    color="white",
                    anchors=(1, 0),
                ),
            },
            "fejlezstői Beálítások": {
                "hitline": CheckBox(
                    self.scene,
                    pos=(80, 0),
                    anchors=(1, 0),
                    default=self.scene.assets.configs["settings"]["hitline"],
                ).add_callback(
                    lambda x: [
                        self.scene.assets.save_config(
                            "settings", {"hitline": x.is_enabled}
                        ),
                        setattr(self.scene.game, "show_hitline", x.is_enabled),
                    ]
                ),
                "hitline_label": self.font.add_text(
                    pos=(20, 0),
                    name="hitline",
                    text="Ütem Vonal",
                    color="white",
                    anchors=(1, 0),
                ),
                "fps": CheckBox(
                    self.scene,
                    pos=(80, 10),
                    anchors=(1, 0),
                    default=self.scene.assets.configs["settings"]["fps"],
                ).add_callback(
                    lambda x: [
                        self.scene.assets.save_config(
                            "settings", {"fps": x.is_enabled}
                        ),
                        setattr(self.scene.game, "_show_fps", x.is_enabled),
                    ],
                ),
                "fps_label": self.font.add_text(
                    pos=(20, 10),
                    name="fps",
                    text="FPS",
                    color="white",
                    anchors=(1, 0),
                ),
            },
        }

        self._build_ui()

    def _update_ui(self):
        offset = self.pos - self.sprite.offset((1, 2))
        for components in self.sections.values():
            for comp in components.values():
                if type(comp) != Text:
                    comp.update(offset)

    def _build_ui(self):
        y_offset = 0
        for section, components in self.sections.items():
            y_offset += self.gap
            self.seperators.append([10, y_offset, -10])
            for comp in components.values():
                comp.pos[1] += y_offset + self.gap / 2
            components["title"] = self.font.add_text(
                name=section, text=section, pos=(10, y_offset), anchors=(1, -1)
            )
            y_offset += self.gap

    def _render_ui(self):
        for components in self.sections.values():
            for comp in components.values():
                comp.render(self.sprite)

    def update(self, dt):
        self.t = clamp(self.t + (self.is_open * 2 - 1) * 10 * dt)
        self.offset[1] = lerp(*self._slide, self.t)
        if self.scene.mouse["press"][0]:
            if not self.sprite.get_rect(
                self.pos - self.sprite.offset((1, 2))
            ).collidepoint(self.scene.mouse["pos"]):
                self.close()
        if self.is_open:
            self._update_ui()

    def render(self, surf):
        if self.offset[1] > self._slide[0]:
            self.sprite.clear("#05051a")
            self._render_ui()
            self.sprite.render(surf, self.pos - self.offset, (0, -1))
        # pygame.draw.rect(
        #     surf, "red", self.sprite.get_rect(self.pos - self.sprite.offset((1, 2)))
        # )

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def switch(self):
        self.is_open = not self.is_open

    def _save_volume_change(self, value):
        self.scene.assets.save_config("settings", {"volume": value})

    def _on_volume_change(self, value):
        self.font["volume"].text = str(int(value * 100))
        self.scene.game.master_volume = value
        pygame.mixer.music.set_volume(value)

    def _on_display_mode_change(self, x):
        self.sections["Képernyő Mód"]["fullscreen"].text.color = (
            "white" if self.current_mode == "fullscreen" else "gray"
        )
        self.sections["Képernyő Mód"]["windowed"].text.color = (
            "white" if self.current_mode == "windowed" else "gray"
        )

    def _handle_seperators(self, surf):
        for sep in self.seperators:
            x, y = sep[0], sep[1]
            w = sep[2] if sep[2] > 0 else self.sprite.w + sep[2]
            pygame.draw.line(surf, (255, 255, 255, 20), (x, y), (w, y))
