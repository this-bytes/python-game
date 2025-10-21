"""SLA Tracker model for monitoring client service level agreements.

Tracks monthly SLA compliance metrics for each client, including
response time and resolution time compliance rates.
"""

from dataclasses import dataclass


@dataclass
class SLATracker:
    """Tracks SLA compliance for a client in a given month."""
    
    tracker_id: str
    client_id: str
    month: int
    
    total_incidents: int = 0
    response_sla_met: int = 0
    response_sla_missed: int = 0
    resolution_sla_met: int = 0
    resolution_sla_missed: int = 0
    
    def get_response_compliance(self) -> float:
        """Get response SLA compliance rate (0.0-1.0).
        
        Returns:
            Compliance rate between 0.0 (all missed) and 1.0 (all met)
        """
        total = self.response_sla_met + self.response_sla_missed
        if total == 0:
            return 1.0
        return self.response_sla_met / total
    
    def get_resolution_compliance(self) -> float:
        """Get resolution SLA compliance rate (0.0-1.0).
        
        Returns:
            Compliance rate between 0.0 (all missed) and 1.0 (all met)
        """
        total = self.resolution_sla_met + self.resolution_sla_missed
        if total == 0:
            return 1.0
        return self.resolution_sla_met / total
    
    def get_overall_compliance(self) -> float:
        """Get combined SLA compliance (average of response + resolution).
        
        Returns:
            Overall compliance rate between 0.0 and 1.0
        """
        response_comp = self.get_response_compliance()
        resolution_comp = self.get_resolution_compliance()
        return (response_comp + resolution_comp) / 2.0
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "tracker_id": self.tracker_id,
            "client_id": self.client_id,
            "month": self.month,
            "total_incidents": self.total_incidents,
            "response_sla_met": self.response_sla_met,
            "response_sla_missed": self.response_sla_missed,
            "resolution_sla_met": self.resolution_sla_met,
            "resolution_sla_missed": self.resolution_sla_missed,
        }
    
    @staticmethod
    def from_dict(data: dict) -> "SLATracker":
        """Create SLATracker from JSON dict."""
        return SLATracker(
            tracker_id=data["tracker_id"],
            client_id=data["client_id"],
            month=data["month"],
            total_incidents=data.get("total_incidents", 0),
            response_sla_met=data.get("response_sla_met", 0),
            response_sla_missed=data.get("response_sla_missed", 0),
            resolution_sla_met=data.get("resolution_sla_met", 0),
            resolution_sla_missed=data.get("resolution_sla_missed", 0),
        )
