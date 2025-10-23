"""Integration test for Tab + Modal architecture.

Demonstrates:
1. TabBar navigation between major features
2. SpecialistModal inspection
3. IncidentModal inspection
4. Modal chains (Specialist -> Incident selector)
5. Modal stacking and transitions
6. Proper event routing and callbacks
"""

import sys
import pytest
from unittest.mock import Mock, MagicMock, patch
import pygame

# Initialize pygame once at module load
pygame.init()
pygame.display.set_mode((1280, 720))

# Import all modal and tab components
from src.ui.modals import (
    SpecialistModal, IncidentModal, IncidentSelectorModal, ModalManager
)
from src.ui.components.tab_bar import TabBar, Tab


class TestTabBarIntegration:
    """Test TabBar component functionality."""

    def test_tab_bar_creation_with_tabs(self):
        """Verify TabBar creates with proper tab definitions."""
        tabs = [
            Tab(id="dashboard", label="Dashboard", icon="📊"),
            Tab(id="operations", label="Operations", icon="⚙️"),
            Tab(id="incidents", label="Incidents", icon="🚨"),
        ]
        
        tab_bar = TabBar(y=10, tabs=tabs)
        
        assert tab_bar.get_active_tab() == "dashboard"
        assert len(tabs) == 3
        content_rect = tab_bar.get_content_area()
        assert content_rect.y == 50  # Height + y position
    
    def test_tab_bar_selection(self):
        """Verify tab selection changes active tab."""
        tabs = [
            Tab(id="tab1", label="Tab 1", icon="1️⃣"),
            Tab(id="tab2", label="Tab 2", icon="2️⃣"),
        ]
        
        callback_data = []
        def on_tab_selected(tab_id):
            callback_data.append(tab_id)
        
        tab_bar = TabBar(y=10, tabs=tabs, on_tab_selected=on_tab_selected)
        
        # Select tab 2
        tab_bar.select_tab("tab2")
        
        assert tab_bar.get_active_tab() == "tab2"
        assert "tab2" in callback_data


class TestEntityModalIntegration:
    """Test EntityModal and subclasses."""

    def test_specialist_modal_creation(self):
        """Verify SpecialistModal creates with proper structure."""
        specialist = Mock()
        specialist.id = "spec_001"
        specialist.name = "Alice Chen"
        specialist.level = 5
        specialist.xp = 2340
        specialist.specialty = "Network Security"
        specialist.speed = 95
        specialist.accuracy = 88
        specialist.incidents_resolved = 12
        specialist.current_incident = None
        specialist.burnout = 35
        
        modal = SpecialistModal(specialist)
        
        assert modal.entity_id == "spec_001"
        assert modal.entity_name == "Alice Chen"
        
        # Verify body sections
        sections = modal.get_body_sections()
        assert len(sections) > 0
        assert any("Level" in str(s) for s in sections)
        
        # Verify action buttons
        buttons = modal.get_action_buttons()
        button_ids = [b.id for b in buttons]
        assert "assign" in button_ids
        assert "promote" in button_ids
        assert "deactivate" in button_ids
    
    def test_incident_modal_creation(self):
        """Verify IncidentModal creates with proper structure."""
        incident = Mock()
        incident.id = "inc_001"
        incident.name = "DDoS Attack"
        incident.difficulty = 3
        incident.priority = "High"
        incident.incident_type = "DDoS"
        incident.specialty_required = "Network Security"
        incident.assigned_specialist_id = None
        incident.sla_seconds = 300
        incident.base_reward = 500
        incident.time_remaining_seconds = 250
        
        modal = IncidentModal(incident)
        
        assert modal.entity_id == "inc_001"
        assert modal.entity_name == "DDoS Attack"
        
        # Verify body sections
        sections = modal.get_body_sections()
        assert len(sections) > 0
        
        # Verify action buttons
        buttons = modal.get_action_buttons()
        button_ids = [b.id for b in buttons]
        assert "assign" in button_ids
        assert "complete" in button_ids
    
    def test_incident_selector_modal_creation(self):
        """Verify IncidentSelectorModal creates with incident list."""
        incidents = [
            Mock(id="inc_001", name="DDoS Attack", priority="High", difficulty=3),
            Mock(id="inc_002", name="Malware", priority="Critical", difficulty=4),
            Mock(id="inc_003", name="Phishing", priority="Low", difficulty=1),
        ]
        
        modal = IncidentSelectorModal(
            available_incidents=incidents,
            specialist_id="spec_001"
        )
        
        # Verify it's a modal
        assert modal.entity_id == "selector"
        
        # Get body sections (groups by priority)
        sections = modal.get_body_sections()
        assert len(sections) > 0
        
        # Select an incident
        modal.select_incident("inc_002")
        assert modal.selected_incident_id == "inc_002"


