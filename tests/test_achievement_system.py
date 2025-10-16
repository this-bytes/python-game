"""Tests for Achievement System."""

import pytest
from unittest.mock import Mock
from src.core.achievement_system import AchievementSystem
from src.models.achievement import Achievement
from src.models.game_state import GameState, GameMetrics
from src.models.specialist import Specialist, SpecialistStats


class TestAchievement:
    """Test Achievement model."""
    
    def test_to_dict(self):
        """Test converting achievement to dictionary."""
        achievement = Achievement(
            id="test_achievement",
            name="Test Achievement",
            description="A test achievement",
            category="progression",
            condition_type="incidents_resolved",
            condition_value=10,
            reward_money=1000,
            reward_xp=100,
            reward_equipment="basic_laptop",
            hidden=False
        )
        
        data = achievement.to_dict()
        
        assert data["id"] == "test_achievement"
        assert data["name"] == "Test Achievement"
        assert data["category"] == "progression"
        assert data["reward_money"] == 1000
    
    def test_from_dict(self):
        """Test creating achievement from dictionary."""
        data = {
            "id": "test_achievement",
            "name": "Test Achievement",
            "description": "A test achievement",
            "category": "efficiency",
            "condition_type": "sla_perfection",
            "condition_value": 50,
            "reward_money": 5000,
            "reward_xp": 500,
            "reward_equipment": None,
            "hidden": True
        }
        
        achievement = Achievement.from_dict(data)
        
        assert achievement.id == "test_achievement"
        assert achievement.category == "efficiency"
        assert achievement.hidden is True


