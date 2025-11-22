import numpy as np
import pygame

from data.scripts.utilities import move_towards
from data.scripts.sprite import Sprite

HIT_THRASHOLD = 20
RMV_DIST = 75


class Node:
    triggered = []

    def __init__(self, spawn_time, hit_line, pos, def_texture: pygame.Surface):
        self.pos = np.array(list(pos), np.float32)
        self.spawn_time = spawn_time
        self.hit_line = hit_line

        self.triggered = False
        self.active = False
        self.rect = def_texture.get_rect()

        # self.r = 10
        # self.color = [70] * 3
        self.sprite = Sprite(def_texture)
        self.surf = self.sprite.get()

        self.scale = 0.5
        self.scale_speed = 0.05
        self.scale_target = 1
        self.overlay_alpha = 0

        mask = pygame.mask.from_surface(self.surf)
        self.overlay = Sprite(
            surf=mask.to_surface(setcolor=(255, 255, 255), unsetcolor=(0, 0, 0))
        )
        self.overlay.surf.set_colorkey((0, 0, 0))
        self.overlay.surf.set_alpha(0)

    def update(self, dir, current_time):
        if current_time >= self.spawn_time:
            
            self.pos += dir
            # if self.pos[1] > self.hit_line_y and not self.triggered:
            #     self.collide()
            #     self.triggered = True

            # if (
            #     self.hit_line_y + HIT_THRASHOLD
            #     >= self.pos[1]
            #     >= self.hit_line_y - HIT_THRASHOLD
            # ):
            #     self.good = True
            # else:
            #     self.good = False

            if self.pos[1] > 30:
                self.scale = move_towards(
                    self.scale, self.scale_target, self.scale_speed, 1
                )
            self.active = True
            if self.pos[1] > self.hit_line + RMV_DIST:
                self.active = False
            self.rect.x = int(self.pos[0])
            self.rect.y = int(self.pos[1]) - self.sprite.get().height / 2
            self.sprite.scale_nrom(self.scale)
            self.overlay.scale_nrom(self.scale)
            self.overlay_alpha = max(self.overlay_alpha - 10, 0)
            self.overlay.surf.set_alpha(self.overlay_alpha)
            # self.color = [max(i - 10, 70) for i in self.color]

    def collide(self):
        # self.r = 20
        if not self.triggered:
            self.triggered = True
            Node.triggered.append(self)
            # if self.good:
            self.scale = 2
            self.scale_speed = 0.1
            self.overlay_alpha = 255
            # else:
            #     self.scale_target = 0.5
            #     self.scale_speed = 0.01

    def render(self, surf, offset=(0, 0)):
        if self.active:
            self.sprite.render(surf, self.pos - offset)
            self.overlay.render(surf, self.pos - offset)
        # pygame.draw.circle(surf, "red", self.pos - offset, 3)
        # pygame.draw.rect(surf, "red", self.rect)
        # surf.blit(self.surf, self.pos - offset)
        # surf.blit(self.overlay, self.pos - offset)

    @classmethod
    def get_result(cls):
        pass

    @classmethod
    def get_collide_rects(cls, nodes):
        out = []
        for node in nodes:
            if node.active and node:
                out.append(node)
        return out

    @staticmethod
    def generate_nodes(
        beatmap,
        hit_line_y,
        start,
        note_speed,
        def_texture,
        strength_min=0.0,
        strength_max=1.0,
    ):
        nodes = []
        for beat in [
            i for i in beatmap if strength_max >= float(i["strength"]) >= strength_min
        ]:
            travel_time = (hit_line_y - start) / note_speed
            spawn_time = beat["time"] - travel_time
            nodes.append(
                Node(
                    spawn_time,
                    hit_line_y,
                    (0, start),
                    def_texture,
                )
            )
        return nodes
