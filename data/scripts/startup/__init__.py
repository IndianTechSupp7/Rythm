from re import S
import numpy as np
import pygame
from data.scripts.scene import Scene
from datetime import datetime

from data.scripts.sprite import Sprite
from data.scripts.ui.letter import RandLetter
import time
from pygame_shaders import Shader, DEFAULT_VERTEX_SHADER, Texture
from random import randint

STAR_AMOUNT = 100


class StartUp(Scene):
    def setup(self, **kwargs):
        self.big = RandLetter(self, 7)
        self.small = RandLetter(self, 3)
        self.time = Sprite(
            self.big.render(datetime.now().strftime("%H:%M"), "white", spacing=5)
        )

        # self.login = Sprite(self.small.render("Belenetkezés", "white"))
        self._login_spacing = 1
        self.login = Btn(
            scene=self,
            pos=self.center,
            surf=self.small.render(
                "Belenetkezés", "white", spacing=self._login_spacing
            ),
        )

        self.background = Shader(
            DEFAULT_VERTEX_SHADER, self.assets.shaders["desktop_bg.glsl"], self.surf
        )

        self.stars_surf = Sprite(self.size)
        self.stars = [
            (
                randint(0, self.stars_surf.w),
                randint(0, self.stars_surf.h),
                randint(200, 255),
                randint(1, 1),
            )
            for _ in range(STAR_AMOUNT)
        ]

        self.stars_tex = Texture(self.stars_surf.surf, self.background.ctx)

        self.background.send("uTexSize", self.surf.get_size())
        self.background.send("bg", pygame.Color("#1f102a").normalize()[:3])
        self.background.send("color3", pygame.Color("#390947").normalize()[:3])
        self.background.send("color2", pygame.Color("#611851").normalize()[:3])
        self.background.send("color1", pygame.Color("#751756").normalize()[:3])

        self.input.add_callback("enter", lambda: Scene.change_scene("Desktop"))
        self.start_time = time.time()
        self.current_time = 0

    def render_stars(self, t):
        for star in self.stars:
            color = max(min(np.sin(t + star[2]) * 255, 255), 100)
            pygame.draw.rect(
                self.stars_surf.surf, [color] * 4, (*star[:2], star[3], star[3])
            )

    def update(self, **kwargs):
        self.surf.fill((0, 0, 0, 0))
        self.current_time = time.time() - self.start_time
        self.render_stars(self.current_time * 0.3)

        if "hover" not in self.login.state:
            self._login_spacing = max(1, self._login_spacing - 20 * self.game.dt)
        else:
            self._login_spacing = min(3, self._login_spacing + 20 * self.game.dt)
        if "press" in self.login.state:
            self._login_spacing = 1.5
            Scene.change_scene("Desktop")

        self.login.surf = self.small.render(
            "Belenetkezés", "white", spacing=self._login_spacing
        )
        h = datetime.now().hour
        m = datetime.now().minute
        self.time.surf = self.big.render(
            # datetime.now().strftime(f"%H{":" if int(time.time())%2==0 else " "}%M"),
            f"{h} {m}",
            "white",
            spacing=4,
        )
        Sprite(
            self.big.render(":" if int(time.time()) % 2 == 0 else " ", "white")
        ).render(self.surf, self.center / (1, 2), (0, -0.20))

        norm = (self._login_spacing - 1) / 2
        self.login.update()
        self.login.scale_nrom(norm * 0.3 + 1).render(self.surf)
        self.time.render(self.surf, self.center / (1, 2), (0, 0))

        self.stars_tex.update(self.stars_surf.surf)
        self.stars_tex.use(2)
        self.background.send("stars", 2)
        self.background.send("time", self.current_time)
        return self.background.render()


class Btn(Sprite):
    def __init__(self, scene, pos, surf=(20, 20), on_press=lambda: ...):
        super().__init__(surf)
        self.scene = scene
        self.pos = pos
        self.on_press = on_press
        self.callbacks = {
            "hover": [],
            "press": [],
            "release": [],
        }
        self.state = ()

    def render(self, surf, flags=0, opacity=1):
        return super().render(surf, self.pos, (0, 0), flags, opacity)

    def update(self):
        self.state = set()
        if self.get_rect(self.pos - self.offset((1, 1))).collidepoint(
            self.scene.mouse["pos"]
        ):
            self.state.add("hover")
            for cb in self.callbacks["hover"]:
                cb(self)
            if self.scene.mouse["press"][0]:
                self.state.add("press")
                for cb in self.callbacks["press"]:
                    cb(self)
            if self.scene.mouse["release"][0]:
                self.state.add("release")
                for cb in self.callbacks["release"]:
                    cb(self)
