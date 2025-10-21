"""Feature Flag Manager for safe feature deployment and A/B testing.

The Feature Manager enables toggling features on/off without code changes,
percentage-based rollout, and dependency validation between features.

All features are configured in data/features.json
"""

from typing import Dict, Any, Optional, Set, List
from dataclasses import dataclass
import random
import time
import json
import os


@dataclass
class FeatureConfig:
    """Configuration for a single feature."""
    id: str
    enabled: bool = False
    rollout_percentage: float = 100.0  # 0-100
    dependencies: Optional[List[str]] = None  # Required features
    description: str = ""
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.dependencies is None:
            self.dependencies = []


class FeatureManager:
    """Manages feature flags for safe deployment and experimentation.
    
    Features:
    - Hot-reload from JSON configuration
    - Percentage-based rollout (A/B testing)
    - Feature dependencies (e.g., prestige requires leveling)
    - Per-session rollout assignment (stable during session)
    
    Example:
        ```python
        manager = FeatureManager()
        
        if manager.is_enabled("prestige_system"):
            # Run prestige code
            pass
            
        # Check with dependencies
        if manager.is_enabled("advanced_automation", check_dependencies=True):
            # Only runs if dependencies are also enabled
            pass
        ```
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize feature manager.
        
        Args:
            config_path: Path to features.json (None = use default)
        """
        if config_path is None:
            # Find project root
            current_dir = os.getcwd()
            if os.path.basename(current_dir) == 'src':
                project_root = os.path.dirname(current_dir)
            else:
                project_root = current_dir
            config_path = os.path.join(project_root, "data", "features.json")
        
        self.config_path = config_path
        self._features: Dict[str, FeatureConfig] = {}
        self._rollout_assignments: Dict[str, bool] = {}  # Feature ID -> assigned state
        self._session_id = int(time.time())  # Unique session ID
        
        # Load features
        self.reload()
    
    def reload(self):
        """Reload feature configuration from JSON file.
        
        Preserves existing rollout assignments to maintain stability.
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                
                self._features.clear()
                for feature_data in data.get("features", []):
                    feature = FeatureConfig(
                        id=feature_data["id"],
                        enabled=feature_data.get("enabled", False),
                        rollout_percentage=feature_data.get("rollout_percentage", 100.0),
                        dependencies=feature_data.get("dependencies", []),
                        description=feature_data.get("description", "")
                    )
                    self._features[feature.id] = feature
            else:
                # Create default features file
                self._create_default_features()
        
        except Exception as e:
            print(f"Error loading features: {e}")
            # Continue with empty features rather than crashing
    
    def _create_default_features(self):
        """Create default features.json file."""
        default_features = {
            "features": [
                {
                    "id": "idle_core",
                    "enabled": True,
                    "rollout_percentage": 100.0,
                    "dependencies": [],
                    "description": "Core idle game mechanics with auto-assignment"
                },
                {
                    "id": "prestige_system",
                    "enabled": True,
                    "rollout_percentage": 100.0,
                    "dependencies": [],
                    "description": "Prestige/rebirth system for meta-progression"
                },
                {
                    "id": "achievement_system",
                    "enabled": True,
                    "rollout_percentage": 100.0,
                    "dependencies": [],
                    "description": "Achievement tracking and rewards"
                },
                {
                    "id": "contract_negotiation",
                    "enabled": False,
                    "rollout_percentage": 0.0,
                    "dependencies": [],
                    "description": "Contract negotiation mini-game"
                },
                {
                    "id": "specialist_relationships",
                    "enabled": False,
                    "rollout_percentage": 0.0,
                    "dependencies": [],
                    "description": "Specialist relationship and synergy system"
                }
            ]
        }
        
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_features, f, indent=2)
        except Exception as e:
            print(f"Error creating default features file: {e}")
    
    def is_enabled(
        self, 
        feature_id: str, 
        check_dependencies: bool = False,
        user_id: Optional[str] = None
    ) -> bool:
        """Check if a feature is enabled.
        
        Args:
            feature_id: Feature identifier
            check_dependencies: If True, also verify dependencies are enabled
            user_id: Optional user ID for rollout (uses session ID if None)
            
        Returns:
            True if feature is enabled and passes rollout check
        """
        if feature_id not in self._features:
            return False
        
        feature = self._features[feature_id]
        
        # Check if explicitly disabled
        if not feature.enabled:
            return False
        
        # Check dependencies
        if check_dependencies:
            for dep_id in (feature.dependencies or []):
                if not self.is_enabled(dep_id, check_dependencies=True, user_id=user_id):
                    return False
        
        # Check rollout percentage
        if feature.rollout_percentage < 100.0:
            # Use stable assignment for this session
            if feature_id not in self._rollout_assignments:
                # Assign based on hash of feature ID + user/session ID
                assignment_seed = feature_id + (user_id or str(self._session_id))
                random.seed(hash(assignment_seed))
                self._rollout_assignments[feature_id] = random.random() * 100 < feature.rollout_percentage
                random.seed()  # Reset seed
            
            return self._rollout_assignments[feature_id]
        
        return True
    
    def get_feature(self, feature_id: str) -> Optional[FeatureConfig]:
        """Get feature configuration.
        
        Args:
            feature_id: Feature identifier
            
        Returns:
            FeatureConfig or None if not found
        """
        return self._features.get(feature_id)
    
    def get_all_features(self) -> Dict[str, FeatureConfig]:
        """Get all feature configurations.
        
        Returns:
            Dictionary of feature ID to FeatureConfig
        """
        return self._features.copy()
    
    def set_enabled(self, feature_id: str, enabled: bool):
        """Enable or disable a feature at runtime.
        
        Args:
            feature_id: Feature identifier
            enabled: True to enable, False to disable
        """
        if feature_id in self._features:
            self._features[feature_id].enabled = enabled
    
    def set_rollout_percentage(self, feature_id: str, percentage: float):
        """Set rollout percentage for a feature.
        
        Args:
            feature_id: Feature identifier
            percentage: Rollout percentage (0-100)
        """
        if feature_id in self._features:
            self._features[feature_id].rollout_percentage = max(0.0, min(100.0, percentage))
            # Clear assignment to force re-evaluation
            if feature_id in self._rollout_assignments:
                del self._rollout_assignments[feature_id]
    
    def validate_dependencies(self) -> List[str]:
        """Validate all feature dependencies.
        
        Returns:
            List of error messages (empty if all valid)
        """
        errors = []
        
        for feature_id, feature in self._features.items():
            for dep_id in (feature.dependencies or []):
                if dep_id not in self._features:
                    errors.append(
                        f"Feature '{feature_id}' depends on unknown feature '{dep_id}'"
                    )
        
        # Check for circular dependencies
        for feature_id in self._features:
            if self._has_circular_dependency(feature_id):
                errors.append(f"Feature '{feature_id}' has circular dependency")
        
        return errors
    
    def _has_circular_dependency(
        self, 
        feature_id: str, 
        visited: Optional[Set[str]] = None
    ) -> bool:
        """Check if feature has circular dependency.
        
        Args:
            feature_id: Feature to check
            visited: Set of already visited features
            
        Returns:
            True if circular dependency detected
        """
        if visited is None:
            visited = set()
        
        if feature_id in visited:
            return True
        
        if feature_id not in self._features:
            return False
        
        visited.add(feature_id)
        
        feature = self._features[feature_id]
        for dep_id in (feature.dependencies or []):
            if self._has_circular_dependency(dep_id, visited.copy()):
                return True
        
        return False
    
    def get_enabled_features(self, check_dependencies: bool = False) -> List[str]:
        """Get list of currently enabled feature IDs.
        
        Args:
            check_dependencies: If True, only include features with satisfied dependencies
            
        Returns:
            List of enabled feature IDs
        """
        enabled = []
        for feature_id in self._features:
            if self.is_enabled(feature_id, check_dependencies=check_dependencies):
                enabled.append(feature_id)
        return enabled
    
    def save_to_file(self):
        """Save current feature configuration to JSON file."""
        try:
            features_data = {
                "features": [
                    {
                        "id": f.id,
                        "enabled": f.enabled,
                        "rollout_percentage": f.rollout_percentage,
                        "dependencies": f.dependencies,
                        "description": f.description
                    }
                    for f in self._features.values()
                ]
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(features_data, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving features: {e}")
            return False


# Global feature manager instance (singleton pattern)
_global_feature_manager: Optional[FeatureManager] = None


def get_feature_manager() -> FeatureManager:
    """Get the global feature manager instance.
    
    Returns:
        Global FeatureManager singleton
    """
    global _global_feature_manager
    if _global_feature_manager is None:
        _global_feature_manager = FeatureManager()
    return _global_feature_manager
