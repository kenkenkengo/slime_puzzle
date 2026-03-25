"""Geometry utilities for slime rendering and physics."""
from __future__ import annotations

import math


def centroid(points: list[tuple[float, float]]) -> tuple[float, float]:
    """Compute the centroid of a set of points."""
    if not points:
        return (0.0, 0.0)
    n = len(points)
    cx = sum(p[0] for p in points) / n
    cy = sum(p[1] for p in points) / n
    return (cx, cy)


def angle_from_center(
    point: tuple[float, float], center: tuple[float, float]
) -> float:
    """Compute the angle from center to point."""
    return math.atan2(point[1] - center[1], point[0] - center[0])


def angle_sort(
    points: list[tuple[float, float]], center: tuple[float, float]
) -> list[tuple[float, float]]:
    """Sort points by angle around a center point."""
    return sorted(points, key=lambda p: angle_from_center(p, center))


def convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Compute convex hull using Andrew's monotone chain algorithm."""
    if len(points) <= 2:
        return list(points)

    sorted_pts = sorted(points)

    def cross(
        o: tuple[float, float],
        a: tuple[float, float],
        b: tuple[float, float],
    ) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list[tuple[float, float]] = []
    for p in sorted_pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper: list[tuple[float, float]] = []
    for p in reversed(sorted_pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Euclidean distance between two points."""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def point_in_rect(
    point: tuple[float, float], rect: tuple[float, float, float, float]
) -> bool:
    """Check if point is inside a rectangle (x, y, w, h)."""
    x, y, w, h = rect
    return x <= point[0] <= x + w and y <= point[1] <= y + h


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation."""
    return a + (b - a) * t
