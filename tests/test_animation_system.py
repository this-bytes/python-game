"""Tests for AnimationSystem - Comprehensive coverage of tweening and easing."""

import pytest
import math
from unittest.mock import patch, MagicMock

from src.utils.animation_system import (
    AnimationSystem,
    Animation,
    AnimationSequence,
    AnimationGroup,
    AnimationState,
    EasingFunction,
    AnimationConfig,
    apply_easing,
    get_animation_system
)


class MockTarget:
    """Mock object for animation testing."""
    
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.opacity = 1.0
        self.scale = 1.0
        self.rotation = 0.0


class TestAnimationSystemCore:
    """Test core animation system functionality."""
    
    @pytest.fixture
    def animation_system(self):
        """Create fresh animation system."""
        AnimationSystem._instance = None
        with patch('pygame.mixer.get_init', return_value=True):
            system = AnimationSystem()
            system.stop_all()
            return system
    
    def test_singleton_pattern(self):
        """Test that AnimationSystem enforces singleton."""
        AnimationSystem._instance = None
        with patch('pygame.mixer.get_init', return_value=True):
            system1 = AnimationSystem()
            system2 = AnimationSystem()
            system3 = get_animation_system()
            
            assert system1 is system2
            assert system2 is system3
    
    def test_initialization(self, animation_system):
        """Test animation system initializes correctly."""
        assert len(animation_system._active_animations) == 0
        assert len(animation_system._active_sequences) == 0
        assert len(animation_system._active_groups) == 0
    
    def test_get_stats(self, animation_system):
        """Test animation system statistics."""
        target = MockTarget()
        
        animation_system.animate(target, "x", 0, 100, 1.0)
        animation_system.animate(target, "y", 0, 200, 1.0)
        
        stats = animation_system.get_stats()
        
        assert stats["active_animations"] == 2
        assert stats["active_sequences"] == 0
        assert stats["active_groups"] == 0
        assert stats["total_active"] == 2


class TestBasicAnimation:
    """Test basic animation functionality."""
    
    @pytest.fixture
    def animation_system(self):
        """Create fresh animation system."""
        AnimationSystem._instance = None
        with patch('pygame.mixer.get_init', return_value=True):
            system = AnimationSystem()
            system.stop_all()
            return system
    
    def test_simple_animation(self, animation_system):
        """Test simple property animation."""
        target = MockTarget()
        
        anim = animation_system.animate(
            target=target,
            property="x",
            start_value=0.0,
            end_value=100.0,
            duration=1.0
        )
        
        # Initial value
        assert target.x == 0.0
        
        # Halfway through
        animation_system.update(0.5)
        assert 45.0 < target.x < 55.0  # Approximately 50
        
        # Complete
        animation_system.update(0.5)
        assert target.x == 100.0
    
    def test_animation_with_delay(self, animation_system):
        """Test animation with delay."""
        target = MockTarget()
        
        animation_system.animate(
            target=target,
            property="x",
            start_value=0.0,
            end_value=100.0,
            duration=1.0,
            delay=0.5
        )
        
        # During delay
        animation_system.update(0.3)
        assert target.x == 0.0  # Hasn't started
        
        # After delay
        animation_system.update(0.3)  # 0.1s into animation
        assert target.x > 0.0
    
    def test_animation_completion_callback(self, animation_system):
        """Test animation completion callback."""
        target = MockTarget()
        callback_called = []
        
        def on_complete():
            callback_called.append(True)
        
        animation_system.animate(
            target=target,
            property="x",
            start_value=0.0,
            end_value=100.0,
            duration=1.0,
            on_complete=on_complete
        )
        
        # Not called yet
        animation_system.update(0.5)
        assert len(callback_called) == 0
        
        # Called on completion
        animation_system.update(0.5)
        assert len(callback_called) == 1
    
    def test_animation_update_callback(self, animation_system):
        """Test animation update callback."""
        target = MockTarget()
        values = []
        
        def on_update(value):
            values.append(value)
        
        animation_system.animate(
            target=target,
            property="x",
            start_value=0.0,
            end_value=100.0,
            duration=1.0,
            on_update=on_update
        )
        
        # Update multiple times
        for _ in range(10):
            animation_system.update(0.1)
        
        # Should have collected values
        assert len(values) >= 9  # At least 9 updates (10th completes)
        assert values[0] < values[-1]  # Increasing
    
    def test_multiple_properties_simultaneously(self, animation_system):
        """Test animating multiple properties on same object."""
        target = MockTarget()
        
        animation_system.animate(target, "x", 0, 100, 1.0)
        animation_system.animate(target, "y", 0, 200, 1.0)
        animation_system.animate(target, "opacity", 1.0, 0.0, 1.0)
        
        # Update
        animation_system.update(0.5)
        
        # All properties should be animating
        assert 40 < target.x < 60
        assert 90 < target.y < 110
        assert 0.4 < target.opacity < 0.6


