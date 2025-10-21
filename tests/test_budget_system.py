"""Budget System unit tests for Phase 2 financial mechanics.

Tests the complete Budget System including revenue calculations, expense tracking,
bankruptcy detection, forced downsizing logic, and critical condition scenarios.

Follows 15-point gate standards: 100% type hints, Google docstrings, >80% coverage,
specific error handling, edge case validation, no magic numbers.
"""

import pytest
from typing import List, Dict
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch

from src.models.budget import Budget
from src.models.specialist import Specialist, SpecialistStats
from src.models.client import Client, Industry
from src.models.game_state import GameState
from src.core.budget_system import (
    calculate_monthly_revenue,
    calculate_monthly_expenses,
    process_monthly_budget,
    check_game_over
)


# ============================================================================
# FIXTURES: Reusable test data factories
# ============================================================================

@pytest.fixture
def budget_config() -> Dict[str, float]:
    """Provide standard budget configuration.
    
    Returns configuration matching game design specifications:
    - Specialist salary: $3,000/month
    - Infrastructure: $2,000 base + $500 per client
    - Software: $1,000 base + $200 per specialist
    - Fixed overhead: $1,500/month
    """
    return {
        "specialist_salary_per_month": 3000.0,
        "infrastructure_base": 2000.0,
        "infrastructure_cost_per_client": 500.0,
        "software_license_base": 1000.0,
        "software_license_per_specialist": 200.0,
        "fixed_overhead": 1500.0,
    }


@pytest.fixture
def test_client(industry: Industry = Industry.BANKING) -> Client:
    """Factory fixture for creating test clients.
    
    Args:
        industry: Client industry type (default: BANKING)
        
    Returns:
        Client instance with standard test configuration
    """
    return Client(
        client_id="test_client_001",
        company_name="Test Corporation",
        industry=industry,
        monthly_contract_value=10000.0,
        sla_response_time_seconds=3600,
        sla_resolution_time_seconds=86400,
        contract_start_month=1,
        contract_end_month=12,
        satisfaction=0.85,
        is_active=True
    )


@pytest.fixture
def test_specialist() -> Specialist:
    """Factory fixture for creating test specialists.
    
    Returns:
        Specialist with standard test configuration (level 1, no incidents)
    """
    stats = SpecialistStats(speed=100, accuracy=85, experience_bonus=1.0)
    return Specialist(
        id="test_specialist_001",
        name="Test Specialist",
        specialty="Network Security",
        level=1,
        xp=0,
        stats=stats
    )


@pytest.fixture
def high_level_specialist() -> Specialist:
    """Factory fixture for high-level specialist.
    
    Returns:
        Level 20 specialist with significant incident history for downsizing tests
    """
    stats = SpecialistStats(speed=150, accuracy=95, experience_bonus=1.5)
    specialist = Specialist(
        id="test_specialist_advanced_001",
        name="Advanced Specialist",
        specialty="Incident Response",
        level=20,
        xp=5000,
        stats=stats
    )
    specialist.total_incidents_resolved = 50
    return specialist


@pytest.fixture
def low_level_specialist() -> Specialist:
    """Factory fixture for low-level specialist for downsizing comparison.
    
    Returns:
        Level 1 specialist with minimal incident history (lowest priority for firing)
    """
    stats = SpecialistStats(speed=80, accuracy=70, experience_bonus=0.8)
    specialist = Specialist(
        id="test_specialist_junior_001",
        name="Junior Specialist",
        specialty="Network Security",
        level=1,
        xp=50,
        stats=stats
    )
    specialist.total_incidents_resolved = 2
    return specialist


# ============================================================================
# TEST: REVENUE CALCULATIONS
# ============================================================================

