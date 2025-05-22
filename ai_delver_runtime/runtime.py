from typing import cast, Any
from .world_objects import WorldObjectsController, WorldObject
from .world_objects.entities.delver import Delver
from .world_objects.items import Goal
from pyglet_dragonbones import config as pdb_config

# Pylance throws a nonsense error here, so I had to ignore type checking.
from pytiling import (
    TilemapBorderTracer,  # type: ignore
    PymunkTilemapPhysics,  # type: ignore
)
from pytiling.pyglet_support import TilemapRenderer  # type: ignore
import pymunk
import json
from pathlib import Path

with open(Path(__file__).parent / "config.json", "r") as file:
    config = json.load(file)

pdb_config.fps = config["fps"]


class Runtime:
    def __init__(self, level: Any):
        self.level = level
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)

        self.running = False

        self.world_objects_controller = self.world_objects_controller_factory(
            self.space
        )
        self.delver = cast(
            "Delver", self.world_objects_controller.get_world_object("delver")
        )
        self.goal = self.world_objects_controller.get_world_object("goal")

        self.tilemap_renderer = self.tilemap_renderer_factory()

    def update(self, dt):
        self.world_objects_controller.update_world_objects(dt)
        # self._check_collisions()

        self.space.step(dt)

    # def _check_collisions(self):
    #     if self.delver.check_collision(self.goal):
    #         from app_manager import app_manager

    #         app_manager.stop_game()

    def run(self):
        self.running = True

    def stop(self):
        if not self.running:
            return

        self.running = False

    @property
    def tilemap(self):
        return self.tilemap_renderer.tilemap

    def world_objects_controller_factory(self, space: "pymunk.Space"):
        world_objects_controller = WorldObjectsController()

        def _place_world_object(world_object: "WorldObject", **args):
            world_object_actual_pos = self.level.map.grid_pos_to_actual_pos(
                element.position
            )
            world_object.position = (
                world_object_actual_pos[0] + self.level.map.tile_size[0] / 2,
                world_object_actual_pos[1] + self.level.map.tile_size[1] / 2,
            )
            world_objects_controller.add_world_object(world_object, **args)

        def _delver_factory(element):
            delver = Delver(self, space=space)
            delver.set_angle(180)

            _place_world_object(delver, unique_identifier="delver")

        def _goal_factory(element):
            goal = Goal(self, element.canvas_object_name)

            _place_world_object(goal, unique_identifier="goal")

        world_objects_factories = {"delver": _delver_factory, "goal": _goal_factory}

        for element in self.level.map.world_objects_map.all_elements:
            world_objects_factories[element.name](element)

        return world_objects_controller

    def tilemap_renderer_factory(self):
        walls = self.level.map.tilemap.get_layer("walls")
        border_tracer = TilemapBorderTracer(walls)
        PymunkTilemapPhysics(border_tracer, self.space)

        tilemap_renderer = TilemapRenderer(self.level.map.tilemap)
        return tilemap_renderer