class TestModalManagerIntegration:
    """Test ModalManager for modal stacking and transitions."""

    def test_modal_manager_push_pop(self):
        """Verify ModalManager handles push/pop operations."""
        manager = ModalManager()
        
        specialist = Mock()
        specialist.id = "spec_001"
        specialist.name = "Alice"
        
        modal = SpecialistModal(specialist)
        
        # Should be empty initially
        assert manager.is_empty()
        assert not manager.has_active_modal()
        
        # Push modal
        manager.push_modal(modal)
        assert not manager.is_empty()
        assert manager.has_active_modal()
        assert manager.get_modal_count() == 1
        
        # Pop modal
        popped = manager.pop_modal()
        assert popped is modal
        assert manager.is_empty()
    
    def test_modal_manager_stack_depth(self):
        """Verify ModalManager tracks modal chains correctly."""
        manager = ModalManager()
        
        specialist = Mock()
        specialist.id = "spec_001"
        specialist.name = "Alice"
        specialist.current_incident = None
        specialist.level = 5
        
        incident = Mock()
        incident.id = "inc_001"
        incident.name = "DDoS"
        
        specialist_modal = SpecialistModal(specialist)
        incident_selector = IncidentSelectorModal([incident], "spec_001")
        
        # Stack modals (simulate modal chain)
        manager.push_modal(specialist_modal)
        assert manager.get_stack_depth() == 1
        assert not manager.can_go_back()
        
        manager.push_modal(incident_selector)
        assert manager.get_stack_depth() == 2
        assert manager.can_go_back()
    
    def test_modal_manager_replace_modal(self):
        """Verify ModalManager can replace modals (useful for modal chains)."""
        manager = ModalManager()
        
        specialist = Mock()
        specialist.id = "spec_001"
        specialist.name = "Alice"
        
        incident = Mock()
        incident.id = "inc_001"
        incident.name = "DDoS"
        
        modal1 = SpecialistModal(specialist)
        modal2 = IncidentModal(incident)
        
        # Push first modal
        manager.push_modal(modal1)
        assert manager.peek_modal() is modal1
        
        # Replace with second modal (modal chain transition)
        manager.replace_modal(modal2)
        assert manager.peek_modal() is modal2
        assert manager.get_modal_count() == 1
    
    def test_modal_manager_clear_all(self):
        """Verify ModalManager can clear all modals."""
        manager = ModalManager()
        
        specialist = Mock()
        specialist.id = "spec_001"
        specialist.name = "Alice"
        
        # Push multiple modals
        for i in range(3):
            modal = SpecialistModal(specialist)
            manager.push_modal(modal)
        
        assert manager.get_modal_count() == 3
        
        # Clear all
        manager.clear_all()
        assert manager.is_empty()
        assert manager.get_modal_count() == 0


class TestModalChainIntegration:
    """Test complete modal chains for workflows."""

    def test_specialist_assignment_chain(self):
        """Verify complete assignment workflow with modal chains.
        
        Flow:
        1. User views Specialist modal
        2. Clicks "Assign" button
        3. IncidentSelector modal opens
        4. User selects incident
        5. Assignment callback fires
        6. Modals close
        """
        manager = ModalManager()
        
        # Setup data
        specialist = Mock()
        specialist.id = "spec_001"
        specialist.name = "Alice Chen"
        specialist.level = 5
        specialist.current_incident = None
        
        incidents = [
            Mock(id="inc_001", name="DDoS Attack", priority="High", difficulty=3),
            Mock(id="inc_002", name="Malware", priority="Critical", difficulty=4),
        ]
        
        assignment_result = []
        
        def on_incident_selected(incident_id):
            """Callback when incident is selected."""
            assignment_result.append({
                "specialist_id": specialist.id,
                "incident_id": incident_id
            })
        
        # Step 1: Open specialist modal
        specialist_modal = SpecialistModal(specialist)
        manager.push_modal(specialist_modal)
        
        assert manager.get_stack_depth() == 1
        assert manager.peek_modal() is specialist_modal
        
        # Step 2: "Assign" button clicked - push incident selector
        incident_selector = IncidentSelectorModal(
            available_incidents=incidents,
            specialist_id=specialist.id,
            on_incident_selected=on_incident_selected
        )
        manager.push_modal(incident_selector)
        
        assert manager.get_stack_depth() == 2
        assert manager.can_go_back()
        
        # Step 3: Select incident
        incident_selector.select_incident("inc_001")
        assert incident_selector.selected_incident_id == "inc_001"
        
        # Step 4: Confirm selection
        incident_selector._on_confirm()
        assert len(assignment_result) == 1
        assert assignment_result[0]["incident_id"] == "inc_001"
        
        # Step 5: Close modal chain
        manager.pop_modal()
        manager.pop_modal()
        
        assert manager.is_empty()


