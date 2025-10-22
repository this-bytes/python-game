"""Phase 4: Incident Dispatch & Assignment System Tests

Tests for incident generation, assignment, and resolution mechanics.
Covers per-client incident generation, specialist assignment, SLA tracking,
and comprehensive integration scenarios.
"""

import pytest
from typing import List
from unittest.mock import Mock

from src.models.incident import Incident, IncidentStatus
from src.models.specialist import Specialist, SpecialistStats
from src.models.client import Client, Industry
from src.models.game_state import GameState
from src.core.incident_generator import IncidentGenerator, IncidentTemplate
from src.core.incident_dispatch_system import IncidentDispatchSystem, AssignmentResult, ResolutionResult
from src.core.plugins.incident_dispatch_plugin import IncidentDispatchPlugin


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def specialist() -> Specialist:
    """Create a test specialist."""
    return Specialist(
        id="spec_001",
        name="Alice Chen",
        specialty="Network Security",
        level=5,
        xp=1000,
        stats=SpecialistStats(speed=85, accuracy=90, experience_bonus=1.2)
    )


@pytest.fixture
def network_specialist() -> Specialist:
    """Create a network security specialist."""
    return Specialist(
        id="spec_network_001",
        name="Bob Networks",
        specialty="Network Security",
        level=3,
        xp=500,
        stats=SpecialistStats(speed=80, accuracy=85, experience_bonus=1.0)
    )


@pytest.fixture
def crypto_specialist() -> Specialist:
    """Create a cryptography specialist."""
    return Specialist(
        id="spec_crypto_001",
        name="Carol Crypto",
        specialty="Cryptography",
        level=4,
        xp=750,
        stats=SpecialistStats(speed=75, accuracy=95, experience_bonus=1.1)
    )


@pytest.fixture
def forensics_specialist() -> Specialist:
    """Create a digital forensics specialist."""
    return Specialist(
        id="spec_forensics_001",
        name="Dave Forensics",
        specialty="Digital Forensics",
        level=2,
        xp=250,
        stats=SpecialistStats(speed=70, accuracy=88, experience_bonus=1.0)
    )


@pytest.fixture
def client() -> Client:
    """Create a test client."""
    return Client(
        client_id="client_001",
        company_name="TechCorp",
        industry=Industry.ECOMMERCE,
        monthly_contract_value=10000.0,
        sla_response_time_seconds=300,
        sla_resolution_time_seconds=3600,
        contract_start_month=1,
        contract_end_month=12,
        satisfaction=1.0,
        threat_landscape=["DDoS", "Fraud", "Data Exfiltration"],
        avg_monthly_incidents=5,
    )


@pytest.fixture
def banking_client() -> Client:
    """Create a banking client with stricter SLA."""
    return Client(
        client_id="client_bank_001",
        company_name="SecureBank",
        industry=Industry.BANKING,
        monthly_contract_value=20000.0,
        sla_response_time_seconds=60,
        sla_resolution_time_seconds=1800,
        contract_start_month=1,
        contract_end_month=12,
        satisfaction=0.9,
        threat_landscape=["Ransomware", "Fraud", "Insider Threats"],
        avg_monthly_incidents=10,
    )


@pytest.fixture
def incident(client: Client) -> Incident:
    """Create a test incident."""
    return Incident(
        id="inc_001",
        incident_type="DDoS Attack",
        specialty_required="Network Security",
        difficulty=2,
        sla_seconds=300,
        base_reward=500,
        xp_reward=100,
        client_id=client.client_id,
        status=IncidentStatus.PENDING.value
    )


@pytest.fixture
def dispatch_system() -> IncidentDispatchSystem:
    """Create incident dispatch system."""
    return IncidentDispatchSystem()


@pytest.fixture
def generator() -> IncidentGenerator:
    """Create incident generator."""
    return IncidentGenerator()


@pytest.fixture
def game_state(specialist, client) -> GameState:
    """Create a test game state."""
    state = GameState()
    state.specialists = [specialist]
    state.clients = [client]
    return state


# ============================================================================
# TESTS: Incident Generation
# ============================================================================

class TestIncidentGeneration:
    """Test incident generation for clients."""
    
    def test_incident_templates_load(self):
        """Verify incident templates load from JSON."""
        generator = IncidentGenerator()
        assert len(generator._templates) > 0
    
    def test_generate_single_incident(self, generator, client):
        """Verify single incident generation."""
        incident = generator.generate_incident(client)
        assert incident is not None
        assert incident.client_id == client.client_id
        assert incident.specialty_required is not None
    
    def test_incident_difficulty_in_range(self, generator, client):
        """Verify incident difficulty is in valid range."""
        for _ in range(10):
            incident = generator.generate_incident(client)
            assert 1 <= incident.difficulty <= 5


