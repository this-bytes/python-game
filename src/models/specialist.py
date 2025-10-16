"""Specialist model representing a cybersecurity expert.

Specialists are the core workforce of the firm. They handle incidents based on their
specialty, gain XP, level up, and unlock automation scripts.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum


class SpecialistStatus(Enum):
    """Enum for specialist availability status."""
    AVAILABLE = "available"
    BUSY = "busy"
    TRAINING = "training"
    OFFLINE = "offline"


class Specialty(Enum):
    """Enum for specialist security specialties."""
    NETWORK_SECURITY = "Network Security"
    MALWARE_ANALYSIS = "Malware Analysis"
    DIGITAL_FORENSICS = "Digital Forensics"
    APPLICATION_SECURITY = "Application Security"
    CLOUD_SECURITY = "Cloud Security"
    INCIDENT_RESPONSE = "Incident Response"


@dataclass
class SpecialistStats:
    """Statistics for a specialist's performance."""
    speed: float  # Resolution speed multiplier (higher = faster)
    accuracy: float  # Success rate percentage (0-100)
    experience_bonus: float  # XP gain multiplier
    
    def to_dict(self) -> Dict:
        """Convert stats to dictionary."""
        return {
            "speed": self.speed,
            "accuracy": self.accuracy,
            "experience_bonus": self.experience_bonus
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SpecialistStats':
        """Create SpecialistStats from dictionary."""
        return cls(
            speed=data["speed"],
            accuracy=data["accuracy"],
            experience_bonus=data["experience_bonus"]
        )


@dataclass
class Specialist:
    """Represents a cybersecurity specialist."""
    
    id: str
    name: str
    specialty: str
    level: int
    xp: int
    stats: SpecialistStats
    status: str = "available"
    automation_scripts: List[str] = field(default_factory=list)
    assigned_incident_id: Optional[str] = None
    skill_points: int = 0
    abilities: List[str] = field(default_factory=list)  # Ability IDs
    ability_cooldowns: Dict[str, float] = field(default_factory=dict)  # Ability ID -> cooldown remaining
    active_effects: List[Dict] = field(default_factory=list)  # Temporary buffs
    equipped_items: Dict[str, str] = field(default_factory=dict)  # Slot -> equipment ID
    inventory: List[str] = field(default_factory=list)  # Owned equipment IDs
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        # Convert stats dict to SpecialistStats if needed
        if isinstance(self.stats, dict):
            self.stats = SpecialistStats.from_dict(self.stats)
    
    def is_available(self) -> bool:
        """Check if specialist is available for assignment.
        
        Returns:
            True if specialist status is AVAILABLE, False otherwise
        """
        return self.status == SpecialistStatus.AVAILABLE.value
    
    def assign_to_incident(self, incident_id: str) -> bool:
        """Assign specialist to an incident.
        
        Args:
            incident_id: ID of the incident to assign
            
        Returns:
            True if assignment successful, False if specialist not available
        """
        if not self.is_available():
            return False
        
        self.assigned_incident_id = incident_id
        self.status = SpecialistStatus.BUSY.value
        return True
    
    def complete_assignment(self) -> Optional[str]:
        """Mark current assignment as complete and return specialist to available status.
        
        Returns:
            ID of the completed incident, or None if no assignment
        """
        if self.assigned_incident_id is None:
            return None
        
        completed_incident_id = self.assigned_incident_id
        self.assigned_incident_id = None
        self.status = SpecialistStatus.AVAILABLE.value
        return completed_incident_id
    
    def gain_xp(self, amount: int) -> bool:
        """Add XP to the specialist.
        
        Args:
            amount: Amount of XP to add (before experience_bonus multiplier)
            
        Returns:
            True if specialist leveled up, False otherwise
        """
        # Apply experience bonus multiplier
        actual_xp = int(amount * self.stats.experience_bonus)
        self.xp += actual_xp
        
        # Check for level up
        return self.check_level_up()
    
    def check_level_up(self) -> bool:
        """Check if specialist should level up based on current XP.
        
        Returns:
            True if leveled up, False otherwise
        """
        # Simple XP curve: level * 100 XP per level with exponential growth
        xp_required = self.calculate_xp_for_next_level()
        
        if self.xp >= xp_required and self.level < 20:  # Max level 20
            self.level += 1
            return True
        
        return False
    
    def calculate_xp_for_next_level(self) -> int:
        """Calculate XP required for next level.
        
        Returns:
            XP required for next level
        """
        # Formula: base_xp * (level ^ exponent)
        # This creates an exponential curve: 100, 250, 450, 700, 1000, etc.
        base_xp = 100
        exponent = 1.5
        return int(base_xp * (self.level ** exponent))
    
    def get_xp_progress_percent(self) -> float:
        """Get XP progress to next level as percentage.
        
        Returns:
            Percentage of XP progress (0-100)
        """
        if self.level >= 20:
            return 100.0
        
        current_level_xp = self.calculate_xp_for_level(self.level)
        next_level_xp = self.calculate_xp_for_next_level()
        xp_in_current_level = self.xp - current_level_xp
        xp_needed = next_level_xp - current_level_xp
        
        if xp_needed <= 0:
            return 100.0
        
        return min(100.0, (xp_in_current_level / xp_needed) * 100)
    
    def calculate_xp_for_level(self, target_level: int) -> int:
        """Calculate total XP required to reach a specific level.
        
        Args:
            target_level: The level to calculate XP for
            
        Returns:
            Total XP required for target level
        """
        if target_level <= 1:
            return 0
        
        base_xp = 100
        exponent = 1.5
        total_xp = 0
        
        for lvl in range(1, target_level):
            total_xp += int(base_xp * (lvl ** exponent))
        
        return total_xp
    
    def has_automation_script(self, script_id: str) -> bool:
        """Check if specialist has unlocked a specific automation script.
        
        Args:
            script_id: ID of the automation script
            
        Returns:
            True if script is unlocked, False otherwise
        """
        return script_id in self.automation_scripts
    
    def unlock_automation_script(self, script_id: str) -> bool:
        """Unlock a new automation script.
        
        Args:
            script_id: ID of the automation script to unlock
            
        Returns:
            True if newly unlocked, False if already unlocked
        """
        if self.has_automation_script(script_id):
            return False
        
        self.automation_scripts.append(script_id)
        return True
    
    def allocate_skill_point(self, stat: str) -> bool:
        """Allocate a skill point to increase a stat.
        
        Args:
            stat: Name of the stat to increase (speed, accuracy, experience_bonus)
            
        Returns:
            True if allocation successful, False if no skill points available or invalid stat
        """
        if self.skill_points <= 0:
            return False
        
        # Define stat increase values
        stat_increases = {
            "speed": 5.0,
            "accuracy": 2.0,
            "experience_bonus": 0.1
        }
        
        if stat not in stat_increases:
            return False
        
        # Apply the stat increase
        if stat == "speed":
            self.stats.speed += stat_increases["speed"]
        elif stat == "accuracy":
            self.stats.accuracy = min(100.0, self.stats.accuracy + stat_increases["accuracy"])
        elif stat == "experience_bonus":
            self.stats.experience_bonus += stat_increases["experience_bonus"]
        
        # Deduct skill point
        self.skill_points -= 1
        return True
    
    def matches_specialty(self, required_specialty: str) -> bool:
        """Check if specialist's specialty matches the required specialty.
        
        Args:
            required_specialty: The required specialty string
            
        Returns:
            True if specialty matches, False otherwise
        """
        return self.specialty == required_specialty
    
    def calculate_resolution_time(self, base_time: float) -> float:
        """Calculate time to resolve an incident based on specialist stats.
        
        Args:
            base_time: Base resolution time in seconds
            
        Returns:
            Actual resolution time considering specialist speed
        """
        # Higher speed = faster resolution
        speed_multiplier = self.stats.speed / 100.0
        return base_time / speed_multiplier
    
    def calculate_success_probability(self, base_difficulty: int) -> float:
        """Calculate probability of successful incident resolution.
        
        Args:
            base_difficulty: Incident difficulty (1-5)
            
        Returns:
            Success probability (0.0-1.0)
        """
        # Base accuracy, reduced by difficulty
        difficulty_penalty = (base_difficulty - 1) * 5  # 0, 5, 10, 15, 20% penalty
        effective_accuracy = max(10, self.stats.accuracy - difficulty_penalty)
        return min(1.0, effective_accuracy / 100.0)
    
    def to_dict(self) -> Dict:
        """Convert specialist to dictionary for serialization.
        
        Returns:
            Dictionary representation of the specialist
        """
        return {
            "id": self.id,
            "name": self.name,
            "specialty": self.specialty,
            "level": self.level,
            "xp": self.xp,
            "stats": self.stats.to_dict(),
            "status": self.status,
            "automation_scripts": self.automation_scripts.copy(),
            "assigned_incident_id": self.assigned_incident_id,
            "skill_points": self.skill_points,
            "abilities": self.abilities.copy(),
            "ability_cooldowns": self.ability_cooldowns.copy(),
            "active_effects": self.active_effects.copy(),
            "equipped_items": self.equipped_items.copy(),
            "inventory": self.inventory.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Specialist':
        """Create Specialist from dictionary.
        
        Args:
            data: Dictionary containing specialist data
            
        Returns:
            New Specialist instance
        """
        return cls(
            id=data["id"],
            name=data["name"],
            specialty=data["specialty"],
            level=data["level"],
            xp=data["xp"],
            stats=data["stats"],  # Will be converted in __post_init__
            status=data.get("status", "available"),
            automation_scripts=data.get("automation_scripts", []).copy(),
            assigned_incident_id=data.get("assigned_incident_id"),
            skill_points=data.get("skill_points", 0),
            abilities=data.get("abilities", []).copy(),
            ability_cooldowns=data.get("ability_cooldowns", {}).copy(),
            active_effects=data.get("active_effects", []).copy(),
            equipped_items=data.get("equipped_items", {}).copy(),
            inventory=data.get("inventory", []).copy()
        )
    
    def __repr__(self) -> str:
        """String representation of specialist."""
        return (f"Specialist(id='{self.id}', name='{self.name}', "
                f"specialty='{self.specialty}', level={self.level}, "
                f"xp={self.xp}, status='{self.status}')")
