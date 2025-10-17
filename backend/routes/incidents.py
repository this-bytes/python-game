"""Incident Management API routes.

Provides endpoints for managing incidents (spawn, list, update, delete).
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import uuid


def create_incidents_blueprint(game_state_ref):
    """Create the incidents blueprint with game state reference.
    
    Args:
        game_state_ref: Reference to the GameState instance
    
    Returns:
        Flask Blueprint for incident routes
    """
    bp = Blueprint('incidents', __name__)
    
    state_container = {'game_state': game_state_ref}
    
    def get_game_state():
        return state_container.get('game_state')
    
    @bp.route('/incidents', methods=['GET'])
    def list_incidents():
        """List all incidents with optional filters."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            # Get query parameters for filtering
            status = request.args.get('status')  # 'pending', 'in_progress', 'resolved'
            specialty = request.args.get('specialty')
            difficulty_min = request.args.get('difficulty_min', type=int)
            difficulty_max = request.args.get('difficulty_max', type=int)
            
            incidents = game_state.incidents
            
            # Apply filters
            if status:
                incidents = [i for i in incidents if i.status == status]
            if specialty:
                incidents = [i for i in incidents if i.specialty == specialty]
            if difficulty_min is not None:
                incidents = [i for i in incidents if i.difficulty >= difficulty_min]
            if difficulty_max is not None:
                incidents = [i for i in incidents if i.difficulty <= difficulty_max]
            
            incidents_data = [i.to_dict() for i in incidents]
            
            return jsonify({
                "success": True,
                "data": incidents_data,
                "count": len(incidents_data),
                "filters": {
                    "status": status,
                    "specialty": specialty,
                    "difficulty_min": difficulty_min,
                    "difficulty_max": difficulty_max
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/incidents/<incident_id>', methods=['GET'])
    def get_incident(incident_id):
        """Get specific incident details."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            incident = next((i for i in game_state.incidents if i.id == incident_id), None)
            if not incident:
                return jsonify({"success": False, "message": "Incident not found"}), 404
            
            return jsonify({
                "success": True,
                "data": incident.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/incidents/spawn', methods=['POST'])
    def spawn_incident():
        """Manually spawn an incident."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            data = request.get_json() or {}
            
            # Get optional parameters
            client_id = data.get('client_id')
            
            # Find client
            if client_id:
                client = game_state.get_client_by_id(client_id)
                if not client:
                    return jsonify({"success": False, "message": "Client not found"}), 404
            else:
                # Pick random active client
                active_clients = [c for c in game_state.clients if c.active]
                if not active_clients:
                    return jsonify({"success": False, "message": "No active clients"}), 400
                import random
                client = random.choice(active_clients)
            
            # Generate incident using the generator
            if hasattr(game_state, 'incident_generator'):
                incident = game_state.incident_generator.generate_incident(client)
                
                if incident:
                    game_state.incidents.append(incident)
                    
                    return jsonify({
                        "success": True,
                        "message": "Incident spawned successfully",
                        "data": incident.to_dict(),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                else:
                    return jsonify({
                        "success": False,
                        "message": "Failed to generate incident"
                    }), 500
            else:
                return jsonify({
                    "success": False,
                    "message": "Incident generator not available"
                }), 501
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/incidents/batch-spawn', methods=['POST'])
    def batch_spawn_incidents():
        """Spawn multiple incidents for stress testing."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            data = request.get_json() or {}
            count = data.get('count', 10)
            count = min(count, 100)  # Cap at 100 for safety
            
            spawned = []
            active_clients = [c for c in game_state.clients if c.active]
            
            if not active_clients:
                return jsonify({"success": False, "message": "No active clients"}), 400
            
            if hasattr(game_state, 'incident_generator'):
                import random
                for _ in range(count):
                    client = random.choice(active_clients)
                    incident = game_state.incident_generator.generate_incident(client)
                    if incident:
                        game_state.incidents.append(incident)
                        spawned.append(incident.id)
                
                return jsonify({
                    "success": True,
                    "message": f"Spawned {len(spawned)} incidents",
                    "data": {"incident_ids": spawned},
                    "count": len(spawned),
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Incident generator not available"
                }), 501
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/incidents/<incident_id>', methods=['PUT'])
    def update_incident(incident_id):
        """Update incident details."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            incident = next((i for i in game_state.incidents if i.id == incident_id), None)
            if not incident:
                return jsonify({"success": False, "message": "Incident not found"}), 404
            
            data = request.get_json()
            
            # Update allowed fields
            if 'status' in data:
                incident.status = data['status']
            if 'sla_remaining' in data:
                incident.sla_remaining = float(data['sla_remaining'])
            if 'assigned_specialist_id' in data:
                incident.assigned_specialist_id = data['assigned_specialist_id']
            
            return jsonify({
                "success": True,
                "message": "Incident updated successfully",
                "data": incident.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/incidents/<incident_id>', methods=['DELETE'])
    def delete_incident(incident_id):
        """Remove/cancel an incident."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            incident = next((i for i in game_state.incidents if i.id == incident_id), None)
            if not incident:
                return jsonify({"success": False, "message": "Incident not found"}), 404
            
            game_state.incidents.remove(incident)
            
            return jsonify({
                "success": True,
                "message": "Incident removed successfully",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/incidents/<incident_id>/complete', methods=['POST'])
    def complete_incident(incident_id):
        """Complete incident with burnout tracking."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            data = request.json or {}
            success = data.get('success', False)
            
            incident = next((i for i in game_state.incidents if i.id == incident_id), None)
            if not incident:
                return jsonify({"success": False, "message": "Incident not found"}), 404
            
            specialist = next((s for s in game_state.specialists if s.id == incident.assigned_specialist_id), None)
            if not specialist:
                return jsonify({"success": False, "message": "Specialist not found"}), 404
            
            from src.core.resolution_system import ResolutionSystem
            resolution_system = ResolutionSystem(game_state._burnout_system)
            
            result = resolution_system.complete_incident(
                specialist, incident, success=success
            )
            
            return jsonify({
                "success": True,
                "message": "Incident completed",
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    return bp
