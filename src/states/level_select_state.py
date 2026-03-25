"""Level select screen."""
from __future__ import annotations

import pygame

from src.constants import COLOR_BG, COLOR_GOAL, COLOR_SLIME, SCREEN_HEIGHT, SCREEN_WIDTH
from src.levels.level_loader import get_level_count
from src.rendering.ui_renderer import draw_button, draw_text
from src.states.state_machine import State, StateMachine


class LevelSelectState(State):
    """Level selection screen with a grid of level buttons."""

    def __init__(self, machine: StateMachine) -> None:
        super().__init__(machine)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 24)
        self.back_font = pygame.font.SysFont("Arial", 20)
        self.level_count = get_level_count()
        self._mouse_pos = (0, 0)

        # Create button rects for each level
        self.level_rects: list[pygame.Rect] = []
        cols = min(5, self.level_count)
        start_x = SCREEN_WIDTH // 2 - (cols * 80) // 2
        start_y = SCREEN_HEIGHT // 2 - 40

        for i in range(self.level_count):
            col = i % cols
            row = i // cols
            rect = pygame.Rect(start_x + col * 80, start_y + row * 80, 60, 60)
            self.level_rects.append(rect)

        self.back_rect = pygame.Rect(20, SCREEN_HEIGHT - 60, 100, 40)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self._mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.level_rects):
                if rect.collidepoint(event.pos):
                    from src.states.play_state import PlayState
                    self.machine.change(PlayState(self.machine, level_id=i + 1))
                    return
            if self.back_rect.collidepoint(event.pos):
                from src.states.menu_state import MenuState
                self.machine.change(MenuState(self.machine))
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from src.states.menu_state import MenuState
            self.machine.change(MenuState(self.machine))

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)

        draw_text(
            surface, "Select Level",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4),
            self.title_font, color=COLOR_SLIME, center=True,
        )

        for i, rect in enumerate(self.level_rects):
            draw_button(surface, str(i + 1), rect, self.button_font, self._mouse_pos)

        draw_button(surface, "Back", self.back_rect, self.back_font, self._mouse_pos)
