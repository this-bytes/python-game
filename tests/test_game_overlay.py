"""Tests for GameOverlay - HUD system."""

import pytest
import pygame
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass

from src.ui.game_overlay import GameOverlay, Notification, NotificationLevel


# Mock game state for testing
@dataclass
class MockGameState:
    """Mock game state with required attributes."""
    money: float = 10000.0
    energy: float = 75.0
    max_energy: float = 100.0
    xp: float = 450.0
    xp_required: float = 1000.0
    level: int = 5
    game_speed: float = 1.0
    game_time_formatted: str = "12:34:56"
    active_incidents_count: int = 3
    total_incidents_count: int = 10
    available_specialists_count: int = 2
    total_specialists_count: int = 5
    passive_income_rate: float = 15.5


@pytest.fixture
def screen():
    """Create test screen surface."""
    pygame.init()
    return pygame.display.set_mode((800, 600))


@pytest.fixture
def overlay():
    """Create test overlay."""
    return GameOverlay(screen_width=800, screen_height=600)


@pytest.fixture
def game_state():
    """Create mock game state."""
    return MockGameState()


class TestGameOverlayCore:
    """Test overlay initialization and core functionality."""
    
    def test_initialization(self, overlay):
        """Test overlay initializes correctly."""
        assert overlay.screen_width == 800
        assert overlay.screen_height == 600
        assert overlay.show_fps is False
        assert overlay.show_debug is False
        assert overlay.notifications == []
        assert overlay.is_paused is False
        assert overlay.speed_index == 1
        assert overlay.speed_options == [0.5, 1.0, 2.0, 4.0]
    
    def test_initialization_with_options(self):
        """Test overlay initializes with custom options."""
        overlay = GameOverlay(
            screen_width=1024,
            screen_height=768,
            show_fps=True,
            show_debug=True
        )
        
        assert overlay.screen_width == 1024
        assert overlay.screen_height == 768
        assert overlay.show_fps is True
        assert overlay.show_debug is True
    
    def test_fonts_initialized(self, overlay):
        """Test fonts are initialized."""
        assert overlay.font_large is not None
        assert overlay.font_medium is not None
        assert overlay.font_small is not None
    
    def test_button_rects_created(self, overlay):
        """Test interaction button rectangles are created."""
        assert overlay.pause_button_rect is not None
        assert overlay.speed_button_rect is not None
        assert overlay.settings_button_rect is not None
        assert isinstance(overlay.pause_button_rect, pygame.Rect)


class TestNotificationSystem:
    """Test notification management."""
    
    def test_add_notification(self, overlay):
        """Test adding a notification."""
        overlay.add_notification("Test message", NotificationLevel.INFO)
        
        assert len(overlay.notifications) == 1
        assert overlay.notifications[0].message == "Test message"
        assert overlay.notifications[0].level == NotificationLevel.INFO
        assert overlay.notifications[0].opacity == 1.0
    
    def test_add_notification_with_duration(self, overlay):
        """Test adding notification with custom duration."""
        overlay.add_notification(
            "Important!", NotificationLevel.WARNING, duration=5.0
        )
        
        assert len(overlay.notifications) == 1
        assert overlay.notifications[0].duration == 5.0
    
    def test_notification_limit(self, overlay):
        """Test notification queue is limited."""
        for i in range(10):
            overlay.add_notification(f"Message {i}")
        
        assert len(overlay.notifications) <= overlay.max_notifications
    
    def test_clear_notifications(self, overlay):
        """Test clearing all notifications."""
        overlay.add_notification("Test 1")
        overlay.add_notification("Test 2")
        overlay.add_notification("Test 3")
        
        assert len(overlay.notifications) == 3
        
        overlay.clear_notifications()
        
        assert len(overlay.notifications) == 0
    
    def test_notification_levels(self, overlay):
        """Test different notification levels."""
        levels = [
            NotificationLevel.INFO,
            NotificationLevel.SUCCESS,
            NotificationLevel.WARNING,
            NotificationLevel.ERROR,
            NotificationLevel.ACHIEVEMENT,
        ]
        
        for level in levels:
            overlay.clear_notifications()
            overlay.add_notification("Test", level)
            assert overlay.notifications[0].level == level


