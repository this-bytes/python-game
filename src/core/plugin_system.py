"""Plugin System - Self-Contained Game Features

This module defines the plugin architecture that allows features to be
added/removed without modifying core game code. Each plugin is a self-contained
GameSystem that can subscribe to events, maintain state, and update each frame.

Example plugin implementation:
    
    class PrestigeSystem(GameSystem):
        def __init__(self, event_bus: EventBus):
            super().__init__(event_bus, "prestige_system")
            self.prestige_points = 0
            
        def initialize(self):
            self.event_bus.subscribe("prestige_triggered", self._on_prestige)
            
        def update(self, dt: float):
            # Called every frame
            pass
            
        def _on_prestige(self, event_data: dict):
            self.prestige_points += event_data.get("points", 0)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class GameSystem(ABC):
    """Base class for all game systems (plugins).
    
    Each system is a self-contained feature that can:
    - Subscribe to events via the event bus
    - Maintain its own state
    - Update each frame
    - Save/load state
    - Be enabled/disabled via feature flags
    """
    
    def __init__(self, event_bus, system_id: str):
        """Initialize game system.
        
        Args:
            event_bus: EventBus instance for subscribing to events
            system_id: Unique identifier for this system (e.g., "prestige_system")
        """
        self.event_bus = event_bus
        self.system_id = system_id
        self.enabled = False
        logger.info(f"System '{system_id}' created")
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the system.
        
        Called once when the system is first enabled. Use this to:
        - Subscribe to events
        - Load initial configuration
        - Set up internal state
        """
        pass
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """Update the system.
        
        Called every frame during the main game loop.
        
        Args:
            dt: Delta time in seconds since last update
        """
        pass
    
    def shutdown(self) -> None:
        """Shutdown the system.
        
        Called when the system is disabled. Use this to:
        - Unsubscribe from events
        - Clean up resources
        - Save state if needed
        
        Default implementation does nothing. Override if needed.
        """
        pass
    
    def get_state(self) -> Dict[str, Any]:
        """Get system state for saving.
        
        Returns:
            Dictionary containing all state that should be persisted
            
        Default implementation returns empty dict. Override to save state.
        """
        return {}
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """Restore system state from save data.
        
        Args:
            state: Dictionary containing saved state
            
        Default implementation does nothing. Override to load state.
        """
        pass
    
    def on_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle events that this system cares about.
        
        This is an optional convenience method. Systems can use this OR
        subscribe to events directly via event_bus.subscribe().
        
        Args:
            event_type: Type of event (e.g., "incident_resolved")
            event_data: Event payload data
            
        Default implementation does nothing.
        """
        pass


class SystemManager:
    """Manages all game systems (plugins).
    
    Responsibilities:
    - Register/unregister systems
    - Initialize/shutdown systems based on feature flags
    - Update all active systems each frame
    - Handle system dependencies
    - Coordinate save/load of system state
    """
    
    def __init__(self, event_bus, feature_manager):
        """Initialize system manager.
        
        Args:
            event_bus: EventBus for system communication
            feature_manager: FeatureManager for checking feature flags
        """
        self.event_bus = event_bus
        self.feature_manager = feature_manager
        self.systems: Dict[str, GameSystem] = {}
        self.update_order: list[str] = []  # Systems update in this order
        logger.info("SystemManager initialized")
    
    def register_system(self, system: GameSystem, dependencies: Optional[list[str]] = None) -> None:
        """Register a game system.
        
        Args:
            system: GameSystem instance to register
            dependencies: List of system IDs this system depends on
                         (dependent systems will be initialized first)
        """
        if system.system_id in self.systems:
            logger.warning(f"System '{system.system_id}' already registered, skipping")
            return
        
        self.systems[system.system_id] = system
        
        # Add to update order, respecting dependencies
        if dependencies:
            # Ensure dependencies are registered first
            for dep_id in dependencies:
                if dep_id not in self.systems:
                    logger.error(f"System '{system.system_id}' depends on '{dep_id}' which is not registered")
                    return
        
        # Simple dependency resolution - just append
        # TODO: Implement proper topological sort for complex dependency graphs
        self.update_order.append(system.system_id)
        
        logger.info(f"Registered system '{system.system_id}' with dependencies: {dependencies or []}")
    
    def unregister_system(self, system_id: str) -> None:
        """Unregister a game system.
        
        Args:
            system_id: ID of system to unregister
        """
        if system_id not in self.systems:
            logger.warning(f"System '{system_id}' not registered, cannot unregister")
            return
        
        system = self.systems[system_id]
        
        # Shutdown if enabled
        if system.enabled:
            self._shutdown_system(system)
        
        # Remove from tracking
        del self.systems[system_id]
        if system_id in self.update_order:
            self.update_order.remove(system_id)
        
        logger.info(f"Unregistered system '{system_id}'")
    
    def initialize_all(self) -> None:
        """Initialize all registered systems based on feature flags."""
        for system_id in self.update_order:
            system = self.systems[system_id]
            
            # Check feature flag
            feature_enabled = self.feature_manager.is_enabled(f"system_{system_id}")
            
            if feature_enabled and not system.enabled:
                self._initialize_system(system)
            elif not feature_enabled and system.enabled:
                self._shutdown_system(system)
    
    def _initialize_system(self, system: GameSystem) -> None:
        """Initialize a single system."""
        try:
            logger.info(f"Initializing system '{system.system_id}'...")
            system.initialize()
            system.enabled = True
            logger.info(f"System '{system.system_id}' initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize system '{system.system_id}': {e}", exc_info=True)
    
    def _shutdown_system(self, system: GameSystem) -> None:
        """Shutdown a single system."""
        try:
            logger.info(f"Shutting down system '{system.system_id}'...")
            system.shutdown()
            system.enabled = False
            logger.info(f"System '{system.system_id}' shut down successfully")
        except Exception as e:
            logger.error(f"Failed to shutdown system '{system.system_id}': {e}", exc_info=True)
    
    def update_all(self, dt: float) -> None:
        """Update all enabled systems.
        
        Args:
            dt: Delta time in seconds since last update
        """
        for system_id in self.update_order:
            system = self.systems[system_id]
            if system.enabled:
                try:
                    system.update(dt)
                except Exception as e:
                    logger.error(f"Error updating system '{system_id}': {e}", exc_info=True)
    
    def get_system(self, system_id: str) -> Optional[GameSystem]:
        """Get a system by ID.
        
        Args:
            system_id: ID of system to retrieve
            
        Returns:
            GameSystem instance or None if not found
        """
        return self.systems.get(system_id)
    
    def save_all_state(self) -> Dict[str, Dict[str, Any]]:
        """Get state from all systems for saving.
        
        Returns:
            Dictionary mapping system_id -> system_state
        """
        state = {}
        for system_id, system in self.systems.items():
            try:
                system_state = system.get_state()
                if system_state:  # Only save non-empty state
                    state[system_id] = system_state
            except Exception as e:
                logger.error(f"Error getting state from system '{system_id}': {e}", exc_info=True)
        return state
    
    def load_all_state(self, state: Dict[str, Dict[str, Any]]) -> None:
        """Restore state to all systems.
        
        Args:
            state: Dictionary mapping system_id -> system_state
        """
        for system_id, system_state in state.items():
            if system_id in self.systems:
                try:
                    self.systems[system_id].set_state(system_state)
                except Exception as e:
                    logger.error(f"Error loading state for system '{system_id}': {e}", exc_info=True)
            else:
                logger.warning(f"System '{system_id}' in save data but not registered")
