"""WebSocket service for real-time game state updates.

Provides real-time broadcasting of game events to connected admin clients.
"""
from typing import Dict, Any, List
from flask_socketio import SocketIO, emit
from datetime import datetime
import threading


class WebSocketService:
    """Manages WebSocket connections and broadcasts game events."""
    
    def __init__(self):
        """Initialize WebSocket service."""
        self.socketio: SocketIO = None
        self.connected_clients: List[str] = []
        self.event_history: List[Dict[str, Any]] = []
        self.max_history = 100
        
    def init_app(self, app, socketio: SocketIO):
        """Initialize with Flask app and SocketIO instance.
        
        Args:
            app: Flask application
            socketio: SocketIO instance
        """
        self.socketio = socketio
        
        @socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            self.connected_clients.append(threading.current_thread().ident)
            self.broadcast('connection', {
                'message': 'Admin client connected',
                'client_count': len(self.connected_clients)
            })
            
        @socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            if threading.current_thread().ident in self.connected_clients:
                self.connected_clients.remove(threading.current_thread().ident)
            self.broadcast('disconnection', {
                'message': 'Admin client disconnected',
                'client_count': len(self.connected_clients)
            })
    
    def broadcast(self, event_type: str, data: Dict[str, Any]):
        """Broadcast event to all connected clients.
        
        Args:
            event_type: Type of event (e.g., 'game_state_update', 'incident_spawned')
            data: Event data to broadcast
        """
        if not self.socketio:
            return
            
        event = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Broadcast to all clients
        self.socketio.emit('game_event', event)
    
    def broadcast_game_state(self, game_state_dict: Dict[str, Any]):
        """Broadcast full game state update.
        
        Args:
            game_state_dict: Dictionary representation of game state
        """
        self.broadcast('game_state_update', game_state_dict)
    
    def broadcast_incident_spawned(self, incident_dict: Dict[str, Any]):
        """Broadcast incident spawned event.
        
        Args:
            incident_dict: Dictionary representation of spawned incident
        """
        self.broadcast('incident_spawned', {
            'incident': incident_dict,
            'message': f"Incident spawned: {incident_dict.get('name', 'Unknown')}"
        })
    
    def broadcast_specialist_updated(self, specialist_id: str, changes: Dict[str, Any]):
        """Broadcast specialist updated event (protocol-compliant).
        
        Args:
            specialist_id: ID of updated specialist
            changes: Dictionary of changed properties
        """
        self.broadcast('specialist_updated', {
            'specialist_id': specialist_id,
            'changes': changes,
            'timestamp': datetime.utcnow().timestamp()
        })
    
    def broadcast_incident_updated(self, incident_id: str, changes: Dict[str, Any]):
        """Broadcast incident updated event (protocol-compliant).
        
        Args:
            incident_id: ID of updated incident
            changes: Dictionary of changed properties
        """
        self.broadcast('incident_updated', {
            'incident_id': incident_id,
            'changes': changes,
            'timestamp': datetime.utcnow().timestamp()
        })
    
    def broadcast_incident_resolved(self, incident_id: str, specialist_id: str, 
                                   success: bool, reward: float, xp_earned: int,
                                   resolution_time: float, sla_met: bool):
        """Broadcast incident resolved event (protocol-compliant).
        
        Args:
            incident_id: ID of resolved incident
            specialist_id: ID of specialist who resolved it
            success: Whether incident was successfully resolved
            reward: Money reward earned
            xp_earned: XP earned
            resolution_time: Time taken to resolve (seconds)
            sla_met: Whether SLA was met
        """
        self.broadcast('incident_resolved', {
            'incident_id': incident_id,
            'specialist_id': specialist_id,
            'success': success,
            'resolution_time': resolution_time,
            'reward': reward,
            'xp_earned': xp_earned,
            'sla_met': sla_met,
            'timestamp': datetime.utcnow().timestamp()
        })
    
    def broadcast_plugin_event(self, plugin_name: str, event_type: str, data: Dict[str, Any]):
        """Broadcast plugin-specific event (protocol-compliant).
        
        Args:
            plugin_name: Name of plugin emitting event
            event_type: Type of plugin event
            data: Event-specific data
        """
        self.broadcast('plugin_event', {
            'plugin_name': plugin_name,
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.utcnow().timestamp()
        })
    
    def broadcast_game_snapshot(self, game_state_dict: Dict[str, Any], incremental: bool = False):
        """Broadcast game snapshot event (protocol-compliant).
        
        Args:
            game_state_dict: Dictionary representation of game state
            incremental: Whether this is an incremental (delta) update
        """
        self.broadcast('game_snapshot', {
            'data': game_state_dict,
            'incremental': incremental,
            'timestamp': datetime.utcnow().timestamp()
        })
    
    def broadcast_error(self, code: str, message: str, details: Dict[str, Any] = None):
        """Broadcast error event (protocol-compliant).
        
        Args:
            code: Error code
            message: Error message
            details: Optional additional error details
        """
        self.broadcast('error', {
            'code': code,
            'message': message,
            'details': details or {},
            'timestamp': datetime.utcnow().timestamp()
        })
    
    def broadcast_specialist_action(self, action: str, specialist_dict: Dict[str, Any]):
        """Broadcast specialist action event (legacy, deprecated).
        
        Args:
            action: Action type (e.g., 'assigned', 'level_up', 'hired')
            specialist_dict: Dictionary representation of specialist
        """
        self.broadcast('specialist_action', {
            'action': action,
            'specialist': specialist_dict,
            'message': f"Specialist {specialist_dict.get('name', 'Unknown')}: {action}"
        })
    
    def broadcast_money_change(self, old_money: float, new_money: float, reason: str):
        """Broadcast money change event.
        
        Args:
            old_money: Previous money amount
            new_money: New money amount
            reason: Reason for change
        """
        delta = new_money - old_money
        self.broadcast('money_change', {
            'old_money': old_money,
            'new_money': new_money,
            'delta': delta,
            'reason': reason,
            'message': f"Money {'increased' if delta > 0 else 'decreased'} by ${abs(delta):.2f}: {reason}"
        })
    
    def get_event_history(self) -> List[Dict[str, Any]]:
        """Get recent event history.
        
        Returns:
            List of recent events
        """
        return self.event_history.copy()
    
    def get_client_count(self) -> int:
        """Get number of connected clients.
        
        Returns:
            Number of connected admin clients
        """
        return len(self.connected_clients)


# Global WebSocket service instance
ws_service = WebSocketService()
