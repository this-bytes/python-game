"""Game User Interface using Pygame.

This module handles all visual rendering and user input for the game.
Following the architecture principles of separation of concerns.
"""

import pygame
from typing import List, Optional, Any, Tuple
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
from src.ui.panels.automation_builder_panel import AutomationBuilderPanel
from src.ui.panels.progressive_difficulty_panel import ProgressiveDifficultyPanel
from src.ui.panels.skill_tree_panel import SkillTreePanel
from src.ui.panels.team_dynamics_panel import TeamDynamicsPanel
from src.ui.panels.economy_panel import EconomyPanel
from src.ui.components.button import Button, ButtonStyle
from src.ui.dopamine_overlay import DopamineFeedbackOverlay
from src.ui.synergy_overlay import SynergySuggestionOverlay, AutoPlayIndicator
from src.ui.player_engagement import EngagementManager
from src.ui.components.navigation_menu import NavigationMenu, MenuItem, MenuPosition
from src.ui.components.hud_overlay import HUDOverlay
from src.ui.components.quick_reference import QuickReference
from src.ui.view_manager import ViewManager, GameView, create_default_views
from src.ui.layout_manager import LayoutManager, GridConfig, GridConstraints, AnchorConstraints, LayerManager, LayoutMode
from src.ui.panel_inspector import PanelInspector
from src.ui.layout_validator import validate_layout
from src.ui.debug_overlay import LayoutDebugOverlay, DebugOverlayMode
from src.ui.drag_drop_manager import get_drag_drop_manager
from src.ui.modal_manager import ModalManager
from src.ui.dashboard_manager import DashboardManager
from src.ui.dashboard_panel import DashboardPanel
from src.ui import event_types


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

    def __init__(self, game_state: GameState, system_manager=None):
        """Initialize the game UI.

        Args:
            game_state: The game state to render
            system_manager: Optional SystemManager for dashboard integration
        """
        self.logger = GameLogger("game_ui")
        self.game_state = game_state
        self.system_manager = system_manager

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
        self.drag_drop_manager = get_drag_drop_manager()
        
        # Initialize layout system
        self._initialize_layout_system()
        
        # Initialize dopamine feedback overlay for addictive gameplay
        self.dopamine_overlay = DopamineFeedbackOverlay(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        
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
        self.automation_builder_panel = AutomationBuilderPanel(self.game_state)
        self.progressive_difficulty_panel = ProgressiveDifficultyPanel(50, 50, 400, 300)
        self.skill_tree_panel = SkillTreePanel(50, 50, 600, 400)
        self.team_dynamics_panel = TeamDynamicsPanel(50, 50, 600, 400)
        self.economy_panel = EconomyPanel(50, 50, 600, 400)

        # Apply theme to panels
        self._apply_theme_to_panels()

    # Panels list for z-order management
        self.panels = [
            self.specialist_roster_panel,
            self.incident_queue_panel,
            self.metrics_panel,
            self.equipment_shop_panel,
            self.equipment_inventory_panel,
            self.automation_builder_panel,
            self.progressive_difficulty_panel,
            self.skill_tree_panel,
            self.team_dynamics_panel,
            self.economy_panel,
        ]

        # Create the modal manager after panels and layout have been initialized so
        # the modal callbacks can access the layout/layer manager to restore focus.
        self.modal_manager = ModalManager(
            self.screen,
            self.game_state,
            on_open=self._on_modal_open,
            on_close=self._on_modal_close
        )
        
        # Initialize dashboard manager for extensible UI framework
        if self.system_manager:
            self.dashboard_manager = DashboardManager(self.system_manager)
            self.dashboard_panel = DashboardPanel(
                x=10,
                y=60,
                on_widget_clicked=self._on_dashboard_widget_clicked
            )
            self.logger.debug("[GAME_UI] Dashboard manager and panel initialized with system plugins")
        else:
            self.dashboard_manager = None
            self.dashboard_panel = None
            self.logger.debug("[GAME_UI] Dashboard not available (no system_manager)")
        
        # Initialize navigation menu
        menu_items = [
            MenuItem("overview", "Overview", "📊", "Game dashboard and key metrics", pygame.K_F1),
            MenuItem("operations", "Operations", "⚡", "Incidents & Specialists", pygame.K_F2),
            MenuItem("management", "Management", "🏢", "Equipment & Facilities", pygame.K_F3),
            MenuItem("analytics", "Analytics", "📈", "Metrics & Achievements", pygame.K_F4),
            MenuItem("automation", "Automation", "🤖", "Build Custom Automation Scripts", pygame.K_F5),
            MenuItem("progressive_difficulty", "Difficulty", "📈", "Progressive Difficulty & Performance", pygame.K_F6),
            MenuItem("skill_tree", "Skill Trees", "🌳", "Specialist Skill Trees & Progression", pygame.K_F7),
            MenuItem("team_dynamics", "Team Dynamics", "👥", "Specialist Relationships & Morale", pygame.K_F8),
            MenuItem("economy", "Economy", "💰", "Market Conditions & Investments", pygame.K_F9),
        ]
        
        self.navigation_menu = NavigationMenu(
            items=menu_items,
            position=MenuPosition.LEFT,
            on_item_selected=self._on_menu_item_selected
        )
        
        # Update layout system with reserved zones for navigation menu and HUD
        self._update_reserved_zones()
        
        # Initialize panels with layout constraints
        self._initialize_panels_with_layout()

        # Initialize view manager
        panel_dict = {
            "specialist_roster": self.specialist_roster_panel,
            "incident_queue": self.incident_queue_panel,
            "metrics": self.metrics_panel,
            "equipment_shop": self.equipment_shop_panel,
            "equipment_inventory": self.equipment_inventory_panel,
            "automation_builder": self.automation_builder_panel,
            "progressive_difficulty": self.progressive_difficulty_panel,
            "skill_tree": self.skill_tree_panel,
            "team_dynamics": self.team_dynamics_panel,
            "economy": self.economy_panel,
        }
        
        self.view_manager = ViewManager(
            views=create_default_views(self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
            panels=panel_dict,
            initial_view=GameView.OPERATIONS,  # Start with operations view
            on_view_changed=self._on_view_changed
        )
        
        # Initialize HUD overlay
        self.hud_overlay = HUDOverlay(
            screen_width=self.WINDOW_WIDTH,
            screen_height=self.WINDOW_HEIGHT,
            position="top"
        )

        # Player engagement manager (urgency, feedback, progression)
        try:
            self.engagement = EngagementManager((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), self.game_state)
        except Exception:
            self.engagement = None
        
        # Initialize quick reference card
        self.quick_reference = QuickReference(
            position="bottom-right",
            auto_hide_delay=5.0  # Auto-hide after 5 seconds
        )

        # Debug overlay for layout visualization and diagnostics
        try:
            self.debug_overlay = LayoutDebugOverlay(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        except Exception:
            # Fail-safe: if debug overlay cannot be created (pygame font issues etc.), disable it
            self.debug_overlay = None

        # Panel inspector (shows details for selected panel in debug overlay)
        try:
            self.panel_inspector = PanelInspector(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        except Exception:
            self.panel_inspector = None

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

        self.logger.info("[GAME_UI] Game UI initialized with drag-and-drop support")
    
    def _initialize_layout_system(self) -> None:
        """Initialize the layout management system."""
        # Create grid configuration (12x12 for responsive design)
        grid_config = GridConfig(
            rows=12,
            cols=12,
            gutter=10,
            margin=20,
            reserved_zones=[]  # Will be updated after navigation menu init
        )
        
        # Initialize layout manager
        self.layout_manager = LayoutManager(
            screen_size=(self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
            grid_config=grid_config
        )
        
        # Initialize layer manager for z-order control
        self.layer_manager = LayerManager()
    
    def _update_reserved_zones(self) -> None:
        """Update layout system with reserved zones for navigation and HUD."""
        # Get navigation menu bounds
        nav_rect = self.navigation_menu.get_rect(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        
        # Get HUD bounds (top area)
        hud_height = 60  # Approximate HUD height
        hud_rect = pygame.Rect(0, 0, self.WINDOW_WIDTH, hud_height)
        
        # Update layout manager with reserved zones
        self.layout_manager.grid_config.reserved_zones = [nav_rect, hud_rect]
        self.layout_manager._calculate_grid()  # Recalculate grid with new reserved zones
    
    def _initialize_panels_with_layout(self) -> None:
        """Initialize panels with layout constraints instead of absolute positioning."""
        # Operations view layout (specialists left, incidents right)
        self.layout_manager.add_panel(
            "specialist_roster",
            self.specialist_roster_panel,
            LayoutMode.GRID,
            GridConstraints(
                row=1, col=0, row_span=8, col_span=4,
                padding=10, alignment="fill"
            )
        )
        
        self.layout_manager.add_panel(
            "incident_queue",
            self.incident_queue_panel,
            LayoutMode.GRID,
            GridConstraints(
                row=1, col=4, row_span=8, col_span=4,
                padding=10, alignment="fill"
            )
        )
        
        # Management view layout (equipment panels)
        self.layout_manager.add_panel(
            "equipment_shop",
            self.equipment_shop_panel,
            LayoutMode.GRID,
            GridConstraints(
                row=1, col=0, row_span=8, col_span=6,
                padding=10, alignment="fill"
            )
        )
        
        self.layout_manager.add_panel(
            "equipment_inventory",
            self.equipment_inventory_panel,
            LayoutMode.GRID,
            GridConstraints(
                row=1, col=6, row_span=8, col_span=6,
                padding=10, alignment="fill"
            )
        )
        
        # Analytics view layout (metrics panel)
        self.layout_manager.add_panel(
            "metrics",
            self.metrics_panel,
            LayoutMode.GRID,
            GridConstraints(
                row=1, col=0, row_span=10, col_span=12,
                padding=10, alignment="fill"
            )
        )
    
    def handle_resize(self, new_size: Tuple[int, int]) -> None:
        """Handle window resize event.
        
        Args:
            new_size: New window size (width, height)
        """
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = new_size
        self.screen = pygame.display.set_mode(new_size)
        
        # Update HUD and other components
        self.hud_overlay = HUDOverlay(
            screen_width=self.WINDOW_WIDTH,
            screen_height=self.WINDOW_HEIGHT,
            position="top"
        )
        
        # Update quick reference
        self.quick_reference = QuickReference(
            position="bottom-right",
            auto_hide_delay=15.0
        )
        
        # Update dopamine overlay
        self.dopamine_overlay = DopamineFeedbackOverlay(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        
        # Update synergy overlay
        self.synergy_overlay = SynergySuggestionOverlay(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        
        # Update navigation menu bounds
        self._update_reserved_zones()
    
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
        self.logger.info(f"[GAME_UI] Switched to view: {view_config.title}")

    def _get_top_panel(self):
        """Return the top-most panel component according to the layer manager.

        This is used to remember which panel had focus (z-order) when a modal
        opens so focus can be restored when the modal closes.
        """
        try:
            render_order = self.layout_manager.layer_manager.get_render_order()
            # Return the last component that is one of our panels
            for comp in reversed(render_order):
                if comp in self.panels:
                    return comp
        except Exception:
            return None
        return None

    def _on_modal_open(self) -> None:
        """Called when a modal opens. Save the current top panel so we can
        restore it later when the modal closes."""
        try:
            self._saved_focused_panel = self._get_top_panel()
        except Exception:
            self._saved_focused_panel = None

    def _on_modal_close(self) -> None:
        """Called when a modal closes. Restore the previously focused panel
        by bringing it to the front of its layer."""
        try:
            panel = getattr(self, '_saved_focused_panel', None)
            if panel and panel in self.panels:
                # Bring back to front so it receives subsequent input
                self.layout_manager.layer_manager.bring_to_front(panel)
        except Exception:
            pass
        finally:
            self._saved_focused_panel = None

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
        # Debug overlay toggles (F12 cycles modes)
        try:
            self.hotkey_manager.register_callback(
                HotkeyAction.DEBUG_TOGGLE,
                lambda: self._toggle_debug_overlay()
            )
        except Exception:
            pass
        # F11 toggles panel inspector
        try:
            self.hotkey_manager.register_callback(
                HotkeyAction.DEBUG_INSPECTOR,
                lambda: self._toggle_panel_inspector()
            )
        except Exception:
            pass
        # F10 takes screenshot
        try:
            self.hotkey_manager.register_callback(
                HotkeyAction.TAKE_SCREENSHOT,
                lambda: self._take_screenshot()
            )
        except Exception:
            pass

    def set_screenshot_utility(self, screenshot_utility) -> None:
        """Set the screenshot utility for hotkey callbacks.
        
        Args:
            screenshot_utility: The screenshot utility instance
        """
        self.screenshot_utility = screenshot_utility

    def _take_screenshot(self) -> None:
        """Take a screenshot of the current game state."""
        if hasattr(self, 'screenshot_utility') and self.screenshot_utility:
            try:
                self.screenshot_utility.capture_screenshot()
                self.notification_manager.show_info("Screenshot", "Screenshot saved!")
            except Exception as e:
                self.logger.error(f"Failed to take screenshot: {e}")
                self.notification_manager.show_error("Screenshot", "Failed to save screenshot")
        else:
            self.logger.warning("Screenshot utility not available")
            self.notification_manager.show_error("Screenshot", "Screenshot utility not initialized")

    def _toggle_panel_inspector(self) -> None:
        """Toggle the panel inspector."""
        inspector = getattr(self, 'panel_inspector', None)
        if not inspector:
            return
        inspector.toggle()

    def _toggle_debug_overlay(self) -> None:
        """Toggle the debug overlay visibility and cycle modes if held."""
        debug = getattr(self, 'debug_overlay', None)
        if not debug:
            return
        # If already enabled, cycle modes; otherwise enable
        if getattr(debug, 'enabled', False):
            debug.cycle_mode()
        else:
            debug.toggle_enabled()
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
            if getattr(self, 'engagement', None):
                try:
                    self.engagement.notify_assignment(specialist.id, incident.id, True)
                except Exception:
                    pass
            else:
                self.notification_manager.show_error(
                    "Assignment Failed",
                    "Could not assign specialist to incident"
                )
            if getattr(self, 'engagement', None):
                try:
                    self.engagement.notify_assignment(specialist.id, incident.id, False)
                except Exception:
                    pass

    def handle_input(self, events: List[pygame.event.Event]) -> List[GameAction]:
        """Process input events and return game actions.

        Args:
            events: List of Pygame events

        Returns:
            List of game actions to process
        """
        actions = []

        for event in events:
            # Give the modal manager first dibs on events
            if self.modal_manager.handle_event(event):
                continue

            # Handle window resize events
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize((event.w, event.h))
                continue
            
            # Handle navigation menu first
            if self.navigation_menu.handle_event(event, self.WINDOW_WIDTH, self.WINDOW_HEIGHT):
                continue
            
            # Handle dashboard widget clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.dashboard_panel:
                    clicked_plugin = self.dashboard_panel.handle_click(event.pos)
                    if clicked_plugin:
                        continue
            
            # Handle mouse movement for dashboard hover effects
            if event.type == pygame.MOUSEMOTION:
                if self.dashboard_panel:
                    self.dashboard_panel.update_hover(event.pos)
            
            # Handle drag and drop events (before panels)
            if self._handle_drag_drop_event(event):
                continue

            # Handle hotkeys
            if self.hotkey_manager.handle_key_event(event):
                continue

            # Handle panel events (in reverse z-order from layout system) - only if visible
            event_consumed = False
            # Let debug overlay capture click events when enabled
            debug = getattr(self, 'debug_overlay', None)
            if debug and getattr(debug, 'enabled', False):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if debug.handle_click(event.pos, self.layout_manager):
                        event_consumed = True
                        # don't pass through
                        continue
            for panel in reversed(self.panels):
                if hasattr(panel, 'visible') and not panel.visible:
                    continue
                    
                if panel.handle_event(event):
                    # Bring panel to front if clicked
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.layout_manager.layer_manager.bring_to_front(panel)
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
                    # H key toggles both help overlay and quick reference
                    self.show_help_overlay = not self.show_help_overlay
                    if not self.show_help_overlay:
                        self.quick_reference.toggle()
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
                            if getattr(self, 'engagement', None):
                                try:
                                    self.engagement.notify_assignment(selected_specialist.id, selected_incident.id, True)
                                except Exception:
                                    pass
                        else:
                            self.notification_manager.show_error(
                                "Assignment Failed", 
                                "Specialist unavailable or specialty mismatch"
                            )
                            if getattr(self, 'engagement', None):
                                try:
                                    self.engagement.notify_assignment(selected_specialist.id, selected_incident.id, False)
                                except Exception:
                                    pass
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
                    self.dragged_incident = self.drag_drop_manager.get_dragged_incident()
                    self.drag_offset = (0, 0)  # Will be set by mouse motion
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
                if getattr(self, 'engagement', None):
                    try:
                        self.engagement.notify_assignment(self.drag_highlight_specialist, self.dragged_incident.id, True)
                    except Exception:
                        pass
                else:
                    self.notification_manager.show_error(
                        "Assignment Failed",
                        "Specialist unavailable or specialty mismatch"
                    )
                if getattr(self, 'engagement', None):
                    try:
                        self.engagement.notify_assignment(self.drag_highlight_specialist, self.dragged_incident.id, False)
                    except Exception:
                        pass
            
            # Clear drag state
            self.dragged_incident = None
            self.drag_offset = (0, 0)
            self.drag_highlight_specialist = None
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
        
        # Update HUD overlay
        self.hud_overlay.update(delta_time, self.game_state)
        
        # Update quick reference
        self.quick_reference.update(delta_time)
        
        # Update modal manager
        self.modal_manager.update(delta_time)
        
        # Update notification manager
        self.notification_manager.update(delta_time)
        
        # Update dopamine overlay with feedback from game state
        self.dopamine_overlay.process_feedback(
            self.game_state.dopamine_feedback_queue,
            self.game_state._dopamine_system
        )
        self.dopamine_overlay.update(delta_time)

        # Update engagement manager
        if getattr(self, 'engagement', None):
            try:
                self.engagement.update(delta_time)
            except Exception:
                pass
        
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

        # Update debug metrics (approx)
        debug = getattr(self, 'debug_overlay', None)
        if debug:
            try:
                fps = self.clock.get_fps() or self.FPS
                layout_time = getattr(self, '_last_layout_time', 0.0)
                render_time = getattr(self, '_last_render_time', 0.0)
                panel_count = len(self.layout_manager.panels)
                # quick collision count
                collision_count = 0
                panels = list(self.layout_manager.panels.values())
                for i, p1 in enumerate(panels):
                    if not hasattr(p1, 'rect'):
                        continue
                    for p2 in panels[i+1:]:
                        if hasattr(p2, 'rect') and p1.rect.colliderect(p2.rect):
                            collision_count += 1

                debug.update_metrics(fps, layout_time, render_time, panel_count, collision_count)
                # Run layout validation and populate overlay issues
                try:
                    issues = validate_layout(self.layout_manager)
                    debug.validation_issues = issues
                except Exception:
                    debug.validation_issues = []
            except Exception:
                # Non-fatal; continue without debug metrics
                pass

    def render(self) -> None:
        """Render the game UI."""
        # Get background color from theme
        bg_color = self.theme_manager.get_color("background", (15, 15, 25))
        self.screen.fill(bg_color)

        # Render modern HUD overlay (replaces old header)
        current_view_config = self.view_manager.get_current_view_config()
        view_title = current_view_config.title if current_view_config else ""
        self.hud_overlay.render(self.screen, self.game_state, view_title)
        
        # Render navigation menu
        self.navigation_menu.render(self.screen, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # Render all visible panels
        for panel in self.panels:
            if hasattr(panel, 'visible') and panel.visible:
                panel.render(self.screen)

        # Render controls (only show assign button in operations view)
        current_view = self.view_manager.current_view
        if current_view == GameView.OPERATIONS:
            self._render_controls()
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

        # Render engagement overlays on top of HUD but below modals/notifications
        if getattr(self, 'engagement', None):
            try:
                self.engagement.render(self.screen)
            except Exception:
                pass

        # Render drag and drop visual feedback (only in operations view)
        if current_view == GameView.OPERATIONS:
            self._render_drag_drop()
        
        # Render dashboard panel overlay (shows UIProvider summaries)
        if self.dashboard_panel and self.dashboard_manager:
            self.dashboard_panel.render(self.screen, self.dashboard_manager, self.game_state)
        
        # Render view transition overlay
        self.view_manager.render_transition_overlay(self.screen)
        
        # Render quick reference card (if visible)
        self.quick_reference.render(self.screen)

        # Render modals on top of everything else
        self.modal_manager.draw()

        # Render notifications (always on top)
        self.notification_manager.render(self.screen)

        # Render help overlay if active
        if self.show_help_overlay:
            self._render_help_overlay()

        # Render debug overlay on top of everything (if present)
        debug = getattr(self, 'debug_overlay', None)
        if debug:
            try:
                debug.render(self.screen, self.layout_manager)
            except Exception:
                # Ensure rendering never crashes the main loop
                pass

        # Render panel inspector (uses debug overlay selection)
        inspector = getattr(self, 'panel_inspector', None)
        if inspector:
            try:
                panel_info = None
                if debug:
                    panel_info = debug.get_panel_info(self.layout_manager)
                inspector.render(self.screen, panel_info)
            except Exception:
                pass

        # Update display
        pygame.display.flip()

    def _render_drag_drop(self) -> None:
        """Render drag and drop visual feedback."""
        if not self.dragged_incident:
            return

        # Get current mouse position for drag preview
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Compute preview position using stored offset
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

    def _on_dashboard_widget_clicked(self, plugin_name: str) -> None:
        """Handle dashboard widget click to open detail panel.
        
        Args:
            plugin_name: Name of the plugin that was clicked
        """
        if not self.dashboard_manager:
            return
        
        # Set expanded panel in dashboard manager
        self.dashboard_manager.set_expanded_panel(plugin_name)
        
        # Get detail panel data from dashboard manager
        detail_data = self.dashboard_manager.get_detail_panel_data(
            plugin_name,
            self.game_state
        )
        
        if detail_data:
            # Log the action
            self.logger.debug(f"[GAME_UI] Dashboard widget clicked: {plugin_name}")
            self.logger.debug(f"[GAME_UI] Detail data keys: {list(detail_data.keys())}")

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
        self.logger.info("[GAME_UI] Shutting down game UI")
