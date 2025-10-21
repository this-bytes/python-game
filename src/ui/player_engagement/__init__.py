"""Player engagement package exports.

Provides EngagementManager which orchestrates urgency, feedback, progression
and flow systems. Modules are lightweight skeletons suitable for incremental
implementation and unit testing.
"""
from .engagement_manager import EngagementManager

__all__ = ["EngagementManager"]
"""Player engagement package: visual urgency, feedback, progression and flow management.

This package contains lightweight, well-typed skeletons that integrate with the
existing `GameUI` rendering pipeline. They are intentionally small so the
team can iterate on visuals and behavior quickly.
"""

from .engagement_manager import EngagementManager

__all__ = ["EngagementManager"]
