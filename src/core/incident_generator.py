"""Incident generation system for creating security incidents.

This module handles the creation of security incidents based on client contracts,
incident templates, and game configuration. It implements probability-based generation
with difficulty scaling and specialty distribution.
"""

import random
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import os

from ..models.incident import Incident
from ..models.client import Client
from ..utils.json_loader import JSONLoader
from ..utils.logger import GameLogger


@dataclass
class IncidentTemplate:
    """Template for generating incidents."""
    id: str
    name: str
    description: str
    specialty_required: str
    difficulty_range: List[int]
    base_sla_seconds: int
    base_reward: int
    xp_reward: int


@dataclass
class GenerationConfig:
    """Configuration for incident generation."""
    difficulty_weights: Dict[int, float]
    specialty_distribution: Dict[str, float]
    max_active_incidents: int


class IncidentGenerator:
    """Handles generation of security incidents based on game state and configuration."""
    # Explicit attribute annotations for clarity and static analysis
    _logger: GameLogger
    _json_loader: JSONLoader
    _templates: List[IncidentTemplate]
    _config: Optional[GenerationConfig]
    _last_generation_time: float

    def __init__(self, logger: Optional[GameLogger] = None):
        """Initialize the incident generator.

        Args:
            logger: Optional logger for generation events
        """
        self._logger = logger or GameLogger("incident_generator")
        self._json_loader = JSONLoader()
        self._templates: List[IncidentTemplate] = []
        self._config: Optional[GenerationConfig] = None
        self._last_generation_time = time.time()

        # Load configuration
        self._load_templates()
        self._load_config()

    def _load_templates(self) -> None:
        """Load incident templates from JSON configuration."""
        try:
            data = self._json_loader.load_data("incidents.json")

            self._templates = []
            for template_data in data.get("incident_types", []):
                template = IncidentTemplate(
                    id=template_data["id"],
                    name=template_data["name"],
                    description=template_data.get("description", ""),
                    specialty_required=template_data["specialty_required"],
                    difficulty_range=template_data["difficulty_range"],
                    base_sla_seconds=template_data["base_sla_seconds"],
                    base_reward=template_data["base_reward"],
                    xp_reward=template_data["xp_reward"]
                )
                self._templates.append(template)

            logger_target = getattr(self._logger, "logger", self._logger)
            logger_target.info(f"[INCIDENT_GENERATOR] Loaded {len(self._templates)} incident templates")

        except Exception as e:
            logger_target = getattr(self._logger, "logger", self._logger)
            logger_target.error(f"[INCIDENT_GENERATOR] Failed to load incident templates: {e}")
            raise

    def _load_config(self) -> None:
        """Load generation configuration from game config."""
        try:
            data = self._json_loader.load_data("game_config.json")

            incident_gen_config = data.get("incident_generation", {})
            game_settings = data.get("game_settings", {})

            self._config = GenerationConfig(
                difficulty_weights=incident_gen_config.get("difficulty_weights", {}),
                specialty_distribution=incident_gen_config.get("specialty_distribution", {}),
                max_active_incidents=game_settings.get("max_active_incidents", 50)
            )

            logger_target = getattr(self._logger, "logger", self._logger)
            logger_target.info("[INCIDENT_GENERATOR] Loaded generation configuration")

        except Exception as e:
            logger_target = getattr(self._logger, "logger", self._logger)
            logger_target.error(f"[INCIDENT_GENERATOR] Failed to load generation config: {e}")
            raise

    def should_generate_incident(self, client: Client, delta_time: float, active_incident_count: int) -> bool:
        """Determine if an incident should be generated for a client.

        Args:
            client: The client to check
            delta_time: Time elapsed since last check (in seconds)
            active_incident_count: Current number of active incidents

        Returns:
            True if incident should be generated, False otherwise
        """
        if not client.active:
            return False

        if active_incident_count >= self._config.max_active_incidents:
            return False

        # Calculate incident probability based on client's rate
        incidents_per_second = client.incident_rate_per_minute / 60.0
        probability = incidents_per_second * delta_time

        # Apply reputation modifier (higher reputation = slightly lower incident rate)
        reputation_modifier = max(0.5, 1.0 - (client.reputation - 50) / 100.0)
        probability *= reputation_modifier

        # Generate random number and check against probability
        return random.random() < probability

    def generate_incident(self, client: Client, incident_id: Optional[str] = None) -> Incident:
        """Generate a new incident for a client.

        Args:
            client: The client for whom to generate the incident
            incident_id: Optional specific ID for the incident

        Returns:
            Newly generated incident
        """
        if not self._templates:
            raise ValueError("No incident templates loaded")

        # Select specialty based on distribution
        specialty = self._select_specialty()

        # Filter templates by selected specialty
        specialty_templates = [t for t in self._templates if t.specialty_required == specialty]

        if not specialty_templates:
            # Fallback to any template if no specialty match
            specialty_templates = self._templates

        # Select random template
        template = random.choice(specialty_templates)

        # Generate difficulty based on weights
        difficulty = self._select_difficulty()

        # Apply client SLA multiplier
        sla_seconds = int(template.base_sla_seconds * client.sla_multiplier)

        # Generate unique ID
        if incident_id is None:
            incident_id = f"inc_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

        # Create incident
        incident = Incident(
            id=incident_id,
            incident_type=template.name,
            specialty_required=template.specialty_required,
            difficulty=difficulty,
            sla_seconds=sla_seconds,
            base_reward=template.base_reward,
            xp_reward=template.xp_reward,
            client_id=client.id
        )

        logger_target = getattr(self._logger, "logger", self._logger)
        logger_target.info(
            f"[INCIDENT_GENERATOR] Generated incident {incident.id} for client {client.id}: "
            f"{template.name} (difficulty {difficulty}, specialty {specialty})"
        )

        return incident

    def _select_specialty(self) -> str:
        """Select a specialty based on configured distribution.

        Returns:
            Selected specialty name
        """
        if not self._config.specialty_distribution:
            # Default distribution if not configured
            specialties = ["Network Security", "Malware Analysis", "Digital Forensics",
                         "Application Security", "Cloud Security", "Incident Response"]
            return random.choice(specialties)

        # Weighted random selection
        specialties = list(self._config.specialty_distribution.keys())
        weights = list(self._config.specialty_distribution.values())

        return random.choices(specialties, weights=weights, k=1)[0]

    def _select_difficulty(self) -> int:
        """Select difficulty level based on configured weights.

        Returns:
            Difficulty level (1-5)
        """
        if not self._config.difficulty_weights:
            # Default uniform distribution if not configured
            return random.randint(1, 5)

        # Weighted random selection
        difficulties = list(self._config.difficulty_weights.keys())
        weights = list(self._config.difficulty_weights.values())

        return random.choices(difficulties, weights=weights, k=1)[0]

    def get_available_specialties(self) -> List[str]:
        """Get list of all available specialties from templates.

        Returns:
            List of specialty names
        """
        return list(set(template.specialty_required for template in self._templates))

    def get_templates_for_specialty(self, specialty: str) -> List[IncidentTemplate]:
        """Get all templates for a specific specialty.

        Args:
            specialty: The specialty to filter by

        Returns:
            List of matching templates
        """
        return [t for t in self._templates if t.specialty_required == specialty]

    def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about incident generation.

        Returns:
            Dictionary with generation statistics
        """
        stats = {
            "total_templates": len(self._templates),
            "specialties": {},
            "difficulty_distribution": self._config.difficulty_weights if self._config else {},
            "max_active_incidents": self._config.max_active_incidents if self._config else 50
        }

        # Count templates per specialty
        for template in self._templates:
            specialty = template.specialty_required
            if specialty not in stats["specialties"]:
                stats["specialties"][specialty] = 0
            stats["specialties"][specialty] += 1

        return stats


    def reload_configuration(self) -> None:
        """Reload templates and configuration from disk."""
        self._load_templates()
        self._load_config()
        logger_target = getattr(self._logger, "logger", self._logger)
        logger_target.info("[INCIDENT_GENERATOR] Configuration reloaded")
