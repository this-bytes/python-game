"""
View Manager for handling different game view modes.

Manages transitions between major game views (Overview, Operations, Management, Analytics)
and controls which panels are visible in each view.
"""

from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass
import pygame


class GameView(Enum):
    """Available game views."""
    OVERVIEW = "overview"
    OPERATIONS = "operations"
    MANAGEMENT = "management"
    ANALYTICS = "analytics"
    AUTOMATION = "automation"
    PROGRESSIVE_DIFFICULTY = "progressive_difficulty"
    SKILL_TREE = "skill_tree"
    TEAM_DYNAMICS = "team_dynamics"


@dataclass
class ViewConfig:
    """Configuration for a game view.
    
    Attributes:
        id: View identifier (matches GameView enum)
        title: Display title
        panels: List of panel names to show in this view
        layout: Layout configuration for panels
        description: Brief description of view
    """
    id: str
    title: str
    panels: List[str]
    layout: Dict[str, Dict]  # panel_name -> {position, size, visible}
    description: str = ""


class ViewManager:
    """Manages game views and panel visibility.
    
    Controls which panels are visible and how they're arranged based on
    the current view mode. Handles smooth transitions between views.
    
    Features:
    - Multiple predefined views
    - Smooth view transitions with fade effects
    - Panel layout management per view
    - View history for back navigation
    - Callbacks for view changes
    
    Example:
        view_manager = ViewManager(
            views=create_default_views(),
            panels={
                "specialist_roster": specialist_panel,
                "incident_queue": incident_panel,
                # ... other panels
            },
            on_view_changed=lambda view: print(f"Switched to {view.title}")
        )
        
        # Switch views
        view_manager.switch_to_view(GameView.OPERATIONS)
        
        # In game loop
        view_manager.update(delta_time)
    """
    
    def __init__(
        self,
        views: Dict[GameView, ViewConfig],
        panels: Dict[str, Any],
        initial_view: GameView = GameView.OVERVIEW,
        on_view_changed: Optional[Callable[[ViewConfig], None]] = None,
        transition_duration: float = 0.3
    ):
        """Initialize ViewManager.
        
        Args:
            views: Dictionary of view configurations
            panels: Dictionary of panel instances by name
            initial_view: Initial view to show
            on_view_changed: Callback when view changes
            transition_duration: Duration of view transition animation
        """
        self.views = views
        self.panels = panels
        self.current_view = initial_view
        self.previous_view: Optional[GameView] = None
        self.on_view_changed = on_view_changed
        self.transition_duration = transition_duration
        
        # Transition state
        self.is_transitioning = False
        self.transition_progress = 0.0
        self.target_view: Optional[GameView] = None
        
        # Apply initial view
        self._apply_view(initial_view, instant=True)
    
    def switch_to_view(self, view: GameView, instant: bool = False, update_history: bool = True) -> None:
        """Switch to a different view.
        
        Args:
            view: Target view to switch to
            instant: Skip transition animation if True
            update_history: Whether to update previous_view for back navigation
        """
        if view == self.current_view:
            return
        
        if view not in self.views:
            return
        
        if update_history:
            self.previous_view = self.current_view
        
        if instant:
            self._apply_view(view, instant=True)
        else:
            self.is_transitioning = True
            self.transition_progress = 0.0
            self.target_view = view
    
    def go_back(self, instant: bool = False) -> bool:
        """Go back to previous view.
        
        Args:
            instant: Skip transition animation if True
            
        Returns:
            True if went back, False if no previous view
        """
        if self.previous_view and self.previous_view != self.current_view:
            target = self.previous_view
            self.switch_to_view(target, instant=instant, update_history=False)
            return True
        return False
    
    def _apply_view(self, view: GameView, instant: bool = False) -> None:
        """Apply view configuration to panels.
        
        Args:
            view: View to apply
            instant: Apply instantly without animation
        """
        if view not in self.views:
            return
        
        view_config = self.views[view]
        
        # Hide all panels first
        for panel_name, panel in self.panels.items():
            if hasattr(panel, 'visible'):
                panel.visible = False
        
        # Show and configure panels for this view
        for panel_name in view_config.panels:
            if panel_name in self.panels:
                panel = self.panels[panel_name]
                
                # Apply visibility
                if hasattr(panel, 'visible'):
                    panel.visible = True
                
                # Apply layout if configured
                if panel_name in view_config.layout:
                    layout = view_config.layout[panel_name]
                    
                    if 'position' in layout and hasattr(panel, 'set_position'):
                        panel.set_position(*layout['position'])
                    
                    if 'size' in layout and hasattr(panel, 'set_size'):
                        panel.set_size(*layout['size'])
                    
                    if 'visible' in layout and hasattr(panel, 'visible'):
                        panel.visible = layout['visible']
        
        self.current_view = view
        self.is_transitioning = False
        
        # Trigger callback
        if self.on_view_changed:
            self.on_view_changed(view_config)
    
    def update(self, delta_time: float) -> None:
        """Update view transitions.
        
        Args:
            delta_time: Time elapsed since last update
        """
        if not self.is_transitioning:
            return
        
        # Update transition progress
        self.transition_progress += delta_time / self.transition_duration
        
        if self.transition_progress >= 1.0:
            # Transition complete
            if self.target_view:
                self._apply_view(self.target_view, instant=True)
            self.is_transitioning = False
            self.transition_progress = 0.0
            self.target_view = None
    
    def get_transition_alpha(self) -> int:
        """Get alpha value for transition fade effect.
        
        Returns:
            Alpha value (0-255)
        """
        if not self.is_transitioning:
            return 255
        
        # Fade out then fade in
        if self.transition_progress < 0.5:
            # Fade out
            return int(255 * (1.0 - self.transition_progress * 2))
        else:
            # Fade in
            return int(255 * ((self.transition_progress - 0.5) * 2))
    
    def render_transition_overlay(self, screen: pygame.Surface) -> None:
        """Render transition fade overlay.
        
        Args:
            screen: Pygame surface to render on
        """
        if not self.is_transitioning:
            return
        
        alpha = 255 - self.get_transition_alpha()
        if alpha > 0:
            overlay = pygame.Surface(screen.get_size())
            overlay.set_alpha(alpha)
            overlay.fill((10, 10, 15))
            screen.blit(overlay, (0, 0))
    
    def get_current_view_config(self) -> Optional[ViewConfig]:
        """Get configuration for current view.
        
        Returns:
            Current view configuration
        """
        return self.views.get(self.current_view)
    
    def is_panel_visible_in_current_view(self, panel_name: str) -> bool:
        """Check if panel should be visible in current view.
        
        Args:
            panel_name: Name of panel to check
            
        Returns:
            True if panel should be visible
        """
        view_config = self.get_current_view_config()
        if not view_config:
            return False
        
        return panel_name in view_config.panels


