"""Burnout & Morale System - Specialist Psychological Management (SIMPLIFIED).

SIMPLIFIED BURNOUT SYSTEM: Track specialist fatigue and recovery.
- Burnout accumulates: 5% per incident (additional 5% per difficulty level 2+)
- Performance penalty: -2% per burnout level (0-100%)
- Recovery: Rest day = -30%, Vacation = -50-80%, Therapy = clears trauma
- Thresholds: Warn at 60%, critical at 80%, force rest at 95%

This creates meaningful strategic choice: overwork for cash vs sustainable growth.
"""

from dataclasses import dataclass
from typing import Dict, Tuple
from enum import Enum
import time


class BurnoutTier(Enum):
    """Burnout severity levels."""
    FRESH = "fresh"            # 0-20% burnout
    STRESSED = "stressed"      # 21-40% burnout
    EXHAUSTED = "exhausted"    # 41-60% burnout
    CRITICAL = "critical"      # 61-80% burnout
    BROKEN = "broken"          # 81-100% burnout


@dataclass
class SpecialistBurnout:
    """Simplified burnout state for a specialist."""
    
    specialist_id: str
    burnout_level: float = 0.0          # 0-100%
    failed_incidents: int = 0           # Trauma counter
    last_rest_time: float = 0.0
    
    @property
    def tier(self) -> BurnoutTier:
        """Get burnout severity tier."""
        if self.burnout_level <= 20:
            return BurnoutTier.FRESH
        elif self.burnout_level <= 40:
            return BurnoutTier.STRESSED
        elif self.burnout_level <= 60:
            return BurnoutTier.EXHAUSTED
        elif self.burnout_level <= 80:
            return BurnoutTier.CRITICAL
        else:
            return BurnoutTier.BROKEN
    
    def get_performance_multiplier(self) -> float:
        """Get performance multiplier from burnout (0.0-1.0).
        
        Returns:
            1.0 = no burnout, 0.5 = 50% burned out, 0.0 = completely broken
        """
        return max(0.0, 1.0 - (self.burnout_level / 100.0))
    
    def get_error_chance(self) -> float:
        """Probability incident will fail due to burnout (0.0-0.5).
        
        Returns:
            0.0 = no extra failure chance, 0.5 = 50% fail at 100% burnout
        """
        return (self.burnout_level / 100.0) * 0.5


class BurnoutSystem:
    """Manages specialist burnout tracking and recovery."""
    
    def __init__(self):
        """Initialize burnout system."""
        self.specialists: Dict[str, SpecialistBurnout] = {}
    
    def register_specialist(self, specialist_id: str) -> SpecialistBurnout:
        """Register specialist in burnout system."""
        if specialist_id not in self.specialists:
            self.specialists[specialist_id] = SpecialistBurnout(specialist_id=specialist_id)
        return self.specialists[specialist_id]
    
    def assign_incident(self, specialist_id: str, incident_difficulty: int) -> Tuple[bool, str]:
        """Record incident assignment, increase burnout.
        
        Args:
            specialist_id: Specialist ID
            incident_difficulty: 1-5 scale
            
        Returns:
            (allowed: bool, message: str)
        """
        burnout = self.register_specialist(specialist_id)
        
        # Calculate burnout cost: 5% base + 5% per difficulty level above 1
        burnout_cost = 5.0 + (max(0, incident_difficulty - 1) * 5.0)
        burnout.burnout_level = min(100.0, burnout.burnout_level + burnout_cost)
        
        # Check thresholds
        if burnout.burnout_level > 95:
            return False, f"{specialist_id} is too broken. Force rest required."
        if burnout.burnout_level > 80:
            return True, f"{specialist_id} CRITICAL (>80%). Performance severely degraded."
        if burnout.burnout_level > 60:
            return True, f"{specialist_id} EXHAUSTED (>60%). Recommend rest soon."
        
        return True, f"Assigned. Burnout: {burnout.burnout_level:.0f}%"
    
    def complete_incident(self, specialist_id: str, success: bool):
        """Record incident completion."""
        burnout = self.register_specialist(specialist_id)
        
        if not success:
            # Failure causes psychological trauma
            burnout.failed_incidents += 1
            burnout.burnout_level = min(100.0, burnout.burnout_level + 10.0)
    
    def take_rest_day(self, specialist_id: str) -> Tuple[bool, str]:
        """Specialist takes a rest day."""
        burnout = self.register_specialist(specialist_id)
        
        # Rest reduces burnout by 30%
        recovery = burnout.burnout_level * 0.30
        burnout.burnout_level = max(0, burnout.burnout_level - recovery)
        burnout.last_rest_time = time.time()
        
        return True, f"Rested. Recovered {recovery:.0f}%. Burnout now: {burnout.burnout_level:.0f}%"
    
    def take_vacation(self, specialist_id: str, days: int, cost_per_day: int) -> Tuple[bool, str]:
        """Send specialist on vacation."""
        burnout = self.register_specialist(specialist_id)
        
        # Longer vacation = more recovery
        recovery_percent = 0.3 + (days * 0.1)  # 30% + 10% per day, up to 80% for 5 days
        recovery = burnout.burnout_level * min(0.8, recovery_percent)
        burnout.burnout_level = max(0, burnout.burnout_level - recovery)
        
        total_cost = cost_per_day * days
        return True, f"{days}-day vacation. Recovered {recovery:.0f}%. Cost: {total_cost}"
    
    def attend_therapy(self, specialist_id: str, cost: int) -> Tuple[bool, str]:
        """Specialist attends therapy."""
        burnout = self.register_specialist(specialist_id)
        
        if burnout.failed_incidents == 0:
            return False, "No trauma to process."
        
        # Therapy reduces trauma-related burnout
        trauma_burnout = burnout.failed_incidents * 10.0
        recovery = min(trauma_burnout, burnout.burnout_level)
        burnout.burnout_level = max(0, burnout.burnout_level - recovery)
        burnout.failed_incidents = 0
        
        return True, f"Therapy complete. Recovered {recovery:.0f}%. Cost: {cost}"
    
    def get_specialist_status(self, specialist_id: str) -> Dict:
        """Get specialist burnout status."""
        burnout = self.register_specialist(specialist_id)
        return {
            "specialist_id": specialist_id,
            "burnout_level": round(burnout.burnout_level, 1),
            "tier": burnout.tier.value,
            "performance_multiplier": round(burnout.get_performance_multiplier(), 2),
            "error_chance": round(burnout.get_error_chance(), 2),
            "trauma_incidents": burnout.failed_incidents,
        }
    
    def get_team_status(self) -> Dict:
        """Get team-wide burnout statistics."""
        if not self.specialists:
            return {"team_size": 0, "average_burnout": 0.0, "critical_count": 0}
        
        specialists = list(self.specialists.values())
        avg_burnout = sum(s.burnout_level for s in specialists) / len(specialists)
        critical_count = sum(1 for s in specialists if s.burnout_level > 80)
        
        return {
            "team_size": len(specialists),
            "average_burnout": round(avg_burnout, 1),
            "critical_count": critical_count,
            "need_intervention": critical_count > 0,
        }
