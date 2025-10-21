"""Hotkey Manager for keyboard shortcuts."""

import pygame
from typing import Dict, Callable, Optional, Any
from enum import Enum


class HotkeyAction(Enum):
    """Predefined hotkey actions."""
    PAUSE_TOGGLE = "pause_toggle"
    QUICK_SAVE = "quick_save"
    INCREASE_SPEED = "increase_speed"
    DECREASE_SPEED = "decrease_speed"
    CLOSE_PANEL = "close_panel"
    TOGGLE_SPECIALIST_PANEL = "toggle_specialist_panel"
    TOGGLE_INCIDENT_PANEL = "toggle_incident_panel"
    TOGGLE_METRICS_PANEL = "toggle_metrics_panel"
    TOGGLE_CLIENT_PANEL = "toggle_client_panel"
    TOGGLE_AUTOMATION_PANEL = "toggle_automation_panel"
    TOGGLE_SHOP_PANEL = "toggle_shop_panel"
    TOGGLE_INVENTORY_PANEL = "toggle_inventory_panel"
    DEBUG_TOGGLE = "debug_toggle"
    DEBUG_INSPECTOR = "debug_inspector"
    TAKE_SCREENSHOT = "take_screenshot"


class HotkeyManager:
    """Manage keyboard shortcuts."""

    def __init__(self):
        """Initialize hotkey manager."""
        self.bindings: Dict[int, HotkeyAction] = {}
        self.callbacks: Dict[HotkeyAction, Callable] = {}

        # Default bindings
        self._set_default_bindings()

    def _set_default_bindings(self) -> None:
        """Set default hotkey bindings."""
        self.bindings = {
            pygame.K_SPACE: HotkeyAction.PAUSE_TOGGLE,
            pygame.K_s: HotkeyAction.QUICK_SAVE,
            pygame.K_EQUALS: HotkeyAction.INCREASE_SPEED,  # + key
            pygame.K_MINUS: HotkeyAction.DECREASE_SPEED,
            pygame.K_ESCAPE: HotkeyAction.CLOSE_PANEL,
            pygame.K_1: HotkeyAction.TOGGLE_SPECIALIST_PANEL,
            pygame.K_2: HotkeyAction.TOGGLE_INCIDENT_PANEL,
            pygame.K_3: HotkeyAction.TOGGLE_METRICS_PANEL,
            pygame.K_4: HotkeyAction.TOGGLE_CLIENT_PANEL,
            pygame.K_5: HotkeyAction.TOGGLE_AUTOMATION_PANEL,
            pygame.K_6: HotkeyAction.TOGGLE_SHOP_PANEL,
            pygame.K_7: HotkeyAction.TOGGLE_INVENTORY_PANEL,
            pygame.K_F11: HotkeyAction.DEBUG_INSPECTOR,
            pygame.K_F12: HotkeyAction.DEBUG_TOGGLE,
            pygame.K_F10: HotkeyAction.TAKE_SCREENSHOT,
        }

    def register_callback(self, action: HotkeyAction, callback: Callable) -> None:
        """Register callback for action.

        Args:
            action: Hotkey action
            callback: Function to call when hotkey pressed
        """
        self.callbacks[action] = callback

    def rebind_hotkey(self, action: HotkeyAction, new_key: int) -> None:
        """Rebind hotkey to new key.

        Args:
            action: Action to rebind
            new_key: New key code
        """
        # Remove old binding
        for key, bound_action in list(self.bindings.items()):
            if bound_action == action:
                del self.bindings[key]

        # Add new binding
        self.bindings[new_key] = action

    def handle_key_event(self, event: Any) -> bool:
        """Process key press event.

        Args:
            event: Pygame key event

        Returns:
            True if key was handled, False otherwise
        """
        if event.type != pygame.KEYDOWN:
            return False

        # Check if key is bound
        if event.key in self.bindings:
            action = self.bindings[event.key]

            # Execute callback if registered
            if action in self.callbacks:
                self.callbacks[action]()
                return True

        return False

    def get_key_name(self, key: int) -> str:
        """Get human-readable key name.

        Args:
            key: Pygame key code

        Returns:
            Key name string
        """
        return pygame.key.name(key).upper()

    def get_binding_for_action(self, action: HotkeyAction) -> Optional[int]:
        """Get key binding for action.

        Args:
            action: Hotkey action

        Returns:
            Key code or None if not bound
        """
        for key, bound_action in self.bindings.items():
            if bound_action == action:
                return key
        return None

    def get_all_bindings(self) -> Dict[HotkeyAction, int]:
        """Get all hotkey bindings.

        Returns:
            Dictionary of action to key mappings
        """
        return {action: key for key, action in self.bindings.items()}
