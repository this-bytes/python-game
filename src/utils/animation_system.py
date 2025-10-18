"""Animation System - Tweening and easing for smooth animations.

Provides:
- Easing functions (linear, ease-in/out, elastic, bounce, etc.)
- Property animation (position, size, color, opacity)
- Animation sequences and chains
- Animation groups (parallel and sequential)
- Pause/resume/reverse support
- Callback system for animation events

Usage:
    animations = get_animation_system()
    
    # Simple tween
    animations.animate(
        target=my_button,
        property="y",
        start=0,
        end=100,
        duration=0.5,
        easing=EasingFunction.EASE_OUT_QUAD
    )
    
    # Fluent API (chaining)
    animations.tween(my_sprite) \\
        .move_to(x=400, y=300, duration=1.0) \\
        .then() \\
        .scale_to(2.0, duration=0.5, easing=EasingFunction.ELASTIC_OUT) \\
        .with_callback(on_complete)
    
    # Update in game loop
    animations.update(delta_time)
"""

import math
from typing import Any, Callable, Optional, List, Dict
from dataclasses import dataclass
from enum import Enum

from src.utils.logger import GameLogger


class EasingFunction(Enum):
    """Easing function types (Robert Penner's equations)."""
    LINEAR = "linear"
    EASE_IN_QUAD = "ease_in_quad"
    EASE_OUT_QUAD = "ease_out_quad"
    EASE_IN_OUT_QUAD = "ease_in_out_quad"
    EASE_IN_CUBIC = "ease_in_cubic"
    EASE_OUT_CUBIC = "ease_out_cubic"
    EASE_IN_OUT_CUBIC = "ease_in_out_cubic"
    EASE_IN_QUART = "ease_in_quart"
    EASE_OUT_QUART = "ease_out_quart"
    EASE_IN_OUT_QUART = "ease_in_out_quart"
    ELASTIC_IN = "elastic_in"
    ELASTIC_OUT = "elastic_out"
    ELASTIC_IN_OUT = "elastic_in_out"
    BOUNCE_IN = "bounce_in"
    BOUNCE_OUT = "bounce_out"
    BOUNCE_IN_OUT = "bounce_in_out"
    BACK_IN = "back_in"
    BACK_OUT = "back_out"
    BACK_IN_OUT = "back_in_out"


class AnimationState(Enum):
    """Animation playback state."""
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"


@dataclass
class AnimationConfig:
    """Configuration for a single animation."""
    target: Any  # Object being animated
    property: str  # Property name to animate
    start_value: float
    end_value: float
    duration: float
    easing: EasingFunction = EasingFunction.LINEAR
    delay: float = 0.0
    on_complete: Optional[Callable] = None
    on_update: Optional[Callable] = None


class Animation:
    """Single property animation with easing."""
    
    def __init__(
        self,
        target: Any,
        property: str,
        start_value: float,
        end_value: float,
        duration: float,
        easing: EasingFunction = EasingFunction.LINEAR,
        delay: float = 0.0,
        on_complete: Optional[Callable] = None,
        on_update: Optional[Callable] = None
    ):
        """Initialize animation.
        
        Args:
            target: Object to animate
            property: Property name (e.g., "x", "y", "opacity")
            start_value: Starting value
            end_value: Target value
            duration: Animation duration in seconds
            easing: Easing function to use
            delay: Delay before starting animation
            on_complete: Callback when animation completes
            on_update: Callback on each update
        """
        self.target = target
        self.property = property
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration
        self.easing = easing
        self.delay = delay
        self.on_complete = on_complete
        self.on_update = on_update
        
        self.elapsed = 0.0
        self.state = AnimationState.PLAYING
    
    def update(self, delta_time: float) -> bool:
        """Update animation.
        
        Args:
            delta_time: Time elapsed since last update
            
        Returns:
            True if animation still running, False if completed
        """
        if self.state != AnimationState.PLAYING:
            return self.state != AnimationState.COMPLETED
        
        # Handle delay
        if self.delay > 0:
            self.delay -= delta_time
            if self.delay > 0:
                return True
            # Delay finished, use overflow time
            delta_time = abs(self.delay)
            self.delay = 0
        
        # Update elapsed time
        self.elapsed += delta_time
        
        # Check completion
        if self.elapsed >= self.duration:
            # Set final value
            setattr(self.target, self.property, self.end_value)
            self.state = AnimationState.COMPLETED
            
            # Call completion callback
            if self.on_complete:
                self.on_complete()
            
            return False
        
        # Calculate progress (0.0 to 1.0)
        progress = self.elapsed / self.duration
        
        # Apply easing
        eased_progress = apply_easing(progress, self.easing)
        
        # Interpolate value
        current_value = self.start_value + (self.end_value - self.start_value) * eased_progress
        
        # Set property
        setattr(self.target, self.property, current_value)
        
        # Call update callback
        if self.on_update:
            self.on_update(current_value)
        
        return True
    
    def pause(self):
        """Pause animation."""
        self.state = AnimationState.PAUSED
    
    def resume(self):
        """Resume paused animation."""
        if self.state == AnimationState.PAUSED:
            self.state = AnimationState.PLAYING
    
    def stop(self):
        """Stop animation."""
        self.state = AnimationState.STOPPED


