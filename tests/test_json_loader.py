"""Tests for JSON loader utility."""

import pytest
from pathlib import Path
from src.utils.json_loader import JSONLoader, load_game_data


def test_json_loader_initialization():
    """Test JSONLoader initialization."""
    loader = JSONLoader(data_dir="data", schema_dir="data/schemas")
    assert loader.data_dir == Path("data")
    assert loader.schema_dir == Path("data/schemas")


def test_load_schema():
    """Test loading a JSON schema file."""
    loader = JSONLoader()
    schema = loader.load_schema("specialist_schema.json")
    assert schema is not None
    assert "$schema" in schema
    assert schema["title"] == "Specialist"


def test_load_data():
    """Test loading a JSON data file."""
    loader = JSONLoader()
    data = loader.load_data("specialists.json", "specialist_schema.json")
    assert data is not None
    assert "specialists" in data
    assert len(data["specialists"]) > 0


def test_load_all_game_data():
    """Test loading all game data files."""
    data = load_game_data()
    assert "specialists" in data
    assert "incidents" in data
    assert "clients" in data
    assert "automation_scripts" in data
    assert "game_config" in data
    assert len(data["specialists"]) > 0
    assert len(data["incidents"]) > 0


def test_data_validation():
    """Test data validation against schema."""
    loader = JSONLoader()
    
    # Valid data should pass
    valid_specialist = {
        "id": "spec_999",
        "name": "Test Specialist",
        "specialty": "Network Security",
        "level": 1,
        "xp": 0,
        "stats": {
            "speed": 50,
            "accuracy": 50,
            "experience_bonus": 1.0
        },
        "status": "available"
    }
    
    schema = loader.load_schema("specialist_schema.json")
    assert loader.validate_data(valid_specialist, schema) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
