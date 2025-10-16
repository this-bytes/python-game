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

from src.core.plugin_system import GameSystem
from src.core.idle_core import IdleCore

logger = logging.getLogger(__name__)


class IdlePlugin(GameSystem):
    """Plugin wrapper for idle game mechanics."""
    
    def __init__(self, event_bus):
        super().__init__(event_bus, "idle_core")
        self.idle_core = IdleCore()
        self._game_state = None
    
    def initialize(self) -> None:
        """Initialize the idle plugin."""
        logger.info("Initializing Idle Core Plugin...")
        
        # Subscribe to events that trigger auto-assignment
        self.event_bus.subscribe("incident_generated", self._on_incident_generated)
        self.event_bus.subscribe("specialist_available", self._on_specialist_available)
        
        # Subscribe to game state updates
        self.event_bus.subscribe("game_state_updated", self._on_game_state_updated)
        
        logger.info("Idle Core Plugin initialized - auto-assignment active")
    
    def update(self, dt: float) -> None:
        """Update idle mechanics each frame.
        
        Args:
            dt: Delta time in seconds
        """
        # Auto-assignment happens on events, not every frame
        # This keeps the system efficient
        pass
    
    def shutdown(self) -> None:
        """Shutdown the idle plugin."""
        logger.info("Shutting down Idle Core Plugin...")
        
        # Unsubscribe from events
        self.event_bus.unsubscribe("incident_generated", self._on_incident_generated)
        self.event_bus.unsubscribe("specialist_available", self._on_specialist_available)
        self.event_bus.unsubscribe("game_state_updated", self._on_game_state_updated)
        
        logger.info("Idle Core Plugin shut down")
    
    def get_state(self) -> Dict[str, Any]:
        """Get idle system state for saving."""
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
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """Restore idle system state."""
        if "config" in state:
            config = state["config"]
            self.idle_core.config.enabled = config.get("enabled", True)
            self.idle_core.config.prefer_synergies = config.get("prefer_synergies", True)
            self.idle_core.config.balance_workload = config.get("balance_workload", True)
            self.idle_core.config.respect_fatigue = config.get("respect_fatigue", True)
            self.idle_core.config.difficulty_threshold = config.get("difficulty_threshold", 5)
        
        if "stats" in state:
            self.idle_core.stats.update(state["stats"])
    
    def _on_incident_generated(self, event_data: Dict[str, Any]) -> None:
        """Handle new incident generation - try to auto-assign."""
        if not self._game_state:
            return
        
        logger.debug(f"New incident generated: {event_data.get('incident_id')}")
        
        # Try to auto-assign
        assignments = self.idle_core.auto_assign_incidents(self._game_state)
        
        # Emit events for each successful assignment
        for assignment in assignments:
            self.event_bus.emit("auto_assignment_triggered", assignment)
            logger.info(
                f"Auto-assigned incident {assignment['incident_id']} to "
                f"specialist {assignment['specialist_id']} "
                f"(quality: {assignment['match_quality']}, "
                f"synergy: {assignment['synergy_active']})"
            )
    
    def _on_specialist_available(self, event_data: Dict[str, Any]) -> None:
        """Handle specialist becoming available - check for pending incidents."""
        if not self._game_state:
            return
        
        logger.debug(f"Specialist available: {event_data.get('specialist_id')}")
        
        # Try to assign pending incidents to newly available specialist
        assignments = self.idle_core.auto_assign_incidents(self._game_state)
        
        for assignment in assignments:
            self.event_bus.emit("auto_assignment_triggered", assignment)
    
    def _on_game_state_updated(self, event_data: Dict[str, Any]) -> None:
        """Handle game state updates.
        
        The main game loop emits this event with the current game state.
        We cache it so we can use it in event handlers.
        """
        self._game_state = event_data.get("game_state")
