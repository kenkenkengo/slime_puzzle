"""Manages multiple slime bodies, handles split and merge operations."""
from __future__ import annotations

import math
import time

import pymunk

from src.constants import (
    INNER_SPRING_DAMPING,
    INNER_SPRING_STIFFNESS,
    MERGE_DISTANCE_FACTOR,
    MERGE_TIME,
    MIN_SPLIT_PARTICLES,
    PARTICLE_ELASTICITY,
    PARTICLE_FRICTION,
    PARTICLE_MASS,
    PARTICLE_RADIUS,
    SPRING_DAMPING,
    SPRING_STIFFNESS,
    CATEGORY_SLIME,
    COLLISION_SLIME,
)
from src.physics.physics_world import PhysicsWorld
from src.physics.slime_body import SlimeBody
from src.utils.geometry import angle_from_center, centroid, distance


class SlimeManager:
    """Manages all slime bodies and their split/merge operations."""

    def __init__(self, world: PhysicsWorld) -> None:
        self.world = world
        self.slimes: list[SlimeBody] = []
        self._merge_timers: dict[tuple[int, int], float] = {}

    def create_slime(
        self,
        center_pos: tuple[float, float],
        radius: float = 40.0,
        num_particles: int = 12,
    ) -> SlimeBody:
        """Create a new slime and add it to the manager."""
        slime = SlimeBody(self.world, center_pos, radius, num_particles)
        self.slimes.append(slime)
        return slime

    def split(
        self, slime: SlimeBody, split_pos: tuple[float, float]
    ) -> tuple[SlimeBody, SlimeBody] | None:
        """Split a slime into two at the given position.

        Returns the two new slimes, or None if split is not possible.
        """
        if slime not in self.slimes:
            return None
        if slime.particle_count < MIN_SPLIT_PARTICLES * 2:
            return None

        center = slime.get_center()

        # Split line perpendicular to the line from center to split_pos
        dx = split_pos[0] - center[0]
        dy = split_pos[1] - center[1]

        # Divide particles into two groups based on which side of the split line
        group_a: list[int] = []
        group_b: list[int] = []

        for i, body in enumerate(slime.outer_particles):
            # Dot product with split direction
            px = body.position.x - center[0]
            py = body.position.y - center[1]
            dot = px * dx + py * dy
            if dot >= 0:
                group_a.append(i)
            else:
                group_b.append(i)

        # Ensure minimum size
        if len(group_a) < MIN_SPLIT_PARTICLES or len(group_b) < MIN_SPLIT_PARTICLES:
            return None

        # Collect particle data before destroying original
        particles_a = [
            (slime.outer_particles[i].position.x, slime.outer_particles[i].position.y,
             slime.outer_particles[i].velocity.x, slime.outer_particles[i].velocity.y)
            for i in group_a
        ]
        particles_b = [
            (slime.outer_particles[i].position.x, slime.outer_particles[i].position.y,
             slime.outer_particles[i].velocity.x, slime.outer_particles[i].velocity.y)
            for i in group_b
        ]

        # Destroy original slime
        self.slimes.remove(slime)
        slime.destroy()

        # Create two new slimes from the particle groups
        slime_a = self._create_from_particles(particles_a)
        slime_b = self._create_from_particles(particles_b)

        self.slimes.append(slime_a)
        self.slimes.append(slime_b)

        return (slime_a, slime_b)

    def _create_from_particles(
        self,
        particle_data: list[tuple[float, float, float, float]],
    ) -> SlimeBody:
        """Create a new SlimeBody from existing particle positions and velocities."""
        positions = [(px, py) for px, py, _, _ in particle_data]
        center_pos = centroid(positions)

        # Sort particles by angle from center for proper ring ordering
        indexed = list(enumerate(particle_data))
        indexed.sort(
            key=lambda item: angle_from_center(
                (item[1][0], item[1][1]), center_pos
            )
        )

        # Create a minimal SlimeBody without auto-creating particles
        slime = SlimeBody.__new__(SlimeBody)
        slime.world = self.world
        slime.radius = max(distance(center_pos, (px, py)) for px, py, _, _ in particle_data)
        slime.outer_particles = []
        slime.outer_shapes = []
        slime.springs = []
        slime.slide_joints = []
        slime._alive = True

        # Create center body
        slime.center_body = pymunk.Body(
            PARTICLE_MASS * 2,
            pymunk.moment_for_circle(PARTICLE_MASS * 2, 0, PARTICLE_RADIUS),
        )
        slime.center_body.position = center_pos
        slime.center_shape = pymunk.Circle(slime.center_body, PARTICLE_RADIUS)
        slime.center_shape.friction = PARTICLE_FRICTION
        slime.center_shape.elasticity = PARTICLE_ELASTICITY
        slime.center_shape.filter = pymunk.ShapeFilter(categories=CATEGORY_SLIME)
        slime.center_shape.collision_type = COLLISION_SLIME
        self.world.add_body(slime.center_body, slime.center_shape)

        # Create outer particles in sorted order
        for _, (px, py, vx, vy) in indexed:
            body = pymunk.Body(
                PARTICLE_MASS,
                pymunk.moment_for_circle(PARTICLE_MASS, 0, PARTICLE_RADIUS),
            )
            body.position = (px, py)
            body.velocity = (vx, vy)
            shape = pymunk.Circle(body, PARTICLE_RADIUS)
            shape.friction = PARTICLE_FRICTION
            shape.elasticity = PARTICLE_ELASTICITY
            shape.filter = pymunk.ShapeFilter(categories=CATEGORY_SLIME)
            shape.collision_type = COLLISION_SLIME
            self.world.add_body(body, shape)
            slime.outer_particles.append(body)
            slime.outer_shapes.append(shape)

        # Rebuild springs
        slime._create_springs()
        return slime

    def check_merges(self) -> None:
        """Check if any slimes are close enough to merge."""
        now = time.monotonic()
        active_pairs: set[tuple[int, int]] = set()

        for i in range(len(self.slimes)):
            for j in range(i + 1, len(self.slimes)):
                a = self.slimes[i]
                b = self.slimes[j]

                dist = distance(a.get_center(), b.get_center())
                merge_dist = (a.get_bounding_radius() + b.get_bounding_radius()) * MERGE_DISTANCE_FACTOR

                pair_key = (id(a), id(b))
                active_pairs.add(pair_key)

                if dist < merge_dist:
                    if pair_key not in self._merge_timers:
                        self._merge_timers[pair_key] = now
                    elif now - self._merge_timers[pair_key] >= MERGE_TIME:
                        self._do_merge(a, b)
                        # Clean up timers and restart check
                        self._merge_timers = {
                            k: v for k, v in self._merge_timers.items()
                            if k in active_pairs
                        }
                        return
                else:
                    self._merge_timers.pop(pair_key, None)

        # Clean stale timers
        self._merge_timers = {
            k: v for k, v in self._merge_timers.items()
            if k in active_pairs
        }

    def _do_merge(self, a: SlimeBody, b: SlimeBody) -> SlimeBody:
        """Merge two slimes into one."""
        # Collect all particle data
        all_particles: list[tuple[float, float, float, float]] = []
        for body in a.outer_particles:
            all_particles.append((body.position.x, body.position.y, body.velocity.x, body.velocity.y))
        for body in b.outer_particles:
            all_particles.append((body.position.x, body.position.y, body.velocity.x, body.velocity.y))

        # Remove old slimes
        self.slimes.remove(a)
        self.slimes.remove(b)
        a.destroy()
        b.destroy()

        # Create merged slime
        merged = self._create_from_particles(all_particles)
        self.slimes.append(merged)
        return merged

    def get_slime_at(self, pos: tuple[float, float]) -> SlimeBody | None:
        """Find a slime near the given position."""
        for slime in self.slimes:
            center = slime.get_center()
            if distance(pos, center) < slime.get_bounding_radius() + 20:
                return slime
        return None

    def get_nearest_particle(
        self, slime: SlimeBody, pos: tuple[float, float]
    ) -> pymunk.Body | None:
        """Find the nearest particle in a slime to the given position."""
        if not slime.outer_particles:
            return None
        return min(
            slime.outer_particles,
            key=lambda b: distance(pos, (b.position.x, b.position.y)),
        )

    def total_particle_count(self) -> int:
        """Total number of outer particles across all slimes."""
        return sum(s.particle_count for s in self.slimes)

    def remove_slime(self, slime: SlimeBody) -> None:
        """Remove a slime from the manager."""
        if slime in self.slimes:
            self.slimes.remove(slime)
            slime.destroy()

    def clear(self) -> None:
        """Remove all slimes."""
        for slime in list(self.slimes):
            slime.destroy()
        self.slimes.clear()
        self._merge_timers.clear()
