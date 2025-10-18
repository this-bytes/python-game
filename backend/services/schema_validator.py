"""Schema validation service for game entities.

Provides JSON schema validation for all entity types to ensure data integrity.
"""
import os
import json
from typing import Dict, Any, Optional, Tuple
import jsonschema
from jsonschema import validate, ValidationError


class SchemaValidator:
    """Validates game entity data against JSON schemas."""
    
    def __init__(self, schemas_dir: Optional[str] = None):
        """Initialize the schema validator.
        
        Args:
            schemas_dir: Path to schemas directory. If None, uses default.
        """
        if schemas_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            schemas_dir = os.path.join(base_dir, 'data', 'schemas')
        
        self.schemas_dir = schemas_dir
        self.schemas: Dict[str, Dict] = {}
        self._load_schemas()
    
    def _load_schemas(self) -> None:
        """Load all JSON schemas from the schemas directory."""
        if not os.path.exists(self.schemas_dir):
            print(f"Warning: Schemas directory not found: {self.schemas_dir}")
            return
        
        for filename in os.listdir(self.schemas_dir):
            if filename.endswith('_schema.json'):
                entity_type = filename.replace('_schema.json', '')
                schema_path = os.path.join(self.schemas_dir, filename)
                
                try:
                    with open(schema_path, 'r') as f:
                        schema = json.load(f)
                        self.schemas[entity_type] = schema
                        print(f"Loaded schema: {entity_type}")
                except Exception as e:
                    print(f"Error loading schema {filename}: {e}")
    
    def get_schema(self, entity_type: str) -> Optional[Dict]:
        """Get schema for a specific entity type.
        
        Args:
            entity_type: Type of entity (e.g., 'client', 'incident')
        
        Returns:
            Schema dictionary or None if not found
        """
        return self.schemas.get(entity_type)
    
    def get_all_schemas(self) -> Dict[str, Dict]:
        """Get all loaded schemas.
        
        Returns:
            Dictionary mapping entity types to their schemas
        """
        return self.schemas.copy()
    
    def validate_entity(self, entity_type: str, entity_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate a single entity against its schema.
        
        Args:
            entity_type: Type of entity (e.g., 'client', 'incident')
            entity_data: Entity data to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        schema = self.get_schema(entity_type)
        
        if not schema:
            return True, None  # No schema available, skip validation
        
        # Extract the entity schema from the file schema
        # Most schemas define the full file structure, we need just the item schema
        entity_schema = None
        
        if 'properties' in schema:
            # Find the array property that contains entities
            for prop_name, prop_schema in schema['properties'].items():
                if prop_schema.get('type') == 'array' and 'items' in prop_schema:
                    entity_schema = prop_schema['items']
                    break
        
        if not entity_schema:
            return True, None  # Could not extract entity schema
        
        try:
            validate(instance=entity_data, schema=entity_schema)
            return True, None
        except ValidationError as e:
            error_path = ' -> '.join(str(p) for p in e.path) if e.path else 'root'
            error_msg = f"Validation error at {error_path}: {e.message}"
            return False, error_msg
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def validate_file_data(self, entity_type: str, file_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate entire file data structure against its schema.
        
        Args:
            entity_type: Type of entity file (e.g., 'clients', 'incidents')
            file_data: Complete file data to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        schema = self.get_schema(entity_type)
        
        if not schema:
            return True, None  # No schema available, skip validation
        
        try:
            validate(instance=file_data, schema=schema)
            return True, None
        except ValidationError as e:
            error_path = ' -> '.join(str(p) for p in e.path) if e.path else 'root'
            error_msg = f"Validation error at {error_path}: {e.message}"
            return False, error_msg
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def is_id_immutable(self, entity_type: str) -> bool:
        """Check if ID field should be immutable for this entity type.
        
        Args:
            entity_type: Type of entity
        
        Returns:
            True if ID should be immutable
        """
        # All entity types should have immutable IDs
        return True
    
    def get_id_pattern(self, entity_type: str) -> Optional[str]:
        """Get the ID pattern/format for an entity type.
        
        Args:
            entity_type: Type of entity
        
        Returns:
            Regex pattern for ID or None
        """
        schema = self.get_schema(entity_type)
        
        if not schema or 'properties' not in schema:
            return None
        
        # Extract entity items schema
        for prop_schema in schema['properties'].values():
            if prop_schema.get('type') == 'array' and 'items' in prop_schema:
                items_schema = prop_schema['items']
                if 'properties' in items_schema and 'id' in items_schema['properties']:
                    id_schema = items_schema['properties']['id']
                    return id_schema.get('pattern')
        
        return None
