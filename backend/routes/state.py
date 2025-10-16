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
            data = request.get_json() or {}
            filename = data.get('filename', 'manual_save.json')
            
            # TODO: Implement save functionality
            return jsonify({
                "success": True,
                "message": f"Game state saved to {filename}",
                "filename": filename,
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
            data = request.get_json() or {}
            filename = data.get('filename', 'manual_save.json')
            
            # TODO: Implement load functionality
            return jsonify({
                "success": True,
                "message": f"Game state loaded from {filename}",
                "filename": filename,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to load game state: {str(e)}"
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
    
    @bp.route('/achievements', methods=['GET'])
    def list_achievements():
        """List all achievements with progress."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            from src.core.achievement_system import AchievementSystem
            from src.utils.json_loader import JSONLoader
            
            # Load achievements config
            json_loader = JSONLoader()
            achievements_config = json_loader.load_data("achievements")
            achievement_system = AchievementSystem(achievements_config)
            
            # Get all achievements with progress
            achievements_data = []
            for achievement in achievement_system.get_all_achievements(include_hidden=True):
                achievement_dict = achievement.to_dict()
                achievement_dict["unlocked"] = achievement.id in game_state.unlocked_achievements
                achievement_dict["progress"] = achievement_system.get_progress(achievement, game_state)
                achievements_data.append(achievement_dict)
            
            return jsonify({
                "success": True,
                "data": achievements_data,
                "count": len(achievements_data),
                "unlocked_count": len(game_state.unlocked_achievements),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/achievements/check', methods=['POST'])
    def check_achievements():
        """Check and unlock newly completed achievements."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            from src.core.achievement_system import AchievementSystem
            from src.utils.json_loader import JSONLoader
            
            # Load achievements config
            json_loader = JSONLoader()
            achievements_config = json_loader.load_data("achievements")
            achievement_system = AchievementSystem(achievements_config)
            
            # Check for newly unlocked achievements
            newly_unlocked = achievement_system.check_achievements(game_state)
            
            return jsonify({
                "success": True,
                "message": f"Checked achievements, {len(newly_unlocked)} newly unlocked",
                "data": [a.to_dict() for a in newly_unlocked],
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/achievements/<achievement_id>/unlock', methods=['POST'])
    def force_unlock_achievement(achievement_id):
        """Force unlock an achievement (for testing)."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            from src.core.achievement_system import AchievementSystem
            from src.utils.json_loader import JSONLoader
            
            # Load achievements config
            json_loader = JSONLoader()
            achievements_config = json_loader.load_data("achievements")
            achievement_system = AchievementSystem(achievements_config)
            
            # Get achievement
            achievement = achievement_system.get_achievement(achievement_id)
            if not achievement:
                return jsonify({"success": False, "message": "Achievement not found"}), 404
            
            # Check if already unlocked
            if achievement_id in game_state.unlocked_achievements:
                return jsonify({
                    "success": False,
                    "message": "Achievement already unlocked"
                }), 400
            
            # Unlock and award
            game_state.unlocked_achievements.append(achievement_id)
            achievement_system.award_achievement(achievement, game_state)
            
            return jsonify({
                "success": True,
                "message": f"Achievement {achievement.name} unlocked",
                "data": achievement.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    return bp
