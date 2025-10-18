"""Backend Integration System for Live Game State Synchronization.

This module provides integration between the running game and the backend API server,
enabling live debugging, state manipulation, and real-time synchronization.
"""

import requests
import threading
import time
from typing import Optional, Dict, Any, Callable
from src.utils.logger import GameLogger
from src.models.game_state import GameState


class BackendIntegration:
    """Handles integration between game and backend API server."""

    def __init__(self, host: str = "localhost", port: int = 5000, logger: Optional[GameLogger] = None):
        """Initialize backend integration.

        Args:
            host: Backend server host
            port: Backend server port
            logger: Optional logger instance
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.logger = logger or GameLogger("backend_integration")

        # Connection state
        self.connected = False
        self.game_state: Optional[GameState] = None

        # Synchronization settings
        self.sync_interval = 1.0  # seconds
        self.last_sync = 0.0
        self.sync_thread: Optional[threading.Thread] = None
        self.running = False

        # Callbacks for state changes
        self.state_change_callbacks: list[Callable] = []

        self.logger.logger.info(f"[BACKEND_INTEGRATION] Initialized with {self.base_url}")

    def connect(self, game_state: GameState) -> bool:
        """Connect to backend and provide game state reference.

        Args:
            game_state: The game state to synchronize

        Returns:
            True if connection successful
        """
        self.game_state = game_state

        try:
            # Test connection
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.connected = True
                self.logger.logger.info("[BACKEND_INTEGRATION] Connected to backend server")

                # Start synchronization thread
                self.running = True
                self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
                self.sync_thread.start()

                return True
            else:
                self.logger.logger.warning(f"[BACKEND_INTEGRATION] Backend health check failed: {response.status_code}")
                return False

        except requests.RequestException as e:
            self.logger.logger.warning(f"[BACKEND_INTEGRATION] Failed to connect to backend: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from backend."""
        self.running = False
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=2.0)

        self.connected = False
        self.game_state = None
        self.logger.logger.info("[BACKEND_INTEGRATION] Disconnected from backend")

    def _sync_loop(self) -> None:
        """Main synchronization loop."""
        while self.running:
            try:
                current_time = time.time()
                if current_time - self.last_sync >= self.sync_interval:
                    self._sync_state()
                    self.last_sync = current_time

                time.sleep(0.1)  # Small sleep to prevent busy waiting

            except Exception as e:
                self.logger.logger.error(f"[BACKEND_INTEGRATION] Sync error: {e}")
                time.sleep(1.0)  # Back off on errors

    def _sync_state(self) -> None:
        """Synchronize game state with backend."""
        if not self.game_state or not self.connected:
            return

        try:
            # Get current state from backend
            response = requests.get(f"{self.base_url}/api/state", timeout=2)
            if response.status_code == 200:
                backend_state = response.json()

                # Check for backend modifications
                if self._has_backend_changes(backend_state):
                    self._apply_backend_changes(backend_state)
                    self.logger.logger.debug("[BACKEND_INTEGRATION] Applied backend state changes")

        except requests.RequestException:
            # Backend might be temporarily unavailable
            pass
        except Exception as e:
            self.logger.logger.error(f"[BACKEND_INTEGRATION] State sync error: {e}")

    def _has_backend_changes(self, backend_state: Dict[str, Any]) -> bool:
        """Check if backend has changes that need to be applied to game.

        Args:
            backend_state: State from backend

        Returns:
            True if there are changes to apply
        """
        if not self.game_state:
            return False

        # Compare key state elements
        game_dict = self.game_state.to_dict()

        # Check money
        if abs(game_dict.get('current_money', 0) - backend_state.get('data', {}).get('current_money', 0)) > 0.01:
            return True

        # Check specialist count
        game_specialists = len(game_dict.get('specialists', []))
        backend_specialists = len(backend_state.get('data', {}).get('specialists', []))
        if game_specialists != backend_specialists:
            return True

        return False

    def _apply_backend_changes(self, backend_state: Dict[str, Any]) -> None:
        """Apply changes from backend to game state.

        Args:
            backend_state: State from backend
        """
        if not self.game_state:
            return

        data = backend_state.get('data', {})

        # Update money
        if 'current_money' in data:
            old_money = self.game_state.current_money
            self.game_state.current_money = data['current_money']
            if old_money != self.game_state.current_money:
                self.logger.logger.info(
                    f"[BACKEND_INTEGRATION] Money updated: "
                    f"${old_money:.2f} → ${self.game_state.current_money:.2f}"
                )

        # Notify callbacks
        for callback in self.state_change_callbacks:
            try:
                callback("backend_sync", data)
            except Exception as e:
                self.logger.logger.error(f"[BACKEND_INTEGRATION] Callback error: {e}")

    def add_state_change_callback(self, callback: Callable) -> None:
        """Add callback for state change notifications.

        Args:
            callback: Function to call when state changes
        """
        self.state_change_callbacks.append(callback)

    def get_backend_state(self) -> Optional[Dict[str, Any]]:
        """Get current state from backend.

        Returns:
            Backend state dict or None if unavailable
        """
        if not self.connected:
            return None

        try:
            response = requests.get(f"{self.base_url}/api/state", timeout=2)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass

        return None

    def update_backend_state(self, updates: Dict[str, Any]) -> bool:
        """Update backend state with changes.

        Args:
            updates: State updates to apply

        Returns:
            True if update successful
        """
        if not self.connected:
            return False

        try:
            response = requests.put(
                f"{self.base_url}/api/state",
                json=updates,
                timeout=2
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def trigger_backend_action(self, action: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """Trigger an action on the backend.

        Args:
            action: Action to trigger
            params: Optional parameters

        Returns:
            True if action successful
        """
        if not self.connected:
            return False

        try:
            payload = {"action": action}
            if params:
                payload.update(params)

            response = requests.post(
                f"{self.base_url}/api/actions",
                json=payload,
                timeout=2
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def is_connected(self) -> bool:
        """Check if backend is connected.

        Returns:
            True if connected
        """
        return self.connected

    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information.

        Returns:
            Connection status and info
        """
        return {
            "connected": self.connected,
            "host": self.host,
            "port": self.port,
            "base_url": self.base_url,
            "sync_interval": self.sync_interval,
            "last_sync": self.last_sync
        }


# Global backend integration instance
_backend_integration = None


def get_backend_integration() -> Optional[BackendIntegration]:
    """Get the global backend integration instance.

    Returns:
        BackendIntegration instance or None if not initialized
    """
    return _backend_integration


def initialize_backend_integration(
    host: str = "localhost",
    port: int = 5000,
    logger: Optional[GameLogger] = None
) -> BackendIntegration:
    """Initialize the global backend integration.

    Args:
        host: Backend server host
        port: Backend server port
        logger: Optional logger instance

    Returns:
        BackendIntegration instance
    """
    global _backend_integration
    _backend_integration = BackendIntegration(host, port, logger)
    return _backend_integration


def connect_to_backend(game_state: GameState) -> bool:
    """Connect game to backend for live synchronization.

    Args:
        game_state: Game state to synchronize

    Returns:
        True if connection successful
    """
    if _backend_integration:
        return _backend_integration.connect(game_state)
    return False