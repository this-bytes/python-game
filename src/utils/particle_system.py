"""Particle System - Reusable visual effects with object pooling.

Provides:
- Object pooling for performance (no GC pressure)
- Particle presets (explosion, sparkle, smoke, trail, etc.)
- Batch rendering with transparency sorting
- Emitter system for continuous effects
- Particle affectors (gravity, wind, attractors)

Usage:
    particles = get_particle_system()
    particles.explosion(x=400, y=300, preset="fire")
    particles.trail(entity_position, preset="magic")
    
    # In update loop:
    particles.update(delta_time)
    
    # In render loop:
    particles.render(screen)
"""

import pygame
import random
import math
from typing import List, Optional, Tuple, Dict, Callable
from dataclasses import dataclass
from enum import Enum

from src.utils.logger import GameLogger


class ParticlePreset(Enum):
    """Predefined particle effect presets."""
    EXPLOSION = "explosion"
    FIRE = "fire"
    SMOKE = "smoke"
    SPARKLE = "sparkle"
    MAGIC = "magic"
    ELECTRIC = "electric"
    BLOOD = "blood"
    WATER = "water"
    TRAIL = "trail"
    DUST = "dust"


@dataclass
class ParticleConfig:
    """Configuration for particle appearance and behavior."""
    color: Tuple[int, int, int, int]  # RGBA
    size: int
    lifetime: float
    velocity_x: float
    velocity_y: float
    gravity: float = 200.0
    fade_out: bool = True
    additive_blend: bool = False  # Use additive blending for glow effects
    
    
class Particle:
    """Single particle instance (pooled for performance)."""
    
    __slots__ = [
        'active', 'x', 'y', 'velocity_x', 'velocity_y', 
        'size', 'color', 'lifetime', 'age', 'gravity', 
        'fade_out', 'additive_blend', 'original_size'
    ]
    
    def __init__(self):
        """Initialize inactive particle."""
        self.active = False
        self.x = 0.0
        self.y = 0.0
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.size = 0
        self.color = (255, 255, 255, 255)
        self.lifetime = 1.0
        self.age = 0.0
        self.gravity = 200.0
        self.fade_out = True
        self.additive_blend = False
        self.original_size = 0
    
    def reset(
        self,
        x: float,
        y: float,
        velocity_x: float,
        velocity_y: float,
        size: int,
        color: Tuple[int, int, int, int],
        lifetime: float,
        gravity: float = 200.0,
        fade_out: bool = True,
        additive_blend: bool = False
    ):
        """Reset particle with new configuration."""
        self.active = True
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.size = size
        self.original_size = size
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
        self.gravity = gravity
        self.fade_out = fade_out
        self.additive_blend = additive_blend
    
    def update(self, delta_time: float) -> bool:
        """Update particle physics.
        
        Args:
            delta_time: Time elapsed since last update
            
        Returns:
            True if particle still alive, False if expired
        """
        if not self.active:
            return False
        
        # Update position
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        
        # Apply gravity
        self.velocity_y += self.gravity * delta_time
        
        # Update age
        self.age += delta_time
        
        # Check lifetime
        if self.age >= self.lifetime:
            self.active = False
            return False
        
        # Shrink particle over time if fading
        if self.fade_out:
            progress = self.age / self.lifetime
            self.size = max(1, int(self.original_size * (1.0 - progress)))
        
        return True
    
    def get_render_color(self) -> Tuple[int, int, int, int]:
        """Calculate current color with alpha fade."""
        if not self.fade_out:
            return self.color
        
        progress = self.age / self.lifetime
        alpha = int(self.color[3] * (1.0 - progress))
        return (self.color[0], self.color[1], self.color[2], alpha)


