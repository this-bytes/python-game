"""Local embedded backend server for standalone mode.

This module provides a local Flask server that runs in a separate thread,
enabling the admin panel and backend API while keeping game logic authoritative.
"""
import sys
import os
import threading
import time
from typing import Optional
from flask import Flask

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend')
sys.path.insert(0, backend_dir)

from backend.app import BackendApp
from src.utils.logger import GameLogger
from src.models.game_state import GameState


class LocalServerLauncher:
    """Manages embedded local backend server in separate thread."""
    # Explicit attribute annotations for static analysis and clarity
    backend_app: Optional[BackendApp]
    server_thread: Optional[threading.Thread]
    game_state: Optional[GameState]
    logger: GameLogger
    running: bool
    started: threading.Event
    
    def __init__(self, port: int = 5001, game_state: Optional[GameState] = None):
        """Initialize local server launcher.
        
        Args:
            port: Port to run server on (default: 5001)
            game_state: Optional GameState instance to provide to backend
        """
        self.port = port
        self.game_state = game_state
        self.logger = GameLogger("local_server")
        
        self.backend_app: Optional[BackendApp] = None
        self.server_thread: Optional[threading.Thread] = None
        self.running = False
        self.started = threading.Event()
        
    def start(self) -> bool:
        """Start local backend server in separate thread.
        
        Returns:
            True if server started successfully, False otherwise
        """
        try:
            self.logger.info(f"[LOCAL_SERVER] Starting embedded backend server on port {self.port}...")
            
            # Create backend app with game state
            self.backend_app = BackendApp(game_state=self.game_state)
            
            # Create server thread
            self.server_thread = threading.Thread(
                target=self._run_server,
                daemon=True,
                name="LocalBackendServer"
            )
            
            self.running = True
            self.server_thread.start()
            
            # Wait for server to start (with timeout)
            if not self.started.wait(timeout=5.0):
                self.logger.error("[LOCAL_SERVER] Server failed to start within timeout")
                return False

            self.logger.info("[LOCAL_SERVER] ✅ Embedded backend server started successfully")
            self.logger.info(f"[LOCAL_SERVER] 🌐 Admin panel: http://localhost:{self.port}/control-panel")
            self.logger.info(f"[LOCAL_SERVER] 📡 API base: http://localhost:{self.port}/api")
            
            return True
            
        except Exception as e:
            self.logger.error(f"[LOCAL_SERVER] Failed to start server: {e}")
            return False
    
    def _run_server(self):
        """Run Flask server in thread (internal method)."""
        try:
            # Disable Flask's startup messages in production
            import logging
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
            
            self.logger.info(f"[LOCAL_SERVER] Server thread running on port {self.port}")
            
            # Signal that server is starting
            self.started.set()

            # Run SocketIO server (ensure backend_app exists)
            if not self.backend_app:
                self.logger.error("[LOCAL_SERVER] No backend_app available to run")
                self.running = False
                return

            self.backend_app.socketio.run(
                self.backend_app.app,
                host='0.0.0.0',
                port=self.port,
                debug=False,
                use_reloader=False,
                allow_unsafe_werkzeug=True
            )
            
        except Exception as e:
            self.logger.error(f"[LOCAL_SERVER] Server thread error: {e}")
            self.running = False
    
    def stop(self):
        """Stop local backend server."""
        if not self.running:
            return
        self.logger.info("[LOCAL_SERVER] Stopping embedded backend server...")
        self.running = False

        # Note: Flask/SocketIO doesn't have a clean shutdown method from another thread
        # The daemon thread will be terminated when the main process exits

        self.logger.info("[LOCAL_SERVER] Server stopped")
    
    def update_game_state(self, game_state: GameState):
        """Update game state reference in backend.
        
        Args:
            game_state: New GameState instance
        """
        if self.backend_app:
            self.backend_app.game_state = game_state
            self.logger.debug("[LOCAL_SERVER] Game state reference updated")
    
    def is_running(self) -> bool:
        """Check if server is running.
        
        Returns:
            True if server thread is active
        """
        if not self.running:
            return False

        if not self.server_thread:
            return False

        return bool(self.server_thread.is_alive())
    
    def get_url(self) -> str:
        """Get server base URL.
        
        Returns:
            Server URL (e.g., 'http://localhost:5001')
        """
        return f"http://localhost:{self.port}"
    
    def get_admin_url(self) -> str:
        """Get admin panel URL.
        
        Returns:
            Admin panel URL
        """
        return f"{self.get_url()}/control-panel"


def launch_local_server(port: int = 5001, game_state: Optional[GameState] = None) -> Optional[LocalServerLauncher]:
    """Launch local embedded backend server.
    
    Args:
        port: Port to run server on (default: 5001)
        game_state: Optional GameState instance
        
    Returns:
        LocalServerLauncher instance if successful, None otherwise
    """
    launcher = LocalServerLauncher(port=port, game_state=game_state)
    
    if launcher.start():
        return launcher
    
    return None
