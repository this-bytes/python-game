"""Incident dispatch plugin for managing incident assignment via the event bus."""

from typing import Dict, Any, List, Optional

from src.core.game_system import GameSystem
from src.core.event_bus import get_event_bus, Event
from src.models.game_state import GameState
from src.models.incident import Incident
from src.models.specialist import Specialist
from src.utils.logger import GameLogger
from src.ui.ui_provider import UIProvider, UISummaryItem, UISectionItem, UIPanelSection, UIAction
from src.core.incident_dispatch_system import IncidentDispatchSystem

class IncidentDispatchPlugin(GameSystem, UIProvider):
    """Plugin for managing incident assignment, driven by UI events."""
    
    def __init__(self):
        super().__init__()
        self._logger = GameLogger("incident_dispatch_plugin")
        self._event_bus = get_event_bus()
        self._subscription_ids: List[str] = []
        self._dispatch_system: Optional[IncidentDispatchSystem] = None
    
    def get_name(self) -> str:
        return "IncidentDispatchPlugin"

    def get_feature_id(self) -> str:
        """Feature flag id for this plugin."""
        return "incident_dispatch_system"

    def initialize(self, game_state: GameState) -> None:
        # Initialize the underlying dispatch system
        self._dispatch_system = IncidentDispatchSystem()

        # Subscribe to UI actions and game loop phase events
        self._subscription_ids = [
            self._event_bus.subscribe("action:assign_incident", self._on_assign_incident_action),
            self._event_bus.subscribe("day_started", self._on_day_started),
            self._event_bus.subscribe("evening_started", self._on_evening_started),
            self._event_bus.subscribe("night_started", self._on_night_started),
        ]
        self._logger.info("[IncidentDispatchPlugin] Initialized, dispatch system created and subscriptions registered.")

    def update(self, game_state: GameState, delta_time: float) -> None:
        # Incident generation and resolution is handled by other systems.
        # This plugin is now only responsible for the assignment action.
        pass

    def shutdown(self, game_state: GameState) -> None:
        for subscription_id in self._subscription_ids:
            self._event_bus.unsubscribe(subscription_id)
        self._subscription_ids.clear()

    # Event handler for the UI action
    def _on_assign_incident_action(self, event: Event) -> None:
        game_state: GameState = event.data.get("game_state")
        incident_id = event.data.get("incident_id")
        specialist_id = event.data.get("specialist_id")

        if not all([game_state, incident_id, specialist_id]):
            self._logger.warning("Assign incident action received with missing data.")
            return

        incident = game_state.get_incident_by_id(incident_id)
        specialist = game_state.get_specialist_by_id(specialist_id)

        if not incident or not specialist:
            self._logger.warning("Assign incident action failed: Incident or Specialist not found.")
            return

        # The core logic of assigning an incident.
        # Prefer using the dispatch system if available, otherwise fall back to GameState helper
        success = False
        if self._dispatch_system:
            result = self._dispatch_system.assign_incident(incident, specialist)
            success = result.success
        else:
            success = game_state.assign_incident_to_specialist(incident_id, specialist_id)
        
        if success:
            message = f"Assigned {incident.incident_type} to {specialist.name}."
            self._logger.info(message)
            self._event_bus.publish("notification", {"title": "Incident Assigned", "message": message})
        else:
            message = f"Failed to assign {incident.incident_type} to {specialist.name}."
            self._logger.warning(message)
            self._event_bus.publish("notification", {"title": "Assignment Failed", "message": message})

    # UIProvider Interface Implementation
    def get_dashboard_summary(self, game_state: GameState) -> UISummaryItem:
        pending_incidents = game_state.get_pending_incidents()
        active_incidents = [i for i in game_state.incidents if i.status == 'assigned']
        
        color = "green"
        if len(pending_incidents) > 5:
            color = "yellow"
        if len(pending_incidents) > 10:
            color = "red"

        return UISummaryItem(
            title="Incidents",
            icon="🚨",
            lines=[
                f"Pending: {len(pending_incidents)}",
                f"Active: {len(active_incidents)}"
            ],
            accent_color=color
        )

    # Plugin wrapper helpers expected by tests
    def get_best_specialist_for_incident(self, incident: Incident, specialists: List[Specialist]) -> Optional[Specialist]:
        """Expose dispatch system's specialist selection logic to tests/UI."""
        if self._dispatch_system:
            return self._dispatch_system.find_best_specialist(incident, specialists)
        # Fallback: simple heuristic
        candidates = [s for s in specialists if s.specialty == incident.specialty_required and s.assigned_incident_id is None]
        if not candidates:
            return None
        candidates.sort(key=lambda s: (-s.level, s.burnout_level))
        return candidates[0]

    def get_dispatch_stats(self) -> Dict[str, Any]:
        """Return dispatch statistics via the underlying system if present."""
        if self._dispatch_system:
            return self._dispatch_system.get_dispatch_stats()
        return {"total_incidents": 0, "pending_count": 0, "active_count": 0}

    # Simple passthroughs expected by tests
    def assign_incident(self, incident: Incident, specialist: Specialist):
        """Assign an incident via the underlying dispatch system."""
        if self._dispatch_system:
            result = self._dispatch_system.assign_incident(incident, specialist)
            # Return simple boolean for legacy callers/tests
            return bool(result.success)
        return False

    def get_pending_incidents(self) -> List[Incident]:
        """Return pending incidents either from dispatch system or game state."""
        if self._dispatch_system:
            return self._dispatch_system.get_pending_incidents()
        # Fallback to GameState helper if someone passes game_state elsewhere
        return []

    # Game loop event handlers (placeholders that integrate with dispatch system)
    def _on_day_started(self, event: Event) -> None:
        # Could trigger daily maintenance or incident generation hooks
        self._logger.debug("[IncidentDispatchPlugin] Day started event received.")

    def _on_evening_started(self, event: Event) -> None:
        # Process assigned incidents if needed (resolution step is elsewhere)
        self._logger.debug("[IncidentDispatchPlugin] Evening started event received.")

    def _on_night_started(self, event: Event) -> None:
        # Night summary / cleanup
        self._logger.debug("[IncidentDispatchPlugin] Night started event received.")

    def get_detail_panel_data(self, game_state: GameState) -> Dict[str, Any]:
        # Section for pending incidents
        incident_items = [
            UISectionItem(name=f"{i.incident_type} (Diff: {i.difficulty})", details=[f"Client: {i.client_id}", f"Required: {i.specialty_required}"])
            for i in game_state.get_pending_incidents()
        ]
        incident_section = UIPanelSection(title="Pending Incidents", items=incident_items)

        # Section for available specialists
        specialist_items = [
            UISectionItem(name=f"{s.name} (Lvl: {s.level})", details=[f"Specialty: {s.specialty}", f"Burnout: {s.burnout_level:.0f}%"])
            for s in game_state.get_available_specialists()
        ]
        specialist_section = UIPanelSection(title="Available Specialists", items=specialist_items)

        # For this refactor, we'll create a non-interactive action to prove the event loop.
        # A proper implementation would require the UI to support selecting one item from each list.
        actions = []
        best_specialist = self._find_best_specialist_for_highest_priority_incident(game_state)
        if best_specialist:
            incident, specialist = best_specialist
            actions.append(UIAction(
                id="assign_incident",
                label=f"Auto-Assign Best Match",
                description=f"Assign {incident.incident_type} to {specialist.name}",
                enabled=True,
                data={
                    "game_state": game_state,
                    "incident_id": incident.id,
                    "specialist_id": specialist.id
                }
            ))

        return {
            "title": "Incident Dispatch",
            "sections": [incident_section, specialist_section],
            "actions": actions
        }

    def _find_best_specialist_for_highest_priority_incident(self, game_state: GameState) -> Optional[tuple[Incident, Specialist]]:
        """Finds the best specialist for the highest priority (oldest) incident."""
        pending_incidents = sorted(game_state.get_pending_incidents(), key=lambda i: i.spawn_time)
        if not pending_incidents:
            return None

        incident_to_assign = pending_incidents[0]
        available_specialists = game_state.get_available_specialists()
        if not available_specialists:
            return None

        best_match = None
        highest_score = -1

        for spec in available_specialists:
            score = 0
            if spec.specialty == incident_to_assign.specialty_required:
                score += 100  # Major bonus for matching specialty
            score -= spec.burnout_level # Penalize for burnout
            score += spec.level # Bonus for level

            if score > highest_score:
                highest_score = score
                best_match = spec
        
        if best_match:
            return (incident_to_assign, best_match)
        return None