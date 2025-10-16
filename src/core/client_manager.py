"""Client relationship manager for tracking satisfaction and reputation.

The ClientManager handles client reputation updates based on incident outcomes,
calculates satisfaction metrics, determines client tier, and applies reputation-based
effects to gameplay.
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.models.client import Client
    from src.models.incident import Incident
    from src.models.game_state import GameState


class ClientManager:
    """Manages client relationships, reputation, and satisfaction."""

    def update_reputation(
        self, client: "Client", incident: "Incident", success: bool, sla_met: bool
    ) -> float:
        """Update client reputation based on incident outcome.

        Args:
            client: The client whose reputation to update
            incident: The completed incident
            success: Whether the incident was successfully resolved
            sla_met: Whether the SLA deadline was met

        Returns:
            The new reputation value
        """
        old_reputation = client.reputation

        if success and sla_met:
            # Excellent service: +2 reputation
            change = 2
            satisfaction = 100.0
        elif success and not sla_met:
            # Success but late: -1 reputation
            change = -1
            satisfaction = 60.0
        else:
            # Failed resolution: -5 reputation
            change = -5
            satisfaction = 0.0

        # Update reputation (clamped 0-100)
        client.reputation = max(0, min(100, old_reputation + change))

        # Track satisfaction history (keep last 10)
        client.satisfaction_history.append(satisfaction)
        if len(client.satisfaction_history) > 10:
            client.satisfaction_history.pop(0)

        # Update incident counters
        if success:
            client.total_incidents_resolved += 1
        if not sla_met:
            client.total_sla_failures += 1

        # Recalculate tier
        client.tier = self.determine_tier(client)

        return client.reputation

    def calculate_satisfaction(self, client: "Client") -> float:
        """Calculate average satisfaction from recent incidents.

        Args:
            client: The client to calculate satisfaction for

        Returns:
            Average satisfaction (0-100) based on recent incident history
        """
        if not client.satisfaction_history:
            return 100.0  # Default to perfect satisfaction

        return sum(client.satisfaction_history) / len(client.satisfaction_history)

    def determine_tier(self, client: "Client") -> int:
        """Determine client tier based on reputation.

        Tier breakdown:
        - Tier 1: 0-20 reputation (At Risk)
        - Tier 2: 20-40 reputation (Poor)
        - Tier 3: 40-60 reputation (Fair)
        - Tier 4: 60-80 reputation (Good)
        - Tier 5: 80-100 reputation (Excellent)

        Args:
            client: The client to determine tier for

        Returns:
            Client tier (1-5)
        """
        reputation = client.reputation

        if reputation >= 80:
            return 5
        elif reputation >= 60:
            return 4
        elif reputation >= 40:
            return 3
        elif reputation >= 20:
            return 2
        else:
            return 1

    def apply_reputation_effects(self, client: "Client") -> dict:
        """Calculate gameplay effects based on client reputation.

        High reputation clients (80-100):
        - +20% reward multiplier
        - -10% difficulty modifier

        Medium reputation clients (40-79):
        - Normal rewards and difficulty

        Low reputation clients (0-39):
        - -20% reward multiplier
        - +10% difficulty modifier

        Args:
            client: The client to calculate effects for

        Returns:
            Dictionary with 'reward_multiplier' and 'difficulty_modifier' keys
        """
        reputation = client.reputation

        if reputation >= 80:
            # High reputation: better rewards, easier incidents
            return {"reward_multiplier": 1.2, "difficulty_modifier": -0.1}
        elif reputation >= 40:
            # Medium reputation: neutral
            return {"reward_multiplier": 1.0, "difficulty_modifier": 0.0}
        else:
            # Low reputation: worse rewards, harder incidents
            return {"reward_multiplier": 0.8, "difficulty_modifier": 0.1}

    def check_contract_renewal(
        self, client: "Client", game_state: "GameState"
    ) -> bool:
        """Check if client will renew their contract.

        Contract renewal is based on:
        - Reputation >= 30: Will renew
        - Reputation < 30: Risk of cancellation
        - Reputation < 20: Very high risk of cancellation

        Args:
            client: The client to check
            game_state: Current game state (for future expansion)

        Returns:
            True if client will renew contract, False if at risk of cancellation
        """
        # Simple threshold-based renewal check
        if client.reputation >= 30:
            return True

        # Below 30 reputation: risk of losing client
        # Below 20 reputation: very likely to cancel
        return False

    def get_reputation_tier_name(self, tier: int) -> str:
        """Get human-readable name for reputation tier.

        Args:
            tier: The tier number (1-5)

        Returns:
            Tier name as string
        """
        tier_names = {
            1: "At Risk",
            2: "Poor",
            3: "Fair",
            4: "Good",
            5: "Excellent",
        }
        return tier_names.get(tier, "Unknown")

    def get_client_summary(self, client: "Client") -> dict:
        """Get comprehensive summary of client status.

        Args:
            client: The client to summarize

        Returns:
            Dictionary with client metrics and status
        """
        satisfaction = self.calculate_satisfaction(client)
        effects = self.apply_reputation_effects(client)
        will_renew = self.check_contract_renewal(client, None)
        tier_name = self.get_reputation_tier_name(client.tier)

        return {
            "client_id": client.id,
            "name": client.name,
            "reputation": client.reputation,
            "tier": client.tier,
            "tier_name": tier_name,
            "satisfaction": satisfaction,
            "total_incidents_assigned": client.total_incidents_assigned,
            "total_incidents_resolved": client.total_incidents_resolved,
            "total_sla_failures": client.total_sla_failures,
            "success_rate": (
                (client.total_incidents_resolved / client.total_incidents_assigned * 100)
                if client.total_incidents_assigned > 0
                else 0.0
            ),
            "sla_compliance_rate": (
                (
                    (client.total_incidents_assigned - client.total_sla_failures)
                    / client.total_incidents_assigned
                    * 100
                )
                if client.total_incidents_assigned > 0
                else 100.0
            ),
            "reward_multiplier": effects["reward_multiplier"],
            "difficulty_modifier": effects["difficulty_modifier"],
            "will_renew_contract": will_renew,
            "at_risk": not will_renew,
        }
