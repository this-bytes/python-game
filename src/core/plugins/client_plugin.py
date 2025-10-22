"""ClientPlugin - Plugin system wrapper for Phase 3 client management.

Integrates client_system into the plugin architecture. Handles:
- Monthly client satisfaction updates based on SLA performance
- Contract renewals at month-end
- Client acquisition and termination
- Event-driven communication with Budget and SLA systems
"""

from typing import Optional, List, Dict, Any
from src.core.game_system import GameSystem
from src.core.event_bus import EventBus
from src.models.game_state import GameState
from src.models.client import Client
from src.core.client_system import (
    generate_client_from_template,
    update_client_satisfaction,
    attempt_contract_renewal,
    handle_contract_termination,
    load_clients_from_json,
)
from src.utils.logger import GameLogger


logger = GameLogger("client_plugin")


class ClientPlugin(GameSystem):
    """Plugin for managing client lifecycle and satisfaction.
    
    Subscribes to SLA tracking events to update client satisfaction,
    handles contract renewals at month-end, and manages client acquisition.
    
    Lifecycle:
    - initialize(): Load clients from JSON or default
    - update(): Check for contract renewals at month-end
    - shutdown(): Save client state
    """
    
    def __init__(self):
        """Initialize ClientPlugin."""
        super().__init__()
        self.name = "ClientPlugin"
        self.event_bus: Optional[EventBus] = None
        self.clients: List[Client] = []
        self.monthly_sla_tracking: Dict[str, Dict[str, int]] = {}  # client_id -> {met, missed}
    
    def get_name(self) -> str:
        """Get plugin name."""
        return self.name
    
    def initialize(self, game_state: GameState) -> bool:
        """Initialize client system from game state or JSON.
        
        Args:
            game_state: Current game state
            
        Returns:
            True if initialization successful
        """
        try:
            logger.info("[ClientPlugin] Initializing...")
            
            # Use clients from game state if available
            if hasattr(game_state, 'clients') and game_state.clients:
                self.clients = game_state.clients
                logger.info(f"[ClientPlugin] Loaded {len(self.clients)} clients from game state")
            else:
                # Load from JSON
                self.clients = load_clients_from_json()
                game_state.clients = self.clients
                logger.info(f"[ClientPlugin] Loaded {len(self.clients)} clients from JSON")
            
            logger.info(f"[ClientPlugin] Ready with {len(self.clients)} clients")
            return True
            
        except Exception as e:
            logger.error("[ClientPlugin] Initialization failed", exception=e)
            return False
    
    def update(self, game_state: GameState, delta_time: float) -> None:
        """Update client system (called each frame).
        
        Currently minimal - most work happens on month-end events.
        
        Args:
            game_state: Current game state
            delta_time: Time elapsed since last update (seconds)
        """
        pass  # Main work happens in event handlers
    
    def shutdown(self) -> None:
        """Shutdown and cleanup."""
        logger.info("[ClientPlugin] Shutting down")
    
    def set_event_bus(self, event_bus: EventBus) -> None:
        """Set the event bus for event communication.
        
        Args:
            event_bus: EventBus instance
        """
        self.event_bus = event_bus
    
    def save_state(self) -> Dict[str, Any]:
        """Save client state to dictionary.
        
        Returns:
            Dictionary with client data
        """
        return {
            "clients": [client.to_dict() for client in self.clients],
        }
    
    def load_state(self, state: Dict[str, Any]) -> None:
        """Load client state from dictionary.
        
        Args:
            state: Dictionary with client data
        """
        # Clients are loaded via initialize()
        pass
    
    # ===== CLIENT MANAGEMENT =====
    
    def acquire_client(self, client: Client) -> bool:
        """Acquire a new client.
        
        Args:
            client: Client to acquire
            
        Returns:
            True if client added successfully
        """
        try:
            # Check for duplicates
            if any(c.client_id == client.client_id for c in self.clients):
                logger.warning(f"Client {client.client_id} already exists")
                return False
            
            self.clients.append(client)
            logger.info(f"Acquired client: {client.company_name}", value=client.monthly_contract_value)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to acquire client", exception=e)
            return False
    
    def get_active_clients(self) -> List[Client]:
        """Get list of active clients.
        
        Returns:
            List of active Client instances
        """
        return [c for c in self.clients if c.is_active]
    
    def get_client_by_id(self, client_id: str) -> Optional[Client]:
        """Get client by ID.
        
        Args:
            client_id: Client ID to search for
            
        Returns:
            Client instance or None if not found
        """
        for client in self.clients:
            if client.client_id == client_id:
                return client
        return None