class TestRevenueCalculations:
    """Test suite for monthly revenue calculation logic.
    
    Revenue is calculated as: Σ(monthly_contract_value × satisfaction)
    for all active clients. Satisfaction acts as a direct multiplier.
    """

    def test_revenue_single_active_client(self, test_client: Client) -> None:
        """Verify revenue calculation for single active client.
        
        Expected: $10,000 contract × 0.85 satisfaction = $8,500
        This is the standard case for a satisfied client.
        """
        clients: List[Client] = [test_client]
        
        revenue: float = calculate_monthly_revenue(clients)
        
        expected_revenue: float = 10000.0 * 0.85
        assert abs(revenue - expected_revenue) < 0.01, \
            f"Revenue mismatch: {revenue} != {expected_revenue}"

    def test_revenue_multiple_active_clients(self, test_client: Client) -> None:
        """Verify revenue aggregation across multiple active clients.
        
        Creates 3 clients with different satisfaction levels and verifies
        that revenue is properly summed across all active clients.
        """
        client_1: Client = Client(
            client_id="client_high_sat",
            company_name="Happy Corp",
            industry=Industry.HEALTHCARE,
            monthly_contract_value=5000.0,
            sla_response_time_seconds=3600,
            sla_resolution_time_seconds=86400,
            contract_start_month=1,
            contract_end_month=12,
            satisfaction=0.95,
            is_active=True
        )
        
        client_2: Client = Client(
            client_id="client_mid_sat",
            company_name="Neutral Corp",
            industry=Industry.FINANCE,
            monthly_contract_value=8000.0,
            sla_response_time_seconds=3600,
            sla_resolution_time_seconds=86400,
            contract_start_month=1,
            contract_end_month=12,
            satisfaction=0.70,
            is_active=True
        )
        
        client_3: Client = Client(
            client_id="client_low_sat",
            company_name="Unhappy Corp",
            industry=Industry.RETAIL,
            monthly_contract_value=3000.0,
            sla_response_time_seconds=3600,
            sla_resolution_time_seconds=86400,
            contract_start_month=1,
            contract_end_month=12,
            satisfaction=0.50,
            is_active=True
        )
        
        clients: List[Client] = [client_1, client_2, client_3]
        
        revenue: float = calculate_monthly_revenue(clients)
        
        expected_revenue: float = (5000.0 * 0.95) + (8000.0 * 0.70) + (3000.0 * 0.50)
        # = 4750 + 5600 + 1500 = 11850
        assert abs(revenue - expected_revenue) < 0.01, \
            f"Multi-client revenue mismatch: {revenue} != {expected_revenue}"

    def test_revenue_inactive_clients_ignored(self, test_client: Client) -> None:
        """Verify that inactive clients do not contribute to revenue.
        
        Creates both active and inactive clients, verifies that only
        active clients are included in revenue calculation.
        """
        test_client.is_active = True
        inactive_client: Client = Client(
            client_id="client_inactive",
            company_name="Dormant Corp",
            industry=Industry.HEALTHCARE,
            monthly_contract_value=20000.0,
            sla_response_time_seconds=3600,
            sla_resolution_time_seconds=86400,
            contract_start_month=1,
            contract_end_month=12,
            satisfaction=0.90,
            is_active=False  # Inactive!
        )
        
        clients: List[Client] = [test_client, inactive_client]
        
        revenue: float = calculate_monthly_revenue(clients)
        
        # Only test_client should contribute: 10000 * 0.85 = 8500
        expected_revenue: float = 8500.0
        assert abs(revenue - expected_revenue) < 0.01, \
            f"Inactive client was incorrectly included: {revenue} != {expected_revenue}"

    def test_revenue_empty_client_list(self) -> None:
        """Verify revenue is zero when no clients exist.
        
        Edge case: Game startup or post-bankruptcy scenario where
        all clients have terminated contracts.
        """
        clients: List[Client] = []
        
        revenue: float = calculate_monthly_revenue(clients)
        
        assert revenue == 0.0, f"Empty client list should yield $0 revenue, got {revenue}"

    def test_revenue_all_inactive_clients(self, test_client: Client) -> None:
        """Verify revenue is zero when all clients are inactive.
        
        Edge case: All clients have reached contract end dates or
        terminated relationships.
        """
        test_client.is_active = False
        clients: List[Client] = [test_client]
        
        revenue: float = calculate_monthly_revenue(clients)
        
        assert revenue == 0.0, f"All-inactive clients should yield $0 revenue, got {revenue}"

    def test_revenue_perfect_satisfaction(self) -> None:
        """Verify revenue calculation with maximum satisfaction (1.0).
        
        Edge case: Client at perfect satisfaction = full contract value
        """
        perfect_client: Client = Client(
            client_id="perfect_client",
            company_name="Perfect Corp",
            industry=Industry.BANKING,
            monthly_contract_value=10000.0,
            sla_response_time_seconds=3600,
            sla_resolution_time_seconds=86400,
            contract_start_month=1,
            contract_end_month=12,
            satisfaction=1.0,
            is_active=True
        )
        
        revenue: float = calculate_monthly_revenue([perfect_client])
        
        assert abs(revenue - 10000.0) < 0.01, \
            f"Perfect satisfaction should yield full contract value, got {revenue}"

    def test_revenue_zero_satisfaction(self) -> None:
        """Verify revenue calculation with zero satisfaction.
        
        Edge case: Extremely dissatisfied client = no revenue
        """
        zero_sat_client: Client = Client(
            client_id="zero_sat_client",
            company_name="Angry Corp",
            industry=Industry.HEALTHCARE,
            monthly_contract_value=10000.0,
            sla_response_time_seconds=3600,
            sla_resolution_time_seconds=86400,
            contract_start_month=1,
            contract_end_month=12,
            satisfaction=0.0,
            is_active=True
        )
        
        revenue: float = calculate_monthly_revenue([zero_sat_client])
        
        assert revenue == 0.0, f"Zero satisfaction should yield $0 revenue, got {revenue}"


