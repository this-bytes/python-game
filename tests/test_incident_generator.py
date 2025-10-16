"""Tests for the incident generation system."""

import pytest
import time
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.core.incident_generator import IncidentGenerator, IncidentTemplate, GenerationConfig
from src.models.client import Client
from src.models.incident import Incident
from src.utils.logger import GameLogger


class TestIncidentTemplate:
    """Test the IncidentTemplate dataclass."""

    def test_template_creation(self):
        """Test creating an incident template."""
        template = IncidentTemplate(
            id="test_001",
            name="Test Incident",
            description="A test incident",
            specialty_required="Network Security",
            difficulty_range=[1, 3],
            base_sla_seconds=300,
            base_reward=500,
            xp_reward=100
        )

        assert template.id == "test_001"
        assert template.name == "Test Incident"
        assert template.specialty_required == "Network Security"
        assert template.difficulty_range == [1, 3]
        assert template.base_sla_seconds == 300
        assert template.base_reward == 500
        assert template.xp_reward == 100


class TestGenerationConfig:
    """Test the GenerationConfig dataclass."""

    def test_config_creation(self):
        """Test creating a generation config."""
        config = GenerationConfig(
            difficulty_weights={1: 0.5, 2: 0.3, 3: 0.2},
            specialty_distribution={"Network": 0.5, "Malware": 0.5},
            max_active_incidents=50
        )

        assert config.difficulty_weights[1] == 0.5
        assert config.specialty_distribution["Network"] == 0.5
        assert config.max_active_incidents == 50


