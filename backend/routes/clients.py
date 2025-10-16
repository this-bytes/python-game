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


def create_contracts_blueprint(game_state_ref):
    """Create the contracts blueprint."""
    bp = Blueprint('contracts', __name__)
    state_container = {'game_state': game_state_ref}
    
    # Import here to avoid circular dependencies
    from src.core.contract_manager import ContractManager
    from src.utils.json_loader import JSONLoader
    
    contract_manager = ContractManager()
    
    # Load contract templates
    try:
        json_loader = JSONLoader()
        contracts_data = json_loader.load_data("contracts.json")
        if "contract_templates" in contracts_data:
            contract_manager.load_templates(contracts_data["contract_templates"])
    except Exception as e:
        print(f"Warning: Could not load contract templates: {e}")
    
    def get_game_state():
        return state_container.get('game_state')
    
    @bp.route('/contracts', methods=['GET'])
    def list_contracts():
        """List all contracts."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            contracts = getattr(game_state, 'contracts', [])
            contracts_data = [contract_manager.get_contract_summary(c) for c in contracts]
            
            return jsonify({
                "success": True,
                "data": contracts_data,
                "count": len(contracts_data),
                "active_count": contract_manager.get_active_contracts_count(contracts),
                "total_retainer_value": contract_manager.get_total_retainer_value(contracts),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/contracts/<contract_id>', methods=['GET'])
    def get_contract(contract_id):
        """Get specific contract details."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            contracts = getattr(game_state, 'contracts', [])
            contract = next((c for c in contracts if c.id == contract_id), None)
            
            if not contract:
                return jsonify({"success": False, "message": "Contract not found"}), 404
            
            summary = contract_manager.get_contract_summary(contract)
            
            return jsonify({
                "success": True,
                "data": summary,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/contracts/negotiate', methods=['POST'])
    def negotiate_contract():
        """Negotiate a new contract with a client."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            data = request.get_json()
            client_id = data.get('client_id')
            template_id = data.get('template_id')
            terms = data.get('terms', {})
            
            client = game_state.get_client_by_id(client_id)
            if not client:
                return jsonify({"success": False, "message": "Client not found"}), 404
            
            contract = contract_manager.negotiate_contract(client, template_id, terms, game_state)
            
            if not contract:
                return jsonify({
                    "success": False,
                    "message": "Contract negotiation failed. Client reputation may be too low."
                }), 400
            
            # Add contract to game state
            if not hasattr(game_state, 'contracts'):
                game_state.contracts = []
            game_state.contracts.append(contract)
            
            return jsonify({
                "success": True,
                "message": "Contract negotiated successfully",
                "data": contract_manager.get_contract_summary(contract),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/contracts/<contract_id>/renew', methods=['PUT'])
    def renew_contract(contract_id):
        """Renew an existing contract."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            contracts = getattr(game_state, 'contracts', [])
            contract = next((c for c in contracts if c.id == contract_id), None)
            
            if not contract:
                return jsonify({"success": False, "message": "Contract not found"}), 404
            
            old_rate = contract.base_rate
            old_duration = contract.duration_days
            
            renewed = contract_manager.renew_contract(contract, game_state)
            
            return jsonify({
                "success": True,
                "message": "Contract renewed successfully",
                "data": {
                    "old_rate": old_rate,
                    "new_rate": renewed.base_rate,
                    "old_duration": old_duration,
                    "new_duration": renewed.duration_days,
                    "contract": contract_manager.get_contract_summary(renewed)
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/contracts/<contract_id>', methods=['DELETE'])
    def terminate_contract(contract_id):
        """Terminate a contract."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            contracts = getattr(game_state, 'contracts', [])
            contract = next((c for c in contracts if c.id == contract_id), None)
            
            if not contract:
                return jsonify({"success": False, "message": "Contract not found"}), 404
            
            data = request.get_json() or {}
            reason = data.get('reason', 'firm_termination')
            
            penalty = contract_manager.terminate_contract(contract, reason, game_state)
            
            # Apply penalty to game state
            if penalty > 0:
                game_state.current_money = max(0, game_state.current_money - penalty)
            
            return jsonify({
                "success": True,
                "message": "Contract terminated",
                "data": {
                    "contract_id": contract_id,
                    "reason": reason,
                    "penalty": penalty,
                    "remaining_money": game_state.current_money
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/contracts/templates', methods=['GET'])
    def list_templates():
        """List available contract templates."""
        try:
            templates = list(contract_manager.contract_templates.values())
            return jsonify({
                "success": True,
                "data": templates,
                "count": len(templates),
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


def create_facilities_blueprint(game_state_ref):
    """Create the facilities blueprint."""
    bp = Blueprint('facilities', __name__)
    state_container = {'game_state': game_state_ref}
    
    # Import here to avoid circular dependencies
    from src.core.facility_system import FacilitySystem
    
    facility_system = FacilitySystem()
    
    def get_game_state():
        return state_container.get('game_state')
    
    @bp.route('/facilities', methods=['GET'])
    def list_facilities():
        """List all facilities with current status."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            facilities = getattr(game_state, 'facilities', [])
            summary = facility_system.get_all_facilities_summary(facilities)
            
            return jsonify({
                "success": True,
                "data": summary,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/facilities/<facility_id>', methods=['GET'])
    def get_facility(facility_id):
        """Get specific facility details."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            facilities = getattr(game_state, 'facilities', [])
            facility = facility_system.get_facility_by_id(facilities, facility_id)
            
            if not facility:
                return jsonify({"success": False, "message": "Facility not found"}), 404
            
            summary = facility_system.get_facility_summary(facility)
            
            return jsonify({
                "success": True,
                "data": summary,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/facilities/<facility_id>/upgrade', methods=['POST'])
    def upgrade_facility(facility_id):
        """Upgrade a facility."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            facilities = getattr(game_state, 'facilities', [])
            facility = facility_system.get_facility_by_id(facilities, facility_id)
            
            if not facility:
                return jsonify({"success": False, "message": "Facility not found"}), 404
            
            if not facility.can_upgrade():
                return jsonify({
                    "success": False,
                    "message": "Facility is already at max level"
                }), 400
            
            upgrade_cost = facility.calculate_upgrade_cost()
            
            if game_state.current_money < upgrade_cost:
                return jsonify({
                    "success": False,
                    "message": f"Insufficient funds. Need ${upgrade_cost}, have ${game_state.current_money}"
                }), 400
            
            old_level = facility.level
            old_money = game_state.current_money
            
            success = facility_system.upgrade_facility(facility, game_state)
            
            if not success:
                return jsonify({
                    "success": False,
                    "message": "Upgrade failed"
                }), 500
            
            return jsonify({
                "success": True,
                "message": f"{facility.name} upgraded to level {facility.level}",
                "data": {
                    "old_level": old_level,
                    "new_level": facility.level,
                    "cost": upgrade_cost,
                    "old_money": old_money,
                    "new_money": game_state.current_money,
                    "facility": facility_system.get_facility_summary(facility)
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/facilities/<facility_id>/set-level', methods=['PUT'])
    def set_facility_level(facility_id):
        """Set facility level directly (admin function)."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            facilities = getattr(game_state, 'facilities', [])
            facility = facility_system.get_facility_by_id(facilities, facility_id)
            
            if not facility:
                return jsonify({"success": False, "message": "Facility not found"}), 404
            
            data = request.get_json()
            new_level = data.get('level', 1)
            
            if new_level < 1 or new_level > facility.max_level:
                return jsonify({
                    "success": False,
                    "message": f"Level must be between 1 and {facility.max_level}"
                }), 400
            
            old_level = facility.level
            facility.level = new_level
            
            return jsonify({
                "success": True,
                "message": f"{facility.name} level set to {new_level}",
                "data": {
                    "old_level": old_level,
                    "new_level": new_level,
                    "facility": facility_system.get_facility_summary(facility)
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    @bp.route('/facilities/effects', methods=['GET'])
    def get_facility_effects():
        """Get aggregate facility effects on game state."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({"success": False, "message": "Game state not initialized"}), 503
        
        try:
            effects = facility_system.apply_facility_effects(game_state)
            
            return jsonify({
                "success": True,
                "data": effects,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    
    return bp
