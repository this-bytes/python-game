"""Modal for inspecting and interacting with a single specialist.

Shows specialist details, stats, current assignments, and provides actions:
- Assign to Incident
- Change Level
- Edit Role
- Deactivate/Activate
"""

from typing import List, Any, Optional, Callable
from src.ui.modals.entity_modal import EntityModal, ActionButton
from src.models.specialist import Specialist


class SpecialistModal(EntityModal):
    """Modal for displaying and interacting with a specialist entity."""

    def __init__(
        self,
        specialist: Specialist,
        on_assign_clicked: Optional[Callable[[], None]] = None,
        on_promote_clicked: Optional[Callable[[], None]] = None,
        on_deactivate_clicked: Optional[Callable[[], None]] = None
    ):
        """Initialize specialist modal.
        
        Args:
            specialist: Specialist object to display
            on_assign_clicked: Callback when Assign is clicked
            on_promote_clicked: Callback when Promote is clicked
            on_deactivate_clicked: Callback when Deactivate is clicked
        """
        super().__init__(specialist.id, specialist.name)
        self.specialist = specialist
        
        self.on_assign_clicked = on_assign_clicked
        self.on_promote_clicked = on_promote_clicked
        self.on_deactivate_clicked = on_deactivate_clicked
    
    def get_body_sections(self) -> List[dict[str, Any]]:
        """Get specialist details sections.
        
        Returns:
            List of section dicts with specialist info
        """
        # Determine current status
        current_status = "Available"
        if self.specialist.assigned_incident_id:
            current_status = f"Assigned to incident {self.specialist.assigned_incident_id}"
        
        sections = [
            {
                "title": "Status",
                "items": [
                    {"label": "State", "value": current_status},
                    {"label": "Health", "value": "100%"},  # Placeholder - get from specialist health system
                ]
            },
            {
                "title": "Experience",
                "items": [
                    {"label": "Level", "value": str(self.specialist.level)},
                    {"label": "XP", "value": str(getattr(self.specialist, 'xp', 0))},
                    {"label": "Specialty", "value": getattr(self.specialist, 'specialty', 'Unspecialized')},
                ]
            },
            {
                "title": "Performance",
                "items": [
                    {"label": "Speed", "value": f"{getattr(self.specialist, 'speed', 100)}%"},
                    {"label": "Accuracy", "value": f"{getattr(self.specialist, 'accuracy', 100)}%"},
                    {"label": "Incidents Resolved", "value": str(getattr(self.specialist, 'incidents_resolved', 0))},
                ]
            },
        ]
        
        # Add burnout if present
        if hasattr(self.specialist, 'burnout'):
            sections.append({
                "title": "Well-being",
                "items": [
                    {"label": "Burnout", "value": f"{self.specialist.burnout_level:.0f}%"},
                ]
            })
        
        return sections
    
    def get_action_buttons(self) -> List[ActionButton]:
        """Get action buttons for specialist.
        
        Returns:
            List of ActionButton objects
        """
        # Determine if specialist is available
        is_available = not self.specialist.assigned_incident_id
        can_promote = self.specialist.level < 10  # Assume level cap is 10
        
        return [
            ActionButton(
                id="assign",
                label="Assign",
                color=(100, 150, 200),
                on_click=self.on_assign_clicked,
                enabled=is_available
            ),
            ActionButton(
                id="promote",
                label="Promote",
                color=(150, 200, 100),
                on_click=self.on_promote_clicked,
                enabled=can_promote
            ),
            ActionButton(
                id="deactivate",
                label="Deactivate",
                color=(200, 100, 100),
                on_click=self.on_deactivate_clicked,
                enabled=True
            ),
        ]
