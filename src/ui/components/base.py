import pygame

class UIComponent:
    """Base class for all UI components."""
    def __init__(self, rect: pygame.Rect, visible: bool = True):
        self.rect = rect
        self.is_visible = visible

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle a single pygame event. Return True if the event was handled, False otherwise."""
        return False

    def update(self, delta_time: float, game_state) -> None:
        """Update the component's state."""
        pass

    def draw(self, screen: pygame.Surface, game_state) -> None:
        """Draw the component to the screen."""
        pass