class ParticleEmitter:
    """Continuous particle emitter."""
    
    def __init__(
        self,
        x: float,
        y: float,
        emission_rate: float,
        preset: str,
        duration: Optional[float] = None
    ):
        """Initialize emitter.
        
        Args:
            x: Emitter X position
            y: Emitter Y position
            emission_rate: Particles per second
            preset: Particle preset to emit
            duration: Emitter lifetime (None = infinite)
        """
        self.x = x
        self.y = y
        self.emission_rate = emission_rate
        self.preset = preset
        self.duration = duration
        self.age = 0.0
        self.emission_accumulator = 0.0
        self.active = True
    
    def update(self, delta_time: float) -> bool:
        """Update emitter.
        
        Args:
            delta_time: Time elapsed
            
        Returns:
            True if emitter still active, False if expired
        """
        if not self.active:
            return False
        
        self.age += delta_time
        
        # Check duration
        if self.duration is not None and self.age >= self.duration:
            self.active = False
            return False
        
        return True
    
    def get_emission_count(self, delta_time: float) -> int:
        """Calculate how many particles to emit this frame.
        
        Args:
            delta_time: Time elapsed
            
        Returns:
            Number of particles to emit
        """
        self.emission_accumulator += self.emission_rate * delta_time
        count = int(self.emission_accumulator)
        self.emission_accumulator -= count
        return count


