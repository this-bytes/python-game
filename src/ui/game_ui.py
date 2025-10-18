"""Game User Interface using Pygame.

This module handles all visual rendering and user input for the game.
Following the architecture principle: Pygame renders, it doesn't think.
"""

import pygame
from typing import List, Optional, Any
from dataclasses import dataclass

from src.models.game_state import GameState
from src.utils.logger import GameLogger
from src.ui.theme_manager import ThemeManager
from src.ui.notification_system import NotificationManager
from src.ui.hotkey_manager import HotkeyManager, HotkeyAction
from src.ui.panels.specialist_roster_panel import SpecialistRosterPanel
from src.ui.panels.incident_queue_panel import IncidentQueuePanel
from src.ui.panels.metrics_panel import MetricsPanel
from src.ui.panels.equipment_shop_panel import EquipmentShopPanel
from src.ui.panels.equipment_inventory_panel import EquipmentInventoryPanel
from src.ui.components.button import Button, ButtonStyle
from src.ui.dopamine_overlay import DopamineFeedbackOverlay
from src.ui.synergy_overlay import SynergySuggestionOverlay, AutoPlayIndicator
from src.ui.components.navigation_menu import NavigationMenu, MenuItem, MenuPosition
from src.ui.view_manager import ViewManager, GameView, create_default_views


@dataclass
class GameAction:
    """Represents an action from the UI to the game logic."""
    action_type: str
    data: dict