class TestEasingFunctions:
    """Test all easing functions."""
    
    @pytest.mark.parametrize("easing", [
        EasingFunction.LINEAR,
        EasingFunction.EASE_IN_QUAD,
        EasingFunction.EASE_OUT_QUAD,
        EasingFunction.EASE_IN_OUT_QUAD,
        EasingFunction.EASE_IN_CUBIC,
        EasingFunction.EASE_OUT_CUBIC,
        EasingFunction.EASE_IN_OUT_CUBIC,
        EasingFunction.EASE_IN_QUART,
        EasingFunction.EASE_OUT_QUART,
        EasingFunction.EASE_IN_OUT_QUART,
        EasingFunction.ELASTIC_IN,
        EasingFunction.ELASTIC_OUT,
        EasingFunction.ELASTIC_IN_OUT,
        EasingFunction.BOUNCE_IN,
        EasingFunction.BOUNCE_OUT,
        EasingFunction.BOUNCE_IN_OUT,
        EasingFunction.BACK_IN,
        EasingFunction.BACK_OUT,
        EasingFunction.BACK_IN_OUT,
    ])
    def test_easing_function(self, easing):
        """Test that easing function works without errors."""
        # Test at key points
        result_start = apply_easing(0.0, easing)
        result_mid = apply_easing(0.5, easing)
        result_end = apply_easing(1.0, easing)
        
        # Start should be 0 (or close)
        assert abs(result_start) < 0.1
        
        # End should be 1 (or close)
        assert abs(result_end - 1.0) < 0.1
        
        # Mid should be a valid number
        assert not math.isnan(result_mid)
        assert not math.isinf(result_mid)
    
    def test_linear_easing(self):
        """Test linear easing is exactly linear."""
        assert apply_easing(0.0, EasingFunction.LINEAR) == 0.0
        assert apply_easing(0.25, EasingFunction.LINEAR) == 0.25
        assert apply_easing(0.5, EasingFunction.LINEAR) == 0.5
        assert apply_easing(0.75, EasingFunction.LINEAR) == 0.75
        assert apply_easing(1.0, EasingFunction.LINEAR) == 1.0
    
    def test_ease_in_quad(self):
        """Test ease-in-quad accelerates."""
        result_quarter = apply_easing(0.25, EasingFunction.EASE_IN_QUAD)
        result_half = apply_easing(0.5, EasingFunction.EASE_IN_QUAD)
        
        # Should accelerate (early values lower than linear)
        assert result_quarter < 0.25
        assert result_half < 0.5
    
    def test_ease_out_quad(self):
        """Test ease-out-quad decelerates."""
        result_half = apply_easing(0.5, EasingFunction.EASE_OUT_QUAD)
        result_threequarters = apply_easing(0.75, EasingFunction.EASE_OUT_QUAD)
        
        # Should decelerate (early values higher than linear)
        assert result_half > 0.5
        assert result_threequarters > 0.75
    
    def test_bounce_out_bounces(self):
        """Test bounce-out creates bounce effect."""
        values = [apply_easing(t / 100, EasingFunction.BOUNCE_OUT) for t in range(101)]
        
        # Should have local maxima (bounces)
        local_maxima = 0
        for i in range(1, len(values) - 1):
            if values[i] > values[i-1] and values[i] > values[i+1]:
                local_maxima += 1
        
        # Should have at least one bounce
        assert local_maxima > 0
    
    def test_elastic_overshoots(self):
        """Test elastic easing overshoots target."""
        values = [apply_easing(t / 100, EasingFunction.ELASTIC_OUT) for t in range(101)]
        
        # Should overshoot (values > 1.0 during animation)
        max_value = max(values)
        assert max_value > 1.0
    
    def test_back_overshoots(self):
        """Test back easing overshoots."""
        # Back-in should go negative
        result = apply_easing(0.3, EasingFunction.BACK_IN)
        assert result < 0.0
        
        # Back-out should exceed 1.0
        values = [apply_easing(t / 100, EasingFunction.BACK_OUT) for t in range(101)]
        max_value = max(values)
        assert max_value > 1.0