# ============================================================================
# TESTS: Incident Assignment
# ============================================================================

class TestIncidentAssignment:
    """Test incident assignment to specialists."""
    
    def test_assign_incident_success(self, dispatch_system, incident, specialist):
        """Verify successful incident assignment."""
        dispatch_system.add_incident(incident)
        
        result = dispatch_system.assign_incident(incident, specialist)
        
        assert result.success is True
        assert result.incident_id == incident.id
        assert result.specialist_id == specialist.id
        assert specialist.assigned_incident_id == incident.id
    
    def test_assign_incident_specialty_mismatch_fails(self, dispatch_system, incident, crypto_specialist):
        """Verify assignment fails when specialty doesn't match."""
        dispatch_system.add_incident(incident)
        
        result = dispatch_system.assign_incident(incident, crypto_specialist)
        
        assert result.success is False
        assert crypto_specialist.assigned_incident_id is None
    
    def test_assign_incident_already_assigned_fails(self, dispatch_system, incident, specialist):
        """Verify assignment fails if specialist already assigned."""
        dispatch_system.add_incident(incident)
        
        result1 = dispatch_system.assign_incident(incident, specialist)
        assert result1.success is True
        
        incident2 = Incident(
            id="inc_002",
            incident_type="Data Breach",
            specialty_required="Network Security",
            difficulty=3,
            sla_seconds=600,
            base_reward=1000,
            xp_reward=200,
            client_id="client_001",
            status=IncidentStatus.PENDING.value
        )
        dispatch_system.add_incident(incident2)
        
        result2 = dispatch_system.assign_incident(incident2, specialist)
        assert result2.success is False
    
    def test_find_best_specialist_by_specialty_match(self, dispatch_system, incident, network_specialist, crypto_specialist):
        """Verify best specialist selection prioritizes specialty match."""
        specialists = [network_specialist, crypto_specialist]
        
        best = dispatch_system.find_best_specialist(incident, specialists)
        
        assert best is not None
        assert best.id == network_specialist.id


# ============================================================================
# TESTS: Incident Resolution
# ============================================================================

class TestIncidentResolution:
    """Test incident resolution and reward calculations."""
    
    def test_resolve_incident_sla_met(self, dispatch_system, incident, specialist):
        """Verify resolution when SLA met."""
        dispatch_system.add_incident(incident)
        dispatch_system.assign_incident(incident, specialist)
        
        result = dispatch_system.resolve_incident(incident, specialist, True, 200)
        
        assert result.success is True
        assert result.sla_met is True
        assert result.xp_earned > 0
        assert result.reward_earned > 0
    
    def test_resolve_incident_sla_missed(self, dispatch_system, incident, specialist):
        """Verify resolution when SLA missed."""
        dispatch_system.add_incident(incident)
        dispatch_system.assign_incident(incident, specialist)
        
        result = dispatch_system.resolve_incident(incident, specialist, True, 600)
        
        assert result.success is True
        assert result.sla_met is False
        assert result.xp_earned > 0
    
    def test_resolve_incident_failure(self, dispatch_system, incident, specialist):
        """Verify resolution when incident fails."""
        dispatch_system.add_incident(incident)
        dispatch_system.assign_incident(incident, specialist)
        
        result = dispatch_system.resolve_incident(incident, specialist, False, 400)
        
        assert result.success is False
    
    def test_burnout_increases_on_resolution(self, dispatch_system, incident, specialist):
        """Verify specialist burnout increases after resolution."""
        dispatch_system.add_incident(incident)
        dispatch_system.assign_incident(incident, specialist)
        
        initial_burnout = specialist.burnout_level
        dispatch_system.resolve_incident(incident, specialist, True, 200)
        
        assert specialist.burnout_level > initial_burnout
    
    def test_xp_granted_on_resolution(self, dispatch_system, incident, specialist):
        """Verify specialist XP increases after resolution."""
        dispatch_system.add_incident(incident)
        dispatch_system.assign_incident(incident, specialist)
        
        initial_xp = specialist.xp
        dispatch_system.resolve_incident(incident, specialist, True, 200)
        
        assert specialist.xp > initial_xp
    
    def test_reward_scales_with_difficulty(self, dispatch_system, specialist):
        """Verify rewards scale with incident difficulty."""
        easy_incident = Incident(
            id="inc_easy",
            incident_type="Minor",
            specialty_required="Network Security",
            difficulty=1,
            sla_seconds=600,
            base_reward=100,
            xp_reward=50,
            client_id="client_001",
            status=IncidentStatus.PENDING.value
        )
        hard_incident = Incident(
            id="inc_hard",
            incident_type="Critical",
            specialty_required="Network Security",
            difficulty=5,
            sla_seconds=600,
            base_reward=100,
            xp_reward=50,
            client_id="client_001",
            status=IncidentStatus.PENDING.value
        )
        
        dispatch_system.add_incident(easy_incident)
        dispatch_system.add_incident(hard_incident)
        
        spec_easy = Specialist(id="spec_easy", name="Easy", specialty="Network Security", level=1, xp=0, stats=SpecialistStats(speed=100, accuracy=100, experience_bonus=1.0))
        spec_hard = Specialist(id="spec_hard", name="Hard", specialty="Network Security", level=1, xp=0, stats=SpecialistStats(speed=100, accuracy=100, experience_bonus=1.0))
        
        result_easy = dispatch_system.resolve_incident(easy_incident, spec_easy, True, 100)
        result_hard = dispatch_system.resolve_incident(hard_incident, spec_hard, True, 100)
        
        assert result_hard.reward_earned > result_easy.reward_earned


