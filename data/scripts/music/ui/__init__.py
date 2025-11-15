import pygame
from data.scripts.utilities import rplc_color
from data.sprite import Sprite
from .letter import RandLetter


class UI:
    def __init__(self, music):
        self.music = music
        self.game = self.music.game
        self.center = self.game.center
        self.surf = pygame.Surface(self.music.surf.get_size(), pygame.SRCALPHA)
        self.current_state = None

        self.rndl = RandLetter(self.game, 2)
        self.counter = 0
        self.base_text = self.music.current_song_name + ".mp3"
        self.index = int(len(self.base_text) * self.music.full_time)
        self.text = [
            ch if i <= self.index or ch == " " else "#"
            for i, ch in enumerate(self.base_text)
        ]
        self.text_sprite = Sprite(self.rndl.render(self.text, "white"))
        # self.rnd_sprite = Sprite(self.rndl.render(self.text[self.index :], "#751756"))

    def menu(self):
        pass

    def update(self):
        self.counter += 1

        if self.counter % 5 == 0:
            self.text_sprite.surf = self.rndl.render(self.text, "white")
            # self.rnd_sprite.surf = self.rndl.render(self.text[self.index :], "#751756")
        self.index = int(len(self.base_text) * self.music.full_time)
        self.text = [
            ch if i <= self.index or ch == " " else "#"
            for i, ch in enumerate(self.base_text)
        ]

    def render(self, surf):
        self.text_sprite.render(surf, (self.center[0], 15), (0, 0))
        # self.rnd_sprite.render(surf, (self.center[0], 15), (0, 0))
