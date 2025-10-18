"""AutomationScript model representing automated actions in the game.

Automation scripts are unlocked by specialists at certain levels and automatically
perform actions like incident assignment or stat boosts when trigger conditions are met.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List
from enum import Enum
import time


class AutomationEffect(Enum):
    """Enum for automation script effects."""
    AUTO_ASSIGN = "auto_assign"
    SPEED_BOOST = "speed_boost"
    ACCURACY_BOOST = "accuracy_boost"
    XP_BOOST = "xp_boost"


@dataclass
class TriggerConditions:
    """Conditions that must be met for automation script to trigger."""
    max_difficulty: Optional[int] = None
    specialty_match: Optional[bool] = None
    specialist_available: Optional[bool] = None
    min_accuracy: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert trigger conditions to dictionary."""
        result = {}
        if self.max_difficulty is not None:
            result["max_difficulty"] = self.max_difficulty
        if self.specialty_match is not None:
            result["specialty_match"] = self.specialty_match
        if self.specialist_available is not None:
            result["specialist_available"] = self.specialist_available
        if self.min_accuracy is not None:
            result["min_accuracy"] = self.min_accuracy
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> 'TriggerConditions':
        """Create TriggerConditions from dictionary."""
        return cls(
            max_difficulty=data.get("max_difficulty"),
            specialty_match=data.get("specialty_match"),
            specialist_available=data.get("specialist_available"),
            min_accuracy=data.get("min_accuracy")
        )


