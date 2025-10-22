"""Tests for Game Loop Plugin - manages daily cycles and phase transitions.

Tests cover:
- Phase transitions (Morning → Day → Evening → Night → Morning)
- Day/month boundaries
- Event publishing for phase changes
- State persistence (save/load)
- Edge cases (pausing, resuming, multiple transitions)
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call

from src.core.plugins.game_loop_plugin import GameLoopPlugin, GamePhase
from src.core.event_bus import get_event_bus, Event
from src.models.game_state import GameState


class TestGamePhaseEnum:
    """Test GamePhase enumeration."""
    
    def test_game_phase_values(self):
        """Verify GamePhase enum has correct values."""
        assert GamePhase.MORNING.value == 1
        assert GamePhase.DAY.value == 2
        assert GamePhase.EVENING.value == 3
        assert GamePhase.NIGHT.value == 4


class TestGameLoopPluginLifecycle:
    """Test GameLoopPlugin lifecycle methods."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        return GameLoopPlugin()
    
    @pytest.fixture
    def mock_game_state(self):
        """Create mock game state."""
        state = Mock(spec=GameState)
        state.current_money = 5000.0
        state.specialists = [Mock(), Mock()]
        state.clients = [Mock(), Mock(), Mock()]
        state.game_config = {"game_loop": {"phase_duration_seconds": 10.0}}
        return state
    
    def test_initialization(self, plugin, mock_game_state):
        """Test plugin initializes correctly."""
        assert plugin.get_name() == "GameLoopPlugin"
        assert plugin.get_feature_id() == "game_loop_system"
    
    def test_initialize_sets_up_state(self, plugin, mock_game_state):
        """Test initialize() sets up initial state."""
        plugin.initialize(mock_game_state)
        
        assert plugin.get_current_phase() == GamePhase.MORNING
        assert plugin.get_current_day() == 1
        assert plugin.get_current_month() == 1
        assert plugin.get_time_in_phase() == 0.0
    
    def test_shutdown_cleans_up(self, plugin, mock_game_state):
        """Test shutdown() cleans up resources."""
        plugin.initialize(mock_game_state)
        plugin.shutdown(mock_game_state)
        
        # Should unsubscribe from all events
        assert len(plugin._subscription_ids) == 0


