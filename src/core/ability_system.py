"""Specialist Ability System.

Handles ability activation, cooldown management, and effect application.
"""

from typing import Dict, List, Optional
import time
from src.models.specialist_ability import SpecialistAbility
from src.utils.logger import GameLogger


class AbilitySystem:
    """Manages specialist abilities and their effects."""
    
    def __init__(self, abilities_config: Dict):
        """Initialize the ability system.
        
        Args:
            abilities_config: Configuration dictionary containing abilities data
        """
        self._logger = GameLogger("ability_system")
        self.abilities: Dict[str, SpecialistAbility] = {}
        
        # Load abilities from config
        if "abilities" in abilities_config:
            for ability_data in abilities_config["abilities"]:
                ability = SpecialistAbility.from_dict(ability_data)
                self.abilities[ability.id] = ability
        
        self._logger.info(
            f"[ABILITY_SYSTEM] Initialized with {len(self.abilities)} abilities"
        )
    
    def activate_ability(self, specialist, ability_id: str, 
                        target=None) -> Dict:
        """Activate an ability for a specialist.
        
        Args:
            specialist: The specialist activating the ability
            ability_id: ID of the ability to activate
            target: Optional target (e.g., incident for certain abilities)
            
        Returns:
            Dictionary containing activation result:
            {
                "success": bool,
                "message": str,
                "effect_applied": Dict (optional)
            }
        """
        # Check if ability exists
        if ability_id not in self.abilities:
            return {
                "success": False,
                "message": f"Ability {ability_id} not found"
            }
        
        ability = self.abilities[ability_id]
        
        # Check if specialist has unlocked the ability
        if ability_id not in specialist.abilities:
            return {
                "success": False,
                "message": f"Ability {ability.name} not unlocked"
            }
        
        # Check if ability is on cooldown
        cooldown_remaining = specialist.ability_cooldowns.get(ability_id, 0.0)
        if cooldown_remaining > 0:
            return {
                "success": False,
                "message": f"Ability on cooldown ({cooldown_remaining:.1f}s remaining)"
            }
        
        # Check specialty requirement
        if ability.specialty != "Any" and specialist.specialty != ability.specialty:
            return {
                "success": False,
                "message": f"Ability requires {ability.specialty} specialty"
            }
        
        # Activate the ability
        effect = self._apply_ability_effect(specialist, ability, target)
        
        # Set cooldown
        specialist.ability_cooldowns[ability_id] = ability.cooldown_seconds
        
        self._logger.info(
            f"[ABILITY_SYSTEM] Specialist {specialist.id} activated {ability.name}"
        )
        
        return {
            "success": True,
            "message": f"Activated {ability.name}",
            "effect_applied": effect
        }
    
    def _apply_ability_effect(self, specialist, ability: SpecialistAbility, 
                             target=None) -> Dict:
        """Apply the effect of an ability.
        
        Args:
            specialist: The specialist using the ability
            ability: The ability being used
            target: Optional target for the ability
            
        Returns:
            Dictionary describing the effect applied
        """
        effect = {
            "ability_id": ability.id,
            "ability_type": ability.ability_type,
            "magnitude": ability.effect_magnitude,
            "duration": ability.duration_seconds,
            "start_time": time.time()
        }
        
        # Apply based on ability type
        if ability.ability_type == "speed_burst":
            # Add temporary speed buff
            effect["stat_affected"] = "speed"
            specialist.active_effects.append(effect)
            
        elif ability.ability_type == "accuracy_boost":
            # Add temporary accuracy buff
            effect["stat_affected"] = "accuracy"
            specialist.active_effects.append(effect)
            
        elif ability.ability_type == "sla_extension":
            # Instant effect - extend SLA on target incident
            if target:
                target.sla_deadline += (target.sla_deadline - target.spawn_time) * (ability.effect_magnitude - 1.0)
                effect["target_incident_id"] = target.id
                effect["instant"] = True
            else:
                effect["instant"] = True
                effect["pending"] = True  # Will be applied to next assigned incident
                specialist.active_effects.append(effect)
                
        elif ability.ability_type == "reward_multiplier":
            # Add buff for next incident completion
            effect["stat_affected"] = "reward"
            effect["pending"] = True
            specialist.active_effects.append(effect)
            
        elif ability.ability_type == "auto_complete":
            # Instant effect - complete current incident
            if target:
                effect["target_incident_id"] = target.id
                effect["instant"] = True
                effect["guaranteed_success"] = True
            else:
                effect["instant"] = True
                effect["pending"] = True
                specialist.active_effects.append(effect)
        
        return effect
    
    def update_cooldowns(self, specialist, delta_time: float):
        """Update ability cooldowns for a specialist.
        
        Args:
            specialist: The specialist to update cooldowns for
            delta_time: Time elapsed in seconds
        """
        for ability_id in list(specialist.ability_cooldowns.keys()):
            specialist.ability_cooldowns[ability_id] -= delta_time
            
            # Remove cooldown if it's finished
            if specialist.ability_cooldowns[ability_id] <= 0:
                del specialist.ability_cooldowns[ability_id]
    
    def update_active_effects(self, specialist, delta_time: float):
        """Update active ability effects and remove expired ones.
        
        Args:
            specialist: The specialist to update effects for
            delta_time: Time elapsed in seconds
        """
        current_time = time.time()
        effects_to_remove = []
        
        for i, effect in enumerate(specialist.active_effects):
            # Check if effect has expired
            if effect.get("duration", 0) > 0:
                elapsed = current_time - effect["start_time"]
                if elapsed >= effect["duration"]:
                    effects_to_remove.append(i)
        
        # Remove expired effects (in reverse order to maintain indices)
        for i in reversed(effects_to_remove):
            specialist.active_effects.pop(i)
    
    def get_available_abilities(self, specialist) -> List[str]:
        """Get list of abilities that can be activated.
        
        Args:
            specialist: The specialist to check abilities for
            
        Returns:
            List of ability IDs that are off cooldown and unlocked
        """
        available = []
        
        for ability_id in specialist.abilities:
            # Check if on cooldown
            if specialist.ability_cooldowns.get(ability_id, 0.0) > 0:
                continue
            
            # Check if ability exists
            if ability_id not in self.abilities:
                continue
            
            ability = self.abilities[ability_id]
            
            # Check specialty requirement
            if ability.specialty != "Any" and specialist.specialty != ability.specialty:
                continue
            
            available.append(ability_id)
        
        return available
    
    def apply_active_effects(self, specialist, incident=None) -> Dict[str, float]:
        """Calculate stat modifiers from active effects.
        
        Args:
            specialist: The specialist to calculate modifiers for
            incident: Optional incident being worked on (for pending effects)
            
        Returns:
            Dictionary of stat modifiers: {"speed": 1.5, "accuracy": 1.2, etc.}
        """
        modifiers = {
            "speed": 1.0,
            "accuracy": 1.0,
            "reward": 1.0
        }
        
        current_time = time.time()
        
        for effect in specialist.active_effects:
            # Skip pending effects unless we have an incident
            if effect.get("pending") and not incident:
                continue
            
            # Check if effect is still active
            if effect.get("duration", 0) > 0:
                elapsed = current_time - effect["start_time"]
                if elapsed >= effect["duration"]:
                    continue
            
            # Apply effect based on type
            stat_affected = effect.get("stat_affected")
            if stat_affected in modifiers:
                if effect["ability_type"] in ["speed_burst", "accuracy_boost"]:
                    # Multiplicative modifier
                    modifiers[stat_affected] *= effect["magnitude"]
                elif effect["ability_type"] == "reward_multiplier":
                    modifiers["reward"] *= effect["magnitude"]
        
        return modifiers
    
    def unlock_abilities_for_level(self, specialist, level: int) -> List[str]:
        """Unlock abilities that become available at a specific level.
        
        Args:
            specialist: The specialist to unlock abilities for
            level: The level reached
            
        Returns:
            List of newly unlocked ability IDs
        """
        unlocked = []
        
        for ability_id, ability in self.abilities.items():
            # Check if ability should be unlocked at this level
            if ability.unlock_level == level:
                # Check specialty requirement
                if ability.specialty == "Any" or ability.specialty == specialist.specialty:
                    # Check if not already unlocked
                    if ability_id not in specialist.abilities:
                        specialist.abilities.append(ability_id)
                        unlocked.append(ability_id)
                        
                        self._logger.info(
                            f"[ABILITY_SYSTEM] Specialist {specialist.id} unlocked {ability.name}"
                        )
        
        return unlocked
    
    def get_ability(self, ability_id: str) -> Optional[SpecialistAbility]:
        """Get an ability by ID.
        
        Args:
            ability_id: The ability ID to get
            
        Returns:
            SpecialistAbility or None if not found
        """
        return self.abilities.get(ability_id)
