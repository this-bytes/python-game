"""Facility management system for upgrading office infrastructure.

The FacilitySystem handles facility upgrades and calculates aggregate bonuses
that affect gameplay mechanics.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from src.models.facility import Facility
    from src.models.game_state import GameState


class FacilitySystem:
    """Manages facility upgrades and bonus calculations."""

    def upgrade_facility(
        self, facility: "Facility", game_state: "GameState"
    ) -> bool:
        """Upgrade a facility if player can afford it.

        Args:
            facility: The facility to upgrade
            game_state: Current game state

        Returns:
            True if upgrade successful, False otherwise
        """
        if not facility.can_upgrade():
            return False

        upgrade_cost = facility.calculate_upgrade_cost()

        if game_state.current_money < upgrade_cost:
            return False

        # Deduct cost and upgrade
        game_state.current_money -= upgrade_cost
        facility.upgrade()

        return True

    def calculate_facility_bonuses(
        self, facilities: List["Facility"]
    ) -> Dict[str, float]:
        """Aggregate all facility bonuses into a single dictionary.

        Args:
            facilities: List of all facilities

        Returns:
            Dictionary mapping bonus types to total bonus values
        """
        aggregated_bonuses = {}

        for facility in facilities:
            facility_bonuses = facility.calculate_total_bonuses()

            for bonus_type, bonus_value in facility_bonuses.items():
                if bonus_type in aggregated_bonuses:
                    aggregated_bonuses[bonus_type] += bonus_value
                else:
                    aggregated_bonuses[bonus_type] = bonus_value

        return aggregated_bonuses

    def apply_facility_effects(self, game_state: "GameState") -> Dict[str, float]:
        """Calculate and return facility effects on game state.

        This doesn't directly modify game_state, but returns a dictionary of effects
        that can be applied by the game loop.

        Args:
            game_state: Current game state

        Returns:
            Dictionary of facility effects to apply
        """
        facilities = getattr(game_state, "facilities", [])
        bonuses = self.calculate_facility_bonuses(facilities)

        # Convert bonuses to game effects
        effects = {
            "max_specialists": 10,  # Base capacity
            "max_active_incidents": 50,  # Base capacity
            "xp_multiplier": 1.0,  # Base multiplier
            "incident_resolution_speed": 1.0,  # Base speed
            "fatigue_reduction": 0.0,  # Base reduction
        }

        # Add facility bonuses
        if "max_specialists" in bonuses:
            effects["max_specialists"] += int(bonuses["max_specialists"])

        if "max_active_incidents" in bonuses:
            effects["max_active_incidents"] += int(bonuses["max_active_incidents"])

        if "xp_multiplier" in bonuses:
            effects["xp_multiplier"] += bonuses["xp_multiplier"]

        if "incident_resolution_speed" in bonuses:
            effects["incident_resolution_speed"] += bonuses["incident_resolution_speed"]

        if "fatigue_reduction" in bonuses:
            effects["fatigue_reduction"] += bonuses["fatigue_reduction"]

        return effects

    def get_facility_by_id(
        self, facilities: List["Facility"], facility_id: str
    ) -> Optional["Facility"]:
        """Get facility by ID.

        Args:
            facilities: List of all facilities
            facility_id: ID of facility to find

        Returns:
            Facility instance or None if not found
        """
        return next((f for f in facilities if f.id == facility_id), None)

    def get_upgradeable_facilities(
        self, facilities: List["Facility"]
    ) -> List["Facility"]:
        """Get list of facilities that can be upgraded.

        Args:
            facilities: List of all facilities

        Returns:
            List of facilities below max level
        """
        return [f for f in facilities if f.can_upgrade()]

    def get_total_upgrade_cost(
        self, facilities: List["Facility"]
    ) -> int:
        """Calculate total cost to upgrade all upgradeable facilities once.

        Args:
            facilities: List of all facilities

        Returns:
            Total upgrade cost
        """
        total_cost = 0
        for facility in facilities:
            if facility.can_upgrade():
                total_cost += facility.calculate_upgrade_cost()

        return total_cost

    def get_max_level_facilities(
        self, facilities: List["Facility"]
    ) -> List["Facility"]:
        """Get list of facilities at max level.

        Args:
            facilities: List of all facilities

        Returns:
            List of max level facilities
        """
        return [f for f in facilities if not f.can_upgrade()]

    def get_facility_summary(self, facility: "Facility") -> Dict:
        """Get comprehensive summary of facility status.

        Args:
            facility: The facility to summarize

        Returns:
            Dictionary with facility information
        """
        bonuses = facility.calculate_total_bonuses()
        upgrade_preview = facility.get_upgrade_preview()

        return {
            "id": facility.id,
            "name": facility.name,
            "description": facility.description,
            "facility_type": facility.facility_type,
            "level": facility.level,
            "max_level": facility.max_level,
            "can_upgrade": facility.can_upgrade(),
            "upgrade_cost": (
                facility.calculate_upgrade_cost() if facility.can_upgrade() else 0
            ),
            "current_bonuses": bonuses,
            "upgrade_preview": upgrade_preview,
        }

    def get_all_facilities_summary(
        self, facilities: List["Facility"]
    ) -> Dict:
        """Get summary of all facilities and aggregate bonuses.

        Args:
            facilities: List of all facilities

        Returns:
            Dictionary with aggregate information
        """
        aggregate_bonuses = self.calculate_facility_bonuses(facilities)
        upgradeable_count = len(self.get_upgradeable_facilities(facilities))
        max_level_count = len(self.get_max_level_facilities(facilities))
        total_upgrade_cost = self.get_total_upgrade_cost(facilities)

        facility_summaries = [
            self.get_facility_summary(f) for f in facilities
        ]

        return {
            "total_facilities": len(facilities),
            "upgradeable_facilities": upgradeable_count,
            "max_level_facilities": max_level_count,
            "total_upgrade_cost": total_upgrade_cost,
            "aggregate_bonuses": aggregate_bonuses,
            "facilities": facility_summaries,
        }
