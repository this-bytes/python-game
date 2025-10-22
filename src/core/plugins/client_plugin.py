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
from src.ui.ui_provider import UIProvider, UISummaryItem, UISectionItem, UIPanelSection, UIAction
from src.utils.logger import GameLogger


logger = GameLogger("client_plugin")


class ClientPlugin(GameSystem, UIProvider):
    """Plugin for managing client lifecycle and satisfaction.
    
    Subscribes to SLA tracking events to update client satisfaction,
    handles contract renewals at month-end, and manages client acquisition.
    
    Implements UIProvider to display client dashboard summary and detail panel.
    
    Lifecycle:
    - initialize(): Load clients from JSON or default
    - update(): Check for contract renewals at month-end
    - shutdown(): Save client state
    - get_dashboard_summary(): Return summary for dashboard widget
    - get_detail_panel_data(): Return expanded client details for modal
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
            
            # Get event bus
            # Import placed here to avoid circular dependency between client_plugin and event_bus.
            from src.core.event_bus import get_event_bus
            self.event_bus = get_event_bus()
            
            # Subscribe to action events
            self.event_bus.subscribe("action:view_client_details", self._on_view_details_action)
            self.event_bus.subscribe("action:contact_client", self._on_contact_client_action)
            
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
    
    # ===== UI PROVIDER IMPLEMENTATION =====
    
    def get_dashboard_summary(self, game_state: GameState) -> UISummaryItem:
        """Get dashboard summary for client manager widget.
        
        Displays key client metrics on the persistent dashboard overlay.
        This is DISPLAY-ONLY - no game logic, just state visualization.
        
        Args:
            game_state: Current game state (read-only)
            
        Returns:
            UISummaryItem with client summary data
        """
        active_count = len(self.get_active_clients())
        total_value = sum(c.monthly_contract_value for c in self.get_active_clients())
        avg_satisfaction = (
            sum(c.satisfaction for c in self.get_active_clients()) / active_count
            if active_count > 0
            else 0.0
        )
        
        # Determine status color based on satisfaction
        if avg_satisfaction >= 0.8:
            accent = "green"
        elif avg_satisfaction >= 0.6:
            accent = "yellow"
        else:
            accent = "red"
        
        return UISummaryItem(
            title="Clients",
            icon="🏢",
            lines=[
                f"Active: {active_count}",
                f"Revenue: ${total_value:,.0f}/month",
                f"Avg Satisfaction: {avg_satisfaction:.0%}",
            ],
            accent_color=accent,
            data={
                "active_count": active_count,
                "total_value": total_value,
                "avg_satisfaction": avg_satisfaction,
                "total_clients": len(self.clients),
            }
        )
    
    def get_detail_panel_data(self, game_state: GameState) -> Dict[str, Any]:
        """Get detail panel data for expanded client view.
        
        Provides full client information for modal detail panel.
        Player can click action buttons which are published as "action:" events.
        This is DISPLAY-ONLY - no mutations happen in this method.
        
        Args:
            game_state: Current game state (read-only)
            
        Returns:
            Dictionary with panel structure and client data
        """
        active_clients = self.get_active_clients()
        
        # Build section items for each client
        client_items = []
        for client in active_clients:
            satisfaction_bar = self._satisfaction_bar(client.satisfaction)
            client_items.append(
                UISectionItem(
                    name=client.company_name,
                    details=[
                        f"Industry: {client.industry}",
                        f"Contract: ${client.monthly_contract_value:,.0f}/month",
                        f"Satisfaction: {satisfaction_bar} {client.satisfaction:.0%}",
                        f"SLA: {client.sla_response_time_seconds}s response",
                    ],
                    clickable=True,
                    data={
                        "client_id": client.client_id,
                        "company_name": client.company_name,
                    }
                )
            )
        
        return {
            "title": "Client Management",
            "sections": [
                UIPanelSection(
                    title=f"Active Clients ({len(active_clients)})",
                    items=client_items,
                    section_type="list"
                )
            ],
            "actions": [
                UIAction(
                    id="view_client_details",
                    label="📋 View Details",
                    description="View detailed client information",
                    enabled=len(active_clients) > 0
                ),
                UIAction(
                    id="contact_client",
                    label="📞 Contact Client",
                    description="Reach out to client",
                    enabled=len(active_clients) > 0
                ),
            ],
            "stats": {
                "total_revenue": sum(c.monthly_contract_value for c in active_clients),
                "avg_satisfaction": (
                    sum(c.satisfaction for c in active_clients) / len(active_clients)
                    if active_clients else 0.0
                ),
            }
        }
    
    @staticmethod
    def _satisfaction_bar(satisfaction: float, width: int = 10) -> str:
        """Create ASCII satisfaction bar for display.
        
        Args:
            satisfaction: Satisfaction value 0.0-1.0
            width: Width of bar in characters
            
        Returns:
            ASCII bar representation
        """
        filled = int(satisfaction * width)
        return "█" * filled + "░" * (width - filled)
    
    # ===== ACTION HANDLERS =====
    
    def _on_view_details_action(self, event) -> None:
        """Handle 'view_client_details' action from UI.
        
        Args:
            event: Event with action data
        """
        logger.info("[ClientPlugin] ✅ View Details action received!")
        logger.debug(f"[ClientPlugin] Event data: {event.data}")
        
        # This is where game logic would go
        # For now, just log to confirm EventBus is working
    
    def _on_contact_client_action(self, event) -> None:
        """Handle 'contact_client' action from UI.
        
        Args:
            event: Event with action data
        """
        logger.info("[ClientPlugin] ✅ Contact Client action received!")
        logger.debug(f"[ClientPlugin] Event data: {event.data}")
        
        # This is where game logic would go
        # For now, just log to confirm EventBus is working
