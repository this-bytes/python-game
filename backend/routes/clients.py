"""Client & Economy API routes.

Provides endpoints for client management and economy adjustments.
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from src.core.client_manager import ClientManager


def create_clients_blueprint(game_state_ref):
    """Create the clients blueprint."""
    bp = Blueprint('clients', __name__)
    state_container = {'game_state': game_state_ref}
    client_manager = ClientManager()
    
    def get_game_state():
        return state_container.get('game_state')
    
    @bp.route('/clients', methods=['GET'])
    def list_clients():
        """List all clients with reputation and tier information."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            clients_data = []
            for client in game_state.clients:
                client_dict = client.to_dict()
                # Add computed fields
                client_dict['tier_name'] = client_manager.get_reputation_tier_name(client.tier)
                client_dict['satisfaction'] = client_manager.calculate_satisfaction(client)
                client_dict['will_renew'] = client_manager.check_contract_renewal(client, game_state)
                clients_data.append(client_dict)
            
            return jsonify({
                "success": True,
                "data": clients_data,
                "count": len(clients_data),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/clients/<client_id>', methods=['GET'])
    def get_client(client_id):
        """Get specific client details with full summary."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            client = game_state.get_client_by_id(client_id)
            if not client:
                return jsonify({"success": False, "message": "Client not found"}), 404
            
            # Get comprehensive summary
            summary = client_manager.get_client_summary(client)
            
            return jsonify({
                "success": True,
                "data": summary,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/clients/<client_id>', methods=['PUT'])
    def update_client(client_id):
        """Update client parameters."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            client = game_state.get_client_by_id(client_id)
            if not client:
                return jsonify({"success": False, "message": "Client not found"}), 404
            
            data = request.get_json()
            
            # Update fields
            if 'incident_rate_per_minute' in data:
                client.incident_rate_per_minute = float(data['incident_rate_per_minute'])
            if 'sla_multiplier' in data:
                client.sla_multiplier = float(data['sla_multiplier'])
            if 'reputation' in data:
                client.reputation = int(data['reputation'])
                client.tier = client_manager.determine_tier(client)
            if 'contract_value' in data:
                client.contract_value = float(data['contract_value'])
            if 'active' in data:
                client.active = bool(data['active'])
            
            return jsonify({
                "success": True,
                "message": "Client updated successfully",
                "data": client.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/clients/<client_id>/reputation', methods=['PUT'])
    def adjust_reputation(client_id):
        """Manually adjust client reputation (admin function)."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            client = game_state.get_client_by_id(client_id)
            if not client:
                return jsonify({"success": False, "message": "Client not found"}), 404
            
            data = request.get_json()
            adjustment = data.get('adjustment', 0)
            
            old_reputation = client.reputation
            old_tier = client.tier
            
            client.reputation = max(0, min(100, client.reputation + adjustment))
            client.tier = client_manager.determine_tier(client)
            
            return jsonify({
                "success": True,
                "message": f"Reputation adjusted by {adjustment:+d}",
                "data": {
                    "old_reputation": old_reputation,
                    "new_reputation": client.reputation,
                    "old_tier": old_tier,
                    "new_tier": client.tier,
                    "tier_name": client_manager.get_reputation_tier_name(client.tier)
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/clients/<client_id>/simulate-incidents', methods=['POST'])
    def simulate_incidents(client_id):
        """Force incident generation for a specific client (testing)."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            client = game_state.get_client_by_id(client_id)
            if not client:
                return jsonify({"success": False, "message": "Client not found"}), 404
            
            data = request.get_json()
            count = data.get('count', 1)
            
            generated_incidents = []
            for _ in range(count):
                incident = game_state.incident_generator.generate_incident(client)
                if incident:
                    game_state.incidents.append(incident)
                    generated_incidents.append(incident.to_dict())
            
            return jsonify({
                "success": True,
                "message": f"Generated {len(generated_incidents)} incidents for {client.name}",
                "data": {
                    "client_id": client_id,
                    "incidents_generated": len(generated_incidents),
                    "incidents": generated_incidents
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    return bp


def create_economy_blueprint(game_state_ref):
    """Create the economy blueprint."""
    bp = Blueprint('economy', __name__)
    state_container = {'game_state': game_state_ref}
    
    def get_game_state():
        return state_container.get('game_state')
    
    @bp.route('/economy/money', methods=['POST'])
    def adjust_money():
        """Add or subtract money."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            data = request.get_json()
            amount = data.get('amount', 0)
            reason = data.get('reason', 'Manual adjustment')
            
            old_money = game_state.current_money
            game_state.current_money += amount
            
            return jsonify({
                "success": True,
                "message": f"Money adjusted: {amount:+.2f} ({reason})",
                "data": {
                    "old_money": old_money,
                    "adjustment": amount,
                    "new_money": game_state.current_money,
                    "reason": reason
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/economy/metrics', methods=['GET'])
    def get_metrics():
        """Get financial and performance metrics."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            metrics_data = game_state.metrics.to_dict()
            metrics_data['current_money'] = game_state.current_money
            
            return jsonify({
                "success": True,
                "data": metrics_data,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    return bp
