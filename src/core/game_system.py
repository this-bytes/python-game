"""GameSystem Interface - Abstract base for all game plugins.

All game systems (idle, prestige, achievements, etc) implement this
interface to work seamlessly with the System Manager.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging


class GameSystem(ABC):
    """Abstract base class for all game systems.
    
    Each system should:
    1. Initialize itself with required dependencies
    2. Update its state each frame
    3. Respond to game events
    4. Provide serializable state
    5. Load state from saves
    
    Example:
        class PrestigeSystem(GameSystem):
            def initialize(self, game_state):
                self.game_state = game_state
                self.prestige_level = 0
            
            def update(self, dt: float):
                # Update prestige calculations
                pass
            
            def on_event(self, event_type: str, data: dict):
                if event_type == "game_reset":
                    self.calculate_prestige()
    """
    
    def __init__(self, name: str, priority: int = 100):
        """Initialize game system.
        
        Args:
            name: Unique identifier for this system
            priority: Update priority (lower = earlier, 0-1000)
        """
        self.name = name
        self.priority = priority
        self.enabled = True
        self.logger = logging.getLogger(f"system.{name}")
        self._initialized = False
    
    @abstractmethod
    def initialize(self, game_state: Any, **dependencies):
        """Initialize the system with game state and dependencies.
        
        Called once when the system is registered. Use this to set up
        subscriptions to events, load initial data, etc.
        
        Args:
            game_state: Main GameState instance
            **dependencies: Other systems this one depends on
        
        Example:
            def initialize(self, game_state, event_bus=None, feature_manager=None):
                self.game_state = game_state
                self.event_bus = event_bus
                if self.event_bus:
                    self.event_bus.subscribe("incident_resolved", self.on_incident)
        """
        pass
    
    @abstractmethod
    def update(self, dt: float):
        """Update system state.
        
        Called every frame by the System Manager.
        
        Args:
            dt: Delta time since last update (seconds)
        
        Example:
            def update(self, dt: float):
                if not self.enabled:
                    return
                
                # Update cooldowns
                self.ability_cooldown -= dt
                
                # Process queued actions
                self.process_queue()
        """
        pass
    
    @abstractmethod
    def on_event(self, event_type: str, data: Dict[str, Any]):
        """Handle game events.
        
        Called by the Event Bus when subscribed events occur.
        
        Args:
            event_type: Type of event (e.g., "incident_resolved")
            data: Event data dictionary
        
        Example:
            def on_event(self, event_type: str, data: dict):
                if event_type == "specialist_leveled_up":
                    specialist_id = data["specialist_id"]
                    self.unlock_new_abilities(specialist_id)
        """
        pass
    
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Get serializable state for saving.
        
        Returns:
            Dictionary containing all state to persist
        
        Example:
            def get_state(self) -> dict:
                return {
                    "prestige_level": self.prestige_level,
                    "prestige_points": self.prestige_points,
                    "unlocked_bonuses": self.unlocked_bonuses
                }
        """
        pass
    
    @abstractmethod
    def set_state(self, state: Dict[str, Any]):
        """Load state from save data.
        
        Args:
            state: State dictionary from save file
        
        Example:
            def set_state(self, state: dict):
                self.prestige_level = state.get("prestige_level", 0)
                self.prestige_points = state.get("prestige_points", 0)
                self.unlocked_bonuses = state.get("unlocked_bonuses", [])
        """
        pass
    
    def enable(self):
        """Enable this system."""
        self.enabled = True
        self.logger.info(f"System {self.name} enabled")
    
    def disable(self):
        """Disable this system."""
        self.enabled = False
        self.logger.info(f"System {self.name} disabled")
    
    def is_initialized(self) -> bool:
        """Check if system has been initialized.
        
        Returns:
            True if initialized
        """
        return self._initialized
    
    def mark_initialized(self):
        """Mark system as initialized."""
        self._initialized = True
    
    def get_dependencies(self) -> List[str]:
        """Get list of system names this system depends on.
        
        Override this to specify dependencies. System Manager will
        ensure dependencies are initialized first.
        
        Returns:
            List of system names (default: empty)
        
        Example:
            def get_dependencies(self) -> List[str]:
                return ["event_bus", "feature_manager", "idle_core"]
        """
        return []
    
    def get_required_features(self) -> List[str]:
        """Get list of feature flags required for this system.
        
        Override this to specify feature requirements. System Manager will
        only initialize if all required features are enabled.
        
        Returns:
            List of feature names (default: empty)
        
        Example:
            def get_required_features(self) -> List[str]:
                return ["prestige_system"]
        """
        return []
    
    def on_shutdown(self):
        """Called when system is being shut down.
        
        Use this to clean up resources, save data, unsubscribe from events.
        
        Example:
            def on_shutdown(self):
                if self.event_bus:
                    self.event_bus.unsubscribe_all(self.on_event)
                self.save_cache()
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get system information for debugging.
        
        Returns:
            Dictionary with system metadata
        """
        return {
            "name": self.name,
            "priority": self.priority,
            "enabled": self.enabled,
            "initialized": self._initialized,
            "dependencies": self.get_dependencies(),
            "required_features": self.get_required_features()
        }


