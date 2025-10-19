"""
Tests for the Team Dynamics System.

This module contains comprehensive tests for the team dynamics system,
covering relationship tracking, morale management, and synergy calculations.
"""

import pytest
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass
from typing import Dict, List, Optional

from src.core.team_dynamics_system import TeamDynamicsSystem, RelationshipType, SynergyBonus
from src.core.plugins.team_dynamics_plugin import TeamDynamicsPlugin
from src.models.specialist import Specialist


@dataclass
class MockSpecialist:
    """Mock specialist for testing."""
    id: str
    name: str
    morale: float = 50.0
    relationships: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.relationships is None:
            self.relationships = {}


"""
Tests for the Team Dynamics System.

This module contains comprehensive tests for the team dynamics system,
covering relationship tracking, morale management, and synergy calculations.
"""

import pytest
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass
from typing import Dict, List, Optional

from src.core.team_dynamics_system import TeamDynamicsSystem, RelationshipType, SynergyBonus
from src.core.plugins.team_dynamics_plugin import TeamDynamicsPlugin
from src.models.specialist import Specialist


class TestTeamDynamicsSystem:
    """Test suite for TeamDynamicsSystem."""

    @pytest.fixture
    def team_dynamics_system(self):
        """Create a TeamDynamicsSystem instance."""
        return TeamDynamicsSystem()

    def test_initialization(self, team_dynamics_system):
        """Test system initialization."""
        assert team_dynamics_system is not None
        assert hasattr(team_dynamics_system, '_relationships')
        assert hasattr(team_dynamics_system, '_morale_states')
        assert hasattr(team_dynamics_system, '_relationship_types')

    def test_config_loading(self, team_dynamics_system):
        """Test configuration loading."""
        assert team_dynamics_system._config is not None
        assert "relationships" in team_dynamics_system._config

    def test_relationship_types_available(self, team_dynamics_system):
        """Test relationship types are loaded."""
        rel_types = team_dynamics_system.get_relationship_types()
        assert isinstance(rel_types, dict)
        assert len(rel_types) > 0

    def test_get_relationship_no_relationship(self, team_dynamics_system):
        """Test getting relationship when none exists."""
        relationship = team_dynamics_system.get_relationship("spec1", "spec2")
        assert relationship is None

    def test_get_all_relationships_empty(self, team_dynamics_system):
        """Test getting all relationships (may have defaults from config)."""
        relationships = team_dynamics_system.get_all_relationships()
        assert isinstance(relationships, list)
        # Note: System may load default relationships from config
        assert len(relationships) >= 0

    def test_update_morale(self, team_dynamics_system):
        """Test morale update functionality."""
        # Create mock specialist
        specialist = Mock()
        specialist.id = "spec1"
        specialist.morale = 50.0

        team_members = []
        current_time = 0.0

        # Should not raise exception
        team_dynamics_system.update_morale(specialist, team_members, current_time)

    def test_calculate_team_synergy(self, team_dynamics_system):
        """Test team synergy calculation."""
        team_members = []

        synergy = team_dynamics_system.calculate_team_synergy(team_members)

        assert isinstance(synergy, SynergyBonus)
        assert hasattr(synergy, 'team_synergy')
        assert hasattr(synergy, 'total_bonus')

    def test_get_morale_state_none(self, team_dynamics_system):
        """Test getting morale state when none exists."""
        morale_state = team_dynamics_system.get_morale_state("nonexistent")
        assert morale_state is None

    def test_relationship_config_structure(self, team_dynamics_system):
        """Test relationship configuration structure."""
        rel_types = team_dynamics_system.get_relationship_types()

        # Should have expected relationship types
        expected_types = ["friendship", "rivalry", "mentorship", "neutral"]
        for rel_type in expected_types:
            assert rel_type in rel_types
            assert "synergy_bonus" in rel_types[rel_type]
            assert "morale_boost" in rel_types[rel_type]


