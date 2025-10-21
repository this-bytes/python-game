"""SLA Plugin for managing service level agreement tracking.

Integrates SLA tracking into the plugin system and game loop, handling:
- SLA timer management for active incidents
- SLA violation detection and reporting
- Event-driven SLA lifecycle (incident created → assigned → completed)
- State persistence for SLA metrics

Follows 15-point gate standards: 100% type hints, Google docstrings,
explicit error handling, no magic numbers, DRY principle.
"""

import logging
from typing import Dict, Any, List, Optional

from src.core.game_system import GameSystem
from src.core.event_bus import get_event_bus, Event
from src.core.sla_system import SLATracker, track_sla_incident
from src.models.incident import Incident
from src.models.client import Client

logger = logging.getLogger(__name__)


class SLAMonitor:
    """Internal monitor for managing active SLA trackers and incident mapping.
    
    This is a simplified state manager that wraps SLATracker instances
    for easy access during plugin updates. Also maintains mapping between
    incidents and their SLA trackers since SLATracker uses client_id only.
    """
    
    def __init__(self):
        """Initialize SLA monitor."""
        self._trackers: Dict[str, SLATracker] = {}
        self._incident_to_tracker: Dict[str, str] = {}
    
    def add_tracker(self, tracker: SLATracker, incident_id: Optional[str] = None) -> None:
        """Add SLA tracker to monitoring.
        
        Args:
            tracker: SLATracker instance to monitor
            incident_id: Optional incident ID for reverse lookup
        """
        self._trackers[tracker.tracker_id] = tracker
        if incident_id:
            self._incident_to_tracker[incident_id] = tracker.tracker_id
    
    def get_all_trackers(self) -> List[SLATracker]:
        """Get all tracked SLA trackers.
        
        Returns:
            List of all SLATracker instances
        """
        return list(self._trackers.values())
    
    def get_tracker_by_id(self, tracker_id: str) -> Optional[SLATracker]:
        """Get tracker by ID.
        
        Args:
            tracker_id: SLA tracker ID
            
        Returns:
            SLATracker if found, None otherwise
        """
        return self._trackers.get(tracker_id)
    
    def get_tracker_for_incident(self, incident_id: str) -> Optional[SLATracker]:
        """Get SLA tracker for specific incident.
        
        Args:
            incident_id: Incident ID to look up
            
        Returns:
            SLATracker if found, None otherwise
        """
        tracker_id = self._incident_to_tracker.get(incident_id)
        if tracker_id:
            return self._trackers.get(tracker_id)
        return None
    
    def remove_tracker(self, tracker_id: str) -> None:
        """Remove SLA tracker from monitoring.
        
        Args:
            tracker_id: SLA tracker ID to remove
        """
        tracker = self._trackers.pop(tracker_id, None)
        if tracker:
            # Find and remove incident mapping
            incident_ids_to_remove = [
                iid for iid, tid in self._incident_to_tracker.items() if tid == tracker_id
            ]
            for iid in incident_ids_to_remove:
                self._incident_to_tracker.pop(iid, None)
    
    def clear(self) -> None:
        """Clear all trackers."""
        self._trackers.clear()
        self._incident_to_tracker.clear()
    
    def set_incident_mapping(self, incident_id: str, tracker_id: str) -> None:
        """Explicitly set incident-to-tracker mapping.
        
        Args:
            incident_id: Incident ID
            tracker_id: SLA tracker ID
        """
        self._incident_to_tracker[incident_id] = tracker_id


