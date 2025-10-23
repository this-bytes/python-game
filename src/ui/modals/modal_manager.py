"""Modal manager for handling modal stacking, transitions, and lifecycle.

Provides:
- Modal stack management (push, pop, peek)
- Modal chain navigation with back button
- Proper cleanup and event routing
- Modal transition callbacks
"""

from typing import List, Optional, Callable, Any
import pygame
from src.ui.modals.entity_modal import EntityModal


class ModalManager:
    """Manages a stack of modals with proper lifecycle and transitions."""

    def __init__(self):
        """Initialize modal manager with empty stack."""
        self.modal_stack: List[EntityModal] = []
        self.on_modal_changed: Optional[Callable[[], None]] = None
    
    def push_modal(self, modal: EntityModal) -> None:
        """Push a new modal onto the stack.
        
        Args:
            modal: Modal to push
        """
        if modal is None:
            return
        
        self.modal_stack.append(modal)
        
        # Notify that modal stack changed
        if self.on_modal_changed:
            self.on_modal_changed()
    
    def pop_modal(self) -> Optional[EntityModal]:
        """Pop the top modal from the stack.
        
        Returns:
            The popped modal, or None if stack is empty
        """
        if self.is_empty():
            return None
        
        modal = self.modal_stack.pop()
        
        # Notify that modal stack changed
        if self.on_modal_changed:
            self.on_modal_changed()
        
        return modal
    
    def peek_modal(self) -> Optional[EntityModal]:
        """Peek at the top modal without removing it.
        
        Returns:
            The top modal, or None if stack is empty
        """
        if self.is_empty():
            return None
        
        return self.modal_stack[-1]
    
    def clear_all(self) -> None:
        """Clear all modals from the stack."""
        self.modal_stack.clear()
        
        # Notify that modal stack changed
        if self.on_modal_changed:
            self.on_modal_changed()
    
    def is_empty(self) -> bool:
        """Check if modal stack is empty.
        
        Returns:
            True if no modals, False otherwise
        """
        return len(self.modal_stack) == 0
    
    def has_active_modal(self) -> bool:
        """Check if there's an active modal.
        
        Returns:
            True if there's at least one modal
        """
        return not self.is_empty()
    
    def get_modal_count(self) -> int:
        """Get the number of modals in the stack.
        
        Returns:
            Number of modals
        """
        return len(self.modal_stack)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input event for the active modal.
        
        Events are routed only to the top modal. If a modal returns True,
        it remains open. If it returns False, it's closed.
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled, False otherwise
        """
        if self.is_empty():
            return False
        
        modal = self.peek_modal()
        should_keep_open = modal.handle_event(event)
        
        if not should_keep_open:
            # Modal wants to close
            self.pop_modal()
            return True
        
        return True
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw all modals in the stack (in order, bottom to top).
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw all modals from bottom to top
        for modal in self.modal_stack:
            modal.draw(screen)
    
    def replace_modal(self, modal: EntityModal) -> None:
        """Replace the top modal with a new one.
        
        Useful for modal chains (specialist → incident selector).
        
        Args:
            modal: New modal to display
        """
        if not self.is_empty():
            self.pop_modal()
        
        self.push_modal(modal)
    
    def get_stack_depth(self) -> int:
        """Get the current depth of the modal stack.
        
        Useful for understanding modal chains:
        - Depth 1: Single modal
        - Depth 2: Modal chain (back button available)
        - Depth 3+: Deep modal chains
        
        Returns:
            Stack depth
        """
        return len(self.modal_stack)
    
    def can_go_back(self) -> bool:
        """Check if there's a modal to go back to.
        
        Returns:
            True if stack has > 1 modal
        """
        return len(self.modal_stack) > 1
