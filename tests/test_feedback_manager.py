"""
Comprehensive tests for FeedbackManager.

Tests the unified juice API that orchestrates AudioManager, ParticleSystem,
and AnimationSystem to provide high-level feedback methods.
"""

import pytest
from unittest.mock import Mock, patch, call

from src.utils.feedback_manager import (
    FeedbackManager,
    get_feedback_manager,
    FeedbackType
)
from src.utils.particle_system import ParticlePreset
from src.utils.animation_system import EasingFunction


class MockTarget:
    """Mock target object for animation tests."""
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.scale = 1.0
        self.opacity = 1.0


@pytest.fixture
def feedback_manager():
    """Create fresh FeedbackManager instance for each test."""
    # Reset singleton
    FeedbackManager._instance = None
    return get_feedback_manager()


class TestFeedbackManagerCore:
    """Test FeedbackManager initialization and core functionality."""
    
    def test_singleton_pattern(self):
        """Test FeedbackManager follows singleton pattern."""
        manager1 = get_feedback_manager()
        manager2 = get_feedback_manager()
        
        assert manager1 is manager2
    
    def test_initialization(self, feedback_manager):
        """Test FeedbackManager initializes with all juice systems."""
        assert feedback_manager.audio is not None
        assert feedback_manager.particles is not None
        assert feedback_manager.animations is not None
        assert feedback_manager.logger is not None
    
    def test_get_stats(self, feedback_manager):
        """Test getting statistics from all systems."""
        stats = feedback_manager.get_stats()
        
        assert "particles" in stats
        assert "animations" in stats
        assert isinstance(stats["particles"], dict)
        assert isinstance(stats["animations"], dict)
    
    def test_clear_all(self, feedback_manager):
        """Test clearing all active feedback."""
        # Emit some particles and animations
        feedback_manager.success(100, 100)
        
        # Clear all
        feedback_manager.clear_all()
        
        # Verify cleared
        particle_stats = feedback_manager.particles.get_stats()
        animation_stats = feedback_manager.animations.get_stats()
        
        assert particle_stats["active_particles"] == 0
        assert animation_stats["active_animations"] == 0


class TestSuccessFeedback:
    """Test success feedback method."""
    
    def test_success_emits_sparkle_particles(self, feedback_manager):
        """Test success feedback emits sparkle particles."""
        feedback_manager.success(100, 200, magnitude=1.0)
        
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] > 0  # Should have sparkle particles
    
    def test_success_magnitude_scales_particles(self, feedback_manager):
        """Test magnitude parameter scales particle count."""
        # Clear particles first
        feedback_manager.particles.clear()
        
        # Low magnitude
        feedback_manager.success(100, 100, magnitude=0.5)
        low_count = feedback_manager.particles.get_stats()["active_particles"]
        
        # Clear and test high magnitude
        feedback_manager.particles.clear()
        feedback_manager.success(100, 100, magnitude=2.0)
        high_count = feedback_manager.particles.get_stats()["active_particles"]
        
        assert high_count > low_count


class TestFailureFeedback:
    """Test failure feedback method."""
    
    def test_failure_emits_dust_particles(self, feedback_manager):
        """Test failure feedback emits dust particles."""
        feedback_manager.particles.clear()
        feedback_manager.failure(100, 200, magnitude=1.0)
        
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] > 0  # Should have dust particles
    
    def test_failure_magnitude_scales_particles(self, feedback_manager):
        """Test magnitude parameter scales particle count."""
        feedback_manager.particles.clear()
        feedback_manager.failure(100, 100, magnitude=0.5)
        low_count = feedback_manager.particles.get_stats()["active_particles"]
        
        feedback_manager.particles.clear()
        feedback_manager.failure(100, 100, magnitude=2.0)
        high_count = feedback_manager.particles.get_stats()["active_particles"]
        
        assert high_count > low_count


class TestLevelUpFeedback:
    """Test level-up feedback method."""
    
    def test_level_up_emits_multiple_particle_types(self, feedback_manager):
        """Test level-up emits sparkle AND magic particles."""
        feedback_manager.particles.clear()
        feedback_manager.level_up(100, 200)
        
        stats = feedback_manager.particles.get_stats()
        # Should have significant particles (50 sparkle + 30 magic = 80)
        assert stats["active_particles"] >= 75
    
    def test_level_up_animates_target_scale(self, feedback_manager):
        """Test level-up animates target with elastic scale."""
        target = MockTarget()
        target.scale = 1.0
        
        feedback_manager.level_up(100, 200, target=target)
        
        # Should have created animation
        stats = feedback_manager.animations.get_stats()
        assert stats["active_animations"] > 0
    
    def test_level_up_without_target(self, feedback_manager):
        """Test level-up works without target (no animation)."""
        # Should not crash
        feedback_manager.level_up(100, 200, target=None)
        
        # Particles should still emit
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] > 0


