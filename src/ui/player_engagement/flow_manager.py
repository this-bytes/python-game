"""FlowManager - dynamic difficulty and pacing helpers.

Provides a simple API to suggest adjustments to incident spawn rate or
automation assistance based on player performance.
"""
from __future__ import annotations

from typing import Any


class FlowManager:
    """Manage pacing and dynamic difficulty suggestions.

    Contains only pure, testable logic. It does not modify game state directly.
    """

    def __init__(self, game_state: Any) -> None:
        self.game_state = game_state
        self._difficulty_modifier = 1.0

    def update(self, delta_time: float) -> None:
        # Basic heuristic: if player success rate is high, increase modifier
        successes = getattr(self.game_state, "recent_successes", 0)
        failures = getattr(self.game_state, "recent_failures", 0)
        total = max(1, successes + failures)
        success_rate = successes / total
        if success_rate > 0.8:
            self._difficulty_modifier = min(2.0, self._difficulty_modifier + 0.01)
        elif success_rate < 0.4:
            self._difficulty_modifier = max(0.5, self._difficulty_modifier - 0.01)

    def get_difficulty_modifier(self) -> float:
        return self._difficulty_modifier
