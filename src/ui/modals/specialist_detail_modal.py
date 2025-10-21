"""Specialist Detail Modal - Shows full specialist information and actions."""

import pygame
from typing import Callable, Optional
from src.models.specialist import Specialist
from src.ui.components.panel import ModernPanel
from src.ui.components.button import ModernButton, ButtonStyle
from src.ui.components.progress_bar import ProgressBar
from src.ui import event_types


class SpecialistDetailModal(ModernPanel):
    """Modal that displays detailed specialist information.
    
    Shows:
    - Full stats (level, XP, specialty, status)
    - Abilities and cooldowns
    - Equipment and stat bonuses
    - Team synergies
    - Action buttons (Assign, Manage Equipment, View History)
    """

    def __init__(
        self,
        screen: pygame.Surface,
        game_state,
        specialist_id: str,
        **kwargs
    ):
        """Initialize specialist detail modal.
        
        Args:
            screen: The main display surface.
            game_state: Game state reference.
            specialist_id: ID of the specialist to display.
            **kwargs: Additional arguments (ignored).
        """
        self.specialist = game_state.get_specialist_by_id(specialist_id)
        if not self.specialist:
            raise ValueError(f"Specialist with ID {specialist_id} not found.")

        # Center on screen
        super().__init__(
            title=f"{self.specialist.name} - {self.specialist.specialty}",
            position=(
                (screen.get_width() - 480) // 2,
                (screen.get_height() - 500) // 2
            ),
            size=(480, 500),
            closeable=True,
            minimizable=False,
            draggable=True,
        )
        
        self.screen = screen
        self.game_state = game_state
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 14, bold=True)
        self.normal_font = pygame.font.SysFont('Arial', 12)
        self.small_font = pygame.font.SysFont('Arial', 10)
        
        # Colors
        self.text_color = (220, 220, 220)
        self.label_color = (150, 150, 200)
        self.value_color = (100, 200, 255)
        
        # Status colors
        self.status_colors = {
            "available": (0, 200, 100),
            "working": (255, 200, 0),
            "resting": (100, 100, 200),
            "assigned": (0, 150, 255),
        }
        
        # Scroll position
        self.scroll_offset = 0
        self.scroll_speed = 20
        
        # Buttons
        self.assign_button = ModernButton(
            text="Assign to Incident",
            position=(0, 0),  # Will be repositioned in render_content
            size=(150, 35),
            callback=self._on_assign_clicked,
            style=ButtonStyle.PRIMARY,
        )
        
        self.close_button_action = ModernButton(
            text="Close",
            position=(0, 0),  # Will be repositioned in render_content
            size=(150, 35),
            callback=self._on_close_clicked,
            style=ButtonStyle.SECONDARY,
        )

    def _on_assign_clicked(self):
        """Handle assign button click."""
        # This would ideally open another modal to select an incident
        print(f"Assign button clicked for {self.specialist.name}")
        # For now, just close the modal
        self._on_close_clicked()

    def _on_close_clicked(self):
        """Handle close button click."""
        pygame.event.post(pygame.event.Event(event_types.HIDE_MODAL))
        
    def handle_event(self, event: pygame.event.Event):
        """Handle events for the modal."""
        super().handle_event(event)
        self.assign_button.handle_event(event)
        self.close_button_action.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Mouse wheel scrolling
            if event.button == 4:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
            elif event.button == 5:  # Scroll down
                # TODO: Add a max scroll limit based on content height
                self.scroll_offset += self.scroll_speed
        
        return True # Consume all events
        
    def update(self, delta_time: float):
        """Update modal state."""
        # The modal is static, so no updates needed for now.
        pass
        
    def draw(self):
        """Draw the modal."""
        # The ModalManager handles the background overlay, so we just draw the panel
        super().render(self.screen)

    def render_content(self, screen: pygame.Surface, content_rect: pygame.Rect) -> None:
        """Render specialist detail content.
        
        Args:
            screen: Pygame surface to render on
            content_rect: Rectangle defining content area
        """
        # Draw background
        pygame.draw.rect(screen, (30, 35, 50), content_rect)
        
        # Set clip region for scrolling
        screen.set_clip(content_rect)
        
        # Calculate layout
        y = content_rect.y - self.scroll_offset
        line_height = 22
        section_spacing = 15
        
        # ===== STATS SECTION =====
        self._render_section_title(screen, "STATS", y)
        y += line_height + 5
        
        # Level and XP
        self._render_stat_line(screen, content_rect.x, y, "Level:", f"{self.specialist.level}")
        y += line_height
        
        # XP bar
        xp_text = self.normal_font.render(
            f"XP: {self.specialist.xp} / {self.specialist.calculate_xp_for_next_level()}",
            True,
            self.label_color
        )
        screen.blit(xp_text, (content_rect.x + 10, y))
        y += 15
        
        xp_bar_rect = pygame.Rect(
            content_rect.x + 10,
            y,
            content_rect.width - 30,
            15
        )
        xp_bar = ProgressBar(
            position=(xp_bar_rect.x, xp_bar_rect.y),
            size=(xp_bar_rect.width, xp_bar_rect.height),
            value=self.specialist.xp,
            max_value=self.specialist.calculate_xp_for_next_level(),
            show_label=False,
        )
        xp_bar.render(screen)
        y += line_height + section_spacing
        
        # Status
        status = self.specialist.status
        if self.specialist.assigned_incident_id:
            status = "assigned"
        status_color = self.status_colors.get(status, (150, 150, 150))
        
        status_text = self.normal_font.render(f"Status: {status.upper()}", True, status_color)
        screen.blit(status_text, (content_rect.x + 10, y))
        y += line_height + section_spacing
        
        # ===== SPECIALTY & SKILLS SECTION =====
        self._render_section_title(screen, "SPECIALTY", y)
        y += line_height + 5
        
        specialty_text = self.normal_font.render(f"{self.specialist.specialty}", True, self.value_color)
        screen.blit(specialty_text, (content_rect.x + 10, y))
        y += line_height + section_spacing
        
        # ===== ABILITIES SECTION =====
        self._render_section_title(screen, "ABILITIES", y)
        y += line_height + 5
        
        # Check if specialist has abilities
        if hasattr(self.specialist, 'abilities') and self.specialist.abilities:
            for ability in self.specialist.abilities[:3]:  # Show first 3
                ability_name = getattr(ability, 'name', 'Unknown Ability')
                self._render_indented_text(screen, content_rect.x, y, f"• {ability_name}", self.text_color)
                y += line_height
        else:
            no_abilities = self.small_font.render("No abilities unlocked yet", True, (100, 100, 100))
            screen.blit(no_abilities, (content_rect.x + 10, y))
            y += line_height
        
        y += section_spacing
        
        # ===== EQUIPMENT SECTION =====
        self._render_section_title(screen, "EQUIPMENT", y)
        y += line_height + 5
        
        # Specialist equipment will be added later when equipment system is complete
        no_equipment = self.small_font.render("Equipment system coming soon", True, (100, 100, 100))
        screen.blit(no_equipment, (content_rect.x + 10, y))
        y += line_height
        
        y += section_spacing
        
        # ===== BURNOUT SECTION =====
        if hasattr(self.game_state, '_burnout_system') and self.game_state._burnout_system:
            self._render_section_title(screen, "BURNOUT", y)
            y += line_height + 5
            
            burnout_status = self.game_state._burnout_system.get_specialist_status(self.specialist.id)
            if burnout_status:
                burnout_level = burnout_status.get('burnout_level', 0)
                burnout_text = self.normal_font.render(f"Burnout: {burnout_level}%", True, self.label_color)
                screen.blit(burnout_text, (content_rect.x + 10, y))
                y += 15
                
                burnout_bar_rect = pygame.Rect(
                    content_rect.x + 10,
                    y,
                    content_rect.width - 30,
                    15
                )
                burnout_color = (255, 100, 100) if burnout_level > 60 else (255, 150, 100)
                burnout_bar = ProgressBar(
                    position=(burnout_bar_rect.x, burnout_bar_rect.y),
                    size=(burnout_bar_rect.width, burnout_bar_rect.height),
                    value=burnout_level,
                    max_value=100,
                    show_label=False,
                )
                burnout_bar.render(screen)
                y += line_height + section_spacing
        
        # ===== TEAM SYNERGIES SECTION =====
        if hasattr(self.game_state, '_relationships_system') and self.game_state._relationships_system:
            self._render_section_title(screen, "TEAM SYNERGIES", y)
            y += line_height + 5

            # RelationshipsSystem does not expose a get_synergies_for_specialist API
            # in some versions; compute synergies from the registered relationships
            # to remain compatible across releases.
            synergies: dict[str, float] = {}
            rel_system = self.game_state._relationships_system
            spec_rels = getattr(rel_system, 'specialists_relationships', {}).get(self.specialist.id)
            if spec_rels and getattr(spec_rels, 'relationships', None):
                for other_id, rel in spec_rels.relationships.items():
                    try:
                        multiplier = rel.get_synergy_multiplier()
                    except Exception:
                        # Defensive: if Relationship object shape changes, default to neutral
                        multiplier = 1.0
                    synergies[other_id] = multiplier

            if synergies:
                for other_spec_id, multiplier in list(synergies.items())[:2]:
                    other_spec = self.game_state.get_specialist_by_id(other_spec_id)
                    if other_spec:
                        synergy_text = self.small_font.render(
                            f"• {other_spec.name}: {multiplier:.2f}x",
                            True,
                            (100, 200, 100) if multiplier > 1.0 else (100, 100, 100)
                        )
                        screen.blit(synergy_text, (content_rect.x + 10, y))
                        y += line_height
            else:
                no_synergies = self.small_font.render("No synergies established yet", True, (100, 100, 100))
                screen.blit(no_synergies, (content_rect.x + 10, y))
                y += line_height
        
        # Reset clip region
        screen.set_clip(None)
        
        # ===== BUTTONS AT BOTTOM =====
        button_y = content_rect.bottom - 45
        
        # Assign button (enabled if specialist is available)
        is_available = self.specialist.status == "available" and not self.specialist.assigned_incident_id
        
        self.assign_button.position = (content_rect.x + 10, button_y)
        self.assign_button.enabled = is_available
        self.assign_button.render(screen)
        
        # Close button
        self.close_button_action.position = (content_rect.right - 160, button_y)
        self.close_button_action.render(screen)

    def _render_section_title(self, screen: pygame.Surface, title: str, y: int) -> None:
        """Render a section title.
        
        Args:
            screen: Pygame surface
            title: Section title text
            y: Y position
        """
        title_surf = self.title_font.render(title, True, (100, 200, 255))
        screen.blit(title_surf, (20, y))

    def _render_stat_line(self, screen: pygame.Surface, x: int, y: int, label: str, value: str) -> None:
        """Render a stat line (label: value).
        
        Args:
            screen: Pygame surface
            x: X position
            y: Y position
            label: Label text
            value: Value text
        """
        label_surf = self.normal_font.render(label, True, self.label_color)
        value_surf = self.normal_font.render(value, True, self.value_color)
        
        screen.blit(label_surf, (x + 10, y))
        screen.blit(value_surf, (x + 120, y))

    def _render_indented_text(self, screen: pygame.Surface, x: int, y: int, text: str, color) -> None:
        """Render indented text.
        
        Args:
            screen: Pygame surface
            x: X position
            y: Y position
            text: Text to render
            color: Text color
        """
        text_surf = self.small_font.render(text, True, color)
        screen.blit(text_surf, (x + 20, y))

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events.
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled
        """
        # Handle scroll (MOUSEWHEEL event in pygame 2.6+)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
                return True
            elif event.button == 5:  # Scroll down
                self.scroll_offset += self.scroll_speed
                return True
        
        # Handle buttons
        if self.assign_button.handle_event(event):
            return True
        if self.close_button_action.handle_event(event):
            return True
        
        # Call parent handler
        return super().handle_event(event)
