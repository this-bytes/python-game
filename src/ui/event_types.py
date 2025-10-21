"""
Defines custom Pygame event types for the UI.

This module centralizes the definition of all custom UI events, ensuring
consistency and preventing conflicts with Pygame's built-in event types.
Using custom events allows for a decoupled architecture where UI components
can communicate without direct dependencies.

-   **SHOW_MODAL**: Posted when a UI component requests to open a modal.
-   **HIDE_MODAL**: Posted to request closing the currently active modal.
-   **BUTTON_CLICKED**: A generic event for button interactions.
-   **NOTIFICATION_NEW**: Posted to show a new notification to the player.

To use, post an event using pygame.event.post() with the appropriate
event type and a dictionary of data.

Example:
    event = pygame.event.Event(
        UI_EVENT_TYPES["SHOW_MODAL"],
        {"modal_id": "specialist_detail", "specialist": specialist_data}
    )
    pygame.event.post(event)
"""
import pygame

# Start custom event types from USEREVENT, Pygame's base for user-defined events.
# This ensures we don't conflict with Pygame's internal event numbers.
SHOW_MODAL = pygame.USEREVENT + 1
HIDE_MODAL = pygame.USEREVENT + 2
BUTTON_CLICKED = pygame.USEREVENT + 3
NOTIFICATION_NEW = pygame.USEREVENT + 4

# A dictionary for easy lookup and management of event types.
# This makes the code more readable and easier to debug.
UI_EVENT_TYPES = {
    "SHOW_MODAL": SHOW_MODAL,
    "HIDE_MODAL": HIDE_MODAL,
    "BUTTON_CLICKED": BUTTON_CLICKED,
    "NOTIFICATION_NEW": NOTIFICATION_NEW,
}

# You can also create a reverse mapping if needed for debugging
EVENT_TYPE_NAMES = {v: k for k, v in UI_EVENT_TYPES.items()}
