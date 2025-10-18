"""Schema API routes.

Provides endpoints for retrieving JSON schemas for entity validation.
"""
from flask import Blueprint, jsonify
from datetime import datetime
from backend.services.schema_validator import SchemaValidator


def create_schemas_blueprint():
    """Create the schemas blueprint.
    
    Returns:
        Flask Blueprint for schema routes
    """
    bp = Blueprint('schemas', __name__)
    
    # Initialize schema validator
    schema_validator = SchemaValidator()
    
    @bp.route('/schemas', methods=['GET'])
    def list_schemas():
        """List all available schemas.
        
        Returns:
            JSON response with list of available schema types
        """
        try:
            schemas = schema_validator.get_all_schemas()
            
            schema_list = []
            for entity_type, schema in schemas.items():
                schema_list.append({
                    'entity_type': entity_type,
                    'title': schema.get('title', entity_type),
                    'description': schema.get('description', ''),
                    'id_pattern': schema_validator.get_id_pattern(entity_type)
                })
            
            return jsonify({
                "success": True,
                "data": schema_list,
                "count": len(schema_list),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to list schemas: {str(e)}"
            }), 500
    
    @bp.route('/schemas/<entity_type>', methods=['GET'])
    def get_schema(entity_type):
        """Get schema for a specific entity type.
        
        Args:
            entity_type: Type of entity (e.g., 'client', 'incident')
        
        Returns:
            JSON response with schema definition
        """
        try:
            schema = schema_validator.get_schema(entity_type)
            
            if not schema:
                return jsonify({
                    "success": False,
                    "message": f"Schema not found for entity type: {entity_type}"
                }), 404
            
            return jsonify({
                "success": True,
                "data": {
                    "entity_type": entity_type,
                    "schema": schema,
                    "id_pattern": schema_validator.get_id_pattern(entity_type),
                    "id_immutable": schema_validator.is_id_immutable(entity_type)
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to get schema: {str(e)}"
            }), 500
    
    @bp.route('/schemas/<entity_type>/validate', methods=['POST'])
    def validate_entity_data(entity_type):
        """Validate entity data against schema.
        
        Args:
            entity_type: Type of entity
        
        Request JSON:
            entity: Entity data to validate
        
        Returns:
            JSON response indicating if data is valid
        """
        try:
            from flask import request
            data = request.get_json()
            
            if not data or 'entity' not in data:
                return jsonify({
                    "success": False,
                    "message": "Entity data required"
                }), 400
            
            entity_data = data['entity']
            is_valid, error_message = schema_validator.validate_entity(entity_type, entity_data)
            
            if is_valid:
                return jsonify({
                    "success": True,
                    "valid": True,
                    "message": "Entity data is valid",
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": True,
                    "valid": False,
                    "message": "Entity data is invalid",
                    "errors": [error_message],
                    "timestamp": datetime.utcnow().isoformat()
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Validation failed: {str(e)}"
            }), 500
    
    return bp
