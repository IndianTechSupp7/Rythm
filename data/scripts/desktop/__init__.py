import pygame
from data.scripts.desktop.desktop import DesktopGrid
from data.scripts.scene import Scene


class Desktop(Scene):
    def setup(self, **kwargs):
        self.input.add_callback("menu", lambda: print("Hello WOrld"))

        self.desktop = DesktopGrid(self)

        self.btn = pygame.Rect((100, 100, 100, 100))

    def update(self, **kwargs):
        self.surf.fill("brown")

        self.desktop.update()
        self.desktop.render(self.surf)

        return self.surf
