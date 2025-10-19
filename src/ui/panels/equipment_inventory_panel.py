"""Equipment Inventory Panel for managing specialist equipment."""

import pygame
from typing import Optional, Any, List, Dict, Tuple
from src.ui.components.panel import Panel
from src.ui.components.scroll_container import ScrollContainer
from src.ui.components.button import Button
from src.ui.components.tooltip import Tooltip
from src.models.game_state import GameState
from src.models.equipment import Equipment
from src.models.specialist import Specialist


class EquipmentInventoryPanel(Panel):
    """Inventory panel for managing specialist equipment."""

    def __init__(self, game_state: GameState):
        """Initialize equipment inventory panel.

        Args:
            game_state: Game state reference
        """
        # Position accounts for navigation menu (200px) + shop panel (380px) + margins (40px)
        # ViewManager will reposition based on current view
        super().__init__(
            title="Equipment Inventory",
            position=(640, 80),
            size=(420, 600),
            closeable=True,
            minimizable=True,
            draggable=True,
        )
        self.game_state = game_state
        self.scroll_container = ScrollContainer(
            position=(0, 0),
            size=(440, 468),
            content_height=0
        )

        # Selection state
        self.selected_specialist: Optional[Specialist] = None
        self.selected_slot: Optional[str] = None

        # Tooltips
        self.equipment_tooltips: Dict[str, Tooltip] = {}
        self.current_tooltip: Optional[Tooltip] = None

        # Rarity colors
        self.rarity_colors = {
            "common": (150, 150, 150),
            "rare": (0, 150, 255),
            "epic": (150, 0, 255),
            "legendary": (255, 150, 0)
        }

        # Equipment type icons
        self.type_icons = {
            "tool": "🔧",
            "badge": "🏷️",
            "peripheral": "⌨️"
        }

        # Slot names
        self.slot_names = {
            "tool": "Tool",
            "badge": "Badge",
            "peripheral": "Peripheral"
        }

    def render(self, screen: pygame.Surface):
        """Render the equipment inventory panel.

        Args:
            screen: Pygame surface to render to
        """
        # Render base panel
        super().render(screen)

        if not self.visible:
            return

        # Render specialist selector
        self._render_specialist_selector(screen)

        # Render equipment slots
        self._render_equipment_slots(screen)

        # Render inventory
        self._render_inventory(screen)

        # Render tooltip if active
        if self.current_tooltip:
            self.current_tooltip.render(screen)

    def _create_equipment_tooltip(self, equipment: Equipment) -> Tooltip:
        """Create a detailed tooltip for equipment.

        Args:
            equipment: Equipment to create tooltip for

        Returns:
            Tooltip instance with equipment details
        """
        lines = [
            f"{equipment.name}",
            f"Type: {equipment.equipment_type.title()}",
            f"Rarity: {equipment.rarity.title()}",
            "",
            "Stat Bonuses:"
        ]

        # Add stat bonuses
        for stat, bonus in equipment.stat_bonuses.items():
            stat_name = stat.replace('_', ' ').title()
            if isinstance(bonus, float) and bonus != int(bonus):
                lines.append(f"  {stat_name}: +{bonus:.1f}")
            else:
                lines.append(f"  {stat_name}: +{int(bonus)}")

        # Add upgrade info if applicable
        if self.game_state._equipment_system and self._can_upgrade_equipment(equipment):
            requirements = self.game_state._equipment_system.get_upgrade_requirements(equipment)
            lines.extend([
                "",
                f"Upgrade: {requirements['target_rarity'].title()}",
                f"Requires: {requirements['required_count']} pieces",
                f"Cost: ${requirements['upgrade_cost']:,}"
            ])

        tooltip_text = "\n".join(lines)
        return Tooltip(tooltip_text, delay=0.3)

    def _update_tooltips(self, mouse_pos: Tuple[int, int], rel_pos: Tuple[int, int]) -> None:
        """Update tooltip state based on mouse position.

        Args:
            mouse_pos: Absolute mouse position
            rel_pos: Relative mouse position within panel
        """
        # Check inventory items for hover
        inventory_items = self._get_inventory_items()
        hovered_equipment = None

        for i, equipment in enumerate(inventory_items):
            item_y = 320 + i * 60 - self.scroll_container.scroll_offset
            if item_y <= rel_pos[1] <= item_y + 50 and 10 <= rel_pos[0] <= self.rect.width - 20:
                hovered_equipment = equipment
                break

        # Update tooltip
        if hovered_equipment:
            tooltip_key = hovered_equipment.id
            if tooltip_key not in self.equipment_tooltips:
                self.equipment_tooltips[tooltip_key] = self._create_equipment_tooltip(hovered_equipment)

            self.current_tooltip = self.equipment_tooltips[tooltip_key]
            self.current_tooltip.update(1/60, mouse_pos, True)  # Assume 60 FPS
        else:
            if self.current_tooltip:
                self.current_tooltip.update(1/60, mouse_pos, False)
            self.current_tooltip = None

    def _render_specialist_selector(self, screen: pygame.Surface):
        """Render specialist selection dropdown.

        Args:
            screen: Pygame surface to render to
        """
        # Specialist selector background
        pygame.draw.rect(screen, (70, 70, 70), (10, 35, self.rect.width - 20, 30))

        # Selected specialist name
        specialist_name = "Select Specialist"
        if self.selected_specialist:
            specialist_name = self.selected_specialist.name

        self._render_text(screen, specialist_name, (20, 50), (255, 255, 255), 14)

        # Dropdown arrow
        pygame.draw.polygon(screen, (200, 200, 200), [
            (self.rect.width - 25, 45),
            (self.rect.width - 15, 45),
            (self.rect.width - 20, 55)
        ])

    def _render_equipment_slots(self, screen: pygame.Surface):
        """Render equipment slots for selected specialist.

        Args:
            screen: Pygame surface to render to
        """
        if not self.selected_specialist:
            self._render_text(screen, "Select a specialist to view equipment",
                            (self.rect.centerx, 100), (150, 150, 150), 14, center=True)
            return

        y_offset = 80
        for slot_type in ["tool", "badge", "peripheral"]:
            self._render_equipment_slot(screen, slot_type, 10, y_offset)
            y_offset += 70

    def _render_equipment_slot(self, screen: pygame.Surface, slot_type: str, x: int, y: int):
        """Render a single equipment slot.

        Args:
            screen: Pygame surface to render to
            slot_type: Type of equipment slot
            x: X position
            y: Y position
        """
        slot_width = self.rect.width - 20
        slot_height = 60

        # Slot background
        is_selected = self.selected_slot == slot_type
        bg_color = (100, 100, 100) if is_selected else (60, 60, 60)
        pygame.draw.rect(screen, bg_color, (x, y, slot_width, slot_height))

        # Slot border
        border_color = (255, 255, 255) if is_selected else (150, 150, 150)
        pygame.draw.rect(screen, border_color, (x, y, slot_width, slot_height), 2)

        # Slot name
        slot_name = self.slot_names.get(slot_type, slot_type.title())
        self._render_text(screen, slot_name, (x + 10, y + 8), (255, 255, 255), 14)

        # Equipped equipment
        equipped_equipment = None
        if self.selected_specialist and slot_type in self.selected_specialist.equipped_items:
            equipment_id = self.selected_specialist.equipped_items[slot_type]
            if self.game_state._equipment_system:
                equipped_equipment = self.game_state._equipment_system.equipment_catalog.get(equipment_id)

        if equipped_equipment:
            # Equipment name and rarity
            name_text = f"{self.type_icons.get(equipped_equipment.equipment_type.lower(), '❓')} {equipped_equipment.name}"
            self._render_text(screen, name_text, (x + 10, y + 25), (255, 255, 255), 12)

            # Rarity badge
            rarity_color = self.rarity_colors.get(equipped_equipment.rarity.lower(), (100, 100, 100))
            pygame.draw.rect(screen, rarity_color, (x + slot_width - 80, y + 8, 70, 20))
            self._render_text(screen, equipped_equipment.rarity.upper(),
                            (x + slot_width - 45, y + 18), (0, 0, 0), 10, center=True)

            # Stat bonuses
            bonuses_text = self._format_stat_bonuses(equipped_equipment.stat_bonuses)
            self._render_text(screen, bonuses_text, (x + 10, y + 40), (150, 255, 150), 10)

            # Unequip button
            pygame.draw.rect(screen, (150, 0, 0), (x + slot_width - 60, y + 35, 50, 20))
            self._render_text(screen, "UNEQUIP", (x + slot_width - 35, y + 45),
                            (255, 255, 255), 10, center=True)
        else:
            # Empty slot
            self._render_text(screen, "Empty", (x + 10, y + 25), (150, 150, 150), 12)

            # Equip button (placeholder)
            pygame.draw.rect(screen, (0, 100, 0), (x + slot_width - 60, y + 35, 50, 20))
            self._render_text(screen, "EQUIP", (x + slot_width - 35, y + 45),
                            (255, 255, 255), 10, center=True)

    def _render_inventory(self, screen: pygame.Surface):
        """Render specialist's equipment inventory.

        Args:
            screen: Pygame surface to render to
        """
        if not self.selected_specialist:
            return

        # Inventory header
        self._render_text(screen, "Inventory", (10, 290), (255, 255, 255), 16)

        # Get inventory items
        inventory_items = []
        if self.game_state._equipment_system:
            for equipment_id in self.selected_specialist.inventory:
                equipment = self.game_state._equipment_system.equipment_catalog.get(equipment_id)
                if equipment:
                    inventory_items.append(equipment)

        # Sort by rarity, then type
        rarity_order = {"common": 0, "rare": 1, "epic": 2, "legendary": 3}
        inventory_items.sort(key=lambda eq: (rarity_order.get(eq.rarity.lower(), 0), eq.equipment_type, eq.name))

        # Calculate content height
        self.scroll_container.content_height = max(0, len(inventory_items) * 60 - 200)

        # Render inventory items
        for i, equipment in enumerate(inventory_items):
            item_y = 320 + i * 60 - self.scroll_container.scroll_offset
            if item_y < 300 or item_y > self.rect.height:
                continue  # Skip off-screen items

            self._render_inventory_item(screen, equipment, 10, item_y)

    def _render_inventory_item(self, screen: pygame.Surface, equipment: Equipment, x: int, y: int):
        """Render an inventory item.

        Args:
            screen: Pygame surface to render to
            equipment: Equipment to render
            x: X position
            y: Y position
        """
        item_width = self.rect.width - 20
        item_height = 50

        # Item background with rarity border
        rarity_color = self.rarity_colors.get(equipment.rarity.lower(), (100, 100, 100))
        pygame.draw.rect(screen, rarity_color, (x, y, item_width, item_height), 2)
        pygame.draw.rect(screen, (50, 50, 50), (x + 2, y + 2, item_width - 4, item_height - 4))

        # Equipment name and type
        name_text = f"{self.type_icons.get(equipment.equipment_type.lower(), '❓')} {equipment.name}"
        self._render_text(screen, name_text, (x + 10, y + 8), (255, 255, 255), 12)

        # Rarity badge
        pygame.draw.rect(screen, rarity_color, (x + item_width - 80, y + 6, 70, 18))
        self._render_text(screen, equipment.rarity.upper(),
                         (x + item_width - 45, y + 15), (0, 0, 0), 9, center=True)

        # Stat bonuses
        bonuses_text = self._format_stat_bonuses(equipment.stat_bonuses)
        self._render_text(screen, bonuses_text, (x + 10, y + 25), (150, 255, 150), 10)

        # Equip button
        can_equip = self._can_equip_equipment(equipment)
        button_color = (0, 150, 0) if can_equip else (100, 100, 100)
        pygame.draw.rect(screen, button_color, (x + item_width - 60, y + 30, 50, 18))
        button_text = "EQUIP" if can_equip else "CAN'T"
        self._render_text(screen, button_text, (x + item_width - 35, y + 39),
                         (255, 255, 255), 9, center=True)

        # Upgrade button (if upgradable)
        can_upgrade = self._can_upgrade_equipment(equipment)
        if can_upgrade:
            upgrade_color = (255, 150, 0)  # Orange for upgrade
            pygame.draw.rect(screen, upgrade_color, (x + item_width - 115, y + 30, 50, 18))
            self._render_text(screen, "UPGRADE", (x + item_width - 90, y + 39),
                             (0, 0, 0), 8, center=True)

    def _can_equip_equipment(self, equipment: Equipment) -> bool:
        """Check if equipment can be equipped by selected specialist.

        Args:
            equipment: Equipment to check

        Returns:
            True if can be equipped
        """
        if not self.selected_specialist:
            return False

        slot_type = equipment.equipment_type.lower()

        # Check if slot is available (not occupied by different equipment)
        if slot_type in self.selected_specialist.equipped_items:
            equipped_id = self.selected_specialist.equipped_items[slot_type]
            # Can equip if it's the same equipment (no-op) or different equipment
            return True

        return True

    def _can_upgrade_equipment(self, equipment: Equipment) -> bool:
        """Check if equipment can be upgraded.

        Args:
            equipment: Equipment to check

        Returns:
            True if equipment can be upgraded
        """
        if not self.game_state._equipment_system:
            return False
        
        return self.game_state._equipment_system.can_upgrade_equipment(equipment)

    def _attempt_upgrade(self, equipment: Equipment) -> None:
        """Attempt to upgrade equipment.

        Args:
            equipment: Equipment to upgrade
        """
        if not self.game_state._equipment_system:
            return
        
        # Get upgrade requirements
        requirements = self.game_state._equipment_system.get_upgrade_requirements(equipment)
        required_count = requirements["required_count"]
        upgrade_cost = requirements["upgrade_cost"]
        
        # Count how many of this equipment type/rarity we have
        inventory_count = 0
        equipment_ids_to_upgrade = []
        
        for eq_id in self.game_state.specialists[0].inventory:  # Use first specialist's inventory as reference
            eq = self.game_state._equipment_system.get_equipment(eq_id)
            if (eq and eq.equipment_type == equipment.equipment_type and 
                eq.rarity == equipment.rarity):
                inventory_count += 1
                equipment_ids_to_upgrade.append(eq_id)
                if inventory_count >= required_count:
                    break
        
        if inventory_count < required_count:
            # Show feedback that not enough equipment
            return
        
        if self.game_state.current_money < upgrade_cost:
            # Show feedback that not enough money
            return
        
        # Perform upgrade
        upgraded_equipment = self.game_state._equipment_system.upgrade_equipment(
            equipment_ids_to_upgrade[:required_count]
        )
        
        if upgraded_equipment:
            # Remove old equipment and cost
            for eq_id in equipment_ids_to_upgrade[:required_count]:
                self.game_state.specialists[0].inventory.remove(eq_id)  # Remove from inventory
            self.game_state.current_money -= upgrade_cost
            
            # Add upgraded equipment
            self.game_state.specialists[0].inventory.append(upgraded_equipment.id)
            
            # Publish dopamine feedback event for upgrade
            if hasattr(self.game_state, '_dopamine_system') and self.game_state._dopamine_system:
                self.game_state._dopamine_system.add_feedback(
                    feedback_type="equipment_upgraded",
                    message=f"Upgraded: {upgraded_equipment.name}",
                    magnitude=2.0,
                    duration=2.0
                )

    def _format_stat_bonuses(self, stat_bonuses: Dict[str, float]) -> str:
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

        mouse_pos = pygame.mouse.get_pos()
        rel_pos = (mouse_pos[0] - self.rect.left, mouse_pos[1] - self.rect.top)

        # Update tooltips
        self._update_tooltips(mouse_pos, rel_pos)

        # Handle specialist selector click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # Specialist selector
            if 35 <= rel_pos[1] <= 65 and 10 <= rel_pos[0] <= self.rect.width - 10:
                self._show_specialist_dropdown()
                return True

            # Equipment slot clicks
            if self.selected_specialist:
                y_offset = 80
                for slot_type in ["tool", "badge", "peripheral"]:
                    if y_offset <= rel_pos[1] <= y_offset + 60:
                        self.selected_slot = slot_type

                        # Check for unequip button click
                        if (self.rect.width - 60 <= rel_pos[0] <= self.rect.width - 10 and
                            35 <= rel_pos[1] - y_offset <= 55):
                            self._unequip_from_slot(slot_type)

                        return True
                    y_offset += 70

            # Inventory item clicks
            inventory_items = self._get_inventory_items()
            for i, equipment in enumerate(inventory_items):
                item_y = 320 + i * 60 - self.scroll_container.scroll_offset
                if item_y <= rel_pos[1] <= item_y + 50:
                    # Check for upgrade button click (left button)
                    if (self.rect.width - 115 <= rel_pos[0] <= self.rect.width - 65 and
                        self._can_upgrade_equipment(equipment)):
                        self._attempt_upgrade(equipment)
                        return True
                    # Check for equip button click (right button)
                    elif self.rect.width - 60 <= rel_pos[0] <= self.rect.width - 10:
                        self._equip_equipment(equipment)
                        return True

        # Handle scrolling
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_container.scroll_offset = max(0, self.scroll_container.scroll_offset - 30)
                return True
            elif event.button == 5:  # Scroll down
                max_scroll = max(0, self.scroll_container.content_height - self.scroll_container.size[1] + 200)
                self.scroll_container.scroll_offset = min(max_scroll, self.scroll_container.scroll_offset + 30)
                return True

        return super().handle_event(event)

    def _get_inventory_items(self) -> List[Equipment]:
        """Get inventory items for selected specialist.

        Returns:
            List of equipment in inventory
        """
        if not self.selected_specialist or not self.game_state._equipment_system:
            return []

        inventory_items = []
        for equipment_id in self.selected_specialist.inventory:
            equipment = self.game_state._equipment_system.equipment_catalog.get(equipment_id)
            if equipment:
                inventory_items.append(equipment)

        return inventory_items

    def _show_specialist_dropdown(self):
        """Show specialist selection dropdown."""
        # For now, just cycle through specialists
        specialists = self.game_state.specialists
        if not specialists:
            return

        if self.selected_specialist is None:
            self.selected_specialist = specialists[0]
        else:
            current_index = specialists.index(self.selected_specialist)
            next_index = (current_index + 1) % len(specialists)
            self.selected_specialist = specialists[next_index]

    def _unequip_from_slot(self, slot_type: str):
        """Unequip equipment from a slot.

        Args:
            slot_type: Slot to unequip from
        """
        if not self.selected_specialist or not self.game_state._equipment_system:
            return

        unequipped = self.game_state._equipment_system.unequip_item(self.selected_specialist, slot_type)
        if unequipped:
            # Add feedback
            self.game_state.dopamine_feedback_queue.append({
                "type": "equipment_unequipped",
                "timestamp": pygame.time.get_ticks() / 1000.0,
                "equipment": unequipped,
                "specialist_id": self.selected_specialist.id
            })

    def _equip_equipment(self, equipment: Equipment):
        """Equip equipment to selected slot.

        Args:
            equipment: Equipment to equip
        """
        if not self.selected_specialist or not self.selected_slot or not self.game_state._equipment_system:
            return

        success = self.game_state._equipment_system.equip_item(self.selected_specialist, equipment)
        if success:
            # Add feedback
            self.game_state.dopamine_feedback_queue.append({
                "type": "equipment_equipped",
                "timestamp": pygame.time.get_ticks() / 1000.0,
                "equipment": equipment,
                "specialist_id": self.selected_specialist.id,
                "slot": self.selected_slot
            })

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