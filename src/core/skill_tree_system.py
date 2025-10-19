"""Skill tree system for specialist progression and specialization.

This module manages skill trees, skill unlocking, and skill effects for specialists.
Each specialty has its own skill tree with multiple tiers and prerequisites.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from pathlib import Path

from src.core.game_system import GameSystem
from src.models.specialist import Specialist
from src.core.event_bus import get_event_bus, Event
from src.models.game_state import GameState

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """Represents a single skill in the skill tree."""
    id: str
    name: str
    description: str
    cost: int
    prerequisites: List[str] = field(default_factory=list)
    effects: Dict[str, Any] = field(default_factory=dict)
    icon: str = ""
    unlocked: bool = False

    def to_dict(self) -> Dict:
        """Convert skill to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "cost": self.cost,
            "prerequisites": self.prerequisites,
            "effects": self.effects,
            "icon": self.icon,
            "unlocked": self.unlocked
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Skill':
        """Create skill from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            cost=data["cost"],
            prerequisites=data.get("prerequisites", []),
            effects=data.get("effects", {}),
            icon=data.get("icon", ""),
            unlocked=data.get("unlocked", False)
        )


@dataclass
class SkillTier:
    """Represents a tier of skills in a skill tree."""
    tier: int
    name: str
    skills: List[Skill] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert tier to dictionary."""
        return {
            "tier": self.tier,
            "name": self.name,
            "skills": [skill.to_dict() for skill in self.skills]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'SkillTier':
        """Create tier from dictionary."""
        return cls(
            tier=data["tier"],
            name=data["name"],
            skills=[Skill.from_dict(skill_data) for skill_data in data.get("skills", [])]
        )


@dataclass
class SkillTree:
    """Represents a complete skill tree for a specialty."""
    specialty: str
    name: str
    description: str
    tiers: List[SkillTier] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert skill tree to dictionary."""
        return {
            "specialty": self.specialty,
            "name": self.name,
            "description": self.description,
            "tiers": [tier.to_dict() for tier in self.tiers]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'SkillTree':
        """Create skill tree from dictionary."""
        return cls(
            specialty=data["specialty"],
            name=data["name"],
            description=data["description"],
            tiers=[SkillTier.from_dict(tier_data) for tier_data in data.get("tiers", [])]
        )


class SkillTreeSystem(GameSystem):
    """Manages skill trees and specialist progression."""

    def __init__(self):
        """Initialize the skill tree system."""
        super().__init__()
        self.skill_trees: Dict[str, SkillTree] = {}
        self.unlocked_skills: Dict[str, Set[str]] = {}  # specialist_id -> set of unlocked skill IDs
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._game_state: Optional[GameState] = None

    def get_name(self) -> str:
        """Get the unique name of this system.

        Returns:
            System name
        """
        return "skill_tree_system"

    def initialize(self, game_state: GameState) -> bool:
        """Initialize the skill tree system.

        Args:
            game_state: Current game state

        Returns:
            True if initialization successful, False otherwise
        """
        self._game_state = game_state
        try:
            self._load_skill_trees()
            self._initialize_unlocked_skills(game_state)
            self._register_event_handlers()
            self.logger.info("Skill tree system initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize skill tree system: {e}")
            return False

    def _load_skill_trees(self) -> None:
        """Load skill tree configurations from JSON file."""
        skill_trees_path = Path("data/skill_trees.json")
        if not skill_trees_path.exists():
            self.logger.warning("Skill trees configuration file not found")
            return

        try:
            with open(skill_trees_path, 'r') as f:
                data = json.load(f)

            for specialty, tree_data in data.get("skill_trees", {}).items():
                skill_tree = SkillTree.from_dict(tree_data)
                self.skill_trees[specialty] = skill_tree

            self.logger.info(f"Loaded {len(self.skill_trees)} skill trees")
        except Exception as e:
            self.logger.error(f"Failed to load skill trees: {e}")
            raise

    def _initialize_unlocked_skills(self, game_state: GameState) -> None:
        """Initialize unlocked skills tracking for all specialists.

        Args:
            game_state: Current game state
        """
        for specialist in game_state.specialists:
            if specialist.id not in self.unlocked_skills:
                self.unlocked_skills[specialist.id] = set()

    def _register_event_handlers(self) -> None:
        """Register event handlers for skill tree system."""
        event_bus = get_event_bus()
        event_bus.subscribe("specialist_leveled_up", self._on_specialist_leveled_up)
        event_bus.subscribe("specialist_created", self._on_specialist_created)

    def update(self, delta_time: float) -> None:
        """Update the skill tree system.

        Args:
            delta_time: Time elapsed since last update
        """
        # Skill tree system doesn't need continuous updates
        pass

    def shutdown(self) -> None:
        """Shutdown the skill tree system."""
        self.logger.info("Skill tree system shut down")

    def save_state(self) -> Dict:
        """Save the current state of the skill tree system.

        Returns:
            Dictionary containing system state
        """
        return {
            "unlocked_skills": {sid: list(skills) for sid, skills in self.unlocked_skills.items()}
        }

    def load_state(self, state: Dict) -> None:
        """Load the state of the skill tree system.

        Args:
            state: Dictionary containing system state
        """
        unlocked_skills_data = state.get("unlocked_skills", {})
        for specialist_id, skills_list in unlocked_skills_data.items():
            self.unlocked_skills[specialist_id] = set(skills_list)

    def get_skill_tree(self, specialty: str) -> Optional[SkillTree]:
        """Get the skill tree for a specialty.

        Args:
            specialty: The specialty to get the skill tree for

        Returns:
            The skill tree if found, None otherwise
        """
        return self.skill_trees.get(specialty)

    def get_available_skills(self, specialist: Specialist) -> List[Skill]:
        """Get skills that a specialist can unlock.

        Args:
            specialist: The specialist to check

        Returns:
            List of skills that can be unlocked
        """
        skill_tree = self.get_skill_tree(specialist.specialty)
        if not skill_tree:
            return []

        available_skills = []
        unlocked_skill_ids = self.unlocked_skills.get(specialist.id, set())

        for tier in skill_tree.tiers:
            for skill in tier.skills:
                if skill.id in unlocked_skill_ids:
                    continue

                # Check if prerequisites are met
                if self._prerequisites_met(specialist, skill):
                    available_skills.append(skill)

        return available_skills

    def can_unlock_skill(self, specialist: Specialist, skill_id: str) -> bool:
        """Check if a specialist can unlock a specific skill.

        Args:
            specialist: The specialist to check
            skill_id: The skill ID to check

        Returns:
            True if the skill can be unlocked, False otherwise
        """
        skill_tree = self.get_skill_tree(specialist.specialty)
        if not skill_tree:
            return False

        # Find the skill
        skill = self._find_skill(skill_tree, skill_id)
        if not skill:
            return False

        # Check if already unlocked
        unlocked_skills = self.unlocked_skills.get(specialist.id, set())
        if skill_id in unlocked_skills:
            return False

        # Check skill points
        if specialist.skill_points < skill.cost:
            return False

        # Check prerequisites
        return self._prerequisites_met(specialist, skill)

    def unlock_skill(self, specialist: Specialist, skill_id: str) -> bool:
        """Unlock a skill for a specialist.

        Args:
            specialist: The specialist to unlock the skill for
            skill_id: The skill ID to unlock

        Returns:
            True if skill was unlocked successfully, False otherwise
        """
        if not self.can_unlock_skill(specialist, skill_id):
            return False

        skill_tree = self.get_skill_tree(specialist.specialty)
        if not skill_tree:
            return False

        skill = self._find_skill(skill_tree, skill_id)
        if not skill:
            return False

        # Deduct skill points
        specialist.skill_points -= skill.cost

        # Unlock the skill
        if specialist.id not in self.unlocked_skills:
            self.unlocked_skills[specialist.id] = set()
        self.unlocked_skills[specialist.id].add(skill_id)

        # Apply skill effects
        self._apply_skill_effects(specialist, skill)

        self.logger.info(f"Specialist {specialist.name} unlocked skill: {skill.name}")

        # Publish event
        event_bus = get_event_bus()
        event_bus.publish("skill_unlocked", {
            "specialist_id": specialist.id,
            "skill_id": skill_id,
            "skill_name": skill.name
        })

        return True

    def get_unlocked_skills(self, specialist: Specialist) -> List[Skill]:
        """Get all unlocked skills for a specialist.

        Args:
            specialist: The specialist to get skills for

        Returns:
            List of unlocked skills
        """
        skill_tree = self.get_skill_tree(specialist.specialty)
        if not skill_tree:
            return []

        unlocked_skill_ids = self.unlocked_skills.get(specialist.id, set())
        unlocked_skills = []

        for tier in skill_tree.tiers:
            for skill in tier.skills:
                if skill.id in unlocked_skill_ids:
                    unlocked_skills.append(skill)

        return unlocked_skills

    def get_specialist_skill_effects(self, specialist: Specialist) -> Dict[str, Any]:
        """Get all skill effects for a specialist.

        Args:
            specialist: The specialist to get effects for

        Returns:
            Dictionary of effect types to cumulative values
        """
        effects = {
            "speed_multiplier": 1.0,
            "accuracy_multiplier": 1.0,
            "experience_bonus": 1.0,
            "detection_multiplier": 1.0,
            "unlocked_abilities": []
        }

        unlocked_skills = self.get_unlocked_skills(specialist)
        for skill in unlocked_skills:
            for effect_type, effect_value in skill.effects.items():
                if effect_type.endswith("_multiplier"):
                    effects[effect_type] = effects.get(effect_type, 1.0) * effect_value
                elif effect_type == "unlock_ability":
                    effects["unlocked_abilities"].append(effect_value)
                else:
                    # Additive effects
                    effects[effect_type] = effects.get(effect_type, 0) + effect_value

        return effects

    def _find_skill(self, skill_tree: SkillTree, skill_id: str) -> Optional[Skill]:
        """Find a skill in a skill tree by ID.

        Args:
            skill_tree: The skill tree to search
            skill_id: The skill ID to find

        Returns:
            The skill if found, None otherwise
        """
        for tier in skill_tree.tiers:
            for skill in tier.skills:
                if skill.id == skill_id:
                    return skill
        return None

    def _prerequisites_met(self, specialist: Specialist, skill: Skill) -> bool:
        """Check if prerequisites are met for a skill.

        Args:
            specialist: The specialist to check
            skill: The skill to check prerequisites for

        Returns:
            True if prerequisites are met, False otherwise
        """
        unlocked_skills = self.unlocked_skills.get(specialist.id, set())
        return all(prereq in unlocked_skills for prereq in skill.prerequisites)

    def _apply_skill_effects(self, specialist: Specialist, skill: Skill) -> None:
        """Apply skill effects to a specialist.

        Args:
            specialist: The specialist to apply effects to
            skill: The skill whose effects to apply
        """
        # Skill effects are applied dynamically through get_specialist_skill_effects()
        # This method can be extended for immediate effect application if needed
        pass

    def _on_specialist_leveled_up(self, event_data: Dict) -> None:
        """Handle specialist level up event.

        Args:
            event_data: Event data containing specialist information
        """
        if not self._game_state:
            return

        specialist_id = event_data.get("specialist_id")
        if not specialist_id:
            return

        specialist = next((s for s in self._game_state.specialists if s.id == specialist_id), None)
        if not specialist:
            return

        # Award skill points based on game config
        skill_points_per_level = 1  # Default value, can be configured later
        specialist.skill_points += skill_points_per_level

        self.logger.info(f"Awarded {skill_points_per_level} skill points to {specialist.name}")

    def _on_specialist_created(self, event_data: Dict) -> None:
        """Handle specialist creation event.

        Args:
            event_data: Event data containing specialist information
        """
        specialist_id = event_data.get("specialist_id")
        if specialist_id:
            self.unlocked_skills[specialist_id] = set()