class TestAchievementFeedback:
    """Test achievement unlock feedback method."""
    
    def test_achievement_unlock_emits_magic_trail(self, feedback_manager):
        """Test achievement unlock emits magic particle trail."""
        feedback_manager.particles.clear()
        feedback_manager.achievement_unlock(100, 200, "First Kill")
        
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] > 0
    
    def test_achievement_unlock_animates_fade_in(self, feedback_manager):
        """Test achievement unlock animates target fade-in."""
        target = MockTarget()
        target.opacity = 1.0
        
        feedback_manager.achievement_unlock(100, 200, "First Kill", target=target)
        
        stats = feedback_manager.animations.get_stats()
        assert stats["active_animations"] > 0
    
    def test_achievement_unlock_without_target(self, feedback_manager):
        """Test achievement unlock works without target."""
        feedback_manager.achievement_unlock(100, 200, "First Kill", target=None)
        
        # Should still emit particles
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] > 0


class TestComboFeedback:
    """Test combo multiplier feedback method."""
    
    def test_combo_multiplier_scales_with_count(self, feedback_manager):
        """Test combo feedback intensity scales with combo count."""
        feedback_manager.particles.clear()
        feedback_manager.combo_multiplier(1, 100, 100, max_combo=10)
        low_count = feedback_manager.particles.get_stats()["active_particles"]
        
        feedback_manager.particles.clear()
        feedback_manager.combo_multiplier(10, 100, 100, max_combo=10)
        high_count = feedback_manager.particles.get_stats()["active_particles"]
        
        assert high_count > low_count
    
    def test_combo_uses_electric_at_high_combo(self, feedback_manager):
        """Test high combo (>= 5) uses electric particles."""
        feedback_manager.particles.clear()
        feedback_manager.combo_multiplier(5, 100, 100)
        
        # Should emit particles (electric preset)
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] > 0
    
    def test_combo_uses_sparkle_at_low_combo(self, feedback_manager):
        """Test low combo (< 5) uses sparkle particles."""
        feedback_manager.particles.clear()
        feedback_manager.combo_multiplier(3, 100, 100)
        
        # Should emit particles (sparkle preset)
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] > 0


class TestButtonClickFeedback:
    """Test button click feedback method."""
    
    def test_button_click_animates_scale_sequence(self, feedback_manager):
        """Test button click creates scale bounce sequence."""
        button = MockTarget()
        button.scale = 1.0
        
        feedback_manager.button_click(button)
        
        # Should create sequence (2 animations: down + up)
        stats = feedback_manager.animations.get_stats()
        assert stats["active_sequences"] > 0
    
    def test_button_click_without_scale_attribute(self, feedback_manager):
        """Test button click handles objects without scale gracefully."""
        button = Mock()
        del button.scale  # Remove scale attribute
        
        # Should not crash
        feedback_manager.button_click(button)


class TestIncidentCompleteFeedback:
    """Test incident completion feedback method."""
    
    def test_incident_complete_success_emits_sparkles(self, feedback_manager):
        """Test successful incident completion emits sparkles."""
        feedback_manager.particles.clear()
        feedback_manager.incident_complete(100, 200, success=True, critical=False)
        
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] > 0
    
    def test_incident_complete_failure_emits_smoke(self, feedback_manager):
        """Test failed incident completion emits smoke."""
        feedback_manager.particles.clear()
        feedback_manager.incident_complete(100, 200, success=False, critical=False)
        
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] > 0
    
    def test_incident_complete_critical_amplifies_feedback(self, feedback_manager):
        """Test critical flag increases particle count."""
        feedback_manager.particles.clear()
        feedback_manager.incident_complete(100, 100, success=True, critical=False)
        normal_count = feedback_manager.particles.get_stats()["active_particles"]
        
        feedback_manager.particles.clear()
        feedback_manager.incident_complete(100, 100, success=True, critical=True)
        critical_count = feedback_manager.particles.get_stats()["active_particles"]
        
        assert critical_count > normal_count


class TestSpecialistHiredFeedback:
    """Test specialist hired feedback method."""
    
    def test_specialist_hired_emits_magic_particles(self, feedback_manager):
        """Test specialist hired emits magic particles."""
        feedback_manager.particles.clear()
        feedback_manager.specialist_hired(100, 200, "Alice Chen")
        
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] > 0


class TestCriticalHitFeedback:
    """Test critical hit feedback method."""
    
    def test_critical_hit_emits_multiple_particle_types(self, feedback_manager):
        """Test critical hit emits electric + explosion particles."""
        feedback_manager.particles.clear()
        feedback_manager.critical_hit(100, 200, damage=500)
        
        stats = feedback_manager.particles.get_stats()
        # Should have electric (30) + explosion (20) = 50 particles
        assert stats["active_particles"] >= 45


class TestWarningFeedback:
    """Test warning feedback method."""
    
    def test_warning_emits_fire_particles(self, feedback_manager):
        """Test warning emits fire particles."""
        feedback_manager.particles.clear()
        feedback_manager.warning(100, 200, "Low resources!")
        
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] > 0


