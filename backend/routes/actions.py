"""Player action processing endpoints.

Provides unified endpoint for all player actions following action-based architecture.
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os

# Add src to path for imports
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.utils.logger import GameLogger


def create_actions_blueprint(game_state_ref):
    """Create actions blueprint with game state reference.
    
    Args:
        game_state_ref: Reference to the GameState instance (legacy, use instance_manager instead)
        
    Returns:
        Flask Blueprint for action routes
    """
    bp = Blueprint('actions', __name__)
    logger = GameLogger("actions_api")
    
    # Import instance manager for multi-client support
    from backend.services.instance_manager import instance_manager
    
    # Store reference that can be updated (legacy support)
    state_container = {'game_state': game_state_ref}
    
    def get_game_state(instance_id: Optional[str] = None):
        """Helper to get current game state for a specific instance.
        
        Args:
            instance_id: Optional instance ID, uses default if not provided
            
        Returns:
            GameState instance or None
        """
        # Try instance manager first
        game_state = instance_manager.get_game_state(instance_id)
        
        # Fallback to legacy single state if no instance found
        if not game_state and instance_id is None:
            game_state = state_container.get('game_state')
        
        return game_state
    
    @bp.route('/action', methods=['POST'])
    def process_action():
        """Process player action for a specific game instance.
        
        Request body:
        {
            "instance_id": "optional-instance-id",  # Uses default if not provided
            "action_type": "assign_incident",
            "data": {
                "incident_id": "inc_001",
                "specialist_id": "spec_001"
            },
            "timestamp": 1697712000  # Optional
        }
        
        Returns:
            JSON response with success status and result
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "INVALID_ACTION",
                        "message": "Request body is required"
                    }
                }), 400
            
            # Extract instance_id from request
            instance_id = data.get('instance_id')
            
            # Get game state for this instance
            game_state = get_game_state(instance_id)
            if not game_state:
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "INVALID_STATE",
                        "message": f"Game state not initialized for instance: {instance_id or 'default'}"
                    }
                }), 503
            
            action_type = data.get('action_type')
            action_data = data.get('data', {})
            
            if not action_type:
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "INVALID_ACTION",
                        "message": "action_type is required"
                    }
                }), 400
            
            # Route to appropriate action handler
            if action_type == 'assign_incident':
                result = _handle_assign_incident(game_state, action_data)
            elif action_type == 'unassign_incident':
                result = _handle_unassign_incident(game_state, action_data)
            elif action_type == 'hire_specialist':
                result = _handle_hire_specialist(game_state, action_data)
            elif action_type == 'fire_specialist':
                result = _handle_fire_specialist(game_state, action_data)
            elif action_type == 'rest_specialist':
                result = _handle_rest_specialist(game_state, action_data)
            elif action_type == 'equip_item':
                result = _handle_equip_item(game_state, action_data)
            elif action_type == 'unequip_item':
                result = _handle_unequip_item(game_state, action_data)
            elif action_type == 'purchase_equipment':
                result = _handle_purchase_equipment(game_state, action_data)
            elif action_type == 'activate_ability':
                result = _handle_activate_ability(game_state, action_data)
            elif action_type == 'prestige':
                result = _handle_prestige(game_state, action_data)
            elif action_type == 'purchase_prestige_upgrade':
                result = _handle_purchase_prestige_upgrade(game_state, action_data)
            elif action_type == 'sign_contract':
                result = _handle_sign_contract(game_state, action_data)
            elif action_type == 'renew_contract':
                result = _handle_renew_contract(game_state, action_data)
            elif action_type == 'build_facility':
                result = _handle_build_facility(game_state, action_data)
            elif action_type == 'upgrade_facility':
                result = _handle_upgrade_facility(game_state, action_data)
            else:
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "INVALID_ACTION",
                        "message": f"Unknown action type: {action_type}"
                    }
                }), 400
            
            logger.logger.info(f"[ACTIONS_API] Processed action: {action_type}", 
                             action_type=action_type, success=result.get('success', False))
            
            return jsonify(result)
            
        except Exception as e:
            logger.logger.error(f"[ACTIONS_API] Action processing error: {e}", exception=e)
            return jsonify({
                "success": False,
                "error": {
                    "code": "SERVER_ERROR",
                    "message": f"Internal server error: {str(e)}"
                }
            }), 500
    
    # Action handlers
    
    def _handle_assign_incident(game_state, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle assign incident action."""
        incident_id = data.get('incident_id')
        specialist_id = data.get('specialist_id')
        
        if not incident_id or not specialist_id:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_ACTION",
                    "message": "incident_id and specialist_id are required"
                }
            }
        
        # Validate incident exists
        incident = game_state.get_incident_by_id(incident_id)
        if not incident:
            return {
                "success": False,
                "error": {
                    "code": "INCIDENT_NOT_FOUND",
                    "message": f"Incident {incident_id} not found"
                }
            }
        
        # Validate specialist exists
        specialist = game_state.get_specialist_by_id(specialist_id)
        if not specialist:
            return {
                "success": False,
                "error": {
                    "code": "SPECIALIST_NOT_FOUND",
                    "message": f"Specialist {specialist_id} not found"
                }
            }
        
        # Attempt assignment
        try:
            success = game_state.assign_incident_to_specialist(incident_id, specialist_id)
            
            if success:
                return {
                    "success": True,
                    "result": {
                        "assigned": True,
                        "incident_id": incident_id,
                        "specialist_id": specialist_id
                    }
                }
            else:
                # Assignment failed - determine why
                if not specialist.is_available():
                    return {
                        "success": False,
                        "error": {
                            "code": "SPECIALIST_BUSY",
                            "message": f"Specialist {specialist.name} is not available",
                            "details": {
                                "specialist_status": specialist.status,
                                "current_incident": specialist.assigned_incident_id
                            }
                        }
                    }
                elif specialist.specialty != incident.specialty_required:
                    return {
                        "success": False,
                        "error": {
                            "code": "SPECIALTY_MISMATCH",
                            "message": f"Specialist specialty doesn't match incident requirement",
                            "details": {
                                "specialist_specialty": specialist.specialty,
                                "required_specialty": incident.specialty_required
                            }
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": {
                            "code": "INVALID_STATE",
                            "message": "Assignment failed for unknown reason"
                        }
                    }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "SERVER_ERROR",
                    "message": str(e)
                }
            }
    
    def _handle_unassign_incident(game_state, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unassign incident action."""
        incident_id = data.get('incident_id')
        
        if not incident_id:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_ACTION",
                    "message": "incident_id is required"
                }
            }
        
        # Unassign logic not yet implemented in GameState
        return {
            "success": False,
            "error": {
                "code": "INVALID_ACTION",
                "message": "unassign_incident not yet implemented"
            }
        }
    
    def _handle_hire_specialist(game_state, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hire specialist action."""
        # TODO: Implement
        return {
            "success": False,
            "error": {
                "code": "INVALID_ACTION",
                "message": "hire_specialist not yet implemented"
            }
        }
    
    def _handle_fire_specialist(game_state, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle fire specialist action."""
        # TODO: Implement
        return {
            "success": False,
            "error": {
                "code": "INVALID_ACTION",
                "message": "fire_specialist not yet implemented"
            }
        }
    
    def _handle_rest_specialist(game_state, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle rest specialist action."""
        # TODO: Implement
        return {
            "success": False,
            "error": {
                "code": "INVALID_ACTION",
                "message": "rest_specialist not yet implemented"
            }
        }
    
    def _handle_equip_item(game_state, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle equip item action."""
        # TODO: Implement
        return {
            "success": False,
            "error": {
                "code": "INVALID_ACTION",
                "message": "equip_item not yet implemented"
            }
        }
    
    def _handle_unequip_item(game_state, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unequip item action."""
        # TODO: Implement
        return {
            "success": False,
            "error": {
                "code": "INVALID_ACTION",
                "message": "unequip_item not yet implemented"
            }
        }
    
    def _handle_purchase_equipment(game_state, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle purchase equipment action."""
        # TODO: Implement
        return {
            "success": False,
            "error": {
                "code": "INVALID_ACTION",
                "message": "purchase_equipment not yet implemented"
            }
        }
    
    def _handle_activate_ability(game_state, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle activate ability action."""
        # TODO: Implement
        return {
            "success": False,
            "error": {
                "code": "INVALID_ACTION",
                "message": "activate_ability not yet implemented"
            }
        }
    
    def _handle_prestige(game_state, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prestige action."""
        # TODO: Implement
        return {
            "success": False,
            "error": {
                "code": "INVALID_ACTION",
                "message": "prestige not yet implemented"
            }
        }
    
    def _handle_purchase_prestige_upgrade(game_state, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle purchase prestige upgrade action."""
        # TODO: Implement
        return {
            "success": False,
            "error": {
                "code": "INVALID_ACTION",
                "message": "purchase_prestige_upgrade not yet implemented"
            }
        }
    
    def _handle_sign_contract(game_state, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sign contract action."""
        # TODO: Implement
        return {
            "success": False,
            "error": {
                "code": "INVALID_ACTION",
                "message": "sign_contract not yet implemented"
            }
        }
    
    def _handle_renew_contract(game_state, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle renew contract action."""
        # TODO: Implement
        return {
            "success": False,
            "error": {
                "code": "INVALID_ACTION",
                "message": "renew_contract not yet implemented"
            }
        }
    
    def _handle_build_facility(game_state, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle build facility action."""
        # TODO: Implement
        return {
            "success": False,
            "error": {
                "code": "INVALID_ACTION",
                "message": "build_facility not yet implemented"
            }
        }
    
    def _handle_upgrade_facility(game_state, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle upgrade facility action."""
        # TODO: Implement
        return {
            "success": False,
            "error": {
                "code": "INVALID_ACTION",
                "message": "upgrade_facility not yet implemented"
            }
        }
    
    return bp