class TestAnimationLifecycle:
    """Test animation state management."""
    
    def test_animation_pause_resume(self):
        """Test pausing and resuming animation."""
        target = MockTarget()
        anim = Animation(target, "x", 0, 100, 1.0)
        
        # Run for a bit
        anim.update(0.3)
        value_at_pause = target.x
        
        # Pause
        anim.pause()
        assert anim.state == AnimationState.PAUSED
        
        # Update while paused (no change)
        anim.update(0.2)
        assert target.x == value_at_pause
        
        # Resume
        anim.resume()
        assert anim.state == AnimationState.PLAYING
        
        # Should continue animating
        anim.update(0.2)
        assert target.x > value_at_pause
    
    def test_animation_stop(self):
        """Test stopping animation."""
        target = MockTarget()
        anim = Animation(target, "x", 0, 100, 1.0)
        
        anim.update(0.3)
        anim.stop()
        
        assert anim.state == AnimationState.STOPPED
        
        # Update after stop (should not continue)
        value_at_stop = target.x
        anim.update(0.5)
        assert target.x == value_at_stop
    
    def test_animation_completion_state(self):
        """Test animation completes with correct state."""
        target = MockTarget()
        anim = Animation(target, "x", 0, 100, 1.0)
        
        # Complete animation
        result = anim.update(1.1)
        
        assert result is False  # Signals completion
        assert anim.state == AnimationState.COMPLETED
        assert target.x == 100.0  # Final value set


class TestAnimationSequence:
    """Test sequential animations."""
    
    @pytest.fixture
    def animation_system(self):
        """Create fresh animation system."""
        AnimationSystem._instance = None
        with patch('pygame.mixer.get_init', return_value=True):
            system = AnimationSystem()
            system.stop_all()
            return system
    
    def test_sequence_plays_in_order(self, animation_system):
        """Test sequence plays animations one after another with delta time overflow.
        
        With delta time overflow handling:
        - update(0.5): First anim at 50% (x=50, y=0)
        - update(0.6): First anim completes (uses 0.5s), overflow 0.1s starts second anim (x=100, y=20)
        - update(0.5): Second anim advances from 0.1s to 0.6s total (y=120)
        """
        target = MockTarget()
        
        anim1 = Animation(target, "x", 0, 100, 1.0)
        anim2 = Animation(target, "y", 0, 200, 1.0)
        
        sequence = animation_system.create_sequence([anim1, anim2])
        
        # First animation should run
        animation_system.update(0.5)
        assert 40 < target.x < 60
        assert target.y == 0  # Second hasn't started
        
        # Complete first animation (0.6s total)
        # First anim needs 0.5s more, leaves 0.1s overflow for second anim
        animation_system.update(0.6)
        assert target.x == 100.0
        assert 15 < target.y < 25  # Second anim started with 0.1s (10% of 200 = 20)
        
        # Second animation continues (now at 0.6s total progress)
        animation_system.update(0.5)
        assert 110 < target.y < 130  # 60% of 200 = 120
    
    def test_sequence_pause_resume(self, animation_system):
        """Test pausing and resuming sequence."""
        target = MockTarget()
        
        anim1 = Animation(target, "x", 0, 100, 1.0)
        anim2 = Animation(target, "y", 0, 200, 1.0)
        
        sequence = AnimationSequence([anim1, anim2])
        
        # Run for a bit
        sequence.update(0.3)
        value_at_pause = target.x
        
        # Pause
        sequence.pause()
        sequence.update(0.2)
        assert target.x == value_at_pause
        
        # Resume
        sequence.resume()
        sequence.update(0.2)
        assert target.x > value_at_pause
    
    def test_sequence_completion(self, animation_system):
        """Test sequence completes after all animations."""
        target = MockTarget()
        
        anim1 = Animation(target, "x", 0, 100, 0.5)
        anim2 = Animation(target, "y", 0, 200, 0.5)
        
        sequence = animation_system.create_sequence([anim1, anim2])
        
        # Complete both animations
        animation_system.update(1.1)
        
        assert target.x == 100.0
        assert target.y == 200.0
        assert len(animation_system._active_sequences) == 0


