"""Tests for AudioManager - Centralized sound system."""

import pytest
import pygame
import os
from unittest.mock import Mock, patch, MagicMock
from src.utils.audio_manager import (
    AudioManager,
    SoundCategory,
    SoundConfig,
    get_audio_manager
)


class TestAudioManager:
    """Test suite for AudioManager."""

    @pytest.fixture
    def audio_manager(self):
        """Create AudioManager instance for testing."""
        # Reset singleton
        AudioManager._instance = None
        AudioManager._initialized = False
        
        with patch('pygame.mixer.get_init', return_value=True), \
             patch('pygame.mixer.set_num_channels'):
            manager = AudioManager()
        
        return manager

    def test_singleton_pattern(self, audio_manager):
        """Verify AudioManager follows singleton pattern."""
        manager1 = get_audio_manager()
        manager2 = get_audio_manager()
        
        assert manager1 is manager2, "Should return same instance"

    def test_initialization(self, audio_manager):
        """Test AudioManager initializes correctly."""
        assert audio_manager.is_enabled() is True
        assert audio_manager.get_master_volume() == 1.0
        assert audio_manager.get_category_volume(SoundCategory.UI) == 0.7
        assert audio_manager.get_category_volume(SoundCategory.GAME) == 0.8
        assert audio_manager.get_category_volume(SoundCategory.AMBIENT) == 0.5
        assert audio_manager.get_category_volume(SoundCategory.MUSIC) == 0.6

    def test_master_volume_control(self, audio_manager):
        """Test master volume setter and getter."""
        audio_manager.set_master_volume(0.5)
        assert audio_manager.get_master_volume() == 0.5
        
        # Test clamping
        audio_manager.set_master_volume(1.5)
        assert audio_manager.get_master_volume() == 1.0
        
        audio_manager.set_master_volume(-0.5)
        assert audio_manager.get_master_volume() == 0.0

    def test_category_volume_control(self, audio_manager):
        """Test category-specific volume control."""
        audio_manager.set_category_volume(SoundCategory.UI, 0.3)
        assert audio_manager.get_category_volume(SoundCategory.UI) == 0.3
        
        audio_manager.set_category_volume(SoundCategory.GAME, 1.0)
        assert audio_manager.get_category_volume(SoundCategory.GAME) == 1.0

    def test_load_sound_success(self, audio_manager):
        """Test loading sound successfully."""
        with patch('os.path.exists', return_value=True), \
             patch('pygame.mixer.Sound') as mock_sound:
            
            result = audio_manager.load_sound(
                "test_sound",
                "sounds/test.wav",
                SoundCategory.GAME,
                0.8
            )
            
            assert result is True
            assert "test_sound" in audio_manager._sounds

    def test_load_sound_file_not_found(self, audio_manager):
        """Test loading sound when file doesn't exist."""
        with patch('os.path.exists', return_value=False):
            result = audio_manager.load_sound(
                "missing_sound",
                "sounds/missing.wav"
            )
            
            assert result is False
            assert "missing_sound" not in audio_manager._sounds

    def test_load_sound_already_loaded(self, audio_manager):
        """Test loading sound that's already loaded."""
        with patch('os.path.exists', return_value=True), \
             patch('pygame.mixer.Sound'):
            
            audio_manager.load_sound("test_sound", "sounds/test.wav")
            result = audio_manager.load_sound("test_sound", "sounds/test.wav")
            
            assert result is True

    def test_play_sound(self, audio_manager):
        """Test playing loaded sound."""
        mock_sound = Mock()
        mock_channel = Mock()
        mock_sound.play.return_value = mock_channel
        
        with patch('os.path.exists', return_value=True), \
             patch('pygame.mixer.Sound', return_value=mock_sound):
            
            audio_manager.load_sound("test_sound", "sounds/test.wav")
            channel = audio_manager.play_sound("test_sound")
            
            assert channel is mock_channel
            mock_sound.set_volume.assert_called_once()
            mock_sound.play.assert_called_once()

    def test_play_sound_not_loaded(self, audio_manager):
        """Test playing sound that hasn't been loaded."""
        result = audio_manager.play_sound("nonexistent_sound")
        assert result is None

    def test_play_sound_with_volume_multiplier(self, audio_manager):
        """Test playing sound with volume multiplier."""
        mock_sound = Mock()
        
        with patch('os.path.exists', return_value=True), \
             patch('pygame.mixer.Sound', return_value=mock_sound):
            
            audio_manager.load_sound("test_sound", "sounds/test.wav", volume=0.8)
            audio_manager.set_master_volume(0.9)
            audio_manager.set_category_volume(SoundCategory.GAME, 0.7)
            
            audio_manager.play_sound("test_sound", volume_multiplier=0.5)
            
            # Calculate expected volume: master * category * base * multiplier
            # 0.9 * 0.7 * 0.8 * 0.5 = 0.252
            called_volume = mock_sound.set_volume.call_args[0][0]
            assert abs(called_volume - 0.252) < 0.001

    def test_play_sound_3d(self, audio_manager):
        """Test spatial audio with distance-based volume."""
        mock_sound = Mock()
        
        with patch('os.path.exists', return_value=True), \
             patch('pygame.mixer.Sound', return_value=mock_sound):
            
            audio_manager.load_sound("test_sound", "sounds/test.wav")
            
            # Test at half max distance
            channel = audio_manager.play_sound_3d(
                "test_sound",
                position=(500, 0),
                listener_position=(0, 0),
                max_distance=1000.0
            )
            
            assert channel is not None
            
            # Test beyond max distance (should not play)
            channel = audio_manager.play_sound_3d(
                "test_sound",
                position=(1500, 0),
                listener_position=(0, 0),
                max_distance=1000.0
            )
            
            assert channel is None

    def test_stop_sound(self, audio_manager):
        """Test stopping a sound."""
        mock_sound = Mock()
        
        with patch('os.path.exists', return_value=True), \
             patch('pygame.mixer.Sound', return_value=mock_sound):
            
            audio_manager.load_sound("test_sound", "sounds/test.wav")
            audio_manager.stop_sound("test_sound")
            
            mock_sound.stop.assert_called_once()

    def test_play_music_success(self, audio_manager):
        """Test playing background music."""
        with patch('os.path.exists', return_value=True), \
             patch('pygame.mixer.music.load') as mock_load, \
             patch('pygame.mixer.music.play') as mock_play, \
             patch('pygame.mixer.music.set_volume') as mock_volume, \
             patch('pygame.mixer.music.get_busy', return_value=False):
            
            result = audio_manager.play_music("music/theme.ogg", loop=True, volume=0.8)
            
            assert result is True
            mock_load.assert_called_once_with("music/theme.ogg")
            mock_play.assert_called_once()
            mock_volume.assert_called_once()

    def test_play_music_with_fade_in(self, audio_manager):
        """Test playing music with fade in."""
        with patch('os.path.exists', return_value=True), \
             patch('pygame.mixer.music.load'), \
             patch('pygame.mixer.music.play') as mock_play, \
             patch('pygame.mixer.music.set_volume'), \
             patch('pygame.mixer.music.get_busy', return_value=False):
            
            audio_manager.play_music("music/theme.ogg", fade_in=2.0)
            
            # Check fade_ms parameter
            call_args = mock_play.call_args
            assert 'fade_ms' in call_args[1]
            assert call_args[1]['fade_ms'] == 2000

    def test_stop_music(self, audio_manager):
        """Test stopping background music."""
        with patch('pygame.mixer.music.stop') as mock_stop:
            audio_manager.stop_music()
            mock_stop.assert_called_once()

    def test_stop_music_with_fade_out(self, audio_manager):
        """Test stopping music with fade out."""
        with patch('pygame.mixer.music.fadeout') as mock_fadeout:
            audio_manager.stop_music(fade_out=1.5)
            mock_fadeout.assert_called_once_with(1500)

    def test_pause_unpause_music(self, audio_manager):
        """Test pausing and unpausing music."""
        with patch('pygame.mixer.music.pause') as mock_pause, \
             patch('pygame.mixer.music.unpause') as mock_unpause, \
             patch('pygame.mixer.music.get_busy', return_value=True):
            
            audio_manager.pause_music()
            mock_pause.assert_called_once()
            
            audio_manager.unpause_music()
            mock_unpause.assert_called_once()

    def test_is_music_playing(self, audio_manager):
        """Test checking if music is playing."""
        with patch('pygame.mixer.music.get_busy', return_value=True):
            assert audio_manager.is_music_playing() is True
        
        with patch('pygame.mixer.music.get_busy', return_value=False):
            assert audio_manager.is_music_playing() is False

    def test_get_current_music(self, audio_manager):
        """Test getting current music path."""
        with patch('os.path.exists', return_value=True), \
             patch('pygame.mixer.music.load'), \
             patch('pygame.mixer.music.play'), \
             patch('pygame.mixer.music.set_volume'), \
             patch('pygame.mixer.music.stop'), \
             patch('pygame.mixer.music.get_busy', return_value=False):
            
            audio_manager.play_music("music/theme.ogg")
            assert audio_manager.get_current_music() == "music/theme.ogg"
            
            audio_manager.stop_music()
            assert audio_manager.get_current_music() is None

    def test_preload_sounds(self, audio_manager):
        """Test preloading multiple sounds from config."""
        sound_configs = [
            {"id": "sound1", "path": "sounds/sound1.wav", "category": "ui", "volume": 0.8},
            {"id": "sound2", "path": "sounds/sound2.wav", "category": "game"},
            {"id": "sound3", "path": "sounds/sound3.wav"},  # Missing category, should use default
        ]
        
        with patch('os.path.exists', return_value=True), \
             patch('pygame.mixer.Sound'):
            
            loaded_count = audio_manager.preload_sounds(sound_configs)
            
            assert loaded_count == 3
            assert "sound1" in audio_manager._sounds
            assert "sound2" in audio_manager._sounds
            assert "sound3" in audio_manager._sounds

    def test_preload_sounds_partial_failure(self, audio_manager):
        """Test preloading sounds with some failures."""
        sound_configs = [
            {"id": "sound1", "path": "sounds/sound1.wav"},
            {"id": "sound2", "path": "sounds/sound2.wav"},
            {"id": "sound3"},  # Missing path
        ]
        
        with patch('os.path.exists', return_value=True), \
             patch('pygame.mixer.Sound'):
            
            loaded_count = audio_manager.preload_sounds(sound_configs)
            
            assert loaded_count == 2

    def test_unload_sound(self, audio_manager):
        """Test unloading a sound from memory."""
        with patch('os.path.exists', return_value=True), \
             patch('pygame.mixer.Sound'):
            
            audio_manager.load_sound("test_sound", "sounds/test.wav")
            assert "test_sound" in audio_manager._sounds
            
            audio_manager.unload_sound("test_sound")
            assert "test_sound" not in audio_manager._sounds

    def test_unload_all_sounds(self, audio_manager):
        """Test unloading all sounds from memory."""
        with patch('os.path.exists', return_value=True), \
             patch('pygame.mixer.Sound'):
            
            audio_manager.load_sound("sound1", "sounds/sound1.wav")
            audio_manager.load_sound("sound2", "sounds/sound2.wav")
            
            audio_manager.unload_all_sounds()
            assert len(audio_manager._sounds) == 0

    def test_audio_disabled_gracefully(self):
        """Test AudioManager handles disabled audio gracefully."""
        # Reset singleton
        AudioManager._instance = None
        AudioManager._initialized = False
        
        with patch('pygame.mixer.get_init', return_value=False), \
             patch('pygame.mixer.init', side_effect=pygame.error("Audio init failed")):
            
            manager = AudioManager()
            
            assert manager.is_enabled() is False
            
            # All operations should fail gracefully
            assert manager.load_sound("test", "test.wav") is False
            assert manager.play_sound("test") is None
            assert manager.play_music("test.ogg") is False

    def test_sound_category_enum(self):
        """Test SoundCategory enum values."""
        assert SoundCategory.UI.value == "ui"
        assert SoundCategory.GAME.value == "game"
        assert SoundCategory.AMBIENT.value == "ambient"
        assert SoundCategory.MUSIC.value == "music"

    def test_sound_config_dataclass(self):
        """Test SoundConfig dataclass."""
        config = SoundConfig(
            path="sounds/test.wav",
            category=SoundCategory.UI,
            volume=0.8
        )
        
        assert config.path == "sounds/test.wav"
        assert config.category == SoundCategory.UI
        assert config.volume == 0.8
        assert config.sound is None
