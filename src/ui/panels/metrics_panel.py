"""Metrics Dashboard Panel for displaying game statistics."""

import pygame
from src.ui.components.panel import Panel
from src.models.game_state import GameState


class MetricsPanel(Panel):
    """Real-time game metrics and statistics."""

    def __init__(self, game_state: GameState):
        """Initialize metrics panel.

        Args:
            game_state: Game state reference
        """
        # Position accounts for navigation menu (200px) + other panels + margins
        # Will be repositioned by ViewManager based on current view
        super().__init__(
            title="Game Metrics",
            position=(220, 80),
            size=(840, 600),
            closeable=True,
            minimizable=True,
            draggable=True,
        )
        self.game_state = game_state

        # Fonts
        self.title_font = None
        self.value_font = None
        self.label_font = None

    def render_content(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        """Render metrics content.

        Args:
            screen: Pygame surface to render on
            content_rect: Rectangle defining content area
        """
        # Initialize fonts if needed
        if self.title_font is None:
            self.title_font = pygame.font.SysFont('Arial', 16, bold=True)
            self.value_font = pygame.font.SysFont('Arial', 24, bold=True)
            self.label_font = pygame.font.SysFont('Arial', 12)

        # KPI cards layout (2x2 grid)
        card_width = (content_rect.width - 30) // 2
        card_height = 80
        card_margin = 10

        kpis = [
            {
                "label": "Total Money",
                "value": f"${self.game_state.current_money:,.0f}",
                "color": (0, 255, 100),
            },
            {
                "label": "Total Profit",
                "value": f"${self.game_state.metrics.total_profit:,.0f}",
                "color": (0, 200, 255),
            },
            {
                "label": "Incidents Handled",
                "value": f"{self.game_state.metrics.total_incidents_handled}",
                "color": (255, 200, 0),
            },
            {
                "label": "SLA Compliance",
                "value": f"{self.game_state.metrics.sla_compliance_rate:.1f}%",
                "color": (255, 100, 255),
            },
        ]

        # Render KPI cards
        for i, kpi in enumerate(kpis):
            row = i // 2
            col = i % 2
            card_x = content_rect.x + card_margin + col * (card_width + card_margin)
            card_y = content_rect.y + card_margin + row * (card_height + card_margin)

            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            self._render_kpi_card(screen, card_rect, kpi)

        # Additional metrics
        y_offset = content_rect.y + 2 * (card_height + card_margin) + 20

        metrics_list = [
            f"Incidents Failed: {self.game_state.metrics.total_incidents_failed}",
            f"Total XP Awarded: {self.game_state.metrics.total_xp_awarded:,.0f}",
            f"Specialist Utilization: {self.game_state.metrics.specialist_utilization_rate:.1f}%",
            f"Active Clients: {len([c for c in self.game_state.clients if c.active])}",
            f"Game Time: {self.game_state.get_game_time_elapsed():.1f}s",
            f"Assignment Success Rate: {self.game_state.metrics.assignment_success_rate:.1f}%",
            f"Specialty Matches: {self.game_state.metrics.specialty_match_assignments}",
            f"Total Assignments: {self.game_state.metrics.total_assignments_attempted}",
        ]

        for metric in metrics_list:
            metric_text = self.label_font.render(metric, True, self.text_color)
            screen.blit(metric_text, (content_rect.x + card_margin, y_offset))
            y_offset += 20

    def _render_kpi_card(self, screen: pygame.Surface, rect: pygame.Rect, kpi: dict) -> None:
        """Render individual KPI card.

        Args:
            screen: Pygame surface to render on
            rect: Rectangle for card
            kpi: KPI data dictionary
        """
        # Card background
        bg_color = (35, 35, 50)
        pygame.draw.rect(screen, bg_color, rect, border_radius=4)

        # Border
        border_color = (60, 60, 80)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=4)

        # Value (large, colored)
        value_text = self.value_font.render(kpi["value"], True, kpi["color"])
        value_rect = value_text.get_rect(centerx=rect.centerx, top=rect.y + 15)
        screen.blit(value_text, value_rect)

        # Label (small, below value)
        label_text = self.label_font.render(kpi["label"], True, (180, 180, 200))
        label_rect = label_text.get_rect(centerx=rect.centerx, bottom=rect.bottom - 10)
        screen.blit(label_text, label_rect)
