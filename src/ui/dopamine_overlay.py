"""Dopamine Feedback Overlay - Visual celebration system for addictive gameplay.

This overlay displays:
- Combo counters with escalating visual effects
- Risk/reward contract offers with exciting animations
- Completion celebrations with particles and screen effects
- Level-up fanfares
- Achievement popups

All designed to make every action FEEL rewarding.
"""

import pygame
from typing import List, Dict, Optional
import time
import random
import math


class ParticleEffect:
    """Simple particle for visual celebrations."""
    
    def __init__(self, x, y, color, velocity_x, velocity_y, lifetime=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.age = 0.0
        self.size = random.randint(2, 5)
    
    def update(self, delta_time):
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        self.velocity_y += 200 * delta_time  # Gravity
        self.age += delta_time
        return self.age < self.lifetime
    
    def render(self, screen):
        # Fade out over lifetime
        alpha = int(255 * (1.0 - self.age / self.lifetime))
        color = (*self.color[:3], alpha) if len(self.color) == 4 else self.color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)


class FloatingText:
    """Floating text for reward notifications."""
    
    def __init__(self, text, x, y, color, font, velocity_y=-50, lifetime=2.0):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.font = font
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.age = 0.0
    
    def update(self, delta_time):
        self.y += self.velocity_y * delta_time
        self.age += delta_time
        return self.age < self.lifetime
    
    def render(self, screen):
        # Fade out over lifetime
        alpha = int(255 * (1.0 - self.age / self.lifetime))
        
        # Render text with outline for visibility
        text_surface = self.font.render(self.text, True, self.color)
        text_rect = text_surface.get_rect(center=(int(self.x), int(self.y)))
        
        # Outline
        outline_color = (0, 0, 0)
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            outline_surface = self.font.render(self.text, True, outline_color)
            outline_rect = outline_surface.get_rect(center=(text_rect.centerx + dx, text_rect.centery + dy))
            screen.blit(outline_surface, outline_rect)
        
        screen.blit(text_surface, text_rect)


