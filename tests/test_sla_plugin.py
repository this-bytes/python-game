"""Unit tests for SLA Plugin.

Tests the SLA Plugin wrapper for the SLA system, including:
- Plugin lifecycle (initialize, update, shutdown)
- Event subscriptions and handling
- SLA tracker creation and management
- State persistence (save/load)
- Integration with event bus

Follows 15-point gate standards: 100% type hints, Google docstrings,
>80% coverage, specific error handling, edge cases.
"""

import pytest
from unittest.mock import Mock

from src.core.plugins.sla_plugin import SLAPlugin, SLAMonitor
from src.core.event_bus import get_event_bus
from src.models.sla_tracker import SLATracker


# ============================================================================
# FIXTURES: Reusable test data and mock objects
# ============================================================================

@pytest.fixture
def sla_plugin() -> SLAPlugin:
    """Create fresh SLA plugin instance."""
    return SLAPlugin()


@pytest.fixture
def sla_monitor() -> SLAMonitor:
    """Create fresh SLA monitor instance."""
    return SLAMonitor()


@pytest.fixture
def mock_game_state() -> Mock:
    """Create mock game state with required attributes."""
    state = Mock()
    state.game_time = 0.0
    return state


@pytest.fixture
def test_tracker() -> SLATracker:
    """Create test SLA tracker."""
    return SLATracker(
        tracker_id="sla_test_001",
        client_id="client_001",
        month=1,
        total_incidents=0,
        response_sla_met=0,
        response_sla_missed=0,
        resolution_sla_met=0,
        resolution_sla_missed=0,
    )


@pytest.fixture
def test_incident() -> Mock:
    """Create mock incident object."""
    incident = Mock()
    incident.incident_id = "inc_001"
    incident.id = "inc_001"
    return incident


@pytest.fixture
def test_client() -> Mock:
    """Create mock client object."""
    client = Mock()
    client.client_id = "client_001"
    client.sla_response_time = 300
    client.sla_resolution_time = 3600
    return client


@pytest.fixture
def event_bus():
    """Get event bus singleton and clean it."""
    bus = get_event_bus()
    bus._subscriptions.clear()
    yield bus
    bus._subscriptions.clear()


# ============================================================================
# TEST SUITE: SLAMonitor
# ============================================================================

class TestSLAMonitor:
    """Test suite for SLAMonitor class."""
    
    def test_monitor_initialization(self, sla_monitor: SLAMonitor):
        """Test SLAMonitor initializes empty."""
        assert len(sla_monitor.get_all_trackers()) == 0
        assert sla_monitor._incident_to_tracker == {}
    
    def test_add_tracker(self, sla_monitor: SLAMonitor, test_tracker: SLATracker):
        """Test adding tracker to monitor."""
        sla_monitor.add_tracker(test_tracker)
        
        assert len(sla_monitor.get_all_trackers()) == 1
        assert sla_monitor.get_tracker_by_id("sla_test_001") is test_tracker
    
    def test_add_tracker_with_incident_mapping(
        self, 
        sla_monitor: SLAMonitor, 
        test_tracker: SLATracker
    ):
        """Test adding tracker with incident mapping."""
        sla_monitor.add_tracker(test_tracker, incident_id="inc_001")
        
        tracker = sla_monitor.get_tracker_for_incident("inc_001")
        assert tracker is test_tracker
    
    def test_get_tracker_not_found(self, sla_monitor: SLAMonitor):
        """Test getting non-existent tracker returns None."""
        tracker = sla_monitor.get_tracker_by_id("nonexistent")
        assert tracker is None
    
    def test_remove_tracker(
        self, 
        sla_monitor: SLAMonitor, 
        test_tracker: SLATracker
    ):
        """Test removing tracker from monitor."""
        sla_monitor.add_tracker(test_tracker)
        assert len(sla_monitor.get_all_trackers()) == 1
        
        sla_monitor.remove_tracker("sla_test_001")
        assert len(sla_monitor.get_all_trackers()) == 0
    
    def test_remove_tracker_cleans_mapping(
        self, 
        sla_monitor: SLAMonitor, 
        test_tracker: SLATracker
    ):
        """Test removing tracker also removes incident mapping."""
        sla_monitor.add_tracker(test_tracker, incident_id="inc_001")
        sla_monitor.remove_tracker("sla_test_001")
        
        tracker = sla_monitor.get_tracker_for_incident("inc_001")
        assert tracker is None
    
    def test_clear_all_trackers(
        self, 
        sla_monitor: SLAMonitor, 
        test_tracker: SLATracker
    ):
        """Test clearing all trackers."""
        sla_monitor.add_tracker(test_tracker, incident_id="inc_001")
        sla_monitor.add_tracker(test_tracker, incident_id="inc_002")
        
        sla_monitor.clear()
        
        assert len(sla_monitor.get_all_trackers()) == 0
        assert len(sla_monitor._incident_to_tracker) == 0