def create_default_views(screen_width: int = 1280, screen_height: int = 720) -> Dict[GameView, ViewConfig]:
    """Create default view configurations.
    
    Args:
        screen_width: Screen width for layout calculations
        screen_height: Screen height for layout calculations
        
    Returns:
        Dictionary of view configurations
    """
    # Calculate dimensions based on screen size
    # Navigation menu is 200px wide on left, HUD overlay is 60px tall at top
    sidebar_width = 200
    header_height = 60
    content_width = screen_width - sidebar_width
    content_height = screen_height - header_height
    
    # Base positions account for navigation menu and HUD
    base_x = sidebar_width + 20  # 220px from left
    base_y = header_height + 20   # 80px from top
    
    return {
        GameView.OVERVIEW: ViewConfig(
            id="overview",
            title="Overview",
            panels=["metrics"],
            layout={
                "metrics": {
                    "position": (base_x, base_y),
                    "size": (content_width - 40, content_height - 40),
                    "visible": True
                }
            },
            description="Dashboard with key metrics and game status"
        ),
        
        GameView.OPERATIONS: ViewConfig(
            id="operations",
            title="Operations",
            panels=["specialist_roster", "incident_queue"],
            layout={
                "specialist_roster": {
                    "position": (base_x, base_y),
                    "size": (400, content_height - 40),
                    "visible": True
                },
                "incident_queue": {
                    "position": (base_x + 420, base_y),  # After specialist panel + margin
                    "size": (content_width - 460, content_height - 40),
                    "visible": True
                }
            },
            description="Manage incidents and specialist assignments"
        ),
        
        GameView.MANAGEMENT: ViewConfig(
            id="management",
            title="Management",
            panels=["equipment_shop", "equipment_inventory"],
            layout={
                "equipment_shop": {
                    "position": (base_x, base_y),
                    "size": (400, content_height - 40),
                    "visible": True
                },
                "equipment_inventory": {
                    "position": (base_x + 420, base_y),  # After shop panel + margin
                    "size": (content_width - 460, content_height - 40),
                    "visible": True
                }
            },
            description="Equipment shop and inventory management"
        ),
        
        GameView.ANALYTICS: ViewConfig(
            id="analytics",
            title="Analytics",
            panels=["metrics"],
            layout={
                "metrics": {
                    "position": (base_x, base_y),
                    "size": (content_width - 40, content_height - 40),
                    "visible": True
                }
            },
            description="Detailed metrics and achievement tracking"
        ),
        
        GameView.AUTOMATION: ViewConfig(
            id="automation",
            title="Automation",
            panels=["automation_builder"],
            layout={
                "automation_builder": {
                    "position": (base_x, base_y),
                    "size": (content_width - 40, content_height - 40),
                    "visible": True
                }
            },
            description="Build custom automation scripts with visual editor"
        ),
        
        GameView.PROGRESSIVE_DIFFICULTY: ViewConfig(
            id="progressive_difficulty",
            title="Progressive Difficulty",
            panels=["progressive_difficulty"],
            layout={
                "progressive_difficulty": {
                    "position": (base_x, base_y),
                    "size": (content_width - 40, content_height - 40),
                    "visible": True
                }
            },
            description="Monitor progressive difficulty and performance metrics"
        ),
        
        GameView.SKILL_TREE: ViewConfig(
            id="skill_tree",
            title="Skill Trees",
            panels=["skill_tree"],
            layout={
                "skill_tree": {
                    "position": (base_x, base_y),
                    "size": (content_width - 40, content_height - 40),
                    "visible": True
                }
            },
            description="Specialist skill trees and progression management"
        ),
        
        GameView.TEAM_DYNAMICS: ViewConfig(
            id="team_dynamics",
            title="Team Dynamics",
            panels=["team_dynamics"],
            layout={
                "team_dynamics": {
                    "position": (base_x, base_y),
                    "size": (content_width - 40, content_height - 40),
                    "visible": True
                }
            },
            description="Specialist relationships and team morale management"
        )
    }
