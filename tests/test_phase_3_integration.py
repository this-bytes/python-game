"""Phase 3 Integration Tests: Client System lifecycle.

Tests verify complete client lifecycle within the game:
- Clients acquired and managed
- Satisfaction tracked based on SLA performance  
- Contract renewals
- Client termination
- Full integration scenarios
"""

import pytest
from typing import List

from src.models.game_state import GameState
from src.models.client import Client, Industry
from src.core.client_system import (
    generate_client_from_template,
    update_client_satisfaction,
    attempt_contract_renewal,
    handle_contract_termination,
)
from src.core.plugins.client_plugin import ClientPlugin


# ===== FIXTURES =====

@pytest.fixture
def client_plugin() -> ClientPlugin:
    """Create ClientPlugin instance."""
    return ClientPlugin()


@pytest.fixture
def sample_game_state() -> GameState:
    """Create sample game state for testing."""
    game_state = GameState()
    game_state.clients = []
    game_state.specialists = []
    return game_state


# ===== CLIENT ACQUISITION TESTS =====

class TestClientAcquisition:
    """Tests for client acquisition and management."""

    def test_acquire_single_client(
        self,
        client_plugin: ClientPlugin,
        sample_game_state: GameState
    ) -> None:
        """Verify acquiring a single client."""
        client = generate_client_from_template(Industry.TECHNOLOGY, "acq_001")
        
        result = client_plugin.acquire_client(client)
        
        assert result is True
        assert client in client_plugin.clients
        assert len(client_plugin.get_active_clients()) == 1

    def test_acquire_multiple_clients(
        self,
        client_plugin: ClientPlugin,
        sample_game_state: GameState
    ) -> None:
        """Verify acquiring multiple clients."""
        clients = [
            generate_client_from_template(Industry.BANKING, "multi_001"),
            generate_client_from_template(Industry.HEALTHCARE, "multi_002"),
            generate_client_from_template(Industry.TECHNOLOGY, "multi_003"),
        ]
        
        for client in clients:
            result = client_plugin.acquire_client(client)
            assert result is True
        
        assert len(client_plugin.get_active_clients()) == 3

    def test_cannot_acquire_duplicate_client(
        self,
        client_plugin: ClientPlugin
    ) -> None:
        """Verify duplicate client acquisition is prevented."""
        client1 = generate_client_from_template(Industry.TECHNOLOGY, "dup_001")
        client2 = generate_client_from_template(Industry.BANKING, "dup_001")
        
        assert client_plugin.acquire_client(client1) is True
        assert client_plugin.acquire_client(client2) is False
        assert len(client_plugin.clients) == 1

    def test_get_client_by_id(
        self,
        client_plugin: ClientPlugin
    ) -> None:
        """Verify client retrieval by ID."""
        client = generate_client_from_template(Industry.TECHNOLOGY, "retrieve_001")
        client_plugin.acquire_client(client)
        
        retrieved = client_plugin.get_client_by_id("retrieve_001")
        
        assert retrieved is not None
        assert retrieved.company_name == client.company_name

    def test_get_nonexistent_client_returns_none(
        self,
        client_plugin: ClientPlugin
    ) -> None:
        """Verify retrieving nonexistent client returns None."""
        result = client_plugin.get_client_by_id("nonexistent")
        assert result is None


# ===== SATISFACTION LIFECYCLE TESTS =====

class TestSatisfactionLifecycle:
    """Tests for client satisfaction changes over time."""

    def test_excellent_performance_maintains_satisfaction(
        self,
        client_plugin: ClientPlugin
    ) -> None:
        """Verify excellent performance maintains high satisfaction."""
        client = generate_client_from_template(Industry.TECHNOLOGY, "perf_001")
        client_plugin.acquire_client(client)
        
        initial_satisfaction = client.satisfaction
        
        # Update with perfect performance (5 met, 0 missed)
        update_client_satisfaction(client, sla_met=5, sla_missed=0)
        
        # Satisfaction should maintain or increase
        assert client.satisfaction >= initial_satisfaction * 0.95

    def test_poor_performance_decreases_satisfaction(
        self,
        client_plugin: ClientPlugin
    ) -> None:
        """Verify poor performance decreases satisfaction."""
        client = generate_client_from_template(Industry.HEALTHCARE, "perf_002")
        client_plugin.acquire_client(client)
        
        initial_satisfaction = client.satisfaction
        
        # Update with poor performance (1 met, 4 missed)
        update_client_satisfaction(client, sla_met=1, sla_missed=4)
        
        # Satisfaction should decrease
        assert client.satisfaction < initial_satisfaction

    def test_cumulative_poor_performance_leads_to_critical(
        self,
        client_plugin: ClientPlugin
    ) -> None:
        """Verify cumulative poor performance leads to critical satisfaction."""
        client = generate_client_from_template(Industry.RETAIL, "cumul_001")
        client_plugin.acquire_client(client)
        
        # Simulate 3 months of poor performance
        for _ in range(3):
            update_client_satisfaction(client, sla_met=1, sla_missed=3)
        
        # Satisfaction should be very low
        assert client.satisfaction < 0.4
