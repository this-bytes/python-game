"""Progressive difficulty system for dynamic incident scaling.

This plugin implements progressive difficulty that adapts incident complexity based on
player performance, game progression, and various metrics. It ensures the game remains
challenging as players improve their cybersecurity firm.
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import random

from src.core.game_system import GameSystem
from src.core.event_bus import get_event_bus, Event
from src.models.game_state import GameState, GameMetrics
from src.utils.logger import GameLogger


@dataclass
class DifficultyMetrics:
    """Metrics used to calculate progressive difficulty."""

    # Performance indicators
    average_resolution_time: float = 0.0
    sla_compliance_rate: float = 100.0
    specialist_utilization_rate: float = 0.0
    assignment_success_rate: float = 0.0

    # Game progression indicators
    total_incidents_handled: int = 0
    average_specialist_level: float = 1.0
    total_money_earned: float = 0.0
    game_time_hours: float = 0.0

    # Recent performance (last 50 incidents)
    recent_success_rate: float = 100.0
    recent_average_resolution_time: float = 0.0
    recent_sla_compliance: float = 100.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for persistence."""
        return {
            "average_resolution_time": self.average_resolution_time,
            "sla_compliance_rate": self.sla_compliance_rate,
            "specialist_utilization_rate": self.specialist_utilization_rate,
            "assignment_success_rate": self.assignment_success_rate,
            "total_incidents_handled": self.total_incidents_handled,
            "average_specialist_level": self.average_specialist_level,
            "total_money_earned": self.total_money_earned,
            "game_time_hours": self.game_time_hours,
            "recent_success_rate": self.recent_success_rate,
            "recent_average_resolution_time": self.recent_average_resolution_time,
            "recent_sla_compliance": self.recent_sla_compliance,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DifficultyMetrics':
        """Create DifficultyMetrics from dictionary."""
        return cls(
            average_resolution_time=data.get("average_resolution_time", 0.0),
            sla_compliance_rate=data.get("sla_compliance_rate", 100.0),
            specialist_utilization_rate=data.get("specialist_utilization_rate", 0.0),
            assignment_success_rate=data.get("assignment_success_rate", 0.0),
            total_incidents_handled=data.get("total_incidents_handled", 0),
            average_specialist_level=data.get("average_specialist_level", 1.0),
            total_money_earned=data.get("total_money_earned", 0.0),
            game_time_hours=data.get("game_time_hours", 0.0),
            recent_success_rate=data.get("recent_success_rate", 100.0),
            recent_average_resolution_time=data.get("recent_average_resolution_time", 0.0),
            recent_sla_compliance=data.get("recent_sla_compliance", 100.0),
        )


@dataclass
class DifficultyScalingConfig:
    """Configuration for difficulty scaling parameters."""

    # Base difficulty multipliers
    base_difficulty_multiplier: float = 1.0
    max_difficulty_multiplier: float = 3.0

    # Performance thresholds
    excellent_performance_threshold: float = 0.9  # 90% success rate
    good_performance_threshold: float = 0.75      # 75% success rate
    poor_performance_threshold: float = 0.6       # 60% success rate

    # Scaling factors
    performance_scaling_factor: float = 0.1       # How much performance affects difficulty
    progression_scaling_factor: float = 0.05      # How much game progression affects difficulty
    time_pressure_scaling_factor: float = 0.02    # SLA time reduction per difficulty level

    # Difficulty milestones
    difficulty_milestones: Dict[int, Dict[str, Any]] = field(default_factory=lambda: {
        1: {"name": "Getting Started", "description": "Basic incident handling"},
        2: {"name": "Building Expertise", "description": "More complex incidents"},
        3: {"name": "Established Firm", "description": "High-stakes scenarios"},
        4: {"name": "Elite Operations", "description": "Critical infrastructure protection"},
        5: {"name": "Legendary Status", "description": "Unprecedented cyber threats"}
    })

    # Incident parameter adjustments
    damage_multiplier_per_level: float = 0.15      # Damage increases with difficulty
    reward_multiplier_per_level: float = 0.1       # Rewards increase with difficulty
    sla_reduction_per_level: float = 0.1           # SLA time decreases with difficulty

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "base_difficulty_multiplier": self.base_difficulty_multiplier,
            "max_difficulty_multiplier": self.max_difficulty_multiplier,
            "excellent_performance_threshold": self.excellent_performance_threshold,
            "good_performance_threshold": self.good_performance_threshold,
            "poor_performance_threshold": self.poor_performance_threshold,
            "performance_scaling_factor": self.performance_scaling_factor,
            "progression_scaling_factor": self.progression_scaling_factor,
            "time_pressure_scaling_factor": self.time_pressure_scaling_factor,
            "difficulty_milestones": self.difficulty_milestones,
            "damage_multiplier_per_level": self.damage_multiplier_per_level,
            "reward_multiplier_per_level": self.reward_multiplier_per_level,
            "sla_reduction_per_level": self.sla_reduction_per_level,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DifficultyScalingConfig':
        """Create config from dictionary."""
        return cls(
            base_difficulty_multiplier=data.get("base_difficulty_multiplier", 1.0),
            max_difficulty_multiplier=data.get("max_difficulty_multiplier", 3.0),
            excellent_performance_threshold=data.get("excellent_performance_threshold", 0.9),
            good_performance_threshold=data.get("good_performance_threshold", 0.75),
            poor_performance_threshold=data.get("poor_performance_threshold", 0.6),
            performance_scaling_factor=data.get("performance_scaling_factor", 0.1),
            progression_scaling_factor=data.get("progression_scaling_factor", 0.05),
            time_pressure_scaling_factor=data.get("time_pressure_scaling_factor", 0.02),
            difficulty_milestones=data.get("difficulty_milestones", {
                1: {"name": "Getting Started", "description": "Basic incident handling"},
                2: {"name": "Building Expertise", "description": "More complex incidents"},
                3: {"name": "Established Firm", "description": "High-stakes scenarios"},
                4: {"name": "Elite Operations", "description": "Critical infrastructure protection"},
                5: {"name": "Legendary Status", "description": "Unprecedented cyber threats"}
            }),
            damage_multiplier_per_level=data.get("damage_multiplier_per_level", 0.15),
            reward_multiplier_per_level=data.get("reward_multiplier_per_level", 0.1),
            sla_reduction_per_level=data.get("sla_reduction_per_level", 0.1),
        )


class ProgressiveDifficultyPlugin(GameSystem):
    """Plugin that implements progressive difficulty scaling based on player performance."""

    def __init__(self):
        """Initialize the progressive difficulty plugin."""
        super().__init__()
        self._event_bus = get_event_bus()
        self._logger = GameLogger("progressive_difficulty")
        self._subscription_ids: List[str] = []

        # Core state
        self._metrics = DifficultyMetrics()
        self._config = DifficultyScalingConfig()
        self._current_difficulty_level = 1
        self._difficulty_multiplier = 1.0

        # Recent incident tracking (for rolling averages)
        self._recent_incidents: List[Dict[str, Any]] = []
        self._max_recent_incidents = 50

        # Performance tracking
        self._last_metrics_update = time.time()
        self._metrics_update_interval = 60.0  # Update every minute

    def get_name(self) -> str:
        """Get plugin name."""
        return "ProgressiveDifficultyPlugin"

    def get_feature_id(self) -> str:
        """Get feature flag ID."""
        return "progressive_difficulty"

    def initialize(self, game_state: GameState) -> None:
        """Initialize the progressive difficulty plugin.

        Args:
            game_state: Current game state
        """
        self._logger.info("[PROGRESSIVE_DIFFICULTY] Initializing progressive difficulty system")

        # Subscribe to relevant events
        self._subscription_ids = [
            self._event_bus.subscribe("incident_completed", self._on_incident_completed),
            self._event_bus.subscribe("incident_failed", self._on_incident_failed),
            self._event_bus.subscribe("incident_generated", self._on_incident_generated),
            self._event_bus.subscribe("game_loaded", self._on_game_loaded),
        ]

        # Load configuration from game config
        self._load_config(game_state)

        # Initialize metrics from game state
        self._update_metrics(game_state)

        self._logger.info(f"[PROGRESSIVE_DIFFICULTY] Initialized with difficulty level {self._current_difficulty_level}")

    def update(self, game_state: GameState, delta_time: float) -> None:
        """Update progressive difficulty logic.

        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update
        """
        current_time = time.time()

        # Update metrics periodically
        if current_time - self._last_metrics_update >= self._metrics_update_interval:
            self._update_metrics(game_state)
            self._calculate_difficulty_level(game_state)
            self._last_metrics_update = current_time

        # Apply difficulty scaling to new incidents
        self._apply_difficulty_scaling(game_state)

    def shutdown(self, game_state: GameState) -> None:
        """Shutdown the progressive difficulty plugin.

        Args:
            game_state: Current game state
        """
        self._logger.info("[PROGRESSIVE_DIFFICULTY] Shutting down progressive difficulty system")

        # Unsubscribe from events
        for subscription_id in self._subscription_ids:
            self._event_bus.unsubscribe(subscription_id)
        self._subscription_ids.clear()

    def save_state(self, game_state: GameState) -> Dict[str, Any]:
        """Save plugin state for persistence.

        Args:
            game_state: Current game state

        Returns:
            Dictionary containing state data
        """
        return {
            "metrics": self._metrics.to_dict(),
            "config": self._config.to_dict(),
            "current_difficulty_level": self._current_difficulty_level,
            "difficulty_multiplier": self._difficulty_multiplier,
            "recent_incidents": self._recent_incidents,
            "last_metrics_update": self._last_metrics_update,
        }

    def load_state(self, game_state: GameState, state_data: Dict[str, Any]) -> None:
        """Load plugin state from saved data.

        Args:
            game_state: Current game state
            state_data: Previously saved state data
        """
        self._metrics = DifficultyMetrics.from_dict(state_data.get("metrics", {}))
        self._config = DifficultyScalingConfig.from_dict(state_data.get("config", {}))
        self._current_difficulty_level = state_data.get("current_difficulty_level", 1)
        self._difficulty_multiplier = state_data.get("difficulty_multiplier", 1.0)
        self._recent_incidents = state_data.get("recent_incidents", [])
        self._last_metrics_update = state_data.get("last_metrics_update", time.time())

        self._logger.info(f"[PROGRESSIVE_DIFFICULTY] Loaded state with difficulty level {self._current_difficulty_level}")

    def get_current_difficulty_level(self) -> int:
        """Get the current difficulty level.

        Returns:
            Current difficulty level (1-5)
        """
        return self._current_difficulty_level

    def get_difficulty_multiplier(self) -> float:
        """Get the current difficulty multiplier.

        Returns:
            Current difficulty multiplier
        """
        return self._difficulty_multiplier

    def get_difficulty_info(self) -> Dict[str, Any]:
        """Get comprehensive difficulty information.

        Returns:
            Dictionary with difficulty information
        """
        milestone = self._config.difficulty_milestones.get(self._current_difficulty_level, {})

        return {
            "current_level": self._current_difficulty_level,
            "difficulty_multiplier": self._difficulty_multiplier,
            "milestone_name": milestone.get("name", "Unknown"),
            "milestone_description": milestone.get("description", ""),
            "metrics": self._metrics.to_dict(),
            "next_milestone_requirements": self._get_next_milestone_requirements(),
        }

    def _load_config(self, game_state: GameState) -> None:
        """Load configuration from game config.

        Args:
            game_state: Current game state
        """
        try:
            # Load from game_config.json
            config_data = game_state._json_loader.load_data("game_config.json")
            difficulty_config = config_data.get("progressive_difficulty", {})

            self._config = DifficultyScalingConfig.from_dict(difficulty_config)

            self._logger.info("[PROGRESSIVE_DIFFICULTY] Loaded configuration from game_config.json")

        except Exception as e:
            self._logger.warning(f"[PROGRESSIVE_DIFFICULTY] Failed to load config, using defaults: {e}")
            # Keep default config

    def _update_metrics(self, game_state: GameState) -> None:
        """Update difficulty metrics from game state.

        Args:
            game_state: Current game state
        """
        metrics = game_state.metrics

        # Update overall metrics
        self._metrics.average_resolution_time = metrics.average_resolution_time
        self._metrics.sla_compliance_rate = metrics.sla_compliance_rate
        self._metrics.specialist_utilization_rate = metrics.specialist_utilization_rate
        self._metrics.assignment_success_rate = metrics.assignment_success_rate
        self._metrics.total_incidents_handled = metrics.total_incidents_handled
        self._metrics.total_money_earned = game_state.total_money_earned

        # Calculate average specialist level
        if game_state.specialists:
            self._metrics.average_specialist_level = sum(s.level for s in game_state.specialists) / len(game_state.specialists)
        else:
            self._metrics.average_specialist_level = 1.0

        # Calculate game time in hours
        game_time_seconds = game_state.current_time - game_state.game_start_time
        self._metrics.game_time_hours = game_time_seconds / 3600.0

        # Update recent performance metrics
        self._update_recent_metrics()

    def _update_recent_metrics(self) -> None:
        """Update recent performance metrics from recent incidents."""
        if not self._recent_incidents:
            return

        # Calculate recent success rate
        successful_incidents = sum(1 for inc in self._recent_incidents if inc.get("success", False))
        self._metrics.recent_success_rate = (successful_incidents / len(self._recent_incidents)) * 100.0

        # Calculate recent average resolution time
        resolution_times = [inc.get("resolution_time", 0) for inc in self._recent_incidents if inc.get("resolution_time", 0) > 0]
        if resolution_times:
            self._metrics.recent_average_resolution_time = sum(resolution_times) / len(resolution_times)

        # Calculate recent SLA compliance
        sla_compliant = sum(1 for inc in self._recent_incidents if inc.get("sla_compliant", False))
        self._metrics.recent_sla_compliance = (sla_compliant / len(self._recent_incidents)) * 100.0

    def _calculate_difficulty_level(self, game_state: GameState) -> None:
        """Calculate the current difficulty level based on performance and progression.

        Args:
            game_state: Current game state
        """
        # Base difficulty from performance
        performance_score = self._calculate_performance_score()

        # Progression bonus
        progression_score = self._calculate_progression_score(game_state)

        # Combine scores
        total_score = performance_score + progression_score

        # Determine difficulty level (1-5)
        new_difficulty_level = min(5, max(1, int(total_score / 20) + 1))  # Scale roughly every 20 points

        # Update difficulty level if changed
        if new_difficulty_level != self._current_difficulty_level:
            self._logger.info(
                f"[PROGRESSIVE_DIFFICULTY] Difficulty level changed: {self._current_difficulty_level} → {new_difficulty_level} "
                f"(performance: {performance_score:.1f}, progression: {progression_score:.1f})"
            )
            self._current_difficulty_level = new_difficulty_level

            # Emit difficulty level changed event
            self._event_bus.publish("difficulty_level_changed", {
                "old_level": self._current_difficulty_level,
                "new_level": new_difficulty_level,
                "performance_score": performance_score,
                "progression_score": progression_score,
            })

        # Calculate difficulty multiplier
        self._difficulty_multiplier = min(
            self._config.max_difficulty_multiplier,
            self._config.base_difficulty_multiplier + (self._current_difficulty_level - 1) * 0.3
        )

    def _calculate_performance_score(self) -> float:
        """Calculate performance score based on recent metrics.

        Returns:
            Performance score (0-100)
        """
        score = 0.0

        # SLA compliance (40% weight)
        sla_score = min(100.0, self._metrics.recent_sla_compliance)
        score += sla_score * 0.4

        # Success rate (35% weight)
        success_score = min(100.0, self._metrics.recent_success_rate)
        score += success_score * 0.35

        # Assignment success rate (15% weight)
        assignment_score = min(100.0, self._metrics.assignment_success_rate * 100.0)
        score += assignment_score * 0.15

        # Utilization rate (10% weight) - higher utilization indicates better performance
        utilization_score = min(100.0, self._metrics.specialist_utilization_rate * 100.0)
        score += utilization_score * 0.1

        return score

    def _calculate_progression_score(self, game_state: GameState) -> float:
        """Calculate progression score based on game advancement.

        Args:
            game_state: Current game state

        Returns:
            Progression score (0-100)
        """
        score = 0.0

        # Incidents handled (30% weight) - more experience = higher difficulty
        incident_score = min(100.0, self._metrics.total_incidents_handled / 10.0)  # 1000 incidents = max score
        score += incident_score * 0.3

        # Average specialist level (25% weight)
        level_score = min(100.0, (self._metrics.average_specialist_level - 1) * 10.0)  # Level 11 = max score
        score += level_score * 0.25

        # Money earned (25% weight) - financial success indicates capability
        money_score = min(100.0, game_state.total_money_earned / 100000.0)  # $100k = max score
        score += money_score * 0.25

        # Game time (20% weight) - longer play indicates experience
        time_score = min(100.0, self._metrics.game_time_hours / 50.0)  # 50 hours = max score
        score += time_score * 0.2

        return score

    def _apply_difficulty_scaling(self, game_state: GameState) -> None:
        """Apply difficulty scaling to game systems.

        Args:
            game_state: Current game state
        """
        # Modify incident generation parameters
        self._scale_incident_generation(game_state)

        # Apply scaling to existing incidents if needed
        self._scale_existing_incidents(game_state)

    def _scale_incident_generation(self, game_state: GameState) -> None:
        """Scale incident generation parameters based on difficulty.

        Args:
            game_state: Current game state
        """
        # Adjust difficulty weights to favor higher difficulties
        difficulty_weights = game_state._incident_generator._config.difficulty_weights.copy()

        # Shift weight towards higher difficulties based on current level
        level_shift = (self._current_difficulty_level - 1) * 0.1  # 10% shift per level

        for difficulty in range(1, 6):
            if difficulty <= self._current_difficulty_level:
                # Increase weight for difficulties at or below current level
                difficulty_weights[str(difficulty)] = difficulty_weights.get(str(difficulty), 0.2) * (1.0 + level_shift)
            else:
                # Decrease weight for difficulties above current level
                difficulty_weights[str(difficulty)] = difficulty_weights.get(str(difficulty), 0.2) * (1.0 - level_shift * 0.5)

        # Normalize weights
        total_weight = sum(difficulty_weights.values())
        for difficulty in difficulty_weights:
            difficulty_weights[difficulty] /= total_weight

        # Update generator config
        game_state._incident_generator._config.difficulty_weights = difficulty_weights

    def _scale_existing_incidents(self, game_state: GameState) -> None:
        """Apply difficulty scaling to existing unassigned incidents.

        Args:
            game_state: Current game state
        """
        for incident in game_state.incidents:
            if incident.status == "unassigned":
                # Scale incident parameters based on difficulty multiplier
                scaling_factor = self._difficulty_multiplier

                # Increase base reward
                reward_increase = self._config.reward_multiplier_per_level * (self._current_difficulty_level - 1)
                incident.base_reward = int(incident.base_reward * (1.0 + reward_increase))

                # Decrease SLA time (increase pressure)
                sla_reduction = self._config.sla_reduction_per_level * (self._current_difficulty_level - 1)
                incident.sla_seconds = int(incident.sla_seconds * (1.0 - sla_reduction))

                # Ensure minimum SLA time
                incident.sla_seconds = max(60, incident.sla_seconds)  # Minimum 1 minute

    def _get_next_milestone_requirements(self) -> Dict[str, Any]:
        """Get requirements for next difficulty milestone.

        Returns:
            Dictionary with next milestone requirements
        """
        next_level = min(5, self._current_difficulty_level + 1)

        if next_level == self._current_difficulty_level:
            return {"message": "Maximum difficulty reached"}

        # Calculate approximate requirements for next level
        required_score = next_level * 20  # Roughly 20 points per level
        current_score = self._calculate_performance_score() + self._calculate_progression_score(None)

        return {
            "next_level": next_level,
            "milestone_name": self._config.difficulty_milestones.get(next_level, {}).get("name", "Unknown"),
            "required_score": required_score,
            "current_score": current_score,
            "progress_percentage": min(100.0, (current_score / required_score) * 100.0),
        }

    def _on_incident_completed(self, event: Event) -> None:
        """Handle incident completion event.

        Args:
            event: Incident completion event
        """
        incident_data = {
            "incident_id": event.data.get("incident_id"),
            "success": True,
            "resolution_time": event.data.get("resolution_time", 0),
            "sla_compliant": event.data.get("sla_compliant", True),
            "timestamp": time.time(),
        }

        self._recent_incidents.append(incident_data)
        if len(self._recent_incidents) > self._max_recent_incidents:
            self._recent_incidents.pop(0)

    def _on_incident_failed(self, event: Event) -> None:
        """Handle incident failure event.

        Args:
            event: Incident failure event
        """
        incident_data = {
            "incident_id": event.data.get("incident_id"),
            "success": False,
            "resolution_time": 0,
            "sla_compliant": False,
            "timestamp": time.time(),
        }

        self._recent_incidents.append(incident_data)
        if len(self._recent_incidents) > self._max_recent_incidents:
            self._recent_incidents.pop(0)

    def _on_incident_generated(self, event: Event) -> None:
        """Handle incident generation event.

        Args:
            event: Incident generation event
        """
        # Could apply immediate scaling to newly generated incidents
        pass

    def _on_game_loaded(self, event: Event) -> None:
        """Handle game loaded event.

        Args:
            event: Game loaded event
        """
        # Recalculate difficulty level after loading
        self._calculate_difficulty_level(event.data.get("game_state"))

    def reset_difficulty(self) -> None:
        """Reset difficulty to base level (for prestige system)."""
        self._current_difficulty_level = 1
        self._difficulty_multiplier = self._config.base_difficulty_multiplier
        self._recent_incidents.clear()

        self._logger.info("[PROGRESSIVE_DIFFICULTY] Difficulty reset to base level")

        # Emit difficulty reset event
        self._event_bus.publish("difficulty_reset", {
            "new_level": self._current_difficulty_level,
            "new_multiplier": self._difficulty_multiplier,
        })