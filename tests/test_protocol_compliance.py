"""Tests for WebSocket/REST protocol compliance.

Verifies that backend endpoints and events follow the canonical protocol
specification defined in data/ws_protocol.json and docs/WS_PROTOCOL.md.
"""
import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from src.ui.net_client import NetworkClient, ActionResult, ConnectionState
from src.models.game_state import GameState
from src.models.specialist import Specialist, SpecialistStats
from src.models.incident import Incident


class TestActionResultDataClass:
    """Test ActionResult dataclass."""
    
    def test_action_result_success(self):
        """Test successful action result."""
        result = ActionResult(success=True, result={'assigned': True})
        assert result.success is True
        assert result.result == {'assigned': True}
        assert result.error is None
    
    def test_action_result_error(self):
        """Test failed action result."""
        result = ActionResult(
            success=False,
            error={'code': 'SPECIALIST_BUSY', 'message': 'Specialist not available'}
        )
        assert result.success is False
        assert result.error['code'] == 'SPECIALIST_BUSY'
        assert result.result is None


class TestNetworkClientInitialization:
    """Test NetworkClient initialization and configuration."""
    
    def test_initialization_default_url(self):
        """Test network client initializes with default URL."""
        client = NetworkClient()
        assert client.backend_url == "http://localhost:5001"
        assert client.connection_state == ConnectionState.DISCONNECTED
        assert client.protocol_version == "1.0.0"
    
    def test_initialization_custom_url(self):
        """Test network client with custom backend URL."""
        client = NetworkClient("http://192.168.1.100:8080")
        assert client.backend_url == "http://192.168.1.100:8080"
    
    def test_session_headers_configured(self):
        """Test HTTP session has required headers."""
        client = NetworkClient()
        assert 'Content-Type' in client.session.headers
        assert client.session.headers['Content-Type'] == 'application/json'
        assert 'User-Agent' in client.session.headers


class TestActionSubmission:
    """Test action submission format and handling."""
    
    @patch('requests.Session.post')
    def test_submit_action_format(self, mock_post):
        """Test action submission follows protocol format."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'success': True,
            'result': {'assigned': True}
        }
        mock_post.return_value = mock_response
        
        client = NetworkClient()
        result = client.submit_action('assign_incident', {
            'incident_id': 'inc_001',
            'specialist_id': 'spec_001'
        })
        
        # Verify request format
        call_args = mock_post.call_args
        assert call_args[0][0].endswith('/api/action')
        
        request_data = call_args[1]['json']
        assert 'action_type' in request_data
        assert 'data' in request_data
        assert 'timestamp' in request_data
        assert request_data['action_type'] == 'assign_incident'
        assert request_data['data']['incident_id'] == 'inc_001'
    
    @patch('requests.Session.post')
    def test_submit_action_success_response(self, mock_post):
        """Test handling successful action response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'success': True,
            'result': {'assigned': True, 'incident_id': 'inc_001'}
        }
        mock_post.return_value = mock_response
        
        client = NetworkClient()
        result = client.submit_action('assign_incident', {'incident_id': 'inc_001', 'specialist_id': 'spec_001'})
        
        assert result.success is True
        assert result.result['assigned'] is True
        assert result.error is None
    
    @patch('requests.Session.post')
    def test_submit_action_error_response(self, mock_post):
        """Test handling error action response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'success': False,
            'error': {
                'code': 'SPECIALIST_BUSY',
                'message': 'Specialist is already assigned'
            }
        }
        mock_post.return_value = mock_response
        
        client = NetworkClient()
        result = client.submit_action('assign_incident', {'incident_id': 'inc_001', 'specialist_id': 'spec_001'})
        
        assert result.success is False
        assert result.error['code'] == 'SPECIALIST_BUSY'
        assert 'already assigned' in result.error['message']


class TestProtocolErrorCodes:
    """Test that error codes follow protocol specification."""
    
    def test_error_codes_defined(self):
        """Test all protocol error codes are recognized."""
        # Load protocol specification
        with open('data/ws_protocol.json') as f:
            protocol = json.load(f)
        
        error_codes = protocol.get('error_codes', {})
        
        # Verify expected error codes are defined
        expected_codes = [
            'INVALID_ACTION',
            'UNAUTHORIZED',
            'SPECIALIST_NOT_FOUND',
            'INCIDENT_NOT_FOUND',
            'SPECIALTY_MISMATCH',
            'SPECIALIST_BUSY',
            'INSUFFICIENT_FUNDS',
            'COOLDOWN_ACTIVE',
            'INVALID_STATE',
            'SERVER_ERROR'
        ]
        
        for code in expected_codes:
            assert code in error_codes, f"Error code {code} not defined in protocol"
            assert len(error_codes[code]) > 0, f"Error code {code} has no description"


class TestActionTypes:
    """Test that action types follow protocol specification."""
    
    def test_action_types_defined(self):
        """Test all action types are defined in protocol."""
        with open('data/ws_protocol.json') as f:
            protocol = json.load(f)
        
        action_types = protocol.get('action_types', {})
        
        # Verify key action types are defined
        expected_actions = [
            'assign_incident',
            'hire_specialist',
            'equip_item',
            'activate_ability',
            'prestige',
            'sign_contract'
        ]
        
        for action in expected_actions:
            assert action in action_types, f"Action type {action} not defined"
            assert 'description' in action_types[action]
            assert 'data' in action_types[action]


class TestWebSocketEvents:
    """Test WebSocket event formats."""
    
    def test_websocket_event_format(self):
        """Test WebSocket events have required fields."""
        with open('data/ws_protocol.json') as f:
            protocol = json.load(f)
        
        server_events = protocol.get('websocket_events', {}).get('server_to_client', {})
        
        # Test key events have proper structure
        assert 'game_snapshot' in server_events
        assert 'incident_generated' in server_events
        assert 'specialist_updated' in server_events
        assert 'error' in server_events
        
        # Verify event structure
        for event_name, event_spec in server_events.items():
            assert 'event' in event_spec, f"Event {event_name} missing 'event' field"
            assert 'data' in event_spec, f"Event {event_name} missing 'data' field"
            assert 'description' in event_spec, f"Event {event_name} missing description"


class TestConnectionStates:
    """Test connection state management."""
    
    def test_initial_state_disconnected(self):
        """Test client starts in disconnected state."""
        client = NetworkClient()
        assert client.connection_state == ConnectionState.DISCONNECTED
        assert not client.is_connected()
    
    def test_connection_state_enum_values(self):
        """Test connection state enum has all required values."""
        states = [
            ConnectionState.DISCONNECTED,
            ConnectionState.CONNECTING,
            ConnectionState.CONNECTED,
            ConnectionState.RECONNECTING,
            ConnectionState.ERROR
        ]
        
        # Verify all states are unique
        state_values = [s.value for s in states]
        assert len(state_values) == len(set(state_values))


class TestStateCaching:
    """Test state caching functionality."""
    
    def test_cached_state_initially_none(self):
        """Test cached state is None on initialization."""
        client = NetworkClient()
        assert client.get_cached_state() is None
    
    @patch('requests.Session.get')
    def test_get_game_state_caches_result(self, mock_get):
        """Test get_game_state caches the result."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {
                'current_money': 10000,
                'specialists': []
            }
        }
        mock_get.return_value = mock_response
        
        client = NetworkClient()
        state = client.get_game_state()
        
        assert state is not None
        assert state['current_money'] == 10000
        assert client.get_cached_state() == state


