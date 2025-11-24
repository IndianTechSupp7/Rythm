from window import ShaderWindow
from data.scripts.desktop.icon import Icon
from data.scripts.scene import Scene
from data.scripts.sprite import Sprite
from data.scripts.utilities import get_json, write_json


TILE_WIDTH = 32
TILE_HEIGTH = 32
TILE_GAP = 3


class DesktopGrid:
    def __init__(self, scene: Scene):
        self.scene = scene
        self.icons = []

        self.add_icon(
            **{
                "pos": (1, 0),
                "img": Sprite(self.scene.assets.images["ext"]["mp3.png"]),
                "title": "Porszem",
                "on_press": lambda: self.open_music("Porszem"),
            }
        )
        self.add_icon(
            **{
                "pos": (6, 5),
                "img": Sprite(self.scene.assets.images["ext"]["mp3.png"]),
                "title": "Blame",
                "on_press": lambda: self.open_music("Blame"),
            }
        )
        self.add_icon(
            **{
                "pos": (2, 6),
                "img": Sprite(self.scene.assets.images["ext"]["mp3.png"]),
                "title": "Rakpart",
                "on_press": lambda: self.open_music("Rakpart"),
            }
        )
        self.add_icon(
            **{
                "pos": (7, 2),
                "img": Sprite(self.scene.assets.images["ext"]["mp3.png"]),
                "title": "Só Fé",
                "on_press": lambda: self.open_music("Só Fé"),
            }
        )
        self.add_icon(
            **{
                "pos": (10, 1),
                "img": Sprite(self.scene.assets.images["ext"]["mp3.png"]),
                "title": "greedy",
                "on_press": lambda: self.open_music("greedy"),
            }
        )
        self.add_icon(
            **{
                "pos": (11, 9),
                "img": Sprite(self.scene.assets.images["ext"]["mp3.png"]),
                "title": "Belehalok",
                "on_press": lambda: self.open_music("Belehalok"),
            }
        )
        self.add_icon(
            **{
                "pos": (3, 8),
                "img": Sprite(self.scene.assets.images["ext"]["mp3.png"]),
                "title": "Angeleyes.mp3",
                "on_press": lambda: self.open_music("Angeleyes"),
            }
        )

        self.row_width = int(self.scene.game.w / TILE_WIDTH)
        self.row_heigth = int(self.scene.game.h / TILE_HEIGTH)
        print(self.row_width, self.row_heigth)

    def open_music(self, music):
        data = self.scene.assets.configs["level"]
        data["song"] = music
        write_json(self.scene.assets.BASE_ASSETS_FOLDER + "/config/level.json", data)
        Scene.change_scene("Music")

    def add_icon(self, **settings):
        self.icons.append(Icon(self.scene, settings))

    def update(self):
        for icon in self.icons:
            icon.update(TILE_WIDTH, TILE_HEIGTH)

    def render(self, surf):
        for icon in self.icons:
            icon.render(surf)


class Table:
    def __init__(self, scene):
        self.scene = scene
        self.sprite = Sprite((0, 20))

    def render(self, surf):
        self.sprite.render(surf, (0, ShaderWindow.h), (1, -1))
