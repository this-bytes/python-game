"""Tests for Facility model and FacilitySystem."""

import pytest
from src.models.facility import Facility
from src.core.facility_system import FacilitySystem
from src.models.game_state import GameState


@pytest.fixture
def sample_facility():
    """Create a sample facility for testing."""
    return Facility(
        id="office_space",
        name="Office Space",
        description="Expand office to hire more specialists",
        facility_type="office_space",
        level=1,
        max_level=10,
        upgrade_cost=5000,
        bonuses={"max_specialists": 2},
    )


@pytest.fixture
def facility_system():
    """Create a FacilitySystem instance."""
    return FacilitySystem()


@pytest.fixture
def sample_facilities():
    """Create a list of sample facilities."""
    return [
        Facility(
            id="office_space",
            name="Office Space",
            description="Expand office",
            facility_type="office_space",
            level=3,
            max_level=10,
            upgrade_cost=5000,
            bonuses={"max_specialists": 2},
        ),
        Facility(
            id="server_room",
            name="Server Room",
            description="Server infrastructure",
            facility_type="server_room",
            level=2,
            max_level=10,
            upgrade_cost=8000,
            bonuses={"max_active_incidents": 10, "incident_resolution_speed": 0.05},
        ),
        Facility(
            id="training_center",
            name="Training Center",
            description="Training facilities",
            facility_type="training_center",
            level=5,
            max_level=10,
            upgrade_cost=10000,
            bonuses={"xp_multiplier": 0.1},
        ),
    ]


class TestFacility:
    """Test suite for Facility model."""

    def test_initialization(self, sample_facility):
        """Test facility initialization."""
        assert sample_facility.id == "office_space"
        assert sample_facility.name == "Office Space"
        assert sample_facility.level == 1
        assert sample_facility.max_level == 10
        assert sample_facility.upgrade_cost == 5000

    def test_can_upgrade(self, sample_facility):
        """Test upgrade availability check."""
        assert sample_facility.can_upgrade() is True

        # At max level
        sample_facility.level = 10
        assert sample_facility.can_upgrade() is False

    def test_calculate_upgrade_cost(self, sample_facility):
        """Test upgrade cost calculation."""
        # Level 1 → 2: 5000 * 1.5^1 = 7500
        assert sample_facility.calculate_upgrade_cost() == 7500

        sample_facility.level = 2
        # Level 2 → 3: 5000 * 1.5^2 = 11250
        assert sample_facility.calculate_upgrade_cost() == 11250

        sample_facility.level = 10
        # At max level
        assert sample_facility.calculate_upgrade_cost() == 0

    def test_upgrade(self, sample_facility):
        """Test facility upgrade."""
        old_level = sample_facility.level
        success = sample_facility.upgrade()

        assert success is True
        assert sample_facility.level == old_level + 1

    def test_upgrade_at_max_level(self, sample_facility):
        """Test upgrade fails at max level."""
        sample_facility.level = 10
        success = sample_facility.upgrade()

        assert success is False
        assert sample_facility.level == 10

    def test_calculate_total_bonuses(self, sample_facility):
        """Test total bonus calculation."""
        sample_facility.level = 3
        bonuses = sample_facility.calculate_total_bonuses()

        assert bonuses["max_specialists"] == 6  # 2 * 3

    def test_get_bonus_value(self, sample_facility):
        """Test getting specific bonus value."""
        sample_facility.level = 4
        bonus = sample_facility.get_bonus_value("max_specialists")

        assert bonus == 8  # 2 * 4

        # Non-existent bonus
        bonus = sample_facility.get_bonus_value("nonexistent")
        assert bonus == 0

    def test_get_upgrade_preview(self, sample_facility):
        """Test upgrade preview."""
        sample_facility.level = 2
        preview = sample_facility.get_upgrade_preview()

        assert preview["can_upgrade"] is True
        assert preview["current_level"] == 2
        assert preview["next_level"] == 3
        assert preview["upgrade_cost"] == 11250
        assert preview["current_bonuses"]["max_specialists"] == 4
        assert preview["next_bonuses"]["max_specialists"] == 6

    def test_get_upgrade_preview_at_max(self, sample_facility):
        """Test upgrade preview at max level."""
        sample_facility.level = 10
        preview = sample_facility.get_upgrade_preview()

        assert preview["can_upgrade"] is False
        assert "message" in preview

    def test_to_dict(self, sample_facility):
        """Test facility serialization."""
        data = sample_facility.to_dict()

        assert data["id"] == "office_space"
        assert data["level"] == 1
        assert data["max_level"] == 10
        assert "bonuses" in data

    def test_from_dict(self):
        """Test facility deserialization."""
        data = {
            "id": "test_facility",
            "name": "Test Facility",
            "description": "Test description",
            "facility_type": "test_type",
            "level": 5,
            "max_level": 10,
            "upgrade_cost": 1000,
            "bonuses": {"test_bonus": 1.5},
        }

        facility = Facility.from_dict(data)

        assert facility.id == "test_facility"
        assert facility.level == 5
        assert facility.bonuses["test_bonus"] == 1.5


