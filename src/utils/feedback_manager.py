"""
Feedback Manager - Unified juice API combining audio, particles, and animations.

This module provides high-level methods that orchestrate coordinated feedback
across audio, visual effects, and animations. Each method encapsulates the
"juice" for common game events, making polish trivial to add.

Usage:
    feedback = get_feedback_manager()
    
    # One-line polish for common events
    feedback.success(x, y)
    feedback.level_up(specialist_position)
    feedback.combo_multiplier(combo_count, position)
    feedback.achievement_unlock(x, y, achievement_name)
    feedback.button_click(button_component)
    
Example:
    # Before FeedbackManager (3 separate calls):
    audio.play_sound("level_up")
    particles.explosion(x, y, "sparkle", 50)
    animations.animate(panel, "scale", 1.0, 1.2, 0.5, ELASTIC_OUT)
    
    # After FeedbackManager (one call):
    feedback.level_up(x, y)
"""

from typing import Optional, Tuple, Any
import math
from enum import Enum

from src.utils.audio_manager import get_audio_manager, SoundCategory
from src.utils.particle_system import get_particle_system, ParticlePreset
from src.utils.animation_system import get_animation_system, EasingFunction
from src.utils.logger import GameLogger


class FeedbackType(Enum):
    """Types of feedback events."""
    SUCCESS = "success"
    FAILURE = "failure"
    LEVEL_UP = "level_up"
    ACHIEVEMENT = "achievement"
    COMBO = "combo"
    BUTTON_CLICK = "button_click"
    INCIDENT_COMPLETE = "incident_complete"
    SPECIALIST_HIRED = "specialist_hired"
    CRITICAL_HIT = "critical_hit"
    WARNING = "warning"


