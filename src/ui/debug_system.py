"""
UI Debug System for Layout and Panel Development.

Provides comprehensive debugging tools for UI development including:
- Layout grid visualization
- Panel bounds and constraints display
- Collision detection overlay
- Performance metrics
- Panel inspector
"""

import pygame
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import time


@dataclass
class DebugMetrics:
    """Performance and layout metrics for debugging."""
    fps: float = 0.0
    render_time: float = 0.0
    layout_time: float = 0.0
    panel_count: int = 0
    collision_count: int = 0
    last_update: float = 0.0


class LayoutDebugOverlay:
    """Debug overlay showing layout grid, panel bounds, and collision detection."""

    def __init__(self, layout_manager, screen_size: Tuple[int, int]):
        """Initialize debug overlay.

        Args:
            layout_manager: LayoutManager instance to debug
            screen_size: Screen dimensions (width, height)
        """
        self.layout_manager = layout_manager
        self.screen_size = screen_size
        self.visible = False

        # Debug settings
        self.show_grid = True
        self.show_panel_bounds = True
        self.show_reserved_zones = True
        self.show_collision_boxes = True
        self.show_panel_info = True
        self.show_performance = True

        # Colors
        self.grid_color = (100, 100, 100, 100)  # Semi-transparent gray
        self.panel_bounds_color = (255, 255, 0, 200)  # Yellow
        self.reserved_zone_color = (255, 0, 0, 100)  # Red semi-transparent
        self.collision_color = (255, 0, 255, 150)  # Magenta
        self.text_color = (255, 255, 255)  # White
        self.background_color = (0, 0, 0, 150)  # Semi-transparent black

        # Fonts
        self.font = pygame.font.SysFont('Arial', 12)
        self.small_font = pygame.font.SysFont('Arial', 10)

        # Performance tracking
        self.metrics = DebugMetrics()
        self.frame_times: List[float] = []
        self.max_frame_samples = 60

    def toggle_visibility(self) -> None:
        """Toggle debug overlay visibility."""
        self.visible = not self.visible

    def toggle_grid(self) -> None:
        """Toggle grid lines visibility."""
        self.show_grid = not self.show_grid

    def toggle_panel_bounds(self) -> None:
        """Toggle panel bounds visibility."""
        self.show_panel_bounds = not self.show_panel_bounds

    def toggle_collision_boxes(self) -> None:
        """Toggle collision detection boxes."""
        self.show_collision_boxes = not self.show_collision_boxes

    def update_metrics(self, fps: float, render_time: float, layout_time: float) -> None:
        """Update performance metrics.

        Args:
            fps: Current FPS
            render_time: Time spent rendering (seconds)
            layout_time: Time spent on layout calculations (seconds)
        """
        current_time = time.time()

        # Update frame time buffer for averaging
        self.frame_times.append(current_time)
        if len(self.frame_times) > self.max_frame_samples:
            self.frame_times.pop(0)

        # Update metrics
        self.metrics.fps = fps
        self.metrics.render_time = render_time * 1000  # Convert to ms
        self.metrics.layout_time = layout_time * 1000  # Convert to ms
        self.metrics.panel_count = len(self.layout_manager.panels)
        self.metrics.collision_count = self._count_collisions()
        self.metrics.last_update = current_time

    def _count_collisions(self) -> int:
        """Count current panel collisions."""
        collision_count = 0
        panels = list(self.layout_manager.panels.values())

        for i, panel1 in enumerate(panels):
            if not hasattr(panel1, 'get_rect'):
                continue
            rect1 = panel1.get_rect()
            for j, panel2 in enumerate(panels[i+1:], i+1):
                if not hasattr(panel2, 'get_rect'):
                    continue
                rect2 = panel2.get_rect()
                if rect1.colliderect(rect2):
                    collision_count += 1

        return collision_count

    def render(self, screen: pygame.Surface) -> None:
        """Render debug overlay.

        Args:
            screen: Pygame surface to render on
        """
        if not self.visible:
            return

        # Show grid lines
        if self.show_grid:
            self._render_grid(screen)

        # Show reserved zones
        if self.show_reserved_zones:
            self._render_reserved_zones(screen)

        # Show panel bounds and info
        if self.show_panel_bounds or self.show_panel_info:
            self._render_panel_info(screen)

        # Show collision detection
        if self.show_collision_boxes:
            self._render_collision_boxes(screen)

        # Show performance metrics
        if self.show_performance:
            self._render_performance_overlay(screen)

    def _render_grid(self, screen: pygame.Surface) -> None:
        """Render grid lines showing layout cells."""
        grid_config = self.layout_manager.grid_config

        # Calculate cell dimensions
        cell_width = self.layout_manager._cell_width
        cell_height = self.layout_manager._cell_height
        origin_x, origin_y = self.layout_manager._grid_origin

        # Draw vertical grid lines
        for col in range(grid_config.cols + 1):
            x = origin_x + col * (cell_width + grid_config.gutter)
            pygame.draw.line(screen, self.grid_color[:3], (x, origin_y),
                           (x, origin_y + grid_config.rows * (cell_height + grid_config.gutter)), 1)

        # Draw horizontal grid lines
        for row in range(grid_config.rows + 1):
            y = origin_y + row * (cell_height + grid_config.gutter)
            pygame.draw.line(screen, self.grid_color[:3], (origin_x, y),
                           (origin_x + grid_config.cols * (cell_width + grid_config.gutter), y), 1)

        # Draw cell coordinates (top-left corner of each cell)
        for row in range(grid_config.rows):
            for col in range(grid_config.cols):
                x = origin_x + col * (cell_width + grid_config.gutter) + 2
                y = origin_y + row * (cell_height + grid_config.gutter) + 2

                coord_text = self.small_font.render(f"{col},{row}", True, self.grid_color[:3])
                screen.blit(coord_text, (x, y))

    def _render_reserved_zones(self, screen: pygame.Surface) -> None:
        """Render reserved zones (navigation menu, HUD, etc.)."""
        for zone in self.layout_manager.grid_config.reserved_zones:
            # Create semi-transparent surface
            zone_surface = pygame.Surface((zone.width, zone.height))
            zone_surface.set_alpha(100)
            zone_surface.fill(self.reserved_zone_color[:3])
            screen.blit(zone_surface, (zone.x, zone.y))

            # Draw border
            pygame.draw.rect(screen, self.reserved_zone_color[:3], zone, 2)

            # Label
            label_text = self.small_font.render("RESERVED", True, self.text_color)
            screen.blit(label_text, (zone.x + 2, zone.y + 2))

    def _render_panel_info(self, screen: pygame.Surface) -> None:
        """Render panel bounds and information."""
        for panel_id, panel in self.layout_manager.panels.items():
            if not hasattr(panel, 'get_rect'):
                continue

            rect = panel.get_rect()

            # Draw panel bounds
            if self.show_panel_bounds:
                pygame.draw.rect(screen, self.panel_bounds_color[:3], rect, 2)

            # Draw panel info
            if self.show_panel_info:
                self._render_panel_details(screen, panel_id, panel, rect)

    def _render_panel_details(self, screen: pygame.Surface, panel_id: str, panel, rect: pygame.Rect) -> None:
        """Render detailed panel information."""
        # Background for text
        info_surface = pygame.Surface((200, 80))
        info_surface.set_alpha(180)
        info_surface.fill(self.background_color[:3])

        # Panel info text
        lines = [
            f"ID: {panel_id}",
            f"Pos: {rect.x},{rect.y}",
            f"Size: {rect.width}x{rect.height}",
            f"Layer: {self.layout_manager.layer_manager.get_layer(panel)}",
            f"Visible: {getattr(panel, 'visible', True)}"
        ]

        y_offset = 5
        for line in lines:
            text = self.small_font.render(line, True, self.text_color)
            info_surface.blit(text, (5, y_offset))
            y_offset += 12

        # Position info box (top-right of panel, or adjust if off-screen)
        info_x = min(rect.right + 5, self.screen_size[0] - 200)
        info_y = max(rect.top, 0)

        screen.blit(info_surface, (info_x, info_y))

    def _render_collision_boxes(self, screen: pygame.Surface) -> None:
        """Render collision detection visualization."""
        panels = list(self.layout_manager.panels.values())

        for i, panel1 in enumerate(panels):
            if not hasattr(panel1, 'get_rect'):
                continue
            rect1 = panel1.get_rect()

            for j, panel2 in enumerate(panels[i+1:], i+1):
                if not hasattr(panel2, 'get_rect'):
                    continue
                rect2 = panel2.get_rect()

                if rect1.colliderect(rect2):
                    # Draw collision highlight
                    collision_rect = rect1.clip(rect2)
                    collision_surface = pygame.Surface((collision_rect.width, collision_rect.height))
                    collision_surface.set_alpha(150)
                    collision_surface.fill(self.collision_color[:3])
                    screen.blit(collision_surface, (collision_rect.x, collision_rect.y))

                    # Draw collision border
                    pygame.draw.rect(screen, self.collision_color[:3], collision_rect, 3)

    def _render_performance_overlay(self, screen: pygame.Surface) -> None:
        """Render performance metrics overlay."""
        # Background
        overlay_width, overlay_height = 250, 120
        overlay_surface = pygame.Surface((overlay_width, overlay_height))
        overlay_surface.set_alpha(180)
        overlay_surface.fill(self.background_color[:3])

        # Performance metrics
        lines = [
            f"FPS: {self.metrics.fps:.1f}",
            f"Render: {self.metrics.render_time:.2f}ms",
            f"Layout: {self.metrics.layout_time:.2f}ms",
            f"Panels: {self.metrics.panel_count}",
            f"Collisions: {self.metrics.collision_count}",
            f"Grid: {self.layout_manager.grid_config.rows}x{self.layout_manager.grid_config.cols}"
        ]

        y_offset = 5
        for line in lines:
            text = self.font.render(line, True, self.text_color)
            overlay_surface.blit(text, (5, y_offset))
            y_offset += 18

        # Position in top-right corner
        screen.blit(overlay_surface, (self.screen_size[0] - overlay_width - 10, 10))


