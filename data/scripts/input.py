from typing import Literal
import pygame




class Input:
    def __init__(self, app):
        self.app = app
        self.assets = app.assets
        self.binds = self.assets.configs["binds"]
        self.callbacks = {"press": {}, "release": {}, "hold": {}}

    def get_event(self, event, mode: Literal["press", "release", "hold"] = "press"):
        for key in self.binds[event]:
            if self.app.get_event(self._get_key(key), mode):
                return True
        return False
    
    def _get_key(self, key):
        return getattr(pygame, f"K_{key}")

    def add_callback(
        self, name, func, mode: Literal["press", "release", "hold"] = "press"
    ):
        if name not in self.callbacks[mode]:
            self.callbacks[mode][name] = []
        self.callbacks[mode][name].append(func)

    def get_callbacks(self):
        callbacks = {"press": {}, "release": {}, "hold": {}}
        for mode in self.callbacks:
            for name in self.callbacks[mode]:
                for bind in self.binds[name]:
                    key = self._get_key(bind)
                    if key is not None:
                        callbacks[mode][key] = lambda mode=mode, name=name: [
                            f() for f in self.callbacks[mode][name]
                        ]
        return callbacks