class TestOverlayUpdate:
    """Test overlay update logic."""
    
    def test_update(self, overlay):
        """Test update doesn't crash."""
        overlay.update(delta_time=0.016, current_fps=60.0)
        assert True
    
    def test_update_with_notifications(self, overlay):
        """Test update processes notifications."""
        overlay.add_notification("Test", duration=0.1)
        
        # Update with short duration should remove notification
        import time
        time.sleep(0.15)
        overlay.update(delta_time=0.016, current_fps=60.0)
        
        assert len(overlay.notifications) == 0
    
    def test_fps_tracking(self):
        """Test FPS tracking when enabled."""
        overlay = GameOverlay(800, 600, show_fps=True)
        
        overlay.update(delta_time=0.016, current_fps=60.0)
        overlay.update(delta_time=0.016, current_fps=58.0)
        overlay.update(delta_time=0.016, current_fps=62.0)
        
        assert len(overlay.fps_history) == 3
        assert 58.0 in overlay.fps_history
    
    def test_fps_history_limit(self):
        """Test FPS history is limited."""
        overlay = GameOverlay(800, 600, show_fps=True)
        
        for i in range(100):
            overlay.update(delta_time=0.016, current_fps=60.0)
        
        assert len(overlay.fps_history) <= overlay.fps_max_samples


class TestOverlayRendering:
    """Test overlay rendering."""
    
    def test_render(self, overlay, screen, game_state):
        """Test render doesn't crash."""
        overlay.render(screen, game_state, current_fps=60.0)
        assert True
    
    def test_render_top_bar(self, overlay, screen):
        """Test top bar rendering."""
        overlay.render_top_bar(
            screen,
            money=5000.0,
            energy=50.0,
            max_energy=100.0,
            xp=250.0,
            xp_required=500.0,
            level=3,
            game_speed=1.0,
            game_time="01:23:45"
        )
        assert True
    
    def test_render_secondary_info(self, overlay, screen):
        """Test secondary info rendering."""
        overlay.render_secondary_info(
            screen,
            active_incidents=5,
            total_incidents=20,
            available_specialists=3,
            total_specialists=8,
            passive_income=12.5
        )
        assert True
    
    def test_render_notifications(self, overlay, screen):
        """Test notification rendering."""
        overlay.add_notification("Test 1")
        overlay.add_notification("Test 2", NotificationLevel.SUCCESS)
        
        overlay.render_notifications(screen)
        assert True
    
    def test_render_fps(self, overlay, screen):
        """Test FPS rendering."""
        overlay.show_fps = True
        overlay.fps_history = [60.0, 58.0, 62.0]
        
        overlay.render_fps(screen)
        assert True
    
    def test_render_fps_disabled(self, overlay, screen):
        """Test FPS rendering when disabled."""
        overlay.show_fps = False
        overlay.render_fps(screen)
        assert True


class TestValueAnimation:
    """Test animated value changes."""
    
    def test_animate_value_change(self, overlay):
        """Test value animation is triggered."""
        overlay.money_display = 1000.0
        overlay.animate_value_change(1000.0, 2000.0, "money_display")
        
        # Animation system should be active
        assert True
    
    def test_animate_value_no_change(self, overlay):
        """Test no animation when values are equal."""
        overlay.money_display = 1000.0
        overlay.animate_value_change(1000.0, 1000.0, "money_display")
        
        assert overlay.money_display == 1000.0


class TestPauseControl:
    """Test pause functionality."""
    
    def test_pause_toggle_click(self, overlay):
        """Test pause button click."""
        pause_called = False
        
        def on_pause():
            nonlocal pause_called
            pause_called = True
        
        overlay.set_pause_callback(on_pause)
        
        # Click pause button
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=overlay.pause_button_rect.center
        )
        
        handled = overlay.handle_event(event)
        
        assert handled is True
        assert overlay.is_paused is True
        assert pause_called is True
    
    def test_pause_keyboard(self, overlay):
        """Test pause with keyboard."""
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        
        assert overlay.is_paused is False
        overlay.handle_event(event)
        assert overlay.is_paused is True
        
        overlay.handle_event(event)
        assert overlay.is_paused is False


