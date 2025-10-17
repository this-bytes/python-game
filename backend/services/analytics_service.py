"""Analytics service for game metrics and statistics.

Provides calculations and aggregations for game analytics.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class AnalyticsService:
    """Service for calculating game analytics and metrics."""
    
    def __init__(self):
        """Initialize analytics service."""
        self.metrics_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.max_history_per_metric = 1000
    
    def record_metric(self, metric_name: str, value: Any, metadata: Optional[Dict[str, Any]] = None):
        """Record a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            metadata: Optional metadata about the metric
        """
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'value': value,
            'metadata': metadata or {}
        }
        
        self.metrics_history[metric_name].append(entry)
        
        # Trim history if needed
        if len(self.metrics_history[metric_name]) > self.max_history_per_metric:
            self.metrics_history[metric_name].pop(0)
    
    def calculate_revenue_metrics(self, game_state) -> Dict[str, Any]:
        """Calculate revenue-related metrics.
        
        Args:
            game_state: GameState instance
            
        Returns:
            Dictionary of revenue metrics
        """
        if not game_state:
            return {}
        
        return {
            'current_money': game_state.money,
            'total_earned': getattr(game_state, 'total_money_earned', 0),
            'total_spent': getattr(game_state, 'total_money_spent', 0),
            'net_profit': getattr(game_state, 'total_money_earned', 0) - getattr(game_state, 'total_money_spent', 0)
        }
    
    def calculate_incident_metrics(self, game_state) -> Dict[str, Any]:
        """Calculate incident-related metrics.
        
        Args:
            game_state: GameState instance
            
        Returns:
            Dictionary of incident metrics
        """
        if not game_state or not hasattr(game_state, 'incidents'):
            return {}
        
        active_incidents = [i for i in game_state.incidents if i.status == 'active']
        completed = [i for i in game_state.incidents if i.status == 'completed']
        failed = [i for i in game_state.incidents if i.status == 'failed']
        
        return {
            'total_incidents': len(game_state.incidents),
            'active': len(active_incidents),
            'completed': len(completed),
            'failed': len(failed),
            'success_rate': len(completed) / len(game_state.incidents) * 100 if game_state.incidents else 0
        }
    
    def calculate_specialist_metrics(self, game_state) -> Dict[str, Any]:
        """Calculate specialist-related metrics.
        
        Args:
            game_state: GameState instance
            
        Returns:
            Dictionary of specialist metrics
        """
        if not game_state or not hasattr(game_state, 'specialists'):
            return {}
        
        available = [s for s in game_state.specialists if s.status == 'available']
        busy = [s for s in game_state.specialists if s.status == 'busy']
        
        avg_level = sum(s.level for s in game_state.specialists) / len(game_state.specialists) if game_state.specialists else 0
        
        return {
            'total_specialists': len(game_state.specialists),
            'available': len(available),
            'busy': len(busy),
            'average_level': round(avg_level, 2)
        }
    
    def calculate_sla_metrics(self, game_state) -> Dict[str, Any]:
        """Calculate SLA compliance metrics.
        
        Args:
            game_state: GameState instance
            
        Returns:
            Dictionary of SLA metrics
        """
        if not game_state or not hasattr(game_state, 'incidents'):
            return {}
        
        completed_incidents = [i for i in game_state.incidents if i.status == 'completed']
        if not completed_incidents:
            return {'sla_compliance': 100.0, 'violations': 0}
        
        violations = sum(1 for i in completed_incidents if getattr(i, 'sla_violated', False))
        compliance = (len(completed_incidents) - violations) / len(completed_incidents) * 100
        
        return {
            'sla_compliance': round(compliance, 2),
            'violations': violations,
            'total_completed': len(completed_incidents)
        }
    
    def get_performance_summary(self, game_state) -> Dict[str, Any]:
        """Get comprehensive performance summary.
        
        Args:
            game_state: GameState instance
            
        Returns:
            Dictionary containing all key metrics
        """
        return {
            'revenue': self.calculate_revenue_metrics(game_state),
            'incidents': self.calculate_incident_metrics(game_state),
            'specialists': self.calculate_specialist_metrics(game_state),
            'sla': self.calculate_sla_metrics(game_state),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_metric_history(self, metric_name: str, time_range: str = "24h") -> List[Dict[str, Any]]:
        """Get historical data for a metric.
        
        Args:
            metric_name: Name of the metric
            time_range: Time range (e.g., "1h", "24h", "7d")
            
        Returns:
            List of metric entries within time range
        """
        if metric_name not in self.metrics_history:
            return []
        
        # Parse time range
        amount = int(time_range[:-1])
        unit = time_range[-1]
        
        if unit == 'h':
            cutoff = datetime.utcnow() - timedelta(hours=amount)
        elif unit == 'd':
            cutoff = datetime.utcnow() - timedelta(days=amount)
        elif unit == 'm':
            cutoff = datetime.utcnow() - timedelta(minutes=amount)
        else:
            return self.metrics_history[metric_name]
        
        # Filter by time range
        return [
            entry for entry in self.metrics_history[metric_name]
            if datetime.fromisoformat(entry['timestamp']) >= cutoff
        ]


# Global analytics service instance
analytics_service = AnalyticsService()
