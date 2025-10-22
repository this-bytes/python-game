"""Incident dispatch plugin for managing incident generation and assignment.

This plugin integrates the incident generation and assignment systems into the game,
handling the creation, assignment, and resolution of incidents based on game state
and client threat landscapes.
"""

import logging
from typing import Optional, Dict, Any, List

from src.core.game_system import GameSystem
from src.core.event_bus import get_event_bus, Event
from src.core.incident_generator import IncidentGenerator
from src.core.incident_dispatch_system import IncidentDispatchSystem, ResolutionResult
from src.models.incident import Incident
from src.models.specialist import Specialist
from src.models.client import Client
from src.utils.logger import GameLogger


class IncidentDispatchPlugin(GameSystem):
    """Plugin for managing incident generation, assignment, and resolution."""
    
    def __init__(self):
        """Initialize the incident dispatch plugin."""
        super().__init__()
        self._logger = GameLogger("incident_dispatch_plugin")
        self._event_bus = get_event_bus()
        self._subscription_ids: List[str] = []
        
        # Systems
        self._incident_generator = IncidentGenerator(self._logger)
        self._dispatch_system = IncidentDispatchSystem(self._logger)
        
        # State tracking
        self._incidents_this_turn: List[Incident] = []
        self._pending_assignments: List[tuple] = []  # (incident, specialist) pairs
    
    def get_name(self) -> str:
        """Get plugin name."""
        return "IncidentDispatchPlugin"
    
    def get_feature_id(self) -> str:
        """Get feature flag ID."""
        return "incident_dispatch_system"
    
    def initialize(self, game_state) -> None:
        """Initialize incident dispatch plugin."""
        self._subscription_ids = [
            self._event_bus.subscribe("incident_generated", self._on_incident_generated),
            self._event_bus.subscribe("incident_assigned", self._on_incident_assigned),
            self._event_bus.subscribe("incident_resolved", self._on_incident_resolved),
            self._event_bus.subscribe("phase_changed", self._on_phase_changed),
        ]
        self._logger.logger.info("[INCIDENT_DISPATCH_PLUGIN] Initialized")
    
    def update(self, game_state, delta_time: float) -> None:
        """Update incident dispatch system each frame."""
        if not hasattr(game_state, 'clients') or not game_state.clients:
            return
        
        # Generate incidents for each active client
        for client in game_state.clients:
            if not client.is_active:
                continue
            
            # Check if incident should be generated
            active_incident_count = len(self._dispatch_system.get_active_incidents())
            if self._incident_generator.should_generate_incident(client, delta_time, active_incident_count):
                incident = self._incident_generator.generate_incident(client)
                self._dispatch_system.add_incident(incident)
                self._incidents_this_turn.append(incident)
                
                # Emit event for UI and other systems
                self._event_bus.publish("incident_generated", {
                    "incident_id": incident.id,
                    "incident_type": incident.incident_type,
                    "client_id": incident.client_id,
                    "difficulty": incident.difficulty,
                    "specialty_required": incident.specialty_required,
                    "sla_seconds": incident.sla_seconds,
                })
        
        # Check for overdue incidents and fail them
        overdue_incidents = self._dispatch_system.get_overdue_incidents()
        for incident in overdue_incidents:
            if incident.is_active():
                # Get specialist who was assigned
                specialist_id = incident.assigned_specialist_id
                if specialist_id and hasattr(game_state, 'specialists'):
                    specialist = next(
                        (s for s in game_state.specialists if s.id == specialist_id),
                        None
                    )
                    if specialist:
                        # Fail the incident
                        result = self._dispatch_system.resolve_incident(
                            incident,
                            specialist,
                            success=False,
                            time_taken=incident.get_time_remaining() * -1  # Time overdue
                        )
                        self._emit_resolution_event(result)
    
    def shutdown(self, game_state) -> None:
        """Shutdown incident dispatch plugin."""
        for subscription_id in self._subscription_ids:
            self._event_bus.unsubscribe(subscription_id)
        self._subscription_ids.clear()
        self._logger.logger.info("[INCIDENT_DISPATCH_PLUGIN] Shutdown")
    
    def save_state(self, game_state) -> Dict[str, Any]:
        """Save plugin state."""
        return {
            "incidents": {
                incident_id: self._serialize_incident(incident)
                for incident_id, incident in self._dispatch_system._incidents.items()
            },
            "active_assignments": self._dispatch_system._active_assignments.copy(),
        }
    
    def load_state(self, game_state, state_data: Dict[str, Any]) -> None:
        """Load plugin state."""
        # Restore incidents
        for incident_id, incident_data in state_data.get("incidents", {}).items():
            incident = self._deserialize_incident(incident_data)
            self._dispatch_system._incidents[incident_id] = incident
        
        # Restore active assignments
        self._dispatch_system._active_assignments = state_data.get("active_assignments", {})
        
        self._logger.logger.info(
            f"[INCIDENT_DISPATCH_PLUGIN] Loaded {len(self._dispatch_system._incidents)} incidents"
        )
    
    def assign_incident(
        self,
        incident: Incident,
        specialist: Specialist
    ) -> bool:
        """Public method to assign an incident to a specialist.
        
        Args:
            incident: Incident to assign
            specialist: Specialist to assign to
            
        Returns:
            True if assignment successful, False otherwise
        """
        result = self._dispatch_system.assign_incident(incident, specialist)
        
        if result.success:
            self._event_bus.publish("incident_assigned", {
                "incident_id": incident.id,
                "specialist_id": specialist.id,
                "specialist_name": specialist.name,
                "incident_type": incident.incident_type,
            })
        
        return result.success
    
    def resolve_incident(
        self,
        incident: Incident,
        specialist: Specialist,
        success: bool,
        time_taken: Optional[float] = None
    ) -> ResolutionResult:
        """Public method to resolve an incident.
        
        Args:
            incident: Incident to resolve
            specialist: Specialist who resolved it
            success: Whether resolution was successful
            time_taken: Optional time taken to resolve
            
        Returns:
            ResolutionResult with outcome details
        """
        result = self._dispatch_system.resolve_incident(incident, specialist, success, time_taken)
        self._emit_resolution_event(result)
        return result
    
    def get_pending_incidents(self) -> List[Incident]:
        """Get all pending incidents waiting for assignment."""
        return self._dispatch_system.get_pending_incidents()
    
    def get_active_incidents(self) -> List[Incident]:
        """Get all active incidents."""
        return self._dispatch_system.get_active_incidents()
    
    def get_incidents_for_client(self, client_id: str) -> List[Incident]:
        """Get all incidents for a client."""
        return self._dispatch_system.get_incidents_for_client(client_id)
    
    def get_best_specialist_for_incident(
        self,
        incident: Incident,
        available_specialists: List[Specialist]
    ) -> Optional[Specialist]:
        """Find the best specialist for an incident."""
        return self._dispatch_system.find_best_specialist(incident, available_specialists)
    
    def get_dispatch_stats(self) -> Dict[str, Any]:
        """Get dispatch system statistics."""
        return self._dispatch_system.get_dispatch_stats()
    
    # Event handlers
    def _on_incident_generated(self, event: Event) -> None:
        """Handle incident generated event."""
        # Already tracked in update(), this is for other systems to react
        pass
    
    def _on_incident_assigned(self, event: Event) -> None:
        """Handle incident assigned event."""
        pass
    
    def _on_incident_resolved(self, event: Event) -> None:
        """Handle incident resolved event."""
        pass
    
    def _on_phase_changed(self, event: Event) -> None:
        """Handle phase change event."""
        phase = event.data.get("phase")
        
        # Clear resolved incidents at start of day (morning phase)
        if phase == "morning":
            cleared = self._dispatch_system.clear_resolved_incidents()
            if cleared > 0:
                self._logger.logger.debug(f"[INCIDENT_DISPATCH_PLUGIN] Cleared {cleared} incidents at phase start")
    
    def _emit_resolution_event(self, result: ResolutionResult) -> None:
        """Emit incident resolved event."""
        self._event_bus.publish("incident_resolved", {
            "incident_id": result.incident_id,
            "specialist_id": result.specialist_id,
            "client_id": result.client_id,
            "success": result.success,
            "sla_met": result.sla_met,
            "time_taken": result.time_taken,
            "xp_earned": result.xp_earned,
            "reward_earned": result.reward_earned,
        })
    
    @staticmethod
    def _serialize_incident(incident: Incident) -> Dict[str, Any]:
        """Serialize incident to dictionary."""
        return {
            "id": incident.id,
            "incident_type": incident.incident_type,
            "specialty_required": incident.specialty_required,
            "difficulty": incident.difficulty,
            "sla_seconds": incident.sla_seconds,
            "base_reward": incident.base_reward,
            "xp_reward": incident.xp_reward,
            "client_id": incident.client_id,
            "description": incident.description,
            "status": incident.status,
            "assigned_specialist_id": incident.assigned_specialist_id,
            "spawn_time": incident.spawn_time,
            "assignment_time": incident.assignment_time,
            "completion_time": incident.completion_time,
            "sla_deadline": incident.sla_deadline,
        }
    
    @staticmethod
    def _deserialize_incident(data: Dict[str, Any]) -> Incident:
        """Deserialize incident from dictionary."""
        incident = Incident(
            id=data["id"],
            incident_type=data["incident_type"],
            specialty_required=data["specialty_required"],
            difficulty=data["difficulty"],
            sla_seconds=data["sla_seconds"],
            base_reward=data["base_reward"],
            xp_reward=data["xp_reward"],
            client_id=data["client_id"],
            description=data.get("description", ""),
            status=data.get("status", "pending"),
            assigned_specialist_id=data.get("assigned_specialist_id"),
            spawn_time=data.get("spawn_time", 0),
            assignment_time=data.get("assignment_time"),
            completion_time=data.get("completion_time"),
            sla_deadline=data.get("sla_deadline"),
        )
        return incident
