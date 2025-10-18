"""Audio Manager - Centralized sound system with categories and volume control.

This module provides a singleton audio manager for handling all game sounds:
- Sound effect categories (UI, game, ambient, music)
- Volume controls per category
- Sound pooling for performance
- Fade in/out support
- 3D spatial audio (distance-based volume)
- Music playlist management
"""

import pygame
import os
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from src.utils.logger import GameLogger


class SoundCategory(Enum):
    """Sound effect categories for volume control."""
    UI = "ui"
    GAME = "game"
    AMBIENT = "ambient"
    MUSIC = "music"


@dataclass
class SoundConfig:
    """Configuration for a loaded sound."""
    path: str
    category: SoundCategory
    volume: float = 1.0
    sound: Optional[pygame.mixer.Sound] = None


class AudioManager:
    """Centralized audio manager with category-based volume control.
    
    Singleton pattern ensures one audio manager for the entire game.
    Handles sound loading, playback, volume control, and spatial audio.
    """

    _instance: Optional["AudioManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "AudioManager":
        """Singleton pattern - only one AudioManager instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize audio manager (only once due to singleton)."""
        if AudioManager._initialized:
            return
        
        self.logger = GameLogger("audio_manager")
        
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                self.logger.logger.info("Pygame mixer initialized")
            except pygame.error as e:
                self.logger.logger.error(f"Failed to initialize pygame mixer: {e}")
                self._audio_enabled = False
                AudioManager._initialized = True
                return
        
        self._audio_enabled = True
        
        # Sound registry
        self._sounds: Dict[str, SoundConfig] = {}
        
        # Category volume levels (0.0 to 1.0)
        self._category_volumes: Dict[SoundCategory, float] = {
            SoundCategory.UI: 0.7,
            SoundCategory.GAME: 0.8,
            SoundCategory.AMBIENT: 0.5,
            SoundCategory.MUSIC: 0.6,
        }
        
        # Master volume
        self._master_volume: float = 1.0
        
        # Music management
        self._current_music: Optional[str] = None
        self._music_volume: float = 0.6
        self._music_fade_duration: float = 0.0
        
        # Sound pooling for performance
        self._max_simultaneous_sounds: int = 16
        pygame.mixer.set_num_channels(self._max_simultaneous_sounds)
        
        AudioManager._initialized = True
        self.logger.logger.info("AudioManager initialized")

    def is_enabled(self) -> bool:
        """Check if audio is enabled."""
        return self._audio_enabled

    def load_sound(
        self,
        sound_id: str,
        path: str,
        category: SoundCategory = SoundCategory.GAME,
        volume: float = 1.0
    ) -> bool:
        """Load a sound effect from file.
        
        Args:
            sound_id: Unique identifier for this sound
            path: Path to sound file (relative to project root)
            category: Sound category for volume control
            volume: Base volume (0.0 to 1.0)
            
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self._audio_enabled:
            return False
        
        # Check if already loaded
        if sound_id in self._sounds:
            self.logger.logger.debug(f"Sound {sound_id} already loaded")
            return True
        
        # Check if file exists
        if not os.path.exists(path):
            self.logger.logger.warning(f"Sound file not found: {path}")
            return False
        
        try:
            sound = pygame.mixer.Sound(path)
            self._sounds[sound_id] = SoundConfig(
                path=path,
                category=category,
                volume=volume,
                sound=sound
            )
            self.logger.logger.info(f"Loaded sound: {sound_id} from {path}")
            return True
        except pygame.error as e:
            self.logger.logger.error(f"Failed to load sound {sound_id}: {e}")
            return False

    def play_sound(
        self,
        sound_id: str,
        volume_multiplier: float = 1.0,
        loops: int = 0
    ) -> Optional[pygame.mixer.Channel]:
        """Play a loaded sound effect.
        
        Args:
            sound_id: ID of sound to play
            volume_multiplier: Additional volume multiplier (0.0 to 1.0)
            loops: Number of times to loop (-1 for infinite)
            
        Returns:
            Channel object if played, None if failed
        """
        if not self._audio_enabled:
            return None
        
        if sound_id not in self._sounds:
            self.logger.logger.warning(f"Sound not loaded: {sound_id}")
            return None
        
        config = self._sounds[sound_id]
        if config.sound is None:
            return None
        
        # Calculate final volume
        category_volume = self._category_volumes.get(config.category, 1.0)
        final_volume = (
            self._master_volume
            * category_volume
            * config.volume
            * volume_multiplier
        )
        
        try:
            config.sound.set_volume(final_volume)
            channel = config.sound.play(loops=loops)
            return channel
        except pygame.error as e:
            self.logger.logger.error(f"Failed to play sound {sound_id}: {e}")
            return None

    def play_sound_3d(
        self,
        sound_id: str,
        position: Tuple[float, float],
        listener_position: Tuple[float, float] = (0, 0),
        max_distance: float = 1000.0,
        volume_multiplier: float = 1.0
    ) -> Optional[pygame.mixer.Channel]:
        """Play sound with distance-based volume (spatial audio).
        
        Args:
            sound_id: ID of sound to play
            position: (x, y) position of sound source
            listener_position: (x, y) position of listener
            max_distance: Distance at which sound is inaudible
            volume_multiplier: Additional volume multiplier
            
        Returns:
            Channel object if played, None if failed
        """
        # Calculate distance
        dx = position[0] - listener_position[0]
        dy = position[1] - listener_position[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        # Calculate distance-based volume
        if distance >= max_distance:
            return None  # Too far to hear
        
        distance_volume = 1.0 - (distance / max_distance)
        
        # Play with distance-adjusted volume
        return self.play_sound(sound_id, volume_multiplier * distance_volume)

    def stop_sound(self, sound_id: str) -> None:
        """Stop all instances of a sound.
        
        Args:
            sound_id: ID of sound to stop
        """
        if not self._audio_enabled:
            return
        
        if sound_id not in self._sounds:
            return
        
        config = self._sounds[sound_id]
        if config.sound:
            config.sound.stop()

    def set_master_volume(self, volume: float) -> None:
        """Set master volume for all sounds.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self._master_volume = max(0.0, min(1.0, volume))
        self.logger.logger.info(f"Master volume set to {self._master_volume:.2f}")

    def set_category_volume(self, category: SoundCategory, volume: float) -> None:
        """Set volume for a specific category.
        
        Args:
            category: Sound category
            volume: Volume level (0.0 to 1.0)
        """
        self._category_volumes[category] = max(0.0, min(1.0, volume))
        self.logger.logger.info(f"{category.value} volume set to {volume:.2f}")

    def get_master_volume(self) -> float:
        """Get current master volume."""
        return self._master_volume

    def get_category_volume(self, category: SoundCategory) -> float:
        """Get current volume for category."""
        return self._category_volumes.get(category, 1.0)

    def play_music(
        self,
        music_path: str,
        loop: bool = True,
        fade_in: float = 0.0,
        volume: float = 1.0
    ) -> bool:
        """Play background music.
        
        Args:
            music_path: Path to music file
            loop: Whether to loop music
            fade_in: Fade in duration in seconds
            volume: Music volume (0.0 to 1.0)
            
        Returns:
            True if started successfully, False otherwise
        """
        if not self._audio_enabled:
            return False
        
        if not os.path.exists(music_path):
            self.logger.logger.warning(f"Music file not found: {music_path}")
            return False
        
        try:
            # Stop current music if playing
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            # Load and play new music
            pygame.mixer.music.load(music_path)
            self._music_volume = volume
            pygame.mixer.music.set_volume(volume * self._master_volume)
            
            loops = -1 if loop else 0
            if fade_in > 0:
                pygame.mixer.music.play(loops=loops, fade_ms=int(fade_in * 1000))
            else:
                pygame.mixer.music.play(loops=loops)
            
            self._current_music = music_path
            self.logger.logger.info(f"Started music: {music_path}")
            return True
        except pygame.error as e:
            self.logger.logger.error(f"Failed to play music: {e}")
            return False

    def stop_music(self, fade_out: float = 0.0) -> None:
        """Stop background music.
        
        Args:
            fade_out: Fade out duration in seconds
        """
        if not self._audio_enabled:
            return
        
        if fade_out > 0:
            pygame.mixer.music.fadeout(int(fade_out * 1000))
        else:
            pygame.mixer.music.stop()
        
        self._current_music = None

    def fade_music_to(
        self,
        new_music_path: str,
        duration: float = 2.0,
        loop: bool = True
    ) -> bool:
        """Fade out current music and fade in new music.
        
        Args:
            new_music_path: Path to new music file
            duration: Total fade duration (half for fade out, half for fade in)
            loop: Whether to loop new music
            
        Returns:
            True if transition started, False otherwise
        """
        fade_duration = duration / 2.0
        
        # Fade out current music
        self.stop_music(fade_out=fade_duration)
        
        # TODO: This is a simplified implementation
        # A proper implementation would use a timer to start the new music
        # after the fade out completes
        # For now, we'll just start the new music with fade in
        return self.play_music(new_music_path, loop=loop, fade_in=fade_duration)

    def pause_music(self) -> None:
        """Pause background music."""
        if self._audio_enabled and pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()

    def unpause_music(self) -> None:
        """Unpause background music."""
        if self._audio_enabled:
            pygame.mixer.music.unpause()

    def is_music_playing(self) -> bool:
        """Check if music is currently playing."""
        return self._audio_enabled and pygame.mixer.music.get_busy()

    def get_current_music(self) -> Optional[str]:
        """Get path of currently playing music."""
        return self._current_music

    def preload_sounds(self, sound_configs: List[Dict]) -> int:
        """Preload multiple sounds from configuration.
        
        Args:
            sound_configs: List of dicts with keys: id, path, category, volume
            
        Returns:
            Number of sounds loaded successfully
        """
        loaded_count = 0
        for config in sound_configs:
            sound_id = config.get("id")
            path = config.get("path")
            category_str = config.get("category", "game")
            volume = config.get("volume", 1.0)
            
            if not sound_id or not path:
                continue
            
            try:
                category = SoundCategory(category_str)
            except ValueError:
                category = SoundCategory.GAME
            
            if self.load_sound(sound_id, path, category, volume):
                loaded_count += 1
        
        self.logger.logger.info(f"Preloaded {loaded_count}/{len(sound_configs)} sounds")
        return loaded_count

    def unload_sound(self, sound_id: str) -> None:
        """Unload a sound from memory.
        
        Args:
            sound_id: ID of sound to unload
        """
        if sound_id in self._sounds:
            del self._sounds[sound_id]
            self.logger.logger.debug(f"Unloaded sound: {sound_id}")

    def unload_all_sounds(self) -> None:
        """Unload all sounds from memory."""
        self._sounds.clear()
        self.logger.logger.info("Unloaded all sounds")


# Singleton accessor
_audio_manager_instance: Optional[AudioManager] = None


def get_audio_manager() -> AudioManager:
    """Get the singleton AudioManager instance.
    
    Returns:
        AudioManager singleton
    """
    global _audio_manager_instance
    if _audio_manager_instance is None:
        _audio_manager_instance = AudioManager()
    return _audio_manager_instance
