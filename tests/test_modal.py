"""
Comprehensive tests for Modal component.

Tests modal dialog functionality: backdrop, animations, buttons, keyboard,
event handling, and result callbacks.
"""

import pytest
import pygame
from unittest.mock import Mock, call

from src.ui.components.modal import (
    Modal,
    ModalResult,
    ModalType,
    ModalButton
)


# Initialize pygame for tests
pygame.init()


@pytest.fixture
def screen():
    """Create test screen surface."""
    return pygame.display.set_mode((800, 600))


@pytest.fixture
def modal_info():
    """Create INFO modal."""
    return Modal(
        title="Information",
        message="This is an info message.",
        modal_type=ModalType.INFO
    )


@pytest.fixture
def modal_confirm():
    """Create CONFIRM modal."""
    return Modal(
        title="Confirm Action",
        message="Are you sure?",
        modal_type=ModalType.CONFIRM
    )


class TestModalCore:
    """Test Modal initialization and core functionality."""
    
    def test_modal_initialization(self):
        """Test modal initializes with correct defaults."""
        modal = Modal(
            title="Test",
            message="Test message",
            modal_type=ModalType.INFO
        )
        
        assert modal.title == "Test"
        assert modal.message == "Test message"
        assert modal.modal_type == ModalType.INFO
        assert not modal.visible
        assert modal.result is None
    
    def test_modal_types(self):
        """Test all modal types."""
        for modal_type in [ModalType.INFO, ModalType.WARNING, ModalType.ERROR, ModalType.CONFIRM]:
            modal = Modal("Title", "Message", modal_type=modal_type)
            assert modal.modal_type == modal_type
    
    def test_modal_custom_buttons(self):
        """Test modal with custom buttons."""
        buttons = [
            ModalButton("Accept", ModalResult.YES, "primary"),
            ModalButton("Decline", ModalResult.NO, "danger"),
        ]
        
        modal = Modal(
            "Custom",
            "Choose wisely",
            buttons=buttons
        )
        
        assert len(modal.buttons) == 2
        assert modal.buttons[0].text == "Accept"
        assert modal.buttons[1].text == "Decline"
    
    def test_modal_dimensions(self):
        """Test custom modal dimensions."""
        modal = Modal(
            "Test",
            "Message",
            width=500,
            height=300
        )
        
        assert modal.width == 500
        assert modal.height == 300


class TestModalDefaultButtons:
    """Test default button configurations for each modal type."""
    
    def test_info_modal_has_ok_button(self):
        """Test INFO modal has single OK button."""
        modal = Modal("Info", "Message", modal_type=ModalType.INFO)
        
        assert len(modal.buttons) == 1
        assert modal.buttons[0].text == "OK"
        assert modal.buttons[0].result == ModalResult.OK
    
    def test_warning_modal_has_ok_button(self):
        """Test WARNING modal has single OK button."""
        modal = Modal("Warning", "Message", modal_type=ModalType.WARNING)
        
        assert len(modal.buttons) == 1
        assert modal.buttons[0].text == "OK"
    
    def test_error_modal_has_ok_button(self):
        """Test ERROR modal has single OK button."""
        modal = Modal("Error", "Message", modal_type=ModalType.ERROR)
        
        assert len(modal.buttons) == 1
        assert modal.buttons[0].text == "OK"
        assert modal.buttons[0].style == "danger"
    
    def test_confirm_modal_has_yes_no_buttons(self):
        """Test CONFIRM modal has Yes/No buttons."""
        modal = Modal("Confirm", "Message", modal_type=ModalType.CONFIRM)
        
        assert len(modal.buttons) == 2
        assert modal.buttons[0].text == "Yes"
        assert modal.buttons[0].result == ModalResult.YES
        assert modal.buttons[1].text == "No"
        assert modal.buttons[1].result == ModalResult.NO