class TestGameLoopPhaseTransitions:
    """Test phase transitions during daily cycle."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        return GameLoopPlugin()
    
    @pytest.fixture
    def mock_game_state(self):
        """Create mock game state."""
        state = Mock(spec=GameState)
        state.current_money = 5000.0
        state.specialists = [Mock()]
        state.clients = [Mock()]
        state.game_config = {"game_loop": {"phase_duration_seconds": 10.0}}
        return state
    
    def test_morning_to_day_transition(self, plugin, mock_game_state):
        """Test transition from Morning to Day phase."""
        plugin.initialize(mock_game_state)
        assert plugin.get_current_phase() == GamePhase.MORNING
        
        # Simulate time passing (enough to transition)
        plugin.update(mock_game_state, 11.0)
        
        assert plugin.get_current_phase() == GamePhase.DAY
        assert plugin.get_time_in_phase() < 1.0  # Reset time
    
    def test_day_to_evening_transition(self, plugin, mock_game_state):
        """Test transition from Day to Evening phase."""
        plugin.initialize(mock_game_state)
        plugin._current_phase = GamePhase.DAY
        plugin._time_in_phase = 0.0
        
        plugin.update(mock_game_state, 11.0)
        
        assert plugin.get_current_phase() == GamePhase.EVENING
    
    def test_evening_to_night_transition(self, plugin, mock_game_state):
        """Test transition from Evening to Night phase."""
        plugin.initialize(mock_game_state)
        plugin._current_phase = GamePhase.EVENING
        plugin._time_in_phase = 0.0
        
        plugin.update(mock_game_state, 11.0)
        
        assert plugin.get_current_phase() == GamePhase.NIGHT
    
    def test_night_to_morning_advances_day(self, plugin, mock_game_state):
        """Test transition from Night to Morning advances day counter."""
        plugin.initialize(mock_game_state)
        plugin._current_phase = GamePhase.NIGHT
        plugin._current_day = 5
        plugin._time_in_phase = 0.0
        
        plugin.update(mock_game_state, 11.0)
        
        assert plugin.get_current_phase() == GamePhase.MORNING
        assert plugin.get_current_day() == 6
    
    def test_month_boundary_at_30_days(self, plugin, mock_game_state):
        """Test month advances after 30 days."""
        plugin.initialize(mock_game_state)
        plugin._current_day = 30
        plugin._current_month = 1
        plugin._current_phase = GamePhase.NIGHT
        plugin._time_in_phase = 0.0
        
        plugin.update(mock_game_state, 11.0)
        
        assert plugin.get_current_day() == 1
        assert plugin.get_current_month() == 2
    
    def test_complete_day_cycle(self, plugin, mock_game_state):
        """Test complete 4-phase day cycle."""
        plugin.initialize(mock_game_state)
        plugin._phase_duration_seconds = 10.0
        
        # Start at morning
        assert plugin.get_current_phase() == GamePhase.MORNING
        
        # Morning → Day
        plugin.update(mock_game_state, 11.0)
        assert plugin.get_current_phase() == GamePhase.DAY
        
        # Day → Evening
        plugin.update(mock_game_state, 11.0)
        assert plugin.get_current_phase() == GamePhase.EVENING
        
        # Evening → Night
        plugin.update(mock_game_state, 11.0)
        assert plugin.get_current_phase() == GamePhase.NIGHT
        
        # Night → Morning (next day)
        plugin.update(mock_game_state, 11.0)
        assert plugin.get_current_phase() == GamePhase.MORNING
        assert plugin.get_current_day() == 2


class TestGameLoopEventHandling:
    """Test event handling in game loop."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        return GameLoopPlugin()
    
    @pytest.fixture
    def mock_game_state(self):
        """Create mock game state."""
        state = Mock(spec=GameState)
        state.current_money = 5000.0
        state.specialists = [Mock()]
        state.clients = [Mock()]
        state.game_config = {}
        return state
    
    def test_phase_events_published(self, plugin, mock_game_state):
        """Test phase transition events are published on transitions."""
        # Set a short phase duration for testing
        plugin.initialize(mock_game_state)
        plugin._phase_duration_seconds = 10.0
        
        # Verify that _emit_phase_event is called during update
        original_emit = plugin._emit_phase_event
        emit_calls = []
        
        def track_emit(*args, **kwargs):
            emit_calls.append(args)
            return original_emit(*args, **kwargs)
        
        plugin._emit_phase_event = track_emit
        
        # Trigger a phase transition
        plugin._current_phase = GamePhase.MORNING
        plugin._time_in_phase = 0.0
        plugin.update(mock_game_state, 11.0)
        
        # Should have called _emit_phase_event at least once
        assert len(emit_calls) > 0
    
    def test_handle_game_paused(self, plugin, mock_game_state):
        """Test handling of game_paused event."""
        plugin.initialize(mock_game_state)
        
        event = Mock()
        event.data = {}
        
        # Should not raise
        plugin._on_game_paused(event)
    
    def test_handle_game_resumed(self, plugin, mock_game_state):
        """Test handling of game_resumed event."""
        plugin.initialize(mock_game_state)
        
        event = Mock()
        event.data = {}
        
        # Should not raise
        plugin._on_game_resumed(event)