class TestScreenShake:
    """Test screen shake effect."""
    
    def test_screen_shake_creates_animation_sequence(self, feedback_manager):
        """Test screen shake creates multiple animations."""
        screen = MockTarget()
        screen.x = 0.0
        screen.y = 0.0
        
        feedback_manager.screen_shake(screen, intensity=10.0, duration=0.3)
        
        # Should create many animations (shake sequence)
        stats = feedback_manager.animations.get_stats()
        assert stats["active_sequences"] > 0
    
    def test_screen_shake_without_xy_attributes(self, feedback_manager):
        """Test screen shake handles objects without x/y gracefully."""
        # Clear previous animations
        feedback_manager.animations.stop_all()
        
        screen = Mock()
        del screen.x
        del screen.y
        
        # Should not crash
        feedback_manager.screen_shake(screen)
        
        # Should not create animations
        stats = feedback_manager.animations.get_stats()
        assert stats["active_animations"] == 0


class TestCascadeEffect:
    """Test cascade particle effect."""
    
    def test_cascade_emits_at_all_positions(self, feedback_manager):
        """Test cascade emits particles at all positions."""
        positions = [(100, 100), (200, 100), (300, 100)]
        
        feedback_manager.particles.clear()
        feedback_manager.cascade_effect(positions, ParticlePreset.SPARKLE)
        
        stats = feedback_manager.particles.get_stats()
        # Should have particles from all 3 positions (20 each = 60 total)
        assert stats["active_particles"] >= 55
    
    def test_cascade_with_empty_positions(self, feedback_manager):
        """Test cascade with no positions doesn't crash."""
        # Clear previous particles
        feedback_manager.particles.clear()
        
        feedback_manager.cascade_effect([], ParticlePreset.FIRE)
        
        # Should not crash, no particles emitted
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] == 0


class TestFeedbackTypeEnum:
    """Test FeedbackType enum."""
    
    def test_feedback_type_enum_values(self):
        """Test FeedbackType has expected values."""
        assert FeedbackType.SUCCESS.value == "success"
        assert FeedbackType.FAILURE.value == "failure"
        assert FeedbackType.LEVEL_UP.value == "level_up"
        assert FeedbackType.ACHIEVEMENT.value == "achievement"
        assert FeedbackType.COMBO.value == "combo"
        assert FeedbackType.BUTTON_CLICK.value == "button_click"
        assert FeedbackType.INCIDENT_COMPLETE.value == "incident_complete"
        assert FeedbackType.SPECIALIST_HIRED.value == "specialist_hired"
        assert FeedbackType.CRITICAL_HIT.value == "critical_hit"
        assert FeedbackType.WARNING.value == "warning"


class TestIntegration:
    """Integration tests combining multiple feedback types."""
    
    def test_multiple_feedback_calls_accumulate(self, feedback_manager):
        """Test multiple feedback calls accumulate particles/animations."""
        feedback_manager.particles.clear()
        feedback_manager.animations.stop_all()
        
        # Trigger multiple feedback events
        feedback_manager.success(100, 100)
        feedback_manager.level_up(200, 200)
        feedback_manager.combo_multiplier(5, 300, 300)
        
        # Should have many particles
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] > 50
    
    def test_clear_all_removes_everything(self, feedback_manager):
        """Test clear_all removes all active feedback."""
        # Trigger various feedback
        feedback_manager.success(100, 100)
        feedback_manager.level_up(200, 200)
        target = MockTarget()
        feedback_manager.achievement_unlock(300, 300, "Test", target)
        
        # Verify we have active feedback
        particle_stats = feedback_manager.particles.get_stats()
        animation_stats = feedback_manager.animations.get_stats()
        assert particle_stats["active_particles"] > 0
        
        # Clear all
        feedback_manager.clear_all()
        
        # Verify cleared
        particle_stats = feedback_manager.particles.get_stats()
        animation_stats = feedback_manager.animations.get_stats()
        assert particle_stats["active_particles"] == 0
        assert animation_stats["active_animations"] == 0
        assert animation_stats["active_sequences"] == 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_feedback_with_zero_magnitude(self, feedback_manager):
        """Test feedback with magnitude=0 doesn't crash."""
        feedback_manager.success(100, 100, magnitude=0.0)
        
        # Should work (though may emit 0 particles)
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] >= 0
    
    def test_feedback_with_negative_position(self, feedback_manager):
        """Test feedback with negative position doesn't crash."""
        feedback_manager.success(-100, -100)
        
        # Should work
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] > 0
    
    def test_combo_with_zero_max_combo(self, feedback_manager):
        """Test combo with max_combo=0 doesn't crash."""
        # Division by zero protection
        feedback_manager.combo_multiplier(5, 100, 100, max_combo=0)
        
        # Should not crash
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] >= 0
    
    def test_level_up_with_object_missing_scale(self, feedback_manager):
        """Test level-up with target missing scale attribute."""
        target = MockTarget()
        del target.scale
        
        # Should not crash
        feedback_manager.level_up(100, 100, target=target)
        
        # Should still emit particles
        stats = feedback_manager.particles.get_stats()
        assert stats["active_particles"] > 0