class TestModalShow:
    """Test modal show/display functionality."""
    
    def test_modal_show_makes_visible(self, modal_info, screen):
        """Test show() makes modal visible."""
        assert not modal_info.visible
        
        modal_info.show(screen)
        
        assert modal_info.visible
    
    def test_modal_show_centers_on_screen(self, modal_info, screen):
        """Test modal is centered on screen."""
        modal_info.show(screen)
        
        expected_x = (800 - modal_info.width) // 2
        expected_y = (600 - modal_info.height) // 2
        
        assert modal_info.x == expected_x
        assert modal_info.y == expected_y
    
    def test_modal_show_initializes_animations(self, modal_info, screen):
        """Test show() initializes fade + scale animations."""
        modal_info.show(screen)
        
        # Opacity and scale start values set
        assert modal_info.opacity == 0.0
        assert modal_info.scale == 0.8
        
        # Animations created (will be in animation system)
        stats = modal_info.animations.get_stats()
        assert stats["active_animations"] >= 2  # Fade + scale


class TestModalClose:
    """Test modal close functionality."""
    
    def test_modal_close_sets_result(self, modal_info, screen):
        """Test close() sets result."""
        modal_info.show(screen)
        modal_info.close(ModalResult.OK)
        
        assert modal_info.result == ModalResult.OK
    
    def test_modal_close_triggers_callback(self, modal_info, screen):
        """Test close() triggers on_result callback."""
        callback = Mock()
        modal_info.on_result = callback
        
        modal_info.show(screen)
        modal_info.close(ModalResult.OK)
        
        # Callback called after animation completes
        modal_info._on_close_complete()
        callback.assert_called_once_with(ModalResult.OK)
    
    def test_modal_close_starts_fade_out(self, modal_info, screen):
        """Test close() starts fade-out animation."""
        modal_info.show(screen)
        modal_info.animations.stop_all()  # Clear show animations
        
        modal_info.close(ModalResult.OK)
        
        # Fade out animation created
        stats = modal_info.animations.get_stats()
        assert stats["active_animations"] >= 1


class TestModalKeyboard:
    """Test modal keyboard handling."""
    
    def test_escape_closes_modal(self, modal_info, screen):
        """Test ESC key closes modal."""
        modal_info.show(screen)
        
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
        consumed = modal_info.handle_event(event)
        
        assert consumed
        assert modal_info.result == ModalResult.CLOSED
    
    def test_enter_triggers_default_button(self, modal_info, screen):
        """Test Enter key triggers first button."""
        modal_info.show(screen)
        
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})
        consumed = modal_info.handle_event(event)
        
        assert consumed
        assert modal_info.result == ModalResult.OK
    
    def test_keyboard_events_consumed(self, modal_info, screen):
        """Test modal consumes all keyboard events."""
        modal_info.show(screen)
        
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_a})
        consumed = modal_info.handle_event(event)
        
        # Even unhandled keys are consumed (modal is blocking)
        assert consumed


