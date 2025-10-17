"""Tests for Feature Manager."""

import pytest
import os
import tempfile
import json
from src.core.feature_manager import FeatureManager, FeatureConfig


class TestFeatureManager:
    """Test suite for FeatureManager."""
    
    def test_initialization(self):
        """Test feature manager initializes correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"features": []}, f)
            config_path = f.name
        
        try:
            manager = FeatureManager(config_path)
            assert manager.config_path == config_path
        finally:
            os.unlink(config_path)
    
    def test_is_enabled_basic(self):
        """Test basic feature enabled check."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "features": [
                    {"id": "feature1", "enabled": True},
                    {"id": "feature2", "enabled": False}
                ]
            }, f)
            config_path = f.name
        
        try:
            manager = FeatureManager(config_path)
            assert manager.is_enabled("feature1") is True
            assert manager.is_enabled("feature2") is False
            assert manager.is_enabled("nonexistent") is False
        finally:
            os.unlink(config_path)
    
    def test_rollout_percentage(self):
        """Test percentage-based rollout."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "features": [
                    {"id": "feature1", "enabled": True, "rollout_percentage": 0.0},
                    {"id": "feature2", "enabled": True, "rollout_percentage": 100.0}
                ]
            }, f)
            config_path = f.name
        
        try:
            manager = FeatureManager(config_path)
            # 0% rollout should always be disabled
            assert manager.is_enabled("feature1") is False
            # 100% rollout should always be enabled
            assert manager.is_enabled("feature2") is True
        finally:
            os.unlink(config_path)
    
    def test_dependencies(self):
        """Test feature dependencies."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "features": [
                    {"id": "base", "enabled": True},
                    {"id": "dependent", "enabled": True, "dependencies": ["base"]},
                    {"id": "broken", "enabled": True, "dependencies": ["missing"]}
                ]
            }, f)
            config_path = f.name
        
        try:
            manager = FeatureManager(config_path)
            
            # Dependent should be enabled when base is enabled
            assert manager.is_enabled("dependent", check_dependencies=True) is True
            
            # Broken should be disabled due to missing dependency
            assert manager.is_enabled("broken", check_dependencies=True) is False
        finally:
            os.unlink(config_path)
    
    def test_get_feature(self):
        """Test getting feature configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "features": [
                    {
                        "id": "test",
                        "enabled": True,
                        "rollout_percentage": 50.0,
                        "description": "Test feature"
                    }
                ]
            }, f)
            config_path = f.name
        
        try:
            manager = FeatureManager(config_path)
            feature = manager.get_feature("test")
            
            assert feature is not None
            assert feature.id == "test"
            assert feature.enabled is True
            assert feature.rollout_percentage == 50.0
            assert feature.description == "Test feature"
        finally:
            os.unlink(config_path)
    
    def test_set_enabled(self):
        """Test enabling/disabling features at runtime."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "features": [
                    {"id": "test", "enabled": False}
                ]
            }, f)
            config_path = f.name
        
        try:
            manager = FeatureManager(config_path)
            assert manager.is_enabled("test") is False
            
            manager.set_enabled("test", True)
            assert manager.is_enabled("test") is True
            
            manager.set_enabled("test", False)
            assert manager.is_enabled("test") is False
        finally:
            os.unlink(config_path)
    
    def test_set_rollout_percentage(self):
        """Test changing rollout percentage."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "features": [
                    {"id": "test", "enabled": True, "rollout_percentage": 50.0}
                ]
            }, f)
            config_path = f.name
        
        try:
            manager = FeatureManager(config_path)
            
            manager.set_rollout_percentage("test", 0.0)
            feature = manager.get_feature("test")
            assert feature.rollout_percentage == 0.0
            
            manager.set_rollout_percentage("test", 100.0)
            feature = manager.get_feature("test")
            assert feature.rollout_percentage == 100.0
        finally:
            os.unlink(config_path)
    
    def test_validate_dependencies(self):
        """Test dependency validation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "features": [
                    {"id": "base", "enabled": True},
                    {"id": "valid", "enabled": True, "dependencies": ["base"]},
                    {"id": "invalid", "enabled": True, "dependencies": ["missing"]}
                ]
            }, f)
            config_path = f.name
        
        try:
            manager = FeatureManager(config_path)
            errors = manager.validate_dependencies()
            
            # Should have error for invalid feature
            assert len(errors) > 0
            assert any("invalid" in err and "missing" in err for err in errors)
        finally:
            os.unlink(config_path)
    
    def test_get_enabled_features(self):
        """Test getting list of enabled features."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "features": [
                    {"id": "enabled1", "enabled": True},
                    {"id": "disabled", "enabled": False},
                    {"id": "enabled2", "enabled": True}
                ]
            }, f)
            config_path = f.name
        
        try:
            manager = FeatureManager(config_path)
            enabled = manager.get_enabled_features()
            
            assert "enabled1" in enabled
            assert "enabled2" in enabled
            assert "disabled" not in enabled
        finally:
            os.unlink(config_path)
    
    def test_reload(self):
        """Test hot-reloading configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "features": [
                    {"id": "test", "enabled": False}
                ]
            }, f)
            config_path = f.name
        
        try:
            manager = FeatureManager(config_path)
            assert manager.is_enabled("test") is False
            
            # Update file
            with open(config_path, 'w') as f:
                json.dump({
                    "features": [
                        {"id": "test", "enabled": True}
                    ]
                }, f)
            
            manager.reload()
            assert manager.is_enabled("test") is True
        finally:
            os.unlink(config_path)
