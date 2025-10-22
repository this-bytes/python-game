"""Incident dispatch and assignment system for SOC startup game.

This module handles the assignment of security incidents to specialists,
resolution tracking, SLA management, and consequence calculation.
"""

import time
import random
import logging
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

from src.models.incident import Incident, IncidentStatus
from src.models.specialist import Specialist
from src.models.client import Client
from src.utils.logger import GameLogger


@dataclass
class AssignmentResult:
    """Result of assigning an incident to a specialist."""
    success: bool
    reason: str
    incident_id: Optional[str] = None
    specialist_id: Optional[str] = None


@dataclass
class ResolutionResult:
    """Result of incident resolution."""
    success: bool
    sla_met: bool
    time_taken: float
    xp_earned: int
    reward_earned: float
    specialist_id: str
    incident_id: str
    client_id: str


class IncidentDispatchSystem:
    """Manages incident assignment and resolution for the SOC."""
    
    def __init__(self, logger: Optional[GameLogger] = None):
        """Initialize the incident dispatch system.
        
        Args:
            logger: Optional logger for dispatch events
        """
        self._logger = logger or GameLogger("incident_dispatch")
        self._active_assignments: Dict[str, str] = {}  # incident_id -> specialist_id mapping
        self._incidents: Dict[str, Incident] = {}  # incident_id -> Incident
        self._logger.logger.info("[INCIDENT_DISPATCH] System initialized")
    
    def add_incident(self, incident: Incident) -> None:
        """Add an incident to the dispatch system.
        
        Args:
            incident: Incident to add
        """
        if incident.id in self._incidents:
            self._logger.logger.warning(f"[INCIDENT_DISPATCH] Incident {incident.id} already exists, overwriting")
        
        self._incidents[incident.id] = incident
        self._logger.logger.debug(f"[INCIDENT_DISPATCH] Added incident {incident.id} for client {incident.client_id}")
    
    def assign_incident(
        self,
        incident: Incident,
        specialist: Specialist
    ) -> AssignmentResult:
        """Attempt to assign an incident to a specialist.
        
        Validates specialty match, specialist availability, and level requirements.
        
        Args:
            incident: Incident to assign
            specialist: Specialist to assign to
            
        Returns:
            AssignmentResult with success status and reason
        """
        # Validation: Incident must be pending
        if not incident.is_pending():
            return AssignmentResult(
                success=False,
                reason=f"Incident {incident.id} is not pending (status: {incident.status})"
            )
        
        # Validation: Specialty match
        if specialist.specialty != incident.specialty_required:
            return AssignmentResult(
                success=False,
                reason=f"Specialist specialty '{specialist.specialty}' does not match incident requirement '{incident.specialty_required}'"
            )
        
        # Validation: Specialist not already assigned
        if specialist.assigned_incident_id is not None:
            return AssignmentResult(
                success=False,
                reason=f"Specialist {specialist.name} is already assigned to incident {specialist.assigned_incident_id}"
            )
        
        # Perform assignment
        specialist.assigned_incident_id = incident.id
        incident.assign_to_specialist(specialist.id)
        self._active_assignments[incident.id] = specialist.id
        
        self._logger.logger.info(
            f"[INCIDENT_DISPATCH] Assigned incident {incident.id} ({incident.incident_type}) "
            f"to specialist {specialist.name} (Level {specialist.level})"
        )
        
        return AssignmentResult(
            success=True,
            reason="Assignment successful",
            incident_id=incident.id,
            specialist_id=specialist.id
        )
    
    def resolve_incident(
        self,
        incident: Incident,
        specialist: Specialist,
        success: bool,
        time_taken: Optional[float] = None
    ) -> ResolutionResult:
        """Resolve an assigned incident.
        
        Calculates SLA compliance, XP rewards, monetary rewards, and updates satisfaction.
        
        Args:
            incident: Incident to resolve
            specialist: Specialist who resolved it
            success: Whether resolution was successful
            time_taken: Optional time taken to resolve (seconds). If None, uses actual time elapsed.
            
        Returns:
            ResolutionResult with detailed outcome
        """
        # Calculate time taken if not provided
        if time_taken is None:
            if incident.assignment_time is None:
                time_taken = 0.0
            else:
                time_taken = time.time() - incident.assignment_time
        
        # Check SLA compliance
        sla_met = time_taken <= incident.sla_seconds if success else False
        
        # Calculate rewards based on difficulty and SLA performance
        base_xp = incident.xp_reward
        base_reward = incident.base_reward
        
        # Difficulty multiplier (1.0-2.5x based on difficulty 1-5)
        difficulty_multiplier = 1.0 + (incident.difficulty - 1) * 0.375
        
        # SLA performance multiplier
        if sla_met:
            sla_multiplier = 1.2  # 20% bonus for meeting SLA
        else:
            sla_multiplier = 0.7  # 30% penalty for missing SLA (if still successful)
        
        # Specialist level bonus (scales up with level)
        level_bonus = 1.0 + (specialist.level - 1) * 0.05  # 5% per level above 1
        
        # Calculate final rewards
        xp_earned = int(base_xp * difficulty_multiplier * sla_multiplier * level_bonus)
        reward_earned = base_reward * difficulty_multiplier * sla_multiplier
        
        # Mark incident as resolved
        incident.completion_time = time.time()
        incident.complete_resolution(success)
        
        # Award specialist
        specialist.gain_xp(xp_earned)
        specialist.assigned_incident_id = None
        
        # Add burnout to specialist (higher difficulty = more burnout)
        burnout_cost = int(5 + (incident.difficulty - 1) * 2)  # 5-13 burnout
        specialist.burnout_level = min(100.0, specialist.burnout_level + burnout_cost)
        
        # Remove from active assignments
        if incident.id in self._active_assignments:
            del self._active_assignments[incident.id]
        
        log_message = (
            f"[INCIDENT_DISPATCH] Resolved incident {incident.id} ({incident.incident_type}) "
            f"- Success: {success}, SLA Met: {sla_met}, XP: {xp_earned}, Reward: ${reward_earned:.0f}, "
            f"Time Taken: {time_taken:.0f}s, SLA Limit: {incident.sla_seconds}s"
        )
        
        if sla_met:
            self._logger.logger.info(log_message + " ✅")
        else:
            self._logger.logger.warning(log_message + " ⚠️")
        
        return ResolutionResult(
            success=success,
            sla_met=sla_met,
            time_taken=time_taken,
            xp_earned=xp_earned,
            reward_earned=reward_earned,
            specialist_id=specialist.id,
            incident_id=incident.id,
            client_id=incident.client_id
        )
    
    def get_pending_incidents(self) -> List[Incident]:
        """Get all pending incidents.
        
        Returns:
            List of incidents waiting for assignment
        """
        return [inc for inc in self._incidents.values() if inc.is_pending()]
    
    def get_active_incidents(self) -> List[Incident]:
        """Get all active (assigned or in-progress) incidents.
        
        Returns:
            List of currently active incidents
        """
        return [inc for inc in self._incidents.values() if inc.is_active()]
    
    def get_incidents_for_specialist(self, specialist_id: str) -> List[Incident]:
        """Get all incidents assigned to a specialist.
        
        Args:
            specialist_id: ID of the specialist
            
        Returns:
            List of incidents assigned to this specialist
        """
        return [inc for inc in self._incidents.values() if inc.assigned_specialist_id == specialist_id]
    
    def get_incidents_for_client(self, client_id: str) -> List[Incident]:
        """Get all incidents for a specific client.
        
        Args:
            client_id: ID of the client
            
        Returns:
            List of incidents for this client
        """
        return [inc for inc in self._incidents.values() if inc.client_id == client_id]
    
    def get_pending_incidents_for_client(self, client_id: str) -> List[Incident]:
        """Get all pending incidents for a specific client.
        
        Args:
            client_id: ID of the client
            
        Returns:
            List of pending incidents for this client
        """
        return [inc for inc in self._incidents.values() 
                if inc.client_id == client_id and inc.is_pending()]
    
    def get_overdue_incidents(self) -> List[Incident]:
        """Get all incidents that have exceeded their SLA deadline.
        
        Returns:
            List of overdue incidents
        """
        return [inc for inc in self._incidents.values() if inc.is_sla_overdue()]
    
    def find_best_specialist(
        self,
        incident: Incident,
        available_specialists: List[Specialist]
    ) -> Optional[Specialist]:
        """Find the best available specialist for an incident.
        
        Selection criteria (in order):
        1. Specialty must match
        2. Not currently assigned
        3. Prefer higher level
        4. Prefer lower burnout
        5. Prefer higher accuracy/speed stats
        
        Args:
            incident: Incident needing assignment
            available_specialists: List of specialists to consider
            
        Returns:
            Best matching specialist, or None if no match
        """
        # Filter by specialty match and availability
        candidates = [
            s for s in available_specialists
            if s.specialty == incident.specialty_required
            and s.assigned_incident_id is None
        ]
        
        if not candidates:
            return None
        
        # Sort by:
        # 1. Level (descending - higher is better)
        # 2. Burnout (ascending - lower is better)
        # 3. Random (for tie-breaking)
        candidates.sort(
            key=lambda s: (-s.level, s.burnout_level, random.random())
        )
        
        return candidates[0]
    
    def get_dispatch_stats(self) -> Dict[str, Any]:
        """Get statistics about current dispatch state.
        
        Returns:
            Dictionary with dispatch statistics
        """
        active_incidents = self.get_active_incidents()
        pending_incidents = self.get_pending_incidents()
        overdue_incidents = self.get_overdue_incidents()
        
        return {
            "total_incidents": len(self._incidents),
            "pending_count": len(pending_incidents),
            "active_count": len(active_incidents),
            "overdue_count": len(overdue_incidents),
            "sla_urgency_critical": sum(1 for inc in active_incidents if inc.get_sla_urgency() == "critical"),
            "sla_urgency_warning": sum(1 for inc in active_incidents if inc.get_sla_urgency() == "warning"),
        }
    
    def clear_resolved_incidents(self) -> int:
        """Remove all resolved/failed incidents from tracking.
        
        Returns:
            Number of incidents removed
        """
        initial_count = len(self._incidents)
        
        self._incidents = {
            incident_id: incident
            for incident_id, incident in self._incidents.items()
            if incident.is_active() or incident.is_pending()
        }
        
        removed = initial_count - len(self._incidents)
        self._logger.logger.info(f"[INCIDENT_DISPATCH] Cleared {removed} resolved/failed incidents")
        
        return removed