# ============================================================================
# TEST SUITE: SLAPlugin Lifecycle
# ============================================================================

class TestSLAPluginLifecycle:
    """Test suite for SLA plugin lifecycle methods."""
    
    def test_plugin_initialization(self, sla_plugin: SLAPlugin):
        """Test plugin initializes with correct name and feature ID."""
        assert sla_plugin.get_name() == "SLAPlugin"
        assert sla_plugin.get_feature_id() == "sla_system"
    
    def test_plugin_initialize_subscribes_to_events(
        self, 
        sla_plugin: SLAPlugin, 
        event_bus,
        mock_game_state: Mock
    ):
        """Test plugin subscribes to incident lifecycle events."""
        sla_plugin.initialize(mock_game_state)
        
        # Verify subscription IDs are stored
        assert len(sla_plugin._subscription_ids) == 3
        
        # Verify event types are subscribed
        subscriptions = event_bus._subscriptions
        assert "incident_created" in subscriptions
        assert "incident_assigned" in subscriptions
        assert "incident_completed" in subscriptions
    
    def test_plugin_shutdown_unsubscribes(
        self, 
        sla_plugin: SLAPlugin, 
        event_bus,
        mock_game_state: Mock
    ):
        """Test plugin unsubscribes from events on shutdown."""
        sla_plugin.initialize(mock_game_state)
        
        sla_plugin.shutdown(mock_game_state)
        
        # After shutdown, subscription IDs should be cleared
        assert len(sla_plugin._subscription_ids) == 0
        assert sla_plugin._sla_monitor.get_all_trackers() == []
    
    def test_plugin_update(self, sla_plugin: SLAPlugin, mock_game_state: Mock):
        """Test plugin update method (placeholder for event-driven model)."""
        sla_plugin.initialize(mock_game_state)
        
        # Update should complete without error
        sla_plugin.update(mock_game_state, delta_time=1.0)
        
        assert True  # No exception raised


# ============================================================================
# TEST SUITE: Event Handling
# ============================================================================