class TestModalButtonStates:
    """Test action button states and enabling/disabling."""

    def test_specialist_modal_button_states(self):
        """Verify specialist modal buttons enable/disable correctly."""
        # Available specialist - all buttons enabled
        available_specialist = Mock()
        available_specialist.id = "spec_001"
        available_specialist.name = "Alice"
        available_specialist.level = 5
        available_specialist.current_incident = None
        
        modal = SpecialistModal(available_specialist)
        buttons = modal.get_action_buttons()
        
        assign_btn = next((b for b in buttons if b.id == "assign"), None)
        assert assign_btn is not None
        assert assign_btn.enabled is True
        
        # Assigned specialist - assign button disabled
        assigned_specialist = Mock()
        assigned_specialist.id = "spec_002"
        assigned_specialist.name = "Bob"
        assigned_specialist.level = 5
        assigned_specialist.current_incident = Mock(name="DDoS Attack")
        
        modal2 = SpecialistModal(assigned_specialist)
        buttons2 = modal2.get_action_buttons()
        
        assign_btn2 = next((b for b in buttons2 if b.id == "assign"), None)
        assert assign_btn2 is not None
        assert assign_btn2.enabled is False
    
    def test_incident_modal_button_states(self):
        """Verify incident modal buttons enable/disable correctly."""
        # Unassigned incident - assign button enabled, complete disabled
        unassigned_incident = Mock(spec=['id', 'name', 'assigned_specialist_id', 'difficulty', 'priority', 'incident_type', 'specialty_required', 'sla_seconds', 'base_reward', 'time_remaining_seconds'])
        unassigned_incident.id = "inc_001"
        unassigned_incident.name = "DDoS"
        unassigned_incident.assigned_specialist_id = None
        unassigned_incident.difficulty = 3
        unassigned_incident.priority = "High"
        unassigned_incident.incident_type = "DDoS"
        unassigned_incident.specialty_required = "Network Security"
        unassigned_incident.sla_seconds = 300
        unassigned_incident.base_reward = 500
        unassigned_incident.time_remaining_seconds = 250
        
        modal = IncidentModal(unassigned_incident)
        buttons = modal.get_action_buttons()
        
        assign_btn = next((b for b in buttons if b.id == "assign"), None)
        complete_btn = next((b for b in buttons if b.id == "complete"), None)
        assert assign_btn is not None
        assert assign_btn.enabled is True
        assert complete_btn is not None
        # Complete should be disabled when not assigned
        assert complete_btn.enabled is False or complete_btn.enabled is None or not complete_btn.enabled
        
        # Assigned incident - complete button should be enabled
        assigned_incident = Mock(spec=['id', 'name', 'assigned_specialist_id', 'difficulty', 'priority', 'incident_type', 'specialty_required', 'sla_seconds', 'base_reward', 'time_remaining_seconds'])
        assigned_incident.id = "inc_002"
        assigned_incident.name = "Malware"
        assigned_incident.assigned_specialist_id = "spec_001"
        assigned_incident.difficulty = 4
        assigned_incident.priority = "Critical"
        assigned_incident.incident_type = "Malware"
        assigned_incident.specialty_required = "Network Security"
        assigned_incident.sla_seconds = 300
        assigned_incident.base_reward = 500
        assigned_incident.time_remaining_seconds = 250
        
        modal2 = IncidentModal(assigned_incident)
        buttons2 = modal2.get_action_buttons()
        
        assign_btn2 = next((b for b in buttons2 if b.id == "assign"), None)
        complete_btn2 = next((b for b in buttons2 if b.id == "complete"), None)
        assert assign_btn2 is not None
        assert assign_btn2.enabled is False
        assert complete_btn2 is not None
        assert complete_btn2.enabled is True


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