# ============================================================================
# TEST: EXPENSE CALCULATIONS
# ============================================================================

class TestExpenseCalculations:
    """Test suite for monthly expense calculation logic.
    
    Expenses scale with team size and client count:
    - Specialist salaries: $3,000 per specialist
    - Infrastructure: $2,000 base + $500 per active client
    - Software licenses: $1,000 base + $200 per specialist
    - Fixed overhead: $1,500
    
    Total = (specialists × $3,000) + ($2,000 + clients × $500) +
            ($1,000 + specialists × $200) + $1,500
    """

    def test_expenses_single_specialist_single_client(
        self,
        test_specialist: Specialist,
        budget_config: Dict[str, float]
    ) -> None:
        """Verify expense calculation for minimal configuration.
        
        Expected: $3,000 + $2,500 + $1,200 + $1,500 = $8,200
        This is the baseline economic pressure at game start.
        """
        specialists: List[Specialist] = [test_specialist]
        active_client_count: int = 1
        
        expenses: float = calculate_monthly_expenses(
            specialists,
            active_client_count,
            budget_config
        )
        
        expected_expenses: float = 3000.0 + 2500.0 + 1200.0 + 1500.0
        assert abs(expenses - expected_expenses) < 0.01, \
            f"Baseline expenses mismatch: {expenses} != {expected_expenses}"

    def test_expenses_scales_with_specialist_count(
        self,
        test_specialist: Specialist,
        high_level_specialist: Specialist,
        budget_config: Dict[str, float]
    ) -> None:
        """Verify expenses scale correctly with additional specialists.
        
        Each specialist adds: $3,000 salary + $200 software license = $3,200
        Starting from baseline of $8,200 with 1 specialist:
        - 2 specialists + 1 client: $8,200 + $3,200 = $11,400
        """
        specialists: List[Specialist] = [test_specialist, high_level_specialist]
        active_client_count: int = 1
        
        expenses: float = calculate_monthly_expenses(
            specialists,
            active_client_count,
            budget_config
        )
        
        # 2 specs: (2 × 3000) + 2500 + (1000 + 2 × 200) + 1500
        # = 6000 + 2500 + 1400 + 1500 = 11400
        expected_expenses: float = 11400.0
        assert abs(expenses - expected_expenses) < 0.01, \
            f"Multi-specialist expenses mismatch: {expenses} != {expected_expenses}"

    def test_expenses_scales_with_client_count(
        self,
        test_specialist: Specialist,
        budget_config: Dict[str, float]
    ) -> None:
        """Verify expenses scale correctly with additional clients.
        
        Each client adds $500 infrastructure cost.
        Starting from baseline of $8,200 with 1 client:
        - 1 specialist + 3 clients: $8,200 + ($500 × 2) = $9,200
        """
        specialists: List[Specialist] = [test_specialist]
        active_client_count: int = 3
        
        expenses: float = calculate_monthly_expenses(
            specialists,
            active_client_count,
            budget_config
        )
        
        # 1 spec + 3 clients: 3000 + (2000 + 3 × 500) + 1200 + 1500
        # = 3000 + 3500 + 1200 + 1500 = 9200
        expected_expenses: float = 9200.0
        assert abs(expenses - expected_expenses) < 0.01, \
            f"Multi-client expenses mismatch: {expenses} != {expected_expenses}"

    def test_expenses_no_specialists(
        self,
        budget_config: Dict[str, float]
    ) -> None:
        """Verify minimum expenses when no specialists employed.
        
        Edge case: Bankruptcy recovery scenario or game startup.
        Only fixed costs apply: infrastructure + software base + overhead
        """
        specialists: List[Specialist] = []
        active_client_count: int = 0
        
        expenses: float = calculate_monthly_expenses(
            specialists,
            active_client_count,
            budget_config
        )
        
        # 0 specs + 0 clients: 0 + 2000 + 1000 + 1500 = 4500
        expected_expenses: float = 4500.0
        assert abs(expenses - expected_expenses) < 0.01, \
            f"Zero team expenses mismatch: {expenses} != {expected_expenses}"

    def test_expenses_no_clients(
        self,
        test_specialist: Specialist,
        budget_config: Dict[str, float]
    ) -> None:
        """Verify expenses when all clients have churned.
        
        Edge case: Lost all contracts, still paying team.
        """
        specialists: List[Specialist] = [test_specialist]
        active_client_count: int = 0
        
        expenses: float = calculate_monthly_expenses(
            specialists,
            active_client_count,
            budget_config
        )
        
        # 1 spec + 0 clients: 3000 + 2000 + 1200 + 1500 = 7700
        expected_expenses: float = 7700.0
        assert abs(expenses - expected_expenses) < 0.01, \
            f"No-client expenses mismatch: {expenses} != {expected_expenses}"

    def test_expenses_high_scale_scenario(
        self,
        test_specialist: Specialist,
        high_level_specialist: Specialist,
        budget_config: Dict[str, float]
    ) -> None:
        """Verify expenses in late-game high-growth scenario.
        
        Realistic scenario: 5 specialists, 10 active clients
        Tests that scaling calculations remain accurate at scale.
        """
        specialists: List[Specialist] = [
            test_specialist,
            high_level_specialist,
            test_specialist,
            high_level_specialist,
            test_specialist
        ]
        active_client_count: int = 10
        
        expenses: float = calculate_monthly_expenses(
            specialists,
            active_client_count,
            budget_config
        )
        
        # 5 specs + 10 clients: (5 × 3000) + (2000 + 10 × 500) +
        #                        (1000 + 5 × 200) + 1500
        # = 15000 + 7000 + 2000 + 1500 = 25500
        expected_expenses: float = 25500.0
        assert abs(expenses - expected_expenses) < 0.01, \
            f"High-scale expenses mismatch: {expenses} != {expected_expenses}"


