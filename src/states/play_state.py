"""Main gameplay state."""
from __future__ import annotations

import time

import pygame

from src.constants import COLOR_BG, SCREEN_HEIGHT, SCREEN_WIDTH
from src.entities.goal_zone import GoalZone
from src.entities.hazard import Hazard, setup_hazard_collision
from src.entities.terrain import Terrain
from src.input.input_handler import InputHandler
from src.levels.level_loader import LevelData, load_level
from src.physics.physics_world import PhysicsWorld
from src.physics.slime_manager import SlimeManager
from src.rendering.slime_renderer import draw_slime
from src.rendering.terrain_renderer import draw_goal, draw_hazard, draw_terrain
from src.rendering.ui_renderer import draw_hud
from src.states.state_machine import State, StateMachine


class PlayState(State):
    """The main gameplay state - loads and runs a level."""

    def __init__(self, machine: StateMachine, level_id: int = 1) -> None:
        super().__init__(machine)
        self.level_id = level_id
        self.world: PhysicsWorld | None = None
        self.slime_manager: SlimeManager | None = None
        self.input_handler: InputHandler | None = None
        self.terrains: list[Terrain] = []
        self.hazards: list[Hazard] = []
        self.goal: GoalZone | None = None
        self.level_data: LevelData | None = None
        self.initial_particles = 0
        self.start_time = 0.0
        self.hud_font = pygame.font.SysFont("Arial", 20)
        self._complete = False
        self._complete_time = 0.0

    def enter(self) -> None:
        self._load_level()

    def _load_level(self) -> None:
        """Load and initialize a level."""
        self._cleanup()
        self._complete = False

        self.level_data = load_level(self.level_id)
        self.world = PhysicsWorld()
        self.slime_manager = SlimeManager(self.world)

        # Create slime
        start = self.level_data.slime_start
        self.slime_manager.create_slime(
            (start.x, start.y),
            radius=start.radius,
            num_particles=start.num_particles,
        )
        self.initial_particles = start.num_particles

        # Create terrain
        for t_data in self.level_data.terrain:
            vertices = [(v[0], v[1]) for v in t_data.vertices]
            self.terrains.append(Terrain(self.world, vertices, t_data.friction))

        # Create hazards
        for h_data in self.level_data.hazards:
            self.hazards.append(
                Hazard(self.world, h_data.rect, h_data.hazard_type)
            )

        # Set up hazard collisions
        if self.hazards:
            setup_hazard_collision(self.world, self.slime_manager)

        # Create goal
        self.goal = GoalZone(self.level_data.goal.rect)

        # Input
        self.input_handler = InputHandler(self.world, self.slime_manager)

        self.start_time = time.monotonic()

    def _cleanup(self) -> None:
        """Clean up current level resources."""
        if self.input_handler:
            self.input_handler.cleanup()
        if self.slime_manager:
            self.slime_manager.clear()
        for t in self.terrains:
            t.destroy()
        for h in self.hazards:
            h.destroy()
        self.terrains.clear()
        self.hazards.clear()

    def exit(self) -> None:
        self._cleanup()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._load_level()
                return
            elif event.key == pygame.K_ESCAPE:
                from src.states.level_select_state import LevelSelectState
                self.machine.change(LevelSelectState(self.machine))
                return
            elif event.key == pygame.K_SPACE and self._complete:
                self._next_level()
                return

        if not self._complete and self.input_handler:
            self.input_handler.handle_event(event)

    def update(self, dt: float) -> None:
        if self._complete:
            return

        if self.world:
            self.world.step(dt)

        if self.slime_manager:
            self.slime_manager.check_merges()

            # Check if all slimes are dead
            if not self.slime_manager.slimes:
                self._load_level()
                return

        # Check goal
        if self.goal and self.slime_manager and self.goal.is_complete(self.slime_manager):
            self._complete = True
            self._complete_time = time.monotonic() - self.start_time

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)

        # Draw terrain
        for terrain in self.terrains:
            draw_terrain(surface, terrain)

        # Draw hazards
        for hazard in self.hazards:
            draw_hazard(surface, hazard)

        # Draw goal
        if self.goal:
            draw_goal(surface, self.goal)

        # Draw slimes
        if self.slime_manager:
            for slime in self.slime_manager.slimes:
                is_dragged = (
                    self.input_handler is not None
                    and self.input_handler.is_dragging
                    and self.input_handler.dragged_slime is slime
                )
                draw_slime(surface, slime, is_dragged=is_dragged)

        # HUD
        if self.level_data and self.slime_manager and self.goal:
            draw_hud(
                surface,
                self.hud_font,
                f"Level {self.level_id}: {self.level_data.name}",
                self.slime_manager.total_particle_count(),
                self.initial_particles,
                self.goal.get_progress(self.slime_manager),
            )

        # Level complete overlay
        if self._complete:
            self._draw_complete_overlay(surface)

    def _draw_complete_overlay(self, surface: pygame.Surface) -> None:
        """Draw the level complete overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        big_font = pygame.font.SysFont("Arial", 48, bold=True)
        info_font = pygame.font.SysFont("Arial", 24)

        # Title
        text = big_font.render("Level Complete!", True, (255, 215, 0))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        surface.blit(text, rect)

        # Time
        time_text = info_font.render(
            f"Time: {self._complete_time:.1f}s", True, (200, 200, 220),
        )
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60))
        surface.blit(time_text, time_rect)

        # Mass retained
        if self.slime_manager:
            mass_pct = int(
                self.slime_manager.total_particle_count()
                / self.initial_particles
                * 100
            )
            mass_text = info_font.render(
                f"Mass Retained: {mass_pct}%", True, (200, 200, 220),
            )
            mass_rect = mass_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 95),
            )
            surface.blit(mass_text, mass_rect)

        # Instructions
        hint = info_font.render(
            "Press SPACE for next level | ESC for level select",
            True, (150, 150, 170),
        )
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 150))
        surface.blit(hint, hint_rect)

    def _next_level(self) -> None:
        """Go to the next level."""
        from src.levels.level_loader import get_level_count
        if self.level_id < get_level_count():
            self.level_id += 1
            self._load_level()
        else:
            from src.states.level_select_state import LevelSelectState
            self.machine.change(LevelSelectState(self.machine))
