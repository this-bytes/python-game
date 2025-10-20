"""Economy panel for displaying market conditions, financial status, and investment options."""

import pygame
from typing import Optional, Dict, Any, List

from src.ui.components.panel import Panel
from src.core.plugins.economy_plugin import EconomyPlugin
from src.core.economy_system import MarketEvent, Investment


class EconomyPanel(Panel):
    """Panel for displaying economy information and managing investments."""

    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize economy panel.

        Args:
            x: Panel x position
            y: Panel y position
            width: Panel width
            height: Panel height
        """
        super().__init__(
            "Economy & Investments",
            (x, y),
            (width, height)
        )
        self.economy_plugin: Optional[EconomyPlugin] = None

        # Layout constants
        self._padding = 10

        # Colors
        self.market_color_good = (76, 175, 80)    # Green
        self.market_color_neutral = (255, 193, 7) # Yellow
        self.market_color_bad = (244, 67, 54)     # Red

        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.header_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.normal_font = pygame.font.SysFont("Arial", 14)
        self.small_font = pygame.font.SysFont("Arial", 12)

    def update(self, game_state) -> None:
        """Update the panel with current game state.

        Args:
            game_state: Current game state
        """
        # Find the economy plugin if not already found
        if not self.economy_plugin:
            if hasattr(game_state, '_systems'):
                for system in game_state._systems.values():
                    if isinstance(system, EconomyPlugin):
                        self.economy_plugin = system
                        break

    def render(self, screen: pygame.Surface) -> None:
        """Render the economy panel.

        Args:
            screen: The surface to render to
        """
        if not self.economy_plugin or not self.economy_plugin.economy_system:
            return

        # Call parent render
        super().render(screen)

        # Get content area
        content_rect = pygame.Rect(
            self.position[0] + self._padding,
            self.position[1] + self._padding + 30,  # Account for title
            self.size[0] - 2 * self._padding,
            self.size[1] - 2 * self._padding - 30
        )

        # Render sections
        self._render_market_summary(screen, content_rect)
        self._render_active_events(screen, content_rect)
        self._render_investment_portfolio(screen, content_rect)
        self._render_investment_options(screen, content_rect)

    def _render_market_summary(self, screen: pygame.Surface, panel_rect: pygame.Rect) -> None:
        """Render market summary section."""
        if not self.economy_plugin or not self.economy_plugin.economy_system:
            return

        y_offset = panel_rect.y + 50

        # Header
        header_text = self.header_font.render("Market Summary", True, (255, 255, 255))
        screen.blit(header_text, (panel_rect.x + 10, y_offset))

        y_offset += 30

        market_summary = self.economy_plugin.economy_system.get_market_summary()

        # Market multiplier
        multiplier = market_summary["market_multiplier"]
        multiplier_color = self._get_multiplier_color(multiplier)
        multiplier_text = self.normal_font.render(
            f"Market Multiplier: {multiplier:.2f}x", True, multiplier_color
        )
        screen.blit(multiplier_text, (panel_rect.x + 20, y_offset))
        y_offset += 20

        # Active events count
        events_text = self.normal_font.render(
            f"Active Events: {market_summary['active_events']}", True, (255, 255, 255)
        )
        screen.blit(events_text, (panel_rect.x + 20, y_offset))
        y_offset += 20

        # Investment summary
        investments_text = self.normal_font.render(
            f"Investments: {market_summary['total_investments']} "
            f"(Value: ${market_summary['investment_value']:,.0f})",
            True, (255, 255, 255)
        )
        screen.blit(investments_text, (panel_rect.x + 20, y_offset))

    def _render_active_events(self, screen: pygame.Surface, panel_rect: pygame.Rect) -> None:
        """Render active market events section."""
        if not self.economy_plugin or not self.economy_plugin.economy_system:
            return

        y_offset = panel_rect.y + 150

        # Header
        header_text = self.header_font.render("Active Market Events", True, (255, 255, 255))
        screen.blit(header_text, (panel_rect.x + 10, y_offset))

        y_offset += 30

        active_events = self.economy_plugin.economy_system.get_active_events()

        if not active_events:
            no_events_text = self.normal_font.render("No active market events", True, (255, 255, 255))
            screen.blit(no_events_text, (panel_rect.x + 20, y_offset))
            return

        for i, event in enumerate(active_events[:3]):  # Show up to 3 events
            if y_offset + 60 > panel_rect.bottom:
                break

            # Event name
            name_text = self.normal_font.render(event.name, True, (255, 255, 255))
            screen.blit(name_text, (panel_rect.x + 20, y_offset))

            # Remaining time
            remaining = event.get_remaining_time(self.economy_plugin.economy_system.last_update_time)
            time_text = self.small_font.render(
                f"{remaining:.0f}s remaining", True, (255, 255, 255)
            )
            screen.blit(time_text, (panel_rect.x + 20, y_offset + 15))

            # Effects summary
            effects = ", ".join([f"{k}: {v:.1f}x" for k, v in event.effects.items() if "multiplier" in k])
            if effects:
                effects_text = self.small_font.render(f"Effects: {effects}", True, (255, 255, 255))
                screen.blit(effects_text, (panel_rect.x + 20, y_offset + 30))

            y_offset += 50

    def _render_investment_portfolio(self, screen: pygame.Surface, panel_rect: pygame.Rect) -> None:
        """Render investment portfolio section."""
        if not self.economy_plugin or not self.economy_plugin.economy_system:
            return

        y_offset = panel_rect.y + 300

        # Header
        header_text = self.header_font.render("Investment Portfolio", True, (255, 255, 255))
        screen.blit(header_text, (panel_rect.x + 10, y_offset))

        y_offset += 30

        investments = self.economy_plugin.economy_system.investments

        if not investments:
            no_inv_text = self.normal_font.render("No active investments", True, (255, 255, 255))
            screen.blit(no_inv_text, (panel_rect.x + 20, y_offset))
            return

        for i, investment in enumerate(investments):
            if y_offset + 40 > panel_rect.bottom:
                break

            # Investment info
            profit_loss = investment.calculate_profit_loss()
            profit_color = self.market_color_good if profit_loss >= 0 else self.market_color_bad

            inv_text = self.normal_font.render(
                f"{investment.investment_type}: ${investment.current_value:,.0f} "
                f"(P/L: ${profit_loss:,.0f})",
                True, profit_color
            )
            screen.blit(inv_text, (panel_rect.x + 20, y_offset))

            y_offset += 20

    def _render_investment_options(self, screen: pygame.Surface, panel_rect: pygame.Rect) -> None:
        """Render available investment options."""
        if not self.economy_plugin or not self.economy_plugin.economy_system:
            return

        y_offset = panel_rect.y + 450

        # Header
        header_text = self.header_font.render("Investment Options", True, (255, 255, 255))
        screen.blit(header_text, (panel_rect.x + 10, y_offset))

        y_offset += 30

        investment_options = self.economy_plugin.economy_system.config["investment_system"]["investment_options"]

        for i, option in enumerate(investment_options):
            if y_offset + 60 > panel_rect.bottom:
                break

            # Option name
            name_text = self.normal_font.render(option["name"], True, (255, 255, 255))
            screen.blit(name_text, (panel_rect.x + 20, y_offset))

            # Return rate
            return_text = self.small_font.render(
                f"Return: {option['base_return_rate']*100:.1f}% | "
                f"Risk: {option['volatility']*100:.1f}% | "
                f"Min: ${option['min_investment']:,.0f}",
                True, (255, 255, 255)
            )
            screen.blit(return_text, (panel_rect.x + 20, y_offset + 15))

            y_offset += 40

    def _get_multiplier_color(self, multiplier: float) -> tuple:
        """Get color for market multiplier display."""
        if multiplier > 1.1:
            return self.market_color_good
        elif multiplier < 0.9:
            return self.market_color_bad
        else:
            return self.market_color_neutral

    def handle_click(self, pos: tuple[int, int]) -> Optional[Dict[str, Any]]:
        """Handle mouse clicks on the economy panel."""
        panel_rect = pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
        if not panel_rect.collidepoint(pos):
            return None

        # For now, just return panel interaction
        # Future: Handle investment selection, market event details, etc.
        return {
            "action": "economy_panel_click",
            "panel": "economy",
            "position": pos
        }