"""Specialist Management API routes.

Provides endpoints for managing specialists (hiring, upgrading, assigning).
"""
from flask import Blueprint, jsonify, request
from datetime import datetime


def create_specialists_blueprint(game_state_ref):
    """Create the specialists blueprint with game state reference.
    
    Args:
        game_state_ref: Reference to the GameState instance
    
    Returns:
        Flask Blueprint for specialist routes
    """
    bp = Blueprint('specialists', __name__)
    
    state_container = {'game_state': game_state_ref}
    
    def get_game_state():
        return state_container.get('game_state')
    
    @bp.route('/specialists', methods=['GET'])
    def list_specialists():
        """List all specialists."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            specialists_data = [s.to_dict() for s in game_state.specialists]
            return jsonify({
                "success": True,
                "data": specialists_data,
                "count": len(specialists_data),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/specialists/<specialist_id>', methods=['GET'])
    def get_specialist(specialist_id):
        """Get specific specialist details."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            specialist = game_state.get_specialist_by_id(specialist_id)
            if not specialist:
                return jsonify({"success": False, "message": "Specialist not found"}), 404
            
            return jsonify({
                "success": True,
                "data": specialist.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/specialists', methods=['POST'])
    def create_specialist():
        """Create/hire a new specialist."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            data = request.get_json()
            specialist_data = data.get('specialist', {})
            
            # Use hire_specialist if available, otherwise create manually
            if hasattr(game_state, 'hire_specialist'):
                success = game_state.hire_specialist(specialist_data)
                if not success:
                    return jsonify({
                        "success": False,
                        "message": "Failed to hire specialist (insufficient funds?)"
                    }), 400
                
                return jsonify({
                    "success": True,
                    "message": "Specialist hired successfully",
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Hiring not yet implemented"
                }), 501
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/specialists/<specialist_id>', methods=['PUT'])
    def update_specialist(specialist_id):
        """Update specialist stats/level."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            specialist = game_state.get_specialist_by_id(specialist_id)
            if not specialist:
                return jsonify({"success": False, "message": "Specialist not found"}), 404
            
            data = request.get_json()
            
            # Update fields
            if 'level' in data:
                specialist.level = int(data['level'])
            if 'xp' in data:
                specialist.xp = int(data['xp'])
            if 'stats' in data:
                if 'speed' in data['stats']:
                    specialist.stats['speed'] = float(data['stats']['speed'])
                if 'accuracy' in data['stats']:
                    specialist.stats['accuracy'] = float(data['stats']['accuracy'])
                if 'experience_bonus' in data['stats']:
                    specialist.stats['experience_bonus'] = float(data['stats']['experience_bonus'])
            if 'status' in data:
                specialist.status = data['status']
            
            return jsonify({
                "success": True,
                "message": "Specialist updated successfully",
                "data": specialist.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/specialists/<specialist_id>', methods=['DELETE'])
    def delete_specialist(specialist_id):
        """Remove a specialist."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            specialist = game_state.get_specialist_by_id(specialist_id)
            if not specialist:
                return jsonify({"success": False, "message": "Specialist not found"}), 404
            
            game_state.specialists.remove(specialist)
            
            return jsonify({
                "success": True,
                "message": "Specialist removed successfully",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/specialists/<specialist_id>/assign', methods=['POST'])
    def assign_specialist(specialist_id):
        """Assign specialist to an incident."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            data = request.get_json()
            incident_id = data.get('incident_id')
            
            if not incident_id:
                return jsonify({"success": False, "message": "incident_id required"}), 400
            
            success = game_state.assign_incident_to_specialist(incident_id, specialist_id)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Specialist assigned successfully",
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Assignment failed (specialty mismatch or specialist busy?)"
                }), 400
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/specialists/available', methods=['GET'])
    def get_available_specialists():
        """Get list of available (not busy) specialists."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            available = game_state.get_available_specialists()
            specialists_data = [s.to_dict() for s in available]
            
            return jsonify({
                "success": True,
                "data": specialists_data,
                "count": len(specialists_data),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    return bp
