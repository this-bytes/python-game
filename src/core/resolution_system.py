"""Incident resolution system with burnout integration."""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import random
from src.core.burnout_system import BurnoutSystem
from src.models.specialist import Specialist
from src.models.incident import Incident


@dataclass
class ResolutionResult:
    """Result of incident resolution attempt."""
    success: bool
    resolution_time: float
    base_time: float
    burnout_multiplier: float
    error_chance: float
    actual_success_rate: float
    specialist_id: str
    incident_id: str


class ResolutionSystem:
    """Calculate and apply incident resolution with burnout penalties."""

    def __init__(self, burnout_system: BurnoutSystem):
        self.burnout_system = burnout_system

    def calculate_resolution_time(
        self,
        specialist: Specialist,
        incident: Incident,
        base_time: float
    ) -> Tuple[float, float]:
        """Calculate actual resolution time with burnout multiplier.

        Args:
            specialist: Resolving specialist
            incident: Incident being resolved
            base_time: Base resolution time in seconds

        Returns:
            (actual_resolution_time, burnout_multiplier)

        Examples:
            - Burnout 0% (multiplier 1.0): base_time = 100s → 100s
            - Burnout 50% (multiplier 0.5): base_time = 100s → 200s
            - Burnout 80% (multiplier 0.25): base_time = 100s → 400s
            - Burnout 100% (multiplier 0.0): Can't resolve
        """
        multiplier = specialist.get_performance_multiplier()

        if multiplier <= 0.0:
            return float('inf'), 0.0

        actual_time = base_time / multiplier
        return actual_time, multiplier

    def calculate_success_rate(
        self,
        specialist: Specialist,
        incident: Incident,
        base_success_rate: float = 0.9
    ) -> float:
        """Calculate success rate with burnout error chance.

        Args:
            specialist: Resolving specialist
            incident: Incident being resolved
            base_success_rate: Base success probability (default 0.9 = 90%)

        Returns:
            Actual success probability (0.0 to 1.0)

        Examples:
            - Base 90%, Burnout 0% (error 0%): 90%
            - Base 90%, Burnout 50% (error 25%): 90% * (1 - 0.25) = 67.5%
            - Base 90%, Burnout 100% (error 50%): 90% * (1 - 0.50) = 45%
        """
        error_chance = specialist.get_error_chance_from_burnout()
        actual_rate = base_success_rate * (1.0 - error_chance)
        return max(0.0, min(1.0, actual_rate))

    def attempt_resolution(
        self,
        specialist: Specialist,
        incident: Incident,
        base_time: float = 100.0,
        base_success_rate: float = 0.9
    ) -> ResolutionResult:
        """Attempt to resolve incident with burnout effects.

        Args:
            specialist: Resolving specialist
            incident: Incident being resolved
            base_time: Base resolution time (seconds)
            base_success_rate: Base success probability

        Returns:
            ResolutionResult with outcome and metrics
        """
        multiplier = specialist.get_performance_multiplier()
        if multiplier <= 0.0:
            return ResolutionResult(
                success=False,
                resolution_time=float('inf'),
                base_time=base_time,
                burnout_multiplier=multiplier,
                error_chance=specialist.get_error_chance_from_burnout(),
                actual_success_rate=0.0,
                specialist_id=specialist.id,
                incident_id=incident.id
            )

        actual_time, burnout_mult = self.calculate_resolution_time(
            specialist, incident, base_time
        )
        success_rate = self.calculate_success_rate(
            specialist, incident, base_success_rate
        )

        success = random.random() < success_rate

        return ResolutionResult(
            success=success,
            resolution_time=actual_time,
            base_time=base_time,
            burnout_multiplier=burnout_mult,
            error_chance=specialist.get_error_chance_from_burnout(),
            actual_success_rate=success_rate,
            specialist_id=specialist.id,
            incident_id=incident.id
        )

    def complete_incident(
        self,
        specialist: Specialist,
        incident: Incident,
        success: bool,
        base_time: float = 100.0
    ) -> Dict:
        """Complete incident and update burnout system.

        Args:
            specialist: Specialist who resolved it
            incident: Incident being completed
            success: Whether resolution succeeded
            base_time: Base resolution time

        Returns:
            Status dict with updates
        """
        result = self.attempt_resolution(specialist, incident, base_time)

        incident.complete_resolution(success)

        self.burnout_system.complete_incident(
            specialist.id,
            success=success
        )

        return {
            'incident_id': incident.id,
            'specialist_id': specialist.id,
            'success': success,
            'resolution_time': result.resolution_time,
            'burnout_level': specialist.burnout_level,
            'burnout_tier': self.burnout_system.get_specialist_status(
                specialist.id
            )['tier'],
            'performance_multiplier': result.burnout_multiplier,
            'error_chance': result.error_chance
        }