class PanelInspector:
    """Interactive panel inspector for detailed component analysis."""

    def __init__(self, layout_manager):
        """Initialize panel inspector.

        Args:
            layout_manager: LayoutManager instance to inspect
        """
        self.layout_manager = layout_manager
        self.selected_panel = None
        self.inspect_mode = False
        self.font = pygame.font.SysFont('Arial', 12)

    def toggle_inspect_mode(self) -> None:
        """Toggle panel inspection mode."""
        self.inspect_mode = not self.inspect_mode
        if not self.inspect_mode:
            self.selected_panel = None

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Handle mouse click for panel selection.

        Args:
            pos: Mouse position (x, y)

        Returns:
            True if click was handled by inspector
        """
        if not self.inspect_mode:
            return False

        # Find panel under mouse
        for panel in reversed(self.layout_manager.layer_manager.get_render_order()):
            if hasattr(panel, 'get_rect') and panel.get_rect().collidepoint(pos):
                self.selected_panel = panel
                return True

        self.selected_panel = None
        return True

    def get_inspection_data(self) -> Optional[Dict[str, Any]]:
        """Get detailed data about selected panel.

        Returns:
            Dictionary with panel inspection data, or None if no panel selected
        """
        if not self.selected_panel:
            return None

        panel = self.selected_panel
        rect = panel.get_rect() if hasattr(panel, 'get_rect') else None

        data = {
            "panel_type": type(panel).__name__,
            "position": (rect.x, rect.y) if rect else None,
            "size": (rect.width, rect.height) if rect else None,
            "visible": getattr(panel, 'visible', True),
            "layer": self.layout_manager.layer_manager.get_layer(panel),
            "layout_mode": None,
            "constraints": None
        }

        # Find panel constraints
        for panel_id, constraints in self.layout_manager.panel_constraints.items():
            if self.layout_manager.panels.get(panel_id) is panel:
                data["panel_id"] = panel_id
                data["layout_mode"] = self.layout_manager.panel_modes.get(panel_id)
                data["constraints"] = constraints
                break

        return data

    def render_inspection_overlay(self, screen: pygame.Surface) -> None:
        """Render inspection overlay for selected panel."""
        if not self.inspect_mode or not self.selected_panel:
            return

        data = self.get_inspection_data()
        if not data:
            return

        # Create inspection panel
        panel_width, panel_height = 300, 200
        inspect_surface = pygame.Surface((panel_width, panel_height))
        inspect_surface.set_alpha(220)
        inspect_surface.fill((20, 20, 30))

        # Border
        pygame.draw.rect(inspect_surface, (0, 180, 255), inspect_surface.get_rect(), 2)

        # Title
        title_text = self.font.render("PANEL INSPECTOR", True, (255, 255, 255))
        inspect_surface.blit(title_text, (10, 10))

        # Panel data
        lines = [
            f"Type: {data['panel_type']}",
            f"ID: {data.get('panel_id', 'N/A')}",
            f"Position: {data['position']}",
            f"Size: {data['size']}",
            f"Visible: {data['visible']}",
            f"Layer: {data['layer']}",
            f"Layout Mode: {data['layout_mode']}",
        ]

        y_offset = 35
        for line in lines:
            text = self.font.render(line, True, (220, 220, 220))
            inspect_surface.blit(text, (10, y_offset))
            y_offset += 18

        # Constraints info
        if data['constraints']:
            constraint_text = self.font.render("Constraints:", True, (255, 255, 0))
            inspect_surface.blit(constraint_text, (10, y_offset))
            y_offset += 18

            # Show key constraint properties
            constraint_lines = []
            if hasattr(data['constraints'], 'row'):
                constraint_lines.append(f"Grid: ({data['constraints'].row}, {data['constraints'].col}) {data['constraints'].row_span}x{data['constraints'].col_span}")
            elif hasattr(data['constraints'], 'anchor_point'):
                constraint_lines.append(f"Anchor: {data['constraints'].anchor_point}")

            for line in constraint_lines[:2]:  # Limit to 2 lines
                text = self.font.render(line, True, (200, 200, 200))
                inspect_surface.blit(text, (20, y_offset))
                y_offset += 15

        # Position in bottom-left corner
        screen.blit(inspect_surface, (10, screen.get_height() - panel_height - 10))


class UIDebugSystem:
    """Main UI debug system coordinating all debug tools."""

    def __init__(self, layout_manager, screen_size: Tuple[int, int]):
        """Initialize UI debug system.

        Args:
            layout_manager: LayoutManager instance to debug
            screen_size: Screen dimensions
        """
        self.layout_debug = LayoutDebugOverlay(layout_manager, screen_size)
        self.panel_inspector = PanelInspector(layout_manager)
        self.layout_manager = layout_manager

        # Debug state
        self.enabled = False

    def toggle_debug(self) -> None:
        """Toggle debug system on/off."""
        self.enabled = not self.enabled
        if not self.enabled:
            self.layout_debug.visible = False
            self.panel_inspector.inspect_mode = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle debug system events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled by debug system
        """
        if not self.enabled:
            return False

        # F12: Toggle debug overlay
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
            self.layout_debug.toggle_visibility()
            return True

        # I key: Toggle panel inspector
        if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            self.panel_inspector.toggle_inspect_mode()
            return True

        # G key: Toggle grid
        if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
            self.layout_debug.toggle_grid()
            return True

        # B key: Toggle panel bounds
        if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            self.layout_debug.toggle_panel_bounds()
            return True

        # C key: Toggle collision boxes
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            self.layout_debug.toggle_collision_boxes()
            return True

        # Mouse click in inspect mode
        if event.type == pygame.MOUSEBUTTONDOWN and self.panel_inspector.inspect_mode:
            return self.panel_inspector.handle_click(event.pos)

        return False

    def update_metrics(self, fps: float, render_time: float, layout_time: float) -> None:
        """Update performance metrics."""
        self.layout_debug.update_metrics(fps, render_time, layout_time)

    def render(self, screen: pygame.Surface) -> None:
        """Render all debug overlays."""
        if not self.enabled:
            return

        self.layout_debug.render(screen)
        self.panel_inspector.render_inspection_overlay(screen)

        # Render debug help text
        self._render_debug_help(screen)

    def _render_debug_help(self, screen: pygame.Surface) -> None:
        """Render debug controls help text."""
        if not self.layout_debug.visible and not self.panel_inspector.inspect_mode:
            return

        help_lines = [
            "DEBUG MODE ACTIVE",
            "F12: Toggle Overlay | I: Inspector | G: Grid | B: Bounds | C: Collisions"
        ]

        y_offset = screen.get_height() - 40
        for line in help_lines:
            text = self.layout_debug.small_font.render(line, True, (255, 255, 0))
            screen.blit(text, (10, y_offset))
            y_offset += 15