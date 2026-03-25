"""Main game loop and initialization."""
from __future__ import annotations

import pygame

from src.constants import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TITLE
from src.states.menu_state import MenuState
from src.states.state_machine import StateMachine


class Game:
    """Main game class - handles the game loop."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.machine = StateMachine()

    def run(self) -> None:
        """Main game loop."""
        self.machine.push(MenuState(self.machine))

        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            # Cap dt to prevent physics explosions
            dt = min(dt, 1 / 30.0)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.machine.handle_event(event)

            self.machine.update(dt)
            self.machine.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
