"""Tests for ParticleSystem - Comprehensive coverage of particle effects."""

import pytest
import pygame
from unittest.mock import patch, MagicMock

from src.utils.particle_system import (
    ParticleSystem,
    Particle,
    ParticleEmitter,
    ParticlePreset,
    ParticleConfig,
    get_particle_system
)


class TestParticleSystemCore:
    """Test core particle system functionality."""
    
    @pytest.fixture
    def particle_system(self):
        """Create fresh particle system for each test."""
        # Reset singleton
        ParticleSystem._instance = None
        with patch('pygame.mixer.get_init', return_value=True):
            system = ParticleSystem()
            system.clear()
            return system
    
    def test_singleton_pattern(self):
        """Test that ParticleSystem enforces singleton."""
        ParticleSystem._instance = None
        with patch('pygame.mixer.get_init', return_value=True):
            system1 = ParticleSystem()
            system2 = ParticleSystem()
            system3 = get_particle_system()
            
            assert system1 is system2
            assert system2 is system3
    
    def test_initialization(self, particle_system):
        """Test particle system initializes correctly."""
        assert particle_system._pool_size == 1000
        assert len(particle_system._pool) == 1000
        assert particle_system._active_count == 0
        assert len(particle_system._emitters) == 0
        assert len(particle_system._presets) == 10  # 10 presets defined
    
    def test_particle_pool_reuse(self, particle_system):
        """Test that particles are reused from pool."""
        # Emit particles
        emitted1 = particle_system.emit(100, 100, 5, ParticlePreset.EXPLOSION.value)
        assert emitted1 == 5
        assert particle_system._active_count == 5
        
        # Update to expire particles
        for _ in range(200):  # Enough updates to expire particles
            particle_system.update(0.01)
        
        # All particles should be expired
        assert particle_system._active_count == 0
        
        # Emit again - should reuse same particles
        emitted2 = particle_system.emit(200, 200, 5, ParticlePreset.SPARKLE.value)
        assert emitted2 == 5
    
    def test_pool_growth_on_exhaustion(self, particle_system):
        """Test that pool grows when exhausted."""
        initial_size = particle_system._pool_size
        
        # Emit more than pool size (with long lifetime)
        particle_system.emit(100, 100, 1100, ParticlePreset.SPARKLE.value)
        
        # Pool should have grown
        assert particle_system._pool_size > initial_size
        assert particle_system._pool_size >= 1100
    
    def test_clear_all_particles(self, particle_system):
        """Test clearing all particles and emitters."""
        # Emit particles
        particle_system.emit(100, 100, 50, ParticlePreset.FIRE.value)
        assert particle_system._active_count > 0
        
        # Create emitter
        emitter = particle_system.create_emitter(200, 200, ParticlePreset.SMOKE.value)
        assert len(particle_system._emitters) == 1
        
        # Clear everything
        particle_system.clear()
        
        assert particle_system._active_count == 0
        assert len(particle_system._emitters) == 0
    
    def test_get_stats(self, particle_system):
        """Test particle system statistics."""
        particle_system.emit(100, 100, 10, ParticlePreset.EXPLOSION.value)
        particle_system.create_emitter(200, 200, ParticlePreset.FIRE.value)
        
        stats = particle_system.get_stats()
        
        assert stats["active_particles"] == 10
        assert stats["pool_size"] == 1000
        assert stats["emitter_count"] == 1