class TestModalMouseInteraction:
    """Test modal mouse click handling."""
    
    def test_backdrop_click_closes_modal(self, modal_info, screen):
        """Test clicking backdrop closes modal."""
        modal_info.show(screen)
        
        # Click outside modal bounds (backdrop)
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
            "button": 1,
            "pos": (10, 10)  # Outside modal
        })
        consumed = modal_info.handle_event(event)
        
        assert consumed
        assert modal_info.result == ModalResult.CLOSED
    
    def test_button_click_triggers_result(self, modal_confirm, screen):
        """Test clicking button triggers correct result."""
        modal_confirm.show(screen)
        
        # Wait for scale animation to complete (set scale to 1.0)
        modal_confirm.scale = 1.0
        
        # Calculate Yes button position (first button) in modal-local coords
        button_width = 100
        button_height = 35
        button_spacing = 15
        total_width = (button_width * 2) + button_spacing
        button_y_local = modal_confirm.height - button_height - 20
        button_x_local = (modal_confirm.width - total_width) // 2
        
        # Convert to screen coords
        button_x = modal_confirm.x + button_x_local
        button_y = modal_confirm.y + button_y_local
        
        # Mouse down on Yes button (center)
        event_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
            "button": 1,
            "pos": (button_x + 50, button_y + 17)  # Center of button
        })
        modal_confirm.handle_event(event_down)
        
        # Mouse up on same button
        event_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {
            "button": 1,
            "pos": (button_x + 50, button_y + 17)
        })
        consumed = modal_confirm.handle_event(event_up)
        
        assert consumed
        assert modal_confirm.result == ModalResult.YES
    
    def test_button_hover_changes_state(self, modal_info, screen):
        """Test hovering over button updates hover state."""
        modal_info.show(screen)
        
        # Wait for scale animation to complete
        modal_info.scale = 1.0
        
        # Calculate button position in modal-local coords
        button_width = 100
        button_height = 35
        button_y_local = modal_info.height - button_height - 20
        button_x_local = (modal_info.width - button_width) // 2
        
        # Convert to screen coords
        button_x = modal_info.x + button_x_local
        button_y = modal_info.y + button_y_local
        
        # Move mouse over button (center)
        event = pygame.event.Event(pygame.MOUSEMOTION, {
            "pos": (button_x + 50, button_y + 17)
        })
        modal_info.handle_event(event)
        
        assert modal_info.hovered_button_index == 0


class TestModalCallbacks:
    """Test button callbacks."""
    
    def test_button_callback_executed_on_click(self, screen):
        """Test button callback is executed when button clicked."""
        callback_mock = Mock()
        
        buttons = [
            ModalButton("Custom", ModalResult.CUSTOM, callback=callback_mock)
        ]
        
        modal = Modal("Test", "Message", buttons=buttons)
        modal.show(screen)
        
        # Wait for scale animation to complete
        modal.scale = 1.0
        
        # Calculate button position in modal-local coords
        button_width = 100
        button_height = 35
        button_y_local = modal.height - button_height - 20
        button_x_local = (modal.width - button_width) // 2
        
        # Convert to screen coords
        button_x = modal.x + button_x_local
        button_y = modal.y + button_y_local
        
        # Simulate button click (center)
        event_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
            "button": 1,
            "pos": (button_x + 50, button_y + 17)
        })
        modal.handle_event(event_down)
        
        event_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {
            "button": 1,
            "pos": (button_x + 50, button_y + 17)
        })
        modal.handle_event(event_up)
        
        # Callback executed
        callback_mock.assert_called_once()


class TestModalRendering:
    """Test modal rendering."""
    
    def test_modal_renders_without_crash(self, modal_info, screen):
        """Test modal renders without crashing."""
        modal_info.show(screen)
        
        # Should not crash
        modal_info.render(screen)
    
    def test_hidden_modal_does_not_render(self, modal_info, screen):
        """Test hidden modal doesn't render."""
        # Modal not shown, should not render
        modal_info.render(screen)
        # No crash = success
    
    def test_modal_renders_with_opacity(self, modal_info, screen):
        """Test modal respects opacity during fade."""
        modal_info.show(screen)
        modal_info.opacity = 0.5
        
        # Should render at half opacity
        modal_info.render(screen)
    
    def test_modal_renders_with_scale(self, modal_info, screen):
        """Test modal respects scale during animation."""
        modal_info.show(screen)
        modal_info.scale = 1.2
        
        # Should render at 1.2x scale
        modal_info.render(screen)


class TestModalTextWrapping:
    """Test text wrapping for long messages."""
    
    def test_long_message_wraps(self, screen):
        """Test long message is wrapped to multiple lines."""
        long_message = "This is a very long message that should wrap across multiple lines when displayed in the modal dialog because it exceeds the maximum width."
        
        modal = Modal("Title", long_message, width=400)
        modal.show(screen)
        
        # Text should be wrapped
        lines = modal._wrap_text(long_message, 360)
        assert len(lines) > 1
    
    def test_short_message_no_wrap(self, screen):
        """Test short message doesn't wrap."""
        short_message = "Short"
        
        modal = Modal("Title", short_message)
        modal.show(screen)
        
        lines = modal._wrap_text(short_message, 360)
        assert len(lines) == 1