class TestSLAPluginEventHandling:
    """Test suite for SLA plugin event handling."""
    
    def test_incident_created_event(
        self, 
        sla_plugin: SLAPlugin, 
        event_bus,
        test_incident: Mock,
        test_client: Mock,
        mock_game_state: Mock
    ):
        """Test handling of incident_created event."""
        sla_plugin.initialize(mock_game_state)
        
        # Publish and process incident_created event
        event_bus.publish("incident_created", {
            "incident": test_incident,
            "client": test_client,
        })
        event_bus.process_events()
        
        # Verify tracker was created
        tracker = sla_plugin._sla_monitor.get_tracker_for_incident("inc_001")
        assert tracker is not None
        assert tracker.client_id == "client_001"
    
    def test_incident_assigned_event(
        self, 
        sla_plugin: SLAPlugin, 
        event_bus,
        test_incident: Mock,
        test_client: Mock,
        mock_game_state: Mock
    ):
        """Test handling of incident_assigned event."""
        sla_plugin.initialize(mock_game_state)
        
        # Create tracker
        event_bus.publish("incident_created", {
            "incident": test_incident,
            "client": test_client,
        })
        event_bus.process_events()
        
        # Publish incident_assigned event
        event_bus.publish("incident_assigned", {
            "incident_id": "inc_001",
            "specialist_id": "spec_001",
        })
        event_bus.process_events()
        
        # Verify response SLA was recorded
        tracker = sla_plugin._sla_monitor.get_tracker_for_incident("inc_001")
        assert tracker is not None
        assert tracker.response_sla_met == 1
    
    def test_incident_completed_success(
        self, 
        sla_plugin: SLAPlugin, 
        event_bus,
        test_incident: Mock,
        test_client: Mock,
        mock_game_state: Mock
    ):
        """Test handling of incident_completed event (success)."""
        sla_plugin.initialize(mock_game_state)
        
        # Create and assign incident
        event_bus.publish("incident_created", {
            "incident": test_incident,
            "client": test_client,
        })
        event_bus.process_events()
        
        event_bus.publish("incident_assigned", {
            "incident_id": "inc_001",
            "specialist_id": "spec_001",
        })
        event_bus.process_events()
        
        # Complete incident successfully
        event_bus.publish("incident_completed", {
            "incident_id": "inc_001",
            "success": True,
        })
        event_bus.process_events()
        
        # Verify resolution SLA was met
        tracker = sla_plugin._sla_monitor.get_tracker_for_incident("inc_001")
        assert tracker is not None
        assert tracker.resolution_sla_met == 1
        assert tracker.resolution_sla_missed == 0
    
    def test_incident_completed_failure(
        self, 
        sla_plugin: SLAPlugin, 
        event_bus,
        test_incident: Mock,
        test_client: Mock,
        mock_game_state: Mock
    ):
        """Test handling of incident_completed event (failure)."""
        sla_plugin.initialize(mock_game_state)
        
        # Create and assign incident
        event_bus.publish("incident_created", {
            "incident": test_incident,
            "client": test_client,
        })
        event_bus.process_events()
        
        event_bus.publish("incident_assigned", {
            "incident_id": "inc_001",
            "specialist_id": "spec_001",
        })
        event_bus.process_events()
        
        # Complete incident with failure
        event_bus.publish("incident_completed", {
            "incident_id": "inc_001",
            "success": False,
        })
        event_bus.process_events()
        
        # Verify resolution SLA was missed
        tracker = sla_plugin._sla_monitor.get_tracker_for_incident("inc_001")
        assert tracker is not None
        assert tracker.resolution_sla_met == 0
        assert tracker.resolution_sla_missed == 1


# ============================================================================
# TEST SUITE: State Persistence
# ============================================================================