class TestParticleEmission:
    """Test particle emission methods."""
    
    @pytest.fixture
    def particle_system(self):
        """Create fresh particle system."""
        ParticleSystem._instance = None
        with patch('pygame.mixer.get_init', return_value=True):
            system = ParticleSystem()
            system.clear()
            return system
    
    def test_emit_basic(self, particle_system):
        """Test basic particle emission."""
        emitted = particle_system.emit(
            x=100,
            y=200,
            count=10,
            preset=ParticlePreset.EXPLOSION.value
        )
        
        assert emitted == 10
        assert particle_system._active_count == 10
    
    def test_emit_invalid_preset(self, particle_system):
        """Test emission with invalid preset returns 0."""
        emitted = particle_system.emit(
            x=100,
            y=200,
            count=10,
            preset="INVALID_PRESET"
        )
        
        assert emitted == 0
        assert particle_system._active_count == 0
    
    def test_emit_with_velocity_variance(self, particle_system):
        """Test emission with velocity variance."""
        emitted = particle_system.emit(
            x=100,
            y=200,
            count=20,
            preset=ParticlePreset.SPARKLE.value,
            velocity_variance=2.0
        )
        
        assert emitted == 20
        
        # Check that particles have varied velocities
        velocities = []
        for particle in particle_system._pool:
            if particle.active:
                velocities.append((particle.velocity_x, particle.velocity_y))
        
        # Should have variety (not all identical)
        unique_velocities = set(velocities)
        assert len(unique_velocities) > 1
    
    def test_explosion_effect(self, particle_system):
        """Test explosion effect creates radial burst."""
        emitted = particle_system.explosion(x=400, y=300, particle_count=30)
        
        assert emitted == 30
        assert particle_system._active_count == 30
    
    def test_trail_effect(self, particle_system):
        """Test trail effect creates concentrated particles."""
        emitted = particle_system.trail(x=150, y=150, particle_count=5)
        
        assert emitted == 5
        assert particle_system._active_count == 5


class TestParticlePresets:
    """Test all particle presets."""
    
    @pytest.fixture
    def particle_system(self):
        """Create fresh particle system."""
        ParticleSystem._instance = None
        with patch('pygame.mixer.get_init', return_value=True):
            system = ParticleSystem()
            system.clear()
            return system
    
    @pytest.mark.parametrize("preset", [
        ParticlePreset.EXPLOSION.value,
        ParticlePreset.FIRE.value,
        ParticlePreset.SMOKE.value,
        ParticlePreset.SPARKLE.value,
        ParticlePreset.MAGIC.value,
        ParticlePreset.ELECTRIC.value,
        ParticlePreset.BLOOD.value,
        ParticlePreset.WATER.value,
        ParticlePreset.TRAIL.value,
        ParticlePreset.DUST.value,
    ])
    def test_preset_emission(self, particle_system, preset):
        """Test that all presets emit particles correctly."""
        emitted = particle_system.emit(100, 100, 10, preset)
        
        assert emitted == 10
        assert particle_system._active_count == 10
    
    def test_fire_preset_rises_upward(self, particle_system):
        """Test fire particles have upward velocity and negative gravity."""
        particle_system.emit(100, 100, 1, ParticlePreset.FIRE.value)
        
        # Find active particle
        particle = None
        for p in particle_system._pool:
            if p.active:
                particle = p
                break
        
        assert particle is not None
        assert particle.velocity_y < 0  # Moving upward
        assert particle.gravity < 0  # Negative gravity (anti-gravity)
    
    def test_explosion_preset_has_varied_directions(self, particle_system):
        """Test explosion particles spread in all directions."""
        particle_system.emit(100, 100, 20, ParticlePreset.EXPLOSION.value)
        
        # Collect velocities
        velocities = []
        for particle in particle_system._pool:
            if particle.active:
                velocities.append((particle.velocity_x, particle.velocity_y))
        
        # Should have particles in different directions
        positive_x = sum(1 for vx, vy in velocities if vx > 0)
        negative_x = sum(1 for vx, vy in velocities if vx < 0)
        positive_y = sum(1 for vx, vy in velocities if vy > 0)
        negative_y = sum(1 for vx, vy in velocities if vy < 0)
        
        assert positive_x > 0
        assert negative_x > 0
        assert positive_y > 0
        assert negative_y > 0
    
    def test_sparkle_preset_has_no_gravity(self, particle_system):
        """Test sparkle particles have zero gravity."""
        particle_system.emit(100, 100, 5, ParticlePreset.SPARKLE.value)
        
        for particle in particle_system._pool:
            if particle.active:
                assert particle.gravity == 0.0
    
    def test_additive_blend_presets(self, particle_system):
        """Test that glow effects use additive blending."""
        glow_presets = [
            ParticlePreset.FIRE.value,
            ParticlePreset.SPARKLE.value,
            ParticlePreset.MAGIC.value,
            ParticlePreset.ELECTRIC.value,
        ]
        
        for preset in glow_presets:
            particle_system.clear()
            particle_system.emit(100, 100, 1, preset)
            
            # Find active particle
            particle = None
            for p in particle_system._pool:
                if p.active:
                    particle = p
                    break
            
            assert particle is not None
            assert particle.additive_blend is True, f"{preset} should use additive blend"


