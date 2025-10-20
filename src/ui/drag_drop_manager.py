"""Drag and Drop Manager for cross-panel interactions."""

import pygame
from typing import Optional, Any
from src.models.incident import Incident


class DragDropManager:
    """Manages drag and drop state across UI panels."""

    def __init__(self):
        """Initialize drag drop manager."""
        self.dragged_incident: Optional[Incident] = None
        self.drag_offset = (0, 0)
        self.is_dragging = False

    def start_drag(self, incident: Incident, mouse_pos: tuple[int, int], card_rect: pygame.Rect) -> None:
        """Start dragging an incident.

        Args:
            incident: Incident being dragged
            mouse_pos: Current mouse position
            card_rect: Rectangle of the incident card being dragged
        """
        self.dragged_incident = incident
        self.drag_offset = (mouse_pos[0] - card_rect.x, mouse_pos[1] - card_rect.y)
        self.is_dragging = True

    def end_drag(self) -> None:
        """End the current drag operation."""
        self.dragged_incident = None
        self.drag_offset = (0, 0)
        self.is_dragging = False

    def is_incident_being_dragged(self) -> bool:
        """Check if an incident is currently being dragged.

        Returns:
            True if incident is being dragged
        """
        return self.is_dragging and self.dragged_incident is not None

    def get_dragged_incident(self) -> Optional[Incident]:
        """Get the incident currently being dragged.

        Returns:
            Dragged incident or None
        """
        return self.dragged_incident

    def get_drag_offset(self) -> tuple[int, int]:
        """Get the drag offset.

        Returns:
            Drag offset as (x, y) tuple
        """
        return self.drag_offset


# Global instance for cross-panel access
_drag_drop_manager = DragDropManager()

def get_drag_drop_manager() -> DragDropManager:
    """Get the global drag drop manager instance.

    Returns:
        Global DragDropManager instance
    """
    return _drag_drop_manager