"""Achievement System - Track Player Accomplishments

Achievements provide goals, feedback, and a sense of progression beyond
just leveling up specialists. They celebrate milestones and reward
exploration of different playstyles.

Achievement Categories:
- Revenue milestones (earn $X)
- Incident count (resolve X incidents)
- Specialist progression (level X reached, all specialists hired)
- Speed runs (resolve incident in < X seconds)
- Perfect runs (X perfect completions in a row)
- Synergy mastery (X synergy bonuses triggered)
- Prestige progression (prestige X times)
- Collections (hire all specialist types, unlock all rooms)

Achievement Rewards:
- Cosmetic unlocks (decorations, themes)
- Title unlocks (displayed in UI)
- Small prestige point bonuses
- Easter eggs and lore unlocks
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import logging
import time

from src.core.game_system import GameSystem
from src.core.event_bus import get_event_bus
from src.models.game_state import GameState

logger = logging.getLogger(__name__)


@dataclass
class Achievement:
    """Definition of an achievement."""
    id: str
    name: str
    description: str
    category: str
    
    # Unlock criteria
    requirement_type: str  # "count", "threshold", "boolean", "streak"
    requirement_value: int
    
    # Tracking
    current_progress: int = 0
    unlocked: bool = False
    unlock_timestamp: Optional[float] = None
    
    # Rewards
    reward_type: Optional[str] = None
    reward_value: Any = None
    
    # Metadata
    hidden: bool = False  # Hidden until unlocked
    rarity: str = "common"  # common, rare, epic, legendary
    points: int = 10  # Achievement points for collection completion


class AchievementSystem(GameSystem):
    """Achievement tracking and rewards system."""
    
    def __init__(self):
        super().__init__()
        
        self.achievements: Dict[str, Achievement] = {}
        self.total_achievement_points = 0
        
        # Stats for achievement tracking
        self.stats = {
            "total_revenue": 0,
            "incidents_resolved": 0,
            "perfect_completions": 0,
            "perfect_streak": 0,
            "max_perfect_streak": 0,
            "synergy_bonuses_triggered": 0,
            "prestige_count": 0,
            "max_specialist_level": 0,
            "fastest_incident_time": float('inf'),
            "specialists_hired": set(),
            "rooms_unlocked": set(),
        }
        
        # Event bus and subscription tracking
        self._event_bus = None
        self._subscription_ids: List[str] = []
        
        self._initialize_achievements()
    
    def get_name(self) -> str:
        """Get system name."""
        return "achievement_system"
    
    def get_feature_id(self) -> Optional[str]:
        """Get feature flag ID."""
        return "achievement_system"
    
    def initialize(self, game_state: GameState) -> None:
        """Initialize achievement system.
        
        Args:
            game_state: Current game state
        """
        logger.info("Initializing Achievement System...")
        
        # Get event bus singleton
        self._event_bus = get_event_bus()
        
        # Subscribe to all relevant events
        sub_id = self._event_bus.subscribe("money_earned", self._on_money_earned)
        self._subscription_ids.append(sub_id)
        
        sub_id = self._event_bus.subscribe("incident_resolved", self._on_incident_resolved)
        self._subscription_ids.append(sub_id)
        
        sub_id = self._event_bus.subscribe("perfect_completion", self._on_perfect_completion)
        self._subscription_ids.append(sub_id)
        
        sub_id = self._event_bus.subscribe("synergy_bonus_applied", self._on_synergy_bonus)
        self._subscription_ids.append(sub_id)
        
        sub_id = self._event_bus.subscribe("prestige_completed", self._on_prestige)
        self._subscription_ids.append(sub_id)
        
        sub_id = self._event_bus.subscribe("specialist_leveled_up", self._on_specialist_level)
        self._subscription_ids.append(sub_id)
        
        sub_id = self._event_bus.subscribe("specialist_hired", self._on_specialist_hired)
        self._subscription_ids.append(sub_id)
        
        sub_id = self._event_bus.subscribe("room_unlocked", self._on_room_unlocked)
        self._subscription_ids.append(sub_id)
        
        logger.info(f"Achievement System initialized with {len(self.achievements)} achievements")
    
    def update(self, game_state: GameState, delta_time: float) -> None:
        """Update achievement system.
        
        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update (seconds)
        """
        # Achievement checking happens on events, not every frame
        pass
    
    def shutdown(self, game_state: GameState) -> None:
        """Shutdown achievement system.
        
        Args:
            game_state: Current game state
        """
        logger.info("Shutting down Achievement System...")
        
        if self._event_bus:
            for sub_id in self._subscription_ids:
                self._event_bus.unsubscribe(sub_id)
            self._subscription_ids.clear()
    
    def save_state(self, game_state: GameState) -> Dict[str, Any]:
        """Get achievement state for saving.
        
        Args:
            game_state: Current game state
            
        Returns:
            Dictionary with achievement state
        """
        achievements_state = {}
        for ach_id, achievement in self.achievements.items():
            achievements_state[ach_id] = {
                "current_progress": achievement.current_progress,
                "unlocked": achievement.unlocked,
                "unlock_timestamp": achievement.unlock_timestamp
            }
        
        return {
            "achievements": achievements_state,
            "total_achievement_points": self.total_achievement_points,
            "stats": {
                "total_revenue": self.stats["total_revenue"],
                "incidents_resolved": self.stats["incidents_resolved"],
                "perfect_completions": self.stats["perfect_completions"],
                "perfect_streak": self.stats["perfect_streak"],
                "max_perfect_streak": self.stats["max_perfect_streak"],
                "synergy_bonuses_triggered": self.stats["synergy_bonuses_triggered"],
                "prestige_count": self.stats["prestige_count"],
                "max_specialist_level": self.stats["max_specialist_level"],
                "fastest_incident_time": self.stats["fastest_incident_time"],
                "specialists_hired": list(self.stats["specialists_hired"]),
                "rooms_unlocked": list(self.stats["rooms_unlocked"]),
            }
        }
    
    def load_state(self, game_state: GameState, state_data: Dict[str, Any]) -> None:
        """Restore achievement state.
        
        Args:
            game_state: Current game state
            state_data: Saved achievement state
        """
        self.total_achievement_points = state_data.get("total_achievement_points", 0)
        
        # Restore stats
        if "stats" in state_data:
            stats = state_data["stats"]
            self.stats["total_revenue"] = stats.get("total_revenue", 0)
            self.stats["incidents_resolved"] = stats.get("incidents_resolved", 0)
            self.stats["perfect_completions"] = stats.get("perfect_completions", 0)
            self.stats["perfect_streak"] = stats.get("perfect_streak", 0)
            self.stats["max_perfect_streak"] = stats.get("max_perfect_streak", 0)
            self.stats["synergy_bonuses_triggered"] = stats.get("synergy_bonuses_triggered", 0)
            self.stats["prestige_count"] = stats.get("prestige_count", 0)
            self.stats["max_specialist_level"] = stats.get("max_specialist_level", 0)
            self.stats["fastest_incident_time"] = stats.get("fastest_incident_time", float('inf'))
            self.stats["specialists_hired"] = set(stats.get("specialists_hired", []))
            self.stats["rooms_unlocked"] = set(stats.get("rooms_unlocked", []))
        
        # Restore achievement progress
        if "achievements" in state_data:
            for ach_id, ach_state in state_data["achievements"].items():
                if ach_id in self.achievements:
                    achievement = self.achievements[ach_id]
                    achievement.current_progress = ach_state.get("current_progress", 0)
                    achievement.unlocked = ach_state.get("unlocked", False)
                    achievement.unlock_timestamp = ach_state.get("unlock_timestamp")
    
    def _initialize_achievements(self):
        """Initialize all achievement definitions."""
        
        # Revenue milestones
        self._add_achievement(Achievement(
            id="first_dollar",
            name="First Dollar",
            description="Earn your first dollar",
            category="revenue",
            requirement_type="threshold",
            requirement_value=1,
            rarity="common",
            points=5
        ))
        
        self._add_achievement(Achievement(
            id="small_business",
            name="Small Business",
            description="Earn $10,000",
            category="revenue",
            requirement_type="threshold",
            requirement_value=10_000,
            rarity="common",
            points=10
        ))
        
        self._add_achievement(Achievement(
            id="big_business",
            name="Big Business",
            description="Earn $100,000",
            category="revenue",
            requirement_type="threshold",
            requirement_value=100_000,
            rarity="rare",
            points=25
        ))
        
        self._add_achievement(Achievement(
            id="millionaire",
            name="Millionaire",
            description="Earn $1,000,000",
            category="revenue",
            requirement_type="threshold",
            requirement_value=1_000_000,
            rarity="epic",
            points=50,
            reward_type="prestige_points",
            reward_value=1
        ))
        
        # Incident resolution
        self._add_achievement(Achievement(
            id="first_incident",
            name="First Response",
            description="Resolve your first incident",
            category="incidents",
            requirement_type="count",
            requirement_value=1,
            rarity="common",
            points=5
        ))
        
        self._add_achievement(Achievement(
            id="incident_100",
            name="Security Veteran",
            description="Resolve 100 incidents",
            category="incidents",
            requirement_type="count",
            requirement_value=100,
            rarity="rare",
            points=25
        ))
        
        self._add_achievement(Achievement(
            id="incident_1000",
            name="Cyber Guardian",
            description="Resolve 1,000 incidents",
            category="incidents",
            requirement_type="count",
            requirement_value=1000,
            rarity="epic",
            points=50
        ))
        
        # Perfect completions
        self._add_achievement(Achievement(
            id="perfectionist",
            name="Perfectionist",
            description="Complete 10 perfect incidents",
            category="mastery",
            requirement_type="count",
            requirement_value=10,
            rarity="rare",
            points=20
        ))
        
        self._add_achievement(Achievement(
            id="perfect_streak_5",
            name="On Fire",
            description="Get 5 perfect completions in a row",
            category="mastery",
            requirement_type="streak",
            requirement_value=5,
            rarity="rare",
            points=30
        ))
        
        self._add_achievement(Achievement(
            id="perfect_streak_10",
            name="Unstoppable",
            description="Get 10 perfect completions in a row",
            category="mastery",
            requirement_type="streak",
            requirement_value=10,
            rarity="epic",
            points=50,
            reward_type="prestige_points",
            reward_value=1
        ))
        
        # Speed achievements
        self._add_achievement(Achievement(
            id="speedrunner",
            name="Speedrunner",
            description="Resolve an incident in under 30 seconds",
            category="speed",
            requirement_type="threshold",
            requirement_value=30,
            rarity="rare",
            points=25
        ))
        
        # Synergy mastery
        self._add_achievement(Achievement(
            id="synergy_master",
            name="Synergy Master",
            description="Trigger 100 synergy bonuses",
            category="mastery",
            requirement_type="count",
            requirement_value=100,
            rarity="rare",
            points=30
        ))
        
        # Prestige
        self._add_achievement(Achievement(
            id="first_prestige",
            name="Fresh Start",
            description="Prestige for the first time",
            category="prestige",
            requirement_type="count",
            requirement_value=1,
            rarity="epic",
            points=50
        ))
        
        self._add_achievement(Achievement(
            id="prestige_veteran",
            name="Eternal Cycle",
            description="Prestige 10 times",
            category="prestige",
            requirement_type="count",
            requirement_value=10,
            rarity="legendary",
            points=100,
            reward_type="prestige_points",
            reward_value=5
        ))
        
        # Collection achievements
        self._add_achievement(Achievement(
            id="team_builder",
            name="Team Builder",
            description="Hire 5 specialists",
            category="collection",
            requirement_type="count",
            requirement_value=5,
            rarity="common",
            points=15
        ))
        
        logger.info(f"Initialized {len(self.achievements)} achievements")
    
    def _add_achievement(self, achievement: Achievement):
        """Add an achievement to the system."""
        self.achievements[achievement.id] = achievement
    
    def _check_achievement(self, achievement_id: str):
        """Check if an achievement should be unlocked."""
        achievement = self.achievements.get(achievement_id)
        if not achievement or achievement.unlocked:
            return
        
        # Check if requirement is met
        unlocked = False
        
        if achievement.requirement_type == "threshold":
            if achievement.id.startswith("revenue") or achievement.category == "revenue":
                unlocked = self.stats["total_revenue"] >= achievement.requirement_value
            elif achievement.id == "speedrunner":
                unlocked = self.stats["fastest_incident_time"] <= achievement.requirement_value
        
        elif achievement.requirement_type == "count":
            if achievement.category == "incidents":
                unlocked = self.stats["incidents_resolved"] >= achievement.requirement_value
            elif achievement.category == "mastery" and "perfect" in achievement.id:
                unlocked = self.stats["perfect_completions"] >= achievement.requirement_value
            elif achievement.id == "synergy_master":
                unlocked = self.stats["synergy_bonuses_triggered"] >= achievement.requirement_value
            elif achievement.category == "prestige":
                unlocked = self.stats["prestige_count"] >= achievement.requirement_value
            elif achievement.category == "collection":
                unlocked = len(self.stats["specialists_hired"]) >= achievement.requirement_value
        
        elif achievement.requirement_type == "streak":
            unlocked = self.stats["max_perfect_streak"] >= achievement.requirement_value
        
        if unlocked:
            self._unlock_achievement(achievement)
    
    def _unlock_achievement(self, achievement: Achievement):
        """Unlock an achievement and grant rewards."""
        achievement.unlocked = True
        achievement.unlock_timestamp = time.time()
        self.total_achievement_points += achievement.points
        
        logger.info(f"Achievement unlocked: {achievement.name} (+{achievement.points} points)")
        
        # Emit unlock event
        if self._event_bus:
            self._event_bus.publish("achievement_unlocked", {
                "achievement_id": achievement.id,
                "achievement_name": achievement.name,
                "achievement_description": achievement.description,
                "points": achievement.points,
                "rarity": achievement.rarity,
                "reward_type": achievement.reward_type,
                "reward_value": achievement.reward_value
            })
        
        # Grant rewards
        if achievement.reward_type == "prestige_points":
            if self._event_bus:
                self._event_bus.publish("prestige_points_awarded", {
                    "amount": achievement.reward_value,
                    "source": f"achievement_{achievement.id}"
                })
    
    def _on_money_earned(self, event) -> None:
        """Track money earned.
        
        Args:
            event: Event object containing money earned data
        """
        amount = event.data.get("amount", 0)
        self.stats["total_revenue"] += amount
        
        # Check revenue achievements
        for ach_id in ["first_dollar", "small_business", "big_business", "millionaire"]:
            self._check_achievement(ach_id)
    
    def _on_incident_resolved(self, event) -> None:
        """Track incident resolution.
        
        Args:
            event: Event object containing incident resolution data
        """
        self.stats["incidents_resolved"] += 1
        
        # Track completion time for speed achievements
        completion_time = event.data.get("completion_time", float('inf'))
        if completion_time < self.stats["fastest_incident_time"]:
            self.stats["fastest_incident_time"] = completion_time
            self._check_achievement("speedrunner")
        
        # Check incident count achievements
        for ach_id in ["first_incident", "incident_100", "incident_1000"]:
            self._check_achievement(ach_id)
    
    def _on_perfect_completion(self, event) -> None:
        """Track perfect completions and streaks.
        
        Args:
            event: Event object containing perfect completion data
        """
        self.stats["perfect_completions"] += 1
        self.stats["perfect_streak"] += 1
        
        if self.stats["perfect_streak"] > self.stats["max_perfect_streak"]:
            self.stats["max_perfect_streak"] = self.stats["perfect_streak"]
        
        # Check perfect completion achievements
        for ach_id in ["perfectionist", "perfect_streak_5", "perfect_streak_10"]:
            self._check_achievement(ach_id)
    
    def _on_synergy_bonus(self, event) -> None:
        """Track synergy bonuses.
        
        Args:
            event: Event object containing synergy bonus data
        """
        self.stats["synergy_bonuses_triggered"] += 1
        self._check_achievement("synergy_master")
    
    def _on_prestige(self, event) -> None:
        """Track prestige count.
        
        Args:
            event: Event object containing prestige completion data
        """
        self.stats["prestige_count"] += 1
        
        # Reset streak on prestige
        self.stats["perfect_streak"] = 0
        
        # Check prestige achievements
        for ach_id in ["first_prestige", "prestige_veteran"]:
            self._check_achievement(ach_id)
    
    def _on_specialist_level(self, event) -> None:
        """Track max specialist level.
        
        Args:
            event: Event object containing specialist level data
        """
        level = event.data.get("level", 1)
        if level > self.stats["max_specialist_level"]:
            self.stats["max_specialist_level"] = level
    
    def _on_specialist_hired(self, event) -> None:
        """Track specialists hired.
        
        Args:
            event: Event object containing specialist hire data
        """
        specialist_id = event.data.get("specialist_id")
        if specialist_id:
            self.stats["specialists_hired"].add(specialist_id)
            self._check_achievement("team_builder")
    
    def _on_room_unlocked(self, event) -> None:
        """Track rooms unlocked.
        
        Args:
            event: Event object containing room unlock data
        """
        room_id = event.data.get("room_id")
        if room_id:
            self.stats["rooms_unlocked"].add(room_id)
    
    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements."""
        return [ach for ach in self.achievements.values() if ach.unlocked]
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get achievement progress summary."""
        total_achievements = len(self.achievements)
        unlocked_count = len([ach for ach in self.achievements.values() if ach.unlocked])
        
        return {
            "total_achievements": total_achievements,
            "unlocked_count": unlocked_count,
            "unlock_percentage": (unlocked_count / total_achievements * 100) if total_achievements > 0 else 0,
            "total_points": self.total_achievement_points
        }