class TestParticleLifecycle:
    """Test particle lifecycle (spawn, update, expiry)."""
    
    @pytest.fixture
    def particle_system(self):
        """Create fresh particle system."""
        ParticleSystem._instance = None
        with patch('pygame.mixer.get_init', return_value=True):
            system = ParticleSystem()
            system.clear()
            return system
    
    def test_particle_update(self, particle_system):
        """Test particle updates position and age."""
        particle_system.emit(100, 100, 1, ParticlePreset.EXPLOSION.value)
        
        # Get active particle
        particle = None
        for p in particle_system._pool:
            if p.active:
                particle = p
                break
        
        initial_x = particle.x
        initial_y = particle.y
        initial_age = particle.age
        
        # Update
        particle_system.update(0.1)
        
        # Position and age should change
        assert particle.x != initial_x
        assert particle.y != initial_y
        assert particle.age > initial_age
    
    def test_particle_expiry(self, particle_system):
        """Test particles expire after lifetime."""
        particle_system.emit(100, 100, 5, ParticlePreset.SPARKLE.value)
        
        assert particle_system._active_count == 5
        
        # Update for long enough to expire all particles
        for _ in range(200):
            particle_system.update(0.01)
        
        assert particle_system._active_count == 0
    
    def test_particle_gravity_application(self, particle_system):
        """Test gravity affects particle velocity."""
        particle_system.emit(100, 100, 1, ParticlePreset.EXPLOSION.value)
        
        # Get active particle
        particle = None
        for p in particle_system._pool:
            if p.active:
                particle = p
                break
        
        initial_vy = particle.velocity_y
        
        # Update multiple times
        for _ in range(10):
            particle_system.update(0.1)
        
        # Velocity Y should increase (gravity accelerates downward)
        # Unless negative gravity (fire/smoke rise)
        if particle.gravity > 0:
            assert particle.velocity_y > initial_vy
    
    def test_particle_fade_out(self, particle_system):
        """Test particles fade out over lifetime."""
        particle_system.emit(100, 100, 1, ParticlePreset.EXPLOSION.value)
        
        # Get active particle
        particle = None
        for p in particle_system._pool:
            if p.active:
                particle = p
                break
        
        initial_alpha = particle.get_render_color()[3]
        
        # Age particle halfway
        particle.age = particle.lifetime * 0.5
        particle_system.update(0.01)
        
        mid_alpha = particle.get_render_color()[3]
        
        # Alpha should decrease
        assert mid_alpha < initial_alpha
    
    def test_particle_size_shrink(self, particle_system):
        """Test particles shrink over lifetime when fade_out enabled."""
        particle_system.emit(100, 100, 1, ParticlePreset.EXPLOSION.value)
        
        # Get active particle
        particle = None
        for p in particle_system._pool:
            if p.active:
                particle = p
                break
        
        initial_size = particle.size
        
        # Age particle halfway
        for _ in range(50):
            particle_system.update(0.01)
        
        # Size should decrease
        assert particle.size < initial_size


