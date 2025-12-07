import pygame
from data.scripts.sprite import Sprite
from data.scripts.ui import SpriteBtn


class CheckBox(SpriteBtn):
    def __init__(
        self,
        scene,
        pos,
        default=False,
        size=(10, 10),
        secondary="white",
        primary="blue",
        anchors=(0, 0),
        border_width=1,
    ):
        super().__init__(
            scene, pos, Sprite(size, flags=pygame.SRCALPHA), anchors=anchors
        ),
        self.is_enabled = default
        self._prev_state = self.is_enabled
        self.primary = primary
        self.secondary = secondary
        self.border_width = border_width
        pygame.draw.rect(
            self.surf, self.secondary, (0, 0, self.w, self.h), self.border_width
        )
        if self.is_enabled:
            pygame.draw.rect(
                self.surf,
                self.primary,
                (
                    self.border_width,
                    self.border_width,
                    self.w - self.border_width * 2,
                    self.h - self.border_width * 2,
                ),
            )
        self.callbacks["press"].insert(
            0, lambda x: setattr(self, "is_enabled", not self.is_enabled)
        )

    def render(self, surf, flags=0, opacity=1):
        if self._prev_state != self.is_enabled:
            self._prev_state = self.is_enabled
            self.clear()
            pygame.draw.rect(
                self.surf, self.secondary, (0, 0, self.w, self.h), self.border_width
            )
            if self.is_enabled:
                pygame.draw.rect(
                    self.surf,
                    self.primary,
                    (
                        self.border_width,
                        self.border_width,
                        self.w - self.border_width * 2,
                        self.h - self.border_width * 2,
                    ),
                )

        super().render(surf, flags, opacity)
