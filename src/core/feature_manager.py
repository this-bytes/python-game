"""Feature Flag System - Safe deployment and A/B testing.

Enables shipping features disabled by default, gradual rollout,
and instant rollback without redeployment.
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import json
import random
import logging
from pathlib import Path


@dataclass
class FeatureFlag:
    """Represents a feature flag configuration."""
    name: str
    enabled: bool = False
    rollout_percentage: int = 0  # 0-100
    dependencies: List[str] = field(default_factory=list)
    description: str = ""
    category: str = "general"
    version: str = "1.0.0"
    owner: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "enabled": self.enabled,
            "rollout_percentage": self.rollout_percentage,
            "dependencies": self.dependencies,
            "description": self.description,
            "category": self.category,
            "version": self.version,
            "owner": self.owner
        }
    
    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'FeatureFlag':
        """Create from dictionary."""
        return cls(
            name=name,
            enabled=data.get("enabled", False),
            rollout_percentage=data.get("rollout_percentage", 0),
            dependencies=data.get("dependencies", []),
            description=data.get("description", ""),
            category=data.get("category", "general"),
            version=data.get("version", "1.0.0"),
            owner=data.get("owner", "")
        )


class FeatureManager:
    """Manages feature flags and gradual rollouts.
    
    Features:
    - Enable/disable features at runtime
    - Gradual rollout (percentage-based)
    - Dependency management
    - Hot-reload from JSON
    - A/B testing support
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize feature manager.
        
        Args:
            config_path: Path to features.json file
        """
        self.logger = logging.getLogger("feature_manager")
        self._features: Dict[str, FeatureFlag] = {}
        self._user_bucket: int = random.randint(0, 99)  # For rollout percentage
        self._overrides: Dict[str, bool] = {}  # Runtime overrides
        
        if config_path is None:
            # Default to data/features.json
            config_path = Path(__file__).parent.parent.parent / "data" / "features.json"
        
        self.config_path = config_path
        self.load_features()
    
    def load_features(self):
        """Load feature flags from JSON file."""
        try:
            if not self.config_path.exists():
                self.logger.warning(f"Features config not found: {self.config_path}")
                self._create_default_config()
                return
            
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            
            self._features.clear()
            for name, feature_data in data.get("features", {}).items():
                self._features[name] = FeatureFlag.from_dict(name, feature_data)
            
            self.logger.info(f"Loaded {len(self._features)} feature flags")
            
        except Exception as e:
            self.logger.error(f"Failed to load features: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default features.json if it doesn't exist."""
        default_features = {
            "features": {
                "idle_mechanics": {
                    "enabled": True,
                    "rollout_percentage": 100,
                    "dependencies": [],
                    "description": "Auto-assignment and synergy system",
                    "category": "core",
                    "version": "1.0.0",
                    "owner": "core-team"
                },
                "dopamine_system": {
                    "enabled": True,
                    "rollout_percentage": 100,
                    "dependencies": [],
                    "description": "Combo system and visual feedback",
                    "category": "core",
                    "version": "1.0.0",
                    "owner": "core-team"
                },
                "prestige_system": {
                    "enabled": False,
                    "rollout_percentage": 0,
                    "dependencies": ["save_system"],
                    "description": "Rebirth and permanent upgrades",
                    "category": "progression",
                    "version": "1.0.0",
                    "owner": "progression-team"
                },
                "achievement_system": {
                    "enabled": False,
                    "rollout_percentage": 0,
                    "dependencies": [],
                    "description": "Achievement tracking and rewards",
                    "category": "progression",
                    "version": "1.0.0",
                    "owner": "progression-team"
                },
                "relationship_system": {
                    "enabled": False,
                    "rollout_percentage": 0,
                    "dependencies": ["specialist_system"],
                    "description": "Specialist relationships and drama",
                    "category": "social",
                    "version": "1.0.0",
                    "owner": "content-team"
                },
                "contract_negotiation": {
                    "enabled": False,
                    "rollout_percentage": 0,
                    "dependencies": ["contract_system"],
                    "description": "Interactive contract negotiation mini-game",
                    "category": "gameplay",
                    "version": "1.0.0",
                    "owner": "gameplay-team"
                },
                "office_decoration": {
                    "enabled": False,
                    "rollout_percentage": 0,
                    "dependencies": [],
                    "description": "Customize office with furniture and decorations",
                    "category": "cosmetic",
                    "version": "1.0.0",
                    "owner": "ui-team"
                },
                "specialist_training": {
                    "enabled": False,
                    "rollout_percentage": 0,
                    "dependencies": ["specialist_system"],
                    "description": "Send specialists to training courses",
                    "category": "progression",
                    "version": "1.0.0",
                    "owner": "progression-team"
                },
                "leaderboards": {
                    "enabled": False,
                    "rollout_percentage": 0,
                    "dependencies": ["backend_api"],
                    "description": "Global leaderboards and competition",
                    "category": "multiplayer",
                    "version": "1.0.0",
                    "owner": "multiplayer-team"
                },
                "live_events": {
                    "enabled": False,
                    "rollout_percentage": 0,
                    "dependencies": ["backend_api"],
                    "description": "Time-limited events and challenges",
                    "category": "live-ops",
                    "version": "1.0.0",
                    "owner": "liveops-team"
                }
            }
        }
        
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_features, f, indent=2)
            self.logger.info(f"Created default features config: {self.config_path}")
            self.load_features()
        except Exception as e:
            self.logger.error(f"Failed to create default config: {e}")
    
    def is_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled for current user.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            True if enabled, False otherwise
        """
        # Check runtime override first
        if feature_name in self._overrides:
            return self._overrides[feature_name]
        
        # Check if feature exists
        if feature_name not in self._features:
            self.logger.warning(f"Unknown feature: {feature_name}")
            return False
        
        feature = self._features[feature_name]
        
        # Check if explicitly disabled
        if not feature.enabled:
            return False
        
        # Check dependencies
        if not self._check_dependencies(feature):
            return False
        
        # Check rollout percentage
        if feature.rollout_percentage < 100:
            # User bucket determines if they're in the rollout
            return self._user_bucket < feature.rollout_percentage
        
        return True
    
    def _check_dependencies(self, feature: FeatureFlag) -> bool:
        """Check if all dependencies are enabled.
        
        Args:
            feature: Feature to check
            
        Returns:
            True if all dependencies met
        """
        for dep in feature.dependencies:
            if not self.is_enabled(dep):
                self.logger.debug(
                    f"Feature {feature.name} disabled due to missing dependency: {dep}"
                )
                return False
        return True
    
    def enable(self, feature_name: str, persist: bool = False):
        """Enable a feature at runtime.
        
        Args:
            feature_name: Feature to enable
            persist: If True, save to config file
        """
        if feature_name not in self._features:
            self.logger.warning(f"Cannot enable unknown feature: {feature_name}")
            return
        
        if persist:
            self._features[feature_name].enabled = True
            self._features[feature_name].rollout_percentage = 100
            self.save_features()
        else:
            self._overrides[feature_name] = True
        
        self.logger.info(f"Feature enabled: {feature_name} (persist={persist})")
    
    def disable(self, feature_name: str, persist: bool = False):
        """Disable a feature at runtime.
        
        Args:
            feature_name: Feature to disable
            persist: If True, save to config file
        """
        if feature_name not in self._features:
            self.logger.warning(f"Cannot disable unknown feature: {feature_name}")
            return
        
        if persist:
            self._features[feature_name].enabled = False
            self.save_features()
        else:
            self._overrides[feature_name] = False
        
        self.logger.info(f"Feature disabled: {feature_name} (persist={persist})")
    
    def set_rollout_percentage(self, feature_name: str, percentage: int):
        """Set rollout percentage for a feature.
        
        Args:
            feature_name: Feature name
            percentage: Percentage (0-100)
        """
        if feature_name not in self._features:
            self.logger.warning(f"Cannot set rollout for unknown feature: {feature_name}")
            return
        
        percentage = max(0, min(100, percentage))
        self._features[feature_name].rollout_percentage = percentage
        self.save_features()
        
        self.logger.info(f"Feature {feature_name} rollout set to {percentage}%")
    
    def save_features(self):
        """Save current features to JSON file."""
        try:
            data = {
                "features": {
                    name: feature.to_dict()
                    for name, feature in self._features.items()
                }
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info("Features saved to config")
            
        except Exception as e:
            self.logger.error(f"Failed to save features: {e}")
    
    def reload(self):
        """Reload features from config file."""
        self.load_features()
        self._overrides.clear()
        self.logger.info("Features reloaded from config")
    
    def get_all_features(self) -> Dict[str, FeatureFlag]:
        """Get all feature flags.
        
        Returns:
            Dictionary of all features
        """
        return self._features.copy()
    
    def get_enabled_features(self) -> List[str]:
        """Get list of currently enabled features.
        
        Returns:
            List of enabled feature names
        """
        return [name for name in self._features if self.is_enabled(name)]
    
    def get_features_by_category(self, category: str) -> Dict[str, FeatureFlag]:
        """Get features in a specific category.
        
        Args:
            category: Category name
            
        Returns:
            Dictionary of features in category
        """
        return {
            name: feature
            for name, feature in self._features.items()
            if feature.category == category
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get feature manager statistics.
        
        Returns:
            Statistics dictionary
        """
        enabled_count = len(self.get_enabled_features())
        return {
            "total_features": len(self._features),
            "enabled_features": enabled_count,
            "disabled_features": len(self._features) - enabled_count,
            "runtime_overrides": len(self._overrides),
            "user_bucket": self._user_bucket,
            "categories": len(set(f.category for f in self._features.values()))
        }


# Global feature manager instance
_global_feature_manager: Optional[FeatureManager] = None


def get_feature_manager() -> FeatureManager:
    """Get the global feature manager instance.
    
    Returns:
        Global FeatureManager instance
    """
    global _global_feature_manager
    if _global_feature_manager is None:
        _global_feature_manager = FeatureManager()
    return _global_feature_manager