class TestIncidentGenerator:
    """Test the IncidentGenerator class."""

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger."""
        mock_game_logger = MagicMock(spec=GameLogger)
        mock_game_logger.logger = MagicMock()  # Add the logger attribute
        return mock_game_logger

    @pytest.fixture
    def sample_client(self):
        """Create a sample client for testing."""
        return Client(
            id="client_001",
            name="Test Client",
            industry="Technology",
            incident_rate_per_minute=0.5,
            sla_multiplier=1.0,
            reputation=80,
            contract_value=10000,
            active=True
        )

    @pytest.fixture
    @patch('src.core.incident_generator.JSONLoader')
    def generator(self, mock_json_loader_class, mock_logger):
        """Create an incident generator with mocked dependencies."""
        # Create a mock JSONLoader instance
        mock_json_loader = MagicMock()
        mock_json_loader_class.return_value = mock_json_loader
        
        # Mock the JSON loading
        mock_json_loader.load_data.side_effect = [
            {  # incidents.json
                "incident_types": [
                    {
                        "id": "inc_001",
                        "name": "Test Incident",
                        "description": "A test incident",
                        "specialty_required": "Network Security",
                        "difficulty_range": [1, 3],
                        "base_sla_seconds": 300,
                        "base_reward": 500,
                        "xp_reward": 100
                    },
                    {
                        "id": "inc_002",
                        "name": "Another Incident",
                        "description": "Another test incident",
                        "specialty_required": "Malware Analysis",
                        "difficulty_range": [2, 4],
                        "base_sla_seconds": 400,
                        "base_reward": 600,
                        "xp_reward": 120
                    }
                ]
            },
            {  # game_config.json
                "game_settings": {
                    "max_active_incidents": 50
                },
                "incident_generation": {
                    "difficulty_weights": {1: 0.5, 2: 0.3, 3: 0.2},
                    "specialty_distribution": {"Network Security": 0.6, "Malware Analysis": 0.4}
                }
            }
        ]

        return IncidentGenerator(logger=mock_logger)

    def test_initialization(self, generator, mock_logger):
        """Test generator initialization."""
        assert len(generator._templates) == 2
        assert generator._config is not None
        assert generator._config.max_active_incidents == 50
        mock_logger.logger.info.assert_called()

    def test_should_generate_incident_active_client(self, generator, sample_client):
        """Test incident generation check for active client."""
        # Should potentially generate (random, but test the logic)
        result = generator.should_generate_incident(sample_client, 60.0, 0)  # 1 minute
        assert isinstance(result, bool)

    def test_should_generate_incident_inactive_client(self, generator):
        """Test incident generation check for inactive client."""
        inactive_client = Client(
            id="client_002",
            name="Inactive Client",
            industry="Technology",
            incident_rate_per_minute=1.0,
            sla_multiplier=1.0,
            reputation=80,
            contract_value=10000,
            active=False
        )

        result = generator.should_generate_incident(inactive_client, 60.0, 0)
        assert result is False

    def test_should_generate_incident_max_reached(self, generator, sample_client):
        """Test incident generation check when max incidents reached."""
        result = generator.should_generate_incident(sample_client, 60.0, 50)
        assert result is False

    def test_generate_incident(self, generator, sample_client, mock_logger):
        """Test incident generation."""
        incident = generator.generate_incident(sample_client, "test_inc_001")

        assert isinstance(incident, Incident)
        assert incident.id == "test_inc_001"
        assert incident.client_id == sample_client.id
        assert incident.specialty_required in ["Network Security", "Malware Analysis"]
        assert 1 <= incident.difficulty <= 3
        assert incident.status == "pending"
        mock_logger.logger.info.assert_called()

    @patch('random.choice')
    @patch('random.choices')
    def test_select_specialty(self, mock_choices, mock_choice, generator):
        """Test specialty selection."""
        mock_choices.return_value = ["Network Security"]

        result = generator._select_specialty()
        assert result == "Network Security"
        mock_choices.assert_called_once()

    @patch('random.choices')
    def test_select_difficulty(self, mock_choices, generator):
        """Test difficulty selection."""
        mock_choices.return_value = [2]

        result = generator._select_difficulty()
        assert result == 2
        mock_choices.assert_called_once()

    def test_get_available_specialties(self, generator):
        """Test getting available specialties."""
        specialties = generator.get_available_specialties()
        assert set(specialties) == {"Network Security", "Malware Analysis"}

    def test_get_templates_for_specialty(self, generator):
        """Test getting templates for a specialty."""
        templates = generator.get_templates_for_specialty("Network Security")
        assert len(templates) == 1
        assert templates[0].specialty_required == "Network Security"

    def test_get_generation_stats(self, generator):
        """Test getting generation statistics."""
        stats = generator.get_generation_stats()

        assert stats["total_templates"] == 2
        assert stats["specialties"]["Network Security"] == 1
        assert stats["specialties"]["Malware Analysis"] == 1
        assert stats["max_active_incidents"] == 50

    def test_reload_configuration(self, generator, mock_logger):
        """Test configuration reloading."""
        # Mock the JSON loader's load_data method for this test
        generator._json_loader.load_data.side_effect = [
            {"incident_types": []},  # Empty templates for test
            {"game_settings": {"max_active_incidents": 25}}
        ]

        generator.reload_configuration()

        assert len(generator._templates) == 0
        assert generator._config.max_active_incidents == 25
        mock_logger.logger.info.assert_called_with("[INCIDENT_GENERATOR] Configuration reloaded")

    def test_generate_incident_with_sla_multiplier(self, generator, sample_client):
        """Test that client SLA multiplier affects incident SLA."""
        # Set client with SLA multiplier
        sample_client.sla_multiplier = 1.5

        incident = generator.generate_incident(sample_client)

        # Base SLA is 300 or 400, multiplied by 1.5 should be 450 or 600
        assert incident.sla_seconds in [450, 600]

    @patch('random.random')
    def test_should_generate_incident_probability(self, mock_random, generator, sample_client):
        """Test incident generation probability calculation."""
        # Force random to return 0.1 (should generate)
        mock_random.return_value = 0.1

        result = generator.should_generate_incident(sample_client, 120.0, 0)  # 2 minutes
        assert result is True

        # Force random to return 0.9 (should not generate)
        mock_random.return_value = 0.9
        result = generator.should_generate_incident(sample_client, 120.0, 0)
        assert result is False

    def test_select_specialty_fallback(self, generator):
        """Test specialty selection fallback when config is empty."""
        # Temporarily clear config
        original_config = generator._config
        generator._config = GenerationConfig({}, {}, 50)

        result = generator._select_specialty()
        assert result in ["Network Security", "Malware Analysis", "Digital Forensics",
                         "Application Security", "Cloud Security", "Incident Response"]

        # Restore config
        generator._config = original_config

    def test_select_difficulty_fallback(self, generator):
        """Test difficulty selection fallback when config is empty."""
        # Temporarily clear config
        original_config = generator._config
        generator._config = GenerationConfig({}, {}, 50)

        result = generator._select_difficulty()
        assert 1 <= result <= 5

        # Restore config
        generator._config = original_config