class AnimationSequence:
    """Sequence of animations played one after another."""
    
    def __init__(self, animations: List[Animation]):
        """Initialize animation sequence.
        
        Args:
            animations: List of animations to play sequentially
        """
        self.animations = animations
        self.current_index = 0
        self.state = AnimationState.PLAYING
    
    def update(self, delta_time: float) -> bool:
        """Update current animation in sequence.
        
        Args:
            delta_time: Time elapsed
            
        Returns:
            True if sequence still running, False if completed
        """
        if self.state != AnimationState.PLAYING:
            return self.state != AnimationState.COMPLETED
        
        if self.current_index >= len(self.animations):
            self.state = AnimationState.COMPLETED
            return False
        
        # Update current animation (may consume all or part of delta_time)
        remaining_time = delta_time
        
        while remaining_time > 0 and self.current_index < len(self.animations):
            current_anim = self.animations[self.current_index]
            
            # Calculate time until this animation completes
            time_until_complete = current_anim.duration - current_anim.elapsed
            
            if remaining_time >= time_until_complete:
                # This animation will complete this frame
                current_anim.update(time_until_complete)
                remaining_time -= time_until_complete
                self.current_index += 1
            else:
                # Animation continues next frame
                current_anim.update(remaining_time)
                remaining_time = 0
        
        if self.current_index >= len(self.animations):
            self.state = AnimationState.COMPLETED
            return False
        
        return True
    
    def pause(self):
        """Pause sequence."""
        self.state = AnimationState.PAUSED
        if self.current_index < len(self.animations):
            self.animations[self.current_index].pause()
    
    def resume(self):
        """Resume sequence."""
        if self.state == AnimationState.PAUSED:
            self.state = AnimationState.PLAYING
            if self.current_index < len(self.animations):
                self.animations[self.current_index].resume()
    
    def stop(self):
        """Stop sequence."""
        self.state = AnimationState.STOPPED
        for anim in self.animations:
            anim.stop()


class AnimationGroup:
    """Group of animations played simultaneously."""
    
    def __init__(self, animations: List[Animation]):
        """Initialize animation group.
        
        Args:
            animations: List of animations to play in parallel
        """
        self.animations = animations
        self.state = AnimationState.PLAYING
    
    def update(self, delta_time: float) -> bool:
        """Update all animations in group.
        
        Args:
            delta_time: Time elapsed
            
        Returns:
            True if any animation still running, False if all completed
        """
        if self.state != AnimationState.PLAYING:
            return self.state != AnimationState.COMPLETED
        
        # Update all animations
        any_running = False
        for anim in self.animations:
            if anim.update(delta_time):
                any_running = True
        
        if not any_running:
            self.state = AnimationState.COMPLETED
        
        return any_running
    
    def pause(self):
        """Pause all animations."""
        self.state = AnimationState.PAUSED
        for anim in self.animations:
            anim.pause()
    
    def resume(self):
        """Resume all animations."""
        if self.state == AnimationState.PAUSED:
            self.state = AnimationState.PLAYING
            for anim in self.animations:
                anim.resume()
    
    def stop(self):
        """Stop all animations."""
        self.state = AnimationState.STOPPED
        for anim in self.animations:
            anim.stop()


