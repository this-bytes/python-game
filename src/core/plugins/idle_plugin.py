"""Idle Core Plugin - Auto-Assignment and Synergy System

This plugin wraps the existing IdleCore functionality into the plugin architecture.
It demonstrates how to migrate existing systems to the new plugin system.

Features:
- Automatic incident assignment to specialists
- Synergy-based bonuses for strategic depth
- Event-driven updates (no polling needed)
- Feature-flag controlled enable/disable
"""

from typing import Dict, Any
import logging

from src.core.game_system import GameSystem
from src.core.event_bus import get_event_bus
from src.core.idle_core import IdleCore
from src.models.game_state import GameState

logger = logging.getLogger(__name__)




class IdlePlugin(GameSystem):
    """Plugin wrapper for idle game mechanics."""
    
    def __init__(self):
        """Initialize the idle plugin."""
        super().__init__()
        self.idle_core = IdleCore()
        self._game_state = None
        self._event_bus = None
    
    def get_name(self) -> str:
        """Get the unique name of this system."""
        return "idle_core"
    
    def get_feature_id(self) -> str:
        """Get feature flag ID for this system."""
        return "idle_core"
    
    def initialize(self, game_state: GameState) -> None:
        """Initialize the idle plugin.
        
        Args:
            game_state: Current game state
        """
        logger.info("Initializing Idle Core Plugin...")
        
        self._game_state = game_state
        self._event_bus = get_event_bus()
        
        # Subscribe to events that trigger auto-assignment
        self._event_bus.subscribe("incident_generated", self._on_incident_generated)
        self._event_bus.subscribe("specialist_available", self._on_specialist_available)
        self._event_bus.subscribe("game_state_updated", self._on_game_state_updated)
        
        logger.info("Idle Core Plugin initialized - auto-assignment active")
    
    def update(self, game_state: GameState, delta_time: float) -> None:
        """Update idle mechanics each frame.
        
        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update (seconds)
        """
        # Auto-assignment happens on events, not every frame
        # This keeps the system efficient
        self._game_state = game_state
    
    def shutdown(self, game_state: GameState) -> None:
        """Shutdown the idle plugin.
        
        Args:
            game_state: Current game state
        """
        logger.info("Shutting down Idle Core Plugin...")
        
        if self._event_bus:
            # Unsubscribe from events
            self._event_bus.unsubscribe("incident_generated", self._on_incident_generated)
            self._event_bus.unsubscribe("specialist_available", self._on_specialist_available)
            self._event_bus.unsubscribe("game_state_updated", self._on_game_state_updated)
        
        logger.info("Idle Core Plugin shut down")
    
    def save_state(self, game_state: GameState) -> Dict[str, Any]:
        """Get idle system state for saving.
        
        Args:
            game_state: Current game state
            
        Returns:
            State dictionary for persistence
        """
        return {
            "config": {
                "enabled": self.idle_core.config.enabled,
                "prefer_synergies": self.idle_core.config.prefer_synergies,
                "balance_workload": self.idle_core.config.balance_workload,
                "respect_fatigue": self.idle_core.config.respect_fatigue,
                "difficulty_threshold": self.idle_core.config.difficulty_threshold
            },
            "stats": self.idle_core.stats.copy()
        }
    
    def load_state(self, game_state: GameState, state_data: Dict[str, Any]) -> None:
        """Restore idle system state.
        
        Args:
            game_state: Current game state
            state_data: Saved state to restore
        """
        if "config" in state_data:
            config = state_data["config"]
            self.idle_core.config.enabled = config.get("enabled", True)
            self.idle_core.config.prefer_synergies = config.get("prefer_synergies", True)
            self.idle_core.config.balance_workload = config.get("balance_workload", True)
            self.idle_core.config.respect_fatigue = config.get("respect_fatigue", True)
            self.idle_core.config.difficulty_threshold = config.get("difficulty_threshold", 5)
        
        if "stats" in state_data:
            self.idle_core.stats.update(state_data["stats"])
    
    def _on_incident_generated(self, event) -> None:
        """Handle new incident generation - try to auto-assign.
        
        Args:
            event: Event object from event bus
        """
        if not self._game_state:
            return
        
        logger.debug(f"New incident generated: {event.data.get('incident_id')}")
        
        # Try to auto-assign
        assignments = self.idle_core.auto_assign_incidents(self._game_state)
        
        # Publish events for each successful assignment
        for assignment in assignments:
            if self._event_bus:
                self._event_bus.publish("auto_assignment_triggered", assignment)
            logger.info(
                f"Auto-assigned incident {assignment['incident_id']} to "
                f"specialist {assignment['specialist_id']} "
                f"(quality: {assignment['match_quality']}, "
                f"synergy: {assignment['synergy_active']})"
            )
    
    def _on_specialist_available(self, event) -> None:
        """Handle specialist becoming available - check for pending incidents.
        
        Args:
            event: Event object from event bus
        """
        if not self._game_state:
            return
        
        logger.debug(f"Specialist available: {event.data.get('specialist_id')}")
        
        # Try to assign pending incidents to newly available specialist
        assignments = self.idle_core.auto_assign_incidents(self._game_state)
        
        for assignment in assignments:
            if self._event_bus:
                self._event_bus.publish("auto_assignment_triggered", assignment)
    
    def _on_game_state_updated(self, event) -> None:
        """Handle game state updates.
        
        The main game loop emits this event with the current game state.
        We cache it so we can use it in event handlers.
        
        Args:
            event: Event object from event bus
        """
        self._game_state = event.data.get("game_state")
