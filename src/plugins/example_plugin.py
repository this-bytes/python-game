"""Example plugin demonstrating the plugin architecture.

This is a template/reference implementation showing how to create
a new game system using the plugin architecture.
"""

from src.core.game_system import GameSystem
from src.core.event_bus import get_event_bus, EventPriority
from src.core.feature_manager import get_feature_manager
from src.models.game_state import GameState
from src.utils.logger import GameLogger


class ExamplePlugin(GameSystem):
    """Example plugin showing best practices.
    
    This plugin demonstrates:
    - Event subscriptions
    - Feature flag integration
    - State persistence
    - Logging
    - Clean architecture
    """
    
    def __init__(self):
        """Initialize the plugin."""
        super().__init__()
        self.logger = GameLogger("example_plugin")
        self.event_bus = None
        self.features = None
        
        # Plugin-specific state
        self.example_counter = 0
        self.example_data = {}
    
    def get_name(self) -> str:
        """Get unique system name."""
        return "example_plugin"
    
    def get_feature_id(self) -> str:
        """Link to feature flag.
        
        If feature flag 'example_feature' is disabled,
        this plugin won't be initialized.
        """
        return "example_feature"
    
    def get_dependencies(self) -> list:
        """Define system dependencies.
        
        This system requires idle_core to be initialized first.
        SystemManager ensures correct initialization order.
        """
        return ["idle_core"]
    
    def initialize(self, game_state: GameState):
        """Initialize the plugin.
        
        Called once when plugin is first added.
        Use this to:
        - Get singletons (event bus, feature manager)
        - Subscribe to events
        - Setup initial state
        """
        self.event_bus = get_event_bus()
        self.features = get_feature_manager()
        
        # Subscribe to events we care about
        self.event_bus.subscribe(
            "incident_resolved",
            self._on_incident_resolved,
            EventPriority.NORMAL
        )
        
        self.event_bus.subscribe(
            "specialist_level_up",
            self._on_specialist_level_up,
            EventPriority.HIGH
        )
        
        self.logger.logger.info("[EXAMPLE] Plugin initialized")
    
    def update(self, game_state: GameState, delta_time: float):
        """Update plugin every frame.
        
        Called every frame while plugin is enabled.
        
        Args:
            game_state: Current game state
            delta_time: Time since last update (seconds)
        """
        # Update plugin logic
        self.example_counter += 1
        
        # Example: Check feature flag at runtime
        if self.features.is_enabled("example_advanced_mode"):
            self._do_advanced_logic(game_state)
        else:
            self._do_basic_logic(game_state)
        
        # Example: Publish events
        if self.example_counter % 100 == 0:
            self.event_bus.publish(
                "example_milestone",
                {"counter": self.example_counter},
                source="example_plugin"
            )
    
    def shutdown(self, game_state: GameState):
        """Shutdown plugin.
        
        Called when plugin is removed or game exits.
        Use this to:
        - Unsubscribe from events (optional, happens automatically)
        - Save final state
        - Cleanup resources
        """
        self.logger.logger.info(
            f"[EXAMPLE] Plugin shutting down (counter: {self.example_counter})"
        )
    
    def save_state(self, game_state: GameState) -> dict:
        """Save plugin-specific state.
        
        Only save data that's NOT in GameState.
        SystemManager coordinates saves across all plugins.
        
        Returns:
            Dictionary with plugin state
        """
        return {
            "example_counter": self.example_counter,
            "example_data": self.example_data
        }
    
    def load_state(self, game_state: GameState, state_data: dict):
        """Load plugin-specific state.
        
        Restore data from save_state().
        
        Args:
            game_state: Current game state
            state_data: Saved state data
        """
        self.example_counter = state_data.get("example_counter", 0)
        self.example_data = state_data.get("example_data", {})
        
        self.logger.logger.info(
            f"[EXAMPLE] State loaded (counter: {self.example_counter})"
        )
    
    def _on_incident_resolved(self, event):
        """Handle incident resolution event.
        
        Args:
            event: Event object with data
        """
        incident_id = event.data.get("incident_id")
        reward = event.data.get("reward", 0)
        
        self.logger.logger.debug(
            f"[EXAMPLE] Incident {incident_id} resolved for ${reward}"
        )
        
        # Update plugin state
        if incident_id not in self.example_data:
            self.example_data[incident_id] = 0
        self.example_data[incident_id] += 1
    
    def _on_specialist_level_up(self, event):
        """Handle specialist level up event.
        
        Args:
            event: Event object with data
        """
        specialist_id = event.data.get("specialist_id")
        new_level = event.data.get("new_level")
        
        self.logger.logger.info(
            f"[EXAMPLE] Specialist {specialist_id} reached level {new_level}"
        )
        
        # Publish our own event
        self.event_bus.publish(
            "example_specialist_milestone",
            {
                "specialist_id": specialist_id,
                "level": new_level
            },
            source="example_plugin"
        )
    
    def _do_basic_logic(self, game_state: GameState):
        """Basic logic when advanced mode is off."""
        pass
    
    def _do_advanced_logic(self, game_state: GameState):
        """Advanced logic when advanced mode is on."""
        pass
