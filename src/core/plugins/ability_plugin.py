"""AbilityPlugin - Specialist Ability Management System.

Plugin wrapper for AbilitySystem providing ability activation, cooldown management,
effect application, and unlocking mechanics. Integrates with game events to automatically
unlock abilities on level-up and manage ability effects.

Features:
- Ability activation with cooldowns
- Temporary stat buffs and effects
- Specialty-based ability restrictions
- Level-based ability unlocking
- Active effect tracking and expiration
"""

from typing import Dict, Any, List, Optional
from src.core.game_system import GameSystem
from src.core.ability_system import AbilitySystem
from src.core.event_bus import get_event_bus, Event
from src.models.specialist_ability import SpecialistAbility


class AbilityPlugin(GameSystem):
    """Plugin wrapper for AbilitySystem with GameSystem integration."""

    def __init__(self):
        """Initialize ability plugin."""
        super().__init__()
        self._ability_system = None  # Will be initialized with game config
        self._event_bus = get_event_bus()
        self._subscription_ids: List[str] = []

    def get_name(self) -> str:
        """Get plugin name."""
        return "AbilityPlugin"

    def get_feature_id(self) -> str:
        """Get feature flag ID for ability system."""
        return "ability_system"

    def initialize(self, game_state) -> None:
        """Initialize ability plugin.

        Args:
            game_state: Current game state
        """
        # Load abilities configuration directly from abilities.json
        from src.utils.json_loader import JSONLoader
        json_loader = JSONLoader()
        abilities_config = json_loader.load_data("abilities.json")
        
        self._ability_system = AbilitySystem(abilities_config)

        # Subscribe to relevant events
        self._subscription_ids = [
            self._event_bus.subscribe("specialist_level_up", self._on_specialist_level_up),
            self._event_bus.subscribe("ability_activate", self._on_ability_activate),
        ]

    def update(self, game_state, delta_time: float) -> None:
        """Update ability plugin.

        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update
        """
        # Update ability cooldowns and effects for all specialists
        if hasattr(game_state, 'specialists'):
            for specialist in game_state.specialists:
                if self._ability_system:
                    self._ability_system.update_cooldowns(specialist, delta_time)
                    self._ability_system.update_active_effects(specialist, delta_time)

    def shutdown(self, game_state) -> None:
        """Shutdown ability plugin.

        Args:
            game_state: Current game state
        """
        # Unsubscribe from all events
        for subscription_id in self._subscription_ids:
            self._event_bus.unsubscribe(subscription_id)
        self._subscription_ids.clear()

    def save_state(self, game_state) -> Dict[str, Any]:
        """Save ability plugin state.

        Args:
            game_state: Current game state

        Returns:
            State data to save
        """
        # Ability state is stored in specialists (abilities, cooldowns, active_effects)
        # No additional state to save for the system itself
        return {}

    def load_state(self, game_state, state_data: Dict[str, Any]) -> None:
        """Load ability plugin state.

        Args:
            game_state: Current game state
            state_data: Previously saved state data
        """
        # Ability state is loaded with specialists
        # No additional state to load
        pass

    def _on_specialist_level_up(self, event: Event) -> None:
        """Handle specialist level up event for ability unlocking.

        Args:
            event: Specialist level up event
        """
        specialist = event.data.get("specialist")
        new_level = event.data.get("new_level")

        if specialist and new_level and self._ability_system:
            unlocked_abilities = self._ability_system.unlock_abilities_for_level(specialist, new_level)

            if unlocked_abilities:
                # Publish abilities unlocked event
                self._event_bus.publish("abilities_unlocked", {
                    "specialist_id": getattr(specialist, 'id', None),
                    "new_level": new_level,
                    "unlocked_abilities": unlocked_abilities,
                })

    def _on_ability_activate(self, event: Event) -> None:
        """Handle ability activation event.

        Args:
            event: Ability activation event
        """
        specialist = event.data.get("specialist")
        ability_id = event.data.get("ability_id")
        target = event.data.get("target")

        if specialist and ability_id and self._ability_system:
            result = self._ability_system.activate_ability(specialist, ability_id, target)

            # Publish ability activated event
            self._event_bus.publish("ability_activated", {
                "specialist_id": getattr(specialist, 'id', None),
                "ability_id": ability_id,
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "effect_applied": result.get("effect_applied"),
            })

    # Public API methods for external access
    def activate_ability(self, specialist, ability_id: str, target=None) -> Dict[str, Any]:
        """Activate an ability for a specialist.

        Args:
            specialist: The specialist activating the ability
            ability_id: ID of the ability to activate
            target: Optional target (e.g., incident for certain abilities)

        Returns:
            Dictionary containing activation result
        """
        if self._ability_system:
            return self._ability_system.activate_ability(specialist, ability_id, target)
        return {"success": False, "message": "Ability system not initialized"}

    def get_available_abilities(self, specialist) -> List[str]:
        """Get list of abilities that can be activated.

        Args:
            specialist: The specialist to check abilities for

        Returns:
            List of ability IDs that are off cooldown and unlocked
        """
        if self._ability_system:
            return self._ability_system.get_available_abilities(specialist)
        return []

    def apply_active_effects(self, specialist, incident=None) -> Dict[str, float]:
        """Calculate stat modifiers from active effects.

        Args:
            specialist: The specialist to calculate modifiers for
            incident: Optional incident being worked on (for pending effects)

        Returns:
            Dictionary of stat modifiers: {"speed": 1.5, "accuracy": 1.2, etc.}
        """
        if self._ability_system:
            return self._ability_system.apply_active_effects(specialist, incident)
        return {"speed": 1.0, "accuracy": 1.0, "reward": 1.0}

    def get_ability(self, ability_id: str) -> Optional[SpecialistAbility]:
        """Get an ability by ID.

        Args:
            ability_id: The ability ID to get

        Returns:
            SpecialistAbility or None if not found
        """
        if self._ability_system:
            return self._ability_system.get_ability(ability_id)
        return None

    def unlock_abilities_for_level(self, specialist, level: int) -> List[str]:
        """Unlock abilities that become available at a specific level.

        Args:
            specialist: The specialist to unlock abilities for
            level: The level reached

        Returns:
            List of newly unlocked ability IDs
        """
        if self._ability_system:
            return self._ability_system.unlock_abilities_for_level(specialist, level)
        return []

    def update_cooldowns(self, specialist, delta_time: float) -> None:
        """Update ability cooldowns for a specialist.

        Args:
            specialist: The specialist to update cooldowns for
            delta_time: Time elapsed in seconds
        """
        if self._ability_system:
            self._ability_system.update_cooldowns(specialist, delta_time)

    def update_active_effects(self, specialist, delta_time: float) -> None:
        """Update active ability effects and remove expired ones.

        Args:
            specialist: The specialist to update effects for
            delta_time: Time elapsed in seconds
        """
        if self._ability_system:
            self._ability_system.update_active_effects(specialist, delta_time)