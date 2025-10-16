"""Contract management system for negotiating and managing service agreements.

The ContractManager handles contract negotiation, renewal, termination, and
calculates penalties/bonuses based on contract terms.
"""

from typing import TYPE_CHECKING, Dict, List, Optional
import time
import uuid

if TYPE_CHECKING:
    from src.models.client import Client
    from src.models.contract import Contract
    from src.models.incident import Incident
    from src.models.game_state import GameState


class ContractManager:
    """Manages service contracts with clients."""

    def __init__(self):
        """Initialize the ContractManager."""
        self.contract_templates: Dict[str, Dict] = {}

    def load_templates(self, templates_data: List[Dict]):
        """Load contract templates from configuration.

        Args:
            templates_data: List of contract template dictionaries
        """
        for template in templates_data:
            self.contract_templates[template["id"]] = template

    def negotiate_contract(
        self,
        client: "Client",
        template_id: str,
        terms: Dict,
        game_state: "GameState",
    ) -> Optional["Contract"]:
        """Negotiate a new contract with a client.

        Args:
            client: The client to negotiate with
            template_id: ID of the contract template to use
            terms: Negotiation terms (can adjust base_rate, duration, etc.)
            game_state: Current game state

        Returns:
            New Contract instance if successful, None otherwise
        """
        from src.models.contract import Contract

        # Get template
        template = self.contract_templates.get(template_id)
        if not template:
            return None

        # Check client reputation - better reputation = better terms possible
        if client.reputation < 30:
            # Low reputation clients unlikely to accept negotiations
            return None

        # Create contract from template with negotiated terms
        contract_id = f"contract_{uuid.uuid4().hex[:8]}"
        base_rate = terms.get("base_rate", template["base_rate"])
        duration_days = terms.get("duration_days", template["duration_days"])

        contract = Contract(
            id=contract_id,
            client_id=client.id,
            contract_type=template["contract_type"],
            base_rate=base_rate,
            sla_terms=template["sla_terms"].copy(),
            duration_days=duration_days,
            penalties=template["penalties"].copy(),
            bonuses=template["bonuses"].copy(),
            start_time=time.time(),
            end_time=0,  # Will be calculated in __post_init__
            status="ACTIVE",
        )

        # Add contract to client's contract list
        client.contracts.append(contract_id)

        return contract

    def renew_contract(
        self, contract: "Contract", game_state: "GameState"
    ) -> "Contract":
        """Renew an existing contract with potentially improved terms.

        Args:
            contract: The contract to renew
            game_state: Current game state

        Returns:
            Renewed contract
        """
        # Get client to check reputation
        client = game_state.get_client_by_id(contract.client_id)
        if not client:
            return contract

        # Better reputation = better renewal terms
        new_duration = contract.duration_days
        new_base_rate = contract.base_rate

        if client.reputation >= 80:
            # Excellent reputation: 20% rate increase, longer duration
            new_base_rate *= 1.2
            new_duration = int(new_duration * 1.5)
        elif client.reputation >= 60:
            # Good reputation: 10% rate increase
            new_base_rate *= 1.1

        # Renew with improved terms
        contract.renew(
            new_duration_days=new_duration, new_terms={"base_rate": new_base_rate}
        )

        return contract

    def terminate_contract(
        self, contract: "Contract", reason: str, game_state: "GameState"
    ) -> float:
        """Terminate a contract and calculate termination penalties.

        Args:
            contract: The contract to terminate
            reason: Reason for termination
            game_state: Current game state

        Returns:
            Termination penalty amount (0 if graceful)
        """
        contract.terminate(reason)

        # Calculate penalty based on contract type and remaining time
        if reason == "client_termination":
            # Client terminated - no penalty
            return 0.0
        elif reason == "firm_termination":
            # We terminated - penalty based on remaining value
            days_remaining = contract.get_days_remaining()
            if contract.contract_type == "retainer":
                # Retainer: forfeit remaining payments
                daily_rate = contract.base_rate / contract.duration_days
                return daily_rate * days_remaining
            else:
                # Per-incident/project: fixed penalty
                return contract.base_rate * 0.5

        return 0.0

    def apply_penalties(
        self, contract: "Contract", incident: "Incident"
    ) -> float:
        """Calculate and apply SLA failure penalties.

        Args:
            contract: The contract with penalty terms
            incident: The incident that failed SLA

        Returns:
            Penalty amount
        """
        return contract.calculate_penalty(incident.base_reward)

    def apply_bonuses(
        self,
        contract: "Contract",
        incident: "Incident",
        bonus_type: str = "fast_resolution",
    ) -> float:
        """Calculate and apply performance bonuses.

        Args:
            contract: The contract with bonus terms
            incident: The incident that earned bonus
            bonus_type: Type of bonus earned

        Returns:
            Bonus amount
        """
        return contract.calculate_bonus(incident.base_reward, bonus_type)

    def calculate_retainer_income(
        self, contracts: List["Contract"], delta_time: float
    ) -> float:
        """Calculate passive income from active retainer contracts.

        Args:
            contracts: List of all contracts
            delta_time: Time elapsed since last calculation (seconds)

        Returns:
            Total passive income earned
        """
        total_income = 0.0

        for contract in contracts:
            if contract.contract_type == "retainer" and contract.is_active():
                # Calculate income based on time elapsed
                # Retainer pays evenly over contract duration
                daily_rate = contract.base_rate / contract.duration_days
                seconds_per_day = 86400
                income_per_second = daily_rate / seconds_per_day

                total_income += income_per_second * delta_time

        return total_income

    def check_expirations(self, contracts: List["Contract"]) -> List["Contract"]:
        """Check for expired contracts and update their status.

        Args:
            contracts: List of all contracts

        Returns:
            List of newly expired contracts
        """
        expired = []

        for contract in contracts:
            if contract.status == "ACTIVE" and contract.is_expired():
                contract.expire()
                expired.append(contract)

        return expired

    def get_contract_summary(self, contract: "Contract") -> Dict:
        """Get comprehensive summary of contract status.

        Args:
            contract: The contract to summarize

        Returns:
            Dictionary with contract metrics and status
        """
        return {
            "id": contract.id,
            "client_id": contract.client_id,
            "contract_type": contract.contract_type,
            "base_rate": contract.base_rate,
            "status": contract.status,
            "is_active": contract.is_active(),
            "days_remaining": contract.get_days_remaining(),
            "time_remaining_seconds": contract.get_time_remaining(),
            "duration_days": contract.duration_days,
            "incidents_handled": contract.incidents_handled,
            "sla_compliance_rate": contract.sla_compliance_rate,
            "sla_terms": contract.sla_terms,
            "penalties": contract.penalties,
            "bonuses": contract.bonuses,
        }

    def get_active_contracts_count(self, contracts: List["Contract"]) -> int:
        """Get count of active contracts.

        Args:
            contracts: List of all contracts

        Returns:
            Number of active contracts
        """
        return sum(1 for c in contracts if c.is_active())

    def get_total_retainer_value(self, contracts: List["Contract"]) -> float:
        """Get total value of all active retainer contracts.

        Args:
            contracts: List of all contracts

        Returns:
            Total retainer value
        """
        return sum(
            c.base_rate
            for c in contracts
            if c.contract_type == "retainer" and c.is_active()
        )
