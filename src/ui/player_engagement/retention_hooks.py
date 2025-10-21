"""Retention hooks - optional engagement/telemetry helpers.

Keep these small and non-invasive. They expose hooks to emit events or
measure micro-engagement metrics without enforcing addictive mechanics.
"""
from __future__ import annotations

from typing import Any
import logging

logger = logging.getLogger("retention")


class RetentionHooks:
    """Lightweight API for telemetry or soft engagement nudges.

    These hooks are opt-in and should not change game mechanics.
    """

    def __init__(self, game_state: Any) -> None:
        self.game_state = game_state

    def record_event(self, name: str, data: dict | None = None) -> None:
        logger.debug("Retention event %s %s", name, data)

    def suggest_nudge(self) -> dict:
        # Return a minimal suggestion if player is idle
        idle_seconds = getattr(self.game_state, "idle_seconds", 0)
        if idle_seconds > 30:
            return {"type": "suggestion", "text": "Try assigning a specialist to the queue"}
        return {}
