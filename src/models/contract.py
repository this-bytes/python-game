"""SOC Startup Contract model for managing service agreements.

This implementation is intentionally backward-compatible with older
test fixtures and templates. It accepts legacy keyword names and
exposes the methods that the test-suite expects (time calculations,
SLA tracking, penalties/bonuses, serialization).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any
import time


@dataclass
class Contract:
    """Represents a service contract with a client.

    The constructor accepts both the modern field names and legacy
    template/fixture keys (e.g. contract_type, base_rate, duration_days,
    start_time). This keeps tests and older save files working.
    """

    # Identity
    id: str
    client_id: str

    # Core terms (legacy names supported)
    contract_type: str = "retainer"
    base_rate: float = 0.0
    sla_terms: dict = field(default_factory=dict)
    duration_days: int = 30

    # Time tracking (epoch seconds)
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0

    # Penalties / bonuses
    penalties: dict = field(default_factory=dict)
    bonuses: dict = field(default_factory=dict)

    # SLA tracking
    sla_compliance_rate: float = 100.0
    incidents_handled: int = 0

    # Status
    status: str = "ACTIVE"

    def __post_init__(self) -> None:
        # Backwards compat: ensure end_time computed when 0
        if not self.end_time or self.end_time == 0:
            self.end_time = self.start_time + (self.duration_days * 86400)

    def is_active(self) -> bool:
        return self.status.upper() == "ACTIVE"

    # Note: keep is_active as a method for compatibility with tests that call
    # `contract.is_active()`. ContractManager and other callers should handle
    # both method and attribute access by checking `callable(...)` when needed.

    def is_expired(self) -> bool:
        return time.time() > self.end_time

    def get_time_remaining(self) -> float:
        return max(0.0, self.end_time - time.time())

    def get_days_remaining(self) -> int:
        seconds = self.get_time_remaining()
        days = int(seconds // 86400)
        return max(0, days)

    def update_sla_compliance(self, met: bool) -> None:
        """Update SLA compliance rate given a boolean (met/failed)."""
        self.incidents_handled += 1
        met_count = int(round(self.sla_compliance_rate / 100.0 * (self.incidents_handled - 1)))
        met_count += 1 if met else 0
        self.sla_compliance_rate = (met_count / self.incidents_handled) * 100.0

    def calculate_penalty(self, amount: float) -> float:
        # Default: use penalties['sla_failure'] multiplier if present
        multiplier = self.penalties.get("sla_failure", 0.5)
        return amount * multiplier

    def calculate_bonus(self, amount: float, bonus_key: str) -> float:
        multiplier = self.bonuses.get(bonus_key, 1.0)
        return amount * multiplier

    def terminate(self, reason: str = "terminated") -> None:
        self.status = "TERMINATED"

    def expire(self) -> None:
        self.status = "EXPIRED"

    def renew(self, duration_days: int, overrides: Dict[str, Any] | None = None) -> None:
        overrides = overrides or {}
        self.duration_days = duration_days
        self.base_rate = overrides.get("base_rate", self.base_rate)
        self.start_time = time.time()
        self.end_time = self.start_time + (self.duration_days * 86400)
        self.status = "ACTIVE"
        self.incidents_handled = 0
        self.sla_compliance_rate = 100.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "client_id": self.client_id,
            "contract_type": self.contract_type,
            "base_rate": float(self.base_rate),
            "sla_terms": self.sla_terms,
            "duration_days": int(self.duration_days),
            "penalties": self.penalties,
            "bonuses": self.bonuses,
            "start_time": float(self.start_time),
            "end_time": float(self.end_time),
            "status": self.status,
            "sla_compliance_rate": float(self.sla_compliance_rate),
            "incidents_handled": int(self.incidents_handled),
        }

    @staticmethod
    def from_dict(data: dict) -> "Contract":
        # Accept both modern and legacy keys
        return Contract(
            id=data.get("id") or data.get("contract_id"),
            client_id=data.get("client_id") or data.get("client"),
            contract_type=data.get("contract_type") or data.get("contract_type"),
            base_rate=data.get("base_rate") or data.get("monthly_value") or 0.0,
            sla_terms=data.get("sla_terms", {}),
            duration_days=data.get("duration_days", data.get("duration", 30)),
            start_time=data.get("start_time", time.time()),
            end_time=data.get("end_time", 0),
            penalties=data.get("penalties", {}),
            bonuses=data.get("bonuses", {}),
            status=data.get("status", "ACTIVE"),
            sla_compliance_rate=data.get("sla_compliance_rate", 100.0),
            incidents_handled=data.get("incidents_handled", 0),
        )

