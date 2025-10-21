from __future__ import annotations

"""EngagementManager coordinates urgency, feedback, progression and flow.

This module provides a single, well-typed EngagementManager that wraps
subsystems: UrgencySystem, FeedbackEngine, ProgressionDisplay and
FlowManager. It is defensive and suitable for integration into the
existing `GameUI` class.
"""

from typing import Tuple, Any
import logging

from src.models.game_state import GameState
from .urgency_system import UrgencySystem
from .feedback_engine import FeedbackEngine
from .progression_display import ProgressionDisplay
from .flow_manager import FlowManager


logger = logging.getLogger("player_engagement")


class EngagementManager:
    """Single entrypoint for player engagement subsystems.

    Args:
        screen_size: (width, height) tuple used for layout if needed
        game_state: reference to GameState (read-only for UI)
    """

    def __init__(self, screen_size: Tuple[int, int], game_state: GameState):
        self.screen_size = screen_size
        self.game_state = game_state

        # Initialize subsystems. Subsystems accept game_state for read-only
        # access to necessary metrics.
        self.urgency = UrgencySystem(game_state)
        self.feedback = FeedbackEngine(game_state)
        self.progression = ProgressionDisplay(game_state)
        self.flow = FlowManager(game_state)

        logger.info("EngagementManager initialized")

    def update(self, delta_time: float) -> None:
        """Update all subsystems; resilient to individual subsystem failures."""
        for subsystem in (self.urgency, self.feedback, self.progression, self.flow):
            try:
                subsystem.update(delta_time)
            except Exception:
                logger.exception("Engagement subsystem update failed")

    def render(self, surface: Any) -> None:
        """Render engagement overlays in priority order."""
        for subsystem in (self.urgency, self.progression, self.feedback):
            try:
                subsystem.render(surface)
            except Exception:
                logger.exception("Engagement subsystem render failed")

    def handle_event(self, event: Any) -> None:
        """Pass input events to subsystems that need them."""
        for subsystem in (self.feedback, self.urgency):
            try:
                subsystem.handle_event(event)
            except Exception:
                logger.debug("Engagement subsystem event handler failed")

    def notify_assignment(self, specialist_id: str, incident_id: str, success: bool) -> None:
        """Notify subsystems about assignment results.

        FeedbackEngine will display success/failure micro-feedback.
        """
        try:
            if success:
                self.feedback.on_success_assignment(specialist_id, incident_id)
            else:
                self.feedback.on_failed_assignment(specialist_id, incident_id)
        except Exception:
            logger.exception("Failed to notify feedback engine of assignment")
