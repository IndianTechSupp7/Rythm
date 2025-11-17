import json
from sys import flags
import numpy as np
import pygame


def bezier(a: float, b: float, c: float, d: float, t: float):
    # return a * (1 - t)**3 + 3*b * (1 - t)**2*t + 3*c * (1-t)*t**2 + d*t**3
    x = (1 - t)**3 * 0 + t*a*(3*(1-t)**2) + c*(3*(1-t)*t**2) + 1*t**3
    y = (1 - t)**3 * 0 + t*b*(3*(1-t)**2) + d*(3*(1-t)*t**2) + 1*t**3
    return x, y

def move_towards(x, target, speed, dt):
    diff = target - x
    if abs(diff) <= speed * dt:
        return target
    return x + np.copysign(speed * dt, diff)


def rplc_color(surf: pygame.Surface, prev_c, new_c):
    prev_c = pygame.Color(prev_c)
    new_c = pygame.Color(new_c)
    surf = surf.copy().convert_alpha()
    px = pygame.PixelArray(surf)

    # Convert colors to the surface format
    old = surf.map_rgb(prev_c)
    new = surf.map_rgb(new_c)

    px.replace(old, new)
    del px

    return surf

def lerp_color(a, b, t):
    a = pygame.Color(a)
    return pygame.Color(b).lerp(a, t)
    # return lerp(a.r, b.r, t), lerp(a.g, b.g, t), lerp(a.b, b.b, t)

def lerp(a, b, t):
    return a + (b - a) * t


def get_json(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def clip(surf, x, y, w, h):
    rect = pygame.Rect(x, y, w, h)
    sub = pygame.Surface((w, h), pygame.SRCALPHA)
    sub.blit(surf, (0, 0), rect)
    return sub


class Font:
    def __init__(self, font_img, font_size=1):
        self.spacing = 1
        self.character_order = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
            ".",
            "-",
            ",",
            ":",
            "+",
            "'",
            "!",
            "?",
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "(",
            ")",
            "/",
            "_",
            "=",
            "\\",
            "[",
            "]",
            "*",
            '"',
            "<",
            ">",
            ";",
            "á",
            "é",
            "í",
            "ó",
            "ö",
            "ő",
            "ú",
            "ü",
            "ű",
            "Á",
            "É",
            "Í",
            "Ó",
            "Ö",
            "Ő",
            "Ú",
            "Ü",
            "Ű",
        ]
        # font_img = pygame.image.load(path).convert()
        current_char_width = 0
        self.characters = {}
        character_count = 0
        for x in range(font_img.get_width()):
            c = font_img.get_at((x, 0))
            if c[0] == 127:
                char_img = clip(
                    font_img,
                    x - current_char_width,
                    0,
                    current_char_width,
                    font_img.get_height(),
                )
                self.characters[self.character_order[character_count]] = (
                    pygame.transform.scale(
                        char_img.copy(),
                        np.array(char_img.get_size()) * font_size,
                    )
                )
                character_count += 1
                current_char_width = 0
            else:
                current_char_width += 1
        self.space_width = self.characters["A"].get_width()

    def render(self, text, color="white"):
        x_offset = 0

        full_width = sum(
            [
                (
                    (self.characters[char].get_width() + self.spacing)
                    if char != " "
                    else self.space_width + self.spacing
                )
                for char in text
            ]
        )

        surf = pygame.Surface(
            (full_width, self.characters["A"].get_height()), pygame.SRCALPHA
        )

        for char in text:
            if char != " ":
                surf.blit(self.characters[char], (x_offset, 0))
                x_offset += self.characters[char].get_width() + self.spacing
            else:
                x_offset += self.space_width + self.spacing
        surf = rplc_color(surf, "red", color)
        # surf.set_colorkey("black")
        return surf