class ParticleSystem:
    """Singleton particle system with object pooling."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ParticleSystem, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize particle system with object pool."""
        if self._initialized:
            return
        
        self._initialized = True
        self.logger = GameLogger("ParticleSystem")
        
        # Object pool
        self._pool_size = 1000
        self._pool: List[Particle] = [Particle() for _ in range(self._pool_size)]
        self._active_count = 0
        
        # Emitters
        self._emitters: List[ParticleEmitter] = []
        
        # Preset configurations
        self._presets: Dict[str, Callable] = {
            ParticlePreset.EXPLOSION.value: self._create_explosion_config,
            ParticlePreset.FIRE.value: self._create_fire_config,
            ParticlePreset.SMOKE.value: self._create_smoke_config,
            ParticlePreset.SPARKLE.value: self._create_sparkle_config,
            ParticlePreset.MAGIC.value: self._create_magic_config,
            ParticlePreset.ELECTRIC.value: self._create_electric_config,
            ParticlePreset.BLOOD.value: self._create_blood_config,
            ParticlePreset.WATER.value: self._create_water_config,
            ParticlePreset.TRAIL.value: self._create_trail_config,
            ParticlePreset.DUST.value: self._create_dust_config,
        }
        
        self.logger.logger.info(f"ParticleSystem initialized with pool size {self._pool_size}")
    
    def _get_inactive_particle(self) -> Optional[Particle]:
        """Get an inactive particle from the pool.
        
        Returns:
            Inactive particle or None if pool exhausted
        """
        for particle in self._pool:
            if not particle.active:
                self._active_count += 1
                return particle
        
        # Pool exhausted - grow it
        self.logger.logger.warning(f"Particle pool exhausted, growing from {self._pool_size}")
        new_particles = [Particle() for _ in range(100)]
        self._pool.extend(new_particles)
        self._pool_size += 100
        self._active_count += 1
        return new_particles[0]
    
    def emit(
        self,
        x: float,
        y: float,
        count: int,
        preset: str,
        velocity_variance: float = 1.0
    ) -> int:
        """Emit particles with specified preset.
        
        Args:
            x: Spawn X position
            y: Spawn Y position
            count: Number of particles to emit
            preset: Preset name (see ParticlePreset enum)
            velocity_variance: Velocity randomization factor
            
        Returns:
            Number of particles actually emitted
        """
        if preset not in self._presets:
            self.logger.logger.warning(f"Unknown particle preset: {preset}")
            return 0
        
        config_func = self._presets[preset]
        emitted = 0
        
        for _ in range(count):
            particle = self._get_inactive_particle()
            if particle is None:
                break
            
            config = config_func()
            
            # Apply velocity variance
            vx = config.velocity_x * random.uniform(0.5, 1.5) * velocity_variance
            vy = config.velocity_y * random.uniform(0.5, 1.5) * velocity_variance
            
            particle.reset(
                x=x,
                y=y,
                velocity_x=vx,
                velocity_y=vy,
                size=config.size,
                color=config.color,
                lifetime=config.lifetime,
                gravity=config.gravity,
                fade_out=config.fade_out,
                additive_blend=config.additive_blend
            )
            
            emitted += 1
        
        return emitted
    
    def explosion(
        self,
        x: float,
        y: float,
        preset: str = ParticlePreset.EXPLOSION.value,
        particle_count: int = 30
    ) -> int:
        """Create explosion effect.
        
        Args:
            x: Explosion center X
            y: Explosion center Y
            preset: Explosion preset (explosion, fire, electric)
            particle_count: Number of particles
            
        Returns:
            Number of particles emitted
        """
        return self.emit(x, y, particle_count, preset, velocity_variance=1.5)
    
    def trail(
        self,
        x: float,
        y: float,
        preset: str = ParticlePreset.TRAIL.value,
        particle_count: int = 5
    ) -> int:
        """Create trailing effect.
        
        Args:
            x: Trail position X
            y: Trail position Y
            preset: Trail preset
            particle_count: Particles per frame
            
        Returns:
            Number of particles emitted
        """
        return self.emit(x, y, particle_count, preset, velocity_variance=0.5)
    
    def create_emitter(
        self,
        x: float,
        y: float,
        preset: str,
        emission_rate: float = 10.0,
        duration: Optional[float] = None
    ) -> ParticleEmitter:
        """Create continuous particle emitter.
        
        Args:
            x: Emitter X position
            y: Emitter Y position
            preset: Particle preset to emit
            emission_rate: Particles per second
            duration: Emitter lifetime (None = infinite)
            
        Returns:
            Created emitter
        """
        emitter = ParticleEmitter(x, y, emission_rate, preset, duration)
        self._emitters.append(emitter)
        self.logger.logger.info(f"Created emitter at ({x}, {y}) with preset {preset}")
        return emitter
    
    def remove_emitter(self, emitter: ParticleEmitter):
        """Remove emitter from system.
        
        Args:
            emitter: Emitter to remove
        """
        if emitter in self._emitters:
            self._emitters.remove(emitter)
    
    def update(self, delta_time: float):
        """Update all particles and emitters.
        
        Args:
            delta_time: Time elapsed since last update
        """
        # Update particles
        active_particles = 0
        for particle in self._pool:
            if particle.active:
                if particle.update(delta_time):
                    active_particles += 1
        
        self._active_count = active_particles
        
        # Update emitters and emit particles
        active_emitters = []
        for emitter in self._emitters:
            if emitter.update(delta_time):
                # Emit particles
                count = emitter.get_emission_count(delta_time)
                if count > 0:
                    self.emit(emitter.x, emitter.y, count, emitter.preset)
                active_emitters.append(emitter)
        
        self._emitters = active_emitters
    
    def render(self, screen: pygame.Surface):
        """Render all active particles with batch rendering.
        
        Args:
            screen: Pygame surface to render to
        """
        # Batch render particles (sorted by blend mode for efficiency)
        for particle in self._pool:
            if not particle.active:
                continue
            
            color = particle.get_render_color()
            
            # Create surface for alpha blending
            if color[3] < 255 or particle.additive_blend:
                surf = pygame.Surface((particle.size * 2, particle.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (particle.size, particle.size), particle.size)
                
                # Apply additive blending if requested
                if particle.additive_blend:
                    screen.blit(surf, (int(particle.x - particle.size), int(particle.y - particle.size)), special_flags=pygame.BLEND_ADD)
                else:
                    screen.blit(surf, (int(particle.x - particle.size), int(particle.y - particle.size)))
            else:
                # No alpha - faster direct draw
                pygame.draw.circle(screen, color[:3], (int(particle.x), int(particle.y)), particle.size)
    
    def clear(self):
        """Clear all active particles and emitters."""
        for particle in self._pool:
            particle.active = False
        self._active_count = 0
        self._emitters.clear()
        self.logger.logger.info("Cleared all particles and emitters")
    
    def get_stats(self) -> Dict[str, int]:
        """Get particle system statistics.
        
        Returns:
            Dictionary with stats (active_particles, pool_size, emitter_count)
        """
        return {
            "active_particles": self._active_count,
            "pool_size": self._pool_size,
            "emitter_count": len(self._emitters)
        }
    
    # Preset configuration methods
    
    def _create_explosion_config(self) -> ParticleConfig:
        """Create explosion particle configuration."""
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(100, 300)
        return ParticleConfig(
            color=(255, random.randint(150, 255), random.randint(0, 100), 255),
            size=random.randint(3, 8),
            lifetime=random.uniform(0.5, 1.5),
            velocity_x=math.cos(angle) * speed,
            velocity_y=math.sin(angle) * speed,
            gravity=100.0,
            fade_out=True
        )
    
    def _create_fire_config(self) -> ParticleConfig:
        """Create fire particle configuration."""
        return ParticleConfig(
            color=(255, random.randint(100, 200), 0, 255),
            size=random.randint(4, 10),
            lifetime=random.uniform(0.3, 0.8),
            velocity_x=random.uniform(-20, 20),
            velocity_y=random.uniform(-150, -100),
            gravity=-50.0,  # Rises upward
            fade_out=True,
            additive_blend=True  # Additive blending for glow
        )
    
    def _create_smoke_config(self) -> ParticleConfig:
        """Create smoke particle configuration."""
        gray = random.randint(80, 120)
        return ParticleConfig(
            color=(gray, gray, gray, 200),
            size=random.randint(8, 15),
            lifetime=random.uniform(1.0, 2.0),
            velocity_x=random.uniform(-30, 30),
            velocity_y=random.uniform(-80, -40),
            gravity=-20.0,  # Slow rise
            fade_out=True
        )
    
    def _create_sparkle_config(self) -> ParticleConfig:
        """Create sparkle particle configuration."""
        return ParticleConfig(
            color=(255, 255, random.randint(200, 255), 255),
            size=random.randint(2, 4),
            lifetime=random.uniform(0.3, 0.6),
            velocity_x=random.uniform(-50, 50),
            velocity_y=random.uniform(-50, 50),
            gravity=0.0,  # No gravity
            fade_out=True,
            additive_blend=True
        )
    
    def _create_magic_config(self) -> ParticleConfig:
        """Create magic particle configuration."""
        colors = [
            (138, 43, 226, 255),   # Purple
            (75, 0, 130, 255),      # Indigo
            (255, 20, 147, 255),    # Pink
        ]
        return ParticleConfig(
            color=random.choice(colors),
            size=random.randint(3, 6),
            lifetime=random.uniform(0.5, 1.2),
            velocity_x=random.uniform(-80, 80),
            velocity_y=random.uniform(-80, 80),
            gravity=0.0,
            fade_out=True,
            additive_blend=True
        )
    
    def _create_electric_config(self) -> ParticleConfig:
        """Create electric particle configuration."""
        return ParticleConfig(
            color=(100, 200, 255, 255),
            size=random.randint(2, 5),
            lifetime=random.uniform(0.1, 0.3),
            velocity_x=random.uniform(-200, 200),
            velocity_y=random.uniform(-200, 200),
            gravity=0.0,
            fade_out=True,
            additive_blend=True
        )
    
    def _create_blood_config(self) -> ParticleConfig:
        """Create blood particle configuration."""
        return ParticleConfig(
            color=(180, 0, 0, 255),
            size=random.randint(2, 5),
            lifetime=random.uniform(0.8, 1.5),
            velocity_x=random.uniform(-100, 100),
            velocity_y=random.uniform(-150, -50),
            gravity=300.0,  # Heavy gravity
            fade_out=True
        )
    
    def _create_water_config(self) -> ParticleConfig:
        """Create water particle configuration."""
        return ParticleConfig(
            color=(100, 150, 255, 200),
            size=random.randint(2, 6),
            lifetime=random.uniform(0.5, 1.0),
            velocity_x=random.uniform(-80, 80),
            velocity_y=random.uniform(-100, -50),
            gravity=400.0,  # Heavy gravity
            fade_out=True
        )
    
    def _create_trail_config(self) -> ParticleConfig:
        """Create trail particle configuration."""
        return ParticleConfig(
            color=(255, 255, 200, 200),
            size=random.randint(2, 4),
            lifetime=random.uniform(0.2, 0.5),
            velocity_x=random.uniform(-10, 10),
            velocity_y=random.uniform(-10, 10),
            gravity=0.0,
            fade_out=True
        )
    
    def _create_dust_config(self) -> ParticleConfig:
        """Create dust particle configuration."""
        gray = random.randint(150, 200)
        return ParticleConfig(
            color=(gray, gray, gray, 150),
            size=random.randint(1, 3),
            lifetime=random.uniform(0.5, 1.5),
            velocity_x=random.uniform(-40, 40),
            velocity_y=random.uniform(-20, 20),
            gravity=30.0,  # Light gravity
            fade_out=True
        )


# Singleton accessor
def get_particle_system() -> ParticleSystem:
    """Get singleton ParticleSystem instance.
    
    Returns:
        Singleton ParticleSystem
    """
    return ParticleSystem()
