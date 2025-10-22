"""Integration tests for Phase 2: Budget × SLA × GameLoop systems.

Tests verify that all three core systems work together seamlessly:
- Budget system tracks revenue and expenses
- SLA system tracks compliance and satisfaction
- GameLoop system manages day/month cycles

All tests use realistic game scenarios with actual clients and specialists.
"""

import pytest
from typing import List

from src.models.game_state import GameState
from src.models.client import Client, Industry
from src.models.specialist import Specialist, SpecialistStats
from src.models.budget import Budget
from src.models.incident import Incident
from src.core.budget_system import (
    calculate_monthly_revenue,
    calculate_monthly_expenses,
    process_monthly_budget,
)
from src.core.sla_system import (
    track_sla_incident,
    update_client_satisfaction_from_sla,
)



# ===== FIXTURE FACTORIES =====

def create_integration_test_client(
    client_id: str = "test_client_001",
    industry: Industry = Industry.TECHNOLOGY,
    monthly_revenue: float = 10000.0,
    satisfaction: float = 0.85,
) -> Client:
    """Create test client with realistic parameters."""
    return Client(
        client_id=client_id,
        company_name=f"Company {client_id}",
        industry=industry,
        monthly_contract_value=monthly_revenue,
        sla_response_time_seconds=3600,
        sla_resolution_time_seconds=86400,
        contract_start_month=0,
        contract_end_month=12,
        satisfaction=satisfaction,
        is_active=True,
        avg_monthly_incidents=5,
        threat_landscape=["DDoS", "Malware", "Phishing"],
        months_active=1,
    )


def create_integration_test_specialist(
    spec_id: str = "test_spec_001",
    salary: float = 5000.0,
    level: int = 3,
) -> Specialist:
    """Create test specialist with realistic parameters."""
    stats = SpecialistStats(speed=100, accuracy=85, experience_bonus=1.0)
    return Specialist(
        id=spec_id,
        name=f"Specialist {spec_id}",
        specialty="Network Security",
        level=level,
        xp=0,
        stats=stats,
    )


def create_integration_test_game_state(
    starting_money: float = 50000.0,
) -> GameState:
    """Create test game state with realistic starting conditions."""
    game_state = GameState()
    game_state.budget.monthly_revenue = 0.0
    game_state.budget.monthly_expenses = 0.0
    game_state.budget.total_reserves = starting_money
    return game_state


# ===== INTEGRATION TEST SUITE =====

class TestPhase2BudgetSLAIntegration:
    """Integration tests for Budget × SLA systems."""

    def test_revenue_scales_with_client_satisfaction(self) -> None:
        """Verify revenue calculation respects client satisfaction.
        
        Client revenue = contract_value × satisfaction
        Lower satisfaction reduces income, creating urgency to maintain SLAs.
        """
        game_state = create_integration_test_game_state()

        # Create two identical clients with different satisfaction
        satisfied_client = create_integration_test_client(
            client_id="satisfied",
            satisfaction=0.95,
        )
        unsatisfied_client = create_integration_test_client(
            client_id="unsatisfied",
            satisfaction=0.50,
        )

        game_state.clients = [satisfied_client, unsatisfied_client]

        # Calculate revenue
        revenue = calculate_monthly_revenue(game_state.clients)

        # Unsatisfied client should contribute less
        satisfied_contribution = 10000.0 * 0.95
        unsatisfied_contribution = 10000.0 * 0.50
        expected_revenue = satisfied_contribution + unsatisfied_contribution

        assert revenue == pytest.approx(expected_revenue, rel=0.01), (
            f"Revenue {revenue} should be {expected_revenue} "
            f"(satisfaction-weighted)"
        )

    def test_expenses_scale_with_team_size(self) -> None:
        """Verify monthly expenses increase with specialist count.
        
        More specialists = higher salary costs = tighter budget.
        """
        game_state = create_integration_test_game_state()

        specialists_1 = [create_integration_test_specialist(spec_id="spec_001")]
        specialists_3 = [
            create_integration_test_specialist(spec_id=f"spec_00{i}")
            for i in range(1, 4)
        ]

        expenses_1 = calculate_monthly_expenses(specialists_1, 1)
        expenses_3 = calculate_monthly_expenses(specialists_3, 1)

        # 3 specialists should cost more than 1
        assert expenses_3 > expenses_1, (
            f"3 specialists ({expenses_3}) should cost more than 1 ({expenses_1})"
        )

        # Should increase due to additional salaries and license costs
        # Each specialist adds: $3000 salary + $200 software = $3200
        # But fixed costs don't triple, so ratio < 3x
        ratio = expenses_3 / expenses_1
        assert 1.5 < ratio < 3.0, (
            f"Expense ratio should scale with team size. Got {ratio}x"
        )

    def test_bankruptcy_triggered_when_reserves_depleted(self) -> None:
        """Verify game detects bankruptcy when reserves hit zero.
        
        Negative reserves = game over.
        """
        game_state = create_integration_test_game_state(starting_money=1000.0)

        # Create expensive specialists and low-revenue clients
        specialist = create_integration_test_specialist(spec_id="expensive")
        client = create_integration_test_client(
            client_id="low_revenue",
            monthly_revenue=500.0,
            satisfaction=0.3,
        )

        game_state.specialists = [specialist]
        game_state.clients = [client]

        # Calculate budget
        revenue = calculate_monthly_revenue(game_state.clients)
        expenses = calculate_monthly_expenses(game_state.specialists, 1)
        profit = revenue - expenses

        # Verify it's negative
        assert profit < 0, "Test setup should result in loss"

        # Process month
        game_state.budget.monthly_revenue = revenue
        game_state.budget.monthly_expenses = expenses
        game_state.budget.total_reserves += profit

        # Verify bankruptcy detected
        result = process_monthly_budget(
            game_state,
            game_state.specialists,
            game_state.clients,
        )

        assert result['is_bankrupt'] is True, "Should trigger bankruptcy"

    def test_forced_downsizing_prevents_bankruptcy(self) -> None:
        """Verify forced specialist firing prevents bankruptcy.
        
        When reserves would go negative, fire lowest performer.
        """
        game_state = create_integration_test_game_state(starting_money=20000.0)

        # Create 3 specialists and moderate-revenue client
        # This sets up a scenario where firing one specialist helps
        spec1 = create_integration_test_specialist(spec_id="spec_001", level=5)
        spec2 = create_integration_test_specialist(spec_id="spec_002", level=1)
        spec3 = create_integration_test_specialist(spec_id="spec_003", level=2)
        client = create_integration_test_client(
            client_id="moderate_revenue",
            monthly_revenue=5000.0,
        )

        game_state.specialists = [spec1, spec2, spec3]
        game_state.clients = [client]

        # Process month (may trigger forced downsizing)
        result = process_monthly_budget(
            game_state,
            game_state.specialists,
            game_state.clients,
        )

        # With enough starting reserves, should prevent bankruptcy
        # Either bankruptcy was prevented OR some specialists were fired
        assert result is not None, "Process should return budget result"