class TestFacilitySystem:
    """Test suite for FacilitySystem."""

    def test_upgrade_facility_success(self, facility_system, sample_facility):
        """Test successful facility upgrade."""
        game_state = GameState(
            specialists=[],
            incidents=[],
            clients=[],
            automation_scripts=[],
            current_money=10000,
        )

        old_level = sample_facility.level
        old_money = game_state.current_money

        success = facility_system.upgrade_facility(sample_facility, game_state)

        assert success is True
        assert sample_facility.level == old_level + 1
        assert game_state.current_money < old_money

    def test_upgrade_facility_insufficient_funds(
        self, facility_system, sample_facility
    ):
        """Test upgrade fails with insufficient funds."""
        game_state = GameState(
            specialists=[],
            incidents=[],
            clients=[],
            automation_scripts=[],
            current_money=1000,
        )

        old_level = sample_facility.level

        success = facility_system.upgrade_facility(sample_facility, game_state)

        assert success is False
        assert sample_facility.level == old_level

    def test_upgrade_facility_at_max_level(
        self, facility_system, sample_facility
    ):
        """Test upgrade fails at max level."""
        game_state = GameState(
            specialists=[],
            incidents=[],
            clients=[],
            automation_scripts=[],
            current_money=100000,
        )

        sample_facility.level = 10

        success = facility_system.upgrade_facility(sample_facility, game_state)

        assert success is False

    def test_calculate_facility_bonuses(
        self, facility_system, sample_facilities
    ):
        """Test aggregate bonus calculation."""
        bonuses = facility_system.calculate_facility_bonuses(sample_facilities)

        # Office: 2 * 3 = 6
        assert bonuses["max_specialists"] == 6

        # Server room: 10 * 2 = 20
        assert bonuses["max_active_incidents"] == 20

        # Server room: 0.05 * 2 = 0.10
        assert abs(bonuses["incident_resolution_speed"] - 0.10) < 0.01

        # Training: 0.1 * 5 = 0.5
        assert abs(bonuses["xp_multiplier"] - 0.5) < 0.01

    def test_apply_facility_effects(self, facility_system, sample_facilities):
        """Test facility effects application."""
        game_state = GameState(
            specialists=[],
            incidents=[],
            clients=[],
            automation_scripts=[],
        )
        game_state.facilities = sample_facilities

        effects = facility_system.apply_facility_effects(game_state)

        # Base 10 + 6 from office
        assert effects["max_specialists"] == 16

        # Base 50 + 20 from server room (note: GameState.max_active_incidents defaults to 50)
        # The effects dict should have total 70
        assert effects["max_active_incidents"] == 70

        # Base 1.0 + 0.5 from training center
        assert abs(effects["xp_multiplier"] - 1.5) < 0.01

    def test_apply_facility_effects_no_facilities(self, facility_system):
        """Test effects with no facilities."""
        game_state = GameState(
            specialists=[],
            incidents=[],
            clients=[],
            automation_scripts=[],
        )
        # Clear facilities that might be loaded
        game_state.facilities = []

        effects = facility_system.apply_facility_effects(game_state)

        # Should return base values
        assert effects["max_specialists"] == 10
        assert effects["max_active_incidents"] == 50
        assert effects["xp_multiplier"] == 1.0

    def test_get_facility_by_id(self, facility_system, sample_facilities):
        """Test getting facility by ID."""
        facility = facility_system.get_facility_by_id(
            sample_facilities, "server_room"
        )

        assert facility is not None
        assert facility.id == "server_room"

        # Non-existent ID
        facility = facility_system.get_facility_by_id(
            sample_facilities, "nonexistent"
        )
        assert facility is None

    def test_get_upgradeable_facilities(
        self, facility_system, sample_facilities
    ):
        """Test getting upgradeable facilities."""
        upgradeable = facility_system.get_upgradeable_facilities(
            sample_facilities
        )

        # All should be upgradeable (none at max level)
        assert len(upgradeable) == 3

        # Set one to max level
        sample_facilities[0].level = 10
        upgradeable = facility_system.get_upgradeable_facilities(
            sample_facilities
        )

        assert len(upgradeable) == 2

    def test_get_total_upgrade_cost(self, facility_system, sample_facilities):
        """Test total upgrade cost calculation."""
        total_cost = facility_system.get_total_upgrade_cost(sample_facilities)

        # Calculate manually
        expected = 0
        for facility in sample_facilities:
            expected += facility.calculate_upgrade_cost()

        assert total_cost == expected

    def test_get_max_level_facilities(self, facility_system, sample_facilities):
        """Test getting max level facilities."""
        max_level = facility_system.get_max_level_facilities(sample_facilities)

        assert len(max_level) == 0

        # Set one to max level
        sample_facilities[0].level = 10
        max_level = facility_system.get_max_level_facilities(sample_facilities)

        assert len(max_level) == 1
        assert max_level[0].id == "office_space"

    def test_get_facility_summary(self, facility_system, sample_facility):
        """Test facility summary generation."""
        sample_facility.level = 3

        summary = facility_system.get_facility_summary(sample_facility)

        assert summary["id"] == "office_space"
        assert summary["level"] == 3
        assert summary["can_upgrade"] is True
        assert "upgrade_cost" in summary
        assert "current_bonuses" in summary
        assert "upgrade_preview" in summary

    def test_get_all_facilities_summary(
        self, facility_system, sample_facilities
    ):
        """Test comprehensive facilities summary."""
        summary = facility_system.get_all_facilities_summary(sample_facilities)

        assert summary["total_facilities"] == 3
        assert summary["upgradeable_facilities"] == 3
        assert summary["max_level_facilities"] == 0
        assert "total_upgrade_cost" in summary
        assert "aggregate_bonuses" in summary
        assert len(summary["facilities"]) == 3
