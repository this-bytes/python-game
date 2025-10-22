"""Game Loop Plugin for managing daily/monthly cycles and phase transitions.

Implements the 6-step core game loop:
1. THREATS SPAWN FOR EACH CLIENT (Morning)
2. PLAYER ASSIGNS SPECIALISTS TO INCIDENTS (Day)
3. RESOLUTION HAPPENS (Evening)
4. CONSEQUENCES & FEEDBACK (Evening)
5. END OF DAY: BUDGET UPDATE (Night)
6. REPEAT

This plugin orchestrates the passage of time in the game, managing phase
transitions and triggering appropriate events for other systems.
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional

from src.core.game_system import GameSystem
from src.core.event_bus import get_event_bus

logger = logging.getLogger(__name__)


class GamePhase(Enum):
    """Phases within a single day."""
    MORNING = 1      # 0-25%: Incidents spawn
    DAY = 2          # 25-75%: Player assigns incidents
    EVENING = 3      # 75-95%: Incidents resolve
    NIGHT = 4        # 95-100%: Budget calculations & next day prep


class GameLoopPlugin(GameSystem):
    """Plugin managing daily cycles and phase transitions.
    
    Responsibilities:
        - Track current phase within the day
        - Manage time progression
        - Trigger phase transitions with events
        - Calculate day/month boundaries
        - Emit events for incident generation, resolution, budget calc
        - Coordinate with other plugins (Budget, SLA, etc.)
    
    Design:
        - Each "day" is subdivided into 4 phases
        - Phases transition automatically based on time
        - Events emitted at each transition for plugins to respond
        - Can be paused/resumed without losing state
    """
    
    def __init__(self):
        """Initialize game loop plugin."""
        super().__init__()
        self._event_bus = get_event_bus()
        self._current_phase = GamePhase.MORNING
        self._current_day = 1
        self._current_month = 1
        self._time_in_phase = 0.0
        self._phase_duration_seconds = 600.0  # 10 minutes per phase (adjustable)
        self._subscription_ids = []
    
    def get_name(self) -> str:
        """Get plugin name."""
        return "GameLoopPlugin"
    
    def get_feature_id(self) -> str:
        """Get feature flag ID."""
        return "game_loop_system"
    
    def initialize(self, game_state) -> None:
        """Initialize game loop plugin.
        
        Sets up phase tracking and loads configuration.
        
        Args:
            game_state: Current game state
        """
        logger.info("[GAME_LOOP] Initializing game loop system")
        
        # Load configuration (if available)
        self._load_configuration(game_state)
        
        # Reset to morning of day 1
        self._current_phase = GamePhase.MORNING
        self._current_day = 1
        self._current_month = 1
        self._time_in_phase = 0.0
        
        # Subscribe to relevant events
        self._subscription_ids = [
            self._event_bus.subscribe("game_paused", self._on_game_paused),
            self._event_bus.subscribe("game_resumed", self._on_game_resumed),
        ]
        
        # Mark as initialized
        self._initialized = True
        
        # Emit initialization event
        self._event_bus.publish("game_loop_initialized", {
            "day": self._current_day,
            "month": self._current_month,
            "phase": self._current_phase.name,
        }, source="game_loop")
        
        logger.info(f"[GAME_LOOP] Initialization complete: day={self._current_day}, "
                   f"month={self._current_month}, phase={self._current_phase.name}")
    
    def update(self, game_state, delta_time: float) -> None:
        """Update game loop with time progression.
        
        Advances time and triggers phase transitions as needed.
        
        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update (seconds)
        """
        if not self._initialized:
            return
        
        # Accumulate time in current phase
        self._time_in_phase += delta_time
        
        # Check if phase should transition
        if self._time_in_phase >= self._phase_duration_seconds:
            self._transition_phase(game_state)
    
    def shutdown(self, game_state) -> None:
        """Shutdown game loop plugin and cleanup resources.
        
        Unsubscribes from events and saves state if needed.
        
        Args:
            game_state: Current game state
        """
        logger.info("[GAME_LOOP] Shutting down game loop system")
        
        # Unsubscribe from events
        for subscription_id in self._subscription_ids:
            self._event_bus.unsubscribe(subscription_id)
        self._subscription_ids.clear()
        
        logger.info("[GAME_LOOP] Shutdown complete")
    
    def save_state(self, game_state) -> Dict[str, Any]:
        """Save game loop state for persistence.
        
        Preserves day, month, phase, and time tracking across saves.
        
        Returns:
            Dictionary containing game loop state
        """
        return {
            "current_day": self._current_day,
            "current_month": self._current_month,
            "current_phase": self._current_phase.name,
            "time_in_phase": self._time_in_phase,
        }
    
    def load_state(self, game_state, state_data: Dict[str, Any]) -> None:
        """Load game loop state from saved data.
        
        Restores day, month, phase, and time tracking from save.
        
        Args:
            game_state: Current game state
            state_data: Previously saved state data
        """
        self._current_day = state_data.get("current_day", 1)
        self._current_month = state_data.get("current_month", 1)
        
        phase_name = state_data.get("current_phase", "MORNING")
        self._current_phase = GamePhase[phase_name]
        
        self._time_in_phase = state_data.get("time_in_phase", 0.0)
        
        logger.info(f"[GAME_LOOP] State loaded: day={self._current_day}, "
                   f"month={self._current_month}, phase={self._current_phase.name}")
    
    def get_current_phase(self) -> GamePhase:
        """Get current game phase.
        
        Returns:
            Current phase (MORNING, DAY, EVENING, NIGHT)
        """
        return self._current_phase
    
    def get_current_day(self) -> int:
        """Get current day number.
        
        Returns:
            Current day (1-indexed)
        """
        return self._current_day
    
    def get_current_month(self) -> int:
        """Get current month number.
        
        Returns:
            Current month (1-indexed)
        """
        return self._current_month
    
    def get_time_in_phase(self) -> float:
        """Get elapsed time in current phase.
        
        Returns:
            Time elapsed in phase (seconds)
        """
        return self._time_in_phase
    
    # ===== PRIVATE METHODS =====
    
    def _load_configuration(self, game_state) -> None:
        """Load game loop configuration from game state.
        
        Args:
            game_state: Current game state
        """
        # Load phase duration from game config if available
        if hasattr(game_state, 'game_config'):
            game_loop_config = game_state.game_config.get("game_loop", {})
            self._phase_duration_seconds = game_loop_config.get("phase_duration_seconds", 600.0)
    
    def _transition_phase(self, game_state) -> None:
        """Transition to next phase in the day cycle.
        
        Handles phase-specific logic:
        - MORNING → spawn incidents
        - DAY → player assigns
        - EVENING → resolve incidents
        - NIGHT → calculate budget & prepare next day
        
        Args:
            game_state: Current game state
        """
        previous_phase = self._current_phase
        
        # Transition based on current phase
        if self._current_phase == GamePhase.MORNING:
            self._current_phase = GamePhase.DAY
            self._emit_phase_event(game_state, "morning_ended")
            self._emit_phase_event(game_state, "day_started")
        
        elif self._current_phase == GamePhase.DAY:
            self._current_phase = GamePhase.EVENING
            self._emit_phase_event(game_state, "day_ended")
            self._emit_phase_event(game_state, "evening_started")
        
        elif self._current_phase == GamePhase.EVENING:
            self._current_phase = GamePhase.NIGHT
            self._emit_phase_event(game_state, "evening_ended")
            self._emit_phase_event(game_state, "night_started")
        
        elif self._current_phase == GamePhase.NIGHT:
            # End of day - advance to next day
            self._current_day += 1
            
            # Check if month boundary
            if self._current_day > 30:  # 30 days per month
                self._current_day = 1
                self._current_month += 1
                self._emit_phase_event(game_state, "month_ended")
            
            # Transition to next morning
            self._current_phase = GamePhase.MORNING
            self._emit_phase_event(game_state, "night_ended")
            self._emit_phase_event(game_state, "day_started", {
                "day": self._current_day,
                "month": self._current_month
            })
        
        # Reset time counter for next phase
        self._time_in_phase = 0.0
        
        logger.info(f"[GAME_LOOP] Phase transition: {previous_phase.name} → "
                   f"{self._current_phase.name} (day={self._current_day}, "
                   f"month={self._current_month})")
    
    def _emit_phase_event(self, game_state, event_type: str, 
                         extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Emit event for phase transition.
        
        Args:
            game_state: Current game state
            event_type: Type of event to emit
            extra_data: Additional event data (optional)
        """
        event_data = {
            "phase": self._current_phase.name,
            "day": self._current_day,
            "month": self._current_month,
            "game_state_money": game_state.current_money,
            "game_state_specialists": len(game_state.specialists),
            "game_state_clients": len(game_state.clients),
        }
        
        if extra_data:
            event_data.update(extra_data)
        
        self._event_bus.publish(event_type, event_data, source="game_loop")
    
    def _on_game_paused(self, event) -> None:
        """Handle game paused event.
        
        Args:
            event: Event data
        """
        logger.info(f"[GAME_LOOP] Game paused at {self._current_phase.name}")
    
    def _on_game_resumed(self, event) -> None:
        """Handle game resumed event.
        
        Args:
            event: Event data
        """
        logger.info(f"[GAME_LOOP] Game resumed, continuing from {self._current_phase.name}")
