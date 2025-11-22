from data.scripts.desktop.icon import Icon


TILE_WIDTH = 32
TILE_HEIGTH = 32
TILE_GAP = 3


class DesktopGrid:
    def __init__(self, scene):
        self.scene = scene
        self.icons = []

        self.add_icon(**{"pos": (0, 0)})
        self.add_icon(**{"pos": (1, 0)})
        self.add_icon(**{"pos": (2, 0)})
        self.add_icon(**{"pos": (3, 0)})

        self.row_width = int(self.scene.game.w / TILE_WIDTH)
        self.row_heigth = int(self.scene.game.h / TILE_HEIGTH)

    def add_icon(self, **settings):
        self.icons.append(Icon(self, settings))

    def update(self):
        for icon in self.icons:
            icon.update(TILE_WIDTH, TILE_HEIGTH)

    def render(self, surf):
        for icon in self.icons:
            icon.render(surf)