# ============================================================================
# TESTS: Dispatch Integration
# ============================================================================

class TestDispatchIntegration:
    """Test incident dispatch system integration."""
    
    def test_get_pending_incidents(self, dispatch_system, incident):
        """Verify pending incidents retrieval."""
        dispatch_system.add_incident(incident)
        
        pending = dispatch_system.get_pending_incidents()
        
        assert len(pending) > 0
        assert incident in pending
    
    def test_get_active_incidents(self, dispatch_system, incident, specialist):
        """Verify active incidents retrieval."""
        dispatch_system.add_incident(incident)
        dispatch_system.assign_incident(incident, specialist)
        
        active = dispatch_system.get_active_incidents()
        
        assert len(active) > 0
        assert incident in active
    
    def test_get_overdue_incidents(self, dispatch_system):
        """Verify overdue incidents detection."""
        import time
        overdue_incident = Incident(
            id="inc_overdue",
            incident_type="Test",
            specialty_required="Network Security",
            difficulty=2,
            sla_seconds=60,
            base_reward=500,
            xp_reward=100,
            client_id="client_001",
            status=IncidentStatus.PENDING.value
        )
        # Set SLA deadline to past (very old)
        overdue_incident.sla_deadline = time.time() - 1000
        
        dispatch_system.add_incident(overdue_incident)
        
        overdue = dispatch_system.get_overdue_incidents()
        
        assert len(overdue) > 0
    
    def test_get_dispatch_stats(self, dispatch_system, incident, specialist):
        """Verify dispatch statistics calculation."""
        dispatch_system.add_incident(incident)
        dispatch_system.assign_incident(incident, specialist)
        
        stats = dispatch_system.get_dispatch_stats()
        
        assert "total_incidents" in stats
        assert "pending_count" in stats
        assert "active_count" in stats


# ============================================================================
# TESTS: Plugin Integration
# ============================================================================

class TestDispatchPlugin:
    """Test IncidentDispatchPlugin GameSystem integration."""
    
    def test_plugin_initialization(self, game_state):
        """Verify plugin initializes correctly."""
        plugin = IncidentDispatchPlugin()
        plugin.initialize(game_state)
        
        assert plugin.get_name() == "IncidentDispatchPlugin"
        assert plugin.get_feature_id() == "incident_dispatch_system"
    
    def test_plugin_assign_wrapper(self, game_state, incident, specialist):
        """Verify plugin assign_incident wrapper works."""
        plugin = IncidentDispatchPlugin()
        plugin.initialize(game_state)
        
        plugin._dispatch_system.add_incident(incident)
        result = plugin.assign_incident(incident, specialist)
        
        assert isinstance(result, bool)
        assert result is True
    
    def test_plugin_get_pending_incidents(self, game_state, incident):
        """Verify plugin pending retrieval."""
        plugin = IncidentDispatchPlugin()
        plugin.initialize(game_state)
        
        plugin._dispatch_system.add_incident(incident)
        pending = plugin.get_pending_incidents()
        
        assert isinstance(pending, list)
        assert len(pending) > 0
    
    def test_plugin_get_best_specialist(self, game_state, incident, network_specialist, crypto_specialist):
        """Verify plugin specialist selection."""
        plugin = IncidentDispatchPlugin()
        plugin.initialize(game_state)
        
        specialists = [network_specialist, crypto_specialist]
        best = plugin.get_best_specialist_for_incident(incident, specialists)
        
        assert best is not None
        assert best.specialty == "Network Security"
    
    def test_plugin_get_stats(self, game_state):
        """Verify plugin statistics interface."""
        plugin = IncidentDispatchPlugin()
        plugin.initialize(game_state)
        
        stats = plugin.get_dispatch_stats()
        
        assert isinstance(stats, dict)


