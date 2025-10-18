"""God Mode API routes.

Provides powerful testing and debugging commands.
"""
from flask import Blueprint, jsonify, request
from backend.services.websocket_service import ws_service
from datetime import datetime
import random
import requests as http_requests


def create_godmode_blueprint(game_state_ref):
    """Create the god mode blueprint with game state reference.
    
    Args:
        game_state_ref: Reference to the GameState instance
    
    Returns:
        Flask Blueprint for god mode routes
    """
    bp = Blueprint('godmode', __name__)
    
    state_container = {'game_state': game_state_ref}
    
    def get_game_state():
        """Helper to get current game state."""
        return state_container.get('game_state')
    
    @bp.route('/godmode/spawn-wave', methods=['POST'])
    def spawn_wave():
        """Spawn a wave of incidents for stress testing.
        
        JSON body:
            count: Number of incidents to spawn (default: 50)
            difficulty: Specific difficulty or range (optional)
        """
        try:
            data = request.get_json() or {}
            count = data.get('count', 50)
            
            # Queue multiple spawn commands
            for _ in range(count):
                http_requests.post(
                    'http://localhost:5001/api/game/command',
                    json={'type': 'spawn_incident', 'params': {}},
                    timeout=2
                )
            
            ws_service.broadcast('wave_spawned', {
                'count': count,
                'message': f"Spawned wave of {count} incidents"
            })
            
            return jsonify({
                "success": True,
                "message": f"Spawned {count} incidents",
                "data": {"count": count}
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to spawn wave: {str(e)}"
            }), 500
    
    @bp.route('/godmode/complete-all-incidents', methods=['POST'])
    def complete_all_incidents():
        """Instantly complete all active incidents."""
        try:
            http_requests.post(
                'http://localhost:5001/api/game/command',
                json={'type': 'complete_all_incidents', 'params': {}},
                timeout=2
            )
            
            ws_service.broadcast('incidents_completed', {
                'message': "Complete all incidents command queued"
            })
            
            return jsonify({
                "success": True,
                "message": "Complete all incidents command queued"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to complete incidents: {str(e)}"
            }), 500
    
    @bp.route('/godmode/level-up-all', methods=['POST'])
    def level_up_all_specialists():
        """Level up all specialists by specified amount.
        
        JSON body:
            levels: Number of levels to add (default: 1)
        """
        try:
            data = request.get_json() or {}
            levels = data.get('levels', 1)
            
            http_requests.post(
                'http://localhost:5001/api/game/command',
                json={'type': 'level_up_specialists', 'params': {'levels': levels}},
                timeout=2
            )
            
            ws_service.broadcast('specialists_leveled', {
                'levels': levels,
                'message': f"Level up specialists command queued"
            })
            
            return jsonify({
                "success": True,
                "message": f"Level up specialists command queued",
                "data": {"levels_added": levels}
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to level up specialists: {str(e)}"
            }), 500
    
    @bp.route('/godmode/set-money', methods=['POST'])
    def set_money():
        """Set money to exact amount.
        
        JSON body:
            amount: Money amount to set
        """
        try:
            data = request.get_json() or {}
            amount = data.get('amount', 0)
            
            # Queue command for game to execute
            command_response = http_requests.post(
                'http://localhost:5001/api/game/command',
                json={
                    'type': 'set_money',
                    'params': {'amount': amount}
                },
                timeout=2
            )
            
            if command_response.status_code == 200:
                ws_service.broadcast('money_command', {
                    'amount': amount,
                    'message': f"Money set command queued: ${amount}"
                })
                
                return jsonify({
                    "success": True,
                    "message": f"Money set command queued: ${amount}",
                    "data": {"amount": amount}
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Failed to queue command"
                }), 500
                
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to set money: {str(e)}"
            }), 500
    
    @bp.route('/godmode/clear-incidents', methods=['POST'])
    def clear_all_incidents():
        """Clear all incidents from the queue."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            count = len(game_state.incidents)
            game_state.incidents.clear()
            
            ws_service.broadcast('incidents_cleared', {
                'count': count,
                'message': f"Cleared {count} incidents"
            })
            
            return jsonify({
                "success": True,
                "message": f"Cleared {count} incidents",
                "data": {"count": count}
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to clear incidents: {str(e)}"
            }), 500
    
    @bp.route('/godmode/max-all-stats', methods=['POST'])
    def max_all_stats():
        """Max out all specialist stats."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            for specialist in game_state.specialists:
                specialist.speed = 100
                specialist.accuracy = 100
                specialist.experience_bonus = 2.0
            
            ws_service.broadcast('stats_maxed', {
                'count': len(game_state.specialists),
                'message': f"Maxed stats for {len(game_state.specialists)} specialists"
            })
            
            return jsonify({
                "success": True,
                "message": f"Maxed stats for {len(game_state.specialists)} specialists",
                "data": {"count": len(game_state.specialists)}
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to max stats: {str(e)}"
            }), 500
    
    return bp
