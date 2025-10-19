"""
Debug Overlay System for UI Layout Development.

Provides visual debugging tools for the layout management system,
including grid visualization, panel bounds, collision detection,
and performance metrics.
"""

import pygame
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time

from src.ui.layout_manager import LayoutManager, UILayer, LayoutMode


class DebugOverlayMode(Enum):
    """Debug overlay display modes."""
    GRID = "grid"              # Show grid lines and cells
    PANELS = "panels"          # Show panel bounds and constraints
    COLLISIONS = "collisions"  # Show collision detection
    PERFORMANCE = "performance"  # Show performance metrics
    ALL = "all"               # Show everything


@dataclass
class DebugMetrics:
    """Performance and layout metrics for debugging."""
    fps: float = 0.0
    layout_calc_time: float = 0.0
    render_time: float = 0.0
    panel_count: int = 0
    collision_count: int = 0
    last_update: float = 0.0


class LayoutDebugOverlay:
    """Debug overlay for visualizing and debugging the layout system."""

    def __init__(self, screen_width: int, screen_height: int):
        """Initialize debug overlay.

        Args:
            screen_width: Screen width
            screen_height: Screen height
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.enabled = False
        self.mode = DebugOverlayMode.ALL
        self.font = pygame.font.SysFont('monospace', 14)
        self.small_font = pygame.font.SysFont('monospace', 10)

        # Colors for debugging
        self.colors = {
            'grid_line': (100, 100, 100, 128),
            'grid_cell': (50, 50, 50, 64),
            'panel_bounds': (255, 255, 0, 200),
            'panel_constraints': (0, 255, 255, 150),
            'collision': (255, 0, 0, 180),
            'text_bg': (0, 0, 0, 180),
            'text_fg': (255, 255, 255),
            'performance_good': (0, 255, 0),
            'performance_warning': (255, 255, 0),
            'performance_bad': (255, 0, 0),
        }

        # Performance tracking
        self.metrics = DebugMetrics()
        self.frame_times: List[float] = []
        self.layout_calc_times: List[float] = []
        # Debug state
        self.selected_panel: Optional[str] = None
        self.show_panel_info = False
        # Validation issues (populated by layout validator)
        self.validation_issues: List[str] = []

    def toggle_enabled(self) -> None:
        """Toggle debug overlay on/off."""
        self.enabled = not self.enabled

    def set_mode(self, mode: DebugOverlayMode) -> None:
        """Set debug overlay mode.

        Args:
            mode: Debug mode to display
        """
        self.mode = mode

    def cycle_mode(self) -> None:
        """Cycle through debug modes."""
        modes = list(DebugOverlayMode)
        current_index = modes.index(self.mode)
        next_index = (current_index + 1) % len(modes)
        self.mode = modes[next_index]

    def update_metrics(self, fps: float, layout_calc_time: float, render_time: float,
                      panel_count: int, collision_count: int) -> None:
        """Update performance metrics.

        Args:
            fps: Current FPS
            layout_calc_time: Time spent calculating layout
            render_time: Time spent rendering
            panel_count: Number of panels
            collision_count: Number of collisions detected
        """
        current_time = time.time()

        self.metrics.fps = fps
        self.metrics.layout_calc_time = layout_calc_time
        self.metrics.render_time = render_time
        self.metrics.panel_count = panel_count
        self.metrics.collision_count = collision_count
        self.metrics.last_update = current_time

        # Keep rolling averages
        self.frame_times.append(1.0 / fps if fps > 0 else 0)
        self.layout_calc_times.append(layout_calc_time)

        # Limit history
        max_history = 60
        if len(self.frame_times) > max_history:
            self.frame_times = self.frame_times[-max_history:]
        if len(self.layout_calc_times) > max_history:
            self.layout_calc_times = self.layout_calc_times[-max_history:]

    def render(self, screen: pygame.Surface, layout_manager: LayoutManager) -> None:
        """Render debug overlay.

        Args:
            screen: Pygame screen surface
            layout_manager: Layout manager to debug
        """
        if not self.enabled:
            return

        # Render based on current mode
        if self.mode in [DebugOverlayMode.GRID, DebugOverlayMode.ALL]:
            self._render_grid_overlay(screen, layout_manager)

        if self.mode in [DebugOverlayMode.PANELS, DebugOverlayMode.ALL]:
            self._render_panel_overlay(screen, layout_manager)

        if self.mode in [DebugOverlayMode.COLLISIONS, DebugOverlayMode.ALL]:
            self._render_collision_overlay(screen, layout_manager)

        if self.mode in [DebugOverlayMode.PERFORMANCE, DebugOverlayMode.ALL]:
            self._render_performance_overlay(screen)

        # Render mode indicator
        self._render_mode_indicator(screen)

    def _render_grid_overlay(self, screen: pygame.Surface, layout_manager: LayoutManager) -> None:
        """Render grid visualization overlay.

        Args:
            screen: Screen surface
            layout_manager: Layout manager
        """
        grid_config = layout_manager.grid_config

        # Create semi-transparent surface for grid
        grid_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

        # Draw grid cells
        for row in range(grid_config.rows):
            for col in range(grid_config.cols):
                cell_rect = self._get_grid_cell_rect(layout_manager, row, col)
                if cell_rect:
                    # Fill cell with semi-transparent color
                    pygame.draw.rect(grid_surface, self.colors['grid_cell'], cell_rect, 0)

                    # Draw cell border
                    pygame.draw.rect(grid_surface, self.colors['grid_line'], cell_rect, 1)

                    # Draw cell coordinates (small text)
                    coord_text = f"{col},{row}"
                    text_surf = self.small_font.render(coord_text, True, self.colors['text_fg'])
                    text_rect = text_surf.get_rect(center=cell_rect.center)
                    grid_surface.blit(text_surf, text_rect)

        # Draw reserved zones
        for zone in grid_config.reserved_zones:
            pygame.draw.rect(grid_surface, (255, 0, 255, 100), zone, 2)  # Magenta for reserved

        screen.blit(grid_surface, (0, 0))

    def _render_panel_overlay(self, screen: pygame.Surface, layout_manager: LayoutManager) -> None:
        """Render panel bounds and constraints overlay.

        Args:
            screen: Screen surface
            layout_manager: Layout manager
        """
        overlay_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

        for panel_name, panel in layout_manager.panels.items():
            if hasattr(panel, 'rect'):
                panel_rect = panel.rect

                # Draw panel bounds
                pygame.draw.rect(overlay_surface, self.colors['panel_bounds'], panel_rect, 2)

                # Draw constraints info if available
                if panel_name in layout_manager.panel_constraints:
                    constraints = layout_manager.panel_constraints[panel_name]
                    mode = layout_manager.panel_modes[panel_name]

                    # Draw constraint visualization for grid-like constraints
                    if mode == LayoutMode.GRID and hasattr(constraints, 'row'):
                        self._draw_grid_constraints(overlay_surface, constraints, panel_rect)

                # Draw panel name
                name_text = self.small_font.render(panel_name, True, self.colors['text_fg'])
                text_bg = pygame.Surface((name_text.get_width() + 4, name_text.get_height() + 2), pygame.SRCALPHA)
                text_bg.fill(self.colors['text_bg'])
                text_bg.blit(name_text, (2, 1))

                screen.blit(text_bg, (panel_rect.left + 5, panel_rect.top + 5))

        screen.blit(overlay_surface, (0, 0))

    def _render_collision_overlay(self, screen: pygame.Surface, layout_manager: LayoutManager) -> None:
        """Render collision detection overlay.

        Args:
            screen: Screen surface
            layout_manager: Layout manager
        """
        overlay_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

        # Check for collisions between panels
        panel_rects = []
        for panel_name, panel in layout_manager.panels.items():
            if hasattr(panel, 'rect'):
                panel_rects.append((panel_name, panel.rect))

        for i, (name1, rect1) in enumerate(panel_rects):
            for name2, rect2 in panel_rects[i+1:]:
                if rect1.colliderect(rect2):
                    # Draw collision area
                    collision_rect = rect1.clip(rect2)
                    pygame.draw.rect(overlay_surface, self.colors['collision'], collision_rect, 0)

                    # Draw collision indicator
                    center = collision_rect.center
                    pygame.draw.circle(overlay_surface, self.colors['collision'], center, 10, 2)

        screen.blit(overlay_surface, (0, 0))

    def _render_performance_overlay(self, screen: pygame.Surface) -> None:
        """Render performance metrics overlay.

        Args:
            screen: Screen surface
        """
        # Create overlay surface
        overlay_surface = pygame.Surface((300, 150), pygame.SRCALPHA)
        overlay_surface.fill(self.colors['text_bg'])

        # Performance metrics
        metrics_text = [
            f"FPS: {self.metrics.fps:.1f}",
            f"Layout: {self.metrics.layout_calc_time*1000:.2f}ms",
            f"Render: {self.metrics.render_time*1000:.2f}ms",
            f"Panels: {self.metrics.panel_count}",
            f"Collisions: {self.metrics.collision_count}",
        ]

        # Color code performance
        fps_color = self._get_performance_color(self.metrics.fps, 60, 30)
        layout_color = self._get_performance_color(self.metrics.layout_calc_time * 1000, 1, 5)
        render_color = self._get_performance_color(self.metrics.render_time * 1000, 5, 16)

        colors = [fps_color, layout_color, render_color,
                 self.colors['text_fg'], self.colors['text_fg']]

        y_offset = 10
        for i, text in enumerate(metrics_text):
            color = colors[i] if i < len(colors) else self.colors['text_fg']
            text_surf = self.font.render(text, True, color)
            overlay_surface.blit(text_surf, (10, y_offset))
            y_offset += 20

        # Position in top-right corner
        screen.blit(overlay_surface, (self.screen_width - 310, 10))

        # Render validation issues below performance box
        if self.validation_issues:
            issues_surface = pygame.Surface((self.screen_width - 20, 100), pygame.SRCALPHA)
            issues_surface.fill((0, 0, 0, 140))
            title = self.small_font.render("Layout Issues:", True, (255, 200, 0))
            issues_surface.blit(title, (6, 6))
            y = 30
            for issue in self.validation_issues[:4]:
                txt = self.small_font.render(issue, True, (255, 180, 180))
                issues_surface.blit(txt, (6, y))
                y += 20

            screen.blit(issues_surface, (10, 10 + 160))

    def _render_mode_indicator(self, screen: pygame.Surface) -> None:
        """Render current debug mode indicator.

        Args:
            screen: Screen surface
        """
        mode_text = f"DEBUG: {self.mode.value.upper()}"
        text_surf = self.font.render(mode_text, True, self.colors['text_fg'])

        # Background
        bg_surf = pygame.Surface((text_surf.get_width() + 10, text_surf.get_height() + 6), pygame.SRCALPHA)
        bg_surf.fill(self.colors['text_bg'])
        bg_surf.blit(text_surf, (5, 3))

        # Position in bottom-left
        screen.blit(bg_surf, (10, self.screen_height - bg_surf.get_height() - 10))

    def _get_grid_cell_rect(self, layout_manager: LayoutManager, row: int, col: int) -> Optional[pygame.Rect]:
        """Get rectangle for a grid cell.

        Args:
            layout_manager: Layout manager
            row: Grid row
            col: Grid column

        Returns:
            Cell rectangle or None if invalid
        """
        try:
            cell_width = layout_manager._cell_width
            cell_height = layout_manager._cell_height
            origin_x, origin_y = layout_manager._grid_origin

            x = origin_x + col * (cell_width + layout_manager.grid_config.gutter)
            y = origin_y + row * (cell_height + layout_manager.grid_config.gutter)

            return pygame.Rect(x, y, cell_width, cell_height)
        except (AttributeError, TypeError):
            return None

    def _draw_grid_constraints(self, surface: pygame.Surface, constraints, panel_rect: pygame.Rect) -> None:
        """Draw grid constraint visualization.

        Args:
            surface: Surface to draw on
            constraints: Grid constraints
            panel_rect: Panel rectangle
        """
        # Draw constraint grid cells
        for r in range(constraints.row, constraints.row + constraints.row_span):
            for c in range(constraints.col, constraints.col + constraints.col_span):
                cell_rect = pygame.Rect(
                    panel_rect.left + (c - constraints.col) * 20,
                    panel_rect.top + (r - constraints.row) * 20,
                    18, 18
                )
                pygame.draw.rect(surface, self.colors['panel_constraints'], cell_rect, 1)

    def _get_performance_color(self, value: float, good_threshold: float, bad_threshold: float) -> Tuple[int, int, int]:
        """Get color based on performance value.

        Args:
            value: Performance value
            good_threshold: Threshold for good performance
            bad_threshold: Threshold for bad performance

        Returns:
            RGB color tuple
        """
        if value <= good_threshold:
            return self.colors['performance_good']
        elif value <= bad_threshold:
            return self.colors['performance_warning']
        else:
            return self.colors['performance_bad']

    def handle_click(self, pos: Tuple[int, int], layout_manager: LayoutManager) -> bool:
        """Handle mouse click for debug interaction.

        Args:
            pos: Mouse position
            layout_manager: Layout manager

        Returns:
            True if debug overlay handled the click
        """
        if not self.enabled:
            return False

        # Check if clicking on a panel for inspection
        for panel_name, panel in layout_manager.panels.items():
            if hasattr(panel, 'rect') and panel.rect.collidepoint(pos):
                self.selected_panel = panel_name
                self.show_panel_info = True
                return True

        # Clear selection if clicking elsewhere
        self.selected_panel = None
        self.show_panel_info = False
        return False

    def get_panel_info(self, layout_manager: LayoutManager) -> Optional[Dict[str, Any]]:
        """Get detailed info about selected panel.

        Args:
            layout_manager: Layout manager

        Returns:
            Panel information dict or None
        """
        if not self.selected_panel or self.selected_panel not in layout_manager.panels:
            return None

        panel = layout_manager.panels[self.selected_panel]
        constraints = layout_manager.panel_constraints.get(self.selected_panel)
        mode = layout_manager.panel_modes.get(self.selected_panel)

        info = {
            'name': self.selected_panel,
            'mode': mode.value if mode else 'unknown',
            'position': (panel.rect.left, panel.rect.top) if hasattr(panel, 'rect') else None,
            'size': (panel.rect.width, panel.rect.height) if hasattr(panel, 'rect') else None,
            'constraints': str(constraints) if constraints else 'none',
            'layer': 'unknown',  # Would need layer manager integration
        }

        return info