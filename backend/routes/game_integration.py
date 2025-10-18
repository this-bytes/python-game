"""Game Integration API routes.

Provides endpoints for real-time integration between the running game and backend.
"""
from flask import Blueprint, jsonify, request
from backend.services.websocket_service import ws_service
from datetime import datetime
import threading


def create_game_integration_blueprint(game_state_ref):
    """Create the game integration blueprint.
    
    Args:
        game_state_ref: Reference to the GameState instance
    
    Returns:
        Flask Blueprint for game integration routes
    """
    bp = Blueprint('game_integration', __name__)
    
    # Shared state container that can be updated
    state_container = {'game_state': game_state_ref}
    
    # Command queue for backend -> game communication
    command_queue = []
    command_lock = threading.Lock()
    
    # Latest state from game
    latest_game_state = {}
    
    def get_game_state():
        """Helper to get current game state."""
        return state_container.get('game_state')
    
    @bp.route('/game/register', methods=['POST'])
    def register_game():
        """Register a game client for integration.
        
        The game calls this endpoint when it starts to signal it's ready
        for backend control.
        """
        # Broadcast to control panel
        ws_service.broadcast('game_registered', {
            'message': 'Game client registered and ready for control',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return jsonify({
            "success": True,
            "message": "Game registered successfully",
            "backend_ready": True,
            "control_panel_url": "/control-panel"
        })
    
    @bp.route('/game/commands', methods=['GET'])
    def get_commands():
        """Get pending commands for the game to execute.
        
        The game polls this endpoint to check for backend commands.
        """
        with command_lock:
            commands = command_queue.copy()
            command_queue.clear()
        
        return jsonify({
            "success": True,
            "commands": commands,
            "count": len(commands)
        })
    
    @bp.route('/game/state-update', methods=['POST'])
    def receive_state_update():
        """Receive state update from the game.
        
        The game pushes its current state here for the control panel to display.
        """
        data = request.get_json() or {}
        
        # Update latest state
        latest_game_state.update(data)
        latest_game_state['last_update'] = datetime.utcnow().isoformat()
        
        # Broadcast to control panel
        ws_service.broadcast('game_state_update', latest_game_state)
        
        return jsonify({"success": True})
    
    @bp.route('/game/command', methods=['POST'])
    def queue_command():
        """Queue a command for the game to execute.
        
        The control panel calls this to send commands to the game.
        
        JSON body:
            type: Command type (set_money, spawn_incident, etc.)
            params: Command parameters
        """
        data = request.get_json() or {}
        command_type = data.get('type')
        params = data.get('params', {})
        
        if not command_type:
            return jsonify({
                "success": False,
                "message": "Command type required"
            }), 400
        
        # Queue command
        command = {
            'type': command_type,
            'params': params,
            'queued_at': datetime.utcnow().isoformat()
        }
        
        with command_lock:
            command_queue.append(command)
        
        return jsonify({
            "success": True,
            "message": f"Command {command_type} queued",
            "command": command
        })
    
    @bp.route('/game/status', methods=['GET'])
    def get_game_status():
        """Get the current game integration status.
        
        Returns information about whether a game is connected and its state.
        """
        game_state = get_game_state()
        
        return jsonify({
            "success": True,
            "game_connected": game_state is not None,
            "latest_state": latest_game_state,
            "pending_commands": len(command_queue)
        })
    
    return bp
