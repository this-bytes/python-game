"""Theme Manager for managing UI themes."""

import json
import os
import pygame
from typing import Dict, Tuple, Optional


class Theme:
    """Color palette and styling for UI."""

    def __init__(self, data: Dict):
        """Initialize theme from data.

        Args:
            data: Theme configuration dictionary
        """
        self.name = data.get("name", "Unnamed Theme")
        self.colors = {}
        self.fonts = data.get("fonts", {})

        # Convert color lists to tuples
        for key, value in data.get("colors", {}).items():
            if isinstance(value, list) and len(value) >= 3:
                self.colors[key] = tuple(value[:3])

    def get_color(self, color_key: str, default: Tuple[int, int, int] = (255, 255, 255)) -> Tuple[int, int, int]:
        """Get color from theme.

        Args:
            color_key: Color key name
            default: Default color if key not found

        Returns:
            RGB color tuple
        """
        return self.colors.get(color_key, default)

    def get_font_size(self, font_key: str, default: int = 14) -> int:
        """Get font size from theme.

        Args:
            font_key: Font key name
            default: Default size if key not found

        Returns:
            Font size in pixels
        """
        return self.fonts.get(font_key, default)


class ThemeManager:
    """Singleton theme manager."""

    _instance = None

    def __new__(cls):
        """Create singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize theme manager."""
        if self._initialized:
            return

        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None
        self.font_cache: Dict[Tuple[str, int, bool], pygame.font.Font] = {}

        # Load themes
        self._load_themes()

        # Set default theme
        self.load_theme("dark_cyber")

        self._initialized = True

    def _load_themes(self) -> None:
        """Load themes from themes.json."""
        themes_path = os.path.join(os.getcwd(), "data", "themes.json")

        try:
            with open(themes_path, 'r') as f:
                data = json.load(f)

            for theme_id, theme_data in data.get("themes", {}).items():
                self.themes[theme_id] = Theme(theme_data)

        except FileNotFoundError:
            print(f"Warning: themes.json not found at {themes_path}")
        except json.JSONDecodeError as e:
            print(f"Warning: Error parsing themes.json: {e}")

    def load_theme(self, theme_name: str) -> bool:
        """Switch to theme.

        Args:
            theme_name: Theme identifier

        Returns:
            True if theme loaded, False otherwise
        """
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
            return True
        return False

    def get_color(self, color_key: str, default: Tuple[int, int, int] = (255, 255, 255)) -> Tuple[int, int, int]:
        """Get color from current theme.

        Args:
            color_key: Color key name
            default: Default color if key not found

        Returns:
            RGB color tuple
        """
        if self.current_theme:
            return self.current_theme.get_color(color_key, default)
        return default

    def get_font(
        self,
        font_key: str = "normal",
        bold: bool = False,
        italic: bool = False,
        font_name: str = "Arial"
    ) -> pygame.font.Font:
        """Get font from current theme.

        Args:
            font_key: Font key for size
            bold: Bold font
            italic: Italic font
            font_name: Font family name

        Returns:
            Pygame font object
        """
        # Get font size from theme
        size = self.current_theme.get_font_size(font_key, 14) if self.current_theme else 14

        # Check cache
        cache_key = (font_name, size, bold)
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]

        # Create font
        font = pygame.font.SysFont(font_name, size, bold=bold, italic=italic)
        self.font_cache[cache_key] = font

        return font

    def get_current_theme(self) -> Optional[Theme]:
        """Get current theme.

        Returns:
            Current theme or None
        """
        return self.current_theme

    def get_available_themes(self) -> list:
        """Get list of available theme names.

        Returns:
            List of theme identifiers
        """
        return list(self.themes.keys())