class TestParticleEmitters:
    """Test continuous particle emitters."""
    
    @pytest.fixture
    def particle_system(self):
        """Create fresh particle system."""
        ParticleSystem._instance = None
        with patch('pygame.mixer.get_init', return_value=True):
            system = ParticleSystem()
            system.clear()
            return system
    
    def test_create_emitter(self, particle_system):
        """Test creating particle emitter."""
        emitter = particle_system.create_emitter(
            x=100,
            y=100,
            preset=ParticlePreset.FIRE.value,
            emission_rate=10.0
        )
        
        assert emitter is not None
        assert len(particle_system._emitters) == 1
        assert emitter.x == 100
        assert emitter.y == 100
        assert emitter.emission_rate == 10.0
    
    def test_emitter_continuous_emission(self, particle_system):
        """Test emitter emits particles continuously."""
        emitter = particle_system.create_emitter(
            x=100,
            y=100,
            preset=ParticlePreset.SMOKE.value,
            emission_rate=20.0
        )
        
        # Update for 1 second
        for _ in range(100):
            particle_system.update(0.01)
        
        # Should have emitted approximately 20 particles
        # (some may have expired, so check for activity)
        assert particle_system._active_count > 0
    
    def test_emitter_with_duration(self, particle_system):
        """Test emitter expires after duration."""
        emitter = particle_system.create_emitter(
            x=100,
            y=100,
            preset=ParticlePreset.SPARKLE.value,
            emission_rate=10.0,
            duration=0.5
        )
        
        # Update for longer than duration
        for _ in range(100):
            particle_system.update(0.01)
        
        # Emitter should be inactive and removed
        assert not emitter.active
        assert len(particle_system._emitters) == 0
    
    def test_remove_emitter(self, particle_system):
        """Test manually removing emitter."""
        emitter = particle_system.create_emitter(
            x=100,
            y=100,
            preset=ParticlePreset.FIRE.value
        )
        
        assert len(particle_system._emitters) == 1
        
        particle_system.remove_emitter(emitter)
        
        assert len(particle_system._emitters) == 0
    
    def test_multiple_emitters(self, particle_system):
        """Test multiple emitters running simultaneously."""
        emitter1 = particle_system.create_emitter(100, 100, ParticlePreset.FIRE.value, emission_rate=5.0)
        emitter2 = particle_system.create_emitter(200, 200, ParticlePreset.SMOKE.value, emission_rate=5.0)
        emitter3 = particle_system.create_emitter(300, 300, ParticlePreset.SPARKLE.value, emission_rate=5.0)
        
        assert len(particle_system._emitters) == 3
        
        # Update for a second
        for _ in range(100):
            particle_system.update(0.01)
        
        # All emitters should have emitted particles
        assert particle_system._active_count > 0


class TestParticleRendering:
    """Test particle rendering."""
    
    @pytest.fixture
    def particle_system(self):
        """Create fresh particle system."""
        ParticleSystem._instance = None
        with patch('pygame.mixer.get_init', return_value=True):
            system = ParticleSystem()
            system.clear()
            return system
    
    @pytest.fixture
    def mock_screen(self):
        """Create mock pygame surface."""
        screen = MagicMock(spec=pygame.Surface)
        return screen
    
    def test_render_no_particles(self, particle_system, mock_screen):
        """Test rendering with no active particles."""
        particle_system.render(mock_screen)
        # Should not crash
    
    def test_render_normal_particles(self, particle_system, mock_screen):
        """Test rendering particles with normal alpha blending."""
        particle_system.emit(100, 100, 5, ParticlePreset.SMOKE.value)
        
        with patch('pygame.draw.circle') as mock_draw, \
             patch('pygame.Surface') as mock_surface:
            
            particle_system.render(mock_screen)
            
            # Should create surfaces for alpha blending
            assert mock_surface.called
    
    def test_render_additive_particles(self, particle_system, mock_screen):
        """Test rendering particles with additive blending."""
        particle_system.emit(100, 100, 5, ParticlePreset.FIRE.value)
        
        with patch('pygame.draw.circle') as mock_draw, \
             patch('pygame.Surface') as mock_surface:
            
            particle_system.render(mock_screen)
            
            # Should use additive blend mode
            # Check that blit was called with special_flags
            assert mock_screen.blit.called


class TestParticleEnums:
    """Test particle system enums and data structures."""
    
    def test_particle_preset_enum_values(self):
        """Test ParticlePreset enum has all expected values."""
        expected_presets = [
            "explosion", "fire", "smoke", "sparkle", "magic",
            "electric", "blood", "water", "trail", "dust"
        ]
        
        for preset in expected_presets:
            assert any(p.value == preset for p in ParticlePreset)
    
    def test_particle_config_dataclass(self):
        """Test ParticleConfig dataclass."""
        config = ParticleConfig(
            color=(255, 128, 0, 255),
            size=5,
            lifetime=1.5,
            velocity_x=100.0,
            velocity_y=-50.0,
            gravity=200.0,
            fade_out=True,
            additive_blend=False
        )
        
        assert config.color == (255, 128, 0, 255)
        assert config.size == 5
        assert config.lifetime == 1.5
        assert config.velocity_x == 100.0
        assert config.velocity_y == -50.0
        assert config.gravity == 200.0
        assert config.fade_out is True
        assert config.additive_blend is False


