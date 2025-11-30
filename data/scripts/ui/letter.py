import pygame
from data.scripts.utilities import Font, lerp_color, rplc_color
import random


class RandLetter(Font):
    def __init__(self, game, font_size=1):
        self.game = game
        super().__init__(
            font_img=self.game.assets.images["font.png"], font_size=font_size
        )
        self.is_fixed = 0

    def render(self, text, color="white", secoundary="#751756", alpha=255, spacing=1):
        x_offset = 0
        secoundary = secoundary or "#751756"
        text = str(text)

        full_width = sum(
            [
                (
                    (self.characters[char].get_width() + spacing)
                    if char != " " and char != "#"
                    else self.space_width + spacing
                )
                for char in str(text)
            ]
        )

        surf = pygame.Surface(
            (full_width, self.characters["A"].get_height()), pygame.SRCALPHA
        )

        for char in text:
            if char == "#":
                choice = random.choice(self.character_order)
                cr = rplc_color(self.characters[choice], "red", secoundary)
                surf.blit(cr, (x_offset, 0))
                x_offset += self.characters[choice].get_width() + spacing
            elif char != " ":
                surf.blit(self.characters[char], (x_offset, 0))
                x_offset += self.characters[char].get_width() + spacing
            else:
                x_offset += self.space_width + spacing
        surf = rplc_color(surf, "red", color)
        # surf.set_colorkey("black")
        surf.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        return surf
