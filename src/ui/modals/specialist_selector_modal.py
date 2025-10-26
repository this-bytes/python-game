"""Modal for selecting a specialist to assign to an incident.

Used as part of modal chain:
1. User views Incident modal
2. Clicks "Assign" button
3. SpecialistSelector modal opens showing available specialists
4. User selects specialist
5. Assignment happens, modal closes
"""

from typing import List, Any, Optional, Callable
from src.ui.modals.entity_modal import EntityModal, ActionButton


class SpecialistSelectorModal(EntityModal):
    """Modal for selecting a specialist from available specialists."""

    def __init__(
        self,
        available_specialists: List[Any],
        incident_id: str,
        on_specialist_selected: Optional[Callable[[str], None]] = None,
    ):
        """Initialize specialist selector modal.

        Args:
            available_specialists: List of specialist objects that can be assigned
            incident_id: ID of incident being assigned
            on_specialist_selected: Callback when specialist is selected (receives specialist_id)
        """
        super().__init__("selector", f"Select Specialist for Assignment")
        self.available_specialists = available_specialists
        self.incident_id = incident_id
        self.on_specialist_selected = on_specialist_selected
        self.selected_specialist_id: Optional[str] = None

    def get_body_sections(self) -> List[dict[str, Any]]:
        """Get list of available specialists to select from.

        Returns:
            List of section dicts with specialist options
        """
        if not self.available_specialists:
            return [{
                "title": "Available Specialists",
                "items": [
                    {"label": "Status", "value": "No specialists available"},
                ]
            }]

        # Group specialists by level (high -> low)
        by_level = {}
        for spec in self.available_specialists:
            level = getattr(spec, 'level', 1)
            by_level.setdefault(level, []).append(spec)

        sections = []
        for level in sorted(by_level.keys(), reverse=True):
            specs = by_level[level]
            items = []
            for spec in specs:
                spec_id = getattr(spec, 'id', 'unknown')
                spec_name = getattr(spec, 'name', 'Unnamed')
                specialty = getattr(spec, 'specialty', '')
                label = f"{spec_name} (Lvl {level}) - {specialty}"
                items.append({
                    "label": label,
                    "value": spec_id,
                    "is_selectable": True,
                    "is_selected": spec_id == self.selected_specialist_id,
                })

            sections.append({
                "title": f"Level {level}",
                "items": items,
            })

        return sections

    def get_action_buttons(self) -> List[ActionButton]:
        """Get action buttons for specialist selection."""
        can_confirm = self.selected_specialist_id is not None
        return [
            ActionButton(
                id="confirm",
                label="Confirm",
                color=(100, 200, 100),
                on_click=self._on_confirm,
                enabled=can_confirm
            ),
        ]

    def handle_event(self, event) -> bool:
        """Handle input events including specialist selection.

        For now defers to parent; selection handled in rendering layer via select_specialist.
        """
        should_stay_open = super().handle_event(event)
        if not should_stay_open:
            return False
        return True

    def select_specialist(self, specialist_id: str) -> None:
        """Select a specialist from the list.

        Args:
            specialist_id: ID of specialist to select
        """
        for spec in self.available_specialists:
            if getattr(spec, 'id', None) == specialist_id:
                self.selected_specialist_id = specialist_id
                return

    def _on_confirm(self) -> None:
        """Handle confirm button click."""
        if self.selected_specialist_id and self.on_specialist_selected:
            self.on_specialist_selected(self.selected_specialist_id)
