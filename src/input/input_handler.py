"""Input handling for slime interaction (drag, split, merge)."""
from __future__ import annotations

import pymunk
import pygame

from src.physics.physics_world import PhysicsWorld
from src.physics.slime_manager import SlimeManager
from src.utils.geometry import distance


class InputHandler:
    """Handles mouse input for dragging and splitting slimes."""

    def __init__(self, world: PhysicsWorld, slime_manager: SlimeManager) -> None:
        self.world = world
        self.slime_manager = slime_manager
        self._drag_body: pymunk.Body | None = None
        self._drag_joint: pymunk.PivotJoint | None = None
        self._dragged_slime: object | None = None
        self._dragging = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """Process a pygame event."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click - drag
                self._start_drag(event.pos)
            elif event.button == 3:  # Right click - split
                self._try_split(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            if self._dragging and self._drag_body:
                self._drag_body.position = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self._stop_drag()

    def _start_drag(self, pos: tuple[int, int]) -> None:
        """Start dragging the nearest slime particle."""
        fpos = (float(pos[0]), float(pos[1]))
        slime = self.slime_manager.get_slime_at(fpos)
        if slime is None:
            return

        particle = self.slime_manager.get_nearest_particle(slime, fpos)
        if particle is None:
            return

        # Create a kinematic body at mouse position
        self._drag_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self._drag_body.position = pos
        self.world.space.add(self._drag_body)

        # Connect it to the nearest particle
        self._drag_joint = pymunk.DampedSpring(
            self._drag_body, particle,
            (0, 0), (0, 0),
            rest_length=0,
            stiffness=800,
            damping=40,
        )
        self.world.add_constraint(self._drag_joint)
        self._dragged_slime = slime
        self._dragging = True

    def _stop_drag(self) -> None:
        """Stop dragging."""
        if self._drag_joint:
            self.world.remove_constraint(self._drag_joint)
            self._drag_joint = None
        if self._drag_body:
            self.world.space.remove(self._drag_body)
            self._drag_body = None
        self._dragged_slime = None
        self._dragging = False

    def _try_split(self, pos: tuple[int, int]) -> None:
        """Try to split the slime at the click position."""
        fpos = (float(pos[0]), float(pos[1]))
        slime = self.slime_manager.get_slime_at(fpos)
        if slime is not None:
            self.slime_manager.split(slime, fpos)

    @property
    def is_dragging(self) -> bool:
        return self._dragging

    @property
    def dragged_slime(self) -> object | None:
        return self._dragged_slime

    def cleanup(self) -> None:
        """Clean up any active drag state."""
        self._stop_drag()
