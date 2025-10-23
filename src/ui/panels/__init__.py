"""Game Panels package.

Modern panel implementations for the main gameplay view.
These panels provide rich visual interfaces for core game mechanics.
"""

from src.ui.panels.specialist_roster_panel import SpecialistRosterPanel
from src.ui.panels.incident_queue_panel import IncidentQueuePanel
from src.ui.panels.workload_analytics_panel import WorkloadAnalyticsPanel
from src.ui.panels.staff_management_panel import StaffManagementPanel
from src.ui.panels.assignment_workflow_panel import AssignmentWorkflowPanel

__all__ = [
    'SpecialistRosterPanel',
    'IncidentQueuePanel',
    'WorkloadAnalyticsPanel',
    'StaffManagementPanel',
    'AssignmentWorkflowPanel',
]
