"""Main Flask application for the backend API server.

This module provides a REST API for live debugging and manipulation of game state.
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from typing import Optional
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import BackendConfig
from src.utils.logger import GameLogger
from backend.services.websocket_service import ws_service


class BackendApp:
    """Flask application wrapper for the game backend API."""
    
    def __init__(self, game_state=None):
        """Initialize the backend application.
        
        Args:
            game_state: Optional GameState instance to manage
        """
        # Set up Flask with static folder
        static_folder = os.path.join(os.path.dirname(__file__), 'static')
        self.app = Flask(__name__, static_folder=static_folder, static_url_path='/static')
        self.logger = GameLogger("backend")
        self.game_state = game_state
        
        # Configure CORS
        CORS(self.app, origins=BackendConfig.CORS_ORIGINS)
        
        # Initialize SocketIO for WebSocket support
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins=BackendConfig.CORS_ORIGINS,
            async_mode='threading',
            ping_interval=BackendConfig.WEBSOCKET_PING_INTERVAL,
            ping_timeout=BackendConfig.WEBSOCKET_PING_TIMEOUT
        )
        
        # Initialize WebSocket service
        ws_service.init_app(self.app, self.socketio)
        
        # Register routes
        self._register_routes()
        
        self.logger.logger.info("[BACKEND] Backend API initialized with WebSocket support")
    
    def _register_routes(self):
        """Register all API routes."""
        
        @self.app.route("/")
        def index():
            """Root endpoint - serve control panel."""
            return send_from_directory(self.app.static_folder, 'control-panel.html')
        
        @self.app.route("/admin")
        def admin():
            """Legacy admin dashboard endpoint."""
            return send_from_directory(self.app.static_folder, 'admin.html')
        
        @self.app.route("/control-panel")
        def control_panel():
            """New ultimate control panel endpoint."""
            return send_from_directory(self.app.static_folder, 'control-panel.html')
        
        @self.app.route("/health")
        def health():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "game_state_loaded": self.game_state is not None
            })
        
        @self.app.route(f"{BackendConfig.API_PREFIX}/game/register", methods=['POST'])
        def register_game():
            """Register a game client's GameState with the backend.
            
            This endpoint is called by the game client to provide its GameState
            reference to the backend for live control.
            
            Note: In Python, we can't pass object references via HTTP, so this
            endpoint confirms the game is running and ready for control.
            """
            return jsonify({
                "success": True,
                "message": "Game registration acknowledged",
                "backend_ready": True
            })
        
        @self.app.route(f"{BackendConfig.API_PREFIX}/config")
        def get_config():
            """Get backend configuration."""
            return jsonify({
                "success": True,
                "data": BackendConfig.to_dict()
            })
        
        # Import and register route blueprints
        from backend.routes.state import create_state_blueprint
        from backend.routes.specialists import create_specialists_blueprint
        from backend.routes.incidents import create_incidents_blueprint
        from backend.routes.clients import (
            create_clients_blueprint,
            create_contracts_blueprint,
            create_facilities_blueprint
        )
        from backend.routes.economy import create_economy_blueprint
        from backend.routes.automation import create_automation_blueprint
        from backend.routes.config_routes import create_config_blueprint
        from backend.routes.time import create_time_blueprint
        from backend.routes.analytics import create_analytics_blueprint
        from backend.routes.godmode import create_godmode_blueprint
        from backend.routes.entity_management import create_entity_management_blueprint
        from backend.routes.game_integration import create_game_integration_blueprint
        from backend.routes.schemas import create_schemas_blueprint
        from backend.routes.actions import create_actions_blueprint
        
        # Register blueprints with game_state reference
        self.app.register_blueprint(
            create_state_blueprint(self.game_state),
            url_prefix=BackendConfig.API_PREFIX
        )
        self.app.register_blueprint(
            create_specialists_blueprint(self.game_state),
            url_prefix=BackendConfig.API_PREFIX
        )
        self.app.register_blueprint(
            create_incidents_blueprint(self.game_state),
            url_prefix=BackendConfig.API_PREFIX
        )
        self.app.register_blueprint(
            create_clients_blueprint(self.game_state),
            url_prefix=BackendConfig.API_PREFIX
        )
        self.app.register_blueprint(
            create_contracts_blueprint(self.game_state),
            url_prefix=BackendConfig.API_PREFIX
        )
        self.app.register_blueprint(
            create_facilities_blueprint(self.game_state),
            url_prefix=BackendConfig.API_PREFIX
        )
        self.app.register_blueprint(
            create_economy_blueprint(self.game_state),
            url_prefix=BackendConfig.API_PREFIX
        )
        self.app.register_blueprint(
            create_automation_blueprint(self.game_state),
            url_prefix=BackendConfig.API_PREFIX
        )
        self.app.register_blueprint(
            create_config_blueprint(self.game_state),
            url_prefix=BackendConfig.API_PREFIX
        )
        self.app.register_blueprint(
            create_time_blueprint(self.game_state),
            url_prefix=BackendConfig.API_PREFIX
        )
        self.app.register_blueprint(
            create_analytics_blueprint(self.game_state),
            url_prefix=BackendConfig.API_PREFIX
        )
        self.app.register_blueprint(
            create_godmode_blueprint(self.game_state),
            url_prefix=BackendConfig.API_PREFIX
        )
        self.app.register_blueprint(
            create_entity_management_blueprint(self.game_state),
            url_prefix=BackendConfig.API_PREFIX
        )
        self.app.register_blueprint(
            create_game_integration_blueprint(self.game_state),
            url_prefix=BackendConfig.API_PREFIX
        )
        self.app.register_blueprint(
            create_schemas_blueprint(),
            url_prefix=BackendConfig.API_PREFIX
        )
        self.app.register_blueprint(
            create_actions_blueprint(self.game_state),
            url_prefix=BackendConfig.API_PREFIX
        )
        
        self.logger.logger.info("[BACKEND] All routes registered")
    
    def set_game_state(self, game_state):
        """Update the game state reference.
        
        This allows the running game to provide its GameState to the backend
        for live manipulation and control.
        
        Args:
            game_state: GameState instance
        """
        self.game_state = game_state
        self.logger.logger.info("[BACKEND] Game state reference updated")
        
        # Broadcast to connected clients
        ws_service.broadcast('game_connected', {
            'message': 'Game client connected with shared state',
            'specialists': len(game_state.specialists) if game_state else 0,
            'money': game_state.current_money if game_state else 0
        })
    
    def run(self, host: Optional[str] = None, port: Optional[int] = None, debug: Optional[bool] = None):
        """Run the Flask development server with SocketIO.
        
        Args:
            host: Host to bind to (default: from config)
            port: Port to bind to (default: from config)
            debug: Enable debug mode (default: from config)
        """
        host = host or BackendConfig.HOST
        port = port or BackendConfig.PORT
        debug = debug if debug is not None else BackendConfig.DEBUG
        
        self.logger.logger.info(f"[BACKEND] Starting server on {host}:{port} (debug={debug})")
        self.socketio.run(self.app, host=host, port=port, debug=debug, use_reloader=False)


def create_app(game_state=None):
    """Factory function to create Flask app instance.
    
    Args:
        game_state: Optional GameState instance
        
    Returns:
        Flask application instance
    """
    backend = BackendApp(game_state)
    return backend.app


if __name__ == "__main__":
    # Run standalone for testing
    app = create_app()
    app.run(host=BackendConfig.HOST, port=BackendConfig.PORT, debug=BackendConfig.DEBUG)
