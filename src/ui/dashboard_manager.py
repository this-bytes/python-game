"""Dashboard Manager - Aggregates UI summaries from all game systems.

The DashboardManager queries all game plugins for their dashboard summaries,
organizes them, and provides methods to render the persistent dashboard overlay
and handle detail panel expansion.

Architecture:
- SystemManager has all plugins
- DashboardManager identifies which plugins implement UIProvider
- Every frame, DashboardManager collects all summaries
- UI renders these summaries as persistent overlay
- When player clicks a summary, detail panel is opened via modal manager
- Detail panel shows expanded information for that system

This is the core of the extensible dashboard system - it requires NO changes
when new plugins are added. New plugins just implement UIProvider.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from src.ui.ui_provider import UIProvider, UISummaryItem
from src.utils.logger import GameLogger
from src.core.event_bus import get_event_bus


@dataclass
class DashboardState:
    """Current state of the dashboard display."""
    summaries: List[Tuple[str, UISummaryItem]]  # List of (plugin_name, summary)
    expanded_panel: Optional[str] = None  # Which panel is expanded (plugin name)
    last_update_time: float = 0.0


class DashboardManager:
    """Manages dashboard overlay and detail panel expansion.
    
    Responsibilities:
    1. Query all plugins that implement UIProvider for summaries
    2. Organize summaries for rendering
    3. Track which detail panel (if any) is currently expanded
    4. Provide detail panel data when requested
    5. Route action button clicks to EventBus
    
    The dashboard is the primary UI element - always visible. Clicking on
    a summary widget expands a detail panel via modal.
    """
    
    def __init__(self, system_manager):
        """Initialize dashboard manager.
        
        Args:
            system_manager: SystemManager instance that holds all plugins
        """
        self.system_manager = system_manager
        self.logger = GameLogger("dashboard")
        self.event_bus = get_event_bus()
        
        self.state = DashboardState(summaries=[])
        
        # Discover UIProvider plugins on initialization
        self.ui_providers: Dict[str, UIProvider] = {}
        self._discover_ui_providers()
        
        self.logger.info(f"Dashboard initialized with {len(self.ui_providers)} UI providers")
    
    def _discover_ui_providers(self):
        """Find all plugins that implement UIProvider interface.
        
        This is called once during initialization. New plugins that implement
        UIProvider will be automatically available after the next game restart.
        """
        all_systems = self.system_manager.get_all_systems()
        for plugin_name, plugin in all_systems.items():
            if isinstance(plugin, UIProvider):
                self.ui_providers[plugin_name] = plugin
                self.logger.debug(f"Discovered UI provider: {plugin_name}")
    
    def get_dashboard_layout(self, game_state) -> DashboardState:
        """Get current dashboard layout with all summaries.
        
        This should be called every frame to ensure dashboard displays
        current state. Queries all UIProvider plugins for summaries.
        
        Args:
            game_state: Current game state to pass to plugins
            
        Returns:
            DashboardState with list of summaries and expansion state
        """
        summaries = []
        
        for plugin_name, provider in self.ui_providers.items():
            try:
                summary = provider.get_dashboard_summary(game_state)
                if summary:
                    summaries.append((plugin_name, summary))
            except Exception as e:
                self.logger.error(
                    f"Failed to get summary from {plugin_name}",
                    exception=e
                )
        
        self.state.summaries = summaries
        return self.state
    
    def get_detail_panel_data(self, plugin_name: str, game_state) -> Optional[Dict[str, Any]]:
        """Get detail panel data for expanded view.
        
        Args:
            plugin_name: Name of plugin providing detail data
            game_state: Current game state to pass to plugin
            
        Returns:
            Dictionary with detail panel structure, or None if plugin not found
        """
        if plugin_name not in self.ui_providers:
            self.logger.warning(f"No UI provider found for: {plugin_name}")
            return None
        
        provider = self.ui_providers[plugin_name]
        
        try:
            data = provider.get_detail_panel_data(game_state)
            return data
        except Exception as e:
            self.logger.error(
                f"Failed to get detail panel from {plugin_name}",
                exception=e
            )
            return None
    
    def set_expanded_panel(self, plugin_name: Optional[str]):
        """Set which detail panel is currently expanded.
        
        Args:
            plugin_name: Name of plugin to expand (None to close panel)
        """
        if plugin_name and plugin_name not in self.ui_providers:
            self.logger.warning(f"Cannot expand unknown plugin: {plugin_name}")
            return
        
        self.state.expanded_panel = plugin_name
        
        if plugin_name:
            self.logger.debug(f"Expanded detail panel for: {plugin_name}")
        else:
            self.logger.debug("Closed detail panel")
    
    def is_panel_expanded(self) -> bool:
        """Check if any detail panel is currently expanded."""
        return self.state.expanded_panel is not None
    
    def get_expanded_panel(self) -> Optional[str]:
        """Get name of currently expanded panel (if any)."""
        return self.state.expanded_panel
    
    def close_panel(self):
        """Close currently expanded detail panel."""
        self.set_expanded_panel(None)
    
    def publish_action(self, action_id: str, data: Dict[str, Any]):
        """Publish action from detail panel button click.
        
        This is called when player clicks an action button in the detail panel.
        The action is published to EventBus with "action:" prefix so the
        corresponding plugin can subscribe and handle it.
        
        Args:
            action_id: Action identifier (e.g., "contact_client")
            data: Action parameters
        """
        event_type = f"action:{action_id}"
        
        self.logger.debug(f"Publishing UI action: {event_type}")
        self.event_bus.publish(
            event_type,
            data,
            source="dashboard_action"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics for debugging."""
        return {
            "ui_providers_count": len(self.ui_providers),
            "active_summaries": len(self.state.summaries),
            "expanded_panel": self.state.expanded_panel,
            "ui_providers": list(self.ui_providers.keys()),
        }