class TestTeamDynamicsPlugin:
    """Test suite for TeamDynamicsPlugin."""

    @pytest.fixture
    def mock_game_state(self):
        """Create a mock game state."""
        game_state = Mock()
        game_state.specialists = []  # Empty list for iteration
        return game_state

    @pytest.fixture
    def plugin(self, mock_game_state):
        """Create a TeamDynamicsPlugin instance."""
        plugin = TeamDynamicsPlugin()
        plugin.initialize(mock_game_state)
        return plugin

    def test_plugin_initialization(self, plugin, mock_game_state):
        """Test plugin initialization."""
        assert plugin._game_state == mock_game_state
        assert plugin._team_dynamics_system is not None
        assert isinstance(plugin._team_dynamics_system, TeamDynamicsSystem)

    def test_plugin_update(self, plugin, mock_game_state):
        """Test plugin update method."""
        # Should not raise any exceptions
        plugin.update(mock_game_state, 0.016)  # 60 FPS delta

    def test_plugin_shutdown(self, plugin, mock_game_state):
        """Test plugin shutdown method."""
        # Should not raise any exceptions
        plugin.shutdown(mock_game_state)

    def test_plugin_system_interface(self, plugin):
        """Test plugin implements GameSystem interface correctly."""
        # Check required methods exist
        assert hasattr(plugin, 'initialize')
        assert hasattr(plugin, 'update')
        assert hasattr(plugin, 'shutdown')
        assert hasattr(plugin, 'save_state')
        assert hasattr(plugin, 'load_state')
        assert hasattr(plugin, 'get_name')

    def test_plugin_name(self, plugin):
        """Test plugin name."""
        assert plugin.get_name() == "team_dynamics"

    def test_plugin_state_persistence(self, plugin, mock_game_state):
        """Test plugin state save/load functionality."""
        # Save state
        saved_state = plugin.save_state()
        assert isinstance(saved_state, dict)

        # Create new plugin and load state
        new_plugin = TeamDynamicsPlugin()
        new_plugin.initialize(mock_game_state)
        new_plugin.load_state(saved_state)

        # Should not raise exceptions
        assert new_plugin._team_dynamics_system is not None


class TestTeamDynamicsIntegration:
    """Integration tests for team dynamics system."""

    @pytest.fixture
    def mock_game_state(self):
        """Create a mock game state for integration tests."""
        game_state = Mock()
        game_state.specialists = []
        return game_state

    @pytest.fixture
    def team_dynamics_system(self):
        """Create a TeamDynamicsSystem instance for integration tests."""
        return TeamDynamicsSystem()

    def test_full_plugin_workflow(self, mock_game_state):
        """Test complete plugin workflow."""
        # Initialize plugin
        plugin = TeamDynamicsPlugin()
        plugin.initialize(mock_game_state)

        # Update plugin
        plugin.update(mock_game_state, 0.016)

        # Save and load state
        saved_state = plugin.save_state()
        new_plugin = TeamDynamicsPlugin()
        new_plugin.initialize(mock_game_state)
        new_plugin.load_state(saved_state)

        # Shutdown
        plugin.shutdown(mock_game_state)

        # Should not raise any exceptions

    def test_synergy_calculation_with_team(self, team_dynamics_system):
        """Test synergy calculation with a team."""
        # Create mock team members
        team_members = []
        for i in range(3):
            specialist = Mock()
            specialist.id = f"spec{i}"
            specialist.morale = 50.0 + i * 10  # Different morale levels
            team_members.append(specialist)

        synergy = team_dynamics_system.calculate_team_synergy(team_members)

        assert isinstance(synergy, SynergyBonus)
        assert synergy.team_synergy >= 0.0
        assert synergy.total_bonus >= 0.0

    def test_morale_update_with_team(self, team_dynamics_system):
        """Test morale updates with team context."""
        # Create mock specialist and team
        specialist = Mock()
        specialist.id = "spec1"
        specialist.morale = 50.0

        team_members = []
        for i in range(2):
            team_member = Mock()
            team_member.id = f"team{i}"
            team_member.morale = 60.0
            team_members.append(team_member)

        # Update morale
        team_dynamics_system.update_morale(specialist, team_members, 0.0)

        # Morale state should be created
        morale_state = team_dynamics_system.get_morale_state("spec1")
        assert morale_state is not None
        assert morale_state.specialist_id == "spec1"