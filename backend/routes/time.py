"""Time manipulation API routes.

Provides endpoints for controlling game time (pause, speed, fast-forward).
"""
from flask import Blueprint, jsonify, request
from datetime import datetime


def create_time_blueprint(game_state_ref):
    """Create the time blueprint."""
    bp = Blueprint('time', __name__)
    state_container = {'game_state': game_state_ref}
    
    def get_game_state():
        return state_container.get('game_state')
    
    @bp.route('/time/pause', methods=['POST'])
    def pause_game():
        """Pause the game."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            game_state.paused = True
            
            return jsonify({
                "success": True,
                "message": "Game paused",
                "data": {"paused": True},
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/time/resume', methods=['POST'])
    def resume_game():
        """Resume the game."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            game_state.paused = False
            
            return jsonify({
                "success": True,
                "message": "Game resumed",
                "data": {"paused": False},
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/time/speed', methods=['POST'])
    def set_game_speed():
        """Set game speed multiplier."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            data = request.get_json()
            speed = data.get('speed', 1.0)
            
            # Clamp speed to reasonable range
            speed = max(0.1, min(speed, 10.0))
            
            game_state.time_scale = speed
            
            return jsonify({
                "success": True,
                "message": f"Game speed set to {speed}x",
                "data": {"time_scale": speed},
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/time/advance', methods=['POST'])
    def fast_forward():
        """Fast-forward time by specified seconds."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            data = request.get_json()
            seconds = data.get('seconds', 60)
            
            # Clamp to reasonable range
            seconds = max(1, min(seconds, 3600))  # Max 1 hour
            
            # Call update multiple times to simulate passage of time
            # Use small delta_time increments for accuracy
            # Use larger increments for efficiency, but not more than 10 seconds
            increment = min(10.0, seconds)
            num_full_steps = int(seconds // increment)
            remainder = seconds % increment
            for _ in range(num_full_steps):
                game_state.update(increment)
            if remainder > 0:
                game_state.update(remainder)
            
            return jsonify({
                "success": True,
                "message": f"Fast-forwarded {seconds} seconds",
                "data": {
                    "seconds_advanced": seconds,
                    "game_time_elapsed": game_state.get_game_time_elapsed()
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/time/status', methods=['GET'])
    def get_time_status():
        """Get current time status."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            return jsonify({
                "success": True,
                "data": {
                    "paused": game_state.paused,
                    "time_scale": game_state.time_scale,
                    "game_time_elapsed": game_state.get_game_time_elapsed(),
                    "real_time_elapsed": game_state.real_time_elapsed
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    return bp