class GameUI:
    """Main UI class handling Pygame rendering and input."""

    # Window settings
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    FPS = 60

    def __init__(self, game_state: GameState):
        """Initialize the game UI.

        Args:
            game_state: The game state to render
        """
        self.logger = GameLogger("game_ui")
        self.game_state = game_state

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 16)

        # Initialize managers
        self.theme_manager = ThemeManager()
        self.notification_manager = NotificationManager(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.hotkey_manager = HotkeyManager()
        
        # Initialize dopamine feedback overlay for addictive gameplay
        self.dopamine_overlay = DopamineFeedbackOverlay(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        
        # Initialize synergy overlay for STRATEGIC DEPTH (Balatro-style)
        self.synergy_overlay = SynergySuggestionOverlay(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.autoplay_indicator = AutoPlayIndicator()

        # Register hotkey callbacks
        self._register_hotkey_callbacks()

        # Initialize panels
        self.specialist_roster_panel = SpecialistRosterPanel(self.game_state)
        self.incident_queue_panel = IncidentQueuePanel(self.game_state)
        self.metrics_panel = MetricsPanel(self.game_state)
        self.equipment_shop_panel = EquipmentShopPanel(self.game_state)
        self.equipment_inventory_panel = EquipmentInventoryPanel(self.game_state)

        # Apply theme to panels
        self._apply_theme_to_panels()

        # Panels list for z-order management
        self.panels = [
            self.specialist_roster_panel,
            self.incident_queue_panel,
            self.metrics_panel,
            self.equipment_shop_panel,
            self.equipment_inventory_panel,
        ]
        
        # Initialize navigation menu
        menu_items = [
            MenuItem("overview", "Overview", "📊", "Game dashboard and key metrics", pygame.K_F1),
            MenuItem("operations", "Operations", "⚡", "Incidents & Specialists", pygame.K_F2),
            MenuItem("management", "Management", "🏢", "Equipment & Facilities", pygame.K_F3),
            MenuItem("analytics", "Analytics", "📈", "Metrics & Achievements", pygame.K_F4),
        ]
        
        self.navigation_menu = NavigationMenu(
            items=menu_items,
            position=MenuPosition.LEFT,
            on_item_selected=self._on_menu_item_selected
        )
        
        # Initialize view manager
        panel_dict = {
            "specialist_roster": self.specialist_roster_panel,
            "incident_queue": self.incident_queue_panel,
            "metrics": self.metrics_panel,
            "equipment_shop": self.equipment_shop_panel,
            "equipment_inventory": self.equipment_inventory_panel,
        }
        
        self.view_manager = ViewManager(
            views=create_default_views(self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
            panels=panel_dict,
            initial_view=GameView.OPERATIONS,  # Start with operations view
            on_view_changed=self._on_view_changed
        )

        # Create assign button
        self.assign_button = Button(
            text="Assign Specialist",
            position=(20, 600),
            size=(200, 40),
            callback=self._handle_assign_button,
            style=ButtonStyle.PRIMARY,
            enabled=False,
        )

        # UI state
        self.show_help_overlay = False
        
        # Drag and drop state
        self.dragged_incident = None
        self.drag_offset = (0, 0)
        self.drag_highlight_specialist = None

        self.logger.logger.info("[GAME_UI] Game UI initialized with drag-and-drop support")
    
    def _on_menu_item_selected(self, item_id: str) -> None:
        """Handle menu item selection.
        
        Args:
            item_id: ID of selected menu item
        """
        # Map menu item IDs to views
        view_map = {
            "overview": GameView.OVERVIEW,
            "operations": GameView.OPERATIONS,
            "management": GameView.MANAGEMENT,
            "analytics": GameView.ANALYTICS,
        }
        
        if item_id in view_map:
            self.view_manager.switch_to_view(view_map[item_id])
    
    def _on_view_changed(self, view_config) -> None:
        """Handle view change.
        
        Args:
            view_config: Configuration of new view
        """
        self.notification_manager.show_info("View", f"Switched to {view_config.title}")
        self.logger.logger.info(f"[GAME_UI] Switched to view: {view_config.title}")

    def _register_hotkey_callbacks(self) -> None:
        """Register hotkey callbacks."""
        self.hotkey_manager.register_callback(
            HotkeyAction.PAUSE_TOGGLE,
            lambda: self._toggle_pause()
        )
        self.hotkey_manager.register_callback(
            HotkeyAction.TOGGLE_SPECIALIST_PANEL,
            lambda: self._toggle_panel(self.specialist_roster_panel)
        )
        self.hotkey_manager.register_callback(
            HotkeyAction.TOGGLE_INCIDENT_PANEL,
            lambda: self._toggle_panel(self.incident_queue_panel)
        )
        self.hotkey_manager.register_callback(
            HotkeyAction.TOGGLE_METRICS_PANEL,
            lambda: self._toggle_panel(self.metrics_panel)
        )
        self.hotkey_manager.register_callback(
            HotkeyAction.TOGGLE_SHOP_PANEL,
            lambda: self._toggle_panel(self.equipment_shop_panel)
        )
        self.hotkey_manager.register_callback(
            HotkeyAction.TOGGLE_INVENTORY_PANEL,
            lambda: self._toggle_panel(self.equipment_inventory_panel)
        )
        self.hotkey_manager.register_callback(
            HotkeyAction.TOGGLE_INCIDENT_PANEL,
            lambda: self._toggle_panel(self.incident_queue_panel)
        )
        self.hotkey_manager.register_callback(
            HotkeyAction.TOGGLE_METRICS_PANEL,
            lambda: self._toggle_panel(self.metrics_panel)
        )

    def _apply_theme_to_panels(self) -> None:
        """Apply current theme to all panels."""
        theme = self.theme_manager.get_current_theme()
        if theme:
            theme_dict = {"colors": theme.colors}
            self.specialist_roster_panel.set_theme_colors(theme_dict)
            self.incident_queue_panel.set_theme_colors(theme_dict)
            self.metrics_panel.set_theme_colors(theme_dict)
            self.equipment_shop_panel.set_theme_colors(theme_dict)
            self.equipment_inventory_panel.set_theme_colors(theme_dict)

    def _toggle_pause(self) -> None:
        """Toggle game pause state."""
        self.game_state.is_paused = not self.game_state.is_paused
        status = "paused" if self.game_state.is_paused else "resumed"
        self.notification_manager.show_info("Game", f"Game {status}")

    def _toggle_panel(self, panel) -> None:
        """Toggle panel visibility."""
        panel.visible = not panel.visible

    def _handle_assign_button(self) -> None:
        """Handle assign button click."""
        specialist = self.specialist_roster_panel.get_selected_specialist()
        incident = self.incident_queue_panel.get_selected_incident()

        if specialist and incident:
            # Try to assign
            success = self.game_state.assign_incident_to_specialist(incident.id, specialist.id)
            if success:
                self.notification_manager.show_success(
                    "Assignment",
                    f"{specialist.name} assigned to {incident.incident_type}"
                )
            else:
                self.notification_manager.show_error(
                    "Assignment Failed",
                    "Could not assign specialist to incident"
                )

    def handle_input(self, events: List[pygame.event.Event]) -> List[GameAction]:
        """Process input events and return game actions.

        Args:
            events: List of Pygame events

        Returns:
            List of game actions to process
        """
        actions = []

        for event in events:
            # Handle navigation menu first
            if self.navigation_menu.handle_event(event, self.WINDOW_WIDTH, self.WINDOW_HEIGHT):
                continue
            
            # Handle drag and drop events (before panels)
            if self._handle_drag_drop_event(event):
                continue

            # Handle hotkeys
            if self.hotkey_manager.handle_key_event(event):
                continue

            # Handle panel events (in reverse z-order) - only if visible
            event_consumed = False
            for panel in reversed(self.panels):
                if hasattr(panel, 'visible') and not panel.visible:
                    continue
                    
                if panel.handle_event(event):
                    # Bring panel to front if clicked
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.panels.remove(panel)
                        self.panels.append(panel)
                    event_consumed = True
                    break

            if event_consumed:
                continue

            # Handle button events
            if self.assign_button.handle_event(event):
                continue

            # Handle other inputs
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    self.show_help_overlay = not self.show_help_overlay
                elif event.key == pygame.K_s:
                    # Toggle synergy suggestions panel (strategic intervention UI)
                    self.synergy_overlay.toggle_visibility()
                elif event.key == pygame.K_ESCAPE:
                    # Go back to previous view
                    self.view_manager.go_back()
                elif event.key == pygame.K_a:
                    # Assign selected incident to selected specialist
                    selected_incident = self.incident_queue_panel.get_selected_incident()
                    selected_specialist = self.specialist_roster_panel.get_selected_specialist()
                    
                    if selected_incident and selected_specialist:
                        success = self.game_state.assign_incident_to_specialist(
                            selected_incident.id, 
                            selected_specialist.id
                        )
                        if success:
                            self.notification_manager.show_success(
                                "Assignment Complete", 
                                f"{selected_specialist.name} assigned to {selected_incident.incident_type}"
                            )
                        else:
                            self.notification_manager.show_error(
                                "Assignment Failed", 
                                "Specialist unavailable or specialty mismatch"
                            )
                    elif not selected_incident:
                        self.notification_manager.show_warning("Assignment", "Select an incident first")
                    elif not selected_specialist:
                        self.notification_manager.show_warning("Assignment", "Select a specialist first")


        return actions

    def _handle_drag_drop_event(self, event: pygame.event.Event) -> bool:
        """Handle drag and drop events for cross-panel incident assignment.

        Args:
            event: Pygame event

        Returns:
            True if event was consumed by drag-drop handling
        """
        # Start drag from incident panel
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.incident_queue_panel.get_rect().collidepoint(event.pos):
                # Let incident panel handle the drag start
                if self.incident_queue_panel.handle_event(event):
                    self.dragged_incident = self.incident_queue_panel.dragged_incident
                    self.drag_offset = self.incident_queue_panel.drag_offset
                    return True

        # Handle drag motion (highlight drop targets)
        elif event.type == pygame.MOUSEMOTION and self.dragged_incident:
            # Check if mouse is over specialist panel
            if self.specialist_roster_panel.get_rect().collidepoint(event.pos):
                # Calculate which specialist is being hovered
                rect = self.specialist_roster_panel.get_rect()
                content_rect = pygame.Rect(
                    rect.x + self.specialist_roster_panel.BORDER_WIDTH,
                    rect.y + self.specialist_roster_panel.TITLE_BAR_HEIGHT + self.specialist_roster_panel.BORDER_WIDTH,
                    rect.width - 2 * self.specialist_roster_panel.BORDER_WIDTH,
                    rect.height - self.specialist_roster_panel.TITLE_BAR_HEIGHT - 2 * self.specialist_roster_panel.BORDER_WIDTH
                )

                if content_rect.collidepoint(event.pos):
                    y_offset = content_rect.y - self.specialist_roster_panel.scroll_container.get_scroll_offset()
                    for specialist in self.game_state.specialists:
                        card_rect = pygame.Rect(
                            content_rect.x + self.specialist_roster_panel.card_margin,
                            y_offset,
                            content_rect.width - self.specialist_roster_panel.card_margin * 2 - self.specialist_roster_panel.scroll_container.scroll_bar_width,
                            self.specialist_roster_panel.card_height
                        )

                        if card_rect.collidepoint(event.pos):
                            self.drag_highlight_specialist = specialist.id
                            return True

                        y_offset += self.specialist_roster_panel.card_height + self.specialist_roster_panel.card_margin
            
            self.drag_highlight_specialist = None
            return True

        # Handle drop (mouse button up)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragged_incident:
            if self.drag_highlight_specialist:
                # Attempt assignment
                success = self.game_state.assign_incident_to_specialist(
                    self.dragged_incident.id, self.drag_highlight_specialist
                )
                if success:
                    self.notification_manager.show_success(
                        "Assignment Complete",
                        f"Incident assigned via drag-and-drop"
                    )
                else:
                    self.notification_manager.show_error(
                        "Assignment Failed",
                        "Specialist unavailable or specialty mismatch"
                    )
            
            # Clear drag state
            self.dragged_incident = None
            self.drag_offset = (0, 0)
            self.drag_highlight_specialist = None
            # Also clear in incident panel
            self.incident_queue_panel.dragged_incident = None
            self.incident_queue_panel.drag_offset = (0, 0)
            return True

        return False

    def update(self, delta_time: float) -> None:
        """Update UI state.

        Args:
            delta_time: Time elapsed since last update
        """
        # Update view manager
        self.view_manager.update(delta_time)
        
        # Update navigation menu
        self.navigation_menu.update(delta_time)
        
        # Update notification manager
        self.notification_manager.update(delta_time)
        
        # Update dopamine overlay with feedback from game state
        self.dopamine_overlay.process_feedback(
            self.game_state.dopamine_feedback_queue,
            self.game_state._dopamine_system
        )
        self.dopamine_overlay.update(delta_time)
        
        # Update synergy overlay with strategic suggestions (IDLE GAME DEPTH)
        if hasattr(self.game_state, '_idle_core') and self.game_state._idle_core:
            self.synergy_overlay.update_suggestions(
                self.game_state._idle_core,
                self.game_state
            )

        # Update button enabled state
        specialist = self.specialist_roster_panel.get_selected_specialist()
        incident = self.incident_queue_panel.get_selected_incident()
        self.assign_button.set_enabled(specialist is not None and incident is not None)

    def render(self) -> None:
        """Render the game UI."""
        # Get background color from theme
        bg_color = self.theme_manager.get_color("background", (15, 15, 25))
        self.screen.fill(bg_color)

        # Render main header
        self._render_header()
        
        # Render navigation menu
        self.navigation_menu.render(self.screen, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # Render all visible panels (in z-order)
        for panel in self.panels:
            if hasattr(panel, 'visible') and panel.visible:
                panel.render(self.screen)

        # Render controls (only show assign button in operations view)
        current_view = self.view_manager.current_view
        if current_view == GameView.OPERATIONS:
            self._render_controls()
        
        # Render AUTO-PLAY INDICATOR (always visible - core idle mechanic)
        if hasattr(self.game_state, '_idle_core') and self.game_state._idle_core:
            self.autoplay_indicator.render(
                self.screen,
                self.game_state._idle_core,
                self.WINDOW_WIDTH
            )
        
        # Render SYNERGY SUGGESTIONS (strategic depth UI)
        if hasattr(self.game_state, '_idle_core') and self.game_state._idle_core:
            num_suggestions = len(self.synergy_overlay.suggestions)
            if self.synergy_overlay.visible:
                self.synergy_overlay.render(self.screen)
            else:
                # Show compact indicator when panel hidden but suggestions exist
                self.synergy_overlay.render_compact_indicator(self.screen, num_suggestions)
        
        # Render dopamine overlay (combo counter, celebrations, risk contracts)
        self.dopamine_overlay.render(self.screen, self.game_state._dopamine_system)

        # Render drag and drop visual feedback (only in operations view)
        if current_view == GameView.OPERATIONS:
            self._render_drag_drop()
        
        # Render view transition overlay
        self.view_manager.render_transition_overlay(self.screen)

        # Render notifications (always on top)
        self.notification_manager.render(self.screen)

        # Render help overlay if active
        if self.show_help_overlay:
            self._render_help_overlay()

        # Update display
        pygame.display.flip()

    def _render_drag_drop(self) -> None:
        """Render drag and drop visual feedback."""
        if not self.dragged_incident:
            return

        # Render dragged incident preview
        mouse_x, mouse_y = pygame.mouse.get_pos()
        drag_x = mouse_x - self.drag_offset[0]
        drag_y = mouse_y - self.drag_offset[1]
        
        # Create semi-transparent dragged card
        card_width = 120  # Compact preview size
        card_height = 60
        dragged_rect = pygame.Rect(drag_x, drag_y, card_width, card_height)
        
        # Semi-transparent background
        drag_surface = pygame.Surface((card_width, card_height))
        drag_surface.set_alpha(220)
        drag_surface.fill((40, 60, 80))
        
        # Border
        pygame.draw.rect(drag_surface, (0, 180, 255), drag_surface.get_rect(), 2, border_radius=4)
        
        # Incident info (compact)
        if self.small_font:
            type_text = self.small_font.render(self.dragged_incident.incident_type[:15], True, (255, 255, 255))
            drag_surface.blit(type_text, (8, 8))
            
            specialty_text = self.small_font.render(self.dragged_incident.specialty_required, True, (150, 150, 200))
            drag_surface.blit(specialty_text, (8, 28))
        
        # Render to screen
        self.screen.blit(drag_surface, (drag_x, drag_y))

        # Render drop highlight if hovering over specialist
        if self.drag_highlight_specialist:
            # Find the highlighted specialist's card position
            rect = self.specialist_roster_panel.get_rect()
            content_rect = pygame.Rect(
                rect.x + self.specialist_roster_panel.BORDER_WIDTH,
                rect.y + self.specialist_roster_panel.TITLE_BAR_HEIGHT + self.specialist_roster_panel.BORDER_WIDTH,
                rect.width - 2 * self.specialist_roster_panel.BORDER_WIDTH,
                rect.height - self.specialist_roster_panel.TITLE_BAR_HEIGHT - 2 * self.specialist_roster_panel.BORDER_WIDTH
            )

            y_offset = content_rect.y - self.specialist_roster_panel.scroll_container.get_scroll_offset()
            for specialist in self.game_state.specialists:
                if specialist.id == self.drag_highlight_specialist:
                    card_rect = pygame.Rect(
                        content_rect.x + self.specialist_roster_panel.card_margin,
                        y_offset,
                        content_rect.width - self.specialist_roster_panel.card_margin * 2 - self.specialist_roster_panel.scroll_container.scroll_bar_width,
                        self.specialist_roster_panel.card_height
                    )
                    
                    # Draw highlight border around target specialist
                    highlight_color = (0, 255, 100)  # Green highlight for valid drop
                    pygame.draw.rect(self.screen, highlight_color, card_rect, 3, border_radius=6)
                    break

                y_offset += self.specialist_roster_panel.card_height + self.specialist_roster_panel.card_margin

    def _render_header(self) -> None:
        """Render the game header with basic info."""
        header_height = 60
        header_rect = pygame.Rect(0, 0, self.WINDOW_WIDTH, header_height)
        
        # Get colors from theme
        primary_color = self.theme_manager.get_color("primary", (0, 180, 255))
        text_color = self.theme_manager.get_color("text", (220, 220, 230))
        
        pygame.draw.rect(self.screen, primary_color, header_rect)

        # Title
        title_text = self.font.render("Cybersecurity Firm - Idle/Tycoon/RPG", True, text_color)
        self.screen.blit(title_text, (20, 15))

        # Money
        money_text = self.font.render(f"Money: ${self.game_state.current_money:,.0f}", True, text_color)
        self.screen.blit(money_text, (self.WINDOW_WIDTH - 300, 15))

        # Time and pause status
        time_text = f"Time: {self.game_state.get_game_time_elapsed():.1f}s"
        if self.game_state.is_paused:
            time_text += " [PAUSED]"
        time_surface = self.font.render(time_text, True, text_color)
        self.screen.blit(time_surface, (self.WINDOW_WIDTH - 300, 35))

    def _render_controls(self) -> None:
        """Render control buttons and instructions."""
        # Render assign button
        self.assign_button.render(self.screen)

        # Instructions - simplified and cleaner
        text_color = self.theme_manager.get_color("text", (220, 220, 230))
        
        instructions = [
            "Navigation: F1-F4 to switch views | ESC to go back | H for help",
            "🎯 Operations: Select incident + specialist, press A to assign or drag & drop",
        ]

        y_offset = 665
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, text_color)
            self.screen.blit(inst_text, (240, y_offset))
            y_offset += 18

    def _render_help_overlay(self) -> None:
        """Render help overlay with all hotkeys."""
        # Semi-transparent overlay
        overlay = pygame.Surface((400, 400))
        overlay.set_alpha(220)
        overlay.fill((30, 30, 40))

        # Position in center
        overlay_x = (self.WINDOW_WIDTH - 400) // 2
        overlay_y = (self.WINDOW_HEIGHT - 400) // 2

        # Title
        title_font = pygame.font.SysFont('Arial', 18, bold=True)
        title_text = title_font.render("Hotkey Reference", True, (255, 255, 255))
        overlay.blit(title_text, (20, 20))

        # Hotkeys
        help_font = pygame.font.SysFont('Arial', 14)
        hotkeys = [
            ("F1", "Overview Dashboard"),
            ("F2", "Operations View"),
            ("F3", "Management View"),
            ("F4", "Analytics View"),
            ("ESC", "Back to Previous View"),
            ("1", "Toggle Specialist Roster"),
            ("2", "Toggle Incident Queue"),
            ("3", "Toggle Metrics Panel"),
            ("A", "Assign Selected Incident to Specialist"),
            ("S", "Toggle Synergy Suggestions"),
            ("SPACE", "Pause/Resume Game"),
            ("+", "Increase Game Speed"),
            ("-", "Decrease Game Speed"),
            ("H", "Toggle This Help"),
        ]

        y_offset = 60
        for key, description in hotkeys:
            key_text = help_font.render(f"{key:10s} - {description}", True, (220, 220, 220))
            overlay.blit(key_text, (20, y_offset))
            y_offset += 25

        # Draw border
        pygame.draw.rect(overlay, (0, 180, 255), overlay.get_rect(), 2, border_radius=4)

        self.screen.blit(overlay, (overlay_x, overlay_y))

    def shutdown(self) -> None:
        """Clean shutdown of UI systems."""
        self.logger.logger.info("[GAME_UI] Shutting down game UI")