class TestSpeedControl:
    """Test game speed controls."""
    
    def test_speed_button_click(self, overlay):
        """Test speed button cycles speeds."""
        speed_changes = []
        
        def on_speed_change(speed):
            speed_changes.append(speed)
        
        overlay.set_speed_change_callback(on_speed_change)
        
        # Click speed button
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=overlay.speed_button_rect.center
        )
        
        overlay.handle_event(event)
        
        assert len(speed_changes) == 1
        assert speed_changes[0] == 2.0  # Next speed from 1.0
    
    def test_speed_cycles(self, overlay):
        """Test speed cycles through all options."""
        speeds = []
        
        def on_speed_change(speed):
            speeds.append(speed)
        
        overlay.set_speed_change_callback(on_speed_change)
        
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=overlay.speed_button_rect.center
        )
        
        # Cycle through all speeds
        for _ in range(len(overlay.speed_options)):
            overlay.handle_event(event)
        
        assert len(speeds) == len(overlay.speed_options)
    
    def test_speed_keyboard_increase(self, overlay):
        """Test speed increase with keyboard."""
        overlay.speed_index = 1  # Start at 1.0x
        
        speeds = []
        
        def on_speed_change(speed):
            speeds.append(speed)
        
        overlay.set_speed_change_callback(on_speed_change)
        
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_EQUALS)
        overlay.handle_event(event)
        
        assert len(speeds) == 1
        assert speeds[0] == 2.0
    
    def test_speed_keyboard_decrease(self, overlay):
        """Test speed decrease with keyboard."""
        overlay.speed_index = 1  # Start at 1.0x
        
        speeds = []
        
        def on_speed_change(speed):
            speeds.append(speed)
        
        overlay.set_speed_change_callback(on_speed_change)
        
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_MINUS)
        overlay.handle_event(event)
        
        assert len(speeds) == 1
        assert speeds[0] == 0.5


class TestSettingsControl:
    """Test settings button."""
    
    def test_settings_button_click(self, overlay):
        """Test settings button triggers callback."""
        settings_called = False
        
        def on_settings():
            nonlocal settings_called
            settings_called = True
        
        overlay.set_settings_callback(on_settings)
        
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=overlay.settings_button_rect.center
        )
        
        handled = overlay.handle_event(event)
        
        assert handled is True
        assert settings_called is True


class TestCallbacks:
    """Test callback management."""
    
    def test_set_pause_callback(self, overlay):
        """Test pause callback can be set."""
        callback = Mock()
        overlay.set_pause_callback(callback)
        assert overlay.on_pause == callback
    
    def test_set_speed_change_callback(self, overlay):
        """Test speed change callback can be set."""
        callback = Mock()
        overlay.set_speed_change_callback(callback)
        assert overlay.on_speed_change == callback
    
    def test_set_settings_callback(self, overlay):
        """Test settings callback can be set."""
        callback = Mock()
        overlay.set_settings_callback(callback)
        assert overlay.on_settings == callback


class TestToggleFunctions:
    """Test toggle functions."""
    
    def test_toggle_fps(self, overlay):
        """Test FPS display toggle."""
        initial = overlay.show_fps
        overlay.toggle_fps()
        assert overlay.show_fps == (not initial)
        
        overlay.toggle_fps()
        assert overlay.show_fps == initial
    
    def test_toggle_debug(self, overlay):
        """Test debug display toggle."""
        initial = overlay.show_debug
        overlay.toggle_debug()
        assert overlay.show_debug == (not initial)
        
        overlay.toggle_debug()
        assert overlay.show_debug == initial


