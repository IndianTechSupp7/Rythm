import os
import pygame
from data.scripts.utilities import get_json, write_json


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


def update_dict(d, path, dct):
    keys = [k for k in path.strip("\\").split("\\") if k]  # split path
    current = d
    for key in keys:
        if key == keys[-1]:
            current[key].update(dct)
            continue
        if key not in current:
            current[key] = {}
        current = current[key]


class AssetManager:
    BASE_ASSETS_FOLDER = "data\\assets"

    def __init__(self):
        self.sfx = {i.split("\\")[-1]: i for i in self.search((".mp3"), "/sfx")}
        self.configs = {
            i.split("\\")[-1].split(".")[0]: get_json(i)
            for i in self.search((".json"), "/config")
        }
        # self.binds = get_json(self.BASE_ASSETS_FOLDER + "\\binds.json")
        # self.binds = get_json(self.BASE_ASSETS_FOLDER + "\\level.json")
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

    def reset_beatmaps(self):
        self.beatmaps = {
            i.split("\\")[-1]: get_json(i) for i in self.search(("json"), "\\beatmaps")
        }
        self.sfx = {i.split("\\")[-1]: i for i in self.search((".mp3"), "/sfx")}

    def refersh_config(self, name):
        path = f"{self.BASE_ASSETS_FOLDER}/config/{name}.json"
        self.configs[name] = get_json(path)

    def save_config(self, path, data):
        name, *path = path.split("/")
        file_path = f"{self.BASE_ASSETS_FOLDER}/config/{name}.json"
        prev = self.configs[name].copy()
        update_dict(prev, "\\".join(path), data)
        #prev.update(data)
        write_json(file_path, prev)
        self.configs[name] = get_json(file_path)

    def search(self, exts: list | tuple, base=""):
        path = self.BASE_ASSETS_FOLDER + base
        data = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.split(".")[-1] in exts:
                    data.append(os.path.join(root, file))
        return data
