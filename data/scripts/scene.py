from abc import ABC, abstractmethod
import inspect
import numpy as np
import pygame

from data.scripts.asset_magare import AssetManager
from data.scripts.input import Input
from window import Window


class Scene(ABC):
    scenes = {}
    _current_scene = None
    game = None
    # assets: AssetManager | None = None

    @classmethod
    def init_scene_manager(cls, game):
        cls.game = game
        # cls.assets = game.assets

    def __init__(self, display_scale=1):
        self.input = Input(self.game)
        self.display_scale = display_scale

        self.size = self.w, self.h = (
            Window.size[0] * self.display_scale,
            Window.size[1] * self.display_scale,
        )

        self.surf: pygame.Surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

        self.center = np.array((self.w / 2, self.h / 2))

        self.assets: AssetManager = self.game.assets
        self.mouse = self.game.mouse
        super().__init__()

    def handle_mouse_events(self):
        mx, my = self.mouse["pos"]
        self.mouse["pos"] = (mx * self.display_scale, my * self.display_scale)

    @classmethod
    def current_scene(cls):
        return cls._current_scene[0]

    @classmethod
    def change_scene(cls, scene_name):
        if cls._current_scene == cls.scenes[scene_name]:
            return
        cls._current_scene = cls.scenes[scene_name]
        cls.game.switch_events(cls._current_scene[0].setup_scene())
        # cls.game.switch_events(cls._current_scene[0].input.get_callbacks())
        # TODO:reset scene?

    @classmethod
    def add_scene(cls, scene):
        scene = scene()
        cls.scenes[scene.__class__.__name__] = scene.get()
        if not cls._current_scene:
            cls._current_scene = cls.scenes[scene.__class__.__name__]

    def get(self):
        return self, inspect.signature(self.update).parameters

    @classmethod
    def update_scene(cls):
        scene, args = cls._current_scene
        values = [getattr(cls.game, arg) for arg in args if hasattr(cls.game, arg)]
        scene.center = np.array((scene.w / 2, scene.h / 2))
        scene.handle_mouse_events()
        return scene.update(*values)

    @classmethod
    def setup_scene(cls):
        cls._current_scene[0].setup()
        return cls._current_scene[0].input.get_callbacks()

    @abstractmethod
    def setup(self, **kwargs):
        """
        Called once when the window is created (like __init__).
        returns a dict of input keys {<action> : {<key> : <func>}}

        """

    @abstractmethod
    def update(self, **kwargs):
        """
        Called once when the window is created (like __init__).
        returns a the display Surface of the Scene

        """
        pass
