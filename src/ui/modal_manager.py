"""
Manages the display and interaction of modal dialogs in the UI.

This class acts as a centralized controller for a stack of modals, ensuring
that only one modal is active and receiving events at any given time. It
listens for custom UI events (SHOW_MODAL, HIDE_MODAL) to manage the modal
stack.

The manager is responsible for:
-   Maintaining a stack of active modals.
-   Drawing the currently active (top-most) modal.
-   Forwarding Pygame events to the active modal.
-   Blocking events from reaching underlying UI elements when a modal is active.
-   Creating modal instances from a factory based on event data.
"""
import pygame

from src.ui.event_types import SHOW_MODAL, HIDE_MODAL
from src.ui.modals.specialist_detail_modal import SpecialistDetailModal
from src.ui.modals.incident_detail_modal import IncidentDetailModal

class ModalManager:
    """Manages a stack of UI modals."""

    def __init__(self, screen: pygame.Surface, game_state=None, on_open=None, on_close=None):
        """
        Initializes the ModalManager.

        Args:
            screen (pygame.Surface): The main display surface to draw modals on.
            game_state: Optional GameState reference to forward to modal constructors.
        """
        self.screen = screen
        self.game_state = game_state
        # Optional callbacks invoked when a modal opens/closes. These allow
        # the surrounding UI (GameUI) to capture and restore focus state.
        # on_open() -> called before modal is pushed
        # on_close() -> called after modal is popped
        self._on_open_callback = on_open
        self._on_close_callback = on_close
        self.modal_stack: list = []
        self._modal_factory = {
            "specialist_detail": SpecialistDetailModal,
            "incident_detail": IncidentDetailModal,
        }

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handles Pygame events, creating or destroying modals as needed.

        Args:
            event (pygame.event.Event): The Pygame event to process.

        Returns:
            bool: True if the event was consumed by a modal, False otherwise.
                  This can be used to block events from propagating further.
        """
        if event.type == SHOW_MODAL:
            modal_id = event.dict.get("modal_id")
            if modal_id in self._modal_factory:
                # Prepare modal kwargs (exclude modal_id) and forward game_state
                modal_data = {k: v for k, v in event.dict.items() if k != "modal_id"}
                try:
                    # Pass screen and game_state as first two args to modal constructors
                    new_modal = self._modal_factory[modal_id](self.screen, self.game_state, **modal_data)
                except TypeError:
                    # Fallback: some modals may accept (screen, **kwargs)
                    new_modal = self._modal_factory[modal_id](self.screen, **modal_data)

                self.modal_stack.append(new_modal)
                # Notify caller that a modal opened (so it can save focus)
                try:
                    if callable(self._on_open_callback):
                        self._on_open_callback()
                except Exception:
                    # Swallow errors from callbacks to avoid breaking modal flow
                    pass
                return True

        if event.type == HIDE_MODAL:
            if self.modal_stack:
                self.modal_stack.pop()
                # Notify caller that a modal closed (so it can restore focus)
                try:
                    if callable(self._on_close_callback):
                        self._on_close_callback()
                except Exception:
                    pass
                return True

        # If a modal is active, pass events to it
        if self.is_modal_active():
            self.get_active_modal().handle_event(event)
            # Consume the event so it doesn't propagate to the game world
            return True

        return False

    def update(self, delta_time: float) -> None:
        """
        Updates the currently active modal.

        Args:
            delta_time (float): Time elapsed since the last frame.
        """
        if self.is_modal_active():
            self.get_active_modal().update(delta_time)

    def draw(self) -> None:
        """Draws the active modal and a semi-transparent overlay."""
        if self.is_modal_active():
            # Draw a semi-transparent overlay to dim the background
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Black with 180/255 alpha
            self.screen.blit(overlay, (0, 0))

            # Draw the top-most modal
            self.get_active_modal().draw()

    def is_modal_active(self) -> bool:
        """
        Checks if there is any modal currently active.

        Returns:
            bool: True if the modal stack is not empty, False otherwise.
        """
        return len(self.modal_stack) > 0

    def get_active_modal(self):
        """
        Gets the currently active modal from the top of the stack.

        Returns:
            The active modal instance, or None if no modal is active.
        """
        if self.is_modal_active():
            return self.modal_stack[-1]
        return None
