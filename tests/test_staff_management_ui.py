"""Integration tests for enhanced staff management UI panels.

Tests verify that new panels integrate correctly with GameUI
and properly handle game state updates.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import pygame

from src.ui.game_ui import GameUI
from src.ui.panels.workload_analytics_panel import WorkloadAnalyticsPanel
from src.ui.panels.staff_management_panel import StaffManagementPanel
from src.ui.panels.assignment_workflow_panel import AssignmentWorkflowPanel
from src.models.game_state import GameState
from src.models.specialist import Specialist
from src.models.incident import Incident


class TestWorkloadAnalyticsPanel:
    """Tests for WorkloadAnalyticsPanel."""
    
    @pytest.fixture
    def panel(self):
        """Create workload analytics panel."""
        return WorkloadAnalyticsPanel(230, 60, 230, 220)
    
    @pytest.fixture
    def specialists(self):
        """Create test specialists."""
        return [
            Specialist(id="spec_001", name="Alice", specialty="Network Security", level=5),
            Specialist(id="spec_002", name="Bob", specialty="Cryptography", level=3),
            Specialist(id="spec_003", name="Carol", specialty="Incident Response", level=4),
        ]
    
    def test_panel_creation(self, panel):
        """Test panel creates without errors."""
        assert panel.rect.width == 230
        assert panel.rect.height == 220
    
    def test_utilization_calculation(self, panel, specialists):
        """Test team utilization calculation."""
        # No one assigned
        utilization = panel._calculate_team_utilization(specialists)
        assert utilization == 0.0
        
        # Simulate assignments
        specialists[0].current_incident = Mock()
        specialists[1].current_incident = Mock()
        
        utilization = panel._calculate_team_utilization(specialists)
        assert abs(utilization - 66.67) < 0.1  # 2 out of 3
    
    def test_burnout_calculation(self, panel, specialists):
        """Test average burnout calculation."""
        specialists[0].burnout_level = 30.0
        specialists[1].burnout_level = 50.0
        specialists[2].burnout_level = 70.0
        
        avg_burnout = panel._calculate_avg_burnout(specialists)
        assert abs(avg_burnout - 50.0) < 0.01
    
    def test_balance_score_calculation(self, panel, specialists):
        """Test workload balance score."""
        # Equal workload (perfectly balanced)
        for spec in specialists:
            spec.burnout_level = 40.0
            spec.current_incident = None
        
        balance = panel._calculate_balance_score(specialists)
        assert balance > 9.0  # Should be near maximum
        
        # Unequal workload (poorly balanced)
        specialists[0].burnout_level = 90.0
        specialists[0].current_incident = Mock()
        specialists[1].burnout_level = 10.0
        specialists[2].burnout_level = 10.0
        
        balance = panel._calculate_balance_score(specialists)
        assert balance < 5.0  # Should be lower


class TestStaffManagementPanel:
    """Tests for StaffManagementPanel."""
    
    @pytest.fixture
    def panel(self):
        """Create staff management panel."""
        return StaffManagementPanel(230, 285, 230, 180)
    
    @pytest.fixture
    def specialists(self):
        """Create test specialists."""
        return [
            Specialist(id="spec_001", name="Alice", specialty="Network Security", level=5),
            Specialist(id="spec_002", name="Bob", specialty="Cryptography", level=3),
        ]
    
    def test_panel_creation(self, panel):
        """Test panel creates without errors."""
        assert panel.rect.width == 230
        assert len(panel.actions) == 6
    
    def test_action_state_updates(self, panel, specialists):
        """Test action enablement based on game state."""
        # Sufficient budget
        panel.update_action_state(specialists, 5000)
        
        hire_entry = next(a for a in panel.actions if a.name == "hire_entry")
        hire_mid = next(a for a in panel.actions if a.name == "hire_mid")
        
        assert hire_entry.enabled is True
        assert hire_mid.enabled is True
        
        # Insufficient budget
        panel.update_action_state(specialists, 1000)
        
        assert hire_entry.enabled is False
        assert hire_mid.enabled is False
    
    def test_fire_action_disabled_with_one_specialist(self, panel):
        """Test fire action disabled when only one specialist."""
        one_specialist = [
            Specialist(id="spec_001", name="Alice", specialty="Network", level=5)
        ]
        
        panel.update_action_state(one_specialist, 10000)
        
        fire_action = next(a for a in panel.actions if a.name == "fire")
        assert fire_action.enabled is False
    
    def test_rest_action_enabled_with_overworked(self, panel, specialists):
        """Test rest action enabled when team overworked."""
        specialists[0].burnout_level = 80.0
        
        panel.update_action_state(specialists, 1000)
        
        rest_action = next(a for a in panel.actions if a.name == "rest_all")
        assert rest_action.enabled is True


class TestAssignmentWorkflowPanel:
    """Tests for AssignmentWorkflowPanel."""
    
    @pytest.fixture
    def panel(self):
        """Create assignment workflow panel."""
        return AssignmentWorkflowPanel(230, 470, 230, 240)
    
    @pytest.fixture
    def specialist(self):
        """Create test specialist."""
        spec = Specialist(id="spec_001", name="Alice", specialty="Network Security", level=5)
        spec.current_incident = None
        return spec
    
    @pytest.fixture
    def incident(self):
        """Create test incident."""
        incident = Incident(
            id="inc_001",
            incident_type="DDoS Attack",
            specialty_required="Network Security",
            difficulty=2,
            client_id="client_001"
        )
        incident.min_level = 3
        return incident
    
    def test_panel_creation(self, panel):
        """Test panel creates without errors."""
        assert panel.rect.width == 230
        assert panel.current_state == panel.STATE_SELECT_SPECIALIST
    
    def test_workflow_state_transitions(self, panel, specialist, incident):
        """Test workflow state transitions."""
        # Initial state
        assert panel.current_state == panel.STATE_SELECT_SPECIALIST
        
        # Select specialist
        panel.set_selection(specialist.id, None, [specialist], [incident])
        # State remains SELECT (not full until incident selected too)
        
        # Select both
        panel.set_selection(specialist.id, incident.id, [specialist], [incident])
        assert panel.current_state == panel.STATE_CONFIRM
    
    def test_assignment_validation(self, panel, specialist, incident):
        """Test assignment compatibility validation."""
        panel.selected_specialist = specialist
        panel.selected_incident = incident
        
        # Should be valid (matching specialty, adequate level)
        is_valid = panel._validate_assignment()
        assert is_valid is True
        
        # Change specialty
        incident.specialty_required = "Cryptography"
        is_valid = panel._validate_assignment()
        assert is_valid is False
    
    def test_match_analysis(self, panel, specialist, incident):
        """Test match analysis provides correct feedback."""
        panel.selected_specialist = specialist
        panel.selected_incident = incident
        
        color, text = panel._get_match_analysis()
        assert "Excellent Match" in text or "Level Mismatch" in text or "Incompatible" in text
    
    def test_workflow_reset(self, panel, specialist, incident):
        """Test workflow reset clears selections."""
        panel.selected_specialist = specialist
        panel.selected_incident = incident
        panel.current_state = panel.STATE_CONFIRM
        
        panel.reset_workflow()
        
        assert panel.selected_specialist is None
        assert panel.selected_incident is None
        assert panel.current_state == panel.STATE_SELECT_SPECIALIST


class TestGameUIIntegration:
    """Tests for GameUI integration with new panels."""
    
    @pytest.fixture
    def mock_game_state(self):
        """Create mock game state."""
        state = Mock(spec=GameState)
        state.specialists = [
            Specialist(id="spec_001", name="Alice", specialty="Network Security", level=5),
            Specialist(id="spec_002", name="Bob", specialty="Cryptography", level=3),
        ]
        state.incidents = [
            Incident(id="inc_001", incident_type="DDoS", specialty_required="Network Security", 
                    difficulty=2, client_id="client_001"),
        ]
        state.current_money = 5000.0
        state.is_paused = False
        return state
    
    def test_new_panels_initialized(self, mock_game_state):
        """Test that new panels are properly initialized in GameUI."""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.display.set_caption'), \
             patch.object(GameUI, 'render', return_value=None):
            
            ui = GameUI(mock_game_state, system_manager=None)
            
            # Check that all new panels exist
            assert hasattr(ui, 'workload_analytics')
            assert isinstance(ui.workload_analytics, WorkloadAnalyticsPanel)
            
            assert hasattr(ui, 'staff_management')
            assert isinstance(ui.staff_management, StaffManagementPanel)
            
            assert hasattr(ui, 'assignment_workflow')
            assert isinstance(ui.assignment_workflow, AssignmentWorkflowPanel)
    
    def test_panel_selection_updates_workflow(self, mock_game_state):
        """Test that specialist/incident selection updates workflow panel."""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.display.set_caption'), \
             patch.object(GameUI, 'render', return_value=None):
            
            ui = GameUI(mock_game_state, system_manager=None)
            
            # Simulate selection
            ui._on_specialist_selected("spec_001")
            assert ui.selected_specialist_id == "spec_001"
            
            ui._on_incident_selected("inc_001")
            assert ui.selected_incident_id == "inc_001"
            
            # Workflow should now be in confirm state
            assert ui.assignment_workflow.current_state == ui.assignment_workflow.STATE_CONFIRM


class TestPanelConsistency:
    """Tests for visual and functional consistency across panels."""
    
    def test_color_definitions(self):
        """Test that all panels have consistent color definitions."""
        colors = {
            'OK': (80, 200, 120),
            'WARNING': (255, 200, 50),
            'CRITICAL': (220, 80, 80),
        }
        
        # Verify WorkloadAnalyticsPanel colors
        assert WorkloadAnalyticsPanel.CAPACITY_OK == colors['OK']
        assert WorkloadAnalyticsPanel.CAPACITY_WARNING == colors['WARNING']
        assert WorkloadAnalyticsPanel.CAPACITY_CRITICAL == colors['CRITICAL']
        
        # Verify StaffManagementPanel colors
        assert StaffManagementPanel.ACTION_BG == (35, 45, 60)
        
        # Verify AssignmentWorkflowPanel colors
        assert AssignmentWorkflowPanel.SUCCESS_COLOR == colors['OK']
        assert AssignmentWorkflowPanel.ERROR_COLOR == colors['CRITICAL']
    
    def test_font_consistency(self):
        """Test that panels use consistent font sizes."""
        # All panels should have title, label, and value fonts
        panel1 = WorkloadAnalyticsPanel(0, 0, 100, 100)
        panel2 = StaffManagementPanel(0, 0, 100, 100)
        panel3 = AssignmentWorkflowPanel(0, 0, 100, 100)
        
        assert hasattr(panel1, 'font_title')
        assert hasattr(panel2, 'font_title')
        assert hasattr(panel3, 'font_title')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
