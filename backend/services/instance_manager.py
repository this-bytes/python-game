"""Game Instance Manager for multi-client backend architecture.

Manages multiple game instances, each with their own GameState, allowing the
backend to serve multiple concurrent game sessions and enable admin panel
to select and control specific instances.
"""
import uuid
import time
from typing import Dict, Optional, List
from datetime import datetime
from src.utils.logger import GameLogger
from src.models.game_state import GameState


class GameInstance:
    """Represents a single game instance/session."""
    
    def __init__(self, instance_id: str, game_state: Optional[GameState] = None, 
                 client_name: Optional[str] = None):
        """Initialize game instance.
        
        Args:
            instance_id: Unique identifier for this instance
            game_state: GameState object for this instance
            client_name: Optional friendly name for the client
        """
        self.instance_id = instance_id
        self.game_state = game_state
        self.client_name = client_name or f"Client-{instance_id[:8]}"
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.connected = True
        
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert instance info to dictionary.
        
        Returns:
            Dictionary with instance metadata
        """
        return {
            'instance_id': self.instance_id,
            'client_name': self.client_name,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'connected': self.connected,
            'has_state': self.game_state is not None,
            'state_summary': self._get_state_summary() if self.game_state else None
        }
    
    def _get_state_summary(self) -> dict:
        """Get summary of game state.
        
        Returns:
            Summary dictionary with key metrics
        """
        if not self.game_state:
            return None
        
        return {
            'money': self.game_state.current_money,
            'specialists': len(self.game_state.specialists),
            'incidents': len([i for i in self.game_state.incidents if i.status in ['pending', 'assigned']]),
            'prestige_level': getattr(self.game_state, 'total_prestiges', 0)
        }


class InstanceManager:
    """Manages multiple game instances for multi-client support."""
    
    def __init__(self):
        """Initialize instance manager."""
        self.instances: Dict[str, GameInstance] = {}
        self.logger = GameLogger("instance_manager")
        self._default_instance_id: Optional[str] = None
        
    def create_instance(self, instance_id: Optional[str] = None, 
                       game_state: Optional[GameState] = None,
                       client_name: Optional[str] = None) -> str:
        """Create a new game instance.
        
        Args:
            instance_id: Optional specific instance ID, or generate new UUID
            game_state: Optional GameState for this instance
            client_name: Optional friendly name for the client
            
        Returns:
            Instance ID of created instance
        """
        if instance_id is None:
            instance_id = str(uuid.uuid4())
        
        instance = GameInstance(instance_id, game_state, client_name)
        self.instances[instance_id] = instance
        
        # Set as default if first instance
        if self._default_instance_id is None:
            self._default_instance_id = instance_id
        
        self.logger.logger.info(
            f"[INSTANCE_MANAGER] Created instance: {instance_id} ({client_name})"
        )
        
        return instance_id
    
    def get_instance(self, instance_id: Optional[str] = None) -> Optional[GameInstance]:
        """Get a specific game instance.
        
        Args:
            instance_id: Instance ID, or None to get default instance
            
        Returns:
            GameInstance or None if not found
        """
        if instance_id is None:
            instance_id = self._default_instance_id
        
        if instance_id is None:
            return None
        
        instance = self.instances.get(instance_id)
        if instance:
            instance.update_activity()
        
        return instance
    
    def get_game_state(self, instance_id: Optional[str] = None) -> Optional[GameState]:
        """Get game state for a specific instance.
        
        Args:
            instance_id: Instance ID, or None to get default instance
            
        Returns:
            GameState or None if not found
        """
        instance = self.get_instance(instance_id)
        return instance.game_state if instance else None
    
    def update_game_state(self, game_state: GameState, 
                         instance_id: Optional[str] = None) -> bool:
        """Update game state for an instance.
        
        Args:
            game_state: New GameState object
            instance_id: Instance ID, or None to update default instance
            
        Returns:
            True if updated successfully
        """
        instance = self.get_instance(instance_id)
        if instance:
            instance.game_state = game_state
            instance.update_activity()
            self.logger.logger.info(
                f"[INSTANCE_MANAGER] Updated state for instance: {instance.instance_id}"
            )
            return True
        return False
    
    def remove_instance(self, instance_id: str) -> bool:
        """Remove a game instance.
        
        Args:
            instance_id: Instance ID to remove
            
        Returns:
            True if removed successfully
        """
        if instance_id in self.instances:
            del self.instances[instance_id]
            
            # Update default if this was it
            if self._default_instance_id == instance_id:
                self._default_instance_id = next(iter(self.instances.keys()), None)
            
            self.logger.logger.info(
                f"[INSTANCE_MANAGER] Removed instance: {instance_id}"
            )
            return True
        return False
    
    def list_instances(self) -> List[dict]:
        """List all active instances.
        
        Returns:
            List of instance info dictionaries
        """
        return [instance.to_dict() for instance in self.instances.values()]
    
    def set_default_instance(self, instance_id: str) -> bool:
        """Set the default instance for operations without explicit ID.
        
        Args:
            instance_id: Instance ID to set as default
            
        Returns:
            True if set successfully
        """
        if instance_id in self.instances:
            self._default_instance_id = instance_id
            self.logger.logger.info(
                f"[INSTANCE_MANAGER] Set default instance: {instance_id}"
            )
            return True
        return False
    
    def get_default_instance_id(self) -> Optional[str]:
        """Get the default instance ID.
        
        Returns:
            Default instance ID or None
        """
        return self._default_instance_id
    
    def cleanup_inactive_instances(self, timeout_seconds: int = 3600):
        """Remove instances that haven't had activity in specified time.
        
        Args:
            timeout_seconds: Seconds of inactivity before cleanup (default 1 hour)
        """
        current_time = datetime.utcnow()
        to_remove = []
        
        for instance_id, instance in self.instances.items():
            inactive_time = (current_time - instance.last_activity).total_seconds()
            if inactive_time > timeout_seconds and not instance.connected:
                to_remove.append(instance_id)
        
        for instance_id in to_remove:
            self.remove_instance(instance_id)
        
        if to_remove:
            self.logger.logger.info(
                f"[INSTANCE_MANAGER] Cleaned up {len(to_remove)} inactive instances"
            )


# Global instance manager
instance_manager = InstanceManager()
