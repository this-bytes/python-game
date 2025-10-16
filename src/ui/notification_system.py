"""Notification System for toast messages."""

import pygame
from typing import List, Optional
from enum import Enum
from dataclasses import dataclass


class NotificationType(Enum):
    """Notification type."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Notification:
    """Toast notification."""
    title: str
    message: str
    notification_type: NotificationType
    duration: float = 3.0
    time_remaining: float = 0

    def __post_init__(self):
        """Initialize time remaining."""
        self.time_remaining = self.duration


class NotificationManager:
    """Manage toast notifications."""

    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        """Initialize notification manager.

        Args:
            screen_width: Screen width for positioning
            screen_height: Screen height for positioning
        """
        self.notifications: List[Notification] = []
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Notification styling
        self.notification_width = 300
        self.notification_height = 80
        self.notification_margin = 10
        self.max_notifications = 5

        # Type colors
        self.type_colors = {
            NotificationType.INFO: (0, 120, 215),
            NotificationType.SUCCESS: (0, 200, 100),
            NotificationType.WARNING: (255, 200, 0),
            NotificationType.ERROR: (255, 50, 50),
        }

        # Fonts
        self.title_font = None
        self.message_font = None

    def show(self, notification: Notification) -> None:
        """Show notification.

        Args:
            notification: Notification to show
        """
        # Add to list
        self.notifications.append(notification)

        # Remove oldest if too many
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)

    def show_info(self, title: str, message: str, duration: float = 3.0) -> None:
        """Show info notification."""
        self.show(Notification(title, message, NotificationType.INFO, duration))

    def show_success(self, title: str, message: str, duration: float = 3.0) -> None:
        """Show success notification."""
        self.show(Notification(title, message, NotificationType.SUCCESS, duration))

    def show_warning(self, title: str, message: str, duration: float = 3.0) -> None:
        """Show warning notification."""
        self.show(Notification(title, message, NotificationType.WARNING, duration))

    def show_error(self, title: str, message: str, duration: float = 3.0) -> None:
        """Show error notification."""
        self.show(Notification(title, message, NotificationType.ERROR, duration))

    def update(self, delta_time: float) -> None:
        """Update notifications (countdown timers).

        Args:
            delta_time: Time elapsed since last update
        """
        # Update timers
        for notification in self.notifications[:]:
            notification.time_remaining -= delta_time
            if notification.time_remaining <= 0:
                self.notifications.remove(notification)

    def render(self, screen: pygame.Surface) -> None:
        """Render notifications.

        Args:
            screen: Pygame surface to render on
        """
        # Initialize fonts if needed
        if self.title_font is None:
            self.title_font = pygame.font.SysFont('Arial', 14, bold=True)
            self.message_font = pygame.font.SysFont('Arial', 12)

        # Render notifications from top-right
        y_offset = self.notification_margin

        for notification in self.notifications:
            x = self.screen_width - self.notification_width - self.notification_margin
            y = y_offset

            rect = pygame.Rect(x, y, self.notification_width, self.notification_height)

            # Calculate opacity based on time remaining (fade out in last 0.5s)
            opacity = 255
            if notification.time_remaining < 0.5:
                opacity = int(255 * (notification.time_remaining / 0.5))

            # Create surface with transparency
            surf = pygame.Surface((rect.width, rect.height))
            surf.set_alpha(opacity)

            # Background
            color = self.type_colors.get(notification.notification_type, (100, 100, 100))
            pygame.draw.rect(surf, (40, 40, 50), surf.get_rect(), border_radius=6)

            # Colored left border
            border_rect = pygame.Rect(0, 0, 4, rect.height)
            pygame.draw.rect(surf, color, border_rect, border_radius=6)

            # Title
            title_text = self.title_font.render(notification.title, True, (255, 255, 255))
            surf.blit(title_text, (15, 10))

            # Message (word wrap if needed)
            message_words = notification.message.split()
            message_lines = []
            current_line = ""

            for word in message_words:
                test_line = current_line + " " + word if current_line else word
                if self.message_font.size(test_line)[0] <= self.notification_width - 30:
                    current_line = test_line
                else:
                    if current_line:
                        message_lines.append(current_line)
                    current_line = word

            if current_line:
                message_lines.append(current_line)

            # Render message lines (max 2 lines)
            for i, line in enumerate(message_lines[:2]):
                line_text = self.message_font.render(line, True, (200, 200, 200))
                surf.blit(line_text, (15, 30 + i * 15))

            # Draw border
            pygame.draw.rect(surf, color, surf.get_rect(), 2, border_radius=6)

            # Blit to screen
            screen.blit(surf, rect)

            y_offset += self.notification_height + self.notification_margin

    def clear(self) -> None:
        """Clear all notifications."""
        self.notifications.clear()
