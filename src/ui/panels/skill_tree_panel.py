"""Skill tree UI panel for specialist progression.

This panel displays skill trees for specialists, allowing players to view
available skills, unlock new abilities, and track progression.
"""

import pygame
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass

from src.ui.components.panel import Panel
from src.core.skill_tree_system import SkillTreeSystem, SkillTree, Skill, SkillTier
from src.models.specialist import Specialist
from src.core.plugins.skill_tree_plugin import SkillTreePlugin


@dataclass
class SkillDisplayData:
    """Data for displaying a skill in the UI."""
    skill: Skill
    can_unlock: bool
    is_unlocked: bool
    position: Tuple[int, int]
    tier: int

    @classmethod
    def from_skill(
        cls,
        skill: Skill,
        specialist: Specialist,
        skill_tree_system: SkillTreeSystem,
        position: Tuple[int, int],
        tier: int
    ) -> 'SkillDisplayData':
        """Create display data from a skill.

        Args:
            skill: The skill to display
            specialist: The specialist who owns the skill tree
            skill_tree_system: The skill tree system
            position: Position to display the skill
            tier: The tier this skill belongs to

        Returns:
            SkillDisplayData for UI rendering
        """
        can_unlock = skill_tree_system.can_unlock_skill(specialist, skill.id)
        is_unlocked = skill.id in [s.id for s in skill_tree_system.get_unlocked_skills(specialist)]

        return cls(
            skill=skill,
            can_unlock=can_unlock,
            is_unlocked=is_unlocked,
            position=position,
            tier=tier
        )


