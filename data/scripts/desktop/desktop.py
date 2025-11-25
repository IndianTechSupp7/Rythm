from window import Window
from data.scripts.desktop.icon import Icon
from data.scripts.scene import Scene
from data.scripts.sprite import Sprite
from data.scripts.utilities import get_json, write_json


TILE_WIDTH = 32
TILE_HEIGTH = 42
TILE_GAP = 3


class DesktopGrid:
    def __init__(self, scene: Scene):
        self.scene = scene
        Icon.scene = self.scene

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

        self.row_width = int(self.scene.w / TILE_WIDTH)
        self.row_heigth = int(self.scene.h / TILE_HEIGTH)

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
        Icon.update_icons(TILE_WIDTH, TILE_HEIGTH, dt)

    def render(self, surf):
        # for icon in self.icons:
        #     icon.render(surf)
        Icon.render_icons(surf)


class Table:
    def __init__(self, scene):
        self.scene = scene
        self.sprite = Sprite((0, 20))

    def render(self, surf):
        self.sprite.render(surf, (0, Window.h), (1, -1))