class TestParticleClass:
    """Test individual Particle class."""
    
    def test_particle_initialization(self):
        """Test particle initializes inactive."""
        particle = Particle()
        
        assert particle.active is False
        assert particle.x == 0.0
        assert particle.y == 0.0
    
    def test_particle_reset(self):
        """Test particle reset activates and configures particle."""
        particle = Particle()
        
        particle.reset(
            x=100.0,
            y=200.0,
            velocity_x=50.0,
            velocity_y=-30.0,
            size=5,
            color=(255, 0, 0, 255),
            lifetime=2.0,
            gravity=100.0,
            fade_out=True,
            additive_blend=False
        )
        
        assert particle.active is True
        assert particle.x == 100.0
        assert particle.y == 200.0
        assert particle.velocity_x == 50.0
        assert particle.velocity_y == -30.0
        assert particle.size == 5
        assert particle.color == (255, 0, 0, 255)
        assert particle.lifetime == 2.0
        assert particle.gravity == 100.0
        assert particle.fade_out is True
        assert particle.additive_blend is False
    
    def test_particle_update_returns_alive_status(self):
        """Test particle update returns True while alive, False when expired."""
        particle = Particle()
        particle.reset(100, 100, 0, 0, 5, (255, 255, 255, 255), lifetime=0.1)
        
        # Should be alive initially
        assert particle.update(0.05) is True
        
        # Should expire after lifetime
        assert particle.update(0.1) is False
        assert particle.active is False
    
    def test_particle_color_fade(self):
        """Test particle color fades over lifetime."""
        particle = Particle()
        particle.reset(100, 100, 0, 0, 5, (255, 0, 0, 255), lifetime=1.0, fade_out=True)
        
        initial_color = particle.get_render_color()
        
        # Age halfway
        particle.age = 0.5
        mid_color = particle.get_render_color()
        
        # Age to almost end
        particle.age = 0.9
        end_color = particle.get_render_color()
        
        # Alpha should decrease
        assert initial_color[3] > mid_color[3] > end_color[3]


class TestParticleEmitterClass:
    """Test ParticleEmitter class."""
    
    def test_emitter_initialization(self):
        """Test emitter initializes correctly."""
        emitter = ParticleEmitter(
            x=100.0,
            y=200.0,
            emission_rate=15.0,
            preset="fire",
            duration=5.0
        )
        
        assert emitter.x == 100.0
        assert emitter.y == 200.0
        assert emitter.emission_rate == 15.0
        assert emitter.preset == "fire"
        assert emitter.duration == 5.0
        assert emitter.active is True
        assert emitter.age == 0.0
    
    def test_emitter_update_ages(self):
        """Test emitter ages over time."""
        emitter = ParticleEmitter(100, 100, 10.0, "smoke")
        
        emitter.update(0.5)
        assert emitter.age == 0.5
        
        emitter.update(0.3)
        assert emitter.age == 0.8
    
    def test_emitter_expires_after_duration(self):
        """Test emitter expires after duration."""
        emitter = ParticleEmitter(100, 100, 10.0, "fire", duration=1.0)
        
        assert emitter.update(0.5) is True
        assert emitter.update(0.6) is False
        assert emitter.active is False
    
    def test_emitter_infinite_duration(self):
        """Test emitter with no duration runs forever."""
        emitter = ParticleEmitter(100, 100, 10.0, "smoke", duration=None)
        
        for _ in range(100):
            assert emitter.update(0.1) is True
        
        assert emitter.active is True
    
    def test_emitter_get_emission_count(self):
        """Test emitter calculates correct emission count."""
        emitter = ParticleEmitter(100, 100, emission_rate=10.0, preset="sparkle")
        
        # At 10 particles/second, 0.1s should emit 1 particle
        count = emitter.get_emission_count(0.1)
        assert count == 1
        
        # Accumulator should handle fractional particles
        count1 = emitter.get_emission_count(0.05)  # 0.5 particles
        count2 = emitter.get_emission_count(0.05)  # 0.5 particles (total 1.0)
        
        assert count1 + count2 == 1  # Should emit 1 total
