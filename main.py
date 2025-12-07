#! .venv\Scripts\python.exe
import pygame
import numpy as np
from data.scripts.asset_magare import AssetManager
from data.scripts.desktop import Desktop
from data.scripts.music import Music

from data.scripts.scene import Scene
from window.shader import ShaderWindow

from data.scripts.sprite import Sprite
from data.scripts.startup import StartUp
from data.scripts.ui.letter import RandLetter


class Game(ShaderWindow):
    def __init__(self, size=..., display_scale=1, resizeable=True):
        super().__init__(size, display_scale, resizeable)
        self.assets = AssetManager()
        self.fullscreen = (
            self.assets.configs["settings"]["display_mode"] == "fullscreen"
        )

    def setup(self):
        pygame.mixer.init()

        self.current_song_name = ""
        self.master_volume = self.assets.configs["settings"]["volume"]

        # self.input = Input(self)
        self.center = np.array((self.w / 2, self.h / 2))

        Scene.init_scene_manager(self)

        Scene.add_scene(StartUp)
        Scene.add_scene(Desktop)
        Scene.add_scene(Music)

        pygame.mouse.set_visible(False)
        self.cursor = Sprite(self.assets.images["cursor.png"])
        self._show_cursor = True

        self._show_fps = self.assets.configs["settings"]["fps"]
        self.font = RandLetter(self, 3)
        self.font.add_text(
            "fps_main",
            text=round(self.clock.get_fps()),
            pos=(10, 10),
            anchors=(1, 1),
        )

        # Scene.change_scene("Desktop")

        # Scene.setup_scene()
        # return self.input.get_callbacks()
        return Scene.setup_scene()

    def set_cursor(self, value=True):
        self._show_cursor = value

    def update(self):
        pygame.display.set_caption(str(self.clock.get_fps()))
        self.display.fill("#1f102a")
        self.center = np.array((self.w / 2, self.h / 2))

        # surfs = Scene.update_scenes(self)
        surf = Scene.update_scene()
        self.display.blit(pygame.transform.scale(surf, self.display.get_size()), (0, 0))
        # self.display.blit(surf, (0, 0))
        if self._show_fps:
            self.font["fps_main"].text = str(round(self.clock.get_fps()))
            self.font["fps_main"].render(self.display)
        if self._show_cursor:
            self.cursor.scale_nrom(2).render(
                self.display, pygame.mouse.get_pos(), (1, 1)
            )
        # pygame.draw.circle(self.display, "red", pygame.mouse.get_pos(), 10)


if __name__ == "__main__":
    try:
        pygame.init()
        info = pygame.display.Info()
        width = int(info.current_w / 1.3)
        height = int(info.current_h / 1.3)
        Game(display_scale=1.0, resizeable=False, size=(1278, 720)).run()
    except KeyboardInterrupt:
        pass
    except pygame.error:
        pass
