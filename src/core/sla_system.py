"""SLA (Service Level Agreement) System - Core Functions.

This module provides the core logic for tracking SLA performance and
calculating impacts on client satisfaction. It acts as the integration
layer between incident resolution and client relationship management.

Key Functions:
- track_sla_incident(): Record SLA compliance for individual incidents
- calculate_sla_impact_on_satisfaction(): Compute satisfaction change
- update_client_satisfaction_from_sla(): Apply changes to client state

Follows 15-point gate standards: 100% type hints, Google docstrings,
explicit error handling, no magic numbers, DRY principle.
"""

import logging
from typing import Tuple, Optional, Dict, Any

from src.models.client import Client
from src.models.incident import Incident
from src.models.sla_tracker import SLATracker
from src.models.game_state import GameState

logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTS: SLA Configuration (from game_config, but duplicated here
#            as defaults for testing/offline use)
# ============================================================================

# Satisfaction impact multipliers per SLA tier (from game_config)
SLA_SATISFACTION_IMPACTS: Dict[str, float] = {
    "excellent": 0.02,    # +2% satisfaction bonus for excellent service
    "good": 0.01,         # +1% satisfaction bonus for good service
    "fair": 0.00,         # No change for fair (meets minimum)
    "poor": -0.03,        # -3% satisfaction penalty for poor service
}

# SLA tier boundaries (from game_config)
SLA_TIER_BOUNDARIES: Dict[str, float] = {
    "excellent": 0.90,    # >= 90%
    "good": 0.75,         # >= 75%
    "fair": 0.60,         # >= 60%
}

# Satisfaction bounds (prevent over/under-saturation)
MIN_SATISFACTION: float = 0.0
MAX_SATISFACTION: float = 1.0


# ============================================================================
# FUNCTION: track_sla_incident
# ============================================================================

def track_sla_incident(
    tracker: SLATracker,
    incident: Incident,
    resolution_time_seconds: float
) -> None:
    """Record SLA compliance for an individual incident resolution.
    
    Compares actual resolution time against the incident's SLA deadline.
    Updates tracker metrics to reflect whether overall SLA was met or missed.
    
    For our simplified model, we track resolution SLA as meeting the overall
    SLA deadline. Response time is implicit (immediate for gameplay purposes).
    
    This function MODIFIES the tracker in place. Call after incident
    is resolved but before month-end processing.
    
    Args:
        tracker: SLATracker instance for the client/month
        incident: Incident object with sla_seconds
        resolution_time_seconds: Actual time from incident creation to resolution
        
    Raises:
        ValueError: If resolution_time_seconds is negative
        TypeError: If tracker/incident parameters are wrong type
        
    Example:
        >>> tracker = SLATracker("tr_001", "client_001", month=1)
        >>> incident = Incident(id="inc_001", sla_seconds=3600, ...)
        >>> track_sla_incident(tracker, incident, 3400)  # Met SLA
        >>> tracker.resolution_sla_met
        1
    """
    # ===== PARAMETER VALIDATION =====
    if not isinstance(tracker, SLATracker):
        raise TypeError(f"tracker must be SLATracker, got {type(tracker)}")
    
    if not isinstance(incident, Incident):
        raise TypeError(f"incident must be Incident, got {type(incident)}")
    
    if resolution_time_seconds < 0:
        raise ValueError(f"resolution_time_seconds cannot be negative, got {resolution_time_seconds}")
    
    # ===== EVALUATE OVERALL SLA (resolution) =====
    sla_threshold: float = float(incident.sla_seconds)
    sla_met: bool = resolution_time_seconds <= sla_threshold
    
    # For response, we track as met (immediate assumption)
    tracker.response_sla_met += 1
    
    if sla_met:
        tracker.resolution_sla_met += 1
        logger.debug(
            f"SLA met: {resolution_time_seconds}s <= {sla_threshold}s "
            f"(incident={incident.id}, tracker={tracker.tracker_id})"
        )
    else:
        tracker.resolution_sla_missed += 1
        logger.debug(
            f"SLA missed: {resolution_time_seconds}s > {sla_threshold}s "
            f"(incident={incident.id}, tracker={tracker.tracker_id})"
        )
    
    # ===== INCREMENT TOTAL INCIDENT COUNT =====
    tracker.total_incidents += 1
    
    logger.info(
        f"Tracked incident SLA: met={sla_met}, "
        f"total_incidents={tracker.total_incidents}"
    )


# ============================================================================
# FUNCTION: calculate_sla_impact_on_satisfaction
# ============================================================================

def calculate_sla_impact_on_satisfaction(
    tracker: SLATracker,
    current_satisfaction: float
) -> float:
    """Calculate new satisfaction value after applying SLA impact.
    
    Gets the current month's SLA status from the tracker, determines
    the satisfaction impact based on tier (excellent/good/fair/poor),
    and applies that impact to the current satisfaction value.
    
    The result is clamped to [0.0, 1.0] to prevent over/under-saturation.
    
    This is a PURE FUNCTION - does not modify any inputs. Use the result
    to update Client.satisfaction in update_client_satisfaction_from_sla().
    
    Args:
        tracker: SLATracker with current month's compliance data
        current_satisfaction: Current satisfaction value (0.0-1.0)
        
    Returns:
        New satisfaction value after applying SLA impact (0.0-1.0 clamped)
        
    Raises:
        TypeError: If tracker/current_satisfaction wrong type
        ValueError: If current_satisfaction outside [0.0, 1.0] range
        
    Example:
        >>> tracker = SLATracker(...)  # 95% compliance (excellent)
        >>> tracker.get_satisfaction_impact()
        0.02
        >>> current_satisfaction = 0.75
        >>> new_satisfaction = calculate_sla_impact_on_satisfaction(tracker, 0.75)
        >>> new_satisfaction
        0.77  # 0.75 + 0.02 (excellent bonus)
    """
    # ===== PARAMETER VALIDATION =====
    if not isinstance(tracker, SLATracker):
        raise TypeError(f"tracker must be SLATracker, got {type(tracker)}")
    
    if not isinstance(current_satisfaction, (int, float)):
        raise TypeError(f"current_satisfaction must be float, got {type(current_satisfaction)}")
    
    if not (0.0 <= current_satisfaction <= 1.0):
        raise ValueError(f"current_satisfaction must be in [0.0, 1.0], got {current_satisfaction}")
    
    # ===== GET SLA STATUS AND IMPACT =====
    sla_status: str = tracker.get_sla_status()  # "excellent", "good", "fair", "poor"
    satisfaction_impact: float = tracker.get_satisfaction_impact()  # -0.03 to +0.02
    
    logger.debug(
        f"SLA impact calculation: status={sla_status}, impact={satisfaction_impact}, "
        f"current_satisfaction={current_satisfaction}"
    )
    
    # ===== APPLY IMPACT AND CLAMP TO BOUNDS =====
    new_satisfaction: float = current_satisfaction + satisfaction_impact
    
    # Clamp to valid range
    if new_satisfaction < MIN_SATISFACTION:
        clamped_satisfaction: float = MIN_SATISFACTION
        logger.warning(
            f"Satisfaction clamped to minimum: {new_satisfaction} -> {MIN_SATISFACTION} "
            f"(tracker={tracker.tracker_id})"
        )
    elif new_satisfaction > MAX_SATISFACTION:
        clamped_satisfaction = MAX_SATISFACTION
        logger.warning(
            f"Satisfaction clamped to maximum: {new_satisfaction} -> {MAX_SATISFACTION} "
            f"(tracker={tracker.tracker_id})"
        )
    else:
        clamped_satisfaction = new_satisfaction
    
    logger.debug(
        f"New satisfaction: {current_satisfaction} + {satisfaction_impact} = {clamped_satisfaction}"
    )
    
    return clamped_satisfaction


# ============================================================================
# FUNCTION: update_client_satisfaction_from_sla
# ============================================================================

def update_client_satisfaction_from_sla(
    game_state: GameState,
    client: Client,
    tracker: SLATracker
) -> Tuple[bool, Optional[str]]:
    """Apply SLA-based satisfaction update to a client.
    
    This is the MAIN INTEGRATION FUNCTION that combines:
    1. Get current SLA tracker for the client/month
    2. Calculate new satisfaction from tracker's SLA status
    3. Update the client's satisfaction field
    4. Log the change for debugging
    
    This function MODIFIES client.satisfaction in place and should be
    called once per month during month-end processing for each active client.
    
    Args:
        game_state: Current game state (for logging/audit trail)
        client: Client to update (satisfaction field will be modified)
        tracker: SLATracker with this month's compliance data
        
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
        - (True, None) on successful update
        - (False, "error_reason") if update failed
        
    Raises:
        (No exceptions raised - all errors returned as (False, error_msg))
        
    Example:
        >>> client = Client(satisfaction=0.75)
        >>> tracker = SLATracker(...)  # 95% compliance
        >>> success, error = update_client_satisfaction_from_sla(game_state, client, tracker)
        >>> success
        True
        >>> client.satisfaction
        0.77
    """
    # ===== PARAMETER VALIDATION =====
    if not isinstance(game_state, GameState):
        error_message: str = f"game_state must be GameState, got {type(game_state)}"
        logger.error(error_message)
        return False, error_message
    
    if not isinstance(client, Client):
        error_message = f"client must be Client, got {type(client)}"
        logger.error(error_message)
        return False, error_message
    
    if not isinstance(tracker, SLATracker):
        error_message = f"tracker must be SLATracker, got {type(tracker)}"
        logger.error(error_message)
        return False, error_message
    
    try:
        # ===== CALCULATE NEW SATISFACTION =====
        old_satisfaction: float = client.satisfaction
        new_satisfaction: float = calculate_sla_impact_on_satisfaction(tracker, old_satisfaction)
        
        # ===== APPLY UPDATE TO CLIENT =====
        client.satisfaction = new_satisfaction
        
        # ===== LOG THE CHANGE =====
        sla_status: str = tracker.get_sla_status()
        satisfaction_delta: float = new_satisfaction - old_satisfaction
        
        logger.info(
            f"Updated client satisfaction: {client.company_name} ({client.client_id}) "
            f"SLA={sla_status} satisfaction {old_satisfaction:.2f} → {new_satisfaction:.2f} "
            f"(delta={satisfaction_delta:+.2f})"
        )
        
        return True, None
        
    except Exception as e:
        error_message = f"Failed to update satisfaction: {str(e)}"
        logger.error(error_message, exc_info=True)
        return False, error_message


# ============================================================================
# FUNCTION: get_sla_satisfaction_tier_name
# ============================================================================

def get_sla_satisfaction_tier_name(sla_status: str) -> str:
    """Get human-readable name for SLA satisfaction tier.
    
    Maps SLA status codes to friendly names for UI/logging.
    
    Args:
        sla_status: SLA status code ("excellent", "good", "fair", "poor")
        
    Returns:
        Human-readable tier name (e.g., "Excellent Service")
        
    Example:
        >>> get_sla_satisfaction_tier_name("excellent")
        "Excellent Service"
        >>> get_sla_satisfaction_tier_name("poor")
        "Poor Service (Risk)"
    """
    tier_names: Dict[str, str] = {
        "excellent": "Excellent Service",
        "good": "Good Service",
        "fair": "Fair Service (At Risk)",
        "poor": "Poor Service (Critical)",
    }
    
    return tier_names.get(sla_status, "Unknown Status")


# ============================================================================
# FUNCTION: get_sla_satisfaction_impact_description
# ============================================================================

def get_sla_satisfaction_impact_description(impact: float) -> str:
    """Get human-readable description of satisfaction impact.
    
    Maps impact multiplier to friendly description for UI/logging.
    
    Args:
        impact: Satisfaction impact (-0.03 to +0.02)
        
    Returns:
        Human-readable description
        
    Example:
        >>> get_sla_satisfaction_impact_description(0.02)
        "+2% Satisfaction Bonus (Excellent)"
        >>> get_sla_satisfaction_impact_description(-0.03)
        "-3% Satisfaction Penalty (Critical)"
    """
    if abs(impact - 0.02) < 0.001:
        return "+2% Satisfaction Bonus (Excellent)"
    elif abs(impact - 0.01) < 0.001:
        return "+1% Satisfaction Bonus (Good)"
    elif abs(impact - 0.0) < 0.001:
        return "No Change (Fair - Meets Minimum)"
    elif abs(impact - (-0.03)) < 0.001:
        return "-3% Satisfaction Penalty (Poor)"
    else:
        return f"Impact: {impact:+.2%}"


if __name__ == "__main__":
    """Enable direct module execution for testing."""
    print("SLA System Core Functions")
    print("=" * 60)
    print("This module provides SLA tracking and satisfaction calculation.")
    print("Functions:")
    print("  - track_sla_incident()")
    print("  - calculate_sla_impact_on_satisfaction()")
    print("  - update_client_satisfaction_from_sla()")
    print("=" * 60)
