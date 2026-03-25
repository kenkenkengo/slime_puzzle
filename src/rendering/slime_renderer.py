"""Renders slime bodies with glow and eyes."""
from __future__ import annotations

import math

import pygame

from src.constants import (
    COLOR_SLIME,
    COLOR_SLIME_DRAG,
    COLOR_SLIME_EYE_PUPIL,
    COLOR_SLIME_EYE_WHITE,
    COLOR_SLIME_GLOW,
)
from src.physics.slime_body import SlimeBody
from src.utils.geometry import centroid, convex_hull


def draw_slime(
    surface: pygame.Surface,
    slime: SlimeBody,
    is_dragged: bool = False,
) -> None:
    """Draw a slime body with glow effect and eyes."""
    positions = slime.get_positions()
    if len(positions) < 3:
        # Draw individual particles if too few for a hull
        for pos in positions:
            pygame.draw.circle(surface, COLOR_SLIME, (int(pos[0]), int(pos[1])), 8)
        return

    hull = convex_hull(positions)
    if len(hull) < 3:
        return

    hull_points = [(int(p[0]), int(p[1])) for p in hull]
    center = centroid(positions)

    # Glow layer (expanded hull)
    glow_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    glow_points = []
    for p in hull:
        dx = p[0] - center[0]
        dy = p[1] - center[1]
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            glow_points.append((
                int(p[0] + dx / dist * 8),
                int(p[1] + dy / dist * 8),
            ))
        else:
            glow_points.append((int(p[0]), int(p[1])))

    if len(glow_points) >= 3:
        pygame.draw.polygon(glow_surface, COLOR_SLIME_GLOW, glow_points)
        surface.blit(glow_surface, (0, 0))

    # Main body
    color = COLOR_SLIME_DRAG if is_dragged else COLOR_SLIME
    pygame.draw.polygon(surface, color, hull_points)

    # Lighter inner highlight
    inner_points = []
    for p in hull:
        dx = p[0] - center[0]
        dy = p[1] - center[1]
        inner_points.append((
            int(center[0] + dx * 0.5),
            int(center[1] + dy * 0.5 - 3),
        ))
    if len(inner_points) >= 3:
        highlight_color = (
            min(color[0] + 40, 255),
            min(color[1] + 40, 255),
            min(color[2] + 40, 255),
        )
        highlight_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(
            highlight_surface,
            (*highlight_color, 80),
            inner_points,
        )
        surface.blit(highlight_surface, (0, 0))

    # Eyes
    _draw_eyes(surface, center, slime.get_bounding_radius())


def _draw_eyes(
    surface: pygame.Surface,
    center: tuple[float, float],
    radius: float,
) -> None:
    """Draw cute eyes on the slime."""
    eye_size = max(4, int(radius * 0.15))
    pupil_size = max(2, eye_size // 2)
    eye_y = int(center[1] - radius * 0.2)
    eye_spacing = max(6, int(radius * 0.25))

    left_eye = (int(center[0] - eye_spacing), eye_y)
    right_eye = (int(center[0] + eye_spacing), eye_y)

    # White
    pygame.draw.circle(surface, COLOR_SLIME_EYE_WHITE, left_eye, eye_size)
    pygame.draw.circle(surface, COLOR_SLIME_EYE_WHITE, right_eye, eye_size)

    # Pupils (slightly offset down for a cute look)
    pygame.draw.circle(
        surface, COLOR_SLIME_EYE_PUPIL,
        (left_eye[0], left_eye[1] + 1), pupil_size,
    )
    pygame.draw.circle(
        surface, COLOR_SLIME_EYE_PUPIL,
        (right_eye[0], right_eye[1] + 1), pupil_size,
    )