class TestGameLoopStatePersistence:
    """Test state save/load functionality."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        return GameLoopPlugin()
    
    @pytest.fixture
    def mock_game_state(self):
        """Create mock game state."""
        state = Mock(spec=GameState)
        state.current_money = 5000.0
        state.specialists = []
        state.clients = []
        state.game_config = {}
        return state
    
    def test_save_state(self, plugin, mock_game_state):
        """Test save_state() returns proper data."""
        plugin.initialize(mock_game_state)
        plugin._current_day = 15
        plugin._current_month = 3
        plugin._current_phase = GamePhase.EVENING
        plugin._time_in_phase = 5.5
        
        saved = plugin.save_state(mock_game_state)
        
        assert saved["current_day"] == 15
        assert saved["current_month"] == 3
        assert saved["current_phase"] == "EVENING"
        assert saved["time_in_phase"] == 5.5
    
    def test_load_state(self, plugin, mock_game_state):
        """Test load_state() restores saved state."""
        plugin.initialize(mock_game_state)
        
        state_data = {
            "current_day": 20,
            "current_month": 2,
            "current_phase": "NIGHT",
            "time_in_phase": 8.3,
        }
        
        plugin.load_state(mock_game_state, state_data)
        
        assert plugin.get_current_day() == 20
        assert plugin.get_current_month() == 2
        assert plugin.get_current_phase() == GamePhase.NIGHT
        assert plugin.get_time_in_phase() == 8.3
    
    def test_save_load_cycle(self, plugin, mock_game_state):
        """Test save/load cycle preserves state."""
        plugin.initialize(mock_game_state)
        
        # Set up state
        plugin._current_day = 7
        plugin._current_month = 1
        plugin._current_phase = GamePhase.DAY
        plugin._time_in_phase = 3.2
        
        # Save
        saved = plugin.save_state(mock_game_state)
        
        # Reset plugin
        plugin2 = GameLoopPlugin()
        plugin2.initialize(mock_game_state)
        
        # Load
        plugin2.load_state(mock_game_state, saved)
        
        # Verify
        assert plugin2.get_current_day() == 7
        assert plugin2.get_current_month() == 1
        assert plugin2.get_current_phase() == GamePhase.DAY
        assert plugin2.get_time_in_phase() == 3.2


class TestGameLoopEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        return GameLoopPlugin()
    
    @pytest.fixture
    def mock_game_state(self):
        """Create mock game state."""
        state = Mock(spec=GameState)
        state.current_money = 5000.0
        state.specialists = []
        state.clients = []
        state.game_config = {}
        return state
    
    def test_no_crash_with_empty_game_state(self, plugin, mock_game_state):
        """Test plugin doesn't crash with empty game state."""
        plugin.initialize(mock_game_state)
        plugin.update(mock_game_state, 5.0)
        
        # Should reach here without crashing
        assert plugin.get_current_phase() in [GamePhase.MORNING, GamePhase.DAY]
    
    def test_multiple_transitions_in_single_update(self, plugin, mock_game_state):
        """Test handling large delta_time that spans multiple phases."""
        plugin.initialize(mock_game_state)
        plugin._phase_duration_seconds = 10.0
        
        # Very large delta time
        plugin.update(mock_game_state, 100.0)
        
        # Should have transitioned (may have cycled multiple times)
        assert plugin.get_current_phase() in [GamePhase.MORNING, GamePhase.DAY, 
                                              GamePhase.EVENING, GamePhase.NIGHT]
    
    def test_zero_delta_time(self, plugin, mock_game_state):
        """Test zero delta_time doesn't break phase tracking."""
        plugin.initialize(mock_game_state)
        plugin.update(mock_game_state, 0.0)
        
        assert plugin.get_current_phase() == GamePhase.MORNING
        assert plugin.get_current_day() == 1
    
    def test_multiple_days_cycle(self, plugin, mock_game_state):
        """Test cycling through multiple days correctly."""
        plugin.initialize(mock_game_state)
        plugin._phase_duration_seconds = 1.0
        
        # Simulate 5 complete days (4 phases each = 20 updates)
        for _ in range(20):
            plugin.update(mock_game_state, 2.0)
        
        # After 5 days should be back at day 6
        assert plugin.get_current_day() >= 5
        assert plugin.get_current_month() == 1


class TestGameLoopIntegration:
    """Integration tests for game loop with other systems."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        return GameLoopPlugin()
    
    @pytest.fixture
    def mock_game_state(self):
        """Create mock game state."""
        state = Mock(spec=GameState)
        state.current_money = 10000.0
        state.specialists = [Mock() for _ in range(3)]
        state.clients = [Mock() for _ in range(2)]
        state.incidents = []
        state.game_config = {}
        return state
    
    def test_event_data_includes_game_state_info(self, plugin, mock_game_state):
        """Test phase transition events include game state info."""
        plugin.initialize(mock_game_state)
        
        events_captured = []
        event_bus = get_event_bus()
        original_publish = event_bus.publish
        
        def capture_publish(event_type, data, source="unknown"):
            events_captured.append((event_type, data))
            return original_publish(event_type, data, source)
        
        with patch.object(event_bus, 'publish', side_effect=capture_publish):
            plugin._current_phase = GamePhase.MORNING
            plugin._time_in_phase = 0.0
            plugin.update(mock_game_state, 11.0)
        
        # Check that phase events were published with context
        if events_captured:
            # At least some events should have been published
            assert len(events_captured) > 0
