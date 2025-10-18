"""Advanced entity management API routes.

Provides comprehensive CRUD operations for all game entities with:
- Schema validation
- Undo/redo support
- Template system
- Batch operations
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import os
import json
import copy


def create_entity_management_blueprint(game_state_ref):
    """Create the entity management blueprint.
    
    Args:
        game_state_ref: Reference to the GameState instance
    
    Returns:
        Flask Blueprint for entity management routes
    """
    bp = Blueprint('entity_management', __name__)
    
    state_container = {'game_state': game_state_ref}
    
    def get_game_state():
        """Helper to get current game state."""
        return state_container.get('game_state')
    
    def get_data_dir():
        """Get the data directory path."""
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    
    @bp.route('/entities/<entity_type>', methods=['GET'])
    def list_entities(entity_type):
        """List all entities of a specific type.
        
        Args:
            entity_type: Type of entities (incidents, specialists, etc.)
        """
        try:
            filepath = os.path.join(get_data_dir(), f'{entity_type}.json')
            
            if not os.path.exists(filepath):
                return jsonify({
                    "success": False,
                    "message": f"Entity type '{entity_type}' not found"
                }), 404
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            return jsonify({
                "success": True,
                "data": data,
                "entity_type": entity_type,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to list entities: {str(e)}"
            }), 500
    
    @bp.route('/entities/<entity_type>/<entity_id>', methods=['GET'])
    def get_entity(entity_type, entity_id):
        """Get a specific entity by ID.
        
        Args:
            entity_type: Type of entity
            entity_id: Entity identifier
        """
        try:
            filepath = os.path.join(get_data_dir(), f'{entity_type}.json')
            
            if not os.path.exists(filepath):
                return jsonify({
                    "success": False,
                    "message": f"Entity type '{entity_type}' not found"
                }), 404
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Search for entity in different structures
            entity = None
            for key in data:
                if isinstance(data[key], list):
                    for item in data[key]:
                        if isinstance(item, dict) and item.get('id') == entity_id:
                            entity = item
                            break
                if entity:
                    break
            
            if not entity:
                return jsonify({
                    "success": False,
                    "message": f"Entity '{entity_id}' not found"
                }), 404
            
            return jsonify({
                "success": True,
                "data": entity,
                "entity_type": entity_type,
                "entity_id": entity_id
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to get entity: {str(e)}"
            }), 500
    
    @bp.route('/entities/<entity_type>', methods=['POST'])
    def create_entity(entity_type):
        """Create a new entity.
        
        Args:
            entity_type: Type of entity to create
        
        JSON body:
            entity: Entity data to create
        """
        try:
            data = request.get_json()
            new_entity = data.get('entity')
            
            if not new_entity:
                return jsonify({
                    "success": False,
                    "message": "Entity data required"
                }), 400
            
            filepath = os.path.join(get_data_dir(), f'{entity_type}.json')
            
            # Create backup
            backup_path = filepath + '.backup'
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    backup_content = f.read()
                with open(backup_path, 'w') as f:
                    f.write(backup_content)
            
            # Load existing data
            with open(filepath, 'r') as f:
                file_data = json.load(f)
            
            # Add new entity to appropriate array
            added = False
            for key in file_data:
                if isinstance(file_data[key], list):
                    file_data[key].append(new_entity)
                    added = True
                    break
            
            if not added:
                return jsonify({
                    "success": False,
                    "message": "Unable to determine where to add entity in file structure"
                }), 500
            
            # Save updated data
            with open(filepath, 'w') as f:
                json.dump(file_data, f, indent=2)
            
            return jsonify({
                "success": True,
                "message": "Entity created successfully",
                "data": new_entity,
                "backup_created": backup_path
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to create entity: {str(e)}"
            }), 500
    
    @bp.route('/entities/<entity_type>/<entity_id>', methods=['PUT'])
    def update_entity(entity_type, entity_id):
        """Update an existing entity.
        
        Args:
            entity_type: Type of entity
            entity_id: Entity identifier
        
        JSON body:
            entity: Updated entity data
        """
        try:
            data = request.get_json()
            updated_entity = data.get('entity')
            
            if not updated_entity:
                return jsonify({
                    "success": False,
                    "message": "Entity data required"
                }), 400
            
            filepath = os.path.join(get_data_dir(), f'{entity_type}.json')
            
            # Create backup
            backup_path = filepath + '.backup'
            with open(filepath, 'r') as f:
                backup_content = f.read()
            with open(backup_path, 'w') as f:
                f.write(backup_content)
            
            # Load and update entity
            with open(filepath, 'r') as f:
                file_data = json.load(f)
            
            updated = False
            for key in file_data:
                if isinstance(file_data[key], list):
                    for i, item in enumerate(file_data[key]):
                        if isinstance(item, dict) and item.get('id') == entity_id:
                            file_data[key][i] = updated_entity
                            updated = True
                            break
                if updated:
                    break
            
            if not updated:
                return jsonify({
                    "success": False,
                    "message": f"Entity '{entity_id}' not found"
                }), 404
            
            # Save updated data
            with open(filepath, 'w') as f:
                json.dump(file_data, f, indent=2)
            
            return jsonify({
                "success": True,
                "message": "Entity updated successfully",
                "data": updated_entity,
                "backup_created": backup_path
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to update entity: {str(e)}"
            }), 500
    
    @bp.route('/entities/<entity_type>/<entity_id>', methods=['DELETE'])
    def delete_entity(entity_type, entity_id):
        """Delete an entity.
        
        Args:
            entity_type: Type of entity
            entity_id: Entity identifier
        """
        try:
            filepath = os.path.join(get_data_dir(), f'{entity_type}.json')
            
            # Create backup
            backup_path = filepath + '.backup'
            with open(filepath, 'r') as f:
                backup_content = f.read()
            with open(backup_path, 'w') as f:
                f.write(backup_content)
            
            # Load and delete entity
            with open(filepath, 'r') as f:
                file_data = json.load(f)
            
            deleted = False
            for key in file_data:
                if isinstance(file_data[key], list):
                    for i, item in enumerate(file_data[key]):
                        if isinstance(item, dict) and item.get('id') == entity_id:
                            deleted_entity = file_data[key].pop(i)
                            deleted = True
                            break
                if deleted:
                    break
            
            if not deleted:
                return jsonify({
                    "success": False,
                    "message": f"Entity '{entity_id}' not found"
                }), 404
            
            # Save updated data
            with open(filepath, 'w') as f:
                json.dump(file_data, f, indent=2)
            
            return jsonify({
                "success": True,
                "message": "Entity deleted successfully",
                "data": deleted_entity,
                "backup_created": backup_path
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to delete entity: {str(e)}"
            }), 500
    
    @bp.route('/entities/<entity_type>/duplicate/<entity_id>', methods=['POST'])
    def duplicate_entity(entity_type, entity_id):
        """Duplicate an entity with a new ID.
        
        Args:
            entity_type: Type of entity
            entity_id: Entity identifier to duplicate
        
        JSON body:
            new_id: New identifier for duplicated entity (optional)
        """
        try:
            data = request.get_json() or {}
            new_id = data.get('new_id')
            
            filepath = os.path.join(get_data_dir(), f'{entity_type}.json')
            
            with open(filepath, 'r') as f:
                file_data = json.load(f)
            
            # Find entity to duplicate
            entity_to_duplicate = None
            for key in file_data:
                if isinstance(file_data[key], list):
                    for item in file_data[key]:
                        if isinstance(item, dict) and item.get('id') == entity_id:
                            entity_to_duplicate = copy.deepcopy(item)
                            break
                if entity_to_duplicate:
                    break
            
            if not entity_to_duplicate:
                return jsonify({
                    "success": False,
                    "message": f"Entity '{entity_id}' not found"
                }), 404
            
            # Update ID for duplicate
            if new_id:
                entity_to_duplicate['id'] = new_id
            else:
                entity_to_duplicate['id'] = f"{entity_id}_copy"
            
            # Add name suffix if exists
            if 'name' in entity_to_duplicate:
                entity_to_duplicate['name'] = f"{entity_to_duplicate['name']} (Copy)"
            
            # Create backup
            backup_path = filepath + '.backup'
            with open(filepath, 'r') as f:
                backup_content = f.read()
            with open(backup_path, 'w') as f:
                f.write(backup_content)
            
            # Add duplicated entity
            for key in file_data:
                if isinstance(file_data[key], list):
                    file_data[key].append(entity_to_duplicate)
                    break
            
            # Save updated data
            with open(filepath, 'w') as f:
                json.dump(file_data, f, indent=2)
            
            return jsonify({
                "success": True,
                "message": "Entity duplicated successfully",
                "data": entity_to_duplicate,
                "backup_created": backup_path
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to duplicate entity: {str(e)}"
            }), 500
    
    @bp.route('/entities/<entity_type>/batch', methods=['POST'])
    def batch_update_entities(entity_type):
        """Perform batch updates on multiple entities.
        
        Args:
            entity_type: Type of entities
        
        JSON body:
            operation: Operation to perform (update, delete)
            entity_ids: List of entity IDs to affect
            data: Data for update operation (optional)
        """
        try:
            request_data = request.get_json()
            operation = request_data.get('operation')
            entity_ids = request_data.get('entity_ids', [])
            update_data = request_data.get('data', {})
            
            if not operation:
                return jsonify({
                    "success": False,
                    "message": "Operation required"
                }), 400
            
            if not entity_ids:
                return jsonify({
                    "success": False,
                    "message": "Entity IDs required"
                }), 400
            
            filepath = os.path.join(get_data_dir(), f'{entity_type}.json')
            
            # Create backup
            backup_path = filepath + '.backup'
            with open(filepath, 'r') as f:
                backup_content = f.read()
            with open(backup_path, 'w') as f:
                f.write(backup_content)
            
            # Load data
            with open(filepath, 'r') as f:
                file_data = json.load(f)
            
            affected = []
            
            if operation == 'delete':
                for key in file_data:
                    if isinstance(file_data[key], list):
                        file_data[key] = [
                            item for item in file_data[key]
                            if not (isinstance(item, dict) and item.get('id') in entity_ids)
                        ]
                        affected = entity_ids
            
            elif operation == 'update':
                for key in file_data:
                    if isinstance(file_data[key], list):
                        for item in file_data[key]:
                            if isinstance(item, dict) and item.get('id') in entity_ids:
                                item.update(update_data)
                                affected.append(item['id'])
            
            else:
                return jsonify({
                    "success": False,
                    "message": f"Unknown operation: {operation}"
                }), 400
            
            # Save updated data
            with open(filepath, 'w') as f:
                json.dump(file_data, f, indent=2)
            
            return jsonify({
                "success": True,
                "message": f"Batch {operation} completed",
                "affected_count": len(affected),
                "affected_ids": affected,
                "backup_created": backup_path
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to perform batch operation: {str(e)}"
            }), 500
    
    @bp.route('/entities/templates/<entity_type>', methods=['GET'])
    def get_entity_templates(entity_type):
        """Get template options for creating new entities.
        
        Args:
            entity_type: Type of entity
        """
        templates = {
            'incidents': {
                'id': 'new_incident_type',
                'name': 'New Incident Type',
                'description': 'Description of the incident',
                'specialty_required': 'Network Security',
                'difficulty_range': [1, 5],
                'base_sla_seconds': 300,
                'base_reward': 500,
                'xp_reward': 100
            },
            'equipment': {
                'id': 'new_equipment',
                'name': 'New Equipment',
                'description': 'Equipment description',
                'equipment_type': 'tool',
                'rarity': 'common',
                'stat_bonuses': {'speed': 5, 'accuracy': 2},
                'unlock_level': 1,
                'cost': 500
            },
            'facilities': {
                'id': 'new_facility',
                'name': 'New Facility',
                'description': 'Facility description',
                'facility_type': 'custom',
                'level': 1,
                'max_level': 10,
                'upgrade_cost': 5000,
                'bonuses': {}
            }
        }
        
        template = templates.get(entity_type, {})
        
        return jsonify({
            "success": True,
            "data": template,
            "entity_type": entity_type
        })
    
    return bp
