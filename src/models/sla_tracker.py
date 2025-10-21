"""SLA Tracker model for monitoring client service level agreements.

Tracks monthly SLA compliance metrics for each client, including
response time and resolution time compliance rates. Provides compliance
calculations and status categorization for integration with client
satisfaction mechanics.
"""

from dataclasses import dataclass
from typing import Dict, Literal


@dataclass
class SLATracker:
    """Tracks SLA compliance for a client in a given month.
    
    Purpose: Monitor whether the SOC (Security Operations Center) is meeting
    promised response and resolution times for this client. SLA compliance
    directly impacts client satisfaction and therefore revenue.
    
    SLA Tiers (for satisfaction impact):
    - Excellent (90-100%): Client satisfaction +2%
    - Good (75-89%): Client satisfaction +1%
    - Fair (60-74%): Client satisfaction unchanged
    - Poor (<60%): Client satisfaction -3% (critical degradation)
    """
    
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
    
    def get_compliance_rate(self) -> float:
        """Get overall SLA compliance rate as percentage (0.0-1.0).
        
        Alias for get_overall_compliance() for consistency with game API.
        
        Returns:
            Overall compliance rate between 0.0 (0%) and 1.0 (100%)
            
        Example:
            - 0.95 = 95% compliance (excellent)
            - 0.70 = 70% compliance (fair)
            - 0.30 = 30% compliance (poor - critical issue)
        """
        return self.get_overall_compliance()
    
    def get_sla_status(self) -> Literal["excellent", "good", "fair", "poor"]:
        """Categorize SLA compliance into tiers for satisfaction impact.
        
        Returns:
            Status tier: "excellent", "good", "fair", or "poor"
            
        Tier Definitions:
        - excellent: >= 90% (0.90)
        - good: 75-89% (0.75-0.89)
        - fair: 60-74% (0.60-0.74)
        - poor: < 60% (< 0.60)
        """
        compliance_rate: float = self.get_compliance_rate()
        
        if compliance_rate >= 0.90:
            return "excellent"
        elif compliance_rate >= 0.75:
            return "good"
        elif compliance_rate >= 0.60:
            return "fair"
        else:
            return "poor"
    
    def get_satisfaction_impact(self) -> float:
        """Calculate impact on client satisfaction from SLA compliance.
        
        Returns:
            Satisfaction multiplier: -0.03 (poor) to +0.02 (excellent)
            
        Impact Tiers:
        - excellent (90-100%): +0.02 bonus (satisfied customer)
        - good (75-89%): +0.01 bonus (acceptable performance)
        - fair (60-74%): 0.00 (meets minimum, no bonus)
        - poor (<60%): -0.03 penalty (critical failure)
        """
        status: Literal["excellent", "good", "fair", "poor"] = self.get_sla_status()
        
        if status == "excellent":
            return 0.02
        elif status == "good":
            return 0.01
        elif status == "fair":
            return 0.00
        else:  # poor
            return -0.03
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict for persistence.
        
        Returns:
            Dictionary with all SLA tracking data
        """
        return {
            "tracker_id": self.tracker_id,
            "client_id": self.client_id,
            "month": self.month,
            "total_incidents": self.total_incidents,
            "response_sla_met": self.response_sla_met,
            "response_sla_missed": self.response_sla_missed,
            "resolution_sla_met": self.resolution_sla_met,
            "resolution_sla_missed": self.resolution_sla_missed,
            "compliance_rate": self.get_compliance_rate(),
            "sla_status": self.get_sla_status(),
            "satisfaction_impact": self.get_satisfaction_impact(),
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "SLATracker":
        """Create SLATracker from JSON dict.
        
        Args:
            data: Dictionary with tracker data (from to_dict or JSON load)
            
        Returns:
            Reconstructed SLATracker instance with all data restored
        """
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
