"""GameSystem interface for plugin-based game architecture.

All game systems (idle mechanics, prestige, achievements, etc.) should inherit
from GameSystem to enable consistent lifecycle management and integration.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.models.game_state import GameState


class GameSystem(ABC):
    """Abstract base class for all game systems.
    
    Game systems are self-contained plugins that:
    - Have clear lifecycle methods (initialize, update, shutdown)
    - Can save/load their state independently
    - Integrate via event bus (publish/subscribe)
    - Can be enabled/disabled via feature flags
    
    Example:
        ```python
        class MySystem(GameSystem):
            def initialize(self, game_state):
                self.some_data = []
                
            def update(self, game_state, delta_time):
                # Update logic here
                pass
                
            def get_name(self):
                return "my_system"
        ```
    """
    
    def __init__(self):
        """Initialize the game system."""
        self._initialized = False
        self._enabled = True
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the unique name of this system.
        
        Returns:
            System name (e.g., "idle_core", "prestige_system")
        """
        pass
    
    @abstractmethod
    def initialize(self, game_state: GameState):
        """Initialize the system with game state.
        
        Called once when the system is first added to the game.
        Use this to set up initial state, subscribe to events, etc.
        
        Args:
            game_state: Current game state
        """
        pass
    
    @abstractmethod
    def update(self, game_state: GameState, delta_time: float):
        """Update the system for one game frame.
        
        Called every frame while the system is enabled.
        
        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update (seconds)
        """
        pass
    
    def shutdown(self, game_state: GameState):
        """Shutdown the system and cleanup resources.
        
        Called when the system is removed or game is closing.
        Use this to unsubscribe from events, save data, etc.
        
        Args:
            game_state: Current game state
        """
        pass
    
    def save_state(self, game_state: GameState) -> Dict[str, Any]:
        """Save system-specific state.
        
        Override to save custom data that isn't in GameState.
        
        Args:
            game_state: Current game state
            
        Returns:
            Dictionary with system state data
        """
        return {}
    
    def load_state(self, game_state: GameState, state_data: Dict[str, Any]):
        """Load system-specific state.
        
        Override to restore custom data that isn't in GameState.
        
        Args:
            game_state: Current game state
            state_data: State data from save_state()
        """
        pass
    
    def is_initialized(self) -> bool:
        """Check if system is initialized.
        
        Returns:
            True if initialize() was called
        """
        return self._initialized
    
    def set_initialized(self, initialized: bool):
        """Set initialized state.
        
        Args:
            initialized: New initialized state
        """
        self._initialized = initialized
    
    def is_enabled(self) -> bool:
        """Check if system is enabled.
        
        Returns:
            True if system is enabled and should update
        """
        return self._enabled
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the system.
        
        Disabled systems don't receive update() calls.
        
        Args:
            enabled: True to enable, False to disable
        """
        self._enabled = enabled
    
    def get_feature_id(self) -> Optional[str]:
        """Get feature flag ID for this system.
        
        Override to link system to a feature flag.
        If feature is disabled, system won't be initialized.
        
        Returns:
            Feature ID or None (always enabled)
        """
        return None
    
    def get_dependencies(self) -> list:
        """Get list of system names this system depends on.
        
        Override to specify dependencies. Dependent systems
        will be initialized before this system.
        
        Returns:
            List of system names (e.g., ["idle_core"])
        """
        return []
    
    def on_event(self, event):
        """Handle an event from the event bus.
        
        Override to respond to specific events.
        Subscribe to events in initialize().
        
        Args:
            event: Event object from event bus
        """
        pass
