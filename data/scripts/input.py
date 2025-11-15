from typing import Literal
import pygame


class Input:
    def __init__(self, app):
        self.assets = app.assets
        self.binds = self.assets.binds
        self.callbacks = {"press": {}, "release": {}, "hold": {}}

    def add_callback(
        self, name, func, mode: Literal["press", "release", "hold"] = "press"
    ):
        if name not in self.callbacks:
            self.callbacks[mode][name] = []
        self.callbacks[mode][name].append(func)

    def get_callbacks(self):
        callbacks = {"press": {}, "release": {}, "hold": {}}
        for mode in self.callbacks:
            for name in self.callbacks[mode]:
                for bind in self.binds[name]:
                    key = getattr(pygame, f"K_{bind}")
                    if key is not None:
                        callbacks[mode][key] = lambda mode=mode, name=name: [
                            f() for f in self.callbacks[mode][name]
                        ]
        return callbacks
