"""EquipmentPlugin - Equipment Management System.

Plugin wrapper for EquipmentSystem providing equipment drops, equipping, stat calculations,
and upgrade mechanics. Integrates with game events to automatically drop equipment on incident completion.

Features:
- Random equipment drops based on incident difficulty
- Equipment equipping and stat bonuses
- Inventory management
- Equipment upgrade system
- Rarity-based drop rates
"""

from typing import Dict, Any, List, Optional
from src.core.game_system import GameSystem
from src.core.equipment_system import EquipmentSystem
from src.core.event_bus import get_event_bus, Event
from src.models.equipment import Equipment


class EquipmentPlugin(GameSystem):
    """Plugin wrapper for EquipmentSystem with GameSystem integration."""

    def __init__(self):
        """Initialize equipment plugin."""
        super().__init__()
        self._equipment_system = None  # Will be initialized with game config
        self._event_bus = get_event_bus()
        self._subscription_ids: List[str] = []

    def get_name(self) -> str:
        """Get plugin name."""
        return "EquipmentPlugin"

    def get_feature_id(self) -> str:
        """Get feature flag ID for equipment system."""
        return "equipment_system"

    def initialize(self, game_state) -> None:
        """Initialize equipment plugin.

        Args:
            game_state: Current game state
        """
        # Initialize equipment system with game config
        game_config = getattr(game_state, 'config', {})
        equipment_config = game_config.get('equipment', {})
        self._equipment_system = EquipmentSystem(equipment_config)

        # Subscribe to relevant events
        self._subscription_ids = [
            self._event_bus.subscribe("incident_completed", self._on_incident_completed),
            self._event_bus.subscribe("equipment_equip", self._on_equip_item),
            self._event_bus.subscribe("equipment_unequip", self._on_unequip_item),
            self._event_bus.subscribe("equipment_add_to_inventory", self._on_add_to_inventory),
            self._event_bus.subscribe("equipment_remove_from_inventory", self._on_remove_from_inventory),
            self._event_bus.subscribe("equipment_upgrade", self._on_upgrade_equipment),
        ]

    def update(self, game_state, delta_time: float) -> None:
        """Update equipment plugin.

        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update
        """
        # Equipment system is event-driven, no continuous updates needed
        pass

    def shutdown(self, game_state) -> None:
        """Shutdown equipment plugin.

        Args:
            game_state: Current game state
        """
        # Unsubscribe from all events
        for subscription_id in self._subscription_ids:
            self._event_bus.unsubscribe(subscription_id)
        self._subscription_ids.clear()

    def save_state(self, game_state) -> Dict[str, Any]:
        """Save equipment plugin state.

        Args:
            game_state: Current game state

        Returns:
            State data to save
        """
        # Equipment system state is stored in specialists and game state
        # No additional state to save for the system itself
        return {}

    def load_state(self, game_state, state_data: Dict[str, Any]) -> None:
        """Load equipment plugin state.

        Args:
            game_state: Current game state
            state_data: Previously saved state data
        """
        # Equipment system state is loaded with specialists
        # No additional state to load
        pass

    def _on_incident_completed(self, event: Event) -> None:
        """Handle incident completion event for equipment drops.

        Args:
            event: Incident completion event
        """
        incident = event.data.get("incident")
        success = event.data.get("success", True)
        specialist = event.data.get("specialist")

        if incident and success and specialist and self._equipment_system:
            # Generate equipment drop
            incident_difficulty = getattr(incident, 'difficulty', 1)
            dropped_equipment = self._equipment_system.generate_equipment_drop(incident_difficulty)

            if dropped_equipment:
                # Add to specialist's inventory
                added = self._equipment_system.add_to_inventory(specialist, dropped_equipment)

                if added:
                    # Publish equipment drop event
                    self._event_bus.publish("equipment_dropped", {
                        "specialist_id": getattr(specialist, 'id', None),
                        "equipment_id": dropped_equipment.id,
                        "equipment_name": dropped_equipment.name,
                        "rarity": dropped_equipment.rarity,
                        "incident_difficulty": incident_difficulty,
                    })

    def _on_equip_item(self, event: Event) -> None:
        """Handle equip item event.

        Args:
            event: Equip item event
        """
        specialist = event.data.get("specialist")
        equipment_id = event.data.get("equipment_id")

        if specialist and equipment_id and self._equipment_system:
            equipment = self._equipment_system.get_equipment(equipment_id)
            if equipment:
                success = self._equipment_system.equip_item(specialist, equipment)

                if success:
                    # Publish equipment equipped event
                    self._event_bus.publish("equipment_equipped", {
                        "specialist_id": getattr(specialist, 'id', None),
                        "equipment_id": equipment.id,
                        "equipment_name": equipment.name,
                        "slot": equipment.equipment_type.lower(),
                    })

    def _on_unequip_item(self, event: Event) -> None:
        """Handle unequip item event.

        Args:
            event: Unequip item event
        """
        specialist = event.data.get("specialist")
        slot = event.data.get("slot")

        if specialist and slot and self._equipment_system:
            unequipped_equipment = self._equipment_system.unequip_item(specialist, slot)

            if unequipped_equipment:
                # Publish equipment unequipped event
                self._event_bus.publish("equipment_unequipped", {
                    "specialist_id": getattr(specialist, 'id', None),
                    "equipment_id": unequipped_equipment.id,
                    "equipment_name": unequipped_equipment.name,
                    "slot": slot,
                })

    def _on_add_to_inventory(self, event: Event) -> None:
        """Handle add to inventory event.

        Args:
            event: Add to inventory event
        """
        specialist = event.data.get("specialist")
        equipment_id = event.data.get("equipment_id")

        if specialist and equipment_id and self._equipment_system:
            equipment = self._equipment_system.get_equipment(equipment_id)
            if equipment:
                added = self._equipment_system.add_to_inventory(specialist, equipment)

                if added:
                    # Publish equipment added event
                    self._event_bus.publish("equipment_added_to_inventory", {
                        "specialist_id": getattr(specialist, 'id', None),
                        "equipment_id": equipment.id,
                        "equipment_name": equipment.name,
                    })

    def _on_remove_from_inventory(self, event: Event) -> None:
        """Handle remove from inventory event.

        Args:
            event: Remove from inventory event
        """
        specialist = event.data.get("specialist")
        equipment_id = event.data.get("equipment_id")

        if specialist and equipment_id and self._equipment_system:
            removed = self._equipment_system.remove_from_inventory(specialist, equipment_id)

            if removed:
                # Publish equipment removed event
                self._event_bus.publish("equipment_removed_from_inventory", {
                    "specialist_id": getattr(specialist, 'id', None),
                    "equipment_id": equipment_id,
                })

    def _on_upgrade_equipment(self, event: Event) -> None:
        """Handle upgrade equipment event.

        Args:
            event: Upgrade equipment event
        """
        equipment_ids = event.data.get("equipment_ids", [])

        if equipment_ids and self._equipment_system:
            upgraded_equipment = self._equipment_system.upgrade_equipment(equipment_ids)

            if upgraded_equipment:
                # Publish equipment upgraded event
                self._event_bus.publish("equipment_upgraded", {
                    "equipment_ids": equipment_ids,
                    "upgraded_equipment_id": upgraded_equipment.id,
                    "upgraded_equipment_name": upgraded_equipment.name,
                    "rarity": upgraded_equipment.rarity,
                })

    # Public API methods for external access
    def generate_equipment_drop(self, incident_difficulty: int, rarity_boost: float = 0.0) -> Optional[Equipment]:
        """Generate a random equipment drop.

        Args:
            incident_difficulty: Difficulty of the resolved incident (1-5)
            rarity_boost: Additional boost to rarity chance (0.0-1.0)

        Returns:
            Equipment instance or None if no drop
        """
        if self._equipment_system:
            return self._equipment_system.generate_equipment_drop(incident_difficulty, rarity_boost)
        return None

    def equip_item(self, specialist, equipment: Equipment) -> bool:
        """Equip an item to a specialist.

        Args:
            specialist: The specialist to equip the item to
            equipment: The equipment to equip

        Returns:
            True if successful, False otherwise
        """
        if self._equipment_system:
            return self._equipment_system.equip_item(specialist, equipment)
        return False

    def unequip_item(self, specialist, slot: str) -> Optional[Equipment]:
        """Unequip an item from a slot.

        Args:
            specialist: The specialist to unequip from
            slot: The equipment slot to unequip

        Returns:
            The unequipped Equipment or None if slot was empty
        """
        if self._equipment_system:
            return self._equipment_system.unequip_item(specialist, slot)
        return None

    def calculate_total_stats(self, specialist):
        """Calculate total stats including equipment bonuses.

        Args:
            specialist: The specialist to calculate stats for

        Returns:
            SpecialistStats with equipment bonuses applied
        """
        if self._equipment_system:
            return self._equipment_system.calculate_total_stats(specialist)
        return specialist.stats

    def get_equipped_items(self, specialist) -> Dict[str, Equipment]:
        """Get all equipped equipment.

        Args:
            specialist: The specialist to get equipment for

        Returns:
            Dictionary mapping slot to Equipment instance
        """
        if self._equipment_system:
            return self._equipment_system.get_equipped_items(specialist)
        return {}

    def get_equipment(self, equipment_id: str) -> Optional[Equipment]:
        """Get equipment by ID.

        Args:
            equipment_id: The equipment ID

        Returns:
            Equipment instance or None if not found
        """
        if self._equipment_system:
            return self._equipment_system.get_equipment(equipment_id)
        return None

    def can_upgrade_equipment(self, equipment: Equipment) -> bool:
        """Check if equipment can be upgraded to a higher rarity.

        Args:
            equipment: The equipment to check

        Returns:
            True if equipment can be upgraded
        """
        if self._equipment_system:
            return self._equipment_system.can_upgrade_equipment(equipment)
        return False

    def get_upgrade_requirements(self, equipment: Equipment) -> Dict[str, Any]:
        """Get the requirements to upgrade equipment.

        Args:
            equipment: The equipment to upgrade

        Returns:
            Dictionary with upgrade requirements
        """
        if self._equipment_system:
            return self._equipment_system.get_upgrade_requirements(equipment)
        return {}

    def upgrade_equipment(self, equipment_ids: List[str]) -> Optional[Equipment]:
        """Upgrade equipment by combining multiple pieces.

        Args:
            equipment_ids: List of equipment IDs to combine

        Returns:
            New upgraded equipment or None if upgrade failed
        """
        if self._equipment_system:
            return self._equipment_system.upgrade_equipment(equipment_ids)
        return None