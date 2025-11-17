import os
import pygame
from data.scripts.utilities import get_json


def add_item(d, path, item):
    keys = [k for k in path.strip("\\").split("\\") if k]  # split path
    current = d
    for key in keys:
        if key == keys[-1]:
            current[key] = item
            continue
        if key not in current:
            current[key] = {}
        current = current[key]


class AssetManager:
    BASE_ASSETS_FOLDER = "data\\assets"

    def __init__(self):
        self.sfx = {i.split("\\")[-1]: i for i in self.search((".mp3"), "/sfx")}
        self.binds = get_json(self.BASE_ASSETS_FOLDER + "\\binds.json")
        self.images = {}
        for i in self.search((".png"), "\\images"):
            add_item(
                self.images,
                i.split(self.BASE_ASSETS_FOLDER + "\\images")[-1],
                pygame.image.load(i).convert_alpha(),
            )
        self.beatmaps = {
            i.split("\\")[-1]: get_json(i) for i in self.search(("json"), "\\beatmaps")
        }
        self.shaders = {
            i.split("\\")[-1]: i for i in self.search((".glsl"), "/shaders")
        }

    def search(self, exts: list | tuple, base=""):
        path = self.BASE_ASSETS_FOLDER + base
        data = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.split(".")[-1] in exts:
                    data.append(os.path.join(root, file))
        return data