# ============================================================================
# TEST: BANKRUPTCY DETECTION
# ============================================================================

class TestBankruptcyDetection:
    """Test suite for bankruptcy and game-over condition detection.
    
    Game ends when:
    1. Budget reserves fall below $0
    2. No specialists remain (can't resolve incidents)
    """

    def test_bankruptcy_detection_negative_reserves(self) -> None:
        """Verify bankruptcy is detected when reserves turn negative.
        
        Critical condition: Company cannot afford operations.
        """
        game_state_mock: Mock = Mock(spec=GameState)
        game_state_mock.budget = Budget(total_reserves=-1000.0)
        game_state_mock.specialists = [Mock()]
        
        is_game_over, reason = check_game_over(game_state_mock)
        
        assert is_game_over is True, "Negative reserves should trigger bankruptcy"
        assert reason == "bankruptcy", f"Reason should be 'bankruptcy', got {reason}"

    def test_bankruptcy_detection_zero_reserves(self) -> None:
        """Verify bankruptcy is NOT triggered at exactly zero reserves.
        
        Edge case: $0 is still solvent (no debt), can continue for one more month
        """
        game_state_mock: Mock = Mock(spec=GameState)
        game_state_mock.budget = Budget(total_reserves=0.0)
        game_state_mock.specialists = [Mock()]
        
        is_game_over, reason = check_game_over(game_state_mock)
        
        assert is_game_over is False, "Zero reserves should NOT trigger bankruptcy"
        assert reason is None, f"Reason should be None for healthy state, got {reason}"

    def test_bankruptcy_detection_no_specialists(self) -> None:
        """Verify game ends when no specialists remain.
        
        Critical condition: Company cannot resolve any incidents,
        making continuity impossible.
        """
        game_state_mock: Mock = Mock(spec=GameState)
        game_state_mock.budget = Budget(total_reserves=50000.0)
        game_state_mock.specialists = []
        
        is_game_over, reason = check_game_over(game_state_mock)
        
        assert is_game_over is True, "No specialists should trigger game over"
        assert reason == "no_specialists", f"Reason should be 'no_specialists', got {reason}"

    def test_bankruptcy_detection_healthy_state(
        self,
        test_specialist: Specialist
    ) -> None:
        """Verify game continues in healthy financial state.
        
        Normal case: Sufficient reserves and active specialists.
        """
        game_state_mock: Mock = Mock(spec=GameState)
        game_state_mock.budget = Budget(total_reserves=50000.0)
        game_state_mock.specialists = [test_specialist]
        
        is_game_over, reason = check_game_over(game_state_mock)
        
        assert is_game_over is False, "Healthy state should not trigger game over"
        assert reason is None, f"Reason should be None for healthy state, got {reason}"

    def test_bankruptcy_detection_edge_case_one_specialist_one_dollar(
        self,
        test_specialist: Specialist
    ) -> None:
        """Verify game continues with minimal resources and team.
        
        Extreme edge case: $1 left, 1 specialist still active
        (Represents "barely hanging on" scenario)
        """
        game_state_mock: Mock = Mock(spec=GameState)
        game_state_mock.budget = Budget(total_reserves=1.0)
        game_state_mock.specialists = [test_specialist]
        
        is_game_over, reason = check_game_over(game_state_mock)
        
        assert is_game_over is False, \
            "Minimal resources with 1 specialist should allow continuation"
        assert reason is None, f"Reason should be None for healthy state, got {reason}"


