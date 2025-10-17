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
    
    @bp.route('/specialists/<specialist_id>/equip', methods=['POST'])
    def equip_item(specialist_id):
        """Equip an item to a specialist."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            from src.core.equipment_system import EquipmentSystem
            from src.utils.json_loader import JSONLoader
            
            specialist = game_state.get_specialist_by_id(specialist_id)
            if not specialist:
                return jsonify({"success": False, "message": "Specialist not found"}), 404
            
            data = request.get_json()
            equipment_id = data.get('equipment_id')
            
            if not equipment_id:
                return jsonify({"success": False, "message": "equipment_id required"}), 400
            
            # Load equipment config
            json_loader = JSONLoader()
            equipment_config = json_loader.load_data("equipment")
            equipment_system = EquipmentSystem(equipment_config)
            
            # Get equipment
            equipment = equipment_system.get_equipment(equipment_id)
            if not equipment:
                return jsonify({"success": False, "message": "Equipment not found"}), 404
            
            # Equip item
            success = equipment_system.equip_item(specialist, equipment)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": f"Equipped {equipment.name}",
                    "data": specialist.to_dict(),
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Failed to equip item (not in inventory?)"
                }), 400
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/specialists/<specialist_id>/unequip', methods=['POST'])
    def unequip_item(specialist_id):
        """Unequip an item from a specialist."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            from src.core.equipment_system import EquipmentSystem
            from src.utils.json_loader import JSONLoader
            
            specialist = game_state.get_specialist_by_id(specialist_id)
            if not specialist:
                return jsonify({"success": False, "message": "Specialist not found"}), 404
            
            data = request.get_json()
            slot = data.get('slot')
            
            if not slot:
                return jsonify({"success": False, "message": "slot required"}), 400
            
            # Load equipment config
            json_loader = JSONLoader()
            equipment_config = json_loader.load_data("equipment")
            equipment_system = EquipmentSystem(equipment_config)
            
            # Unequip item
            unequipped = equipment_system.unequip_item(specialist, slot)
            
            if unequipped:
                return jsonify({
                    "success": True,
                    "message": f"Unequipped {unequipped.name}",
                    "data": specialist.to_dict(),
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "No item equipped in that slot"
                }), 400
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/equipment', methods=['GET'])
    def list_equipment():
        """List all equipment in the game."""
        try:
            from src.core.equipment_system import EquipmentSystem
            from src.utils.json_loader import JSONLoader
            
            json_loader = JSONLoader()
            equipment_config = json_loader.load_data("equipment")
            equipment_system = EquipmentSystem(equipment_config)
            
            equipment_data = [eq.to_dict() for eq in equipment_system.equipment_catalog.values()]
            
            return jsonify({
                "success": True,
                "data": equipment_data,
                "count": len(equipment_data),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/equipment/drop', methods=['POST'])
    def force_equipment_drop():
        """Force an equipment drop (for testing)."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            from src.core.equipment_system import EquipmentSystem
            from src.utils.json_loader import JSONLoader
            
            data = request.get_json()
            difficulty = data.get('difficulty', 3)
            rarity_boost = data.get('rarity_boost', 0.0)
            specialist_id = data.get('specialist_id')
            
            # Load equipment config
            json_loader = JSONLoader()
            equipment_config = json_loader.load_data("equipment")
            equipment_system = EquipmentSystem(equipment_config)
            
            # Generate drop
            dropped_equipment = equipment_system.generate_equipment_drop(difficulty, rarity_boost)
            
            if dropped_equipment:
                # Add to specialist inventory if specified
                if specialist_id:
                    specialist = game_state.get_specialist_by_id(specialist_id)
                    if specialist:
                        equipment_system.add_to_inventory(specialist, dropped_equipment)
                
                return jsonify({
                    "success": True,
                    "message": f"Dropped {dropped_equipment.name}",
                    "data": dropped_equipment.to_dict(),
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": True,
                    "message": "No equipment dropped",
                    "data": None,
                    "timestamp": datetime.utcnow().isoformat()
                })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    # ===== BURNOUT MANAGEMENT ENDPOINTS =====
    
    @bp.route('/specialists/<specialist_id>/burnout-status', methods=['GET'])
    def get_specialist_burnout_status(specialist_id):
        """Get burnout status for a specialist.
        
        Returns burnout level, tier, performance multiplier, error chance, and trauma count.
        """
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            specialist = game_state.get_specialist_by_id(specialist_id)
            if not specialist:
                return jsonify({"success": False, "message": "Specialist not found"}), 404
            
            # Get burnout status from burnout system
            if not game_state._burnout_system:
                return jsonify({"success": False, "message": "Burnout system not initialized"}), 500
            
            status = game_state._burnout_system.get_specialist_status(specialist_id)
            
            return jsonify({
                "success": True,
                "data": status,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/team/burnout-status', methods=['GET'])
    def get_team_burnout_status():
        """Get team-wide burnout statistics.
        
        Returns aggregate burnout data: average, critical specialists, intervention needed.
        """
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            if not game_state._burnout_system:
                return jsonify({"success": False, "message": "Burnout system not initialized"}), 500
            
            status = game_state._burnout_system.get_team_status()
            
            return jsonify({
                "success": True,
                "data": status,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/specialists/<specialist_id>/rest-day', methods=['POST'])
    def specialist_rest_day(specialist_id):
        """Specialist takes a rest day to recover from burnout.
        
        Recovers 30% of current burnout. No cost.
        """
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            specialist = game_state.get_specialist_by_id(specialist_id)
            if not specialist:
                return jsonify({"success": False, "message": "Specialist not found"}), 404
            
            if not game_state._burnout_system:
                return jsonify({"success": False, "message": "Burnout system not initialized"}), 500
            
            # Register if not already registered
            game_state._burnout_system.register_specialist(specialist_id)
            
            # Take rest day
            success, message = game_state._burnout_system.take_rest_day(specialist_id)
            
            if success:
                # Update specialist's burnout_level
                burnout = game_state._burnout_system.specialists[specialist_id]
                specialist.burnout_level = burnout.burnout_level
                
                return jsonify({
                    "success": True,
                    "message": message,
                    "data": game_state._burnout_system.get_specialist_status(specialist_id),
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "message": message
                }), 400
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/specialists/<specialist_id>/vacation', methods=['POST'])
    def specialist_vacation(specialist_id):
        """Send specialist on vacation to recover from burnout.
        
        Request JSON: {
            "days": int (1-5),
            "cost_per_day": int
        }
        
        Recovers 30% + 10% per day of burnout (up to 80%). Costs money.
        """
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            specialist = game_state.get_specialist_by_id(specialist_id)
            if not specialist:
                return jsonify({"success": False, "message": "Specialist not found"}), 404
            
            if not game_state._burnout_system:
                return jsonify({"success": False, "message": "Burnout system not initialized"}), 500
            
            data = request.get_json()
            days = data.get('days', 3)
            cost_per_day = data.get('cost_per_day', 100)
            
            # Validate input
            if not 1 <= days <= 5:
                return jsonify({
                    "success": False,
                    "message": "Days must be between 1 and 5"
                }), 400
            
            total_cost = days * cost_per_day
            if game_state.current_money < total_cost:
                return jsonify({
                    "success": False,
                    "message": f"Insufficient funds. Need {total_cost}, have {game_state.current_money}"
                }), 400
            
            # Register if not already registered
            game_state._burnout_system.register_specialist(specialist_id)
            
            # Take vacation
            success, message = game_state._burnout_system.take_vacation(
                specialist_id, 
                days=days, 
                cost_per_day=cost_per_day
            )
            
            if success:
                # Deduct cost
                game_state.current_money -= total_cost
                
                # Update specialist's burnout_level
                burnout = game_state._burnout_system.specialists[specialist_id]
                specialist.burnout_level = burnout.burnout_level
                
                return jsonify({
                    "success": True,
                    "message": message,
                    "data": {
                        "specialist_status": game_state._burnout_system.get_specialist_status(specialist_id),
                        "cost": total_cost,
                        "remaining_money": game_state.current_money
                    },
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "message": message
                }), 400
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/specialists/<specialist_id>/therapy', methods=['POST'])
    def specialist_therapy(specialist_id):
        """Specialist attends therapy to process trauma.
        
        Request JSON: {
            "cost": int (500+ recommended)
        }
        
        Clears all trauma (failed incidents) and recovers trauma-related burnout.
        """
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            specialist = game_state.get_specialist_by_id(specialist_id)
            if not specialist:
                return jsonify({"success": False, "message": "Specialist not found"}), 404
            
            if not game_state._burnout_system:
                return jsonify({"success": False, "message": "Burnout system not initialized"}), 500
            
            data = request.get_json()
            cost = data.get('cost', 500)
            
            # Validate input
            if cost < 0:
                return jsonify({
                    "success": False,
                    "message": "Cost cannot be negative"
                }), 400
            
            if game_state.current_money < cost:
                return jsonify({
                    "success": False,
                    "message": f"Insufficient funds. Need {cost}, have {game_state.current_money}"
                }), 400
            
            # Register if not already registered
            game_state._burnout_system.register_specialist(specialist_id)
            
            # Attend therapy
            success, message = game_state._burnout_system.attend_therapy(specialist_id, cost=cost)
            
            if success:
                # Deduct cost
                game_state.current_money -= cost
                
                # Update specialist's burnout_level
                burnout = game_state._burnout_system.specialists[specialist_id]
                specialist.burnout_level = burnout.burnout_level
                
                return jsonify({
                    "success": True,
                    "message": message,
                    "data": {
                        "specialist_status": game_state._burnout_system.get_specialist_status(specialist_id),
                        "cost": cost,
                        "remaining_money": game_state.current_money
                    },
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "message": message
                }), 400
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    return bp
