"""Modal for inspecting and interacting with a single incident.

Shows incident details, requirements, current status, and provides actions:
- Assign Specialist
- View Details
- Complete
"""

from typing import List, Any, Optional, Callable
from src.ui.modals.entity_modal import EntityModal, ActionButton
from src.models.incident import Incident


class IncidentModal(EntityModal):
    """Modal for displaying and interacting with an incident entity."""

    def __init__(
        self,
        incident: Incident,
        on_assign_clicked: Optional[Callable[[], None]] = None,
        on_complete_clicked: Optional[Callable[[], None]] = None,
    ):
        """Initialize incident modal.
        
        Args:
            incident: Incident object to display
            on_assign_clicked: Callback when Assign is clicked
            on_complete_clicked: Callback when Complete is clicked
        """
        super().__init__(incident.id, incident.name)
        self.incident = incident
        
        self.on_assign_clicked = on_assign_clicked
        self.on_complete_clicked = on_complete_clicked
    
    def get_body_sections(self) -> List[dict[str, Any]]:
        """Get incident details sections.
        
        Returns:
            List of section dicts with incident info
        """
        # Determine status
        is_assigned = hasattr(self.incident, 'assigned_specialist_id') and self.incident.assigned_specialist_id
        assigned_status = f"Assigned to {self.incident.assigned_specialist_id}" if is_assigned else "Unassigned"
        
        # Get time remaining if available
        time_remaining = getattr(self.incident, 'time_remaining_seconds', None)
        time_str = f"{int(time_remaining)}s" if time_remaining else "Unknown"
        
        sections = [
            {
                "title": "Assignment",
                "items": [
                    {"label": "Status", "value": assigned_status},
                    {"label": "Required Specialty", "value": getattr(self.incident, 'specialty_required', 'Any')},
                ]
            },
            {
                "title": "Details",
                "items": [
                    {"label": "Difficulty", "value": str(getattr(self.incident, 'difficulty', 0))},
                    {"label": "Priority", "value": getattr(self.incident, 'priority', 'Medium')},
                    {"label": "Type", "value": getattr(self.incident, 'incident_type', 'Unknown')},
                ]
            },
            {
                "title": "Response",
                "items": [
                    {"label": "SLA Remaining", "value": time_str},
                    {"label": "Time Limit", "value": f"{getattr(self.incident, 'sla_seconds', 300)}s"},
                    {"label": "Base Reward", "value": f"${getattr(self.incident, 'base_reward', 0)}"},
                ]
            },
        ]
        
        return sections
    
    def get_action_buttons(self) -> List[ActionButton]:
        """Get action buttons for incident.
        
        Returns:
            List of ActionButton objects
        """
        # Determine if incident is already assigned
        is_assigned = (
            hasattr(self.incident, 'assigned_specialist_id') 
            and self.incident.assigned_specialist_id is not None
            and bool(self.incident.assigned_specialist_id)
        )
        
        return [
            ActionButton(
                id="assign",
                label="Assign",
                color=(100, 150, 200),
                on_click=self.on_assign_clicked,
                enabled=not is_assigned
            ),
            ActionButton(
                id="complete",
                label="Complete",
                color=(150, 200, 100),
                on_click=self.on_complete_clicked,
                enabled=is_assigned
            ),
        ]
