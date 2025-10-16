"""Game State API routes.

Provides endpoints for managing the overall game state.
"""
from flask import Blueprint, jsonify, request
from datetime import datetime


def create_state_blueprint(game_state_ref):
    """Create the state blueprint with game state reference.
    
    Args:
        game_state_ref: Reference to the GameState instance (can be None initially)
    
    Returns:
        Flask Blueprint for state routes
    """
    bp = Blueprint('state', __name__)
    
    # Store reference that can be updated
    state_container = {'game_state': game_state_ref}
    
    def get_game_state():
        """Helper to get current game state."""
        return state_container.get('game_state')
    
    @bp.route('/state', methods=['GET'])
    def get_state():
        """Get full game state snapshot."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            state_dict = game_state.to_dict()
            return jsonify({
                "success": True,
                "data": state_dict,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to get game state: {str(e)}"
            }), 500
    
    @bp.route('/state', methods=['PUT'])
    def update_state():
        """Update game state with provided data."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            data = request.get_json()
            
            # Update various state properties
            if 'money' in data:
                game_state.current_money = float(data['money'])
            
            if 'current_money' in data:
                game_state.current_money = float(data['current_money'])
            
            if 'paused' in data:
                game_state.paused = bool(data['paused'])
            
            if 'time_scale' in data:
                game_state.time_scale = float(data['time_scale'])
            
            return jsonify({
                "success": True,
                "message": "Game state updated successfully",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to update game state: {str(e)}"
            }), 500
    
    @bp.route('/state/reset', methods=['POST'])
    def reset_state():
        """Reset game state to initial values."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            # Reload initial data
            # Prefer public API for resetting game state
            if hasattr(game_state, "reset") and callable(getattr(game_state, "reset")):
                game_state.reset()
            elif hasattr(game_state, "reload_initial_data") and callable(getattr(game_state, "reload_initial_data")):
                game_state.reload_initial_data()
            else:
                # Fallback: direct call to private method (should be replaced with public API)
                game_state._load_initial_data()
            
            return jsonify({
                "success": True,
                "message": "Game state reset successfully",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to reset game state: {str(e)}"
            }), 500
    
    @bp.route('/state/save', methods=['POST'])
    def save_state():
        """Save game state to file."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            from src.core.save_manager import SaveManager
            
            data = request.get_json() or {}
            slot = data.get('slot', 1)  # Default to slot 1 (not auto-save)
            
            save_manager = SaveManager()
            filepath = save_manager.save_game(game_state, slot)
            
            # Get save metadata
            saves = save_manager.list_saves()
            save_info = next((s for s in saves if s['slot'] == slot), None)
            
            return jsonify({
                "success": True,
                "message": f"Game state saved to slot {slot}",
                "data": {
                    "slot": slot,
                    "filepath": filepath,
                    "metadata": save_info.get('metadata') if save_info else None
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to save game state: {str(e)}"
            }), 500
    
    @bp.route('/state/load', methods=['POST'])
    def load_state():
        """Load game state from file."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            from src.core.save_manager import SaveManager
            
            data = request.get_json() or {}
            slot = data.get('slot', 1)
            
            save_manager = SaveManager()
            new_state = save_manager.load_game(slot)
            
            # Update the state container reference
            state_container['game_state'] = new_state
            
            return jsonify({
                "success": True,
                "message": f"Game state loaded from slot {slot}",
                "data": {
                    "slot": slot,
                    "money": new_state.current_money,
                    "specialists": len(new_state.specialists),
                    "prestige_level": getattr(new_state, 'total_prestiges', 0)
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except FileNotFoundError as e:
            return jsonify({
                "success": False,
                "message": f"Save file not found for slot {slot}"
            }), 404
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to load game state: {str(e)}"
            }), 500
    
    @bp.route('/saves', methods=['GET'])
    def list_save_files():
        """List all save files."""
        try:
            from src.core.save_manager import SaveManager
            
            save_manager = SaveManager()
            saves = save_manager.list_saves()
            
            return jsonify({
                "success": True,
                "data": saves,
                "count": len([s for s in saves if s.get('exists', False)]),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to list saves: {str(e)}"
            }), 500
    
    @bp.route('/saves/<int:slot>', methods=['DELETE'])
    def delete_save_file(slot):
        """Delete a save file."""
        try:
            from src.core.save_manager import SaveManager
            
            save_manager = SaveManager()
            deleted = save_manager.delete_save(slot)
            
            if deleted:
                return jsonify({
                    "success": True,
                    "message": f"Save slot {slot} deleted",
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Save file not found"
                }), 404
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to delete save: {str(e)}"
            }), 500
    
    @bp.route('/state/summary', methods=['GET'])
    def get_summary():
        """Get game state summary (lightweight)."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            summary = game_state.get_game_summary()
            return jsonify({
                "success": True,
                "data": summary,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to get game summary: {str(e)}"
            }), 500
    
    @bp.route('/prestige/calculate', methods=['GET'])
    def calculate_prestige():
        """Calculate prestige points if reset now."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            # Load prestige upgrades if not already loaded
            if not hasattr(game_state, '_prestige_system') or not game_state._prestige_system:
                from src.utils.json_loader import JSONLoader
                from src.models.prestige import PrestigeUpgrade
                from src.core.prestige_system import PrestigeSystem
                
                json_loader = JSONLoader()
                prestige_data = json_loader.load_data("prestige_upgrades")
                prestige_upgrades = [PrestigeUpgrade.from_dict(u) for u in prestige_data.get("prestige_upgrades", [])]
                game_state._prestige_system = PrestigeSystem(prestige_upgrades, game_state._logger)
            
            points = game_state._prestige_system.calculate_prestige_points(game_state)
            
            return jsonify({
                "success": True,
                "data": {
                    "prestige_points_to_earn": points,
                    "current_prestige_points": getattr(game_state, 'prestige_points', 0),
                    "total_after_prestige": getattr(game_state, 'prestige_points', 0) + points
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to calculate prestige: {str(e)}"
            }), 500
    
    @bp.route('/prestige/perform', methods=['POST'])
    def perform_prestige():
        """Perform prestige reset."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            # Load prestige system if not already loaded
            if not hasattr(game_state, '_prestige_system') or not game_state._prestige_system:
                from src.utils.json_loader import JSONLoader
                from src.models.prestige import PrestigeUpgrade
                from src.core.prestige_system import PrestigeSystem
                
                json_loader = JSONLoader()
                prestige_data = json_loader.load_data("prestige_upgrades")
                prestige_upgrades = [PrestigeUpgrade.from_dict(u) for u in prestige_data.get("prestige_upgrades", [])]
                game_state._prestige_system = PrestigeSystem(prestige_upgrades, game_state._logger)
            
            # Perform prestige
            new_state = game_state._prestige_system.perform_prestige(game_state)
            
            # Update the state container reference
            state_container['game_state'] = new_state
            
            return jsonify({
                "success": True,
                "message": "Prestige performed successfully",
                "data": {
                    "prestige_points": new_state.prestige_points,
                    "total_prestiges": new_state.total_prestiges
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to perform prestige: {str(e)}"
            }), 500
    
    @bp.route('/prestige/upgrades', methods=['GET'])
    def list_prestige_upgrades():
        """List all prestige upgrades."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            # Load prestige system if not already loaded
            if not hasattr(game_state, '_prestige_system') or not game_state._prestige_system:
                from src.utils.json_loader import JSONLoader
                from src.models.prestige import PrestigeUpgrade
                from src.core.prestige_system import PrestigeSystem
                
                json_loader = JSONLoader()
                prestige_data = json_loader.load_data("prestige_upgrades")
                prestige_upgrades = [PrestigeUpgrade.from_dict(u) for u in prestige_data.get("prestige_upgrades", [])]
                game_state._prestige_system = PrestigeSystem(prestige_upgrades, game_state._logger)
            
            upgrades = game_state._prestige_system.get_available_upgrades(game_state)
            
            return jsonify({
                "success": True,
                "data": upgrades,
                "count": len(upgrades),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to get prestige upgrades: {str(e)}"
            }), 500
    
    @bp.route('/prestige/upgrades/<upgrade_id>/purchase', methods=['POST'])
    def purchase_prestige_upgrade(upgrade_id):
        """Purchase a prestige upgrade."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            # Load prestige system if not already loaded
            if not hasattr(game_state, '_prestige_system') or not game_state._prestige_system:
                from src.utils.json_loader import JSONLoader
                from src.models.prestige import PrestigeUpgrade
                from src.core.prestige_system import PrestigeSystem
                
                json_loader = JSONLoader()
                prestige_data = json_loader.load_data("prestige_upgrades")
                prestige_upgrades = [PrestigeUpgrade.from_dict(u) for u in prestige_data.get("prestige_upgrades", [])]
                game_state._prestige_system = PrestigeSystem(prestige_upgrades, game_state._logger)
            
            result = game_state._prestige_system.purchase_prestige_upgrade(upgrade_id, game_state)
            
            if result['success']:
                return jsonify({
                    "success": True,
                    "message": f"Prestige upgrade purchased: level {result['new_level']}",
                    "data": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "message": result.get('error', 'Purchase failed'),
                    "data": result,
                    "timestamp": datetime.utcnow().isoformat()
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to purchase prestige upgrade: {str(e)}"
            }), 500
    
    @bp.route('/offline-progress', methods=['GET'])
    def get_offline_progress():
        """Get offline progress report."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            report = game_state.get_offline_progress_report()
            
            if report:
                return jsonify({
                    "success": True,
                    "data": report,
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": True,
                    "message": "No offline progress to report",
                    "data": None,
                    "timestamp": datetime.utcnow().isoformat()
                })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to get offline progress: {str(e)}"
            }), 500
    
    @bp.route('/offline-progress/simulate', methods=['POST'])
    def simulate_offline_progress():
        """Simulate offline progress (testing/admin)."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            data = request.get_json() or {}
            time_elapsed = data.get('time_elapsed', 3600)  # Default 1 hour
            
            if hasattr(game_state, '_offline_progress_system') and game_state._offline_progress_system:
                report = game_state._offline_progress_system.calculate_offline_progress(game_state, time_elapsed)
                
                return jsonify({
                    "success": True,
                    "message": f"Simulated {time_elapsed/3600:.1f} hours of offline progress",
                    "data": report,
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Offline progress system not available"
                }), 503
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to simulate offline progress: {str(e)}"
            }), 500
    
    return bp
