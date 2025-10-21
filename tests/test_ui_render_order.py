import types
import pytest
import typing

import pygame

from src.ui.panels.specialist_roster_panel import SpecialistRosterPanel
from src.ui.panels.incident_queue_panel import IncidentQueuePanel
from src.models.game_state import GameState
from src.ui.components.scroll_container import ScrollContainer


class SpyScrollContainer:
    def __init__(self):
        self.calls = []
        self.position = (0, 0)
        self.size = (0, 0)
        self.content_height = 0
        self.scroll_bar_width = 15

    def set_content_height(self, h):
        self.content_height = h
        self.calls.append(('set_content_height', h))

    def render_background(self, screen):
        self.calls.append(('render_background', None))

    def render_scrollbar(self, screen):
        self.calls.append(('render_scrollbar', None))

    def get_scroll_offset(self):
        return 0

    def handle_event(self, event):
        return False


@pytest.fixture(autouse=True)
def pygame_init_and_quit():
    pygame.init()
    yield
    pygame.quit()


def test_specialist_roster_panel_calls_scroll_in_order():
    game_state = GameState()
    # Create panel
    panel = SpecialistRosterPanel(game_state)

    # Replace scroll_container with spy (cast to ScrollContainer for static typing)
    spy = SpyScrollContainer()
    panel.scroll_container = typing.cast(ScrollContainer, spy)

    # Create real pygame Surface and content rect
    screen = pygame.Surface((200, 200))
    content_rect = pygame.Rect(10, 10, 100, 180)

    # Call render_content
    panel.render_content(screen, content_rect)

    # Find indices of background and scrollbar
    names = [c[0] for c in spy.calls]
    assert 'render_background' in names, "render_background should be called"
    assert 'render_scrollbar' in names, "render_scrollbar should be called"
    assert names.index('render_background') < names.index('render_scrollbar'), "Background must be rendered before scrollbar"


def test_incident_queue_panel_calls_scroll_in_order():
    game_state = GameState()
    game_state.incidents = []
    panel = IncidentQueuePanel(game_state)
    spy = SpyScrollContainer()
    panel.scroll_container = typing.cast(ScrollContainer, spy)

    screen = pygame.Surface((240, 240))
    content_rect = pygame.Rect(10, 10, 120, 200)

    panel.render_content(screen, content_rect)

    names = [c[0] for c in spy.calls]
    assert 'render_background' in names
    assert 'render_scrollbar' in names
    assert names.index('render_background') < names.index('render_scrollbar')