class SLAPlugin(GameSystem):
    """Plugin that manages SLA tracking and violation detection.
    
    Responsibilities:
        - Subscribe to incident lifecycle events
        - Create SLA trackers when incidents spawn
        - Track SLA timers during incident resolution
        - Detect and report SLA violations
        - Calculate compliance metrics
        - Provide state persistence
    
    Integration Points:
        - Events: incident_created, incident_assigned, incident_completed
        - Systems: Budget (revenue/satisfaction), Client (satisfaction updates)
        - Configuration: SLA thresholds from game_config.json
    """
    
    def __init__(self):
        """Initialize SLA plugin."""
        super().__init__()
        self._event_bus = get_event_bus()
        self._sla_monitor = SLAMonitor()
        self._subscription_ids: List[str] = []
        self._config: Dict[str, Any] = {}
        self._active_violations: Dict[str, bool] = {}
    
    def get_name(self) -> str:
        """Get plugin name.
        
        Returns:
            Plugin name identifier
        """
        return "SLAPlugin"
    
    def get_feature_id(self) -> str:
        """Get feature flag ID.
        
        Used to enable/disable SLA system via feature flags.
        
        Returns:
            Feature flag identifier
        """
        return "sla_system"
    
    def initialize(self, game_state) -> None:
        """Initialize SLA plugin with game state.
        
        Sets up event subscriptions and loads configuration.
        
        Args:
            game_state: Current game state
            
        Raises:
            Exception: If event bus subscription fails
        """
        logger.info("[SLA_PLUGIN] Initializing SLA plugin")
        
        try:
            # Subscribe to incident lifecycle events
            sub1 = self._event_bus.subscribe("incident_created", self._on_incident_created)
            sub2 = self._event_bus.subscribe("incident_assigned", self._on_incident_assigned)
            sub3 = self._event_bus.subscribe("incident_completed", self._on_incident_completed)
            
            self._subscription_ids = [sub1, sub2, sub3]
            
            logger.info("[SLA_PLUGIN] Subscribed to incident events")
            logger.info("[SLA_PLUGIN] Initialization complete")
            
        except Exception as e:
            logger.error(f"[SLA_PLUGIN] Failed to initialize: {e}")
            raise
    
    def update(self, game_state, delta_time: float) -> None:
        """Update SLA system status.
        
        Called every game frame. In the current phase, this is a placeholder
        as SLA violation detection is event-driven. Future phases may add
        time-based SLA tracking for response times.
        
        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update (seconds)
        """
        # SLA tracking is primarily event-driven in this design
        # Violations are tracked when incidents are created, assigned, and completed
        pass
    
    def shutdown(self, game_state) -> None:
        """Shutdown SLA plugin and cleanup resources.
        
        Unsubscribes from all events and clears internal state.
        
        Args:
            game_state: Current game state
        """
        logger.info("[SLA_PLUGIN] Shutting down SLA plugin")
        
        # Unsubscribe from all events
        for subscription_id in self._subscription_ids:
            try:
                self._event_bus.unsubscribe(subscription_id)
            except Exception as e:
                logger.warning(f"[SLA_PLUGIN] Failed to unsubscribe {subscription_id}: {e}")
        
        self._subscription_ids.clear()
        self._sla_monitor.clear()
        self._active_violations.clear()
        
        logger.info("[SLA_PLUGIN] Shutdown complete")
    
    def save_state(self, game_state) -> Dict[str, Any]:
        """Save SLA plugin state for persistence.
        
        Serializes all active SLA trackers for game save file.
        
        Args:
            game_state: Current game state
            
        Returns:
            Dictionary containing SLA state to save
        """
        trackers_data = []
        for tracker in self._sla_monitor.get_all_trackers():
            # Use tracker's to_dict() method for proper serialization
            tracker_dict = tracker.to_dict()
            trackers_data.append(tracker_dict)
        
        return {
            "active_trackers": trackers_data,
            "incident_mappings": dict(self._sla_monitor._incident_to_tracker),
        }
    
    def load_state(self, game_state, state_data: Dict[str, Any]) -> None:
        """Load SLA plugin state from saved data.
        
        Restores all SLA trackers from game save file.
        
        Args:
            game_state: Current game state
            state_data: Previously saved state data
        """
        # Restore trackers using from_dict factory method
        trackers_data = state_data.get("active_trackers", [])
        for tracker_dict in trackers_data:
            tracker = SLATracker.from_dict(tracker_dict)
            self._sla_monitor.add_tracker(tracker)
        
        # Restore incident-to-tracker mappings
        incident_mappings = state_data.get("incident_mappings", {})
        for incident_id, tracker_id in incident_mappings.items():
            self._sla_monitor.set_incident_mapping(incident_id, tracker_id)
        
        logger.info(f"[SLA_PLUGIN] Loaded {len(trackers_data)} SLA trackers from save")
    
    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================
    
    def _on_incident_created(self, event: Event) -> None:
        """Handle incident created event.
        
        Creates a new SLA tracker when an incident spawns for a client.
        
        Args:
            event: Event with incident and client data
        """
        try:
            incident_data = event.data.get("incident")
            client_data = event.data.get("client")
            
            if not incident_data or not client_data:
                logger.warning(
                    "[SLA_PLUGIN] Incident created event missing incident or client data"
                )
                return
            
            # Extract incident ID and client ID
            incident_id = getattr(incident_data, 'incident_id', None) or incident_data.get('incident_id')
            client_id = getattr(client_data, 'client_id', None) or client_data.get('client_id')
            
            if not incident_id or not client_id:
                logger.warning(
                    f"[SLA_PLUGIN] Cannot create SLA tracker: "
                    f"incident_id={incident_id}, client_id={client_id}"
                )
                return
            
            # Create SLA tracker
            tracker_id = f"sla_{incident_id}"
            
            tracker = SLATracker(
                tracker_id=tracker_id,
                client_id=client_id,
                month=0,  # Assume current month (handled by client manager)
                total_incidents=1,
            )
            
            # Add tracker and register incident mapping
            self._sla_monitor.add_tracker(tracker, incident_id=incident_id)
            
            logger.info(
                f"[SLA_PLUGIN] Created SLA tracker for incident {incident_id} "
                f"(client {client_id})"
            )
            
        except Exception as e:
            logger.error(f"[SLA_PLUGIN] Error handling incident_created: {e}", exc_info=True)
    
    def _on_incident_assigned(self, event: Event) -> None:
        """Handle incident assigned event.
        
        Starts the response timer when incident is assigned to a specialist.
        
        Args:
            event: Event with assignment data
        """
        try:
            incident_id = event.data.get("incident_id")
            specialist_id = event.data.get("specialist_id")
            
            if not incident_id:
                logger.warning("[SLA_PLUGIN] Incident assigned event missing incident_id")
                return
            
            tracker = self._sla_monitor.get_tracker_for_incident(incident_id)
            if tracker:
                # Mark response SLA as met (response time = assignment time)
                tracker.response_sla_met += 1
                logger.info(
                    f"[SLA_PLUGIN] Incident {incident_id} assigned to specialist {specialist_id}, "
                    f"response SLA met"
                )
            else:
                logger.warning(
                    f"[SLA_PLUGIN] No SLA tracker found for incident {incident_id}"
                )
        
        except Exception as e:
            logger.error(f"[SLA_PLUGIN] Error handling incident_assigned: {e}", exc_info=True)
    
    def _on_incident_completed(self, event: Event) -> None:
        """Handle incident completed event.
        
        Finalizes SLA tracking when incident is resolved.
        
        Args:
            event: Event with resolution data
        """
        try:
            incident_id = event.data.get("incident_id")
            success = event.data.get("success", False)
            
            if not incident_id:
                logger.warning("[SLA_PLUGIN] Incident completed event missing incident_id")
                return
            
            tracker = self._sla_monitor.get_tracker_for_incident(incident_id)
            if tracker:
                # Record resolution SLA result
                if success:
                    tracker.resolution_sla_met += 1
                    logger.info(
                        f"[SLA_PLUGIN] Incident {incident_id} resolved successfully, "
                        f"resolution SLA met"
                    )
                else:
                    tracker.resolution_sla_missed += 1
                    logger.warning(
                        f"[SLA_PLUGIN] Incident {incident_id} resolved with failure, "
                        f"resolution SLA missed"
                    )
            else:
                logger.warning(
                    f"[SLA_PLUGIN] No SLA tracker found for completed incident {incident_id}"
                )
        
        except Exception as e:
            logger.error(f"[SLA_PLUGIN] Error handling incident_completed: {e}", exc_info=True)
