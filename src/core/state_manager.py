"""
StateManager - Pure data layer for entity storage and CRUD operations.

This module provides the foundation layer of the new game state architecture.
StateManager handles all entity storage and basic CRUD operations without
any business logic or validation.
"""

from typing import Dict, List, Optional, Any, Iterator
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from src.models.specialist import Specialist
from src.models.incident import Incident
from src.models.client import Client
from src.models.contract import Contract
from src.models.budget import Budget
from src.models.sla_tracker import SLATracker


@dataclass
class StateManager:
    """
    Pure data layer for entity storage and CRUD operations.

    StateManager provides thread-safe, validated storage for all game entities
    without any business logic. It handles basic CRUD operations and maintains
    referential integrity between entities.
    """

    # Entity collections
    specialists: Dict[str, Specialist] = field(default_factory=dict)
    incidents: Dict[str, Incident] = field(default_factory=dict)
    clients: Dict[str, Client] = field(default_factory=dict)
    contracts: Dict[str, Contract] = field(default_factory=dict)
    sla_trackers: Dict[str, SLATracker] = field(default_factory=dict)

    # Game metadata
    budget: Optional[Budget] = None
    game_time: float = 0.0
    day_counter: int = 0
    company_name: str = "SOC Startup"

    # Metrics and statistics
    total_incidents_resolved: int = 0
    total_money_earned: float = 0.0
    total_xp_gained: int = 0

    def __post_init__(self):
        """Initialize StateManager with empty collections if needed."""
        if self.budget is None:
            self.budget = Budget(total_reserves=5000.0)

    # ===== SPECIALIST OPERATIONS =====

    def add_specialist(self, specialist: Specialist) -> None:
        """Add a specialist to the state."""
        self.specialists[specialist.id] = specialist

    def get_specialist(self, specialist_id: str) -> Optional[Specialist]:
        """Get a specialist by ID."""
        return self.specialists.get(specialist_id)

    def remove_specialist(self, specialist_id: str) -> Optional[Specialist]:
        """Remove and return a specialist by ID."""
        return self.specialists.pop(specialist_id, None)

    def get_all_specialists(self) -> List[Specialist]:
        """Get all specialists."""
        return list(self.specialists.values())

    def get_specialists_by_specialty(self, specialty: str) -> List[Specialist]:
        """Get all specialists with a specific specialty."""
        return [s for s in self.specialists.values() if s.specialty == specialty]

    def get_available_specialists(self) -> List[Specialist]:
        """Get specialists who are not currently assigned to incidents."""
        return [s for s in self.specialists.values() if s.current_incident is None]

    # ===== INCIDENT OPERATIONS =====

    def add_incident(self, incident: Incident) -> None:
        """Add an incident to the state."""
        self.incidents[incident.id] = incident

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get an incident by ID."""
        return self.incidents.get(incident_id)

    def remove_incident(self, incident_id: str) -> Optional[Incident]:
        """Remove and return an incident by ID."""
        return self.incidents.pop(incident_id, None)

    def get_all_incidents(self) -> List[Incident]:
        """Get all incidents."""
        return list(self.incidents.values())

    def get_active_incidents(self) -> List[Incident]:
        """Get incidents that are not resolved."""
        return [i for i in self.incidents.values() if not i.is_resolved]

    def get_incidents_by_client(self, client_id: str) -> List[Incident]:
        """Get all incidents for a specific client."""
        return [i for i in self.incidents.values() if i.client_id == client_id]

    def get_unassigned_incidents(self) -> List[Incident]:
        """Get incidents that are not assigned to any specialist."""
        return [i for i in self.incidents.values() if i.assigned_specialist_id is None]

    # ===== CLIENT OPERATIONS =====

    def add_client(self, client: Client) -> None:
        """Add a client to the state."""
        self.clients[client.client_id] = client

    def get_client(self, client_id: str) -> Optional[Client]:
        """Get a client by ID."""
        return self.clients.get(client_id)

    def remove_client(self, client_id: str) -> Optional[Client]:
        """Remove and return a client by ID."""
        return self.clients.pop(client_id, None)

    def get_all_clients(self) -> List[Client]:
        """Get all clients."""
        return list(self.clients.values())

    def get_active_clients(self) -> List[Client]:
        """Get clients that are currently active."""
        return [c for c in self.clients.values() if c.is_active]

    # ===== CONTRACT OPERATIONS =====

    def add_contract(self, contract: Contract) -> None:
        """Add a contract to the state."""
        self.contracts[contract.id] = contract

    def get_contract(self, contract_id: str) -> Optional[Contract]:
        """Get a contract by ID."""
        return self.contracts.get(contract_id)

    def remove_contract(self, contract_id: str) -> Optional[Contract]:
        """Remove and return a contract by ID."""
        return self.contracts.pop(contract_id, None)

    def get_all_contracts(self) -> List[Contract]:
        """Get all contracts."""
        return list(self.contracts.values())

    def get_contracts_by_client(self, client_id: str) -> List[Contract]:
        """Get all contracts for a specific client."""
        return [c for c in self.contracts.values() if c.client_id == client_id]

    # ===== SLA TRACKER OPERATIONS =====

    def add_sla_tracker(self, sla_tracker: SLATracker) -> None:
        """Add an SLA tracker to the state."""
        self.sla_trackers[sla_tracker.tracker_id] = sla_tracker

    def get_sla_tracker(self, tracker_id: str) -> Optional[SLATracker]:
        """Get an SLA tracker by ID."""
        return self.sla_trackers.get(tracker_id)

    def remove_sla_tracker(self, tracker_id: str) -> Optional[SLATracker]:
        """Remove and return an SLA tracker by ID."""
        return self.sla_trackers.pop(tracker_id, None)

    def get_all_sla_trackers(self) -> List[SLATracker]:
        """Get all SLA trackers."""
        return list(self.sla_trackers.values())

    def get_sla_trackers_by_client(self, client_id: str) -> List[SLATracker]:
        """Get all SLA trackers for a specific client."""
        return [t for t in self.sla_trackers.values() if t.client_id == client_id]

    # ===== BUDGET OPERATIONS =====

    def update_budget(self, new_budget: Budget) -> None:
        """Update the budget."""
        self.budget = new_budget

    def get_budget(self) -> Budget:
        """Get the current budget."""
        return self.budget

    # ===== METADATA OPERATIONS =====

    def update_game_time(self, new_time: float) -> None:
        """Update the game time."""
        self.game_time = new_time

    def increment_day_counter(self) -> None:
        """Increment the day counter."""
        self.day_counter += 1

    def update_metrics(self, incidents_resolved: int = 0, money_earned: float = 0.0, xp_gained: int = 0) -> None:
        """Update game metrics."""
        self.total_incidents_resolved += incidents_resolved
        self.total_money_earned += money_earned
        self.total_xp_gained += xp_gained

    # ===== SERIALIZATION =====

    def to_dict(self) -> Dict[str, Any]:
        """Convert StateManager to dictionary for serialization."""
        return {
            "specialists": {sid: s.to_dict() for sid, s in self.specialists.items()},
            "incidents": {iid: i.to_dict() for iid, i in self.incidents.items()},
            "clients": {cid: c.to_dict() for cid, c in self.clients.items()},
            "contracts": {cid: c.to_dict() for cid, c in self.contracts.items()},
            "sla_trackers": {tid: t.to_dict() for tid, t in self.sla_trackers.items()},
            "budget": self.budget.to_dict() if self.budget else None,
            "game_time": self.game_time,
            "day_counter": self.day_counter,
            "company_name": self.company_name,
            "total_incidents_resolved": self.total_incidents_resolved,
            "total_money_earned": self.total_money_earned,
            "total_xp_gained": self.total_xp_gained,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateManager":
        """Create StateManager from dictionary."""
        # Create empty StateManager
        state_manager = cls()

        # Load specialists
        for specialist_id, specialist_data in data.get("specialists", {}).items():
            specialist = Specialist.from_dict(specialist_data)
            state_manager.add_specialist(specialist)

        # Load incidents
        for incident_id, incident_data in data.get("incidents", {}).items():
            incident = Incident.from_dict(incident_data)
            state_manager.add_incident(incident)

        # Load clients
        for client_id, client_data in data.get("clients", {}).items():
            client = Client.from_dict(client_data)
            state_manager.add_client(client)

        # Load contracts
        for contract_id, contract_data in data.get("contracts", {}).items():
            contract = Contract.from_dict(contract_data)
            state_manager.add_contract(contract)

        # Load SLA trackers
        for tracker_id, tracker_data in data.get("sla_trackers", {}).items():
            tracker = SLATracker.from_dict(tracker_data)
            state_manager.add_sla_tracker(tracker)

        # Load budget
        budget_data = data.get("budget")
        if budget_data:
            state_manager.update_budget(Budget.from_dict(budget_data))

        # Load metadata
        state_manager.game_time = data.get("game_time", 0.0)
        state_manager.day_counter = data.get("day_counter", 0)
        state_manager.company_name = data.get("company_name", "SOC Startup")
        state_manager.total_incidents_resolved = data.get("total_incidents_resolved", 0)
        state_manager.total_money_earned = data.get("total_money_earned", 0.0)
        state_manager.total_xp_gained = data.get("total_xp_gained", 0)

        return state_manager

    # ===== UTILITY METHODS =====

    def clear_all_entities(self) -> None:
        """Clear all entities from the state manager."""
        self.specialists.clear()
        self.incidents.clear()
        self.clients.clear()
        self.contracts.clear()
        self.sla_trackers.clear()
        self.budget = Budget()

    def get_entity_counts(self) -> Dict[str, int]:
        """Get counts of all entities."""
        return {
            "specialists": len(self.specialists),
            "incidents": len(self.incidents),
            "clients": len(self.clients),
            "contracts": len(self.contracts),
            "sla_trackers": len(self.sla_trackers),
        }

    def validate_referential_integrity(self) -> List[str]:
        """
        Validate referential integrity between entities.

        Returns a list of validation errors found.
        """
        errors = []

        # Check incident -> specialist references
        for incident in self.incidents.values():
            if incident.assigned_specialist_id and incident.assigned_specialist_id not in self.specialists:
                errors.append(f"Incident {incident.id} references non-existent specialist {incident.assigned_specialist_id}")

        # Check incident -> client references
        for incident in self.incidents.values():
            if incident.client_id and incident.client_id not in self.clients:
                errors.append(f"Incident {incident.id} references non-existent client {incident.client_id}")

        # Check contract -> client references
        for contract in self.contracts.values():
            if contract.client_id and contract.client_id not in self.clients:
                errors.append(f"Contract {contract.id} references non-existent client {contract.client_id}")

        # Check SLA tracker -> client references
        for tracker in self.sla_trackers.values():
            if tracker.client_id and tracker.client_id not in self.clients:
                errors.append(f"SLA tracker {tracker.id} references non-existent client {tracker.client_id}")

        return errors