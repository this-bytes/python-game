"""Equipment Shop Panel for purchasing equipment."""

import pygame
from typing import Optional, Any, List
from src.ui.components.panel import Panel
from src.ui.components.scroll_container import ScrollContainer
from src.ui.components.button import Button
from src.models.game_state import GameState
from src.models.equipment import Equipment


class EquipmentShopPanel(Panel):
    """Shop panel for purchasing equipment items."""

    def __init__(self, game_state: GameState):
        """Initialize equipment shop panel.

        Args:
            game_state: Game state reference
        """
        # Position accounts for navigation menu (200px) + margin (20px)
        # ViewManager will reposition based on current view
        super().__init__(
            title="Equipment Shop",
            position=(220, 80),
            size=(380, 600),
            closeable=True,
            minimizable=True,
            draggable=True,
        )
        self.game_state = game_state
        self.scroll_container = ScrollContainer(
            position=(0, 0),
            size=(380, 468),
            content_height=0
        )

        # Equipment filtering
        self.selected_rarity = "all"  # all, common, rare, epic, legendary
        self.selected_type = "all"    # all, tool, badge, peripheral

        # Rarity colors
        self.rarity_colors = {
            "common": (150, 150, 150),
            "rare": (0, 150, 255),
            "epic": (150, 0, 255),
            "legendary": (255, 150, 0)
        }

        # Equipment type icons (simple text for now)
        self.type_icons = {
            "tool": "🔧",
            "badge": "🏷️",
            "peripheral": "⌨️"
        }

    def render(self, screen: pygame.Surface):
        """Render the equipment shop panel.

        Args:
            screen: Pygame surface to render to
        """
        # Render base panel
        super().render(screen)

        if not self.visible:
            return

        # Render filters
        self._render_filters(screen)

        # Render money display
        money_text = f"Money: ${self.game_state.current_money:,}"
        money_color = (0, 200, 0) if self.game_state.current_money > 0 else (200, 0, 0)
        self._render_text(screen, money_text, (10, 35), money_color, 16)

        # Render equipment list
        self._render_equipment_list(screen)

    def _render_filters(self, screen: pygame.Surface):
        """Render filter controls.

        Args:
            screen: Pygame surface to render to
        """
        # Rarity filter buttons
        rarities = ["all", "common", "rare", "epic", "legendary"]
        for i, rarity in enumerate(rarities):
            color = self.rarity_colors.get(rarity, (100, 100, 100))
            if self.selected_rarity == rarity:
                color = (255, 255, 255)  # Highlight selected

            pygame.draw.rect(screen, color,
                           (10 + i * 70, 55, 65, 25))
            self._render_text(screen, rarity.title(),
                            (10 + i * 70 + 32, 55 + 12),
                            (0, 0, 0), 12, center=True)

        # Type filter buttons
        types = ["all", "tool", "badge", "peripheral"]
        for i, eq_type in enumerate(types):
            color = (100, 100, 100)
            if self.selected_type == eq_type:
                color = (255, 255, 255)  # Highlight selected

            pygame.draw.rect(screen, color,
                           (10 + i * 90, 85, 85, 25))
            type_text = eq_type.title() if eq_type != "all" else "All Types"
            self._render_text(screen, type_text,
                            (10 + i * 90 + 42, 85 + 12),
                            (0, 0, 0), 12, center=True)

    def _render_equipment_list(self, screen: pygame.Surface):
        """Render the list of available equipment.

        Args:
            screen: Pygame surface to render to
        """
        if not self.game_state._equipment_system:
            self._render_text(screen, "Equipment system not available",
                            (self.rect.centerx, 150), (200, 0, 0), 16, center=True)
            return

        # Get filtered equipment
        equipment_list = self._get_filtered_equipment()

        # Calculate content height
        self.scroll_container.content_height = len(equipment_list) * 100

        # Render equipment cards
        for i, equipment in enumerate(equipment_list):
            card_y = i * 100 + self.scroll_container.scroll_offset
            if card_y < -100 or card_y > self.rect.height:
                continue  # Skip off-screen cards

            self._render_equipment_card(screen, equipment, 10, 120 + card_y)

    def _get_filtered_equipment(self) -> List[Equipment]:
        """Get equipment list filtered by current settings.

        Returns:
            List of filtered equipment
        """
        if not self.game_state._equipment_system:
            return []

        equipment_list = list(self.game_state._equipment_system.equipment_catalog.values())

        # Filter by rarity
        if self.selected_rarity != "all":
            equipment_list = [eq for eq in equipment_list
                            if eq.rarity.lower() == self.selected_rarity]

        # Filter by type
        if self.selected_type != "all":
            equipment_list = [eq for eq in equipment_list
                            if eq.equipment_type.lower() == self.selected_type]

        # Sort by cost
        equipment_list.sort(key=lambda eq: eq.cost)

        return equipment_list

    def _render_equipment_card(self, screen: pygame.Surface, equipment: Equipment,
                              x: int, y: int):
        """Render an equipment card.

        Args:
            screen: Pygame surface to render to
            equipment: Equipment to render
            x: X position
            y: Y position
        """
        card_width = self.rect.width - 20
        card_height = 90

        # Card background with rarity color border
        rarity_color = self.rarity_colors.get(equipment.rarity.lower(), (100, 100, 100))
        pygame.draw.rect(screen, rarity_color, (x, y, card_width, card_height), 2)
        pygame.draw.rect(screen, (50, 50, 50), (x + 2, y + 2, card_width - 4, card_height - 4))

        # Equipment name and type
        name_text = f"{self.type_icons.get(equipment.equipment_type.lower(), '❓')} {equipment.name}"
        self._render_text(screen, name_text, (x + 10, y + 10), (255, 255, 255), 14)

        # Rarity badge
        rarity_text = equipment.rarity.upper()
        pygame.draw.rect(screen, rarity_color, (x + card_width - 80, y + 8, 70, 20))
        self._render_text(screen, rarity_text, (x + card_width - 45, y + 18),
                         (0, 0, 0), 10, center=True)

        # Description
        desc_text = equipment.description[:40] + "..." if len(equipment.description) > 40 else equipment.description
        self._render_text(screen, desc_text, (x + 10, y + 30), (200, 200, 200), 11)

        # Stat bonuses
        bonuses_text = self._format_stat_bonuses(equipment.stat_bonuses)
        self._render_text(screen, bonuses_text, (x + 10, y + 45), (150, 255, 150), 11)

        # Cost and buy button
        cost_text = f"Cost: ${equipment.cost:,}"
        can_afford = self.game_state.current_money >= equipment.cost
        cost_color = (0, 255, 0) if can_afford else (255, 0, 0)
        self._render_text(screen, cost_text, (x + 10, y + 65), cost_color, 12)

        # Buy button
        button_color = (0, 150, 0) if can_afford else (100, 100, 100)
        pygame.draw.rect(screen, button_color, (x + card_width - 80, y + 60, 70, 25))
        self._render_text(screen, "BUY", (x + card_width - 45, y + 72),
                         (255, 255, 255), 12, center=True)

    def _format_stat_bonuses(self, stat_bonuses: dict) -> str:
        """Format stat bonuses for display.

        Args:
            stat_bonuses: Dictionary of stat bonuses

        Returns:
            Formatted string
        """
        bonuses = []
        for stat, value in stat_bonuses.items():
            if stat == "xp_bonus" or stat == "experience_bonus":
                bonuses.append(f"XP +{value:.0%}")
            elif stat == "speed":
                bonuses.append(f"Speed +{value}")
            elif stat == "accuracy":
                bonuses.append(f"Acc +{value}")
            else:
                bonuses.append(f"{stat.title()} +{value}")

        return " | ".join(bonuses)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled
        """
        if not self.visible:
            return False

        # Handle filter clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            rel_pos = (mouse_pos[0] - self.rect.left, mouse_pos[1] - self.rect.top)

            # Rarity filters
            if 55 <= rel_pos[1] <= 80:
                for i, rarity in enumerate(["all", "common", "rare", "epic", "legendary"]):
                    if 10 + i * 70 <= rel_pos[0] <= 10 + i * 70 + 65:
                        self.selected_rarity = rarity
                        return True

            # Type filters
            if 85 <= rel_pos[1] <= 110:
                for i, eq_type in enumerate(["all", "tool", "badge", "peripheral"]):
                    if 10 + i * 90 <= rel_pos[0] <= 10 + i * 90 + 85:
                        self.selected_type = eq_type
                        return True

            # Buy buttons
            equipment_list = self._get_filtered_equipment()
            for i, equipment in enumerate(equipment_list):
                card_y = 120 + i * 100 - self.scroll_container.scroll_offset
                if 60 <= rel_pos[1] - card_y <= 85 and self.rect.width - 100 <= rel_pos[0] <= self.rect.width - 10:
                    self._attempt_purchase(equipment)
                    return True

        # Handle scrolling
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_container.scroll_offset = max(0, self.scroll_container.scroll_offset - 30)
                return True
            elif event.button == 5:  # Scroll down
                max_scroll = max(0, self.scroll_container.content_height - self.scroll_container.size[1])
                self.scroll_container.scroll_offset = min(max_scroll, self.scroll_container.scroll_offset + 30)
                return True

        return super().handle_event(event)

    def _attempt_purchase(self, equipment: Equipment):
        """Attempt to purchase equipment.

        Args:
            equipment: Equipment to purchase
        """
        if self.game_state.current_money >= equipment.cost:
            # Deduct cost
            self.game_state.current_money -= equipment.cost

            # Add to player's equipment inventory (for now, add to all specialists)
            # In a full implementation, this would go to a player inventory
            # For now, let's add it to the first available specialist as a demo
            if self.game_state.specialists:
                specialist = self.game_state.specialists[0]
                if self.game_state._equipment_system:
                    self.game_state._equipment_system.add_to_inventory(specialist, equipment)
                    self.game_state.equipment_instances[equipment.id] = equipment

                    # Add feedback
                    self.game_state.dopamine_feedback_queue.append({
                        "type": "equipment_purchase",
                        "timestamp": pygame.time.get_ticks() / 1000.0,
                        "equipment": equipment,
                        "cost": equipment.cost
                    })

        # Could add sound effect or visual feedback here

    def _render_text(self, screen: pygame.Surface, text: str, pos: tuple,
                    color: tuple = (255, 255, 255), size: int = 14,
                    center: bool = False):
        """Render text to screen.

        Args:
            screen: Surface to render to
            text: Text to render
            pos: Position (x, y)
            color: Text color
            size: Font size
            center: Whether to center text at position
        """
        try:
            font = pygame.font.SysFont("Arial", size)
            text_surface = font.render(text, True, color)
            if center:
                rect = text_surface.get_rect(center=pos)
                screen.blit(text_surface, rect)
            else:
                screen.blit(text_surface, pos)
        except Exception:
            pass  # Skip text rendering if font fails