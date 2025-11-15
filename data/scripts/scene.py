from abc import ABC, abstractmethod
import inspect


class Scene(ABC):
    scenes = {}

    @classmethod
    def add_scene(cls, scene):
        cls.scenes[scene.__class__.__name__] = scene().get()

    def get(self):
        return self, inspect.signature(self.update).parameters

    @classmethod
    def update_scenes(cls, game):
        surfs = []
        for name in cls.scenes:
            scene, args = cls.scenes[name]
            values = [getattr(game, arg) for arg in args if hasattr(game, arg)]
            surfs.append(scene.update(*values))
        return surfs

    @classmethod
    def setup_scenes(cls, game):
        for name in cls.scenes:
            scene, _ = cls.scenes[name]
            scene.setup(game)

    @abstractmethod
    def setup(self, game, **kwargs):
        """
        Called once when the window is created (like __init__).
        returns a dict of input keys {<action> : {<key> : <func>}}

        """
        pass

    @abstractmethod
    def update(self, **kwargs):
        """
        Called once when the window is created (like __init__).
        returns a the display Surface of the Scene

        """
        pass
