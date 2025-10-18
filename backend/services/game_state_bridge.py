"""Game State Bridge for Backend-Game Integration.

This module provides a bridge between the backend API server and the running game.
Since they run in separate processes, we use a shared state mechanism to keep them
synchronized.
"""

from typing import Optional, Dict, Any
import threading
import queue
import time


class GameStateBridge:
    """Bridge for synchronizing game state between backend and game client.
    
    This class acts as a message queue and state store that both the backend
    and game client can access to coordinate state changes.
    """
    
    def __init__(self):
        """Initialize the bridge."""
        self.game_state_ref: Optional[Any] = None
        self.command_queue: queue.Queue = queue.Queue()
        self.state_updates: queue.Queue = queue.Queue()
        
        # Lock for thread-safe access
        self.lock = threading.RLock()
        
        # Connection state
        self.game_connected = False
        self.last_heartbeat = 0.0
        
    def register_game_state(self, game_state: Any) -> None:
        """Register the game's GameState reference.
        
        Args:
            game_state: The game's GameState instance
        """
        with self.lock:
            self.game_state_ref = game_state
            self.game_connected = True
            self.last_heartbeat = time.time()
            
    def unregister_game_state(self) -> None:
        """Unregister the game state (game disconnected)."""
        with self.lock:
            self.game_state_ref = None
            self.game_connected = False
            
    def is_game_connected(self) -> bool:
        """Check if a game client is connected.
        
        Returns:
            True if game is connected
        """
        with self.lock:
            # Consider disconnected if no heartbeat in 10 seconds
            if self.game_connected:
                if time.time() - self.last_heartbeat > 10.0:
                    self.game_connected = False
            return self.game_connected
            
    def heartbeat(self) -> None:
        """Update heartbeat timestamp (called by game client)."""
        with self.lock:
            self.last_heartbeat = time.time()
            
    def get_game_state(self) -> Optional[Any]:
        """Get the game state reference.
        
        Returns:
            GameState instance or None if not connected
        """
        with self.lock:
            return self.game_state_ref
            
    def queue_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Queue a command for the game to execute.
        
        Args:
            command: Command name
            params: Optional parameters
        """
        self.command_queue.put({
            'command': command,
            'params': params or {},
            'timestamp': time.time()
        })
        
    def get_pending_commands(self) -> list:
        """Get all pending commands for the game.
        
        Returns:
            List of command dictionaries
        """
        commands = []
        try:
            while True:
                command = self.command_queue.get_nowait()
                commands.append(command)
        except queue.Empty:
            pass
        return commands
        
    def queue_state_update(self, updates: Dict[str, Any]) -> None:
        """Queue a state update from the game.
        
        Args:
            updates: State updates dictionary
        """
        self.state_updates.put({
            'updates': updates,
            'timestamp': time.time()
        })
        
    def get_pending_updates(self) -> list:
        """Get all pending state updates.
        
        Returns:
            List of update dictionaries
        """
        updates = []
        try:
            while True:
                update = self.state_updates.get_nowait()
                updates.append(update)
        except queue.Empty:
            pass
        return updates


# Global bridge instance
_game_state_bridge = GameStateBridge()


def get_game_state_bridge() -> GameStateBridge:
    """Get the global game state bridge instance.
    
    Returns:
        GameStateBridge instance
    """
    return _game_state_bridge