class TestAchievementSystem:
    """Test AchievementSystem class."""
    
    @pytest.fixture
    def achievements_config(self):
        """Sample achievements configuration."""
        return {
            "achievements": [
                {
                    "id": "first_incident",
                    "name": "First Incident",
                    "description": "Resolve first incident",
                    "category": "progression",
                    "condition_type": "incidents_resolved",
                    "condition_value": 1,
                    "reward_money": 500,
                    "reward_xp": 50,
                    "reward_equipment": None
                },
                {
                    "id": "veteran",
                    "name": "Veteran",
                    "description": "Resolve 50 incidents",
                    "category": "progression",
                    "condition_type": "incidents_resolved",
                    "condition_value": 50,
                    "reward_money": 5000,
                    "reward_xp": 500,
                    "reward_equipment": "gold_badge"
                },
                {
                    "id": "rich",
                    "name": "Rich",
                    "description": "Earn $100k",
                    "category": "wealth",
                    "condition_type": "money_earned",
                    "condition_value": 100000,
                    "reward_money": 10000,
                    "reward_xp": 1000,
                    "reward_equipment": None
                },
                {
                    "id": "level_10",
                    "name": "Expert",
                    "description": "Reach level 10",
                    "category": "progression",
                    "condition_type": "specialist_level",
                    "condition_value": 10,
                    "reward_money": 5000,
                    "reward_xp": 500,
                    "reward_equipment": None
                },
                {
                    "id": "perfect_10",
                    "name": "Perfect 10",
                    "description": "10 perfect SLA",
                    "category": "efficiency",
                    "condition_type": "sla_perfection",
                    "condition_value": 10,
                    "reward_money": 5000,
                    "reward_xp": 500,
                    "reward_equipment": None
                }
            ]
        }
    
    @pytest.fixture
    def achievement_system(self, achievements_config):
        """Create an achievement system for testing."""
        return AchievementSystem(achievements_config)
    
    @pytest.fixture
    def mock_game_state(self):
        """Create a mock game state for testing."""
        game_state = Mock()
        game_state.metrics = GameMetrics()
        game_state.specialists = []
        game_state.clients = []
        game_state.current_money = 0
        game_state.total_money_earned = 0
        game_state.total_prestiges = 0
        game_state.unlocked_achievements = []
        game_state.achievement_progress = {}
        return game_state
    
    def test_initialization(self, achievement_system):
        """Test achievement system initialization."""
        assert len(achievement_system.achievements) == 5
        assert "first_incident" in achievement_system.achievements
        assert "veteran" in achievement_system.achievements
    
    def test_check_achievement_incidents_resolved(self, achievement_system, mock_game_state):
        """Test checking incidents resolved achievement."""
        mock_game_state.metrics.total_incidents_handled = 1
        
        newly_unlocked = achievement_system.check_achievements(mock_game_state)
        
        assert len(newly_unlocked) >= 1
        assert newly_unlocked[0].id == "first_incident"
        assert "first_incident" in mock_game_state.unlocked_achievements
    
    def test_check_achievement_already_unlocked(self, achievement_system, mock_game_state):
        """Test that already unlocked achievements are not re-unlocked."""
        mock_game_state.metrics.total_incidents_handled = 1
        mock_game_state.unlocked_achievements = ["first_incident"]
        
        newly_unlocked = achievement_system.check_achievements(mock_game_state)
        
        assert len(newly_unlocked) == 0
    
    def test_check_achievement_money_earned(self, achievement_system, mock_game_state):
        """Test checking money earned achievement."""
        mock_game_state.total_money_earned = 100000
        
        newly_unlocked = achievement_system.check_achievements(mock_game_state)
        
        assert len(newly_unlocked) >= 1
        assert newly_unlocked[0].id == "rich"
    
    def test_check_achievement_specialist_level(self, achievement_system, mock_game_state):
        """Test checking specialist level achievement."""
        specialist = Specialist(
            id="test_spec",
            name="Test",
            specialty="Network Security",
            level=10,
            xp=1000,
            stats=SpecialistStats(50, 50, 1.0)
        )
        mock_game_state.specialists = [specialist]
        
        newly_unlocked = achievement_system.check_achievements(mock_game_state)
        
        assert len(newly_unlocked) >= 1
        assert newly_unlocked[0].id == "level_10"
    
    def test_check_achievement_sla_perfection(self, achievement_system, mock_game_state):
        """Test checking SLA perfection achievement."""
        mock_game_state.metrics.total_incidents_handled = 10
        mock_game_state.metrics.total_incidents_failed = 0
        mock_game_state.metrics.sla_compliance_rate = 100.0
        
        newly_unlocked = achievement_system.check_achievements(mock_game_state)
        
        assert len(newly_unlocked) >= 1
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "perfect_10" in unlocked_ids
    
    def test_award_achievement_money(self, achievement_system, mock_game_state):
        """Test awarding money reward."""
        achievement = achievement_system.get_achievement("first_incident")
        initial_money = mock_game_state.current_money
        
        achievement_system.award_achievement(achievement, mock_game_state)
        
        assert mock_game_state.current_money == initial_money + 500
    
    def test_award_achievement_xp(self, achievement_system, mock_game_state):
        """Test awarding XP reward."""
        specialist = Specialist(
            id="test_spec",
            name="Test",
            specialty="Network Security",
            level=1,
            xp=0,
            stats=SpecialistStats(50, 50, 1.0)
        )
        mock_game_state.specialists = [specialist]
        
        achievement = achievement_system.get_achievement("first_incident")
        achievement_system.award_achievement(achievement, mock_game_state)
        
        # XP should be awarded to specialist
        assert specialist.xp > 0
    
    def test_award_achievement_equipment(self, achievement_system, mock_game_state):
        """Test awarding equipment reward."""
        specialist = Specialist(
            id="test_spec",
            name="Test",
            specialty="Network Security",
            level=1,
            xp=0,
            stats=SpecialistStats(50, 50, 1.0)
        )
        mock_game_state.specialists = [specialist]
        
        achievement = achievement_system.get_achievement("veteran")
        achievement_system.award_achievement(achievement, mock_game_state)
        
        # Equipment should be added to inventory
        assert "gold_badge" in specialist.inventory
    
    def test_get_progress_incidents(self, achievement_system, mock_game_state):
        """Test getting progress for incidents achievement."""
        mock_game_state.metrics.total_incidents_handled = 25
        
        achievement = achievement_system.get_achievement("veteran")
        progress = achievement_system.get_progress(achievement, mock_game_state)
        
        assert progress == 0.5  # 25/50
    
    def test_get_progress_money(self, achievement_system, mock_game_state):
        """Test getting progress for money achievement."""
        mock_game_state.total_money_earned = 50000
        
        achievement = achievement_system.get_achievement("rich")
        progress = achievement_system.get_progress(achievement, mock_game_state)
        
        assert progress == 0.5  # 50000/100000
    
    def test_get_progress_unlocked(self, achievement_system, mock_game_state):
        """Test that unlocked achievements have 100% progress."""
        mock_game_state.unlocked_achievements = ["first_incident"]
        
        achievement = achievement_system.get_achievement("first_incident")
        progress = achievement_system.get_progress(achievement, mock_game_state)
        
        assert progress == 1.0
    
    def test_get_achievement(self, achievement_system):
        """Test getting achievement by ID."""
        achievement = achievement_system.get_achievement("veteran")
        
        assert achievement is not None
        assert achievement.name == "Veteran"
        
        # Non-existent achievement
        assert achievement_system.get_achievement("nonexistent") is None
    
    def test_get_all_achievements(self, achievement_system):
        """Test getting all achievements."""
        achievements = achievement_system.get_all_achievements()
        
        assert len(achievements) == 5
    
    def test_get_achievements_by_category(self, achievement_system):
        """Test getting achievements by category."""
        progression = achievement_system.get_achievements_by_category("progression")
        wealth = achievement_system.get_achievements_by_category("wealth")
        
        assert len(progression) == 3
        assert len(wealth) == 1
    
    def test_multiple_achievements_unlocked(self, achievement_system, mock_game_state):
        """Test unlocking multiple achievements at once."""
        # Set conditions for multiple achievements
        mock_game_state.metrics.total_incidents_handled = 50
        mock_game_state.total_money_earned = 100000
        
        newly_unlocked = achievement_system.check_achievements(mock_game_state)
        
        # Should unlock first_incident, veteran, and rich
        assert len(newly_unlocked) >= 2
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "first_incident" in unlocked_ids
        assert "veteran" in unlocked_ids
