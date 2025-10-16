"""Tests for prestige system (Task 22)."""

from unittest.mock import Mock
import pytest

from src.models.prestige import PrestigeUpgrade, PrestigeEffectType
from src.core.prestige_system import PrestigeSystem
from src.models.specialist import Specialist, SpecialistStats
from src.models.game_state import GameMetrics


class TestPrestigeUpgrade:
    """Test prestige upgrade model."""

    def test_initialization(self):
        """Test prestige upgrade initialization."""
        upgrade = PrestigeUpgrade(
            id="test_upgrade",
            name="Test Upgrade",
            description="Test description",
            cost_prestige_points=10,
            effect_type="xp_multiplier",
            effect_magnitude=0.1,
            max_level=5
        )
        
        assert upgrade.id == "test_upgrade"
        assert upgrade.effect_type == "xp_multiplier"
        assert upgrade.max_level == 5

    def test_invalid_effect_type(self):
        """Test that invalid effect type raises error."""
        with pytest.raises(ValueError, match="Invalid prestige effect type"):
            PrestigeUpgrade(
                id="test",
                name="Test",
                description="Test",
                cost_prestige_points=10,
                effect_type="invalid_type",
                effect_magnitude=0.1,
                max_level=5
            )

    def test_calculate_cost(self):
        """Test cost calculation with exponential scaling."""
        upgrade = PrestigeUpgrade(
            id="test",
            name="Test",
            description="Test",
            cost_prestige_points=10,
            effect_type="xp_multiplier",
            effect_magnitude=0.1,
            max_level=5
        )
        
        # Level 0 → 1
        assert upgrade.calculate_cost(0) == 10
        
        # Level 1 → 2
        assert upgrade.calculate_cost(1) == 15
        
        # Level 2 → 3
        assert upgrade.calculate_cost(2) == int(10 * 1.5 ** 2)
        
        # At max level
        assert upgrade.calculate_cost(5) == -1

    def test_calculate_total_effect(self):
        """Test total effect calculation."""
        upgrade = PrestigeUpgrade(
            id="test",
            name="Test",
            description="Test",
            cost_prestige_points=10,
            effect_type="xp_multiplier",
            effect_magnitude=0.1,
            max_level=5
        )
        
        assert upgrade.calculate_total_effect(0) == 0.0
        assert upgrade.calculate_total_effect(1) == pytest.approx(0.1)
        assert upgrade.calculate_total_effect(3) == pytest.approx(0.3)
        assert upgrade.calculate_total_effect(5) == pytest.approx(0.5)

    def test_serialization(self):
        """Test to_dict and from_dict."""
        original = PrestigeUpgrade(
            id="test",
            name="Test Upgrade",
            description="Test description",
            cost_prestige_points=10,
            effect_type="xp_multiplier",
            effect_magnitude=0.1,
            max_level=5
        )
        
        data = original.to_dict()
        restored = PrestigeUpgrade.from_dict(data)
        
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.effect_type == original.effect_type
        assert restored.effect_magnitude == original.effect_magnitude