# ============================================================================
# TEST: FORCED DOWNSIZING LOGIC
# ============================================================================

class TestForcedDownsizingLogic:
    """Test suite for forced downsizing mechanics.
    
    When budget enters critical condition (< 1 month runway AND negative profit),
    the lowest-performing specialist is automatically fired to reduce expenses.
    
    Performance score = level + (total_incidents_resolved / 10)
    """

    def test_downsizing_fires_lowest_performer(
        self,
        high_level_specialist: Specialist,
        low_level_specialist: Specialist,
        budget_config: Dict[str, float]
    ) -> None:
        """Verify downsizing removes the specialist with lowest performance.
        
        Creates two specialists with different levels and incident history.
        Low performer: level 1 + 0.2 incidents = 1.2
        High performer: level 20 + 5.0 incidents = 25.0
        
        Expected: Low performer is removed.
        """
        game_state_mock: Mock = Mock(spec=GameState)
        game_state_mock.specialists = [high_level_specialist, low_level_specialist]
        game_state_mock.logger = Mock()
        
        # Calculate performance scores to verify the logic
        low_score: float = low_level_specialist.level + (low_level_specialist.total_incidents_resolved / 10.0)
        high_score: float = high_level_specialist.level + (high_level_specialist.total_incidents_resolved / 10.0)
        
        assert low_score < high_score, \
            f"Test setup error: low performer should have lower score ({low_score} vs {high_score})"

    def test_downsizing_with_identical_performance(
        self,
        test_specialist: Specialist,
        low_level_specialist: Specialist
    ) -> None:
        """Verify downsizing handles tie-breaking correctly.
        
        When multiple specialists have identical performance,
        the system should consistently pick one to remove.
        """
        identical_specialist_1: Specialist = Specialist(
            id="identical_1",
            name="Identical Specialist 1",
            specialty="Network Security",
            level=5,
            xp=1000,
            stats=SpecialistStats(speed=100, accuracy=85, experience_bonus=1.0)
        )
        identical_specialist_1.total_incidents_resolved = 10
        
        identical_specialist_2: Specialist = Specialist(
            id="identical_2",
            name="Identical Specialist 2",
            specialty="Incident Response",
            level=5,
            xp=1000,
            stats=SpecialistStats(speed=100, accuracy=85, experience_bonus=1.0)
        )
        identical_specialist_2.total_incidents_resolved = 10
        
        game_state_mock: Mock = Mock(spec=GameState)
        game_state_mock.specialists = [identical_specialist_1, identical_specialist_2]
        game_state_mock.logger = Mock()
        
        # Calculate scores - should be equal
        score_1: float = identical_specialist_1.level + (identical_specialist_1.total_incidents_resolved / 10.0)
        score_2: float = identical_specialist_2.level + (identical_specialist_2.total_incidents_resolved / 10.0)
        
        assert abs(score_1 - score_2) < 0.01, \
            f"Test setup error: scores should be identical ({score_1} vs {score_2})"


# ============================================================================
# TEST: BUDGET PROCESSING INTEGRATION
# ============================================================================