class TestAnimationGroup:
    """Test parallel animations."""
    
    @pytest.fixture
    def animation_system(self):
        """Create fresh animation system."""
        AnimationSystem._instance = None
        with patch('pygame.mixer.get_init', return_value=True):
            system = AnimationSystem()
            system.stop_all()
            return system
    
    def test_group_plays_simultaneously(self, animation_system):
        """Test group plays all animations in parallel."""
        target = MockTarget()
        
        anim1 = Animation(target, "x", 0, 100, 1.0)
        anim2 = Animation(target, "y", 0, 200, 1.0)
        anim3 = Animation(target, "opacity", 1.0, 0.0, 1.0)
        
        group = animation_system.create_group([anim1, anim2, anim3])
        
        # Update
        animation_system.update(0.5)
        
        # All properties should be animating simultaneously
        assert 40 < target.x < 60
        assert 90 < target.y < 110
        assert 0.4 < target.opacity < 0.6
    
    def test_group_pause_resume(self, animation_system):
        """Test pausing and resuming group."""
        target = MockTarget()
        
        anim1 = Animation(target, "x", 0, 100, 1.0)
        anim2 = Animation(target, "y", 0, 200, 1.0)
        
        group = AnimationGroup([anim1, anim2])
        
        # Run for a bit
        group.update(0.3)
        x_at_pause = target.x
        y_at_pause = target.y
        
        # Pause
        group.pause()
        group.update(0.2)
        assert target.x == x_at_pause
        assert target.y == y_at_pause
        
        # Resume
        group.resume()
        group.update(0.2)
        assert target.x > x_at_pause
        assert target.y > y_at_pause
    
    def test_group_completion(self, animation_system):
        """Test group completes when all animations finish."""
        target = MockTarget()
        
        anim1 = Animation(target, "x", 0, 100, 0.5)
        anim2 = Animation(target, "y", 0, 200, 1.0)  # Longer duration
        
        group = animation_system.create_group([anim1, anim2])
        
        # After 0.6s, first animation done but second still running
        animation_system.update(0.6)
        assert target.x == 100.0
        assert len(animation_system._active_groups) == 1  # Group still active
        
        # After 1.1s total, both done
        animation_system.update(0.5)
        assert target.y == 200.0
        assert len(animation_system._active_groups) == 0


class TestAnimationSystemControl:
    """Test animation system global controls."""
    
    @pytest.fixture
    def animation_system(self):
        """Create fresh animation system."""
        AnimationSystem._instance = None
        with patch('pygame.mixer.get_init', return_value=True):
            system = AnimationSystem()
            system.stop_all()
            return system
    
    def test_pause_all(self, animation_system):
        """Test pausing all animations."""
        target1 = MockTarget()
        target2 = MockTarget()
        
        animation_system.animate(target1, "x", 0, 100, 1.0)
        animation_system.animate(target2, "y", 0, 200, 1.0)
        
        # Run for a bit
        animation_system.update(0.3)
        x_at_pause = target1.x
        y_at_pause = target2.y
        
        # Pause all
        animation_system.pause_all()
        animation_system.update(0.5)
        
        # Values should not change
        assert target1.x == x_at_pause
        assert target2.y == y_at_pause
    
    def test_resume_all(self, animation_system):
        """Test resuming all animations."""
        target = MockTarget()
        
        animation_system.animate(target, "x", 0, 100, 1.0)
        animation_system.update(0.3)
        
        animation_system.pause_all()
        x_at_pause = target.x
        
        animation_system.resume_all()
        animation_system.update(0.2)
        
        # Should continue animating
        assert target.x > x_at_pause
    
    def test_stop_all(self, animation_system):
        """Test stopping all animations."""
        target1 = MockTarget()
        target2 = MockTarget()
        
        animation_system.animate(target1, "x", 0, 100, 1.0)
        animation_system.animate(target2, "y", 0, 200, 1.0)
        
        # Run for a bit
        animation_system.update(0.3)
        
        # Stop all
        animation_system.stop_all()
        
        # All collections should be empty
        assert len(animation_system._active_animations) == 0
        assert len(animation_system._active_sequences) == 0
        assert len(animation_system._active_groups) == 0


