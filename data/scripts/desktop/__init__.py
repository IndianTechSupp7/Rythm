import pygame
from random import randint
import numpy as np
from data.scripts.desktop.desktop import DesktopGrid, Table
from data.scripts.scene import Scene
from data.scripts.sprite import Sprite
from pygame_shaders import (
    Shader,
    Texture,
    DEFAULT_VERTEX_SHADER,
    DEFAULT_FRAGMENT_SHADER,
)

STAR_AMOUNT = 50


class Desktop(Scene):
    def __init__(self):
        super().__init__(display_scale=0.5)
        self.desktop = DesktopGrid(self)

    def setup(self, **kwargs):
        self.game.set_cursor(True)
        self.desktop.update_song_progress()
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
        # self.noise = Texture(self.assets.images["noise.png"], self.background.ctx)

        # self.desktop =
        self.table = Table(self)
        self.time = 0

        self.background.send("uTexSize", self.surf.get_size())
        self.background.send("bg", pygame.Color("#1f102a").normalize()[:3])
        self.background.send("color3", pygame.Color("#390947").normalize()[:3])
        self.background.send("color2", pygame.Color("#611851").normalize()[:3])
        self.background.send("color1", pygame.Color("#751756").normalize()[:3])


    def update(self, **kwargs):
        self.surf.fill((0, 0, 0, 0))
        self.time += 1 * self.game.dt
        self.render_stars(self.time * 0.3)

        # TODO:  ???? #
        # pygame.draw.circle(self.stars_surf.surf, "#ffc3f2", (300, 50), radius=14)
        # self.surf.blit(self.assets.images["moon.png"], (300, 50))
        # self.moon.scale_nrom(0.80).render(self.stars_surf.surf, (300, 50))

        # TODO: meh ####
        # self.moon.render(self.surf, (300, 50))

        self.desktop.update(self.game.dt)
        self.desktop.render(self.surf)
        self.table.render(self.surf)

        self.stars_tex.update(self.stars_surf.surf)
        self.stars_tex.use(2)
        self.background.send("stars", 2)
        self.background.send("time", self.time)
        return self.background.render()

    def render_stars(self, t):
        for star in self.stars:
            color = max(min(np.sin(t + star[2]) * 255, 255), 100)
            pygame.draw.rect(
                self.stars_surf.surf, [color] * 4, (*star[:2], star[3], star[3])
            )
