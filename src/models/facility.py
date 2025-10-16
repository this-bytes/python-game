"""Facility model representing upgradeable office infrastructure.

Facilities provide passive bonuses to firm capabilities like specialist capacity,
XP gain, incident handling, and specialist fatigue reduction.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Facility:
    """Represents an upgradeable facility in the cybersecurity firm."""

    id: str
    name: str
    description: str
    facility_type: str  # OFFICE_SPACE, SERVER_ROOM, TRAINING_CENTER, BREAK_ROOM
    level: int = 1
    max_level: int = 10
    upgrade_cost: int = 1000  # Base cost
    bonuses: Dict[str, float] = field(default_factory=dict)  # Bonuses per level

    def can_upgrade(self) -> bool:
        """Check if facility can be upgraded.

        Returns:
            True if facility is below max level
        """
        return self.level < self.max_level

    def calculate_upgrade_cost(self) -> int:
        """Calculate cost to upgrade to next level.

        Cost formula: base_cost * (1.5 ** level)

        Returns:
            Upgrade cost in dollars
        """
        if not self.can_upgrade():
            return 0

        return int(self.upgrade_cost * (1.5**self.level))

    def upgrade(self) -> bool:
        """Upgrade facility to next level.

        Returns:
            True if upgraded, False if already at max level
        """
        if not self.can_upgrade():
            return False

        self.level += 1
        return True

    def calculate_total_bonuses(self) -> Dict[str, float]:
        """Calculate total bonuses from current facility level.

        Returns:
            Dictionary of bonus types to total bonus values
        """
        total_bonuses = {}

        for bonus_type, bonus_per_level in self.bonuses.items():
            total_bonuses[bonus_type] = bonus_per_level * self.level

        return total_bonuses

    def get_bonus_value(self, bonus_type: str) -> float:
        """Get total bonus value for a specific bonus type.

        Args:
            bonus_type: The type of bonus to get

        Returns:
            Total bonus value (0 if type not found)
        """
        bonus_per_level = self.bonuses.get(bonus_type, 0.0)
        return bonus_per_level * self.level

    def get_upgrade_preview(self) -> Dict:
        """Get preview of bonuses after upgrading.

        Returns:
            Dictionary with current and next level bonus information
        """
        if not self.can_upgrade():
            return {
                "can_upgrade": False,
                "message": "Facility already at max level",
            }

        current_bonuses = self.calculate_total_bonuses()
        next_bonuses = {}
        for bonus_type, bonus_per_level in self.bonuses.items():
            next_bonuses[bonus_type] = bonus_per_level * (self.level + 1)

        return {
            "can_upgrade": True,
            "current_level": self.level,
            "next_level": self.level + 1,
            "upgrade_cost": self.calculate_upgrade_cost(),
            "current_bonuses": current_bonuses,
            "next_bonuses": next_bonuses,
        }

    def to_dict(self) -> Dict:
        """Convert facility to dictionary for serialization.

        Returns:
            Dictionary representation of the facility
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "facility_type": self.facility_type,
            "level": self.level,
            "max_level": self.max_level,
            "upgrade_cost": self.upgrade_cost,
            "bonuses": self.bonuses.copy(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Facility":
        """Create Facility from dictionary.

        Args:
            data: Dictionary containing facility data

        Returns:
            New Facility instance
        """
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            facility_type=data["facility_type"],
            level=data.get("level", 1),
            max_level=data["max_level"],
            upgrade_cost=data["upgrade_cost"],
            bonuses=data["bonuses"].copy(),
        )

    def __repr__(self) -> str:
        """String representation of facility."""
        return (
            f"Facility(id='{self.id}', name='{self.name}', "
            f"level={self.level}/{self.max_level})"
        )