class SimpleGameSystem(GameSystem):
    """Simplified base class for basic game systems.
    
    Use this when you don't need event handling or complex state management.
    Just override update() and you're good to go.
    
    Example:
        class AutoSaveSystem(SimpleGameSystem):
            def __init__(self):
                super().__init__("auto_save")
                self.save_timer = 0
            
            def update(self, dt: float):
                self.save_timer += dt
                if self.save_timer >= 60:  # Save every minute
                    self.game_state.save()
                    self.save_timer = 0
    """
    
    def __init__(self, name: str, priority: int = 100):
        super().__init__(name, priority)
        self.game_state = None
    
    def initialize(self, game_state: Any, **dependencies):
        """Initialize with game state."""
        self.game_state = game_state
        self.mark_initialized()
    
    def on_event(self, event_type: str, data: Dict[str, Any]):
        """Default: ignore events."""
        pass
    
    def get_state(self) -> Dict[str, Any]:
        """Default: no state to save."""
        return {}
    
    def set_state(self, state: Dict[str, Any]):
        """Default: no state to load."""
        pass


class EventDrivenGameSystem(GameSystem):
    """Base class for event-driven game systems.
    
    Automatically subscribes to specified events during initialization.
    
    Example:
        class AchievementSystem(EventDrivenGameSystem):
            def get_subscribed_events(self) -> List[str]:
                return ["incident_resolved", "specialist_leveled_up", "contract_completed"]
            
            def on_event(self, event_type: str, data: dict):
                if event_type == "incident_resolved":
                    self.check_achievement("speed_demon", data)
    """
    
    def __init__(self, name: str, priority: int = 100):
        super().__init__(name, priority)
        self.game_state = None
        self.event_bus = None
    
    def initialize(self, game_state: Any, **dependencies):
        """Initialize and subscribe to events."""
        self.game_state = game_state
        self.event_bus = dependencies.get("event_bus")
        
        if self.event_bus:
            for event_type in self.get_subscribed_events():
                self.event_bus.subscribe(event_type, self.on_event)
        
        self.mark_initialized()
    
    @abstractmethod
    def get_subscribed_events(self) -> List[str]:
        """Get list of events to subscribe to.
        
        Returns:
            List of event type strings
        """
        pass
    
    def on_shutdown(self):
        """Unsubscribe from all events."""
        if self.event_bus:
            for event_type in self.get_subscribed_events():
                self.event_bus.unsubscribe(event_type, self.on_event)
    
    def update(self, dt: float):
        """Default: event-driven systems don't need updates."""
        pass
    
    def get_state(self) -> Dict[str, Any]:
        """Default: no state to save."""
        return {}
    
    def set_state(self, state: Dict[str, Any]):
        """Default: no state to load."""
        pass
