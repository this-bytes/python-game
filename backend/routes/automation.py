"""Automation & Configuration API routes.

Provides endpoints for automation script management and configuration hot-reloading.
"""
from flask import Blueprint, jsonify, request
from datetime import datetime


def create_automation_blueprint(game_state_ref):
    """Create the automation blueprint."""
    bp = Blueprint('automation', __name__)
    state_container = {'game_state': game_state_ref}
    
    def get_game_state():
        return state_container.get('game_state')
    
    @bp.route('/automation-scripts', methods=['GET'])
    def list_automation_scripts():
        """List all automation scripts."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            scripts_data = [s.to_dict() for s in game_state.automation_scripts]
            return jsonify({
                "success": True,
                "data": scripts_data,
                "count": len(scripts_data),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/automation-scripts/<script_id>', methods=['GET'])
    def get_automation_script(script_id):
        """Get specific automation script details."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            script = game_state.get_automation_script_by_id(script_id)
            if not script:
                return jsonify({"success": False, "message": "Automation script not found"}), 404
            
            return jsonify({
                "success": True,
                "data": script.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/automation-scripts/<script_id>', methods=['PUT'])
    def update_automation_script(script_id):
        """Update automation script parameters."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            script = game_state.get_automation_script_by_id(script_id)
            if not script:
                return jsonify({"success": False, "message": "Automation script not found"}), 404
            
            data = request.get_json()
            
            # Update fields (trigger conditions, effect parameters)
            if 'enabled' in data:
                # TODO: Add enabled field to AutomationScript model
                pass
            
            if 'trigger_conditions' in data:
                # Update trigger conditions
                tc = data['trigger_conditions']
                if 'max_difficulty' in tc:
                    script.trigger_conditions.max_difficulty = tc['max_difficulty']
                if 'min_difficulty' in tc:
                    script.trigger_conditions.min_difficulty = tc['min_difficulty']
                if 'specialty_match' in tc:
                    script.trigger_conditions.specialty_match = tc['specialty_match']
                if 'specialist_available' in tc:
                    script.trigger_conditions.specialist_available = tc['specialist_available']
                if 'min_accuracy' in tc:
                    script.trigger_conditions.min_accuracy = tc['min_accuracy']
            
            return jsonify({
                "success": True,
                "message": "Automation script updated successfully",
                "data": script.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    return bp
