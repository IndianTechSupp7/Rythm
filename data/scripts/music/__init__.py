from ast import Not
from csv import Error
import random
import time
from typing import Text
from networkx import is_path
import pygame
from pygame_shaders import Shader, DEFAULT_VERTEX_SHADER, Texture
from scipy import sparse
from data.scripts.asset_magare import AssetManager
from data.scripts.music.ui import UI
from data.scripts.scene import Scene
from data.scripts.utilities import bezier, clamp, lerp, lerp_color
from .node import Node
from .controller import Controller

NOTE_SPACING = 40
NOTE_SPEED = 200
Y_OFFSET = -30
BEAT_TOLERANCE = 0.8
BG_ANIM_TIME = 2
AUTO_SAVE = 5


"""
Bent a neved: "tom": 0.6, "kick": 0.2, "cym": 0.5, "snr": 0.4

Anyám mondta 
            self.min_strgs = {"tom": 0.1, "kick": 0.2, "cym": 0.1, "snr": 0.4}
            self.max_strgs = {"tom": 0.5, "kick": 1.0, "cym": 0.5, "snr": 1.0}

Apologize 
            self.min_strgs = {"tom": 0.4, "kick": 0.2, "cym": 0.4, "snr": 0.4}
            self.max_strgs = {"tom": 0.6, "kick": 1.0, "cym": 0.8, "snr": 0.7}

The Night Begins to Shine   
     
            self.min_strgs = {"tom": 0.4, "kick": 0.2, "cym": 0.4, "snr": 0.4}
            self.max_strgs = {"tom": 0.6, "kick": 1.0, "cym": 0.8, "snr": 0.7}    

Rakpart
            self.min_strgs = {"tom": 0.3, "kick": 0.2, "cym": 0.4, "snr": 0.4}
            self.max_strgs = {"tom": 0.4, "kick": 1.0, "cym": 0.8, "snr": 0.7}

"""