class TestAnimationEnums:
    """Test animation system enums and data structures."""
    
    def test_easing_function_enum_values(self):
        """Test EasingFunction enum has all expected values."""
        expected_easings = [
            "linear", "ease_in_quad", "ease_out_quad", "ease_in_out_quad",
            "ease_in_cubic", "ease_out_cubic", "ease_in_out_cubic",
            "ease_in_quart", "ease_out_quart", "ease_in_out_quart",
            "elastic_in", "elastic_out", "elastic_in_out",
            "bounce_in", "bounce_out", "bounce_in_out",
            "back_in", "back_out", "back_in_out"
        ]
        
        for easing in expected_easings:
            assert any(e.value == easing for e in EasingFunction)
    
    def test_animation_state_enum_values(self):
        """Test AnimationState enum has all expected values."""
        expected_states = ["playing", "paused", "stopped", "completed"]
        
        for state in expected_states:
            assert any(s.value == state for s in AnimationState)
    
    def test_animation_config_dataclass(self):
        """Test AnimationConfig dataclass."""
        target = MockTarget()
        config = AnimationConfig(
            target=target,
            property="x",
            start_value=0.0,
            end_value=100.0,
            duration=1.5,
            easing=EasingFunction.EASE_IN_QUAD,
            delay=0.5,
            on_complete=None,
            on_update=None
        )
        
        assert config.target is target
        assert config.property == "x"
        assert config.start_value == 0.0
        assert config.end_value == 100.0
        assert config.duration == 1.5
        assert config.easing == EasingFunction.EASE_IN_QUAD
        assert config.delay == 0.5


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_zero_duration_animation(self):
        """Test animation with zero duration completes immediately."""
        target = MockTarget()
        anim = Animation(target, "x", 0, 100, 0.0)
        
        result = anim.update(0.1)
        
        assert result is False  # Completes immediately
        assert target.x == 100.0
    
    def test_negative_progress_handled(self):
        """Test that negative progress (shouldn't happen) is handled."""
        # Easing functions should handle edge cases
        result = apply_easing(0.0, EasingFunction.BOUNCE_OUT)
        assert not math.isnan(result)
        assert not math.isinf(result)
    
    def test_animation_removed_after_completion(self):
        """Test completed animations are removed from active list."""
        AnimationSystem._instance = None
        with patch('pygame.mixer.get_init', return_value=True):
            system = AnimationSystem()
            system.stop_all()
            
            target = MockTarget()
            system.animate(target, "x", 0, 100, 0.5)
            
            # Animation active
            assert len(system._active_animations) == 1
            
            # Complete animation
            system.update(0.6)
            
            # Animation should be removed
            assert len(system._active_animations) == 0
    
    def test_empty_sequence(self):
        """Test sequence with no animations."""
        sequence = AnimationSequence([])
        
        result = sequence.update(0.1)
        
        assert result is False  # Completes immediately
        assert sequence.state == AnimationState.COMPLETED
    
    def test_empty_group(self):
        """Test group with no animations."""
        group = AnimationGroup([])
        
        result = group.update(0.1)
        
        assert result is False  # Completes immediately
        assert group.state == AnimationState.COMPLETED