class TestPrestigeSystem:
    """Test prestige system features."""

    def test_initialization(self):
        """Test prestige system initialization."""
        upgrades = [
            PrestigeUpgrade(
                id="test1",
                name="Test 1",
                description="Test",
                cost_prestige_points=10,
                effect_type="xp_multiplier",
                effect_magnitude=0.1,
                max_level=5
            )
        ]
        
        system = PrestigeSystem(upgrades)
        assert len(system._upgrades) == 1

    def test_calculate_prestige_points_from_xp(self):
        """Test prestige point calculation from XP."""
        upgrades = []
        system = PrestigeSystem(upgrades)
        
        game_state = Mock()
        game_state.specialists = [
            Mock(xp=15000, level=10),
            Mock(xp=25000, level=15)
        ]
        game_state.total_money_earned = 0
        game_state.metrics = GameMetrics()
        
        points = system.calculate_prestige_points(game_state)
        
        # XP: 40,000 / 10,000 = 4 points
        # Levels: 25 / 10 = 2 points
        # Total: 6 points minimum
        assert points >= 6

    def test_calculate_prestige_points_from_money(self):
        """Test prestige point calculation from money."""
        upgrades = []
        system = PrestigeSystem(upgrades)
        
        game_state = Mock()
        game_state.specialists = []
        game_state.total_money_earned = 350000
        game_state.metrics = GameMetrics()
        
        points = system.calculate_prestige_points(game_state)
        
        # Money: 350,000 / 100,000 = 3 points
        assert points >= 3

    def test_calculate_prestige_points_sla_bonus(self):
        """Test prestige point bonus for high SLA compliance."""
        upgrades = []
        system = PrestigeSystem(upgrades)
        
        game_state = Mock()
        game_state.specialists = []
        game_state.total_money_earned = 0
        game_state.metrics = GameMetrics()
        game_state.metrics.sla_compliance_rate = 96.0
        
        points = system.calculate_prestige_points(game_state)
        
        # Should get bonus points for >95% SLA
        # With 0 base points: 0 + 5 (>=90%) + 5 (>=95%) = 10
        # Then max(1, 10) = 10
        assert points == 10

    def test_purchase_prestige_upgrade_success(self):
        """Test successful prestige upgrade purchase."""
        upgrades = [
            PrestigeUpgrade(
                id="test_upgrade",
                name="Test",
                description="Test",
                cost_prestige_points=10,
                effect_type="xp_multiplier",
                effect_magnitude=0.1,
                max_level=5
            )
        ]
        system = PrestigeSystem(upgrades)
        
        game_state = Mock()
        game_state.prestige_points = 20
        game_state.prestige_upgrades = {}
        
        result = system.purchase_prestige_upgrade("test_upgrade", game_state)
        
        assert result["success"] is True
        assert result["new_level"] == 1
        assert result["cost"] == 10
        assert game_state.prestige_points == 10

    def test_purchase_prestige_upgrade_insufficient_points(self):
        """Test prestige upgrade purchase with insufficient points."""
        upgrades = [
            PrestigeUpgrade(
                id="test_upgrade",
                name="Test",
                description="Test",
                cost_prestige_points=10,
                effect_type="xp_multiplier",
                effect_magnitude=0.1,
                max_level=5
            )
        ]
        system = PrestigeSystem(upgrades)
        
        game_state = Mock()
        game_state.prestige_points = 5
        game_state.prestige_upgrades = {}
        
        result = system.purchase_prestige_upgrade("test_upgrade", game_state)
        
        assert result["success"] is False
        assert "Insufficient" in result["error"]

    def test_purchase_prestige_upgrade_max_level(self):
        """Test prestige upgrade purchase at max level."""
        upgrades = [
            PrestigeUpgrade(
                id="test_upgrade",
                name="Test",
                description="Test",
                cost_prestige_points=10,
                effect_type="xp_multiplier",
                effect_magnitude=0.1,
                max_level=2
            )
        ]
        system = PrestigeSystem(upgrades)
        
        game_state = Mock()
        game_state.prestige_points = 100
        game_state.prestige_upgrades = {"test_upgrade": 2}
        
        result = system.purchase_prestige_upgrade("test_upgrade", game_state)
        
        assert result["success"] is False
        assert "max level" in result["error"]

    def test_apply_prestige_bonuses(self):
        """Test applying prestige bonuses."""
        upgrades = [
            PrestigeUpgrade(
                id="xp_boost",
                name="XP Boost",
                description="Test",
                cost_prestige_points=10,
                effect_type="xp_multiplier",
                effect_magnitude=0.1,
                max_level=5
            )
        ]
        system = PrestigeSystem(upgrades)
        
        game_state = Mock()
        game_state.prestige_upgrades = {"xp_boost": 3}
        
        bonuses = system.apply_prestige_bonuses(game_state)
        
        assert "xp_multiplier" in bonuses
        assert bonuses["xp_multiplier"] == pytest.approx(0.3)  # 3 levels * 0.1

    def test_get_prestige_multiplier(self):
        """Test getting prestige multiplier for effect type."""
        upgrades = [
            PrestigeUpgrade(
                id="money_boost",
                name="Money Boost",
                description="Test",
                cost_prestige_points=10,
                effect_type="money_multiplier",
                effect_magnitude=0.15,
                max_level=5
            )
        ]
        system = PrestigeSystem(upgrades)
        
        game_state = Mock()
        game_state.prestige_upgrades = {"money_boost": 2}
        
        multiplier = system.get_prestige_multiplier(game_state, "money_multiplier")
        
        # 1.0 + (2 * 0.15) = 1.3
        assert multiplier == pytest.approx(1.3, rel=0.01)

    def test_get_available_upgrades(self):
        """Test getting available upgrades list."""
        upgrades = [
            PrestigeUpgrade(
                id="test1",
                name="Test 1",
                description="Test",
                cost_prestige_points=10,
                effect_type="xp_multiplier",
                effect_magnitude=0.1,
                max_level=5
            ),
            PrestigeUpgrade(
                id="test2",
                name="Test 2",
                description="Test",
                cost_prestige_points=20,
                effect_type="money_multiplier",
                effect_magnitude=0.15,
                max_level=3
            )
        ]
        system = PrestigeSystem(upgrades)
        
        game_state = Mock()
        game_state.prestige_points = 15
        game_state.prestige_upgrades = {"test1": 2}
        
        available = system.get_available_upgrades(game_state)
        
        assert len(available) == 2
        
        # First upgrade
        upgrade1 = next(u for u in available if u["id"] == "test1")
        assert upgrade1["current_level"] == 2
        assert upgrade1["can_afford"] is False  # Cost is 10 * 1.5^2 = 22.5
        
        # Second upgrade
        upgrade2 = next(u for u in available if u["id"] == "test2")
        assert upgrade2["current_level"] == 0
        assert upgrade2["can_afford"] is False  # Cost is 20

    def test_statistics_tracking(self):
        """Test statistics tracking."""
        upgrades = []
        system = PrestigeSystem(upgrades)
        
        stats = system.get_statistics()
        assert "total_prestiges" in stats
        assert "total_prestige_points_earned" in stats
        assert "total_prestige_points_spent" in stats

    def test_reset_statistics(self):
        """Test statistics reset."""
        upgrades = []
        system = PrestigeSystem(upgrades)
        
        system._stats["total_prestiges"] = 5
        system.reset_statistics()
        
        stats = system.get_statistics()
        assert stats["total_prestiges"] == 0
