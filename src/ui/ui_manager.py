from typing import List
import pygame

from src.ui.components.base import UIComponent

class UIManager:
    """Manages a stack of UI components, handling input, updates, and rendering."""

    def __init__(self):
        self._components: List[UIComponent] = []

    def push(self, component: UIComponent):
        """Push a component onto the top of the UI stack."""
        self._components.append(component)

    def pop(self) -> UIComponent:
        """Pop the top-most component from the UI stack."""
        return self._components.pop()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Passes an event to the top-most component on the stack.

        The event is only passed down the stack if the top component doesn't handle it.
        """
        # Iterate in reverse order so the top-most components get events first
        for component in reversed(self._components):
            if component.is_visible and component.handle_event(event):
                return True
        return False

    def update(self, delta_time: float, game_state):
        """Update all visible components."""
        for component in self._components:
            if component.is_visible:
                component.update(delta_time, game_state)

    def draw(self, screen: pygame.Surface, game_state):
        """Draw all visible components from bottom to top."""
        for component in self._components:
            if component.is_visible:
                component.draw(screen, game_state)
