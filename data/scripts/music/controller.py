from platform import node
import numpy as np
import pygame

from data.scripts.sprite import Sprite
from data.scripts.utilities import bezier
from .node import Node

from data.scripts.asset_magare import AssetManager
from data.scripts.input import Input

IMG_SCALE = 2
BBOX = (10, 10)


class Btn:
    def __init__(
        self, game, nodes, pos, key, sheet: list[pygame.Surface], anchor_point=(1, 1)
    ):
        self.game = game
        self.nodes = nodes
        self.input: Input = self.game.input

        self.anchor_point = np.array(anchor_point)

        # self.sheet = [
        #     pygame.transform.scale(
        #         sheet[y],
        #         (
        #             sheet[y].get_size()[0] * IMG_SCALE,
        #             sheet[y].get_size()[1] * IMG_SCALE,
        #         ),
        #     )
        #     for y in sheet
        # ]
        self.sheet = [sheet[i] for i in sheet]

        self.on = Sprite(self.sheet[1]).scale_nrom(IMG_SCALE)
        self.off = Sprite(self.sheet[0]).scale_nrom(IMG_SCALE)

        # self.on = pygame.Surface(self.sheet[1].get_size(), pygame.SRCALPHA)
        # self.on.blit(self.sheet[1], (0, 0))

        # self.off = pygame.Surface(self.sheet[0].get_size(), pygame.SRCALPHA)
        # self.off.blit(self.sheet[0], (0, 0))

        # self.on = pygame.transform.scale(self.on, np.array(self.on.size) * IMG_SCALE)
        # self.off = pygame.transform.scale(self.off, np.array(self.off.size) * IMG_SCALE)

        self.pos = np.array(pos)

        self.mouse = self.game.mouse
        self.input.add_callback(key, self.active, "press")
        self.input.add_callback(key, self.reset, "release")

        self.current_state = self.off
        self.rect: pygame.Rect = self.current_state.get_rect(
            self.pos - self.current_state.offset((1, 1))
        )

        self.collide = False

    def active(self):
        self.current_state = self.on
        self.rect: pygame.Rect = self.current_state.get_rect(
            self.pos - self.current_state.offset((1, 1))
        )
        for node in self.nodes:
            if self.rect.inflate(*BBOX).colliderect(node.rect):
                node.collide()

    def reset(self):
        self.current_state = self.off
        self.rect: pygame.Rect = self.current_state.get_rect(
            self.pos - self.current_state.offset((1, 1))
        )

    def update(self, offset, nodes):
        self.nodes = nodes

    def render(self, surf, offset):
        self.current_state.render(surf, self.pos - offset, self.anchor_point)
        # surf.blit(
        #     self.current_state,
        #     self.pos - self.rect.center + (self.rect.center * self.anchor_point),
        # )
        # pygame.draw.rect(surf, "blue", self.rect.inflate(*BBOX))


class Controller:
    def __init__(
        self,
        game,
        beatmap,
        start_pos,
        note_speed,
        note,
        hit_line_y,
        min_strength=0.0,
        max_strength=1.0,
    ):
        self.beatmap = beatmap
        self.note = note
        self.game = game

        self.assets: AssetManager = self.game.assets

        self.start_pos = np.array(start_pos)
        self.note_speed = note_speed
        self.min_strength = min_strength
        self.max_strength = max_strength
        self.dir = np.array((0.0, 1.0))
        self.hit_line_y = hit_line_y
        # self.finished = False

        self.img = self.assets.images["notes"][note + ".png"]
        self.nodes = Node.generate_nodes(
            beatmap=self.beatmap,
            hit_line_y=self.hit_line_y,
            start=self.start_pos[1],
            note_speed=self.note_speed,
            strength_min=self.min_strength,
            strength_max=self.max_strength,
            def_texture=pygame.transform.scale(
                self.img, np.array(self.img.get_size()) * IMG_SCALE
            ),
        )

        self.center = self.game.center
        self.btn = Btn(
            game=self.game,
            nodes=self.nodes,
            pos=(self.start_pos[0], self.hit_line_y),
            key=self.note,
            sheet=self.assets.images[self.note],
            anchor_point=(0, 0.5),
        )
        self.entering = abs(self.center[0] - self.start_pos[0]) * 0.01

    def update(self, dt, current_time):
        for i, node in sorted(enumerate(self.nodes), reverse=True):
            if node.update(self.dir * self.note_speed * dt, current_time, dt):
                self.nodes.pop(i)
            else:
                node.rect.centerx = self.start_pos[0]
        # if self.nodes[-1].triggered:
        #     self.finished = True
        nodes = Node.get_collide_rects(self.nodes)
        self.btn.update((-self.start_pos[0], 0), nodes)

    def render(self, surf):
        # pygame.draw.line(
        #     surf, "white", (0, self.hit_line_y), (self.game.game.w, self.hit_line_y)
        # )

        # pygame.draw.line(
        #     surf, "blue", (100, self.hit_line_y - 20), (100, self.hit_line_y + 20)
        # )
        self.entering = max(0, min(1, self.entering + 0.03))
        e = 1 - bezier(0.187, 0.627, 0.762, 1.256, self.entering)[1]
        for node in self.nodes[::-1]:
            node.render(surf, (-self.start_pos[0], 0))
        self.btn.render(surf, (0, -(e * 70)))
