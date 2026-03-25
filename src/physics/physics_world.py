"""Physics world wrapper around pymunk Space."""
from __future__ import annotations

import pymunk

from src.constants import GRAVITY, PHYSICS_TIMESTEP


class PhysicsWorld:
    """Manages the pymunk physics simulation."""

    def __init__(self) -> None:
        self.space = pymunk.Space()
        self.space.gravity = GRAVITY
        self.space.damping = 0.95
        self._accumulator = 0.0

    def step(self, dt: float) -> None:
        """Step physics with fixed timestep accumulator."""
        self._accumulator += dt
        while self._accumulator >= PHYSICS_TIMESTEP:
            self.space.step(PHYSICS_TIMESTEP)
            self._accumulator -= PHYSICS_TIMESTEP

    def add_body(self, body: pymunk.Body, *shapes: pymunk.Shape) -> None:
        """Add a body and its shapes to the space."""
        self.space.add(body, *shapes)

    def remove_body(self, body: pymunk.Body, *shapes: pymunk.Shape) -> None:
        """Remove a body and its shapes from the space."""
        self.space.remove(body, *shapes)

    def add_static(self, *shapes: pymunk.Shape) -> None:
        """Add static shapes to the space."""
        self.space.add(*shapes)

    def remove_static(self, *shapes: pymunk.Shape) -> None:
        """Remove static shapes from the space."""
        self.space.remove(*shapes)

    def add_constraint(self, constraint: pymunk.Constraint) -> None:
        """Add a constraint to the space."""
        self.space.add(constraint)

    def remove_constraint(self, constraint: pymunk.Constraint) -> None:
        """Remove a constraint from the space."""
        self.space.remove(constraint)