class TestSaveLoadOperations:
    """Test save/load operation format."""
    
    @patch('requests.Session.post')
    def test_save_game_format(self, mock_post):
        """Test save game request follows protocol."""
        mock_response = Mock()
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response
        
        client = NetworkClient()
        result = client.save_game(slot=1)
        
        call_args = mock_post.call_args
        assert call_args[0][0].endswith('/api/save')
        assert call_args[1]['json'] == {'slot': 1}
    
    @patch('requests.Session.post')
    def test_load_game_format(self, mock_post):
        """Test load game request follows protocol."""
        mock_response = Mock()
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response
        
        client = NetworkClient()
        result = client.load_game(slot=2)
        
        call_args = mock_post.call_args
        assert call_args[0][0].endswith('/api/load')
        assert call_args[1]['json'] == {'slot': 2}


class TestEventHandlers:
    """Test event handler registration and triggering."""
    
    def test_register_event_handler(self):
        """Test registering event handler."""
        client = NetworkClient()
        handler_called = {'count': 0}
        
        def test_handler(data):
            handler_called['count'] += 1
        
        client.on_event('incident_resolved', test_handler)
        
        # Trigger handler manually
        client._trigger_event_handlers('incident_resolved', {'incident_id': 'inc_001'})
        
        assert handler_called['count'] == 1
    
    def test_multiple_handlers_for_same_event(self):
        """Test multiple handlers can be registered for same event."""
        client = NetworkClient()
        call_log = []
        
        client.on_event('test_event', lambda data: call_log.append('handler1'))
        client.on_event('test_event', lambda data: call_log.append('handler2'))
        
        client._trigger_event_handlers('test_event', {})
        
        assert len(call_log) == 2
        assert 'handler1' in call_log
        assert 'handler2' in call_log
    
    def test_state_update_callbacks(self):
        """Test state update callbacks."""
        client = NetworkClient()
        received_state = {'captured': None}
        
        def state_callback(state):
            received_state['captured'] = state
        
        client.on_state_update(state_callback)
        
        # Manually trigger state update (normally via WebSocket)
        test_state = {'current_money': 5000}
        client.cached_state = test_state
        for callback in client.state_update_callbacks:
            callback(test_state)
        
        assert received_state['captured'] == test_state


class TestProtocolVersion:
    """Test protocol version handling."""
    
    def test_protocol_version_initialized(self):
        """Test protocol version is set on initialization."""
        client = NetworkClient()
        assert client.protocol_version == "1.0.0"
    
    def test_protocol_version_from_protocol_file(self):
        """Test protocol version matches specification file."""
        with open('data/ws_protocol.json') as f:
            protocol = json.load(f)
        
        assert 'protocol_version' in protocol
        assert protocol['protocol_version'] == "1.0.0"
