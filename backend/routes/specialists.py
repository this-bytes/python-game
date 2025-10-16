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
    
    @bp.route('/specialists/<specialist_id>/gain-xp', methods=['POST'])
    def gain_xp(specialist_id):
        """Award XP to a specialist."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            specialist = game_state.get_specialist_by_id(specialist_id)
            if not specialist:
                return jsonify({"success": False, "message": "Specialist not found"}), 404
            
            data = request.get_json()
            xp_amount = data.get('xp', 0)
            
            if xp_amount <= 0:
                return jsonify({"success": False, "message": "XP amount must be positive"}), 400
            
            leveled_up = specialist.gain_xp(xp_amount)
            
            return jsonify({
                "success": True,
                "message": f"Awarded {xp_amount} XP",
                "data": {
                    "leveled_up": leveled_up,
                    "current_xp": specialist.xp,
                    "current_level": specialist.level
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/specialists/<specialist_id>/level-up', methods=['POST'])
    def force_level_up(specialist_id):
        """Force a specialist to level up (for testing/admin)."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            from src.core.progression_system import ProgressionSystem
            from src.utils.json_loader import JSONLoader
            
            specialist = game_state.get_specialist_by_id(specialist_id)
            if not specialist:
                return jsonify({"success": False, "message": "Specialist not found"}), 404
            
            # Load game config and create progression system
            json_loader = JSONLoader()
            game_config = json_loader.load_data("game_config")
            progression_system = ProgressionSystem(game_config)
            
            # Set XP to next level threshold
            next_level_xp = progression_system.calculate_xp_for_level(specialist.level + 1)
            specialist.xp = next_level_xp
            
            # Trigger level up
            leveled_up = specialist.check_level_up()
            
            if leveled_up:
                # Process level up rewards
                rewards = progression_system.process_level_up(specialist)
                
                return jsonify({
                    "success": True,
                    "message": "Specialist leveled up",
                    "data": {
                        "specialist": specialist.to_dict(),
                        "rewards": rewards
                    },
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Specialist already at max level"
                }), 400
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/specialists/<specialist_id>/allocate-skill', methods=['POST'])
    def allocate_skill(specialist_id):
        """Allocate a skill point to a stat."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            specialist = game_state.get_specialist_by_id(specialist_id)
            if not specialist:
                return jsonify({"success": False, "message": "Specialist not found"}), 404
            
            data = request.get_json()
            stat = data.get('stat')
            
            if not stat:
                return jsonify({"success": False, "message": "stat parameter required"}), 400
            
            success = specialist.allocate_skill_point(stat)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": f"Skill point allocated to {stat}",
                    "data": specialist.to_dict(),
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Failed to allocate skill point (no points available or invalid stat?)"
                }), 400
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/specialists/<specialist_id>/abilities', methods=['GET'])
    def get_abilities(specialist_id):
        """Get unlocked abilities for a specialist."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            from src.core.ability_system import AbilitySystem
            from src.utils.json_loader import JSONLoader
            
            specialist = game_state.get_specialist_by_id(specialist_id)
            if not specialist:
                return jsonify({"success": False, "message": "Specialist not found"}), 404
            
            # Load abilities config
            json_loader = JSONLoader()
            abilities_config = json_loader.load_data("abilities")
            ability_system = AbilitySystem(abilities_config)
            
            # Get unlocked abilities with details
            abilities_data = []
            for ability_id in specialist.abilities:
                ability = ability_system.get_ability(ability_id)
                if ability:
                    ability_dict = ability.to_dict()
                    ability_dict["cooldown_remaining"] = specialist.ability_cooldowns.get(ability_id, 0.0)
                    ability_dict["available"] = ability_id in ability_system.get_available_abilities(specialist)
                    abilities_data.append(ability_dict)
            
            return jsonify({
                "success": True,
                "data": abilities_data,
                "count": len(abilities_data),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/specialists/<specialist_id>/activate-ability', methods=['POST'])
    def activate_ability(specialist_id):
        """Activate an ability for a specialist."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            from src.core.ability_system import AbilitySystem
            from src.utils.json_loader import JSONLoader
            
            specialist = game_state.get_specialist_by_id(specialist_id)
            if not specialist:
                return jsonify({"success": False, "message": "Specialist not found"}), 404
            
            data = request.get_json()
            ability_id = data.get('ability_id')
            target_incident_id = data.get('target_incident_id')
            
            if not ability_id:
                return jsonify({"success": False, "message": "ability_id required"}), 400
            
            # Load abilities config
            json_loader = JSONLoader()
            abilities_config = json_loader.load_data("abilities")
            ability_system = AbilitySystem(abilities_config)
            
            # Get target incident if specified
            target = None
            if target_incident_id:
                target = game_state.get_incident_by_id(target_incident_id)
            
            # Activate ability
            result = ability_system.activate_ability(specialist, ability_id, target)
            
            if result["success"]:
                return jsonify({
                    "success": True,
                    "message": result["message"],
                    "data": {
                        "specialist": specialist.to_dict(),
                        "effect": result.get("effect_applied")
                    },
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "message": result["message"]
                }), 400
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    return bp
