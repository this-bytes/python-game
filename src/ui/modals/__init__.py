"""UI Modal components for entity inspection and interaction.

Provides:
- EntityModal: Base class for all entity modals
- SpecialistModal: Specialist inspection and actions
- IncidentModal: Incident inspection and actions
- IncidentSelectorModal: Modal for selecting incidents in assignment chains
- ModalManager: Manages modal stacking and transitions
"""

from src.ui.modals.entity_modal import EntityModal, ActionButton
from src.ui.modals.specialist_modal import SpecialistModal
from src.ui.modals.incident_modal import IncidentModal
from src.ui.modals.incident_selector_modal import IncidentSelectorModal
from src.ui.modals.modal_manager import ModalManager

__all__ = [
    "EntityModal",
    "ActionButton",
    "SpecialistModal",
    "IncidentModal",
    "IncidentSelectorModal",
    "ModalManager",
]
