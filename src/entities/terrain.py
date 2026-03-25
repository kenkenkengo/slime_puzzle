"""Static terrain for level geometry."""
from __future__ import annotations

import pymunk

from src.constants import (
    CATEGORY_TERRAIN,
    COLLISION_TERRAIN,
    PARTICLE_ELASTICITY,
    PARTICLE_FRICTION,
)
from src.physics.physics_world import PhysicsWorld


class Terrain:
    """Static terrain polygon."""

    def __init__(
        self,
        world: PhysicsWorld,
        vertices: list[tuple[float, float]],
        friction: float = PARTICLE_FRICTION,
    ) -> None:
        self.world = world
        self.vertices = vertices
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.shapes: list[pymunk.Shape] = []

        if len(vertices) >= 3:
            # Add filled poly for collision
            try:
                poly = pymunk.Poly(self.body, vertices)
                poly.friction = friction
                poly.elasticity = PARTICLE_ELASTICITY
                poly.filter = pymunk.ShapeFilter(categories=CATEGORY_TERRAIN)
                poly.collision_type = COLLISION_TERRAIN
                self.shapes.append(poly)
            except Exception:
                # Fallback to segments for invalid polygon vertex configs
                for i in range(len(vertices)):
                    a = vertices[i]
                    b = vertices[(i + 1) % len(vertices)]
                    seg = pymunk.Segment(self.body, a, b, 2.0)
                    seg.friction = friction
                    seg.elasticity = PARTICLE_ELASTICITY
                    seg.filter = pymunk.ShapeFilter(categories=CATEGORY_TERRAIN)
                    seg.collision_type = COLLISION_TERRAIN
                    self.shapes.append(seg)

        world.space.add(self.body, *self.shapes)

    def destroy(self) -> None:
        """Remove terrain from the world."""
        self.world.remove_static(*self.shapes)
        self.shapes.clear()