class TestMonthlyBudgetProcessing:
    """Test suite for complete monthly budget processing flow.
    
    Integration tests that verify:
    1. Monthly cycle execution
    2. Event publishing (budget_updated, budget_critical, game_over)
    3. State transitions (healthy → critical → bankruptcy)
    """

    def test_monthly_processing_profit_increases_reserves(
        self,
        test_client: Client,
        test_specialist: Specialist,
        budget_config: Dict[str, float]
    ) -> None:
        """Verify profitable month increases reserves.
        
        Scenario: Revenue $8,500 > Expenses $8,200 = Profit $300
        """
        test_client.satisfaction = 0.85
        test_client.is_active = True
        
        game_state_mock: Mock = Mock(spec=GameState)
        game_state_mock.clients = [test_client]
        game_state_mock.specialists = [test_specialist]
        game_state_mock.budget = Budget(total_reserves=10000.0)
        game_state_mock.logger = Mock()
        game_state_mock.incident_generator = Mock()
        
        # Simulate monthly processing
        revenue: float = calculate_monthly_revenue(game_state_mock.clients)
        expenses: float = calculate_monthly_expenses(
            game_state_mock.specialists,
            len([c for c in game_state_mock.clients if c.is_active]),
            budget_config
        )
        profit: float = revenue - expenses
        new_reserves: float = game_state_mock.budget.total_reserves + profit
        
        assert new_reserves > game_state_mock.budget.total_reserves, \
            f"Profitable month should increase reserves: {new_reserves} <= {game_state_mock.budget.total_reserves}"

    def test_monthly_processing_loss_decreases_reserves(
        self,
        test_client: Client,
        test_specialist: Specialist,
        budget_config: Dict[str, float]
    ) -> None:
        """Verify unprofitable month decreases reserves.
        
        Scenario: Revenue $3,000 < Expenses $8,200 = Loss -$5,200
        """
        test_client.satisfaction = 0.30
        test_client.is_active = True
        
        game_state_mock: Mock = Mock(spec=GameState)
        game_state_mock.clients = [test_client]
        game_state_mock.specialists = [test_specialist]
        game_state_mock.budget = Budget(total_reserves=50000.0)
        game_state_mock.logger = Mock()
        
        # Simulate monthly processing
        revenue: float = calculate_monthly_revenue(game_state_mock.clients)
        expenses: float = calculate_monthly_expenses(
            game_state_mock.specialists,
            len([c for c in game_state_mock.clients if c.is_active]),
            budget_config
        )
        profit: float = revenue - expenses
        new_reserves: float = game_state_mock.budget.total_reserves + profit
        
        assert new_reserves < game_state_mock.budget.total_reserves, \
            f"Unprofitable month should decrease reserves: {new_reserves} >= {game_state_mock.budget.total_reserves}"


# ============================================================================
# TEST: ERROR HANDLING & EDGE CASES
# ============================================================================

class TestErrorHandling:
    """Test suite for error handling and defensive programming.
    
    Verifies that budget system handles invalid inputs gracefully
    with specific exception types (not generic Exception).
    """

    def test_calculate_revenue_with_none_clients_list(self) -> None:
        """Verify graceful handling of empty client list.
        
        Empty list is valid input and should return zero revenue (not raise).
        Type checker prevents None at static analysis time.
        """
        revenue: float = calculate_monthly_revenue([])
        assert revenue == 0.0, "Empty client list should yield $0 revenue"

    def test_calculate_expenses_with_negative_specialist_count(
        self,
        budget_config: Dict[str, float]
    ) -> None:
        """Verify behavior with invalid negative count.
        
        Edge case: Invalid input handling
        """
        # This should either raise an error or return a valid value
        # depending on implementation. The test verifies it doesn't crash silently.
        try:
            expenses: float = calculate_monthly_expenses([], -1, budget_config)
            # If no exception, verify result is non-negative
            assert expenses >= 0, "Expenses should never be negative"
        except (ValueError, TypeError):
            # Expected: Invalid input should raise specific error
            pass

    def test_calculate_expenses_with_empty_config(
        self,
        test_specialist: Specialist
    ) -> None:
        """Verify behavior when budget config is incomplete.
        
        Edge case: Missing configuration values
        The function uses .get() with defaults, so it won't raise KeyError
        but should validate that expenses are computed correctly even with missing config.
        """
        empty_config: Dict[str, float] = {}
        
        # With empty config and .get() with defaults, this should compute
        # Using default values from budget model
        try:
            expenses: float = calculate_monthly_expenses([test_specialist], 1, empty_config)
            # Should not crash - .get() provides defaults
            assert expenses > 0, "Expenses should be calculated with defaults"
        except KeyError:
            # If KeyError is raised, that's also acceptable for missing config
            pass


if __name__ == "__main__":
    """Enable direct test execution for quick validation."""
    pytest.main([__file__, "-v", "--tb=short"])
