"""Soft-body slime implemented as a particle mesh with spring constraints."""
from __future__ import annotations

import math

import pymunk

from src.constants import (
    CATEGORY_SLIME,
    COLLISION_SLIME,
    INNER_SPRING_DAMPING,
    INNER_SPRING_STIFFNESS,
    PARTICLE_ELASTICITY,
    PARTICLE_FRICTION,
    PARTICLE_MASS,
    PARTICLE_RADIUS,
    SPRING_DAMPING,
    SPRING_STIFFNESS,
)
from src.physics.physics_world import PhysicsWorld
from src.utils.geometry import centroid, distance


class SlimeBody:
    """A soft-body slime made of particles connected by springs."""

    def __init__(
        self,
        world: PhysicsWorld,
        center_pos: tuple[float, float],
        radius: float = 40.0,
        num_particles: int = 12,
    ) -> None:
        self.world = world
        self.radius = radius
        self.outer_particles: list[pymunk.Body] = []
        self.outer_shapes: list[pymunk.Circle] = []
        self.center_body: pymunk.Body | None = None
        self.center_shape: pymunk.Circle | None = None
        self.springs: list[pymunk.DampedSpring] = []
        self.slide_joints: list[pymunk.SlideJoint] = []
        self._alive = True

        self._create_particles(center_pos, radius, num_particles)
        self._create_springs()

    def _create_particles(
        self,
        center_pos: tuple[float, float],
        radius: float,
        num_particles: int,
    ) -> None:
        """Create center + outer ring of particles."""
        # Center particle
        self.center_body = pymunk.Body(PARTICLE_MASS * 2, pymunk.moment_for_circle(PARTICLE_MASS * 2, 0, PARTICLE_RADIUS))
        self.center_body.position = center_pos
        self.center_shape = pymunk.Circle(self.center_body, PARTICLE_RADIUS)
        self.center_shape.friction = PARTICLE_FRICTION
        self.center_shape.elasticity = PARTICLE_ELASTICITY
        self.center_shape.filter = pymunk.ShapeFilter(categories=CATEGORY_SLIME)
        self.center_shape.collision_type = COLLISION_SLIME
        self.world.add_body(self.center_body, self.center_shape)

        # Outer particles in a ring
        for i in range(num_particles):
            angle = 2 * math.pi * i / num_particles
            x = center_pos[0] + radius * math.cos(angle)
            y = center_pos[1] + radius * math.sin(angle)

            body = pymunk.Body(PARTICLE_MASS, pymunk.moment_for_circle(PARTICLE_MASS, 0, PARTICLE_RADIUS))
            body.position = (x, y)
            shape = pymunk.Circle(body, PARTICLE_RADIUS)
            shape.friction = PARTICLE_FRICTION
            shape.elasticity = PARTICLE_ELASTICITY
            shape.filter = pymunk.ShapeFilter(categories=CATEGORY_SLIME)
            shape.collision_type = COLLISION_SLIME
            self.world.add_body(body, shape)
            self.outer_particles.append(body)
            self.outer_shapes.append(shape)

    def _create_springs(self) -> None:
        """Connect particles with damped springs."""
        n = len(self.outer_particles)

        # Connect adjacent outer particles
        for i in range(n):
            a = self.outer_particles[i]
            b = self.outer_particles[(i + 1) % n]
            rest_length = distance(
                (a.position.x, a.position.y),
                (b.position.x, b.position.y),
            )
            spring = pymunk.DampedSpring(
                a, b, (0, 0), (0, 0),
                rest_length=rest_length,
                stiffness=SPRING_STIFFNESS,
                damping=SPRING_DAMPING,
            )
            self.world.add_constraint(spring)
            self.springs.append(spring)

            # Safety slide joint to prevent extreme stretching
            slide = pymunk.SlideJoint(
                a, b, (0, 0), (0, 0),
                min=rest_length * 0.3,
                max=rest_length * 2.5,
            )
            self.world.add_constraint(slide)
            self.slide_joints.append(slide)

        # Connect each outer particle to center
        assert self.center_body is not None
        for particle in self.outer_particles:
            rest_length = distance(
                (particle.position.x, particle.position.y),
                (self.center_body.position.x, self.center_body.position.y),
            )
            spring = pymunk.DampedSpring(
                particle, self.center_body, (0, 0), (0, 0),
                rest_length=rest_length,
                stiffness=INNER_SPRING_STIFFNESS,
                damping=INNER_SPRING_DAMPING,
            )
            self.world.add_constraint(spring)
            self.springs.append(spring)

            slide = pymunk.SlideJoint(
                particle, self.center_body, (0, 0), (0, 0),
                min=rest_length * 0.2,
                max=rest_length * 3.0,
            )
            self.world.add_constraint(slide)
            self.slide_joints.append(slide)

        # Cross-bracing: connect opposite outer particles for stability
        for i in range(n // 2):
            a = self.outer_particles[i]
            b = self.outer_particles[i + n // 2]
            rest_length = distance(
                (a.position.x, a.position.y),
                (b.position.x, b.position.y),
            )
            spring = pymunk.DampedSpring(
                a, b, (0, 0), (0, 0),
                rest_length=rest_length,
                stiffness=INNER_SPRING_STIFFNESS * 0.5,
                damping=INNER_SPRING_DAMPING * 0.5,
            )
            self.world.add_constraint(spring)
            self.springs.append(spring)

    def get_center(self) -> tuple[float, float]:
        """Get the average position of all particles."""
        positions = self.get_positions()
        return centroid(positions)

    def get_positions(self) -> list[tuple[float, float]]:
        """Get positions of all outer particles."""
        return [(b.position.x, b.position.y) for b in self.outer_particles]

    def get_all_positions(self) -> list[tuple[float, float]]:
        """Get positions of all particles including center."""
        positions = self.get_positions()
        if self.center_body:
            positions.append((self.center_body.position.x, self.center_body.position.y))
        return positions

    def apply_force(self, force: tuple[float, float]) -> None:
        """Apply a force to the center body."""
        if self.center_body:
            self.center_body.apply_force_at_local_point(force, (0, 0))

    def get_bounding_radius(self) -> float:
        """Get the current bounding radius from center."""
        center = self.get_center()
        if not self.outer_particles:
            return 0.0
        return max(
            distance(center, (b.position.x, b.position.y))
            for b in self.outer_particles
        )

    def get_velocity(self) -> tuple[float, float]:
        """Get average velocity of all particles."""
        if not self.outer_particles:
            return (0.0, 0.0)
        vx = sum(b.velocity.x for b in self.outer_particles) / len(self.outer_particles)
        vy = sum(b.velocity.y for b in self.outer_particles) / len(self.outer_particles)
        return (vx, vy)

    def destroy(self) -> None:
        """Remove all bodies, shapes, and constraints from the world."""
        if not self._alive:
            return
        self._alive = False

        for spring in self.springs:
            self.world.remove_constraint(spring)
        for slide in self.slide_joints:
            self.world.remove_constraint(slide)

        for body, shape in zip(self.outer_particles, self.outer_shapes):
            self.world.remove_body(body, shape)

        if self.center_body and self.center_shape:
            self.world.remove_body(self.center_body, self.center_shape)

        self.springs.clear()
        self.slide_joints.clear()
        self.outer_particles.clear()
        self.outer_shapes.clear()
        self.center_body = None
        self.center_shape = None

    @property
    def alive(self) -> bool:
        return self._alive

    @property
    def particle_count(self) -> int:
        return len(self.outer_particles)
