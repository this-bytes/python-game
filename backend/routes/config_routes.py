"""Configuration management API routes.

Provides endpoints for hot-reloading JSON configuration files.
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import os
import json


def create_config_blueprint(game_state_ref):
    """Create the config blueprint."""
    bp = Blueprint('config_routes', __name__)
    state_container = {'game_state': game_state_ref}
    
    def get_game_state():
        return state_container.get('game_state')
    
    @bp.route('/config/reload', methods=['POST'])
    def reload_config():
        """Hot-reload all JSON configuration files."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            # Reload initial data
            game_state._load_initial_data()
            
            # Reload incident generator configuration
            if hasattr(game_state, 'incident_generator'):
                game_state.incident_generator.reload_configuration()
            
            return jsonify({
                "success": True,
                "message": "Configuration reloaded successfully",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/config/files', methods=['GET'])
    def list_config_files():
        """List available configuration files."""
        try:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
            config_files = []
            
            for filename in os.listdir(data_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(data_dir, filename)
                    config_files.append({
                        "name": filename,
                        "path": filepath,
                        "size": os.path.getsize(filepath)
                    })
            
            return jsonify({
                "success": True,
                "data": config_files,
                "count": len(config_files),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/config/files/<filename>', methods=['GET'])
    def get_config_file(filename):
        """Get content of a specific configuration file."""
        try:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
            filepath = os.path.join(data_dir, filename)
            
            if not os.path.exists(filepath):
                return jsonify({"success": False, "message": "File not found"}), 404
            
            with open(filepath, 'r') as f:
                content = json.load(f)
            
            return jsonify({
                "success": True,
                "data": {
                    "filename": filename,
                    "content": content
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/config/files/<filename>', methods=['PUT'])
    def update_config_file(filename):
        """Update a configuration file (DANGEROUS - use with caution)."""
        try:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
            filepath = os.path.join(data_dir, filename)
            
            data = request.get_json()
            content = data.get('content')
            
            if not content:
                return jsonify({"success": False, "message": "Content required"}), 400
            
            # Backup original file
            backup_path = filepath + '.backup'
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    backup_content = f.read()
                with open(backup_path, 'w') as f:
                    f.write(backup_content)
            
            # Write new content
            with open(filepath, 'w') as f:
                json.dump(content, f, indent=2)
            
            return jsonify({
                "success": True,
                "message": f"Configuration file {filename} updated successfully (backup created)",
                "backup_path": backup_path,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    return bp
