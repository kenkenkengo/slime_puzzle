"""Simple state machine for game state management."""
from __future__ import annotations

from abc import ABC, abstractmethod

import pygame


class State(ABC):
    """Base class for game states."""

    def __init__(self, machine: StateMachine) -> None:
        self.machine = machine

    def enter(self) -> None:
        """Called when entering this state."""

    def exit(self) -> None:
        """Called when leaving this state."""

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a pygame event."""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update state logic."""

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the state."""


class StateMachine:
    """Manages game state transitions."""

    def __init__(self) -> None:
        self._states: list[State] = []

    @property
    def current(self) -> State | None:
        return self._states[-1] if self._states else None

    def push(self, state: State) -> None:
        """Push a new state onto the stack."""
        state.enter()
        self._states.append(state)

    def pop(self) -> None:
        """Pop the current state."""
        if self._states:
            self._states[-1].exit()
            self._states.pop()

    def change(self, state: State) -> None:
        """Replace the current state."""
        if self._states:
            self._states[-1].exit()
            self._states.pop()
        state.enter()
        self._states.append(state)

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.current:
            self.current.handle_event(event)

    def update(self, dt: float) -> None:
        if self.current:
            self.current.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        if self.current:
            self.current.draw(surface)
