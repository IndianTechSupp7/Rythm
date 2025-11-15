from ast import Not
import time
import pygame
from data.scripts.asset_magare import AssetManager
from data.scripts.music.ui import UI
from data.scripts.scene import Scene
from .node import Node
from .controller import Controller

NOTE_SPACING = 40
NOTE_SPEED = 200
Y_OFFSET = -30
BEAT_TOLERANCE = 0.8

"""
Bent a neved: "tom": 0.6, "kick": 0.2, "cym": 0.5, "snr": 0.4

Anyám mondta 
            self.min_strgs = {"tom": 0.1, "kick": 0.2, "cym": 0.1, "snr": 0.4}
            self.max_strgs = {"tom": 0.5, "kick": 1.0, "cym": 0.5, "snr": 1.0}

            

"""


class Music(Scene):
    def setup(self, game):
        self.is_paused = False

        self.game = game
        self.assets: AssetManager = game.assets
        self.center = self.game.center

        self.surf = self.game.display.copy()

        self.current_song_name = "Anyám mondta"

        self.current_beatmap = self.assets.beatmaps[self.current_song_name + ".json"]
        self.start_time = time.time()
        self.current_time = 0
        # self.full_time = max(
        #     self.current_beatmap["tracks"]["Tom"][-1]["time"],
        #     self.current_beatmap["tracks"]["Cymbal"][-1]["time"],
        #     self.current_beatmap["tracks"]["Kick"][-1]["time"],
        # )

        self.full_time = 0
        self.min_strgs = {"tom": 0.1, "kick": 0.2, "cym": 0.1, "snr": 0.4}
        self.max_strgs = {"tom": 0.5, "kick": 1.0, "cym": 0.5, "snr": 1.0}

        self.hit_line_y = self.center[1] + 130
        self.finished = False

        row = [((i * 32) + NOTE_SPACING) for i in range(4)]
        row = [self.center[0] - (i - ((4 * 32 + NOTE_SPACING) / 2)) for i in row][::-1]
        print(row)
        self.tom = Controller(
            self.game,
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
            self.game,
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
            self.game,
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
            self.game,
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
        self.ui = UI(self)

        pygame.mixer.music.load(self.assets.sfx[self.current_beatmap["song"]])
        pygame.mixer.music.play()

        self.game.input.add_callback("menu", self.pause, "press")
        # self.game.input.add_callback("menu", self.active, "press")

    def pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

    def update(self, dt, **kwargs):
        if not self.is_paused:
            self.surf.fill((0, 0, 0, 0))

            self.full_time = len(Node.triggered) / (self.all_beats * BEAT_TOLERANCE)

            if not pygame.mixer.music.get_busy():
                self.finished = True
                # self.ui.

            self.current_time = time.time() - self.start_time

            self.center = self.game.center

            self.tom.update(dt, self.current_time)
            self.kick.update(dt, self.current_time)
            self.cym.update(dt, self.current_time)
            self.snare.update(dt, self.current_time)

            self.tom.render(self.surf)
            self.kick.render(self.surf)
            self.cym.render(self.surf)
            self.snare.render(self.surf)

            self.ui.update()
            self.ui.render(self.surf)

        return self.surf
