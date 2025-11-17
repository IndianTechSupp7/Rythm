import pygame
from data.scripts.scene import Scene


class Desktop(Scene):
    def setup(self, **kwargs):
        self.input.add_callback("menu", lambda: print("Hello WOrld"))

        self.btn = pygame.Rect((100, 100, 100, 100))

    def update(self, **kwargs):
        self.surf.fill("black")

        if self.btn.collidepoint(self.mouse["pos"]) and self.mouse["press"][0]:
            Scene.change_scene("Music")
        pygame.draw.rect(self.surf, "blue", self.btn)

        return self.surf
