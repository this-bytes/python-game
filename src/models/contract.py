"""Contract model representing client service agreements.

Contracts define the terms of service between the firm and clients, including
payment terms, SLA requirements, penalties, and bonuses.
"""

from dataclasses import dataclass, field
from typing import Dict, Any
import time


@dataclass
class Contract:
    """Represents a service contract with a client."""

    id: str
    client_id: str
    contract_type: str  # RETAINER, PER_INCIDENT, PROJECT
    base_rate: float  # Base payment amount
    sla_terms: Dict[str, Any]  # SLA requirements
    duration_days: int  # Contract length in days
    penalties: Dict[str, float]  # Penalty multipliers
    bonuses: Dict[str, float]  # Bonus multipliers
    start_time: float
    end_time: float
    status: str  # ACTIVE, EXPIRED, TERMINATED
    incidents_handled: int = 0
    sla_compliance_rate: float = 100.0

    def __post_init__(self):
        """Validate and calculate fields after initialization."""
        # Calculate end_time from start_time + duration if not provided
        if self.end_time == 0:
            self.end_time = self.start_time + (self.duration_days * 86400)

    def is_active(self) -> bool:
        """Check if contract is currently active.

        Returns:
            True if contract status is ACTIVE and not expired
        """
        if self.status != "ACTIVE":
            return False

        current_time = time.time()
        return current_time < self.end_time

    def is_expired(self) -> bool:
        """Check if contract has expired.

        Returns:
            True if current time is past end_time
        """
        current_time = time.time()
        return current_time >= self.end_time

    def get_time_remaining(self) -> float:
        """Get time remaining on contract.

        Returns:
            Time remaining in seconds (negative if expired)
        """
        current_time = time.time()
        return self.end_time - current_time

    def get_days_remaining(self) -> int:
        """Get days remaining on contract.

        Returns:
            Days remaining (rounded down, 0 if expired)
        """
        time_remaining = self.get_time_remaining()
        if time_remaining < 0:
            return 0
        return int(time_remaining / 86400)

    def get_duration_elapsed(self) -> float:
        """Get elapsed time since contract start.

        Returns:
            Elapsed time in seconds
        """
        current_time = time.time()
        return current_time - self.start_time

    def update_sla_compliance(self, incident_sla_met: bool):
        """Update SLA compliance rate based on incident outcome.

        Args:
            incident_sla_met: Whether SLA was met for the incident
        """
        self.incidents_handled += 1

        # Recalculate compliance rate
        # Use weighted average to incorporate new result
        total_met = self.sla_compliance_rate * (self.incidents_handled - 1) / 100.0
        if incident_sla_met:
            total_met += 1

        self.sla_compliance_rate = (total_met / self.incidents_handled) * 100.0

    def calculate_penalty(self, incident_base_reward: float) -> float:
        """Calculate penalty for SLA failure.

        Args:
            incident_base_reward: Base reward of the incident

        Returns:
            Penalty amount
        """
        penalty_multiplier = self.penalties.get("sla_failure", 0.0)
        return incident_base_reward * penalty_multiplier

    def calculate_bonus(self, incident_base_reward: float, bonus_type: str = "fast_resolution") -> float:
        """Calculate bonus for exceptional performance.

        Args:
            incident_base_reward: Base reward of the incident
            bonus_type: Type of bonus to calculate

        Returns:
            Bonus amount
        """
        bonus_multiplier = self.bonuses.get(bonus_type, 0.0)
        return incident_base_reward * bonus_multiplier

    def terminate(self, reason: str = "client_termination"):
        """Terminate the contract.

        Args:
            reason: Reason for termination
        """
        self.status = "TERMINATED"

    def expire(self):
        """Mark contract as expired."""
        self.status = "EXPIRED"

    def renew(self, new_duration_days: int, new_terms: Dict[str, Any] = None):
        """Renew contract with updated terms.

        Args:
            new_duration_days: New contract duration
            new_terms: Optional dictionary with updated terms
        """
        self.start_time = time.time()
        self.duration_days = new_duration_days
        self.end_time = self.start_time + (new_duration_days * 86400)
        self.status = "ACTIVE"
        self.incidents_handled = 0
        self.sla_compliance_rate = 100.0

        # Update terms if provided
        if new_terms:
            if "base_rate" in new_terms:
                self.base_rate = new_terms["base_rate"]
            if "sla_terms" in new_terms:
                self.sla_terms = new_terms["sla_terms"]
            if "penalties" in new_terms:
                self.penalties = new_terms["penalties"]
            if "bonuses" in new_terms:
                self.bonuses = new_terms["bonuses"]

    def to_dict(self) -> Dict:
        """Convert contract to dictionary for serialization.

        Returns:
            Dictionary representation of the contract
        """
        return {
            "id": self.id,
            "client_id": self.client_id,
            "contract_type": self.contract_type,
            "base_rate": self.base_rate,
            "sla_terms": self.sla_terms.copy(),
            "duration_days": self.duration_days,
            "penalties": self.penalties.copy(),
            "bonuses": self.bonuses.copy(),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "incidents_handled": self.incidents_handled,
            "sla_compliance_rate": self.sla_compliance_rate,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Contract":
        """Create Contract from dictionary.

        Args:
            data: Dictionary containing contract data

        Returns:
            New Contract instance
        """
        return cls(
            id=data["id"],
            client_id=data["client_id"],
            contract_type=data["contract_type"],
            base_rate=data["base_rate"],
            sla_terms=data["sla_terms"].copy(),
            duration_days=data["duration_days"],
            penalties=data["penalties"].copy(),
            bonuses=data["bonuses"].copy(),
            start_time=data["start_time"],
            end_time=data["end_time"],
            status=data["status"],
            incidents_handled=data.get("incidents_handled", 0),
            sla_compliance_rate=data.get("sla_compliance_rate", 100.0),
        )

    def __repr__(self) -> str:
        """String representation of contract."""
        return (
            f"Contract(id='{self.id}', client_id='{self.client_id}', "
            f"type='{self.contract_type}', status='{self.status}', "
            f"days_remaining={self.get_days_remaining()})"
        )