class TestSLAPluginStatePersistence:
    """Test suite for SLA plugin save/load functionality."""
    
    def test_save_state_empty(self, sla_plugin: SLAPlugin, mock_game_state: Mock):
        """Test saving state with no trackers."""
        sla_plugin.initialize(mock_game_state)
        
        state = sla_plugin.save_state(mock_game_state)
        
        assert "active_trackers" in state
        assert "incident_mappings" in state
        assert len(state["active_trackers"]) == 0
    
    def test_save_state_with_trackers(
        self, 
        sla_plugin: SLAPlugin, 
        mock_game_state: Mock,
        test_tracker: SLATracker
    ):
        """Test saving state with active trackers."""
        sla_plugin.initialize(mock_game_state)
        
        # Add tracker
        sla_plugin._sla_monitor.add_tracker(test_tracker, incident_id="inc_001")
        
        state = sla_plugin.save_state(mock_game_state)
        
        assert len(state["active_trackers"]) == 1
        assert state["active_trackers"][0]["tracker_id"] == "sla_test_001"
    
    def test_load_state(
        self, 
        sla_plugin: SLAPlugin, 
        mock_game_state: Mock,
        test_tracker: SLATracker
    ):
        """Test loading state with trackers."""
        sla_plugin.initialize(mock_game_state)
        
        # Save state from first tracker
        sla_plugin._sla_monitor.add_tracker(test_tracker, incident_id="inc_001")
        saved_state = sla_plugin.save_state(mock_game_state)
        
        # Create new plugin and load state
        new_plugin = SLAPlugin()
        new_plugin.initialize(mock_game_state)
        new_plugin.load_state(mock_game_state, saved_state)
        
        # Verify tracker was restored
        restored_tracker = new_plugin._sla_monitor.get_tracker_by_id("sla_test_001")
        assert restored_tracker is not None
        assert restored_tracker.client_id == "client_001"
    
    def test_load_state_restores_mappings(
        self, 
        sla_plugin: SLAPlugin, 
        mock_game_state: Mock,
        test_tracker: SLATracker
    ):
        """Test loading state restores incident mappings."""
        sla_plugin.initialize(mock_game_state)
        
        # Save state with mapping
        sla_plugin._sla_monitor.add_tracker(test_tracker, incident_id="inc_001")
        saved_state = sla_plugin.save_state(mock_game_state)
        
        # Load state
        new_plugin = SLAPlugin()
        new_plugin.initialize(mock_game_state)
        new_plugin.load_state(mock_game_state, saved_state)
        
        # Verify mapping was restored
        tracker = new_plugin._sla_monitor.get_tracker_for_incident("inc_001")
        assert tracker is not None


# ============================================================================
# TEST SUITE: Edge Cases
# ============================================================================

class TestSLAPluginEdgeCases:
    """Test suite for edge cases and error handling."""
    
    def test_incident_created_missing_incident(self, sla_plugin: SLAPlugin, event_bus, mock_game_state: Mock):
        """Test handling incident_created without incident data."""
        sla_plugin.initialize(mock_game_state)
        
        # Publish with missing data
        event_bus.publish("incident_created", {
            "incident": None,
            "client": Mock(),
        })
        event_bus.process_events()
        
        # Should handle gracefully
        assert len(sla_plugin._sla_monitor.get_all_trackers()) == 0
    
    def test_incident_assigned_nonexistent_incident(self, sla_plugin: SLAPlugin, event_bus, mock_game_state: Mock):
        """Test handling incident_assigned for non-existent incident."""
        sla_plugin.initialize(mock_game_state)
        
        # Publish assignment for non-existent incident
        event_bus.publish("incident_assigned", {
            "incident_id": "nonexistent",
            "specialist_id": "spec_001",
        })
        event_bus.process_events()
        
        # Should handle gracefully
        assert True
    
    def test_multiple_incidents_tracked_independently(
        self, 
        sla_plugin: SLAPlugin, 
        event_bus,
        mock_game_state: Mock
    ):
        """Test tracking multiple incidents independently."""
        sla_plugin.initialize(mock_game_state)
        
        # Create multiple incidents
        for i in range(3):
            incident = Mock()
            incident.incident_id = f"inc_{i}"
            client = Mock()
            client.client_id = f"client_{i}"
            
            event_bus.publish("incident_created", {
                "incident": incident,
                "client": client,
            })
        
        event_bus.process_events()
        
        # Verify all tracked
        assert len(sla_plugin._sla_monitor.get_all_trackers()) == 3
    
    def test_tracker_compliance_calculation(self, test_tracker: SLATracker):
        """Test SLA compliance calculations on tracker."""
        # Set some compliance metrics
        test_tracker.response_sla_met = 8
        test_tracker.response_sla_missed = 2
        test_tracker.resolution_sla_met = 7
        test_tracker.resolution_sla_missed = 3
        
        # Verify calculations
        assert test_tracker.get_response_compliance() == 0.8
        assert test_tracker.get_resolution_compliance() == 0.7
        assert test_tracker.get_overall_compliance() == 0.75
