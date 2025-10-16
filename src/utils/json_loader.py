"""JSON loader utility module with validation and hot-reload capabilities.

This module provides functions to load, validate, and hot-reload JSON configuration
files for the cybersecurity firm game. All game data is stored in JSON format for
easy editing and balance tuning.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
import jsonschema
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)


class JSONLoader:
    """Handles loading and validation of JSON configuration files."""
    
    def __init__(self, data_dir: str = "data", schema_dir: str = "data/schemas"):
        """Initialize the JSON loader.
        
        Args:
            data_dir: Directory containing JSON data files
            schema_dir: Directory containing JSON schema files
        """
        self.data_dir = Path(data_dir)
        self.schema_dir = Path(schema_dir)
        self._schemas: Dict[str, Dict] = {}
        self._data_cache: Dict[str, Any] = {}
        self._file_timestamps: Dict[str, float] = {}
        
        logger.info(f"JSONLoader initialized: data_dir={data_dir}, schema_dir={schema_dir}")
    
    def load_schema(self, schema_name: str) -> Dict:
        """Load a JSON schema file.
        
        Args:
            schema_name: Name of the schema file (e.g., 'specialist_schema.json')
            
        Returns:
            Dictionary containing the schema definition
            
        Raises:
            FileNotFoundError: If schema file doesn't exist
            json.JSONDecodeError: If schema file is malformed
        """
        if schema_name in self._schemas:
            return self._schemas[schema_name]
        
        schema_path = self.schema_dir / schema_name
        
        if not schema_path.exists():
            logger.error(f"Schema file not found: {schema_path}")
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            self._schemas[schema_name] = schema
            logger.debug(f"Loaded schema: {schema_name}")
            return schema
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse schema {schema_name}: {e}")
            raise
    
    def load_data(self, filename: str, schema_name: Optional[str] = None, 
                  validate_data: bool = True) -> Any:
        """Load a JSON data file with optional validation.
        
        Args:
            filename: Name of the data file (e.g., 'specialists.json')
            schema_name: Name of the schema file to validate against (optional)
            validate_data: Whether to validate data against schema
            
        Returns:
            Parsed JSON data
            
        Raises:
            FileNotFoundError: If data file doesn't exist
            json.JSONDecodeError: If data file is malformed
            ValidationError: If data doesn't match schema
        """
        data_path = self.data_dir / filename
        
        if not data_path.exists():
            logger.error(f"Data file not found: {data_path}")
            raise FileNotFoundError(f"Data file not found: {data_path}")
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update file timestamp for hot-reload tracking
            self._file_timestamps[filename] = os.path.getmtime(data_path)
            
            # Validate against schema if provided
            if validate_data and schema_name:
                schema = self.load_schema(schema_name)
                self.validate_data(data, schema, filename)
            
            # Cache the data
            self._data_cache[filename] = data
            logger.info(f"Loaded data file: {filename}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse data file {filename}: {e}")
            raise
    
    def validate_data(self, data: Any, schema: Dict, filename: str = "") -> bool:
        """Validate data against a JSON schema.
        
        Args:
            data: Data to validate
            schema: JSON schema definition
            filename: Optional filename for error reporting
            
        Returns:
            True if validation succeeds
            
        Raises:
            ValidationError: If data doesn't match schema
        """
        try:
            validate(instance=data, schema=schema)
            logger.debug(f"Validation successful: {filename}")
            return True
        except ValidationError as e:
            logger.error(f"Validation failed for {filename}: {e.message}")
            logger.error(f"Failed path: {' -> '.join(str(p) for p in e.path)}")
            raise
    
    def load_all_game_data(self) -> Dict[str, Any]:
        """Load all game data files with validation.
        
        Returns:
            Dictionary containing all game data:
            {
                'specialists': [...],
                'incidents': [...],
                'clients': [...],
                'automation_scripts': [...],
                'game_config': {...}
            }
        """
        logger.info("Loading all game data...")
        
        game_data = {}
        
        try:
            # Load specialists
            specialists_data = self.load_data(
                'specialists.json', 
                'specialist_schema.json'
            )
            game_data['specialists'] = specialists_data.get('specialists', [])
            
            # Load incidents
            incidents_data = self.load_data(
                'incidents.json',
                'incident_schema.json'
            )
            game_data['incidents'] = incidents_data.get('incident_types', [])
            
            # Load clients
            clients_data = self.load_data(
                'clients.json',
                'client_schema.json'
            )
            game_data['clients'] = clients_data.get('clients', [])
            
            # Load automation scripts
            automation_data = self.load_data(
                'automation_scripts.json',
                'automation_script_schema.json'
            )
            game_data['automation_scripts'] = automation_data.get('automation_scripts', [])
            
            # Load game config (no schema validation for now)
            game_data['game_config'] = self.load_data(
                'game_config.json',
                validate_data=False
            )
            
            logger.info("Successfully loaded all game data")
            return game_data
            
        except Exception as e:
            logger.error(f"Failed to load game data: {e}")
            raise
    
    def check_for_updates(self) -> Dict[str, bool]:
        """Check if any cached files have been modified on disk.
        
        Returns:
            Dictionary mapping filenames to whether they've been modified
        """
        updates = {}
        
        for filename, cached_timestamp in self._file_timestamps.items():
            data_path = self.data_dir / filename
            
            if not data_path.exists():
                logger.warning(f"Previously loaded file no longer exists: {filename}")
                updates[filename] = False
                continue
            
            current_timestamp = os.path.getmtime(data_path)
            
            if current_timestamp > cached_timestamp:
                logger.info(f"File modified: {filename}")
                updates[filename] = True
            else:
                updates[filename] = False
        
        return updates
    
    def hot_reload(self, filename: str, schema_name: Optional[str] = None) -> Any:
        """Hot-reload a data file if it has been modified.
        
        Args:
            filename: Name of the data file to reload
            schema_name: Optional schema to validate against
            
        Returns:
            Reloaded data if file was modified, cached data otherwise
        """
        data_path = self.data_dir / filename
        
        if not data_path.exists():
            logger.error(f"Cannot reload non-existent file: {filename}")
            return self._data_cache.get(filename)
        
        current_timestamp = os.path.getmtime(data_path)
        cached_timestamp = self._file_timestamps.get(filename, 0)
        
        if current_timestamp > cached_timestamp:
            logger.info(f"Hot-reloading modified file: {filename}")
            try:
                return self.load_data(filename, schema_name)
            except Exception as e:
                logger.error(f"Hot-reload failed for {filename}: {e}")
                logger.info(f"Returning cached data for {filename}")
                return self._data_cache.get(filename)
        
        logger.debug(f"No changes detected for {filename}")
        return self._data_cache.get(filename)
    
    def save_data(self, filename: str, data: Any, validate_before_save: bool = True,
                  schema_name: Optional[str] = None) -> bool:
        """Save data to a JSON file with optional validation.
        
        Args:
            filename: Name of the file to save
            data: Data to save
            validate_before_save: Whether to validate before saving
            schema_name: Schema to validate against if validate_before_save is True
            
        Returns:
            True if save was successful
        """
        data_path = self.data_dir / filename
        
        # Validate before saving if requested
        if validate_before_save and schema_name:
            try:
                schema = self.load_schema(schema_name)
                self.validate_data(data, schema, filename)
            except ValidationError as e:
                logger.error(f"Cannot save {filename}: validation failed")
                return False
        
        try:
            # Create backup of existing file
            if data_path.exists():
                backup_path = data_path.with_suffix('.json.bak')
                data_path.rename(backup_path)
                logger.debug(f"Created backup: {backup_path}")
            
            # Write new data
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Update cache and timestamp
            self._data_cache[filename] = data
            self._file_timestamps[filename] = os.path.getmtime(data_path)
            
            logger.info(f"Successfully saved data to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save {filename}: {e}")
            # Restore backup if it exists
            backup_path = data_path.with_suffix('.json.bak')
            if backup_path.exists():
                backup_path.rename(data_path)
                logger.info("Restored backup after save failure")
            return False


# Convenience functions for common operations

def load_game_data(data_dir: str = "data") -> Dict[str, Any]:
    """Convenience function to load all game data.
    
    Args:
        data_dir: Directory containing data files
        
    Returns:
        Dictionary containing all game data
    """
    loader = JSONLoader(data_dir=data_dir)
    return loader.load_all_game_data()