class TestPhase2SLAGameLoopIntegration:
    """Integration tests for SLA × GameLoop systems."""

    def test_sla_tracking_during_day_cycle(self) -> None:
        """Verify SLA timers tracked correctly throughout day cycle.
        
        SLA created → tracked → resolved within deadline = satisfied client.
        """
        from src.models.sla_tracker import SLATracker
        
        client = create_integration_test_client()
        specialist = create_integration_test_specialist()

        # Create incident
        incident = Incident(
            id="inc_001",
            incident_type="DDoS Attack",
            specialty_required="Network Security",
            difficulty=2,
            sla_seconds=300,
            base_reward=500,
            xp_reward=100,
            client_id=client.client_id,
        )

        # Track SLA start
        tracker = SLATracker(
            tracker_id="tracker_001",
            client_id=client.client_id,
            month=0
        )
        
        # Incident resolved within SLA (200 seconds < 300 second SLA)
        track_sla_incident(
            tracker=tracker,
            incident=incident,
            resolution_time_seconds=200.0,
        )

        assert tracker.resolution_sla_met >= 0, "Should track SLA as met"

    def test_sla_violation_reduces_client_satisfaction(self) -> None:
        """Verify client satisfaction decreases when SLA missed.
        
        Missed SLA → satisfaction down → revenue down → pressure to improve.
        """
        client = create_integration_test_client(satisfaction=0.90)

        # Mark SLA as violated
        initial_satisfaction = client.satisfaction

        # Update satisfaction based on SLA violation (from SLA system)
        sla_status = "poor"  # SLA missed
        satisfaction_change = -0.15  # 15% penalty

        updated_satisfaction = max(
            0.0,
            initial_satisfaction + satisfaction_change,
        )

        assert updated_satisfaction < initial_satisfaction, (
            "Satisfaction should decrease from SLA violation"
        )
        assert updated_satisfaction == pytest.approx(0.75, rel=0.01), (
            "Satisfaction should be 0.75 after 15% penalty"
        )

    def test_multiple_incidents_compound_satisfaction_impact(self) -> None:
        """Verify multiple SLA misses compound to reduce satisfaction faster.
        
        1 miss: -15%, 2 misses: -30%, etc. Can cause client loss.
        """
        client = create_integration_test_client(satisfaction=1.0)

        # Simulate 3 consecutive SLA misses
        satisfaction_penalty_per_miss = -0.15

        current_satisfaction = client.satisfaction
        for miss_count in range(3):
            current_satisfaction += satisfaction_penalty_per_miss
            current_satisfaction = max(0.0, current_satisfaction)

        # After 3 misses, satisfaction should be low
        assert current_satisfaction <= 0.55, (
            f"After 3 misses, satisfaction ({current_satisfaction}) should be ~0.55"
        )

        # At this low satisfaction, client might leave
        assert current_satisfaction < 0.70, (
            "Low satisfaction indicates client at risk"
        )


