import pygame
from data.scripts.utilities import Font, rplc_color
import random


class RandLetter(Font):
    def __init__(self, game, font_size=1):
        self.game = game
        super().__init__(
            font_img=self.game.assets.images["font.png"], font_size=font_size
        )
        self.is_fixed = 0
        self.spacing = 3

    def render(self, text, color="white"):
        x_offset = 0

        full_width = sum(
            [
                (
                    (self.characters[char].get_width() + self.spacing)
                    if char != " " and char != "#"
                    else self.space_width + self.spacing
                )
                for char in text
            ]
        )

        surf = pygame.Surface(
            (full_width, self.characters["A"].get_height()), pygame.SRCALPHA
        )

        for char in text:
            if char == "#":
                choice = random.choice(self.character_order)
                cr = rplc_color(self.characters[choice], "red", "#751756")
                surf.blit(cr, (x_offset, 0))
                x_offset += self.characters[choice].get_width() + self.spacing
            elif char != " ":
                surf.blit(self.characters[char], (x_offset, 0))
                x_offset += self.characters[char].get_width() + self.spacing
            else:
                x_offset += self.space_width + self.spacing
        surf = rplc_color(surf, "red", color)
        # surf.set_colorkey("black")
        return surf
