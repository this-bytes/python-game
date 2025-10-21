"""FeedbackEngine - provides satisfying micro-feedback for actions.

Contains small utilities to queue visual/sound feedback and render them.
"""
from __future__ import annotations

from typing import Any
import time


class FeedbackEngine:
    """Queue and render short-lived feedback effects.

    Effects are lightweight dictionaries. The engine exposes `push_effect`
    to enqueue events and `render` to draw them.
    """

    def __init__(self, game_state: Any) -> None:
        self.game_state = game_state
        self._effects: list[dict] = []

    def update(self, delta_time: float) -> None:
        now = time.time()
        # Expire effects older than 1.5s
        self._effects = [e for e in self._effects if now - e.get("ts", now) < 1.5]

    def push_effect(self, kind: str, payload: dict | None = None) -> None:
        """Add a feedback effect.

        kind: e.g. 'assign_success', 'assign_fail', 'level_up', 'money_gain'
        payload: optional metadata used by renderers
        """
        self._effects.append({"kind": kind, "payload": payload or {}, "ts": time.time()})

    def render(self, surface) -> None:
        # Real rendering happens in GameUI; here we simply maintain state.
        return None

    def handle_event(self, event: Any) -> None:
        # Accept events from UI (e.g., clicks) to generate immediate feedback
        return None

    def on_success_assignment(self, specialist_id: str, incident_id: str) -> None:
        """Generate micro-feedback for a successful assignment."""
        self.push_effect("assign_success", {"specialist_id": specialist_id, "incident_id": incident_id})

    def on_failed_assignment(self, specialist_id: str, incident_id: str) -> None:
        """Generate micro-feedback for a failed assignment."""
        self.push_effect("assign_fail", {"specialist_id": specialist_id, "incident_id": incident_id})
