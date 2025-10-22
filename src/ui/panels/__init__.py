"""Game Panels package.

Modern panel implementations for the main gameplay view.
These panels provide rich visual interfaces for core game mechanics.
"""

from src.ui.panels.specialist_roster_panel import SpecialistRosterPanel
from src.ui.panels.incident_queue_panel import IncidentQueuePanel

__all__ = [
    'SpecialistRosterPanel',
    'IncidentQueuePanel',
]