class DopamineFeedbackOverlay:
    """Overlay system for dopamine-triggering visual feedback."""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Visual effects
        self.particles: List[ParticleEffect] = []
        self.floating_texts: List[FloatingText] = []
        
        # Fonts
        pygame.font.init()
        self.combo_font = pygame.font.Font(None, 72)
        self.reward_font = pygame.font.Font(None, 48)
        self.message_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Combo display state
        self.current_combo = 0
        self.combo_multiplier = 1.0
        self.combo_display_scale = 1.0
        self.combo_pulse_timer = 0.0
        
        # Risk contract notifications
        self.risk_contract_notifications: List[Dict] = []
        
        # Screen shake
        self.screen_shake_intensity = 0.0
        self.screen_shake_duration = 0.0
    
    def process_feedback(self, feedback_queue: List[Dict], dopamine_system):
        """Process feedback from game state and trigger visuals.
        
        Args:
            feedback_queue: List of feedback events from GameState
            dopamine_system: Reference to DopamineSystem for current state
        """
        for feedback_event in feedback_queue:
            event_type = feedback_event["type"]
            
            if event_type == "assignment":
                self._process_assignment_feedback(feedback_event)
            elif event_type == "completion":
                self._process_completion_feedback(feedback_event)
            elif event_type == "risk_contract_offer":
                self._process_risk_contract_offer(feedback_event)
            elif event_type == "combo_broken":
                self._process_combo_broken(feedback_event)
        
        # Update combo display from dopamine system
        self.current_combo = dopamine_system.combo_state.current_combo
        self.combo_multiplier = dopamine_system.combo_state.get_multiplier()
        
        # Clear processed feedback
        feedback_queue.clear()
    
    def _process_assignment_feedback(self, event: Dict):
        """Process incident assignment feedback."""
        feedback = event["feedback"]
        combo = feedback["combo_count"]
        is_milestone = feedback.get("is_milestone", False)
        
        if is_milestone:
            # Trigger combo milestone celebration
            self._trigger_combo_milestone(combo, feedback["multiplier"])
    
    def _process_completion_feedback(self, event: Dict):
        """Process incident completion feedback."""
        feedback = event["feedback"]
        
        # Floating reward text
        reward = feedback["final_reward"]
        message = feedback["message"]
        
        # Position near center-top
        x = self.screen_width // 2 + random.randint(-50, 50)
        y = self.screen_height // 3
        
        # Color based on reward tier
        tier = feedback.get("reward_tier")
        if tier and hasattr(tier, 'value'):
            tier_value = tier.value
        else:
            tier_value = "minor"
        
        if tier_value == "epic":
            color = (255, 50, 255)
            self._spawn_particle_burst(x, y, 50, color)
            self._trigger_screen_shake(0.3, 10)
        elif tier_value == "major":
            color = (255, 200, 0)
            self._spawn_particle_burst(x, y, 30, color)
        elif tier_value == "standard":
            color = (0, 255, 200)
            self._spawn_particle_burst(x, y, 15, color)
        else:
            color = (0, 255, 100)
        
        # Add floating text
        floating_text = FloatingText(
            message,
            x, y,
            color,
            self.reward_font,
            velocity_y=-80
        )
        self.floating_texts.append(floating_text)
        
        # Pulse combo counter if active
        if self.current_combo > 0:
            self.combo_pulse_timer = 0.3
            self.combo_display_scale = 1.5
    
    def _process_risk_contract_offer(self, event: Dict):
        """Process risk contract offer notification."""
        contract = event["contract"]
        
        # Add to notification queue
        self.risk_contract_notifications.append({
            "contract": contract,
            "timestamp": time.time(),
            "lifetime": 5.0  # Show for 5 seconds
        })
    
    def _process_combo_broken(self, event: Dict):
        """Process combo broken event."""
        # Show "COMBO BROKEN" message
        x = self.screen_width // 2
        y = self.screen_height // 2
        
        broken_text = FloatingText(
            "COMBO BROKEN!",
            x, y,
            (255, 50, 50),
            self.combo_font,
            velocity_y=-30,
            lifetime=1.5
        )
        self.floating_texts.append(broken_text)
        
        # Reset combo display
        self.current_combo = 0
        self.combo_multiplier = 1.0
    
    def _trigger_combo_milestone(self, combo: int, multiplier: float):
        """Trigger visual celebration for combo milestone."""
        x = self.screen_width // 2
        y = 100
        
        # Big combo announcement
        if combo >= 50:
            message = f"🔥 LEGENDARY {combo}X! 🔥"
            color = (255, 50, 255)
            particles = 100
            self._trigger_screen_shake(0.5, 15)
        elif combo >= 20:
            message = f"⚡ MEGA {combo}X! ⚡"
            color = (255, 100, 0)
            particles = 60
            self._trigger_screen_shake(0.3, 10)
        elif combo >= 10:
            message = f"💥 SUPER {combo}X!"
            color = (255, 200, 0)
            particles = 40
        elif combo >= 5:
            message = f"✨ COMBO x{combo}!"
            color = (0, 255, 200)
            particles = 20
        else:
            message = f"Combo x{combo}"
            color = (0, 255, 100)
            particles = 10
        
        # Floating text
        milestone_text = FloatingText(
            message,
            x, y,
            color,
            self.combo_font,
            velocity_y=-60,
            lifetime=2.0
        )
        self.floating_texts.append(milestone_text)
        
        # Particle burst
        self._spawn_particle_burst(x, y, particles, color)
        
        # Pulse combo display
        self.combo_pulse_timer = 0.5
        self.combo_display_scale = 2.0
    
    def _spawn_particle_burst(self, x, y, count, color):
        """Spawn a burst of particles at position."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 300)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed - 100  # Bias upward
            
            particle = ParticleEffect(
                x, y,
                color,
                velocity_x, velocity_y,
                lifetime=random.uniform(0.5, 1.5)
            )
            self.particles.append(particle)
    
    def _trigger_screen_shake(self, duration, intensity):
        """Trigger screen shake effect."""
        self.screen_shake_duration = duration
        self.screen_shake_intensity = intensity
    
    def get_screen_shake_offset(self):
        """Get current screen shake offset."""
        if self.screen_shake_duration > 0:
            shake_x = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
            shake_y = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
            return (int(shake_x), int(shake_y))
        return (0, 0)
    
    def update(self, delta_time):
        """Update all visual effects."""
        # Update particles
        self.particles = [p for p in self.particles if p.update(delta_time)]
        
        # Update floating texts
        self.floating_texts = [t for t in self.floating_texts if t.update(delta_time)]
        
        # Update combo display pulse
        if self.combo_pulse_timer > 0:
            self.combo_pulse_timer -= delta_time
            # Ease back to scale 1.0
            self.combo_display_scale = 1.0 + (self.combo_display_scale - 1.0) * max(0, self.combo_pulse_timer / 0.3)
        
        # Update screen shake
        if self.screen_shake_duration > 0:
            self.screen_shake_duration -= delta_time
            if self.screen_shake_duration <= 0:
                self.screen_shake_intensity = 0
        
        # Remove expired risk contract notifications
        current_time = time.time()
        self.risk_contract_notifications = [
            n for n in self.risk_contract_notifications
            if (current_time - n["timestamp"]) < n["lifetime"]
        ]
    
    def render(self, screen, dopamine_system):
        """Render all visual effects.
        
        Args:
            screen: Pygame surface to render on
            dopamine_system: DopamineSystem for accessing combo state
        """
        # Render particles
        for particle in self.particles:
            particle.render(screen)
        
        # Render floating texts
        for text in self.floating_texts:
            text.render(screen)
        
        # Render combo counter (top-right)
        if self.current_combo > 0:
            self._render_combo_counter(screen, dopamine_system)
        
        # Render risk contract notifications
        self._render_risk_notifications(screen)
    
    def _render_combo_counter(self, screen, dopamine_system):
        """Render combo counter in top-right corner."""
        x = self.screen_width - 150
        y = 80
        
        # Get color based on combo tier
        color = dopamine_system.get_combo_display_color(self.current_combo)
        
        # Scale based on pulse
        font_size = int(48 * self.combo_display_scale)
        scaled_font = pygame.font.Font(None, font_size)
        
        # Render combo count
        combo_text = f"{self.current_combo}x"
        combo_surface = scaled_font.render(combo_text, True, color)
        combo_rect = combo_surface.get_rect(center=(x, y))
        
        # Background
        bg_rect = combo_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=8)
        pygame.draw.rect(screen, color, bg_rect, 2, border_radius=8)
        
        screen.blit(combo_surface, combo_rect)
        
        # Multiplier text below
        if self.combo_multiplier > 1.0:
            mult_text = f"{self.combo_multiplier}x rewards"
            mult_surface = self.small_font.render(mult_text, True, (255, 255, 255))
            mult_rect = mult_surface.get_rect(center=(x, y + 30))
            screen.blit(mult_surface, mult_rect)
    
    def _render_risk_notifications(self, screen):
        """Render risk contract offer notifications."""
        y_offset = 200
        for notification in self.risk_contract_notifications:
            contract = notification["contract"]
            age = time.time() - notification["timestamp"]
            
            # Fade in/out
            if age < 0.5:
                alpha = int(255 * (age / 0.5))
            elif age > 4.5:
                alpha = int(255 * (1.0 - (age - 4.5) / 0.5))
            else:
                alpha = 255
            
            # Position top-left
            x = 20
            y = y_offset
            
            # Background with alpha blending
            width = 400
            height = 80
            bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            bg_surface.set_alpha(alpha)
            pygame.draw.rect(bg_surface, (50, 20, 20, 255), bg_surface.get_rect(), border_radius=8)
            pygame.draw.rect(bg_surface, (255, 100, 0, 255), bg_surface.get_rect(), 3, border_radius=8)
            screen.blit(bg_surface, (x, y))
            
            # Icon
            icon_text = self.combo_font.render(contract.icon, True, (255, 200, 0))
            screen.blit(icon_text, (x + 10, y + 10))
            
            # Title
            title = f"{contract.contract_type.upper()} AVAILABLE!"
            title_surface = self.message_font.render(title, True, (255, 200, 0))
            screen.blit(title_surface, (x + 70, y + 5))
            
            # Description
            desc_surface = self.small_font.render(contract.description, True, (200, 200, 200))
            screen.blit(desc_surface, (x + 70, y + 35))
            
            # Hint
            hint = "Click incident to accept!"
            hint_surface = self.small_font.render(hint, True, (150, 150, 150))
            screen.blit(hint_surface, (x + 70, y + 55))
            
            y_offset += 90
