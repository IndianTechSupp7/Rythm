import pygame
from window import Window
import numpy as np
from data.scripts.asset_magare import AssetManager
from data.scripts.music import Music
from data.scripts.input import Input

from data.scripts.scene import Scene


class Game(Window):
    def setup(self):

        pygame.mixer.init()

        self.assets = AssetManager()
        self.input = Input(self)
        self.center = np.array((self.w / 2, self.h / 2))

        Scene.add_scene(Music)

        Scene.setup_scenes(self)
        return self.input.get_callbacks()

    def update(self):
        self.display.fill("#1f102a")
        self.center = np.array((self.w / 2, self.h / 2))

        surfs = Scene.update_scenes(self)
        for surf in surfs:
            self.display.blit(surf, (0, 0))


if __name__ == "__main__":
    Game(display_scale=0.5).run()
