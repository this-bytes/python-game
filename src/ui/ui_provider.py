"""UI Provider interface for game systems.

This module defines the minimal interface that game systems (plugins) can implement
to provide UI display capabilities. This enables true separation of concerns:
- Game logic lives in plugins (change state)
- UI display lives in UIProvider implementations (show state)
- EventBus handles communication between them

A game system is not required to implement UIProvider. Only systems that want to
display information on the dashboard or have expandable detail panels need to
implement this interface.

Example:
    ```python
    from src.ui.ui_provider import UIProvider, UISummaryItem
    from src.core.game_system import GameSystem
    
    class ClientPlugin(GameSystem, UIProvider):
        \"\"\"Game logic for client management + UI display.\"\"\"
        
        def get_dashboard_summary(self, game_state):
            active_clients = len(self.clients)
            return UISummaryItem(
                title="Clients",
                icon="🏢",
                lines=[
                    f"Active: {active_clients}/5",
                    f"Avg Satisfaction: 85%",
                ],
                accent_color="green",
            )
        
        def get_detail_panel_data(self, game_state):
            return {
                "title": "Client Management",
                "sections": [
                    {
                        "title": "Active Clients",
                        "items": [
                            {
                                "name": "ACME Corp",
                                "details": ["Industry: Banking", "Revenue: $15k/month"]
                            }
                        ]
                    }
                ],
                "actions": [
                    {
                        "id": "contact_client",
                        "label": "📞 Contact Client",
                        "enabled": True
                    }
                ]
            }
    ```
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


@dataclass
class UISummaryItem:
    """Dashboard summary widget for a game system.
    
    This is displayed as a card on the persistent dashboard overlay.
    Clicking on it (if clickable=True) opens the detail panel.
    
    Attributes:
        title: Display title ("Clients", "Budget", "Team")
        icon: Icon or emoji ("🏢", "💰", "👥")
        lines: 3-5 lines of summary data (most recent on top)
        accent_color: Color hint for rendering ("green", "red", "yellow", "blue")
        clickable: Can player click to expand detail panel?
        data: Optional raw data passed to detail panel when expanded
    """
    title: str
    icon: str
    lines: List[str]
    accent_color: str
    clickable: bool = True
    data: Optional[Dict[str, Any]] = field(default=None)


@dataclass
class UISectionItem:
    """Single item in a detail panel section.
    
    Attributes:
        name: Item display name (e.g., "ACME Corp")
        details: List of detail lines to display
        clickable: Can user interact with this item?
        data: Optional data associated with this item
    """
    name: str
    details: List[str]
    clickable: bool = False
    data: Optional[Dict[str, Any]] = field(default=None)


@dataclass
class UIPanelSection:
    """Section within a detail panel.
    
    Attributes:
        title: Section title ("Active Clients", "Financial Summary")
        items: List of UISectionItems to display
        section_type: Type of section ("list", "stats", "table")
    """
    title: str
    items: List[UISectionItem]
    section_type: str = "list"


@dataclass
class UIAction:
    """Action button for detail panel.
    
    When player clicks action button, UI publishes an event:
        event_bus.publish("action:{id}", data, source="ui")
    
    The corresponding game system listens for this action and executes logic.
    
    Attributes:
        id: Action identifier (e.g., "contact_client")
        label: Button display text (e.g., "📞 Contact Client")
        description: Tooltip/help text
        cost: Optional cost display (e.g., "$1,000")
        enabled: Is button clickable?
        requires_selection: Does action require user to select an item first?
    """
    id: str
    label: str
    description: str = ""
    cost: str = ""
    enabled: bool = True
    requires_selection: bool = False
    data: Optional[Dict[str, Any]] = field(default=None)


class UIProvider(ABC):
    """Base interface for game systems that provide UI display.
    
    Any GameSystem can implement this interface to automatically:
    1. Display a summary widget on the persistent dashboard
    2. Provide an expandable detail panel
    3. Handle user actions via EventBus
    
    CRITICAL RULE: UIProvider methods are DISPLAY ONLY.
    - They read game_state
    - They format data for display
    - They DO NOT modify game_state
    - They DO NOT execute game logic
    
    Game logic belongs in GameSystem methods, triggered by action events.
    UI display belongs in UIProvider methods.
    
    The EventBus connects them:
    1. UI publishes action: event_bus.publish("action:contact_client", data)
    2. GameSystem subscribed to it executes: def _on_contact_client_action(event)
    3. GameSystem publishes result: event_bus.publish("client_contacted", result_data)
    4. UI listens and updates display
    """
    
    @abstractmethod
    def get_dashboard_summary(self, game_state) -> UISummaryItem:
        """Return summary widget for persistent dashboard overlay.
        
        Called every frame to update dashboard display. Keep this lightweight:
        - Just format existing game_state data
        - No heavy computation
        - No game logic
        - Must return quickly
        
        Args:
            game_state: Current game state (read-only)
            
        Returns:
            UISummaryItem with dashboard display data
            
        Raises:
            Exception: Should not raise. If error occurs, DashboardManager catches it.
        """
        pass
    
    @abstractmethod
    def get_detail_panel_data(self, game_state) -> Dict[str, Any]:
        """Return complete data for expanded detail panel.
        
        Called when player clicks on dashboard summary to expand full view.
        Return all information player might need to see and interact with.
        
        Structure should be:
        ```python
        {
            "title": "Panel Title",
            "sections": [
                {
                    "title": "Section Title",
                    "items": [
                        {
                            "name": "Item Name",
                            "details": ["Detail 1", "Detail 2"],
                            "clickable": False,
                            "data": {}  # Optional data for this item
                        }
                    ]
                }
            ],
            "actions": [
                {
                    "id": "action_id",
                    "label": "📞 Action Label",
                    "description": "What this action does",
                    "cost": "$1,000",
                    "enabled": True
                }
            ]
        }
        ```
        
        Args:
            game_state: Current game state (read-only)
            
        Returns:
            Dictionary with panel structure as shown above
        """
        pass
