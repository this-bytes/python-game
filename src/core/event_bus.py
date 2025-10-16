"""Event Bus System - Decoupled communication between game systems.

This enables features to communicate without tight coupling, allowing
plug-and-play architecture where systems can be added/removed without
modifying existing code.

Usage:
    event_bus = EventBus()
    event_bus.subscribe("incident_resolved", my_callback)
    event_bus.emit("incident_resolved", {"incident_id": "123"})
"""

from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum  # Keep for EventPriority only
import logging
from collections import defaultdict
import time


class EventPriority(Enum):
    """Event handler priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


# Standard game event types - use strings directly, no constants needed
# 
# Usage: 
#   event_bus.emit("incident_resolved", {"incident_id": "123"})
#   event_bus.subscribe("specialist_leveled_up", my_callback)
#
# Common Event Types (for reference):
#   Incidents: "incident_generated", "incident_assigned", "incident_resolved", 
#              "incident_failed", "incident_sla_warning"
#   Specialists: "specialist_assigned", "specialist_available", "specialist_leveled_up",
#                "specialist_xp_gained", "specialist_hired", "specialist_retired"
#   Contracts: "contract_signed", "contract_completed", "contract_lost"
#   Clients: "client_reputation_changed"
#   Money: "money_earned", "money_spent", "money_milestone"
#   Progression: "achievement_unlocked", "prestige_triggered", "level_milestone"
#   Relationships: "relationship_changed", "rivalry_triggered", "romance_started"
#   Office: "furniture_placed", "room_upgraded"
#   System: "game_paused", "game_resumed", "game_saved", "game_loaded"
#   Synergy: "synergy_bonus_applied", "auto_assignment_triggered"
#   Dopamine: "combo_triggered", "perfect_completion", "risk_contract_accepted"


@dataclass
class EventSubscription:
    """Represents a subscription to an event."""
    event_type: str
    callback: Callable
    priority: EventPriority
    subscriber_id: str
    created_at: float = field(default_factory=time.time)


class EventBus:
    """Central event bus for game-wide communication.
    
    Features:
    - Priority-based event handling
    - Async event queuing
    - Event history/replay
    - Subscription management
    - Performance metrics
    """
    
    def __init__(self, enable_history: bool = False, max_history: int = 1000):
        """Initialize event bus.
        
        Args:
            enable_history: Whether to store event history
            max_history: Maximum events to store in history
        """
        self._subscriptions: Dict[str, List[EventSubscription]] = defaultdict(list)
        self._event_queue: List[tuple] = []
        self._enable_history = enable_history
        self._max_history = max_history
        self._event_history: List[Dict] = []
        self._stats = {
            "events_emitted": 0,
            "events_handled": 0,
            "errors": 0
        }
        self.logger = logging.getLogger("event_bus")
    
    def subscribe(
        self,
        event_type: str,
        callback: Callable,
        priority: EventPriority = EventPriority.NORMAL,
        subscriber_id: Optional[str] = None
    ) -> str:
        """Subscribe to an event.
        
        Args:
            event_type: Event type to subscribe to
            callback: Function to call when event fires
            priority: Handler priority (higher = called first)
            subscriber_id: Optional ID for the subscriber
            
        Returns:
            Subscription ID for unsubscribing
        """
        if subscriber_id is None:
            subscriber_id = f"sub_{id(callback)}_{time.time()}"
        
        subscription = EventSubscription(
            event_type=event_type,
            callback=callback,
            priority=priority,
            subscriber_id=subscriber_id
        )
        
        self._subscriptions[event_type].append(subscription)
        
        # Sort by priority (highest first)
        self._subscriptions[event_type].sort(
            key=lambda s: s.priority.value,
            reverse=True
        )
        
        self.logger.debug(
            f"Subscription added: {subscriber_id} -> {event_type} "
            f"(priority: {priority.name})"
        )
        
        return subscriber_id
    
    def unsubscribe(self, event_type: str, subscriber_id: str) -> bool:
        """Unsubscribe from an event.
        
        Args:
            event_type: Event type to unsubscribe from
            subscriber_id: Subscriber ID from subscribe()
            
        Returns:
            True if unsubscribed, False if not found
        """
        if event_type not in self._subscriptions:
            return False
        
        original_count = len(self._subscriptions[event_type])
        self._subscriptions[event_type] = [
            sub for sub in self._subscriptions[event_type]
            if sub.subscriber_id != subscriber_id
        ]
        
        removed = len(self._subscriptions[event_type]) < original_count
        
        if removed:
            self.logger.debug(f"Unsubscribed: {subscriber_id} from {event_type}")
        
        return removed
    
    def unsubscribe_all(self, subscriber_id: str) -> int:
        """Unsubscribe from all events.
        
        Args:
            subscriber_id: Subscriber ID to remove
            
        Returns:
            Number of subscriptions removed
        """
        count = 0
        for event_type in list(self._subscriptions.keys()):
            if self.unsubscribe(event_type, subscriber_id):
                count += 1
        return count
    
    def emit(self, event_type: str, data: Optional[Dict[str, Any]] = None, immediate: bool = True):
        """Emit an event.
        
        Args:
            event_type: Type of event to emit
            data: Event data payload
            immediate: If True, handle immediately. If False, queue for later.
        """
        if data is None:
            data = {}
        
        self._stats["events_emitted"] += 1
        
        # Store in history
        if self._enable_history:
            self._add_to_history(event_type, data)
        
        if immediate:
            self._handle_event(event_type, data)
        else:
            self._event_queue.append((event_type, data, time.time()))
    
    def _handle_event(self, event_type: str, data: Dict[str, Any]):
        """Handle an event by calling all subscribers.
        
        Args:
            event_type: Event type
            data: Event data
        """
        if event_type not in self._subscriptions:
            return
        
        for subscription in self._subscriptions[event_type]:
            try:
                subscription.callback(event_type, data)
                self._stats["events_handled"] += 1
            except Exception as e:
                self._stats["errors"] += 1
                self.logger.error(
                    f"Error handling event {event_type} in {subscription.subscriber_id}: {e}",
                    exc_info=True
                )
    
    def process_queue(self, max_events: Optional[int] = None):
        """Process queued events.
        
        Args:
            max_events: Maximum number of events to process (None = all)
        """
        count = 0
        while self._event_queue and (max_events is None or count < max_events):
            event_type, data, timestamp = self._event_queue.pop(0)
            self._handle_event(event_type, data)
            count += 1
    
    def _add_to_history(self, event_type: str, data: Dict[str, Any]):
        """Add event to history.
        
        Args:
            event_type: Event type
            data: Event data
        """
        self._event_history.append({
            "type": event_type,
            "data": data,
            "timestamp": time.time()
        })
        
        # Trim history if too long
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
    
    def get_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get event history.
        
        Args:
            event_type: Filter by event type (None = all)
            limit: Maximum events to return
            
        Returns:
            List of historical events
        """
        history = self._event_history
        
        if event_type:
            history = [e for e in history if e["type"] == event_type]
        
        return history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            **self._stats,
            "active_subscriptions": sum(len(subs) for subs in self._subscriptions.values()),
            "event_types": len(self._subscriptions),
            "queued_events": len(self._event_queue)
        }
    
    def clear_history(self):
        """Clear event history."""
        self._event_history.clear()
    
    def reset_stats(self):
        """Reset statistics."""
        self._stats = {
            "events_emitted": 0,
            "events_handled": 0,
            "errors": 0
        }


# Global event bus instance
_global_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance.
    
    Returns:
        Global EventBus instance
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus(enable_history=True)
    return _global_event_bus