@dataclass
class AutomationScript:
    """Represents an automation script that can be unlocked by specialists."""

    id: str
    name: str
    description: str
    required_level: int
    specialty: str
    trigger_conditions: TriggerConditions
    effect: str
    effect_magnitude: float = 1.0
    enabled: bool = True  # Whether this script is active
    trigger_logic: str = "AND"  # "AND" or "OR" for multi-condition evaluation
    chained_scripts: List[str] = field(default_factory=list)  # Execute these scripts after
    priority: int = 0  # Execution order (higher = first)
    cooldown_seconds: float = 0.0  # Cooldown between triggers
    last_triggered: float = 0.0  # Timestamp of last trigger
    upgrade_level: int = 0  # Upgrade level (reduces cooldown, improves efficiency)

    def __post_init__(self):
        """Validate and normalize data after initialization."""
        # Convert trigger_conditions dict to TriggerConditions if needed
        if isinstance(self.trigger_conditions, dict):
            self.trigger_conditions = TriggerConditions.from_dict(self.trigger_conditions)

        # Validate effect is supported
        if self.effect not in [e.value for e in AutomationEffect]:
            raise ValueError(f"Unsupported automation effect: {self.effect}")
        
        # Validate trigger_logic
        if self.trigger_logic not in ["AND", "OR"]:
            raise ValueError(f"Invalid trigger_logic: {self.trigger_logic}. Must be 'AND' or 'OR'.")

    def evaluate_triggers(self, specialist: Any, incident: Any) -> bool:
        """Evaluate if trigger conditions are met for this automation script.

        Args:
            specialist: The specialist to evaluate against
            incident: The incident to evaluate against

        Returns:
            True if all trigger conditions are met (AND logic) or any condition is met (OR logic)
        """
        conditions = self.trigger_conditions
        results = []

        # Check max_difficulty (ensure we compare ints)
        if conditions.max_difficulty is not None:
            try:
                incident_difficulty = int(incident.difficulty)
            except (TypeError, ValueError):
                # If difficulty can't be interpreted, fail this condition
                results.append(False)
            else:
                results.append(incident_difficulty <= conditions.max_difficulty)

        # Check specialty_match
        if conditions.specialty_match is not None and conditions.specialty_match:
            results.append(specialist.matches_specialty(incident.specialty_required))

        # Check specialist_available
        if conditions.specialist_available is not None and conditions.specialist_available:
            results.append(specialist.is_available())

        # Check min_accuracy
        if conditions.min_accuracy is not None:
            results.append(specialist.stats.accuracy >= conditions.min_accuracy)

        # If no conditions, return True
        if not results:
            return True

        # Apply trigger logic
        if self.trigger_logic == "AND":
            return all(results)
        else:  # OR
            return any(results)

    def apply_effect(self, specialist: Any, incident: Optional[Any] = None) -> Dict[str, Any]:
        """Apply the automation effect to the specialist and/or incident.

        Args:
            specialist: The specialist to apply effect to
            incident: The incident to apply effect to (for auto_assign)

        Returns:
            Dictionary containing effect results and metadata
        """
        effect_result = {
            "script_id": self.id,
            "effect_type": self.effect,
            "magnitude": self.effect_magnitude,
            "success": True,
            "details": {}
        }

        if self.effect == AutomationEffect.AUTO_ASSIGN.value:
            if incident is None:
                effect_result["success"] = False
                effect_result["details"]["error"] = "No incident provided for auto-assign"
                return effect_result

            # Attempt to assign incident to specialist
            assignment_success = specialist.assign_to_incident(incident.id)
            if assignment_success:
                incident.status = "assigned"
                incident.assigned_specialist_id = specialist.id
                incident.assignment_time = time.time()
                effect_result["details"]["assigned_incident"] = incident.id
                effect_result["details"]["assigned_specialist"] = specialist.id
            else:
                effect_result["success"] = False
                effect_result["details"]["error"] = "Specialist not available for assignment"

        elif self.effect == AutomationEffect.SPEED_BOOST.value:
            # Apply speed boost multiplier
            original_speed = specialist.stats.speed
            specialist.stats.speed *= self.effect_magnitude
            effect_result["details"]["original_speed"] = original_speed
            effect_result["details"]["new_speed"] = specialist.stats.speed

        elif self.effect == AutomationEffect.ACCURACY_BOOST.value:
            # Apply accuracy boost
            original_accuracy = specialist.stats.accuracy
            specialist.stats.accuracy = min(100.0, specialist.stats.accuracy * self.effect_magnitude)
            effect_result["details"]["original_accuracy"] = original_accuracy
            effect_result["details"]["new_accuracy"] = specialist.stats.accuracy

        elif self.effect == AutomationEffect.XP_BOOST.value:
            # Apply XP boost multiplier
            original_xp_bonus = specialist.stats.experience_bonus
            specialist.stats.experience_bonus *= self.effect_magnitude
            effect_result["details"]["original_xp_bonus"] = original_xp_bonus
            effect_result["details"]["new_xp_bonus"] = specialist.stats.experience_bonus

        return effect_result

    def is_on_cooldown(self, current_time: float) -> bool:
        """Check if the script is currently on cooldown.
        
        Args:
            current_time: Current game time
            
        Returns:
            True if on cooldown, False otherwise
        """
        if self.cooldown_seconds <= 0:
            return False
        
        time_since_last = current_time - self.last_triggered
        return time_since_last < self.get_effective_cooldown()
    
    def get_effective_cooldown(self) -> float:
        """Calculate effective cooldown considering upgrade level.
        
        Returns:
            Effective cooldown in seconds
        """
        # Each upgrade level reduces cooldown by 10%
        reduction = 1.0 - (self.upgrade_level * 0.10)
        reduction = max(0.1, reduction)  # Minimum 10% of original cooldown
        return self.cooldown_seconds * reduction
    
    def get_effective_magnitude(self) -> float:
        """Calculate effective magnitude considering upgrade level.
        
        Returns:
            Effective magnitude
        """
        # Each upgrade level increases efficiency by 5%
        bonus = 1.0 + (self.upgrade_level * 0.05)
        return self.effect_magnitude * bonus
    
    def calculate_upgrade_cost(self) -> int:
        """Calculate cost to upgrade this script to next level.
        
        Returns:
            Cost in money
        """
        base_cost = 1000
        # Cost increases exponentially with level
        return int(base_cost * (1.5 ** self.upgrade_level))
    
    def upgrade(self) -> bool:
        """Upgrade the automation script to next level.
        
        Returns:
            True if upgrade successful
        """
        max_upgrade_level = 10
        if self.upgrade_level >= max_upgrade_level:
            return False
        
        self.upgrade_level += 1
        return True
    
    def mark_triggered(self, current_time: float):
        """Mark the script as triggered at current time.
        
        Args:
            current_time: Current game time
        """
        self.last_triggered = current_time

    def can_be_used_by(self, specialist: Any) -> bool:
        """Check if a specialist can use this automation script.

        Args:
            specialist: The specialist to check

        Returns:
            True if specialist meets requirements, False otherwise
        """
        # Check level requirement
        if specialist.level < self.required_level:
            return False

        # Check specialty requirement (unless "Any")
        if self.specialty != "Any" and not specialist.matches_specialty(self.specialty):
            return False

        # Check if specialist has unlocked this script
        return specialist.has_automation_script(self.id)

    def to_dict(self) -> Dict:
        """Convert automation script to dictionary for serialization.

        Returns:
            Dictionary representation of the automation script
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "required_level": self.required_level,
            "specialty": self.specialty,
            "trigger_conditions": self.trigger_conditions.to_dict(),
            "effect": self.effect,
            "effect_magnitude": self.effect_magnitude,
            "enabled": self.enabled,
            "trigger_logic": self.trigger_logic,
            "chained_scripts": self.chained_scripts.copy(),
            "priority": self.priority,
            "cooldown_seconds": self.cooldown_seconds,
            "last_triggered": self.last_triggered,
            "upgrade_level": self.upgrade_level
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'AutomationScript':
        """Create AutomationScript from dictionary.

        Args:
            data: Dictionary containing automation script data

        Returns:
            New AutomationScript instance
        """
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            required_level=data["required_level"],
            specialty=data["specialty"],
            trigger_conditions=data["trigger_conditions"],  # Will be converted in __post_init__
            effect=data["effect"],
            effect_magnitude=data.get("effect_magnitude", 1.0),
            enabled=data.get("enabled", True),
            trigger_logic=data.get("trigger_logic", "AND"),
            chained_scripts=data.get("chained_scripts", []).copy() if isinstance(data.get("chained_scripts"), list) else [],
            priority=data.get("priority", 0),
            cooldown_seconds=data.get("cooldown_seconds", 0.0),
            last_triggered=data.get("last_triggered", 0.0),
            upgrade_level=data.get("upgrade_level", 0)
        )

    def __repr__(self) -> str:
        """String representation of automation script."""
        return (f"AutomationScript(id='{self.id}', name='{self.name}', "
                f"effect='{self.effect}', required_level={self.required_level})")
