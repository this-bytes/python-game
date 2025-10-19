"""Network client for UI ↔ Backend communication.

This module provides a unified interface for UI to interact with backend
via HTTP REST and WebSocket, following the canonical protocol specification.

The UI should NEVER directly modify GameState. All actions go through this client.
"""
import requests
import socketio
import time
import threading
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass
from enum import Enum

from src.utils.logger import GameLogger


class ConnectionState(Enum):
    """WebSocket connection states."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


@dataclass
class ActionResult:
    """Result of an action submission."""
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class NetworkClient:
    """Network client for UI communication with backend.
    
    Handles both REST API calls and WebSocket event subscriptions.
    All UI interactions with game logic should go through this client.
    """
    
    def __init__(self, backend_url: str = "http://localhost:5001", instance_id: Optional[str] = None):
        """Initialize network client.
        
        Args:
            backend_url: Base URL of backend server
            instance_id: Optional instance ID for multi-client scenarios
        """
        self.backend_url = backend_url
        self.instance_id = instance_id  # Track which instance this client manages
        self.logger = GameLogger("net_client")
        
        # HTTP session for REST calls
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CybersecGame-UI/1.0'
        })
        
        # WebSocket client
        self.sio = socketio.Client(
            reconnection=True,
            reconnection_attempts=5,
            reconnection_delay=1,
            reconnection_delay_max=5
        )
        
        # Connection state
        self.connection_state = ConnectionState.DISCONNECTED
        self.protocol_version = "1.0.0"
        self.server_time_offset = 0.0
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # State cache (read-only representation)
        self.cached_state: Optional[Dict[str, Any]] = None
        self.state_update_callbacks: List[Callable] = []
        
        # Setup WebSocket event handlers
        self._setup_websocket_handlers()
        
        self.logger.logger.info(f"[NET_CLIENT] Initialized with backend: {backend_url}")
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket event handlers."""
        
        @self.sio.on('connect')
        def on_connect():
            self.connection_state = ConnectionState.CONNECTED
            self.logger.logger.info("[NET_CLIENT] WebSocket connected")
            
            # Subscribe to all event channels
            self._subscribe_to_channels([
                'game_state', 'incidents', 'specialists', 'plugin_events'
            ])
        
        @self.sio.on('disconnect')
        def on_disconnect():
            self.connection_state = ConnectionState.DISCONNECTED
            self.logger.logger.warning("[NET_CLIENT] WebSocket disconnected")
        
        @self.sio.on('connection')
        def on_connection_event(data):
            """Handle connection event from server."""
            self.logger.logger.info("[NET_CLIENT] Connection confirmed by server")
            self.protocol_version = data.get('protocol_version', '1.0.0')
            server_time = data.get('server_time', time.time())
            self.server_time_offset = server_time - time.time()
        
        @self.sio.on('game_snapshot')
        def on_game_snapshot(data):
            """Handle game snapshot event."""
            self.cached_state = data.get('data', {})
            timestamp = data.get('timestamp', 0)
            
            # Notify state update callbacks
            for callback in self.state_update_callbacks:
                try:
                    callback(self.cached_state)
                except Exception as e:
                    self.logger.logger.error(f"[NET_CLIENT] State callback error: {e}")
        
        @self.sio.on('incident_generated')
        def on_incident_generated(data):
            """Handle incident generated event."""
            self._trigger_event_handlers('incident_generated', data)
        
        @self.sio.on('incident_updated')
        def on_incident_updated(data):
            """Handle incident updated event."""
            self._trigger_event_handlers('incident_updated', data)
        
        @self.sio.on('incident_resolved')
        def on_incident_resolved(data):
            """Handle incident resolved event."""
            self._trigger_event_handlers('incident_resolved', data)
        
        @self.sio.on('specialist_updated')
        def on_specialist_updated(data):
            """Handle specialist updated event."""
            self._trigger_event_handlers('specialist_updated', data)
        
        @self.sio.on('plugin_event')
        def on_plugin_event(data):
            """Handle plugin event."""
            self._trigger_event_handlers('plugin_event', data)
        
        @self.sio.on('error')
        def on_error(data):
            """Handle error event from server."""
            self.logger.logger.error(f"[NET_CLIENT] Server error: {data.get('message')}")
            self._trigger_event_handlers('error', data)
    
    def connect(self) -> bool:
        """Connect to backend server.
        
        Returns:
            True if connection successful
        """
        try:
            self.connection_state = ConnectionState.CONNECTING
            
            # Test HTTP connectivity first
            response = self.session.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code != 200:
                self.logger.logger.error(f"[NET_CLIENT] Backend health check failed: {response.status_code}")
                self.connection_state = ConnectionState.ERROR
                return False
            
            # Connect WebSocket
            self.sio.connect(self.backend_url, transports=['websocket', 'polling'])
            
            # Wait for connection confirmation
            timeout = 5.0
            start_time = time.time()
            while self.connection_state != ConnectionState.CONNECTED:
                if time.time() - start_time > timeout:
                    self.logger.logger.error("[NET_CLIENT] WebSocket connection timeout")
                    self.connection_state = ConnectionState.ERROR
                    return False
                time.sleep(0.1)
            
            self.logger.logger.info("[NET_CLIENT] ✅ Connected to backend successfully")
            return True
            
        except Exception as e:
            self.logger.logger.error(f"[NET_CLIENT] Connection failed: {e}")
            self.connection_state = ConnectionState.ERROR
            return False
    
    def disconnect(self):
        """Disconnect from backend server."""
        if self.sio.connected:
            self.sio.disconnect()
        self.connection_state = ConnectionState.DISCONNECTED
        self.logger.logger.info("[NET_CLIENT] Disconnected from backend")
    
    def _subscribe_to_channels(self, channels: List[str]):
        """Subscribe to WebSocket event channels.
        
        Args:
            channels: List of channel names to subscribe to
        """
        try:
            self.sio.emit('subscribe', {'channels': channels})
            self.logger.logger.debug(f"[NET_CLIENT] Subscribed to channels: {channels}")
        except Exception as e:
            self.logger.logger.warning(f"[NET_CLIENT] Failed to subscribe to channels: {e}")
    
    def submit_action(self, action_type: str, data: Dict[str, Any]) -> ActionResult:
        """Submit player action to backend.
        
        Args:
            action_type: Type of action (e.g., 'assign_incident')
            data: Action-specific data
            
        Returns:
            ActionResult with success status and result/error
        """
        try:
            payload = {
                'action_type': action_type,
                'data': data,
                'timestamp': time.time()
            }
            
            # Include instance_id if set
            if self.instance_id:
                payload['instance_id'] = self.instance_id
            
            response = self.session.post(
                f"{self.backend_url}/api/action",
                json=payload,
                timeout=10
            )
            
            response_data = response.json()
            
            if response_data.get('success'):
                self.logger.logger.info(f"[NET_CLIENT] Action succeeded: {action_type}")
                return ActionResult(
                    success=True,
                    result=response_data.get('result')
                )
            else:
                self.logger.logger.warning(f"[NET_CLIENT] Action failed: {action_type}")
                return ActionResult(
                    success=False,
                    error=response_data.get('error')
                )
                
        except Exception as e:
            self.logger.logger.error(f"[NET_CLIENT] Action submission error: {e}")
            return ActionResult(
                success=False,
                error={
                    'code': 'CLIENT_ERROR',
                    'message': str(e)
                }
            )
    
    def get_game_state(self) -> Optional[Dict[str, Any]]:
        """Get full game state from backend.
        
        Returns:
            Game state dictionary or None if failed
        """
        try:
            params = {}
            if self.instance_id:
                params['instance_id'] = self.instance_id
            
            response = self.session.get(
                f"{self.backend_url}/api/game/state",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.cached_state = data.get('data')
                    return self.cached_state
            
            return None
            
        except Exception as e:
            self.logger.logger.error(f"[NET_CLIENT] Failed to get game state: {e}")
            return None
    
    def save_game(self, slot: int = 0) -> bool:
        """Save game to slot.
        
        Args:
            slot: Save slot number
            
        Returns:
            True if save successful
        """
        try:
            response = self.session.post(
                f"{self.backend_url}/api/save",
                json={'slot': slot},
                timeout=10
            )
            
            data = response.json()
            return data.get('success', False)
            
        except Exception as e:
            self.logger.logger.error(f"[NET_CLIENT] Save failed: {e}")
            return False
    
    def load_game(self, slot: int = 0) -> bool:
        """Load game from slot.
        
        Args:
            slot: Save slot number
            
        Returns:
            True if load successful
        """
        try:
            response = self.session.post(
                f"{self.backend_url}/api/load",
                json={'slot': slot},
                timeout=10
            )
            
            data = response.json()
            return data.get('success', False)
            
        except Exception as e:
            self.logger.logger.error(f"[NET_CLIENT] Load failed: {e}")
            return False
    
    def on_event(self, event_type: str, callback: Callable):
        """Register callback for specific event type.
        
        Args:
            event_type: Event type to listen for
            callback: Function to call when event occurs
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(callback)
    
    def on_state_update(self, callback: Callable):
        """Register callback for state updates.
        
        Args:
            callback: Function to call when state updates (receives state dict)
        """
        self.state_update_callbacks.append(callback)
    
    def _trigger_event_handlers(self, event_type: str, data: Dict[str, Any]):
        """Trigger all registered handlers for event type.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    self.logger.logger.error(f"[NET_CLIENT] Event handler error: {e}")
    
    def is_connected(self) -> bool:
        """Check if connected to backend.
        
        Returns:
            True if connected
        """
        return self.connection_state == ConnectionState.CONNECTED
    
    def get_cached_state(self) -> Optional[Dict[str, Any]]:
        """Get cached game state (from last snapshot).
        
        Returns:
            Cached state dictionary or None
        """
        return self.cached_state
