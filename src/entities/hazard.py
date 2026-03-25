"""Hazard entities that destroy slime particles."""
from __future__ import annotations

import pymunk

from src.constants import (
    CATEGORY_HAZARD,
    COLLISION_HAZARD,
    COLLISION_SLIME,
)
from src.physics.physics_world import PhysicsWorld
from src.physics.slime_manager import SlimeManager


class Hazard:
    """A hazardous zone that destroys slime particles on contact."""

    def __init__(
        self,
        world: PhysicsWorld,
        rect: tuple[float, float, float, float],
        hazard_type: str = "spikes",
    ) -> None:
        self.world = world
        self.rect = rect
        self.hazard_type = hazard_type
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)

        x, y, w, h = rect
        vertices = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        self.shape = pymunk.Poly(self.body, vertices)
        self.shape.sensor = True
        self.shape.filter = pymunk.ShapeFilter(categories=CATEGORY_HAZARD)
        self.shape.collision_type = COLLISION_HAZARD
        world.space.add(self.body, self.shape)

    def destroy(self) -> None:
        """Remove hazard from the world."""
        self.world.remove_static(self.shape)


def setup_hazard_collision(
    world: PhysicsWorld,
    slime_manager: SlimeManager,
    on_particle_hit: callable | None = None,
) -> None:
    """Set up collision handler between slime particles and hazards."""
    handler = world.space.add_collision_handler(COLLISION_SLIME, COLLISION_HAZARD)

    particles_to_remove: list[tuple[pymunk.Body, pymunk.Shape]] = []

    def begin(arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict) -> bool:
        shapes = arbiter.shapes
        # Find the slime shape (not the hazard)
        for shape in shapes:
            if shape.collision_type == COLLISION_SLIME:
                particles_to_remove.append((shape.body, shape))
        return False  # Don't process collision physically

    def post_step_remove(space: pymunk.Space, key: object, data: dict) -> None:
        for body, shape in particles_to_remove:
            # Find which slime owns this particle and remove it
            for slime in list(slime_manager.slimes):
                if body in slime.outer_particles:
                    idx = slime.outer_particles.index(body)
                    # Remove springs connected to this particle
                    springs_to_remove = [
                        s for s in slime.springs
                        if s.a == body or s.b == body
                    ]
                    slides_to_remove = [
                        s for s in slime.slide_joints
                        if s.a == body or s.b == body
                    ]
                    for s in springs_to_remove:
                        world.remove_constraint(s)
                        slime.springs.remove(s)
                    for s in slides_to_remove:
                        world.remove_constraint(s)
                        slime.slide_joints.remove(s)

                    world.remove_body(body, shape)
                    slime.outer_particles.pop(idx)
                    slime.outer_shapes.pop(idx)

                    if slime.particle_count < 3:
                        slime_manager.remove_slime(slime)

                    if on_particle_hit:
                        on_particle_hit()
                    break
        particles_to_remove.clear()

    def separate(arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict) -> None:
        pass

    handler.begin = begin
    handler.separate = separate

    # We need to process removals in post_step to avoid modifying space during collision
    original_step = world.step

    def step_with_cleanup(dt: float) -> None:
        original_step(dt)
        if particles_to_remove:
            post_step_remove(world.space, None, {})

    world.step = step_with_cleanup  # type: ignore[assignment]