class SkillTreePanel(Panel):
    """Panel for displaying and managing specialist skill trees."""

    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize the skill tree panel.

        Args:
            x: Panel x position
            y: Panel y position
            width: Panel width
            height: Panel height
        """
        super().__init__(
            "Skill Trees",
            (x, y),
            (width, height)
        )
        self._skill_tree_system: Optional[SkillTreeSystem] = None
        self._current_specialist: Optional[Specialist] = None
        self._skill_display_data: List[SkillDisplayData] = []
        self._selected_skill: Optional[Skill] = None

        # Layout constants
        self._tier_height = 80
        self._skill_spacing = 120
        self._skill_size = 60
        self._tier_spacing = 100

        # Colors
        self._colors = {
            'locked': (100, 100, 100),      # Gray
            'available': (255, 255, 0),     # Yellow
            'unlocked': (0, 255, 0),        # Green
            'selected': (0, 0, 255),        # Blue
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'light_gray': (200, 200, 200),
            'dark_gray': (50, 50, 50)
        }

    def set_skill_tree_system(self, skill_tree_system: SkillTreeSystem) -> None:
        """Set the skill tree system for this panel.

        Args:
            skill_tree_system: The skill tree system to use
        """
        self._skill_tree_system = skill_tree_system

    def set_specialist(self, specialist: Specialist) -> None:
        """Set the specialist whose skill tree to display.

        Args:
            specialist: The specialist to display skills for
        """
        self._current_specialist = specialist
        self._selected_skill = None
        self._update_skill_display_data()

    def _update_skill_display_data(self) -> None:
        """Update the skill display data for the current specialist."""
        if not self._skill_tree_system or not self._current_specialist:
            self._skill_display_data = []
            return

        skill_tree = self._skill_tree_system.get_skill_tree(self._current_specialist.specialty)
        if not skill_tree:
            self._skill_display_data = []
            return

        display_data = []
        start_y = 60  # Start below the title

        for tier_idx, tier in enumerate(skill_tree.tiers):
            tier_y = start_y + tier_idx * (self._tier_height + self._tier_spacing)
            skills_in_tier = len(tier.skills)

            # Center skills horizontally in the tier
            total_width = (skills_in_tier - 1) * self._skill_spacing
            start_x = (self.size[0] - total_width) // 2

            for skill_idx, skill in enumerate(tier.skills):
                skill_x = start_x + skill_idx * self._skill_spacing
                position = (skill_x, tier_y)

                skill_data = SkillDisplayData.from_skill(
                    skill, self._current_specialist, self._skill_tree_system, position, tier_idx
                )
                display_data.append(skill_data)

        self._skill_display_data = display_data

    def render(self, screen: pygame.Surface) -> None:
        """Render the skill tree panel.

        Args:
            screen: The surface to render to
        """
        # Render background
        super().render(screen)

        if not self._current_specialist:
            self._render_no_specialist_selected(screen)
            return

        if not self._skill_tree_system:
            self._render_no_system(screen)
            return

        # Render specialist info
        self._render_specialist_info(screen)

        # Render skill tree
        self._render_skill_tree(screen)

        # Render skill details
        if self._selected_skill:
            self._render_skill_details(screen)

    def _render_no_specialist_selected(self, screen: pygame.Surface) -> None:
        """Render message when no specialist is selected.

        Args:
            screen: The surface to render to
        """
        font = pygame.font.Font(None, 24)
        text = font.render("Select a specialist to view their skill tree", True, self._colors['white'])
        text_rect = text.get_rect(center=(self.position[0] + self.size[0] // 2, self.position[1] + self.size[1] // 2))
        screen.blit(text, text_rect)

    def _render_no_system(self, screen: pygame.Surface) -> None:
        """Render message when skill tree system is not available.

        Args:
            screen: The surface to render to
        """
        font = pygame.font.Font(None, 24)
        text = font.render("Skill tree system not available", True, self._colors['red'])
        text_rect = text.get_rect(center=(self.position[0] + self.size[0] // 2, self.position[1] + self.size[1] // 2))
        screen.blit(text, text_rect)

    def _render_specialist_info(self, screen: pygame.Surface) -> None:
        """Render specialist information at the top of the panel.

        Args:
            screen: The surface to render to
        """
        if not self._current_specialist:
            return

        font = pygame.font.Font(None, 20)

        # Specialist name and specialty
        name_text = font.render(
            f"{self._current_specialist.name} - {self._current_specialist.specialty}",
            True, self._colors['white']
        )
        screen.blit(name_text, (self.position[0] + 10, self.position[1] + 30))

        # Level and skill points
        level_text = font.render(
            f"Level {self._current_specialist.level} | Skill Points: {self._current_specialist.skill_points}",
            True, self._colors['available']
        )
        screen.blit(level_text, (self.position[0] + 10, self.position[1] + 50))

    def _render_skill_tree(self, screen: pygame.Surface) -> None:
        """Render the skill tree visualization.

        Args:
            screen: The surface to render to
        """
        for skill_data in self._skill_display_data:
            self._render_skill_node(screen, skill_data)

            # Render connections to prerequisite skills
            self._render_skill_connections(screen, skill_data)

    def _render_skill_node(self, screen: pygame.Surface, skill_data: SkillDisplayData) -> None:
        """Render a single skill node.

        Args:
            screen: The surface to render to
            skill_data: The skill display data
        """
        x, y = skill_data.position
        x += self.position[0]
        y += self.position[1]

        # Determine color based on skill state
        if skill_data.is_unlocked:
            color = self._colors['unlocked']
        elif skill_data.can_unlock:
            color = self._colors['available']
        else:
            color = self._colors['locked']

        if skill_data.skill == self._selected_skill:
            color = self._colors['selected']

        # Draw skill node (circle)
        pygame.draw.circle(screen, color, (x + self._skill_size // 2, y + self._skill_size // 2), self._skill_size // 2)

        # Draw skill icon or letter
        font = pygame.font.Font(None, 24)
        icon_text = skill_data.skill.icon if skill_data.skill.icon else skill_data.skill.name[0]
        text = font.render(icon_text, True, self._colors['black'])
        text_rect = text.get_rect(center=(x + self._skill_size // 2, y + self._skill_size // 2))
        screen.blit(text, text_rect)

        # Draw skill cost if not unlocked
        if not skill_data.is_unlocked:
            cost_font = pygame.font.Font(None, 16)
            cost_text = cost_font.render(str(skill_data.skill.cost), True, self._colors['white'])
            screen.blit(cost_text, (x + self._skill_size + 5, y + 5))

    def _render_skill_connections(self, screen: pygame.Surface, skill_data: SkillDisplayData) -> None:
        """Render connections from this skill to its prerequisites.

        Args:
            screen: The surface to render to
            skill_data: The skill display data
        """
        if not skill_data.skill.prerequisites:
            return

        start_x = skill_data.position[0] + self.position[0] + self._skill_size // 2
        start_y = skill_data.position[1] + self.position[1] + self._skill_size // 2

        for prereq_id in skill_data.skill.prerequisites:
            # Find the prerequisite skill's position
            prereq_data = next(
                (sd for sd in self._skill_display_data if sd.skill.id == prereq_id),
                None
            )
            if prereq_data:
                end_x = prereq_data.position[0] + self.position[0] + self._skill_size // 2
                end_y = prereq_data.position[1] + self.position[1] + self._skill_size // 2

                # Draw line from current skill to prerequisite
                pygame.draw.line(screen, self._colors['locked'], (start_x, start_y), (end_x, end_y), 2)

    def _render_skill_details(self, screen: pygame.Surface) -> None:
        """Render detailed information about the selected skill.

        Args:
            screen: The surface to render to
        """
        if not self._selected_skill:
            return

        # Draw details panel on the right side
        details_x = self.position[0] + self.size[0] - 250
        details_y = self.position[1] + 30
        details_width = 240
        details_height = self.size[1] - 40

        # Background
        pygame.draw.rect(screen, self._colors['dark_gray'], (details_x, details_y, details_width, details_height))
        pygame.draw.rect(screen, self._colors['white'], (details_x, details_y, details_width, details_height), 1)

        # Skill name
        font = pygame.font.Font(None, 20)
        name_text = font.render(self._selected_skill.name, True, self._colors['white'])
        screen.blit(name_text, (details_x + 10, details_y + 10))

        # Skill description
        desc_font = pygame.font.Font(None, 16)
        desc_lines = self._wrap_text(self._selected_skill.description, desc_font, details_width - 20)
        for i, line in enumerate(desc_lines):
            desc_text = desc_font.render(line, True, self._colors['light_gray'])
            screen.blit(desc_text, (details_x + 10, details_y + 35 + i * 20))

        # Prerequisites
        if self._selected_skill.prerequisites:
            prereq_text = desc_font.render("Prerequisites:", True, self._colors['available'])
            screen.blit(prereq_text, (details_x + 10, details_y + 80))

            for i, prereq_id in enumerate(self._selected_skill.prerequisites):
                # Find prerequisite skill name
                prereq_skill = next(
                    (sd.skill for sd in self._skill_display_data if sd.skill.id == prereq_id),
                    None
                )
                prereq_name = prereq_skill.name if prereq_skill else prereq_id
                prereq_line = desc_font.render(f"• {prereq_name}", True, self._colors['light_gray'])
                screen.blit(prereq_line, (details_x + 20, details_y + 100 + i * 20))

        # Cost and unlock status
        y_offset = details_y + 140
        if self._selected_skill.prerequisites:
            y_offset += len(self._selected_skill.prerequisites) * 20

        cost_text = desc_font.render(f"Cost: {self._selected_skill.cost} skill points", True, self._colors['white'])
        screen.blit(cost_text, (details_x + 10, y_offset))

        # Unlock button or status
        if self._skill_tree_system and self._current_specialist:
            can_unlock = self._skill_tree_system.can_unlock_skill(
                self._current_specialist, self._selected_skill.id
            )
            is_unlocked = self._selected_skill.id in [
                s.id for s in self._skill_tree_system.get_unlocked_skills(self._current_specialist)
            ]

            if is_unlocked:
                status_text = desc_font.render("✓ Unlocked", True, self._colors['unlocked'])
            elif can_unlock:
                status_text = desc_font.render("Click to unlock", True, self._colors['available'])
            else:
                status_text = desc_font.render("Locked", True, self._colors['red'])

            screen.blit(status_text, (details_x + 10, y_offset + 25))

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Wrap text to fit within a maximum width.

        Args:
            text: The text to wrap
            font: The font to use for measuring
            max_width: Maximum width in pixels

        Returns:
            List of text lines
        """
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Handle mouse click events.

        Args:
            pos: Mouse position

        Returns:
            True if the click was handled, False otherwise
        """
        if not self.contains_point(pos):
            return False

        # Check if clicking on a skill node
        for skill_data in self._skill_display_data:
            skill_rect = pygame.Rect(
                skill_data.position[0] + self.position[0],
                skill_data.position[1] + self.position[1],
                self._skill_size,
                self._skill_size
            )

            if skill_rect.collidepoint(pos):
                self._selected_skill = skill_data.skill

                # Try to unlock the skill if it's available
                if (skill_data.can_unlock and self._skill_tree_system and self._current_specialist):
                    success = self._skill_tree_system.unlock_skill(
                        self._current_specialist, skill_data.skill.id
                    )
                    if success:
                        self._update_skill_display_data()  # Refresh display

                return True

        # Check if clicking in details panel (deselect)
        details_x = self.position[0] + self.size[0] - 250
        if pos[0] >= details_x:
            self._selected_skill = None
            return True

        return False

    def update_panel(self, game_state: Any) -> None:
        """Update the panel with current game state.

        Args:
            game_state: Current game state
        """
        # Find the skill tree system if not already found
        if not self._skill_tree_system:
            for system in game_state._systems.values():
                if isinstance(system, SkillTreePlugin):
                    self._skill_tree_system = system.get_skill_tree_system()
                    break

        # Update skill display data if we have a specialist
        if self._current_specialist:
            self._update_skill_display_data()