class FeedbackManager:
    """Manages coordinated audio, particle, and animation feedback.
    
    FeedbackManager orchestrates all three juice systems (AudioManager,
    ParticleSystem, AnimationSystem) to provide simple one-line calls
    for adding professional polish to game events.
    
    Attributes:
        audio: AudioManager singleton instance
        particles: ParticleSystem singleton instance
        animations: AnimationSystem singleton instance
        logger: GameLogger for debugging feedback calls
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern - only one FeedbackManager instance."""
        if cls._instance is None:
            cls._instance = super(FeedbackManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize FeedbackManager with juice system references."""
        if self._initialized:
            return
        
        self.audio = get_audio_manager()
        self.particles = get_particle_system()
        self.animations = get_animation_system()
        self.logger = GameLogger("FeedbackManager")

        self._initialized = True
        self.logger.info("FeedbackManager initialized")
    
    # ==================== HIGH-LEVEL FEEDBACK METHODS ====================
    
    def success(self, x: float, y: float, magnitude: float = 1.0) -> None:
        """Generic success feedback: sound + sparkle particles + pulse.
        
        Use for: completing actions, successful assignments, positive events.
        
        Args:
            x: X position for particles
            y: Y position for particles
            magnitude: Intensity multiplier (0.5-2.0, default 1.0)
        """
        self.logger.debug(f"Success feedback at ({x}, {y}) magnitude={magnitude}")
        
        # Sound: Light positive chime (if available)
        # self.audio.play_sound("success", volume_multiplier=magnitude)
        
        # Particles: Sparkle burst
        particle_count = int(15 * magnitude)
        self.particles.explosion(x, y, ParticlePreset.SPARKLE.value, particle_count)
        
        # Animation: Quick pulse effect (if target provided later)
        # Can be extended with target parameter for scale pulse
    
    def failure(self, x: float, y: float, magnitude: float = 1.0) -> None:
        """Generic failure feedback: sound + dust particles + shake.
        
        Use for: failed actions, errors, negative events.
        
        Args:
            x: X position for particles
            y: Y position for particles
            magnitude: Intensity multiplier (0.5-2.0, default 1.0)
        """
        self.logger.debug(f"Failure feedback at ({x}, {y}) magnitude={magnitude}")
        
        # Sound: Negative buzz (if available)
        # self.audio.play_sound("failure", volume_multiplier=magnitude)
        
        # Particles: Dust cloud
        particle_count = int(20 * magnitude)
        self.particles.explosion(x, y, ParticlePreset.DUST.value, particle_count)
        
        # Animation: Screen shake (would need screen reference)
    
    def level_up(self, x: float, y: float, target: Optional[Any] = None) -> None:
        """Level-up feedback: fanfare + explosion + elastic scale.
        
        Use for: specialist level-up, prestige level increase.
        
        Args:
            x: X position for particles
            y: Y position for particles
            target: Optional target object to animate (scale pulse)
        """
        self.logger.info(f"Level-up feedback at ({x}, {y})")
        
        # Sound: Triumphant fanfare (if available)
        # self.audio.play_sound("level_up_fanfare")
        
        # Particles: Large sparkle explosion
        self.particles.explosion(x, y, ParticlePreset.SPARKLE.value, particle_count=50)
        self.particles.explosion(x, y, ParticlePreset.MAGIC.value, particle_count=30)
        
        # Animation: Elastic scale pulse
        if target and hasattr(target, 'scale'):
            original_scale = getattr(target, 'scale', 1.0)
            self.animations.animate(
                target, "scale",
                original_scale, original_scale * 1.3,
                duration=0.5,
                easing=EasingFunction.ELASTIC_OUT
            )
    
    def achievement_unlock(
        self,
        x: float,
        y: float,
        achievement_name: str,
        target: Optional[object] = None
    ) -> None:
        """Achievement unlock feedback: chime + magic trail + fade-in.
        
        Use for: unlocking achievements, completing milestones.
        
        Args:
            x: X position for particles
            y: Y position for particles
            achievement_name: Name of achievement (for logging)
            target: Optional UI element to animate (fade-in)
        """
        self.logger.info(f"Achievement unlocked: {achievement_name} at ({x}, {y})")
        
        # Sound: Bell chime (if available)
        # self.audio.play_sound("achievement_chime")
        
        # Particles: Magic sparkle trail
        self.particles.trail(x, y, ParticlePreset.MAGIC.value, particle_count=40)
        
        # Animation: Fade-in effect
        if target and hasattr(target, 'opacity'):
            self.animations.animate(
                target, "opacity",
                0.0, 1.0,
                duration=1.0,
                easing=EasingFunction.EASE_OUT_CUBIC
            )
    
    def combo_multiplier(
        self,
        combo_count: int,
        x: float,
        y: float,
        max_combo: int = 10
    ) -> None:
        """Combo multiplier feedback: escalating sound + trail + bounce.
        
        Use for: combo systems, chain bonuses, multiplier increases.
        
        Args:
            combo_count: Current combo count
            x: X position for particles
            y: Y position for particles
            max_combo: Maximum combo for intensity scaling (default 10)
        """
        self.logger.debug(f"Combo x{combo_count} at ({x}, {y})")
        
        # Scale intensity with combo count (up to max_combo)
        # Protect against division by zero
        if max_combo <= 0:
            intensity = 1.0
        else:
            intensity = min(combo_count / max_combo, 1.0)
        
        # Sound: Escalating pitch with combo (if available)
        # pitch = 1.0 + (intensity * 0.5)  # 1.0 to 1.5x pitch
        # self.audio.play_sound("combo_hit", volume_multiplier=0.5 + intensity * 0.5)
        
        # Particles: Trail effect (more particles at higher combo)
        particle_count = int(10 + (intensity * 30))  # 10-40 particles
        if combo_count >= 5:
            # High combo: Use electric particles for intensity
            self.particles.trail(x, y, ParticlePreset.ELECTRIC.value, particle_count)
        else:
            # Low combo: Use sparkle particles
            self.particles.trail(x, y, ParticlePreset.SPARKLE.value, particle_count)
    
    def button_click(self, button: Any) -> None:
        """Button click feedback: click sound + scale bounce.
        
        Use for: all UI button interactions.
        
        Args:
            button: Button component to animate (needs scale attribute)
        """
        # Sound: UI click (if available)
        # self.audio.play_sound("button_click", volume_multiplier=0.3)
        
        # Animation: Quick bounce
        if hasattr(button, 'scale'):
            original_scale = getattr(button, 'scale', 1.0)
            # Sequence: scale down, then bounce back up
            anim_down = self.animations.animate(
                button, "scale",
                original_scale, original_scale * 0.9,
                duration=0.1,
                easing=EasingFunction.EASE_OUT_QUAD
            )
            anim_up = self.animations.animate(
                button, "scale",
                original_scale * 0.9, original_scale,
                duration=0.2,
                easing=EasingFunction.BOUNCE_OUT
            )
            # Create sequence
            self.animations.create_sequence([anim_down, anim_up])
    
    def incident_complete(
        self,
        x: float,
        y: float,
        success: bool,
        critical: bool = False
    ) -> None:
        """Incident completion feedback: conditional based on outcome.
        
        Use for: incident resolution, mission completion.
        
        Args:
            x: X position for particles
            y: Y position for particles
            success: Whether incident resolved successfully
            critical: Whether this was critical/high-importance (amplifies feedback)
        """
        magnitude = 1.5 if critical else 1.0
        
        if success:
            self.logger.info(f"Incident complete (success) at ({x}, {y})")
            # Success: green sparkles + positive sound
            self.particles.explosion(x, y, ParticlePreset.SPARKLE.value, int(25 * magnitude))
            # self.audio.play_sound("incident_success", volume_multiplier=magnitude)
        else:
            self.logger.warning(f"Incident complete (failure) at ({x}, {y})")
            # Failure: smoke + negative sound
            self.particles.explosion(x, y, ParticlePreset.SMOKE.value, int(20 * magnitude))
            # self.audio.play_sound("incident_failure", volume_multiplier=magnitude)
    
    def specialist_hired(self, x: float, y: float, specialist_name: str) -> None:
        """Specialist hired feedback: positive sound + magic particles.
        
        Use for: hiring new specialists, team expansion.
        
        Args:
            x: X position for particles
            y: Y position for particles
            specialist_name: Name of hired specialist (for logging)
        """
        self.logger.info(f"Specialist hired: {specialist_name} at ({x}, {y})")
        
        # Sound: Positive chime (if available)
        # self.audio.play_sound("specialist_hired")
        
        # Particles: Magic portal effect
        self.particles.explosion(x, y, ParticlePreset.MAGIC.value, particle_count=40)
    
    def critical_hit(self, x: float, y: float, damage: float) -> None:
        """Critical hit feedback: impact sound + blood/electric particles.
        
        Use for: critical incidents, high-impact events.
        
        Args:
            x: X position for particles
            y: Y position for particles
            damage: Damage amount (for intensity scaling)
        """
        self.logger.info(f"Critical hit at ({x}, {y}) damage={damage}")
        
        # Sound: Heavy impact (if available)
        # self.audio.play_sound("critical_hit")
        
        # Particles: Electric + explosion combo
        self.particles.explosion(x, y, ParticlePreset.ELECTRIC.value, particle_count=30)
        self.particles.explosion(x, y, ParticlePreset.EXPLOSION.value, particle_count=20)
    
    def warning(self, x: float, y: float, message: str) -> None:
        """Warning feedback: alert sound + fire particles.
        
        Use for: warnings, alerts, danger notifications.
        
        Args:
            x: X position for particles
            y: Y position for particles
            message: Warning message (for logging)
        """
        self.logger.warning(f"Warning at ({x}, {y}): {message}")
        
        # Sound: Alert tone (if available)
        # self.audio.play_sound("warning_alert")
        
        # Particles: Fire burst (indicates danger)
        self.particles.explosion(x, y, ParticlePreset.FIRE.value, particle_count=15)
    
    # ==================== ADVANCED FEEDBACK COMPOSITIONS ====================
    
    def screen_shake(
        self,
        screen: Any,
        intensity: float = 10.0,
        duration: float = 0.3
    ) -> None:
        """Screen shake effect using animation system.
        
        Args:
            screen: Screen/camera object with x, y attributes
            intensity: Shake magnitude in pixels (default 10.0)
            duration: Shake duration in seconds (default 0.3)
        """
        # Validate screen has x and y attributes
        try:
            original_x = screen.x
            original_y = screen.y
        except AttributeError:
            # Screen doesn't have x/y, cannot shake
            return
        
        # Create rapid shake sequence
        shake_count = int(duration / 0.05)  # 20 shakes per second
        animations = []
        
        for i in range(shake_count):
            # Random offset within intensity radius
            import random
            offset_x = random.uniform(-intensity, intensity)
            offset_y = random.uniform(-intensity, intensity)
            
            anim_x = self.animations.animate(
                screen, "x",
                original_x, original_x + offset_x,
                duration=0.05,
                easing=EasingFunction.LINEAR
            )
            anim_y = self.animations.animate(
                screen, "y",
                original_y, original_y + offset_y,
                duration=0.05,
                easing=EasingFunction.LINEAR
            )
            animations.extend([anim_x, anim_y])
        
        # Return to original position
        anim_reset_x = self.animations.animate(
            screen, "x",
            screen.x, original_x,
            duration=0.1,
            easing=EasingFunction.EASE_OUT_QUAD
        )
        anim_reset_y = self.animations.animate(
            screen, "y",
            screen.y, original_y,
            duration=0.1,
            easing=EasingFunction.EASE_OUT_QUAD
        )
        animations.extend([anim_reset_x, anim_reset_y])
        
        # Create sequence
        self.animations.create_sequence(animations)
    
    def cascade_effect(
        self,
        positions: list[Tuple[float, float]],
        preset: ParticlePreset,
        delay_between: float = 0.1
    ) -> None:
        """Cascade particle effect across multiple positions.
        
        Args:
            positions: List of (x, y) positions
            preset: ParticlePreset to use for all positions
            delay_between: Delay in seconds between each explosion (default 0.1)
        """
        for i, (x, y) in enumerate(positions):
            # Delayed particle emission (would need timer/scheduler)
            # For now, emit all immediately (can enhance with delay later)
            self.particles.explosion(x, y, preset.value, particle_count=20)
    
    # ==================== UTILITY METHODS ====================
    
    def clear_all(self) -> None:
        """Clear all active feedback (particles, animations).
        
        Use when transitioning scenes or resetting game state.
        """
        self.particles.clear()
        self.animations.stop_all()
        self.logger.info("Cleared all active feedback")
    
    def get_stats(self) -> dict:
        """Get statistics from all juice systems.
        
        Returns:
            Dictionary with stats from audio, particles, animations
        """
        return {
            "particles": self.particles.get_stats(),
            "animations": self.animations.get_stats()
        }


# ==================== SINGLETON ACCESS ====================

_feedback_manager_instance = None


def get_feedback_manager() -> FeedbackManager:
    """Get FeedbackManager singleton instance.
    
    Returns:
        FeedbackManager singleton instance
    """
    global _feedback_manager_instance
    if _feedback_manager_instance is None:
        _feedback_manager_instance = FeedbackManager()
    return _feedback_manager_instance
