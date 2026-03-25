"""Main menu state."""
from __future__ import annotations

import pygame

from src.constants import COLOR_BG, COLOR_SLIME, SCREEN_HEIGHT, SCREEN_WIDTH
from src.rendering.ui_renderer import draw_button, draw_text
from src.states.state_machine import State, StateMachine


class MenuState(State):
    """Title screen with Play and Quit buttons."""

    def __init__(self, machine: StateMachine) -> None:
        super().__init__(machine)
        self.title_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.subtitle_font = pygame.font.SysFont("Arial", 24)
        self.button_font = pygame.font.SysFont("Arial", 28)
        self.play_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50,
        )
        self.quit_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, 200, 50,
        )
        self._mouse_pos = (0, 0)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self._mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_rect.collidepoint(event.pos):
                from src.states.level_select_state import LevelSelectState
                self.machine.change(LevelSelectState(self.machine))
            elif self.quit_rect.collidepoint(event.pos):
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)

        # Title
        draw_text(
            surface, "Slime Puzzle",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3),
            self.title_font, color=COLOR_SLIME, center=True,
        )

        # Subtitle
        draw_text(
            surface, "Stretch, Split, and Squish your way through!",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60),
            self.subtitle_font, color=(180, 180, 200), center=True,
        )

        # Buttons
        draw_button(surface, "Play", self.play_rect, self.button_font, self._mouse_pos)
        draw_button(surface, "Quit", self.quit_rect, self.button_font, self._mouse_pos)