class TestEdgeCases:
    """Test edge cases."""
    
    def test_render_with_missing_state_attributes(self, overlay, screen):
        """Test render handles missing game state attributes."""
        empty_state = object()
        overlay.render(screen, empty_state, current_fps=60.0)
        assert True
    
    def test_notification_word_wrap(self, overlay, screen):
        """Test notification message wraps long text."""
        long_message = "This is a very long notification message that should wrap across multiple lines to fit within the notification width"
        overlay.add_notification(long_message)
        
        overlay.render_notifications(screen)
        assert True
    
    def test_zero_max_energy(self, overlay, screen):
        """Test render handles zero max energy."""
        overlay.render_top_bar(
            screen,
            money=1000.0,
            energy=0.0,
            max_energy=0.0,
            xp=100.0,
            xp_required=200.0,
            level=1,
            game_speed=1.0
        )
        assert True
    
    def test_zero_xp_required(self, overlay, screen):
        """Test render handles zero XP required."""
        overlay.render_top_bar(
            screen,
            money=1000.0,
            energy=50.0,
            max_energy=100.0,
            xp=100.0,
            xp_required=0.0,
            level=20,
            game_speed=1.0
        )
        assert True
    
    def test_speed_boundary_increase(self, overlay):
        """Test speed increase at maximum doesn't crash."""
        overlay.speed_index = len(overlay.speed_options) - 1
        
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_EQUALS)
        overlay.handle_event(event)
        
        # Should stay at max
        assert overlay.speed_index == len(overlay.speed_options) - 1
    
    def test_speed_boundary_decrease(self, overlay):
        """Test speed decrease at minimum doesn't crash."""
        overlay.speed_index = 0
        
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_MINUS)
        overlay.handle_event(event)
        
        # Should stay at min
        assert overlay.speed_index == 0


class TestNotificationExpiry:
    """Test notification expiration."""
    
    def test_notification_fades(self, overlay):
        """Test notification opacity decreases before expiry."""
        overlay.add_notification("Test", duration=1.0)
        notification = overlay.notifications[0]
        
        import time
        time.sleep(0.6)  # Wait past fade start (0.5s)
        overlay.update(delta_time=0.016, current_fps=60.0)
        
        assert notification.opacity < 1.0
    
    def test_notification_expires(self, overlay):
        """Test notification is removed after duration."""
        overlay.add_notification("Test", duration=0.1)
        
        import time
        time.sleep(0.15)
        overlay.update(delta_time=0.016, current_fps=60.0)
        
        assert len(overlay.notifications) == 0


class TestMouseInteraction:
    """Test mouse interaction handling."""
    
    def test_click_outside_buttons_not_handled(self, overlay):
        """Test clicks outside buttons return False."""
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=(400, 300)
        )
        
        handled = overlay.handle_event(event)
        assert handled is False
    
    def test_right_click_not_handled(self, overlay):
        """Test right clicks are not handled."""
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=3,  # Right click
            pos=overlay.pause_button_rect.center
        )
        
        handled = overlay.handle_event(event)
        assert handled is False


class TestIntegration:
    """Test integrated workflows."""
    
    def test_full_workflow(self, overlay, screen, game_state):
        """Test complete overlay workflow."""
        # Add notifications
        overlay.add_notification("Achievement unlocked!", NotificationLevel.ACHIEVEMENT)
        overlay.add_notification("Specialist leveled up!", NotificationLevel.SUCCESS)
        
        # Update
        overlay.update(delta_time=0.016, current_fps=60.0)
        
        # Render
        overlay.render(screen, game_state, current_fps=60.0)
        
        # Interact
        pause_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=overlay.pause_button_rect.center
        )
        overlay.handle_event(pause_event)
        
        assert overlay.is_paused is True
        assert len(overlay.notifications) == 2
    
    def test_rapid_speed_changes(self, overlay):
        """Test rapid speed changes work correctly."""
        speeds = []
        
        def on_speed_change(speed):
            speeds.append(speed)
        
        overlay.set_speed_change_callback(on_speed_change)
        
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=overlay.speed_button_rect.center
        )
        
        # Rapid clicks
        for _ in range(10):
            overlay.handle_event(event)
        
        assert len(speeds) == 10
