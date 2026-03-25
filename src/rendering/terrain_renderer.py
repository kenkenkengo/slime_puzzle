"""Renders terrain, hazards, and goal zones."""
from __future__ import annotations

import math

import pygame

from src.constants import (
    COLOR_GOAL,
    COLOR_GOAL_GLOW,
    COLOR_HAZARD,
    COLOR_TERRAIN,
    COLOR_TERRAIN_OUTLINE,
)
from src.entities.goal_zone import GoalZone
from src.entities.hazard import Hazard
from src.entities.terrain import Terrain


def draw_terrain(surface: pygame.Surface, terrain: Terrain) -> None:
    """Draw a terrain polygon."""
    if len(terrain.vertices) < 3:
        return
    points = [(int(v[0]), int(v[1])) for v in terrain.vertices]
    pygame.draw.polygon(surface, COLOR_TERRAIN, points)
    pygame.draw.polygon(surface, COLOR_TERRAIN_OUTLINE, points, 2)


def draw_hazard(surface: pygame.Surface, hazard: Hazard) -> None:
    """Draw a hazard zone with spike triangles."""
    x, y, w, h = [int(v) for v in hazard.rect]
    rect = pygame.Rect(x, y, w, h)

    # Base rectangle
    pygame.draw.rect(surface, COLOR_HAZARD, rect)

    # Spike triangles on top
    spike_width = 12
    num_spikes = max(1, w // spike_width)
    actual_width = w / num_spikes

    for i in range(num_spikes):
        sx = x + i * actual_width
        points = [
            (int(sx), y),
            (int(sx + actual_width / 2), y - 8),
            (int(sx + actual_width), y),
        ]
        pygame.draw.polygon(surface, COLOR_HAZARD, points)

    # Outline
    pygame.draw.rect(surface, (180, 30, 30), rect, 1)


def draw_goal(surface: pygame.Surface, goal: GoalZone) -> None:
    """Draw the goal zone with a pulsing glow."""
    x, y, w, h = [int(v) for v in goal.rect]
    rect = pygame.Rect(x, y, w, h)

    alpha = goal.pulse_alpha()
    glow_surface = pygame.Surface((w + 20, h + 20), pygame.SRCALPHA)
    glow_color = (*COLOR_GOAL_GLOW, int(alpha * 80))
    pygame.draw.rect(glow_surface, glow_color, (0, 0, w + 20, h + 20), border_radius=8)
    surface.blit(glow_surface, (x - 10, y - 10))

    # Main goal area
    goal_surface = pygame.Surface((w, h), pygame.SRCALPHA)
    goal_color = (*COLOR_GOAL, int(alpha * 120))
    pygame.draw.rect(goal_surface, goal_color, (0, 0, w, h), border_radius=4)
    surface.blit(goal_surface, (x, y))

    # Border
    pygame.draw.rect(surface, COLOR_GOAL, rect, 2, border_radius=4)

    # Star icon in center
    cx, cy = int(x + w / 2), int(y + h / 2)
    _draw_star(surface, cx, cy, 12, 6, COLOR_GOAL)


def _draw_star(
    surface: pygame.Surface,
    cx: int,
    cy: int,
    outer_r: int,
    inner_r: int,
    color: tuple[int, int, int],
) -> None:
    """Draw a 5-pointed star."""
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = outer_r if i % 2 == 0 else inner_r
        points.append((
            int(cx + r * math.cos(angle)),
            int(cy - r * math.sin(angle)),
        ))
    pygame.draw.polygon(surface, color, points)
