"""ProgressionDisplay - shows XP, money, levels and micro-progress visuals.

This component is responsible for rendering prominent progression cues like
money, XP, and level-up notifications. Keep logic minimal and data-driven.
"""
from __future__ import annotations

from typing import Any


class ProgressionDisplay:
    """Display and manage progression-related visual state.

    Methods are split between `update` (state) and `render` (visuals).
    """

    def __init__(self, game_state: Any) -> None:
        self.game_state = game_state
        self._last_money = None

    def update(self, delta_time: float) -> None:
        # Track changes to money/xp to trigger animations
        try:
            money = getattr(self.game_state, "money", None)
            if money != self._last_money:
                self._last_money = money
        except Exception:
            return None

    def render(self, surface) -> None:
        # Minimal placeholder; GameUI should draw actual fonts/animations
        return None