class AnimationSystem:
    """Singleton animation system managing all active animations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnimationSystem, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize animation system."""
        if self._initialized:
            return
        
        self._initialized = True
        self.logger = GameLogger("AnimationSystem")
        
        # Active animations/sequences/groups
        self._active_animations: List[Animation] = []
        self._active_sequences: List[AnimationSequence] = []
        self._active_groups: List[AnimationGroup] = []
        
        self.logger.logger.info("AnimationSystem initialized")
    
    def animate(
        self,
        target: Any,
        property: str,
        start_value: float,
        end_value: float,
        duration: float,
        easing: EasingFunction = EasingFunction.LINEAR,
        delay: float = 0.0,
        on_complete: Optional[Callable] = None,
        on_update: Optional[Callable] = None
    ) -> Animation:
        """Create and start animation.
        
        Args:
            target: Object to animate
            property: Property name to animate
            start_value: Starting value
            end_value: Target value
            duration: Animation duration
            easing: Easing function
            delay: Delay before starting
            on_complete: Completion callback
            on_update: Update callback
            
        Returns:
            Created animation
        """
        animation = Animation(
            target, property, start_value, end_value, duration,
            easing, delay, on_complete, on_update
        )
        self._active_animations.append(animation)
        return animation
    
    def create_sequence(self, animations: List[Animation]) -> AnimationSequence:
        """Create animation sequence.
        
        Args:
            animations: Animations to play sequentially
            
        Returns:
            Created sequence
        """
        sequence = AnimationSequence(animations)
        self._active_sequences.append(sequence)
        return sequence
    
    def create_group(self, animations: List[Animation]) -> AnimationGroup:
        """Create animation group.
        
        Args:
            animations: Animations to play in parallel
            
        Returns:
            Created group
        """
        group = AnimationGroup(animations)
        self._active_groups.append(group)
        return group
    
    def update(self, delta_time: float):
        """Update all active animations.
        
        Args:
            delta_time: Time elapsed since last update
        """
        # Update individual animations
        self._active_animations = [
            anim for anim in self._active_animations
            if anim.update(delta_time)
        ]
        
        # Update sequences
        self._active_sequences = [
            seq for seq in self._active_sequences
            if seq.update(delta_time)
        ]
        
        # Update groups
        self._active_groups = [
            group for group in self._active_groups
            if group.update(delta_time)
        ]
    
    def pause_all(self):
        """Pause all animations."""
        for anim in self._active_animations:
            anim.pause()
        for seq in self._active_sequences:
            seq.pause()
        for group in self._active_groups:
            group.pause()
    
    def resume_all(self):
        """Resume all animations."""
        for anim in self._active_animations:
            anim.resume()
        for seq in self._active_sequences:
            seq.resume()
        for group in self._active_groups:
            group.resume()
    
    def stop_all(self):
        """Stop all animations."""
        for anim in self._active_animations:
            anim.stop()
        for seq in self._active_sequences:
            seq.stop()
        for group in self._active_groups:
            group.stop()
        
        self._active_animations.clear()
        self._active_sequences.clear()
        self._active_groups.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """Get animation system statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            "active_animations": len(self._active_animations),
            "active_sequences": len(self._active_sequences),
            "active_groups": len(self._active_groups),
            "total_active": (
                len(self._active_animations) +
                len(self._active_sequences) +
                len(self._active_groups)
            )
        }


# Easing function implementations (Robert Penner's equations)

def apply_easing(t: float, easing: EasingFunction) -> float:
    """Apply easing function to progress value.
    
    Args:
        t: Progress (0.0 to 1.0)
        easing: Easing function to apply
        
    Returns:
        Eased progress value
    """
    if easing == EasingFunction.LINEAR:
        return t
    elif easing == EasingFunction.EASE_IN_QUAD:
        return t * t
    elif easing == EasingFunction.EASE_OUT_QUAD:
        return t * (2 - t)
    elif easing == EasingFunction.EASE_IN_OUT_QUAD:
        return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t
    elif easing == EasingFunction.EASE_IN_CUBIC:
        return t * t * t
    elif easing == EasingFunction.EASE_OUT_CUBIC:
        return (t - 1) ** 3 + 1
    elif easing == EasingFunction.EASE_IN_OUT_CUBIC:
        return 4 * t ** 3 if t < 0.5 else 1 + (t - 1) * (2 * (t - 1)) ** 2
    elif easing == EasingFunction.EASE_IN_QUART:
        return t ** 4
    elif easing == EasingFunction.EASE_OUT_QUART:
        return 1 - (t - 1) ** 4
    elif easing == EasingFunction.EASE_IN_OUT_QUART:
        return 8 * t ** 4 if t < 0.5 else 1 - 8 * (t - 1) ** 4
    elif easing == EasingFunction.ELASTIC_IN:
        return 0 if t == 0 else 1 if t == 1 else -2 ** (10 * (t - 1)) * math.sin((t - 1.1) * 5 * math.pi)
    elif easing == EasingFunction.ELASTIC_OUT:
        return 0 if t == 0 else 1 if t == 1 else 2 ** (-10 * t) * math.sin((t - 0.1) * 5 * math.pi) + 1
    elif easing == EasingFunction.ELASTIC_IN_OUT:
        if t == 0 or t == 1:
            return t
        t = t * 2
        if t < 1:
            return -0.5 * 2 ** (10 * (t - 1)) * math.sin((t - 1.1) * 5 * math.pi)
        return 0.5 * 2 ** (-10 * (t - 1)) * math.sin((t - 1.1) * 5 * math.pi) + 1
    elif easing == EasingFunction.BOUNCE_OUT:
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375
    elif easing == EasingFunction.BOUNCE_IN:
        return 1 - apply_easing(1 - t, EasingFunction.BOUNCE_OUT)
    elif easing == EasingFunction.BOUNCE_IN_OUT:
        if t < 0.5:
            return apply_easing(t * 2, EasingFunction.BOUNCE_IN) * 0.5
        return apply_easing(t * 2 - 1, EasingFunction.BOUNCE_OUT) * 0.5 + 0.5
    elif easing == EasingFunction.BACK_IN:
        c1 = 1.70158
        return t * t * ((c1 + 1) * t - c1)
    elif easing == EasingFunction.BACK_OUT:
        c1 = 1.70158
        return 1 + (t - 1) ** 2 * ((c1 + 1) * (t - 1) + c1)
    elif easing == EasingFunction.BACK_IN_OUT:
        c1 = 1.70158
        c2 = c1 * 1.525
        if t < 0.5:
            return (2 * t) ** 2 * ((c2 + 1) * 2 * t - c2) / 2
        return ((2 * t - 2) ** 2 * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2
    else:
        return t  # Fallback to linear


# Singleton accessor
def get_animation_system() -> AnimationSystem:
    """Get singleton AnimationSystem instance.
    
    Returns:
        Singleton AnimationSystem
    """
    return AnimationSystem()
