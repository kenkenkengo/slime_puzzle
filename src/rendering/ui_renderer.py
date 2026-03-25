"""UI rendering: HUD, buttons, menus."""
from __future__ import annotations

import pygame

from src.constants import (
    COLOR_BUTTON,
    COLOR_BUTTON_HOVER,
    COLOR_BUTTON_TEXT,
    COLOR_TEXT,
    COLOR_TEXT_SHADOW,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


def draw_text(
    surface: pygame.Surface,
    text: str,
    pos: tuple[int, int],
    font: pygame.font.Font,
    color: tuple[int, int, int] = COLOR_TEXT,
    shadow: bool = True,
    center: bool = False,
) -> pygame.Rect:
    """Draw text with optional shadow and centering."""
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos

    if shadow:
        shadow_rendered = font.render(text, True, COLOR_TEXT_SHADOW)
        shadow_rect = shadow_rendered.get_rect()
        shadow_rect.topleft = (rect.x + 2, rect.y + 2)
        surface.blit(shadow_rendered, shadow_rect)

    surface.blit(rendered, rect)
    return rect


def draw_button(
    surface: pygame.Surface,
    text: str,
    rect: pygame.Rect,
    font: pygame.font.Font,
    mouse_pos: tuple[int, int],
) -> bool:
    """Draw a button and return True if hovered."""
    hovered = rect.collidepoint(mouse_pos)
    color = COLOR_BUTTON_HOVER if hovered else COLOR_BUTTON
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, COLOR_TEXT, rect, 2, border_radius=8)
    draw_text(surface, text, rect.center, font, COLOR_BUTTON_TEXT, shadow=False, center=True)
    return hovered


def draw_hud(
    surface: pygame.Surface,
    font: pygame.font.Font,
    level_name: str,
    particle_count: int,
    initial_particles: int,
    goal_progress: float,
) -> None:
    """Draw the in-game HUD."""
    # Background bar
    hud_surface = pygame.Surface((SCREEN_WIDTH, 40), pygame.SRCALPHA)
    hud_surface.fill((0, 0, 0, 120))
    surface.blit(hud_surface, (0, 0))

    # Level name
    draw_text(surface, level_name, (10, 8), font, shadow=False)

    # Particle count
    mass_pct = int(particle_count / initial_particles * 100) if initial_particles > 0 else 0
    mass_color = (80, 220, 100) if mass_pct > 70 else (220, 180, 50) if mass_pct > 30 else (220, 50, 50)
    draw_text(
        surface,
        f"Mass: {mass_pct}%",
        (SCREEN_WIDTH // 2, 8),
        font,
        color=mass_color,
        shadow=False,
        center=True,
    )

    # Goal progress
    progress_text = f"Goal: {int(goal_progress * 100)}%"
    draw_text(surface, progress_text, (SCREEN_WIDTH - 150, 8), font, shadow=False)

    # Controls hint
    hint_font = pygame.font.SysFont("Arial", 14)
    draw_text(
        surface,
        "Left drag: Move | Right click: Split | R: Restart | ESC: Menu",
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20),
        hint_font,
        color=(150, 150, 170),
        shadow=False,
        center=True,
    )
