"""God Mode API routes.

Provides powerful testing and debugging commands.
"""
from flask import Blueprint, jsonify, request
from backend.services.websocket_service import ws_service
from datetime import datetime
import random


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
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            data = request.get_json() or {}
            count = data.get('count', 50)
            difficulty = data.get('difficulty')
            
            spawned = []
            for _ in range(count):
                # Spawn incident using game's incident generator
                if hasattr(game_state, 'incident_generator'):
                    incident = game_state.incident_generator.generate_incident()
                    if difficulty:
                        incident.difficulty = difficulty
                    game_state.incidents.append(incident)
                    spawned.append(incident.to_dict())
            
            # Broadcast event
            ws_service.broadcast('wave_spawned', {
                'count': len(spawned),
                'message': f"Spawned wave of {len(spawned)} incidents"
            })
            
            return jsonify({
                "success": True,
                "message": f"Spawned {len(spawned)} incidents",
                "data": {
                    "count": len(spawned),
                    "incidents": spawned[:10]  # Return first 10 for preview
                }
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to spawn wave: {str(e)}"
            }), 500
    
    @bp.route('/godmode/complete-all-incidents', methods=['POST'])
    def complete_all_incidents():
        """Instantly complete all active incidents."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            completed_count = 0
            for incident in game_state.incidents:
                if incident.status == 'active':
                    incident.status = 'completed'
                    completed_count += 1
            
            ws_service.broadcast('incidents_completed', {
                'count': completed_count,
                'message': f"Completed {completed_count} incidents"
            })
            
            return jsonify({
                "success": True,
                "message": f"Completed {completed_count} incidents",
                "data": {"count": completed_count}
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
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            data = request.get_json() or {}
            levels = data.get('levels', 1)
            
            for specialist in game_state.specialists:
                specialist.level += levels
                # Add XP to match new level
                if hasattr(game_state, 'progression_system'):
                    xp_for_level = game_state.progression_system.calculate_xp_for_level(specialist.level)
                    specialist.xp = xp_for_level
            
            ws_service.broadcast('specialists_leveled', {
                'count': len(game_state.specialists),
                'levels': levels,
                'message': f"Leveled up {len(game_state.specialists)} specialists by {levels} levels"
            })
            
            return jsonify({
                "success": True,
                "message": f"Leveled up {len(game_state.specialists)} specialists",
                "data": {
                    "count": len(game_state.specialists),
                    "levels_added": levels
                }
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
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            data = request.get_json() or {}
            amount = data.get('amount', 0)
            
            old_money = game_state.money
            game_state.money = amount
            
            ws_service.broadcast_money_change(old_money, amount, "God mode: Set money")
            
            return jsonify({
                "success": True,
                "message": f"Money set to ${amount}",
                "data": {
                    "old_money": old_money,
                    "new_money": amount
                }
            })
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
