"""Team dynamics plugin for managing specialist relationships, morale, and recruitment."""

from typing import Any, Dict, List, Optional

from src.core.game_system import GameSystem
from src.core.event_bus import get_event_bus, Event
from src.models.game_state import GameState
from src.models.specialist import Specialist
from src.utils.logger import GameLogger
from src.ui.ui_provider import UIProvider, UISummaryItem, UISectionItem, UIPanelSection, UIAction

class TeamDynamicsPlugin(GameSystem, UIProvider):
    """Plugin for team dynamics, including recruitment."""

    def __init__(self):
        super().__init__()
        self._logger = GameLogger("team_dynamics_plugin")
        self._event_bus = get_event_bus()
        self._subscription_ids: List[str] = []

    def get_name(self) -> str:
        return "team_dynamics"

    def initialize(self, game_state: GameState) -> None:
        self._subscription_ids = [
            self._event_bus.subscribe("action:hire_specialist", self._on_hire_specialist_action)
        ]
        # Ensure recruitment pool is populated if empty
        if not game_state.recruitment_pool:
            self._refresh_recruitment_pool(game_state)
        self._logger.info("Team dynamics plugin initialized.")

    def update(self, game_state: GameState, delta_time: float) -> None:
        # This is where morale and relationship updates would happen periodically.
        pass

    def shutdown(self, game_state: GameState) -> None:
        for subscription_id in self._subscription_ids:
            self._event_bus.unsubscribe(subscription_id)
        self._subscription_ids.clear()

    def _on_hire_specialist_action(self, event: Event) -> None:
        game_state: GameState = event.data.get("game_state")
        candidate_data = event.data.get("candidate_data")

        if not game_state or not candidate_data:
            self._logger.warning("Hire specialist action received with missing data.")
            return

        # The hire_specialist method on GameState handles the logic
        success = game_state.hire_specialist(candidate_data)

        if success:
            message = f"Hired {candidate_data['name']} as a new {candidate_data['specialty']} specialist."
            self._logger.info(message)
            self._event_bus.publish("notification", {"title": "New Hire", "message": message})
            # Remove the hired candidate from the pool
            game_state.recruitment_pool = [c for c in game_state.recruitment_pool if c['id'] != candidate_data['id']]
            # Refresh the pool if it gets low
            if len(game_state.recruitment_pool) < 2:
                self._refresh_recruitment_pool(game_state)
        else:
            message = f"Failed to hire {candidate_data['name']}. Insufficient funds?"
            self._logger.warning(message)
            self._event_bus.publish("notification", {"title": "Hiring Failed", "message": message})

    def _refresh_recruitment_pool(self, game_state: GameState):
        """Generates a new list of candidates for hire."""
        # This is a simplified placeholder. A real implementation would be more complex.
        game_state.recruitment_pool.clear()
        from src.utils.json_loader import JSONLoader
        loader = JSONLoader()
        templates = loader.load_data("specialist_templates.json").get("specialist_archetypes", [])
        import random

        for i in range(3):
            template = random.choice(templates)
            candidate = {
                "id": f"cand_{int(game_state.current_time)}_{i}",
                "name": template["name"],
                "specialty": template["specialty"],
                "level": 1,
                "xp": 0,
                "stats": template["base_stats"],
                "status": "available",
            }
            game_state.recruitment_pool.append(candidate)
        self._logger.info(f"Refreshed recruitment pool with {len(game_state.recruitment_pool)} new candidates.")

    # UIProvider Interface Implementation
    def get_dashboard_summary(self, game_state: GameState) -> UISummaryItem:
        return UISummaryItem(
            title="Team",
            icon="👥",
            lines=[
                f"Specialists: {len(game_state.specialists)}",
                f"Available for hire: {len(game_state.recruitment_pool)}"
            ],
            accent_color="blue"
        )

    def get_detail_panel_data(self, game_state: GameState) -> Dict[str, Any]:
        candidate_items = []
        for candidate in game_state.recruitment_pool:
            candidate_items.append(UISectionItem(
                name=candidate['name'],
                details=[
                    f"Specialty: {candidate['specialty']}",
                    f"Cost: $2000" # Placeholder cost
                ],
                clickable=True,
                data=candidate
            ))

        sections = [UIPanelSection(title="Available Candidates", items=candidate_items)]

        # Create an action for each candidate
        actions = []
        for candidate in game_state.recruitment_pool:
            actions.append(UIAction(
                id="hire_specialist",
                label=f"Hire {candidate['name']}",
                enabled=game_state.current_money >= 2000, # Placeholder cost
                data={"game_state": game_state, "candidate_data": candidate}
            ))

        return {
            "title": "Recruitment & Team Management",
            "sections": sections,
            "actions": actions
        }
