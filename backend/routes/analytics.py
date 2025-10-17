"""Analytics API routes.

Provides endpoints for game analytics and metrics.
"""
from flask import Blueprint, jsonify, request
from backend.services.analytics_service import analytics_service
from datetime import datetime


def create_analytics_blueprint(game_state_ref):
    """Create the analytics blueprint with game state reference.
    
    Args:
        game_state_ref: Reference to the GameState instance
    
    Returns:
        Flask Blueprint for analytics routes
    """
    bp = Blueprint('analytics', __name__)
    
    state_container = {'game_state': game_state_ref}
    
    def get_game_state():
        """Helper to get current game state."""
        return state_container.get('game_state')
    
    @bp.route('/analytics/summary', methods=['GET'])
    def get_analytics_summary():
        """Get comprehensive analytics summary."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            summary = analytics_service.get_performance_summary(game_state)
            return jsonify({
                "success": True,
                "data": summary,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to get analytics: {str(e)}"
            }), 500
    
    @bp.route('/analytics/revenue', methods=['GET'])
    def get_revenue_metrics():
        """Get revenue metrics."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            metrics = analytics_service.calculate_revenue_metrics(game_state)
            return jsonify({
                "success": True,
                "data": metrics
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to get revenue metrics: {str(e)}"
            }), 500
    
    @bp.route('/analytics/incidents', methods=['GET'])
    def get_incident_metrics():
        """Get incident metrics."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            metrics = analytics_service.calculate_incident_metrics(game_state)
            return jsonify({
                "success": True,
                "data": metrics
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to get incident metrics: {str(e)}"
            }), 500
    
    @bp.route('/analytics/specialists', methods=['GET'])
    def get_specialist_metrics():
        """Get specialist metrics."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            metrics = analytics_service.calculate_specialist_metrics(game_state)
            return jsonify({
                "success": True,
                "data": metrics
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to get specialist metrics: {str(e)}"
            }), 500
    
    @bp.route('/analytics/sla', methods=['GET'])
    def get_sla_metrics():
        """Get SLA compliance metrics."""
        game_state = get_game_state()
        if not game_state:
            return jsonify({
                "success": False,
                "message": "Game state not initialized"
            }), 503
        
        try:
            metrics = analytics_service.calculate_sla_metrics(game_state)
            return jsonify({
                "success": True,
                "data": metrics
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to get SLA metrics: {str(e)}"
            }), 500
    
    @bp.route('/analytics/history/<metric_name>', methods=['GET'])
    def get_metric_history(metric_name):
        """Get historical data for a metric.
        
        Query params:
            time_range: Time range (default: "24h")
        """
        time_range = request.args.get('time_range', '24h')
        
        try:
            history = analytics_service.get_metric_history(metric_name, time_range)
            return jsonify({
                "success": True,
                "data": {
                    "metric": metric_name,
                    "time_range": time_range,
                    "history": history
                }
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to get metric history: {str(e)}"
            }), 500
    
    return bp