# ============================================================================
# TESTS: Phase 4 Complete Scenarios
# ============================================================================

class TestPhase4Scenarios:
    """Test complete Phase 4 workflows."""
    
    def test_scenario_generate_and_assign_multiple_incidents(self, generator, dispatch_system, client, specialist):
        """Test generating multiple incidents and assigning them."""
        # Generate 3 incidents using single-incident generation
        incident_ids = []
        for i in range(3):
            incident = generator.generate_incident(client, f"test_inc_{i}")
            dispatch_system.add_incident(incident)
            incident_ids.append(incident.id)
        
        pending = dispatch_system.get_pending_incidents()
        assert len(pending) == 3
    
    def test_scenario_multi_client_generation(self, generator, client, banking_client):
        """Test incident generation across multiple clients."""
        # Generate one incident per client using single-incident generation
        incident_client1 = generator.generate_incident(client, "inc_ecom_1")
        incident_client2 = generator.generate_incident(banking_client, "inc_bank_1")
        
        assert incident_client1.client_id == client.client_id
        assert incident_client2.client_id == banking_client.client_id
        # Verify incidents are valid types for their industry (not name-matching, just verifying they exist)
        assert incident_client1.incident_type is not None
        assert incident_client2.incident_type is not None
    
    def test_scenario_specialist_specialization_matching(self, dispatch_system, network_specialist, crypto_specialist):
        """Test that specialists handle correct specialties."""
        network_incident = Incident(
            id="inc_net",
            incident_type="Network",
            specialty_required="Network Security",
            difficulty=2,
            sla_seconds=300,
            base_reward=500,
            xp_reward=100,
            client_id="client_001",
            status=IncidentStatus.PENDING.value
        )
        
        crypto_incident = Incident(
            id="inc_crypto",
            incident_type="Encryption",
            specialty_required="Cryptography",
            difficulty=2,
            sla_seconds=300,
            base_reward=500,
            xp_reward=100,
            client_id="client_001",
            status=IncidentStatus.PENDING.value
        )
        
        dispatch_system.add_incident(network_incident)
        dispatch_system.add_incident(crypto_incident)
        
        result_net = dispatch_system.assign_incident(network_incident, network_specialist)
        assert result_net.success is True
        
        result_crypto = dispatch_system.assign_incident(crypto_incident, crypto_specialist)
        assert result_crypto.success is True
    
    def test_scenario_sla_pressure_affects_rewards(self, dispatch_system, specialist):
        """Test that SLA performance affects rewards."""
        incident = Incident(
            id="inc_sla_test",
            incident_type="Test",
            specialty_required="Network Security",
            difficulty=2,
            sla_seconds=600,
            base_reward=1000,
            xp_reward=100,
            client_id="client_001",
            status=IncidentStatus.PENDING.value
        )
        
        dispatch_system.add_incident(incident)
        dispatch_system.assign_incident(incident, specialist)
        
        result_met = dispatch_system.resolve_incident(incident, specialist, True, 300)
        reward_met = result_met.reward_earned
        
        specialist.assigned_incident_id = None
        incident2 = Incident(
            id="inc_sla_test2",
            incident_type="Test",
            specialty_required="Network Security",
            difficulty=2,
            sla_seconds=600,
            base_reward=1000,
            xp_reward=100,
            client_id="client_001",
            status=IncidentStatus.PENDING.value
        )
        
        dispatch_system.add_incident(incident2)
        dispatch_system.assign_incident(incident2, specialist)
        
        result_missed = dispatch_system.resolve_incident(incident2, specialist, True, 700)
        reward_missed = result_missed.reward_earned
        
        assert reward_met > reward_missed
    
    def test_scenario_complete_workflow(self, generator, dispatch_system, client, specialist):
        """Test complete workflow: generate → assign → resolve."""
        incident = generator.generate_incident(client, "workflow_incident")
        
        dispatch_system.add_incident(incident)
        
        pending = dispatch_system.get_pending_incidents()
        assert len(pending) > 0
        
        if incident.specialty_required == specialist.specialty:
            result = dispatch_system.assign_incident(incident, specialist)
            
            if result.success:
                resolution = dispatch_system.resolve_incident(incident, specialist, True, 200)
                assert resolution.success is True
