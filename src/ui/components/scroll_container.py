"""Scroll container component for game UI."""

import pygame
from typing import Tuple, List, Any


class ScrollContainer:
    """Scrollable content area with scroll bars."""

    def __init__(
        self,
        position: Tuple[int, int],
        size: Tuple[int, int],
        content_height: int,
    ):
        """Initialize scroll container."""
        self.position = position
        self.size = size
        self.content_height = content_height
        self.scroll_offset = 0
        self.scroll_bar_width = 15

        self.bg_color = (30, 30, 30)
        self.scroll_bar_color = (100, 100, 100)
        self.scroll_handle_color = (150, 150, 150)

        self.is_scrolling = False
        self.scroll_start_y = 0

    def render(self, screen: pygame.Surface) -> None:
        """Render scroll container."""
        rect = pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])

        # Draw background
        pygame.draw.rect(screen, self.bg_color, rect)

        # Draw scroll bar if content is larger than container
        if self.content_height > self.size[1]:
            scroll_bar_rect = pygame.Rect(
                rect.right - self.scroll_bar_width,
                rect.y,
                self.scroll_bar_width,
                rect.height
            )
            pygame.draw.rect(screen, self.scroll_bar_color, scroll_bar_rect)

            # Calculate scroll handle
            handle_height = max(20, int((self.size[1] / self.content_height) * self.size[1]))
            handle_y = rect.y + int((self.scroll_offset / (self.content_height - self.size[1])) * (self.size[1] - handle_height))
            handle_rect = pygame.Rect(
                scroll_bar_rect.x + 2,
                handle_y,
                scroll_bar_rect.width - 4,
                handle_height
            )
            pygame.draw.rect(screen, self.scroll_handle_color, handle_rect, border_radius=2)

    def handle_event(self, event: Any) -> bool:
        """Handle scroll events."""
        rect = pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])

        if event.type == pygame.MOUSEWHEEL and rect.collidepoint(pygame.mouse.get_pos()):
            self.scroll_offset -= event.y * 20
            self.scroll_offset = max(0, min(self.content_height - self.size[1], self.scroll_offset))
            return True

        return False

    def get_scroll_offset(self) -> int:
        """Get current scroll offset."""
        return int(self.scroll_offset)

    def set_content_height(self, height: int) -> None:
        """Set content height."""
        self.content_height = height
        self.scroll_offset = max(0, min(self.scroll_offset, self.content_height - self.size[1]))
