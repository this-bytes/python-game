"""Specialist Roster Panel for displaying all specialists."""

import pygame
from typing import Optional, Any
from src.ui.components.panel import Panel
from src.ui.components.progress_bar import ProgressBar
from src.ui.components.scroll_container import ScrollContainer
from src.models.game_state import GameState
from src.models.specialist import Specialist


class SpecialistRosterPanel(Panel):
    """Display all specialists with filters and sorting."""

    def __init__(self, game_state: GameState):
        """Initialize specialist roster panel.

        Args:
            game_state: Game state reference
        """
        # Position accounts for navigation menu (200px) + margin (20px)
        super().__init__(
            title="Specialist Roster",
            position=(220, 80),
            size=(380, 500),
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
        self.selected_specialist: Optional[Specialist] = None
        self.selected_team: list[Specialist] = []
        self.drag_highlight: Optional[str] = None  # Specialist ID being highlighted for drop

        # Card styling
        self.card_height = 80
        self.card_margin = 5

        # Status colors
        self.status_colors = {
            "available": (0, 200, 100),
            "working": (255, 200, 0),
            "resting": (100, 100, 200),
            "assigned": (0, 150, 255),  # Blue for assigned but not yet working
        }

        # Fonts
        self.card_font = None
        self.small_font = None
        self.tiny_font = None

    def render_content(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        """Render specialist roster content.

        Args:
            screen: Pygame surface to render on
            content_rect: Rectangle defining content area
        """
        # Initialize fonts if needed
        if self.card_font is None:
            self.card_font = pygame.font.SysFont('Arial', 14, bold=True)
            self.small_font = pygame.font.SysFont('Arial', 11)
            self.tiny_font = pygame.font.SysFont('Arial', 10)

        # Update scroll container
        specialists = self.game_state.specialists
        self.scroll_container.set_content_height(len(specialists) * (self.card_height + self.card_margin))
        self.scroll_container.position = (content_rect.x, content_rect.y)
        self.scroll_container.size = (content_rect.width, content_rect.height)

        # Create clipping region for scrolling
        screen.set_clip(content_rect)

        # Render specialists
        y_offset = content_rect.y - self.scroll_container.get_scroll_offset()

        for specialist in specialists:
            card_rect = pygame.Rect(
                content_rect.x + self.card_margin,
                y_offset,
                content_rect.width - self.card_margin * 2 - self.scroll_container.scroll_bar_width,
                self.card_height
            )

            # Skip if not visible
            if card_rect.bottom < content_rect.top or card_rect.top > content_rect.bottom:
                y_offset += self.card_height + self.card_margin
                continue

            self._render_specialist_card(screen, specialist, card_rect)
            y_offset += self.card_height + self.card_margin

        # Reset clipping
        screen.set_clip(None)

        # Render scroll container
        self.scroll_container.render(screen)

        # Render team synergy info if multiple specialists selected
        if len(self.selected_team) > 1 and hasattr(self.game_state, '_relationships_system'):
            self._render_team_synergy_info(screen, content_rect)

    def _render_specialist_card(self, screen: pygame.Surface, specialist: Specialist, rect: pygame.Rect) -> None:
        """Render individual specialist card.

        Args:
            screen: Pygame surface to render on
            specialist: Specialist to render
            rect: Rectangle for card
        """
        # Card background
        bg_color = (45, 45, 60) if specialist != self.selected_specialist else (60, 60, 80)
        pygame.draw.rect(screen, bg_color, rect, border_radius=4)

        # Border
        border_color = (80, 80, 100)
        if specialist == self.selected_specialist:
            border_color = (0, 180, 255)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=4)

        # Specialist name
        name_text = self.card_font.render(specialist.name, True, self.text_color)
        screen.blit(name_text, (rect.x + 10, rect.y + 5))

        # Level
        level_text = self.small_font.render(f"Lv.{specialist.level}", True, (200, 200, 0))
        screen.blit(level_text, (rect.x + 10, rect.y + 25))

        # Specialty
        specialty_text = self.small_font.render(specialist.specialty, True, (150, 150, 200))
        screen.blit(specialty_text, (rect.x + 60, rect.y + 25))

        # Status - enhanced to show assignment state
        status = specialist.status
        if specialist.assigned_incident_id:
            status = "assigned"
        
        status_color = self.status_colors.get(status, (150, 150, 150))
        status_text = self.small_font.render(status.upper(), True, status_color)
        screen.blit(status_text, (rect.right - 80, rect.y + 5))

        # Current assignment indicator
        if specialist.assigned_incident_id:
            assignment_text = self.tiny_font.render("ON MISSION", True, (0, 150, 255))
            screen.blit(assignment_text, (rect.right - 80, rect.y + 20))

        # XP Progress bar
        xp_rect = pygame.Rect(rect.x + 10, rect.y + 45, rect.width - 20, 20)
        xp_bar = ProgressBar(
            position=(xp_rect.x, xp_rect.y),
            size=(xp_rect.width, xp_rect.height),
            value=specialist.xp,
            max_value=specialist.calculate_xp_for_next_level(),
            show_label=True,
        )
        xp_bar.fill_color = (0, 150, 255)
        xp_bar.render(screen)

        # Burnout meter (if burnout system exists)
        if hasattr(self.game_state, '_burnout_system') and self.game_state._burnout_system:
            burnout_status = self.game_state._burnout_system.get_specialist_status(specialist.id)
            if burnout_status:
                burnout_level = burnout_status.get('burnout_level', 0)
                burnout_rect = pygame.Rect(rect.x + 10, rect.y + 70, rect.width - 20, 15)
                
                # Background
                pygame.draw.rect(screen, (40, 40, 40), burnout_rect)
                
                # Burnout fill (red for high burnout)
                burnout_color = (255, 100, 100) if burnout_level > 60 else (255, 150, 100) if burnout_level > 30 else (100, 255, 100)
                fill_width = int(burnout_rect.width * (burnout_level / 100))
                if fill_width > 0:
                    fill_rect = pygame.Rect(burnout_rect.x, burnout_rect.y, fill_width, burnout_rect.height)
                    pygame.draw.rect(screen, burnout_color, fill_rect)
                
                # Border
                pygame.draw.rect(screen, (80, 80, 80), burnout_rect, 1)
                
                # Label
                burnout_text = self.tiny_font.render(f"Burnout: {burnout_level}%", True, (200, 200, 200))
                screen.blit(burnout_text, (rect.x + 10, rect.y + 88))

        # Equipment indicators
        self._render_equipment_indicators(screen, specialist, rect)

        # Relationship indicators (if relationships system exists)
        if hasattr(self.game_state, '_relationships_system') and self.game_state._relationships_system:
            rel_summary = self.game_state._relationships_system.get_specialist_relationships_summary(specialist.id)
            if rel_summary:
                friends = rel_summary.get('friends', 0)
                rivals = rel_summary.get('rivals', 0)
                
                # Friend indicator
                if friends > 0:
                    friend_text = self.tiny_font.render(f"🤝 {friends}", True, (100, 255, 100))
                    screen.blit(friend_text, (rect.right - 60, rect.y + 70))
                
                # Rival indicator
                if rivals > 0:
                    rival_text = self.tiny_font.render(f"⚔️ {rivals}", True, (255, 100, 100))
                    screen.blit(rival_text, (rect.right - 60, rect.y + 85))

    def _render_equipment_indicators(self, screen: pygame.Surface, specialist: Specialist, rect: pygame.Rect) -> None:
        """Render equipment indicators for specialist.

        Args:
            screen: Pygame surface to render on
            specialist: Specialist to show equipment for
            rect: Card rectangle
        """
        if not hasattr(specialist, 'equipped_items') or not specialist.equipped_items:
            return

        # Equipment slot indicators
        equipment_y = rect.y + 70
        slot_types = ["tool", "badge", "peripheral"]
        slot_icons = ["🔧", "🏷️", "⌨️"]

        for i, (slot_type, icon) in enumerate(zip(slot_types, slot_icons)):
            slot_x = rect.x + 10 + i * 40

            # Check if equipment is equipped
            if slot_type in specialist.equipped_items:
                equipment_id = specialist.equipped_items[slot_type]
                if self.game_state._equipment_system:
                    equipment = self.game_state._equipment_system.equipment_catalog.get(equipment_id)
                    if equipment:
                        # Rarity color background
                        rarity_colors = {
                            "common": (150, 150, 150),
                            "rare": (0, 150, 255),
                            "epic": (150, 0, 255),
                            "legendary": (255, 150, 0)
                        }
                        rarity_color = rarity_colors.get(equipment.rarity.lower(), (100, 100, 100))

                        # Equipment icon with rarity background
                        pygame.draw.circle(screen, rarity_color, (slot_x + 8, equipment_y + 8), 10)
                        icon_text = self.tiny_font.render(icon, True, (0, 0, 0))
                        screen.blit(icon_text, (slot_x + 3, equipment_y + 2))
                    else:
                        # Unknown equipment
                        pygame.draw.circle(screen, (100, 100, 100), (slot_x + 8, equipment_y + 8), 10)
                        icon_text = self.tiny_font.render("?", True, (255, 255, 255))
                        screen.blit(icon_text, (slot_x + 6, equipment_y + 4))
                else:
                    # No equipment system
                    pygame.draw.circle(screen, (80, 80, 80), (slot_x + 8, equipment_y + 8), 10)
                    icon_text = self.tiny_font.render(icon, True, (150, 150, 150))
                    screen.blit(icon_text, (slot_x + 3, equipment_y + 2))
            else:
                # Empty slot
                pygame.draw.circle(screen, (60, 60, 60), (slot_x + 8, equipment_y + 8), 10)
                icon_text = self.tiny_font.render(icon, True, (100, 100, 100))
                screen.blit(icon_text, (slot_x + 3, equipment_y + 2))

    def handle_event(self, event: Any) -> bool:
        """Handle events for specialist roster panel.

        Args:
            event: Pygame event

        Returns:
            True if event was consumed, False otherwise
        """
        # Handle panel events first
        if super().handle_event(event):
            return True

        # Handle scroll container events
        if self.scroll_container.handle_event(event):
            return True

        # Handle specialist selection
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            rect = self.get_rect()
            content_rect = pygame.Rect(
                rect.x + self.BORDER_WIDTH,
                rect.y + self.TITLE_BAR_HEIGHT + self.BORDER_WIDTH,
                rect.width - 2 * self.BORDER_WIDTH,
                rect.height - self.TITLE_BAR_HEIGHT - 2 * self.BORDER_WIDTH
            )

            if content_rect.collidepoint(event.pos):
                # Calculate which specialist was clicked
                y_offset = content_rect.y - self.scroll_container.get_scroll_offset()
                for specialist in self.game_state.specialists:
                    card_rect = pygame.Rect(
                        content_rect.x + self.card_margin,
                        y_offset,
                        content_rect.width - self.card_margin * 2 - self.scroll_container.scroll_bar_width,
                        self.card_height
                    )

                    if card_rect.collidepoint(event.pos):
                        # Ctrl+click for multi-selection
                        if pygame.key.get_mods() & pygame.KMOD_CTRL:
                            if specialist in self.selected_team:
                                self.selected_team.remove(specialist)
                            else:
                                self.selected_team.append(specialist)
                        else:
                            # Single selection - clear team and select individual
                            self.selected_team.clear()
                            self.selected_specialist = specialist
                        return True

                    y_offset += self.card_height + self.card_margin

        # Handle drag over (highlight potential drop targets)
        elif event.type == pygame.MOUSEMOTION:
            if self._is_incident_being_dragged():
                rect = self.get_rect()
                content_rect = pygame.Rect(
                    rect.x + self.BORDER_WIDTH,
                    rect.y + self.TITLE_BAR_HEIGHT + self.BORDER_WIDTH,
                    rect.width - 2 * self.BORDER_WIDTH,
                    rect.height - self.TITLE_BAR_HEIGHT - 2 * self.BORDER_WIDTH
                )

                if content_rect.collidepoint(event.pos):
                    # Check which specialist is being hovered
                    y_offset = content_rect.y - self.scroll_container.get_scroll_offset()
                    for specialist in self.game_state.specialists:
                        card_rect = pygame.Rect(
                            content_rect.x + self.card_margin,
                            y_offset,
                            content_rect.width - self.card_margin * 2 - self.scroll_container.scroll_bar_width,
                            self.card_height
                        )

                        if card_rect.collidepoint(event.pos):
                            self.drag_highlight = specialist.id
                            return True

                        y_offset += self.card_height + self.card_margin
                
                self.drag_highlight = None

        # Handle drop event (mouse button up during drag)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.drag_highlight and self._is_incident_being_dragged():
                # Attempt assignment
                dragged_incident = self._get_dragged_incident()
                if dragged_incident:
                    success = self.game_state.assign_incident_to_specialist(
                        dragged_incident.id, self.drag_highlight
                    )
                    if success:
                        # Clear drag state in incident panel (cross-panel communication needed)
                        # For now, just clear our highlight
                        self.drag_highlight = None
                        return True

        # Handle keyboard shortcuts
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and len(self.selected_team) > 1:
                # Space to calculate synergy for selected team
                # Synergy is already displayed when team is selected
                return True
            elif event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Ctrl+C to clear team selection
                self.selected_team.clear()
                return True

        return False

    def get_selected_specialist(self) -> Optional[Specialist]:
        """Get currently selected specialist.

        Returns:
            Selected specialist or None
        """
        return self.selected_specialist

    def get_selected_team(self) -> list[Specialist]:
        """Get currently selected team.

        Returns:
            List of selected specialists
        """
        return self.selected_team.copy()

    def assign_selected_incident(self, incident_id: str) -> bool:
        """Assign an incident to the selected specialist.

        Args:
            incident_id: ID of incident to assign

        Returns:
            True if assignment successful
        """
        if not self.selected_specialist:
            return False

        return self.game_state.assign_incident_to_specialist(incident_id, self.selected_specialist.id)

    def _is_incident_being_dragged(self) -> bool:
        """Check if an incident is currently being dragged from another panel.
        
        Returns:
            True if incident is being dragged
        """
        # Cross-panel drag state requires a shared UI state manager.
        # Current architecture doesn't support this - incidents are dropped
        # directly on specialist cards for assignment. Full drag-drop between
        # panels would require refactoring to use a centralized DragDropManager.
        return False  # Not implemented - use direct click assignment instead

    def _get_dragged_incident(self) -> Optional[Any]:
        """Get the incident currently being dragged.
        
        Returns:
            Dragged incident or None
        """
        # See _is_incident_being_dragged() - requires shared UI state manager.
        return None  # Not implemented - use direct click assignment instead

    def _render_team_synergy_info(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        """Render team synergy information.

        Args:
            screen: Pygame surface to render on
            content_rect: Content rectangle
        """
        if not hasattr(self.game_state, '_relationships_system') or not self.game_state._relationships_system or self.small_font is None:
            return

        # Calculate synergy
        team_ids = [s.id for s in self.selected_team]
        synergy_multiplier = self.game_state._relationships_system.get_team_synergy_multiplier(team_ids)

        # Render synergy box at bottom
        synergy_rect = pygame.Rect(
            content_rect.x + 5,
            content_rect.bottom - 40,
            content_rect.width - 10,
            35
        )

        # Background
        pygame.draw.rect(screen, (30, 30, 50), synergy_rect, border_radius=4)
        pygame.draw.rect(screen, (80, 80, 100), synergy_rect, 1, border_radius=4)

        # Synergy text
        synergy_color = (100, 255, 100) if synergy_multiplier > 1.0 else ((255, 100, 100) if synergy_multiplier < 1.0 else (200, 200, 200))
        synergy_text = self.small_font.render(
            f"Team Synergy: {synergy_multiplier:.2f}x ({((synergy_multiplier - 1.0) * 100):+.1f}%)",
            True,
            synergy_color
        )
        screen.blit(synergy_text, (synergy_rect.x + 10, synergy_rect.y + 8))