class TestModalVisibility:
    """Test modal visibility state."""
    
    def test_is_visible_when_shown(self, modal_info, screen):
        """Test is_visible() returns True when shown."""
        modal_info.show(screen)
        assert modal_info.is_visible()
    
    def test_is_not_visible_initially(self, modal_info):
        """Test is_visible() returns False initially."""
        assert not modal_info.is_visible()
    
    def test_is_not_visible_after_close(self, modal_info, screen):
        """Test is_visible() returns False after close completes."""
        modal_info.show(screen)
        modal_info.close(ModalResult.OK)
        modal_info._on_close_complete()
        
        assert not modal_info.is_visible()


class TestModalIntegration:
    """Integration tests for modal functionality."""
    
    def test_full_modal_workflow(self, screen):
        """Test complete modal workflow: show → interact → close → callback."""
        callback_mock = Mock()
        
        modal = Modal(
            "Confirm Delete",
            "Delete this item?",
            modal_type=ModalType.CONFIRM,
            on_result=callback_mock
        )
        
        # Show modal
        modal.show(screen)
        assert modal.is_visible()
        
        # Wait for scale animation to complete
        modal.scale = 1.0
        
        # Calculate Yes button position in modal-local coords
        button_width = 100
        button_height = 35
        button_spacing = 15
        total_width = (button_width * 2) + button_spacing
        button_y_local = modal.height - button_height - 20
        button_x_local = (modal.width - total_width) // 2
        
        # Convert to screen coords
        button_x = modal.x + button_x_local
        button_y = modal.y + button_y_local
        
        # Simulate clicking Yes button (center)
        event_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
            "button": 1,
            "pos": (button_x + 50, button_y + 17)
        })
        modal.handle_event(event_down)
        
        event_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {
            "button": 1,
            "pos": (button_x + 50, button_y + 17)
        })
        modal.handle_event(event_up)
        
        # Close animation completes
        modal._on_close_complete()
        
        # Modal closed, callback triggered
        assert not modal.is_visible()
        assert modal.result == ModalResult.YES
        callback_mock.assert_called_once_with(ModalResult.YES)
    
    def test_multiple_modals_independent(self, screen):
        """Test multiple modal instances are independent."""
        modal1 = Modal("Modal 1", "Message 1")
        modal2 = Modal("Modal 2", "Message 2")
        
        modal1.show(screen)
        modal2.show(screen)
        
        # Both visible
        assert modal1.is_visible()
        assert modal2.is_visible()
        
        # Close one
        modal1.close(ModalResult.OK)
        modal1._on_close_complete()
        
        # Only first closed
        assert not modal1.is_visible()
        assert modal2.is_visible()


class TestModalEdgeCases:
    """Test edge cases and error handling."""
    
    def test_modal_with_empty_message(self, screen):
        """Test modal with empty message doesn't crash."""
        modal = Modal("Title", "")
        modal.show(screen)
        modal.render(screen)
    
    def test_modal_with_no_buttons(self, screen):
        """Test modal with empty button list."""
        modal = Modal("Title", "Message", buttons=[])
        modal.show(screen)
        
        # Should still render
        modal.render(screen)
    
    def test_modal_close_before_show(self):
        """Test closing modal before showing doesn't crash."""
        modal = Modal("Title", "Message")
        modal.close(ModalResult.OK)
        # Should not crash
    
    def test_event_handling_when_not_visible(self, modal_info):
        """Test events ignored when modal not visible."""
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
        consumed = modal_info.handle_event(event)
        
        # Event not consumed (modal not visible)
        assert not consumed
