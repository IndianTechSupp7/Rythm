import random
from turtle import color, rt
import numpy as np
import pygame
from torch import rand

from data.scripts.particles import Bit, Circle, Physics, Spark
from data.scripts.ui.letter import RandLetter
from data.scripts.utilities import adjuts, bezier, move_towards
from data.scripts.sprite import Sprite

HIT_THRASHOLD = 20
RMV_DIST = 75


class Node:
    triggered = []

    def __init__(
        self, game, spawn_time, hit_line, pos, def_texture: pygame.Surface, strength
    ):
        self.game = game
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

        self._color = self.surf.get_at((5, 5))

        mask = pygame.mask.from_surface(self.surf).to_surface(
            setcolor=(255, 255, 255), unsetcolor=(0, 0, 0)
        )
        mask.set_colorkey((0, 0, 0))
        self.overlay = Sprite(
            surf=mask,
            flags=pygame.SRCALPHA,
        )
        self.overlay.surf.set_alpha(0)

        self.font = RandLetter(self.game)
        self.strength = Sprite(self.font.render(strength, color=(0, 0, 0), alpha=60))

    def update(self, dir, current_time, dt):
        if current_time >= self.spawn_time:
            if self.pos[1] <= 10:
                self.active = True

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

            self.rect.x = int(self.pos[0])
            self.rect.y = int(self.pos[1]) - self.sprite.get().height / 2
            self.sprite.scale_nrom(self.scale)
            self.overlay.scale_nrom(self.scale)
            self.overlay_alpha = max(self.overlay_alpha - 10, 0)
            # self.overlay.surf.set_alpha(self.overlay_alpha)
            if self.pos[1] > self.hit_line + RMV_DIST:
                self.active = False
                return True
            if not self.active:
                return True
            # self.color = [max(i - 10, 70) for i in self.color]

    def collide(self, perfect=False):
        # self.r = 20
        if not self.triggered:
            self.triggered = True
            Node.triggered.append(self)
            # if self.good:

            if perfect:
                self.game.shake()
                amount = 6
                speed = 20
                for _ in range(random.randint(5, 15) + amount):
                    self.game.particleManager.add_particle(
                        Spark(
                            pos=self.pos,
                            color=self._color,
                            dir=random.random() * np.pi * 2,
                            speed=random.randint(60, 80) - speed,
                            size=random.randint(5, 10),
                            thickness=random.random() * 0.3,
                        )
                    )
                    
            for _ in range(3):
                self.game.particleManager.add_particle(
                    Bit(
                        self.game,
                        self.pos,
                        adjuts((0, 0), random.random() * -np.pi, random.randint(1, 3)),
                        random.random() * 2 + 1,
                        color=self._color,
                    )
                )

            self.active = False

            # else:
            #     self.scale_target = 0.5
            #     self.scale_speed = 0.01

    def render(self, surf, offset=(0, 0)):
        if self.active:
            # if abs(self.pos[1] - self.hit_line) < 3:
            #     pygame.draw.circle(surf, "blue", self.pos - offset, 15)
            self.sprite.render(surf, self.pos - offset)
            self.strength.render(surf, self.pos - offset)
            self.overlay.render(surf, self.pos - offset, opacity=self.overlay_alpha)
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
        game,
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
            travel_time = (hit_line_y - start[1]) / note_speed
            spawn_time = round(beat["time"], 1) - travel_time
            nodes.append(
                Node(
                    game,
                    spawn_time,
                    hit_line_y,
                    start,
                    def_texture,
                    str(round(beat["strength"] * 1000)),
                )
            )
        return nodes
