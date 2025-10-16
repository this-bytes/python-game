"""Incident model representing a security incident requiring triage and resolution.

Incidents are generated continuously based on client contracts and must be assigned
to specialists to be resolved within SLA deadlines.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict
from datetime import datetime, timedelta
from enum import Enum
import time


class IncidentStatus(Enum):
    """Enum for incident lifecycle status."""
    PENDING = "pending"  # Waiting for assignment
    ASSIGNED = "assigned"  # Assigned to a specialist
    IN_PROGRESS = "in_progress"  # Being worked on
    RESOLVED = "resolved"  # Successfully resolved
    FAILED = "failed"  # SLA missed or resolution failed
    CANCELLED = "cancelled"  # Cancelled/expired


@dataclass
class Incident:
    """Represents a security incident that needs to be handled."""
    
    id: str
    incident_type: str
    specialty_required: str
    difficulty: int  # 1-5 scale
    sla_seconds: int  # Time until SLA deadline
    base_reward: int  # Monetary reward for resolution
    xp_reward: int  # XP reward for resolution
    client_id: str
    status: str = "pending"
    assigned_specialist_id: Optional[str] = None
    spawn_time: float = field(default_factory=time.time)
    assignment_time: Optional[float] = None
    completion_time: Optional[float] = None
    sla_deadline: Optional[float] = None
    
    def __post_init__(self):
        """Calculate SLA deadline after initialization."""
        if self.sla_deadline is None:
            self.sla_deadline = self.spawn_time + self.sla_seconds
    
    def is_pending(self) -> bool:
        """Check if incident is pending assignment.
        
        Returns:
            True if status is PENDING, False otherwise
        """
        return self.status == IncidentStatus.PENDING.value
    
    def is_assigned(self) -> bool:
        """Check if incident is assigned to a specialist.
        
        Returns:
            True if status is ASSIGNED or IN_PROGRESS, False otherwise
        """
        return self.status in [IncidentStatus.ASSIGNED.value, IncidentStatus.IN_PROGRESS.value]
    
    def is_resolved(self) -> bool:
        """Check if incident has been resolved.
        
        Returns:
            True if status is RESOLVED, False otherwise
        """
        return self.status == IncidentStatus.RESOLVED.value
    
    def is_failed(self) -> bool:
        """Check if incident has failed (SLA missed or resolution failed).
        
        Returns:
            True if status is FAILED, False otherwise
        """
        return self.status == IncidentStatus.FAILED.value
    
    def is_active(self) -> bool:
        """Check if incident is still active (not resolved, failed, or cancelled).
        
        Returns:
            True if incident is active, False otherwise
        """
        return self.status not in [
            IncidentStatus.RESOLVED.value,
            IncidentStatus.FAILED.value,
            IncidentStatus.CANCELLED.value
        ]
    
    def assign_to_specialist(self, specialist_id: str) -> bool:
        """Assign incident to a specialist.
        
        Args:
            specialist_id: ID of the specialist to assign
            
        Returns:
            True if assignment successful, False if already assigned
        """
        if not self.is_pending():
            return False
        
        self.assigned_specialist_id = specialist_id
        self.assignment_time = time.time()
        self.status = IncidentStatus.ASSIGNED.value
        return True
    
    def start_resolution(self) -> bool:
        """Mark incident as in progress.
        
        Returns:
            True if successfully started, False if not in correct state
        """
        if self.status != IncidentStatus.ASSIGNED.value:
            return False
        
        self.status = IncidentStatus.IN_PROGRESS.value
        return True
    
    def complete_resolution(self, success: bool) -> bool:
        """Mark incident as resolved or failed.
        
        Args:
            success: Whether resolution was successful
            
        Returns:
            True if completion recorded successfully
        """
        if not self.is_assigned() and not self.is_pending():
            return False
        
        self.completion_time = time.time()
        
        if success:
            self.status = IncidentStatus.RESOLVED.value
        else:
            self.status = IncidentStatus.FAILED.value
        
        return True
    
    def get_time_remaining(self) -> float:
        """Get time remaining until SLA deadline.
        
        Returns:
            Time remaining in seconds (negative if overdue)
        """
        if self.sla_deadline is None:
            return 0.0
        
        return self.sla_deadline - time.time()
    
    def is_sla_met(self) -> bool:
        """Check if SLA deadline was met.
        
        Returns:
            True if resolved before deadline, False otherwise
        """
        if self.completion_time is None or self.sla_deadline is None:
            return False
        
        return self.completion_time <= self.sla_deadline
    
    def is_sla_overdue(self) -> bool:
        """Check if current time has passed SLA deadline.
        
        Returns:
            True if overdue, False otherwise
        """
        return self.get_time_remaining() < 0
    
    def get_sla_urgency(self) -> str:
        """Get urgency level based on time remaining.
        
        Returns:
            Urgency level: 'critical', 'warning', or 'good'
        """
        time_remaining = self.get_time_remaining()
        sla_percent_remaining = (time_remaining / self.sla_seconds) * 100 if self.sla_seconds > 0 else 0
        
        if sla_percent_remaining < 20:
            return "critical"
        elif sla_percent_remaining < 50:
            return "warning"
        else:
            return "good"
    
    def calculate_reward(self, difficulty_multipliers: Dict[int, float], 
                        perfect_bonus: float = 1.2,
                        sla_penalty: float = 0.5) -> int:
        """Calculate actual reward based on resolution performance.
        
        Args:
            difficulty_multipliers: Dictionary mapping difficulty to reward multiplier
            perfect_bonus: Bonus multiplier for perfect completion
            sla_penalty: Penalty multiplier for SLA failure
            
        Returns:
            Calculated reward amount
        """
        if not self.is_resolved():
            return 0
        
        # Base reward with difficulty multiplier
        difficulty_mult = difficulty_multipliers.get(self.difficulty, 1.0)
        reward = int(self.base_reward * difficulty_mult)
        
        # Apply perfect completion bonus if SLA met
        if self.is_sla_met():
            # Check if completion was particularly fast (within first 25% of SLA)
            time_used = (self.completion_time - self.spawn_time) if self.completion_time and self.spawn_time else self.sla_seconds
            if time_used < (self.sla_seconds * 0.25):
                reward = int(reward * perfect_bonus)
        else:
            # Apply SLA penalty
            reward = int(reward * sla_penalty)
        
        return max(0, reward)
    
    def get_resolution_time(self) -> Optional[float]:
        """Get total time taken to resolve incident.
        
        Returns:
            Resolution time in seconds, or None if not completed
        """
        if self.completion_time is None:
            return None
        
        return self.completion_time - self.spawn_time
    
    def get_age(self) -> float:
        """Get age of incident since spawn.
        
        Returns:
            Age in seconds
        """
        return time.time() - self.spawn_time
    
    def matches_specialty(self, specialist_specialty: str) -> bool:
        """Check if incident specialty matches specialist specialty.
        
        Args:
            specialist_specialty: Specialist's specialty
            
        Returns:
            True if specialty matches, False otherwise
        """
        return self.specialty_required == specialist_specialty
    
    def cancel(self) -> bool:
        """Cancel the incident.
        
        Returns:
            True if cancelled successfully
        """
        if not self.is_active():
            return False
        
        self.status = IncidentStatus.CANCELLED.value
        self.completion_time = time.time()
        return True
    
    def to_dict(self) -> Dict:
        """Convert incident to dictionary for serialization.
        
        Returns:
            Dictionary representation of the incident
        """
        return {
            "id": self.id,
            "incident_type": self.incident_type,
            "specialty_required": self.specialty_required,
            "difficulty": self.difficulty,
            "sla_seconds": self.sla_seconds,
            "base_reward": self.base_reward,
            "xp_reward": self.xp_reward,
            "client_id": self.client_id,
            "status": self.status,
            "assigned_specialist_id": self.assigned_specialist_id,
            "spawn_time": self.spawn_time,
            "assignment_time": self.assignment_time,
            "completion_time": self.completion_time,
            "sla_deadline": self.sla_deadline
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Incident':
        """Create Incident from dictionary.
        
        Args:
            data: Dictionary containing incident data
            
        Returns:
            New Incident instance
        """
        return cls(
            id=data["id"],
            incident_type=data["incident_type"],
            specialty_required=data["specialty_required"],
            difficulty=data["difficulty"],
            sla_seconds=data["sla_seconds"],
            base_reward=data["base_reward"],
            xp_reward=data["xp_reward"],
            client_id=data["client_id"],
            status=data.get("status", "pending"),
            assigned_specialist_id=data.get("assigned_specialist_id"),
            spawn_time=data.get("spawn_time", time.time()),
            assignment_time=data.get("assignment_time"),
            completion_time=data.get("completion_time"),
            sla_deadline=data.get("sla_deadline")
        )
    
    def __repr__(self) -> str:
        """String representation of incident."""
        return (f"Incident(id='{self.id}', type='{self.incident_type}', "
                f"difficulty={self.difficulty}, status='{self.status}', "
                f"time_remaining={self.get_time_remaining():.1f}s)")
