"""Goal zone entity - target area for slime to reach."""
from __future__ import annotations

import math
import time

from src.physics.slime_manager import SlimeManager
from src.utils.geometry import point_in_rect


class GoalZone:
    """Target zone that the slime must reach to complete the level."""

    def __init__(self, rect: tuple[float, float, float, float]) -> None:
        self.rect = rect  # (x, y, w, h)
        self._pulse_start = time.monotonic()

    @property
    def center(self) -> tuple[float, float]:
        return (self.rect[0] + self.rect[2] / 2, self.rect[1] + self.rect[3] / 2)

    def pulse_alpha(self) -> float:
        """Get a pulsing alpha value for rendering."""
        t = time.monotonic() - self._pulse_start
        return 0.5 + 0.3 * math.sin(t * 3)

    def is_complete(self, slime_manager: SlimeManager) -> bool:
        """Check if all slime particles are within the goal zone."""
        if not slime_manager.slimes:
            return False

        for slime in slime_manager.slimes:
            for body in slime.outer_particles:
                pos = (body.position.x, body.position.y)
                if not point_in_rect(pos, self.rect):
                    return False
        return True

    def get_progress(self, slime_manager: SlimeManager) -> float:
        """Get fraction of particles inside the goal zone."""
        total = 0
        inside = 0
        for slime in slime_manager.slimes:
            for body in slime.outer_particles:
                total += 1
                pos = (body.position.x, body.position.y)
                if point_in_rect(pos, self.rect):
                    inside += 1
        return inside / total if total > 0 else 0.0
