"""Game User Interface using Pygame - Dashboard Framework.

This module handles all visual rendering and user input for the game.
Uses the new Dashboard Framework with UIProvider architecture.
Legacy panel system has been removed.
"""

import pygame
from typing import List, Optional, Any, Tuple
from dataclasses import dataclass

from src.models.game_state import GameState
from src.utils.logger import GameLogger
from src.ui.theme_manager import ThemeManager
from src.ui.notification_system import NotificationManager
from src.ui.hotkey_manager import HotkeyManager, HotkeyAction
from src.ui.modal_manager import ModalManager
from src.ui.dashboard_manager import DashboardManager
from src.ui.dashboard_panel import DashboardPanel
from src.ui.detail_panel_renderer import DetailPanelRenderer
from src.ui.components.hud_overlay import HUDOverlay
from src.ui.components.quick_reference import QuickReference
from src.core.event_bus import get_event_bus, Event


@dataclass
class GameAction:
    """Represents an action from the UI to the game logic."""
    action_type: str
    data: dict


class GameUI:
    """Main UI class handling Pygame rendering and input.
    
    Uses Dashboard Framework with UIProvider plugins for extensible UI.
    All game systems that want to display information implement UIProvider.
    """

    # Window settings
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    FPS = 60

    def __init__(self, game_state: GameState, system_manager=None):
        """Initialize the game UI.

        Args:
            game_state: The game state to render (read-only)
            system_manager: SystemManager with registered plugins
        """
        self.logger = GameLogger("game_ui")
        self.game_state = game_state
        self.system_manager = system_manager
        self.event_bus = get_event_bus()

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Cybersecurity Firm - Idle/Tycoon/RPG")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 16)

        # Initialize managers
        self.theme_manager = ThemeManager()
        self.notification_manager = NotificationManager(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.hotkey_manager = HotkeyManager()
        
        # Initialize HUD overlay
        self.hud_overlay = HUDOverlay(
            screen_width=self.WINDOW_WIDTH,
            screen_height=self.WINDOW_HEIGHT,
            position="top"
        )
        
        # Initialize quick reference
        self.quick_reference = QuickReference(
            position="bottom-right",
            auto_hide_delay=5.0
        )
        
        # Initialize modal manager for detail panels
        self.modal_manager = ModalManager(
            self.screen,
            self.game_state,
            on_open=None,
            on_close=self._on_detail_panel_close
        )
        
        # Initialize detail panel renderer
        self.detail_panel_renderer = DetailPanelRenderer()
        
        # Initialize dashboard manager and panel
        if self.system_manager:
            self.dashboard_manager = DashboardManager(self.system_manager)
            self.dashboard_panel = DashboardPanel(
                x=10,
                y=60
                # Removed on_widget_clicked callback
            )
            self.logger.info("[GAME_UI] Dashboard initialized with system plugins")
        else:
            self.dashboard_manager = None
            self.dashboard_panel = None
            self.logger.warning("[GAME_UI] No system_manager provided - dashboard disabled")
        
        # Initialize gameplay panels (NEW - management sim style layout)
        from src.ui.panels import SpecialistRosterPanel, IncidentQueuePanel
        
        # Specialist roster panel (top half of main area)
        self.specialist_roster = SpecialistRosterPanel(
            x=230,  # After dashboard
            y=60,   # Below HUD
            width=1040,
            height=300
        )
        
        # Incident queue panel (bottom half of main area)
        self.incident_queue = IncidentQueuePanel(
            x=230,
            y=370,  # Below roster
            width=1040,
            height=340
        )
        
        # Set up assignment workflow callbacks
        self.specialist_roster.set_selection_callback(self._on_specialist_selected)
        self.incident_queue.set_selection_callback(self._on_incident_selected)
        
        # Track current selections for assignment
        self.selected_specialist_id: Optional[str] = None
        self.selected_incident_id: Optional[str] = None

        # Register hotkeys
        self._register_hotkey_callbacks()

        # Register Event Bus subscriptions
        self.event_bus.subscribe("ui_dashboard_widget_clicked", self._on_dashboard_widget_clicked)

        # UI state
        self.show_help_overlay = False
        self.running = True
        
        # Detail panel state
        self.detail_panel_open = False
        self.detail_panel_plugin = None
        self.detail_panel_data = None
        self.detail_panel_rect = pygame.Rect(
            (self.WINDOW_WIDTH - 700) // 2,
            (self.WINDOW_HEIGHT - 500) // 2,
            700,
            500
        )

        self.logger.info("[GAME_UI] Game UI initialized (Dashboard Framework)")

    def _register_hotkey_callbacks(self) -> None:
        """Register hotkey callbacks."""
        self.hotkey_manager.register_callback(
            HotkeyAction.PAUSE_TOGGLE,
            lambda: self._toggle_pause()
        )

    def _toggle_pause(self) -> None:
        """Publish event to toggle game pause state."""
        # ANTI-PATTERN (Removed): self.game_state.is_paused = not self.game_state.is_paused
        # The UI should not modify state directly. It publishes an event.
        # A core game system (e.g., GameLoopPlugin) will listen for this
        # and update the state, which the UI will then read.
        if self.game_state.is_paused:
            self.event_bus.publish("game_resumed", {}, source="game_ui")
        else:
            self.event_bus.publish("game_paused", {}, source="game_ui")
        
        # ANTI-PATTERN (Removed): self.notification_manager.show_info(...)
        # The notification system should listen for "game_paused" and
        # "game_resumed" events to show its own notifications.

    def _on_dashboard_widget_clicked(self, event: Event) -> None:
        """Handle dashboard widget click to open detail panel.
        
        Args:
            event: Event containing the plugin_name
        """
        if not self.dashboard_manager:
            return
        
        plugin_name = event.data.get("plugin_name")
        if not plugin_name:
            self.logger.warning("[GAME_UI] Received ui_dashboard_widget_clicked event with no plugin_name")
            return

        self.logger.debug(f"[GAME_UI] Dashboard widget clicked: {plugin_name}")
        
        # Get detail panel data from dashboard manager
        detail_data = self.dashboard_manager.get_detail_panel_data(
            plugin_name,
            self.game_state
        )
        
        if detail_data:
            # Open detail panel
            self.detail_panel_open = True
            self.detail_panel_plugin = plugin_name
            self.detail_panel_data = detail_data
            self.dashboard_manager.set_expanded_panel(plugin_name)
            
            self.logger.debug(f"[GAME_UI] Detail panel opened for {plugin_name}")
        else:
            self.logger.warning(f"[GAME_UI] No detail data for {plugin_name}")
    
    def _on_detail_panel_close(self) -> None:
        """Handle detail panel close."""
        self.detail_panel_open = False
        self.detail_panel_plugin = None
        self.detail_panel_data = None
        
        if self.dashboard_manager:
            self.dashboard_manager.close_panel()
        
        self.logger.debug("[GAME_UI] Detail panel closed")
    
    def _on_specialist_selected(self, specialist_id: str):
        """Handle specialist selection from roster panel.
        
        Args:
            specialist_id: ID of selected specialist
        """
        self.selected_specialist_id = specialist_id
        self.logger.info(f"[GAME_UI] Specialist selected: {specialist_id}")
        
        # If both specialist and incident are selected, perform assignment
        if self.selected_incident_id:
            self._attempt_assignment()
    
    def _on_incident_selected(self, incident_id: str):
        """Handle incident selection from queue panel.
        
        Args:
            incident_id: ID of selected incident
        """
        self.selected_incident_id = incident_id
        self.logger.info(f"[GAME_UI] Incident selected: {incident_id}")
        
        # If both specialist and incident are selected, perform assignment
        if self.selected_specialist_id:
            self._attempt_assignment()
    
    def _attempt_assignment(self):
        """Attempt to assign selected specialist to selected incident."""
        if not self.selected_specialist_id or not self.selected_incident_id:
            return
        
        self.logger.info(
            f"[GAME_UI] Attempting assignment: "
            f"specialist={self.selected_specialist_id}, "
            f"incident={self.selected_incident_id}"
        )
        
        # Publish assignment event
        self.event_bus.publish("action:assign_incident", {
            "specialist_id": self.selected_specialist_id,
            "incident_id": self.selected_incident_id,
            "game_state": self.game_state
        }, source="game_ui")
        
        # Clear selections
        self.selected_specialist_id = None
        self.selected_incident_id = None
        self.specialist_roster.clear_selection()
        self.incident_queue.clear_selection()
        
        # Show feedback
        self.notification_manager.show_success("Assignment attempted!")

    def handle_input(self, events: List[pygame.event.Event]) -> None:
        """Process input events. Game actions are published via EventBus.

        Args:
            events: List of Pygame events
        """
        for event in events:
            # Modal manager gets first priority
            if self.modal_manager.handle_event(event):
                continue
            
            # Detail panel gets next priority
            if self.detail_panel_open:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check if click is on detail panel
                    if self.detail_panel_rect.collidepoint(event.pos):
                        # Let detail panel renderer handle it
                        if self.detail_panel_renderer.handle_click(
                            event.pos,
                            self.detail_panel_rect
                        ):
                            # Action button clicked, keep panel open
                            continue
                        # Check if close button clicked (handled internally)
                        # Close button is in top-right corner
                        close_x = self.detail_panel_rect.x + self.detail_panel_rect.width - 40
                        close_y = self.detail_panel_rect.y + 10
                        close_rect = pygame.Rect(close_x, close_y, 30, 30)
                        if close_rect.collidepoint(event.pos):
                            self._on_detail_panel_close()
                            continue
                    else:
                        # Click outside panel - close it
                        self._on_detail_panel_close()
                        continue
                
                elif event.type == pygame.MOUSEMOTION:
                    # Update hover state
                    self.detail_panel_renderer.update_hover(
                        event.pos,
                        self.detail_panel_rect
                    )
                    continue

            # Handle window resize
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize((event.w, event.h))
                continue
            
            # Handle gameplay panel interactions (specialist roster & incident queue)
            if self.specialist_roster.handle_event(event):
                continue
            if self.incident_queue.handle_event(event):
                continue

            # Handle dashboard widget interactions
            if self.dashboard_panel:
                # Handle both clicks and hover
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check if a widget was clicked
                    for widget in self.dashboard_panel.widgets:
                        if widget.rect.collidepoint(event.pos):
                            # Publish event to open detail panel
                            self.event_bus.publish("ui_dashboard_widget_clicked", {
                                "plugin_name": widget.plugin_name
                            }, source="game_ui")
                            continue
                elif event.type == pygame.MOUSEMOTION:
                    self.dashboard_panel.update_hover()

            # Handle hotkeys
            if self.hotkey_manager.handle_key_event(event):
                continue

            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    self.show_help_overlay = not self.show_help_overlay
                    if not self.show_help_overlay:
                        self.quick_reference.toggle()
                elif event.key == pygame.K_ESCAPE:
                    # Close detail panel or exit
                    if self.detail_panel_open:
                        self._on_detail_panel_close()
                    elif self.modal_manager.is_modal_open():
                        self.modal_manager.close_modal()
                    else:
                        self.running = False
        
        # No actions are returned; they are published via event_bus
        return

    def handle_resize(self, new_size: Tuple[int, int]) -> None:
        """Handle window resize event.
        
        Args:
            new_size: New window size (width, height)
        """
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = new_size
        self.screen = pygame.display.set_mode(new_size)
        
        # Update HUD
        self.hud_overlay = HUDOverlay(
            screen_width=self.WINDOW_WIDTH,
            screen_height=self.WINDOW_HEIGHT,
            position="top"
        )
        
        # Update quick reference
        self.quick_reference = QuickReference(
            position="bottom-right",
            auto_hide_delay=5.0
        )

    def update(self, delta_time: float) -> None:
        """Update UI state.

        Args:
            delta_time: Time elapsed since last update
        """
        # Update HUD overlay
        self.hud_overlay.update(delta_time, self.game_state)
        
        # Update quick reference
        self.quick_reference.update(delta_time)
        
        # Update modal manager
        self.modal_manager.update(delta_time)
        
        # Update notification manager
        self.notification_manager.update(delta_time, self.game_state)

    def render(self) -> None:
        """Render the game UI."""
        # Get background color from theme
        bg_color = self.theme_manager.get_color("background", (15, 15, 25))
        self.screen.fill(bg_color)

        # Render HUD overlay
        self.hud_overlay.render(self.screen, self.game_state, "Dashboard")
        
        # Render dashboard panel (left sidebar with UIProvider summaries)
        if self.dashboard_panel and self.dashboard_manager:
            # Set managers if not already set
            if not self.dashboard_panel.dashboard_manager:
                self.dashboard_panel.set_managers(self.dashboard_manager, self.game_state)
            self.dashboard_panel.draw(self.screen, self.game_state)
        
        # Render gameplay panels (main area - management sim style)
        # Get unassigned incidents and specialists
        unassigned_incidents = [
            inc for inc in self.game_state.incidents 
            if not hasattr(inc, 'assigned_specialist_id') or inc.assigned_specialist_id is None
        ]
        
        # Render specialist roster panel (top)
        self.specialist_roster.draw(self.screen, self.game_state.specialists)
        
        # Render incident queue panel (bottom)
        self.incident_queue.draw(self.screen, unassigned_incidents, self.game_state)
        
        # Render quick reference card
        self.quick_reference.render(self.screen)
        
        # Render detail panel if open
        if self.detail_panel_open and self.detail_panel_data:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Render detail panel
            self.detail_panel_renderer.render(
                self.screen,
                self.detail_panel_data,
                self.detail_panel_rect.x,
                self.detail_panel_rect.y,
                on_close=self._on_detail_panel_close
            )

        # Render modals on top of everything
        self.modal_manager.draw()

        # Render notifications (always on top)
        self.notification_manager.render(self.screen)

        # Render help overlay if active
        if self.show_help_overlay:
            self._render_help_overlay()

        # Update display
        pygame.display.flip()

    def _render_help_overlay(self) -> None:
        """Render help overlay with hotkeys."""
        # Semi-transparent overlay
        overlay = pygame.Surface((400, 300))
        overlay.set_alpha(220)
        overlay.fill((30, 30, 40))

        # Position in center
        overlay_x = (self.WINDOW_WIDTH - 400) // 2
        overlay_y = (self.WINDOW_HEIGHT - 300) // 2

        # Title
        title_font = pygame.font.SysFont('Arial', 18, bold=True)
        title_text = title_font.render("Hotkey Reference", True, (255, 255, 255))
        overlay.blit(title_text, (20, 20))

        # Hotkeys
        help_font = pygame.font.SysFont('Arial', 14)
        hotkeys = [
            ("H", "Toggle This Help"),
            ("ESC", "Close Modal / Exit"),
            ("SPACE", "Pause/Resume Game"),
            ("", ""),
            ("Dashboard:", ""),
            ("Click widget", "Open detail panel"),
            ("", ""),
            ("🏢 Clients plugin shows real data", ""),
        ]

        y_offset = 60
        for key, description in hotkeys:
            if key and description:
                text = help_font.render(f"{key:12s} - {description}", True, (220, 220, 220))
            elif description:
                text = help_font.render(description, True, (180, 180, 200))
            else:
                continue
            overlay.blit(text, (20, y_offset))
            y_offset += 22

        # Draw border
        pygame.draw.rect(overlay, (0, 180, 255), overlay.get_rect(), 2, border_radius=4)

        self.screen.blit(overlay, (overlay_x, overlay_y))

    def set_screenshot_utility(self, screenshot_utility) -> None:
        """Set the screenshot utility for hotkey callbacks.
        
        Args:
            screenshot_utility: The screenshot utility instance
        """
        self.screenshot_utility = screenshot_utility

    def shutdown(self) -> None:
        """Clean shutdown of UI systems."""
        self.logger.info("[GAME_UI] Shutting down game UI")
        pygame.quit()