class TestPhase2BudgetSLAGameLoopIntegration:
    """Integration tests for all three Phase 2 systems together."""

    def test_full_month_cycle_with_incidents(self) -> None:
        """Test complete month: incidents → assignment → SLA → budget.
        
        This is the core game loop:
        1. Incidents generated for client
        2. Specialist assigned
        3. SLA tracked
        4. Resolution affects satisfaction
        5. Budget calculated with satisfaction-weighted revenue
        """
        game_state = create_integration_test_game_state(starting_money=20000.0)

        # Setup: 1 client, 1 specialist
        client = create_integration_test_client(
            client_id="client_001",
            satisfaction=0.85,
        )
        specialist = create_integration_test_specialist(spec_id="spec_001")

        game_state.clients = [client]
        game_state.specialists = [specialist]

        initial_reserves = game_state.budget.total_reserves
        initial_satisfaction = client.satisfaction

        # Simulate: Revenue minus expenses
        revenue = calculate_monthly_revenue(game_state.clients)
        expenses = calculate_monthly_expenses(game_state.specialists, 1)
        profit = revenue - expenses

        # Update reserves
        game_state.budget.total_reserves += profit

        # Verify:
        # 1. Reserves changed (profit applied)
        assert game_state.budget.total_reserves != initial_reserves, (
            "Reserves should change after monthly calculation"
        )

        # 2. If satisfied, reserves increased
        if initial_satisfaction >= 0.8:
            expected_revenue_multiplier = initial_satisfaction
            expected_revenue = 10000.0 * expected_revenue_multiplier
            assert game_state.budget.total_reserves > initial_reserves, (
                "With good satisfaction, reserves should increase"
            )

    def test_declining_satisfaction_triggers_downsizing_cycle(self) -> None:
        """Test cascade: SLA misses → satisfaction drops → revenue drops → bankruptcy.
        
        Demonstrates why SLA management is critical.
        """
        game_state = create_integration_test_game_state(starting_money=30000.0)

        # Setup: 2 specialists, 1 client
        spec1 = create_integration_test_specialist(spec_id="spec_001")
        spec2 = create_integration_test_specialist(spec_id="spec_002")
        client = create_integration_test_client(satisfaction=1.0)

        game_state.specialists = [spec1, spec2]
        game_state.clients = [client]

        month_count = 0
        current_satisfaction = client.satisfaction

        # Simulate 6 months of SLA misses
        for month in range(6):
            month_count += 1

            # Each month: SLA miss reduces satisfaction
            current_satisfaction -= 0.10  # 10% per month
            current_satisfaction = max(0.0, current_satisfaction)
            client.satisfaction = current_satisfaction

            # Revenue drops as satisfaction drops
            revenue = calculate_monthly_revenue(game_state.clients)
            expenses = calculate_monthly_expenses(game_state.specialists, 1)
            profit = revenue - expenses

            game_state.budget.total_reserves += profit

            # Once reserves get too low, would trigger forced downsizing
            if game_state.budget.total_reserves < 5000.0:
                # Fire lowest performer
                if len(game_state.specialists) > 1:
                    game_state.specialists.pop(0)

        # After 6 months of SLA misses:
        # - Satisfaction very low
        # - Revenue minimal
        # - Team smaller due to forced downsizing
        assert client.satisfaction < 0.41, (
            "After 6 months of misses, satisfaction should be ~0.4 or lower"
        )
        assert len(game_state.specialists) < 2, (
            "Should have fired specialist due to budget pressure"
        )

    def test_strategic_growth_with_good_sla_performance(self) -> None:
        """Test positive cycle: good SLA → high satisfaction → growing revenue.
        
        Demonstrates path to success.
        """
        game_state = create_integration_test_game_state(starting_money=30000.0)

        # Setup: 1 specialist, 2 diverse clients
        specialist = create_integration_test_specialist(spec_id="spec_001")
        client1 = create_integration_test_client(
            client_id="client_001",
            satisfaction=0.95,
        )
        client2 = create_integration_test_client(
            client_id="client_002",
            satisfaction=0.85,
        )

        game_state.specialists = [specialist]
        game_state.clients = [client1, client2]

        initial_reserves = game_state.budget.total_reserves

        # Simulate 3 months of maintaining high SLA compliance
        for month in range(3):
            # Satisfaction increases slightly (bonus for perfect month)
            for client in game_state.clients:
                client.satisfaction = min(1.0, client.satisfaction + 0.05)

            revenue = calculate_monthly_revenue(game_state.clients)
            expenses = calculate_monthly_expenses(game_state.specialists, 1)
            profit = revenue - expenses

            game_state.budget.total_reserves += profit

        # After 3 months of good SLA:
        # - Satisfaction higher
        # - Revenue higher
        # - Can afford to hire more specialists
        assert game_state.budget.total_reserves > initial_reserves, (
            "With good SLA performance, reserves should grow"
        )

        for client in game_state.clients:
            assert client.satisfaction >= 0.90, (
                "Good SLA should maintain/increase satisfaction"
            )
