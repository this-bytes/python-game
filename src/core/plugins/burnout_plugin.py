"""BurnoutPlugin - Specialist Psychological Management System.

This plugin manages specialist burnout, a critical factor affecting performance.
It listens to game events and adjusts specialist burnout levels based on their
activities, such as completing incidents or taking rests. All configuration
is driven by the `data/burnout.json` file.
"""

from typing import Dict, Any, List, Tuple, Optional
from enum import Enum

from src.core.game_system import GameSystem
from src.core.event_bus import get_event_bus, Event
from src.models.game_state import GameState
from src.models.specialist import Specialist
from src.utils.json_loader import JSONLoader
from src.ui.ui_provider import UIProvider, UISummaryItem, UISectionItem, UIPanelSection, UIAction

class BurnoutTier(Enum):
    """Burnout severity levels."""
    FRESH = "fresh"
    STRESSED = "stressed"
    EXHAUSTED = "exhausted"
    CRITICAL = "critical"
    BROKEN = "broken"

class BurnoutPlugin(GameSystem, UIProvider):
    """A self-contained system for managing specialist burnout, with UI hooks."""

    def __init__(self):
        super().__init__()
        self._event_bus = get_event_bus()
        self._subscription_ids: List[str] = []
        self.config: Dict[str, Any] = {}
        self._json_loader = JSONLoader()

    def get_name(self) -> str:
        return "BurnoutPlugin"

    def get_feature_id(self) -> str:
        return "burnout_system"

    def initialize(self, game_state: GameState) -> None:
        self.config = self._json_loader.load_data("burnout.json")
        self._subscription_ids = [
            self._event_bus.subscribe("incident_completed", self._on_incident_completed),
            self._event_bus.subscribe("action:rest_specialist", self._on_rest_specialist_action),
        ]

    def update(self, game_state: GameState, delta_time: float) -> None:
        pass

    def shutdown(self, game_state: GameState) -> None:
        for subscription_id in self._subscription_ids:
            self._event_bus.unsubscribe(subscription_id)
        self._subscription_ids.clear()

    def _get_specialist(self, game_state: GameState, specialist_id: str) -> Optional[Specialist]:
        return game_state.get_specialist_by_id(specialist_id)

    # Event Handlers
    def _on_incident_completed(self, event: Event) -> None:
        game_state: GameState = event.data.get("game_state")
        if not game_state:
            return
        specialist_id = event.data.get("specialist_id")
        incident_difficulty = event.data.get("incident_difficulty", 1)
        success = event.data.get("success", True)

        specialist = self._get_specialist(game_state, specialist_id)
        if not specialist:
            return

        burnout_cost = self.config["burnout_costs"]["base_incident_cost"] + \
                       (max(0, incident_difficulty - 1) * self.config["burnout_costs"]["per_difficulty_level_cost"])
        specialist.burnout_level = min(100.0, specialist.burnout_level + burnout_cost)

        if not success:
            specialist.burnout_level = min(100.0, specialist.burnout_level + self.config["burnout_costs"]["incident_failure_cost"])

        self._event_bus.publish("burnout_updated", {"specialist_id": specialist_id, "burnout_level": specialist.burnout_level})

    def _on_rest_specialist_action(self, event: Event) -> None:
        game_state: GameState = event.data.get("game_state")
        if not game_state:
            return
        specialist_id = event.data.get("specialist_id")
        if specialist_id:
            self.take_rest_day(game_state, specialist_id)

    # Public API Methods
    def take_rest_day(self, game_state: GameState, specialist_id: str) -> Tuple[bool, str]:
        specialist = self._get_specialist(game_state, specialist_id)
        if not specialist:
            return False, "Specialist not found."

        recovery_multiplier = self.config["recovery_rates"]["rest_day_recovery_multiplier"]
        recovery_amount = specialist.burnout_level * recovery_multiplier
        specialist.burnout_level = max(0, specialist.burnout_level - recovery_amount)

        message = f"Rested. Recovered {recovery_amount:.0f}%. Burnout now: {specialist.burnout_level:.0f}%"
        self._event_bus.publish("burnout_updated", {"specialist_id": specialist_id, "burnout_level": specialist.burnout_level})
        self._event_bus.publish("notification", {"title": f"{specialist.name} Rested", "message": message})
        return True, message

    # UIProvider Interface Implementation
    def get_dashboard_summary(self, game_state: GameState) -> UISummaryItem:
        team_status = self.get_team_status(game_state)
        avg_burnout = team_status["average_burnout"]
        critical_count = team_status["critical_count"]

        color = "green"
        if avg_burnout > 50:
            color = "yellow"
        if avg_burnout > 75 or critical_count > 0:
            color = "red"

        return UISummaryItem(
            title="Team Morale",
            icon="❤️",
            lines=[
                f"Avg. Burnout: {avg_burnout:.1f}%",
                f"Critical: {critical_count}"
            ],
            accent_color=color
        )

    def get_detail_panel_data(self, game_state: GameState) -> Dict[str, Any]:
        specialist_items = []
        most_burned_out_spec = None
        max_burnout = -1

        for spec in sorted(game_state.specialists, key=lambda s: s.burnout_level, reverse=True):
            if spec.burnout_level > max_burnout:
                max_burnout = spec.burnout_level
                most_burned_out_spec = spec

            tier = self.get_burnout_tier(spec)
            item = UISectionItem(
                name=spec.name,
                details=[
                    f"Burnout: {spec.burnout_level:.1f}% ({tier.value})",
                    f"Specialty: {spec.specialty}"
                ]
            )
            specialist_items.append(item)
        
        sections = [UIPanelSection(title="Specialist Burnout Levels", items=specialist_items)]
        
        actions = []
        if most_burned_out_spec and most_burned_out_spec.burnout_level > 0:
            actions.append(UIAction(
                id="rest_specialist",
                label=f"Rest {most_burned_out_spec.name}",
                description=f"Give {most_burned_out_spec.name} a day off to recover.",
                enabled=True,
                data={"specialist_id": most_burned_out_spec.id, "game_state": game_state}
            ))

        return {
            "title": "Burnout & Morale",
            "sections": sections,
            "actions": actions
        }

    # Utility/Query Methods
    def get_burnout_tier(self, specialist: Specialist) -> BurnoutTier:
        level = specialist.burnout_level
        if level <= 20: return BurnoutTier.FRESH
        if level <= 40: return BurnoutTier.STRESSED
        if level <= 60: return BurnoutTier.EXHAUSTED
        if level <= 80: return BurnoutTier.CRITICAL
        return BurnoutTier.BROKEN

    def get_team_status(self, game_state: GameState) -> Dict:
        specialists = game_state.specialists
        if not specialists:
            return {"team_size": 0, "average_burnout": 0.0, "critical_count": 0}

        avg_burnout = sum(s.burnout_level for s in specialists) / len(specialists)
        critical_count = sum(1 for s in specialists if s.burnout_level > self.config["thresholds"]["critical"])

        return {
            "team_size": len(specialists),
            "average_burnout": round(avg_burnout, 1),
            "critical_count": critical_count,
        }
