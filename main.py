import pygame
from window import Window
import numpy as np
from data.scripts.asset_magare import AssetManager
from data.scripts.desktop import Desktop
from data.scripts.music import Music
from data.scripts.input import Input

from data.scripts.scene import Scene
from window.shader import ShaderWindow


class Game(ShaderWindow):
    def setup(self):

        pygame.mixer.init()

        self.assets = AssetManager()
        # self.input = Input(self)
        self.center = np.array((self.w / 2, self.h / 2))

        Scene.init_scene_manager(self)

        Scene.add_scene(Music)
        Scene.add_scene(Desktop)


        # Scene.setup_scene()
        # return self.input.get_callbacks()
        return Scene.setup_scene()

    def update(self):
        self.display.fill("#1f102a")
        self.center = np.array((self.w / 2, self.h / 2))

        # surfs = Scene.update_scenes(self)
        surf = Scene.update_scene()
        self.display.blit(surf, (0, 0))


if __name__ == "__main__":
    Game(display_scale=0.5).run()
