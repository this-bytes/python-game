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
        self.shadows = data.get("shadows", {})

        # Convert color lists to tuples
        for key, value in data.get("colors", {}).items():
            if isinstance(value, list) and len(value) >= 3:
                # Handle RGBA colors (4 values) and RGB colors (3 values)
                if len(value) == 4:
                    self.colors[key] = tuple(value[:4])
                else:
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

    def get_rgba_color(self, color_key: str, default: Tuple[int, int, int, int] = (255, 255, 255, 255)) -> Tuple[int, int, int, int]:
        """Get RGBA color from theme.

        Args:
            color_key: Color key name
            default: Default RGBA color if key not found

        Returns:
            RGBA color tuple
        """
        color = self.colors.get(color_key, default)
        if len(color) == 3:
            return (color[0], color[1], color[2], 255)
        return color

    def get_font_size(self, font_key: str, default: int = 14) -> int:
        """Get font size from theme.

        Args:
            font_key: Font key name
            default: Default size if key not found

        Returns:
            Font size in pixels
        """
        return self.fonts.get(font_key, default)

    def get_shadow(self, shadow_key: str, default: Tuple[int, int, int, int] = (0, 2, 8, 128)) -> Tuple[int, int, int, int]:
        """Get shadow parameters from theme.

        Args:
            shadow_key: Shadow key name
            default: Default shadow parameters (offset_x, offset_y, blur, alpha)

        Returns:
            Shadow parameters as (offset_x, offset_y, blur, alpha)
        """
        shadow = self.shadows.get(shadow_key, default)
        if isinstance(shadow, list) and len(shadow) >= 4:
            return tuple(shadow[:4])
        return default


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
        self.font_cache: Dict[Tuple[str, int, bool, bool], pygame.font.Font] = {}

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

    def get_rgba_color(self, color_key: str, default: Tuple[int, int, int, int] = (255, 255, 255, 255)) -> Tuple[int, int, int, int]:
        """Get RGBA color from current theme.

        Args:
            color_key: Color key name
            default: Default RGBA color if key not found

        Returns:
            RGBA color tuple
        """
        if self.current_theme:
            return self.current_theme.get_rgba_color(color_key, default)
        return default

    def get_color(self, color_key: str, default: Tuple[int, int, int] = (255, 255, 255)) -> Tuple[int, int, int]:
        """Get RGB color from current theme.

        Args:
            color_key: Color key name
            default: Default RGB color if key not found

        Returns:
            RGB color tuple
        """
        if self.current_theme:
            return self.current_theme.get_color(color_key, default)
        return default

    def get_shadow(self, shadow_key: str, default: Tuple[int, int, int, int] = (0, 2, 8, 128)) -> Tuple[int, int, int, int]:
        """Get shadow parameters from current theme.

        Args:
            shadow_key: Shadow key name
            default: Default shadow parameters

        Returns:
            Shadow parameters as (offset_x, offset_y, blur, alpha)
        """
        if self.current_theme:
            return self.current_theme.get_shadow(shadow_key, default)
        return default

    def get_font(
        self,
        font_key: str = "body",
        bold: bool = False,
        italic: bool = False,
        font_family: Optional[str] = None
    ) -> pygame.font.Font:
        """Get font from current theme with modern typography.

        Args:
            font_key: Font key for size and weight
            bold: Bold font weight
            italic: Italic style
            font_family: Override font family

        Returns:
            Pygame font object with appropriate styling
        """
        # Modern font stack with fallbacks
        if font_family is None:
            # Primary: Clean, modern sans-serif fonts
            font_stack = ['dejavusans', 'ubuntumono', 'nimbussans', 'arial']
            font_family = font_stack[0]  # Use first available

        # Get font size from theme
        size = self.current_theme.get_font_size(font_key, 14) if self.current_theme else 14

        # Adjust size based on font key for better hierarchy
        if font_key == "title":
            size = int(size * 1.2)  # Slightly larger titles
        elif font_key == "heading":
            size = int(size * 1.1)  # Slightly larger headings
        elif font_key == "small":
            size = max(10, int(size * 0.85))  # Smaller but readable
        elif font_key == "tiny":
            size = max(8, int(size * 0.75))  # Very small but legible

        # Create cache key
        cache_key = (font_family, size, bold, italic)

        # Check cache first
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]

        # Create font with styling
        try:
            font = pygame.font.SysFont(font_family, size, bold=bold, italic=italic)
        except:
            # Fallback to default if font family not available
            font = pygame.font.SysFont('dejavusans', size, bold=bold, italic=italic)

        # Cache the font
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
