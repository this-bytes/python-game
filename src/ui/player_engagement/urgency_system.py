"""UrgencySystem - visual indicators for time-sensitive game objects.

This module provides detection for incidents and specialists that require
immediate attention and exposes a small render API the GameUI can call.
"""
from __future__ import annotations

from typing import Any
import time


class UrgencySystem:
    """Detects urgent incidents and provides render data.

    This class intentionally doesn't draw complex animations. It exposes
    `get_urgent_items` for unit tests and a `render(surface)` method for the
    real UI.
    """

    def __init__(self, game_state: Any) -> None:
        self.game_state = game_state
        self._last_check = time.time()

    def update(self, delta_time: float) -> None:
        # For now we only update a timestamp; logic can be expanded later.
        self._last_check = time.time()

    def get_urgent_items(self) -> list[dict]:
        """Return a list of urgent items with minimal metadata.

        Each item is a dict: {"type": "incident"|"specialist", "id": str, "urgency": float}
        """
        urgent = []
        # Defensive: game_state may be None in tests
        try:
            if not hasattr(self.game_state, "incidents"):
                return urgent

            for inc in getattr(self.game_state, "incidents", []):
                sla_pct = getattr(inc, "sla_percent", 1.0)
                if sla_pct >= 0.8:
                    urgent.append({"type": "incident", "id": getattr(inc, "id", ""), "urgency": sla_pct})

            for spec in getattr(self.game_state, "specialists", []):
                burnout = getattr(spec, "burnout", 0)
                if burnout >= 80:
                    urgent.append({"type": "specialist", "id": getattr(spec, "id", ""), "urgency": burnout / 100.0})
        except Exception:
            # Keep UI resilient; don't propagate exceptions from game logic
            return urgent

        return urgent

    def render(self, surface) -> None:
        """Render urgency indicators on the provided surface.

        The rendering is intentionally minimal here; designers should replace
        with polished visuals (pulsing borders, countdown timers, icons).
        """
        # Implementation is UI-specific. Keep placeholder no-op to avoid import-heavy pygame in tests.
        return None

    def handle_event(self, event: Any) -> None:
        # Placeholder for click-to-prioritize handling
        return None