class Music(Scene):
    def __init__(self):
        super().__init__(display_scale=0.5)
        self.input.add_callback("menu", self.pause, "press")
        self.input.add_callback(
            "kick",
            lambda: self.change_theme(None, [random.randint(0, 255) for i in range(3)]),
            "press",
        )

    def setup(self):
        self.is_paused = False
        self.assets.reset_beatmaps()
        self.game.set_cursor(False)

        # self.assets: AssetManager = self.game.assets
        # self.center = self.center

        self.current_song_name = self.game.current_song_name

        self.current_beatmap = self.assets.beatmaps[self.current_song_name + ".json"]
        self.current_time = 0
        self.color_timer = 0
        self.start_time = time.time()
        # self.full_time = max(
        #     self.current_beatmap["tracks"]["Tom"][-1]["time"],
        #     self.current_beatmap["tracks"]["Cymbal"][-1]["time"],
        #     self.current_beatmap["tracks"]["Kick"][-1]["time"],
        # )

        self.full_time = 0
        self.min_strgs = (
            self.current_beatmap.get("min") or self.assets.configs["level"]["min"]
        )
        self.max_strgs = (
            self.current_beatmap.get("max") or self.assets.configs["level"]["max"]
        )

        self.hit_line_y = self.center[1] + 130
        self.finished = False

        row = [((i * 32) + NOTE_SPACING) for i in range(4)]
        row = [self.center[0] - (i - ((4 * 32 + NOTE_SPACING) / 2)) for i in row][::-1]

        self.tom = Controller(
            self,
            self.current_beatmap["tracks"]["Tom"],
            # (self.center[0] - NOTE_SPACING, Y_OFFSET),
            (row[0], Y_OFFSET),
            NOTE_SPEED,
            hit_line_y=self.hit_line_y,
            min_strength=self.min_strgs["tom"],
            max_strength=self.max_strgs["tom"],
            note="tom",
        )
        self.kick = Controller(
            self,
            self.current_beatmap["tracks"]["Kick"],
            # (self.center[0], Y_OFFSET),
            (row[1], Y_OFFSET),
            NOTE_SPEED,
            hit_line_y=self.hit_line_y,
            min_strength=self.min_strgs["kick"],
            max_strength=self.max_strgs["kick"],
            note="kick",
        )
        self.snare = Controller(
            self,
            self.current_beatmap["tracks"]["Snare"],
            # (self.center[0] + NOTE_SPACING, Y_OFFSET),
            (row[2], Y_OFFSET),
            NOTE_SPEED,
            hit_line_y=self.hit_line_y,
            min_strength=self.min_strgs["snr"],
            max_strength=self.max_strgs["snr"],
            note="snr",
        )
        self.cym = Controller(
            self,
            self.current_beatmap["tracks"]["Cymbal"],
            # (self.center[0] + NOTE_SPACING * 2, Y_OFFSET),
            (row[3], Y_OFFSET),
            NOTE_SPEED,
            hit_line_y=self.hit_line_y,
            min_strength=self.min_strgs["cym"],
            max_strength=self.max_strgs["cym"],
            note="cym",
        )

        self.all_beats = sum(
            (
                len(self.kick.nodes),
                len(self.snare.nodes),
                len(self.tom.nodes),
                len(self.cym.nodes),
            ),
        )
        self.on_finish = []
        self.on_pause = []
        self.on_unpause = []
        self.in_tutorial = True

        self.ui = UI(self)
        self.background = pygame.Surface(self.surf.get_size())
        self.setup_bg()
        self.bg_shader = Shader(
            DEFAULT_VERTEX_SHADER, self.assets.shaders["music_bg.glsl"], self.surf
        )
        self.noise_texture = Texture(
            self.assets.images["noise.png"], self.bg_shader.ctx
        )
        self.bg_texture = Texture(self.background, self.bg_shader.ctx)
        self.secondary = "#25246b"
        self._prev_color = (0, 0, 0, 0)
        self._current_color = (0, 0, 0, 0)

        # self.bright = Shader(DEFAULT_VERTEX_SHADER, "bright.glsl", self.surf)
        # self.blur = Shader(DEFAULT_VERTEX_SHADER, "blur.glsl", self.surf)
        # self.combine = Shader(DEFAULT_VERTEX_SHADER, "combine.glsl", self.surf)

        # self.bright_tex = Texture(pygame.Surface(self.size), self.bright.ctx)
        # self.blur_tex = Texture(pygame.Surface(self.size), self.blur.ctx)
        # self.final_tex = Texture(pygame.Surface(self.size), self.combine.ctx)

        pygame.mixer.music.load(self.assets.sfx[self.current_beatmap["song"]])

        # self.game.input.add_callback("menu", self.active, "press")

        # self.input.add_callback("continue", lambda: pygame.mixer.music.stop())
        self.pause_time = 0

    def reset(self):
        pygame.mixer.music.play()
        self.start_time = time.time()

    def pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_time = time.time()
            pygame.mixer.music.pause()
            for func in self.on_pause:
                func()
        else:
            self.start_time += time.time() - self.pause_time
            pygame.mixer.music.unpause()
            for func in self.on_unpause:
                func()

        # Scene.change_scene("Desktop")

    def change_theme(self, primary, secoundary):
        self.color_timer = time.time() - self.start_time
        self._prev_color = self._current_color
        self.secondary = pygame.Color(secoundary)

    def on_tutorial_complete(self):
        pygame.mixer.music.play()
        self.start_time = time.time()
        self.color_timer = time.time() - self.start_time
        self.current_time = time.time() - self.start_time

        # self.current_time = time.time() - self.start_time

    def update(self, dt, **kwargs):
        self.surf.fill((0, 0, 0, 0))
        if not self.is_paused:
            if not self.in_tutorial:
                if round(time.time(), 2) % AUTO_SAVE == 0:
                    data = self.assets.configs["level"]
                    data["songs"][self.current_song_name][2] = self.full_time
                    self.assets.save_config("level", data)
                # self.surf.fill("#1f102a")
                # self.surf.blit(self.background, (0, 0))

                if self.all_beats:
                    self.full_time = len(Node.triggered) / (
                        self.all_beats * BEAT_TOLERANCE
                    )
                else:
                    assert Error("nem jo a zene")
                if not pygame.mixer.music.get_busy():
                    if not self.finished:
                        for func in self.on_finish:
                            func()
                        self.finished = True
                        self.is_paused = True

            # self.center = self.game.center
            if (
                not any(
                    [i.in_tutorial for i in (self.tom, self.kick, self.cym, self.snare)]
                )
                and self.in_tutorial
            ):
                self.on_tutorial_complete()
                self.in_tutorial = False

            self.current_time = time.time() - self.start_time

            self.tom.update(dt, self.current_time)
            self.kick.update(dt, self.current_time)
            self.cym.update(dt, self.current_time)
            self.snare.update(dt, self.current_time)

            self._current_color = lerp_color(
                self.secondary,
                # "#751756",
                self._prev_color,
                min(self.current_time - self.color_timer, BG_ANIM_TIME) / BG_ANIM_TIME,
            )
            # print(self._current_color.normalize())

            self.bg_shader.send("vg_color", list(self._current_color.normalize())[:3])
            # self.bg_shader.send("vg_color", (1., 0., 0.))
            self.ui.secondary = self._current_color

            self.noise_texture.use(1)
            self.bg_texture.use(2)
            self.bg_shader.send("noiseTexture", 1)
            self.bg_shader.send("bgTexture", 2)
            self.bg_shader.send("time", self.current_time)
        else:
            if self.input.get_event("continue", "press"):
                # if self.finished:
                #     Scene.change_scene("Desktop")
                # else:
                #     self.pause()
                Scene.change_scene("Desktop")
            # if self.input.get_event("menu", "press"):
            #     print(1)
            #     Scene.change_scene("Desktop")
        self.tom.render(self.surf)
        self.kick.render(self.surf)
        self.cym.render(self.surf)
        self.snare.render(self.surf)

        self.ui.update()
        self.ui.render(self.surf)
        return self.bg_shader.render()

    def setup_bg(self):
        ROW = 10
        ROW_WIDTH = self.background.width / ROW
        LINE_WIDTH = 1

        self.background.fill("#1f102a")
        for i in range(ROW):
            pygame.draw.line(
                self.background,
                "#390947",
                (i * ROW_WIDTH, 0),
                (i * ROW_WIDTH, self.background.height),
                LINE_WIDTH,
            )
