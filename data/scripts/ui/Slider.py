import time
import numpy as np
from data.scripts.ui.progressbar import Bar
from data.scripts.utilities import clamp


class Slider(Bar):
    def __init__(
        self,
        scene,
        pos,
        start_value=0,
        scale=(60, 10),
        color="white",
        anchors=(0, 0),
        secondary=(255, 255, 255, 10),
    ):
        super().__init__(scene, start_value, 0, scale[0], scale, color, secondary)
        self.pos = np.array(pos)
        self.grab = False
        self.anchors = np.array(anchors)
        self.on_change = []
        self.on_fix_change = []
        self._prev = self.t
        self._last_changed = time.time()

    def add_callback(self, func, mode):
        getattr(self, mode, []).append(func)
        return self

    def update(self, offset=(0, 0)):
        global_pos = self.pos + offset - self.offset((1, 1) - self.anchors)
        if self.scene.mouse["press"][0]:
            if self.get_rect(global_pos).collidepoint(self.scene.mouse["pos"]):
                self.grab = True
        if self.grab:
            self.value = self.scene.mouse["pos"][0] - global_pos[0]
            for func in self.on_change:
                func(self.t)
        if self.value != self._prev:
            self._last_changed = time.time()
            self._prev = self.value
        if time.time() - self._last_changed > 0.1:
            for func in self.on_fix_change:
                func(self.t)

        if self.scene.mouse["release"][0]:
            self.grab = False

    def render(self, surf):
        super().render(surf, self.pos, anchors=self.anchors)
