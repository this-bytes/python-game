"""Modal for selecting an incident to assign a specialist to.

Used as part of modal chain:
1. User views Specialist modal
2. Clicks "Assign" button
3. IncidentSelector modal opens showing available incidents
4. User selects incident
5. Assignment happens, modal closes
"""

from typing import List, Any, Optional, Callable
from src.ui.modals.entity_modal import EntityModal, ActionButton


class IncidentSelectorModal(EntityModal):
    """Modal for selecting an incident from available unassigned incidents."""

    def __init__(
        self,
        available_incidents: List[Any],
        specialist_id: str,
        on_incident_selected: Optional[Callable[[str], None]] = None,
    ):
        """Initialize incident selector modal.
        
        Args:
            available_incidents: List of incident objects that can be assigned
            specialist_id: ID of specialist being assigned
            on_incident_selected: Callback when incident is selected (receives incident_id)
        """
        super().__init__("selector", f"Select Incident for Assignment")
        self.available_incidents = available_incidents
        self.specialist_id = specialist_id
        self.on_incident_selected = on_incident_selected
        self.selected_incident_id: Optional[str] = None
    
    def get_body_sections(self) -> List[dict[str, Any]]:
        """Get list of available incidents to select from.
        
        Returns:
            List of section dicts with incident options
        """
        if not self.available_incidents:
            return [{
                "title": "Available Incidents",
                "items": [
                    {"label": "Status", "value": "No incidents available"},
                ]
            }]
        
        # Group incidents by priority
        incidents_by_priority = {
            "Critical": [],
            "High": [],
            "Medium": [],
            "Low": [],
        }
        
        for incident in self.available_incidents:
            priority = getattr(incident, 'priority', 'Medium')
            if priority not in incidents_by_priority:
                incidents_by_priority['Medium'].append(incident)
            else:
                incidents_by_priority[priority].append(incident)
        
        sections = []
        for priority in ["Critical", "High", "Medium", "Low"]:
            incidents = incidents_by_priority[priority]
            if not incidents:
                continue
            
            items = []
            for incident in incidents:
                incident_id = getattr(incident, 'id', 'unknown')
                incident_name = getattr(incident, 'name', 'Unknown')
                difficulty = getattr(incident, 'difficulty', 0)
                
                # Format: "Name (Difficulty X)"
                label = f"{incident_name} (Diff {difficulty})"
                items.append({
                    "label": label,
                    "value": incident_id,
                    "is_selectable": True,
                    "is_selected": incident_id == self.selected_incident_id,
                })
            
            if items:
                sections.append({
                    "title": f"{priority} Priority",
                    "items": items,
                })
        
        return sections
    
    def get_action_buttons(self) -> List[ActionButton]:
        """Get action buttons for incident selection.
        
        Returns:
            List of ActionButton objects
        """
        can_confirm = self.selected_incident_id is not None
        
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
        """Handle input events including incident selection.
        
        Args:
            event: Pygame event
            
        Returns:
            True to keep modal open, False to close
        """
        # Call parent to handle standard modal events (close button, etc.)
        should_stay_open = super().handle_event(event)
        
        if not should_stay_open:
            return False
        
        # Handle custom incident selection (would be implemented in rendering layer)
        # For now, just return True to keep modal open
        return True
    
    def select_incident(self, incident_id: str) -> None:
        """Select an incident from the list.
        
        Args:
            incident_id: ID of incident to select
        """
        # Verify incident exists in available list
        for incident in self.available_incidents:
            if getattr(incident, 'id', None) == incident_id:
                self.selected_incident_id = incident_id
                return
    
    def _on_confirm(self) -> None:
        """Handle confirm button click."""
        if self.selected_incident_id and self.on_incident_selected:
            self.on_incident_selected(self.selected_incident_id)
