"""Event Bus System for decoupled communication between game systems.

The Event Bus provides a publish-subscribe mechanism for game systems to communicate
without direct dependencies. Events are priority-based and processed in order.

Event Types (use these strings when publishing/subscribing):
    - "incident_generated" - New incident created
    - "incident_assigned" - Incident assigned to specialist
    - "incident_resolved" - Incident successfully resolved
    - "incident_failed" - Incident failed (SLA breach)
    - "specialist_hired" - New specialist added to roster
    - "specialist_level_up" - Specialist gained a level
    - "automation_unlocked" - Automation script unlocked
    - "money_earned" - Money added to game state
    - "money_spent" - Money deducted from game state
    - "game_paused" - Game paused by player
    - "game_resumed" - Game resumed by player
    - "prestige_performed" - Player performed prestige reset
    - "achievement_unlocked" - Achievement completed
    - "feature_toggled" - Feature flag changed
"""

from typing import Callable, Dict, List, Any
from dataclasses import dataclass, field
from enum import IntEnum
import time


class EventPriority(IntEnum):
    """Priority levels for event processing."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class EventSubscription:
    """Represents a subscription to an event type."""
    event_type: str
    callback: Callable
    priority: EventPriority = EventPriority.NORMAL
    subscription_id: str = ""
    
    def __post_init__(self):
        """Generate subscription ID if not provided."""
        if not self.subscription_id:
            self.subscription_id = f"{self.event_type}_{id(self.callback)}"


@dataclass
class Event:
    """Represents a single event in the system."""
    event_type: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    source: str = "unknown"


class EventBus:
    """Central event bus for publish-subscribe communication.
    
    Features:
    - Priority-based event handling (LOW → NORMAL → HIGH → CRITICAL)
    - Event history tracking for debugging
    - Performance statistics
    - Hot-reloadable subscriptions
    
    Example:
        ```python
        # Subscribe to events
        event_bus.subscribe("incident_generated", handle_new_incident, EventPriority.HIGH)
        
        # Publish events
        event_bus.publish("incident_generated", {"incident_id": "inc_001"}, source="generator")
        
        # Process events
        event_bus.process_events()
        ```
    """
    
    def __init__(self, max_history: int = 100):
        """Initialize the event bus.
        
        Args:
            max_history: Maximum number of events to keep in history
        """
        self._subscriptions: Dict[str, List[EventSubscription]] = {}
        self._pending_events: List[Event] = []
        self._event_history: List[Event] = []
        self._max_history = max_history
        
        # Performance tracking
        self._stats = {
            "total_events_published": 0,
            "total_events_processed": 0,
            "events_by_type": {},
            "average_processing_time": 0.0
        }
    
    def subscribe(
        self, 
        event_type: str, 
        callback: Callable, 
        priority: EventPriority = EventPriority.NORMAL
    ) -> str:
        """Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to (e.g., "incident_generated")
            callback: Function to call when event occurs
            priority: Priority level for this subscription
            
        Returns:
            Subscription ID (for unsubscribing later)
        """
        subscription = EventSubscription(event_type, callback, priority)
        
        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = []
        
        self._subscriptions[event_type].append(subscription)
        
        # Sort by priority (highest first)
        self._subscriptions[event_type].sort(key=lambda s: s.priority, reverse=True)
        
        return subscription.subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from an event.
        
        Args:
            subscription_id: ID returned from subscribe()
            
        Returns:
            True if subscription was removed, False if not found
        """
        for event_type, subscriptions in self._subscriptions.items():
            for i, sub in enumerate(subscriptions):
                if sub.subscription_id == subscription_id:
                    subscriptions.pop(i)
                    return True
        return False
    
    def publish(
        self, 
        event_type: str, 
        data: Dict[str, Any], 
        source: str = "unknown"
    ):
        """Publish an event to the bus.
        
        Events are queued and processed during process_events().
        
        Args:
            event_type: Type of event (e.g., "incident_generated")
            data: Event payload data
            source: Source system publishing the event
        """
        event = Event(event_type, data, source=source)
        self._pending_events.append(event)
        
        # Track statistics
        self._stats["total_events_published"] += 1
        if event_type not in self._stats["events_by_type"]:
            self._stats["events_by_type"][event_type] = 0
        self._stats["events_by_type"][event_type] += 1
    
    def process_events(self):
        """Process all pending events in priority order.
        
        Should be called once per game frame to handle queued events.
        """
        if not self._pending_events:
            return
        
        start_time = time.time()
        events_processed = 0
        
        # Process all pending events
        while self._pending_events:
            event = self._pending_events.pop(0)
            self._dispatch_event(event)
            events_processed += 1
            
            # Add to history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
        
        # Update statistics
        if events_processed > 0:
            processing_time = time.time() - start_time
            self._stats["total_events_processed"] += events_processed
            
            # Update running average
            total_processed = self._stats["total_events_processed"]
            current_avg = self._stats["average_processing_time"]
            self._stats["average_processing_time"] = (
                (current_avg * (total_processed - events_processed) + processing_time) 
                / total_processed
            )
    
    def _dispatch_event(self, event: Event):
        """Dispatch an event to all subscribers.
        
        Args:
            event: Event to dispatch
        """
        if event.event_type not in self._subscriptions:
            return
        
        # Call all subscribers in priority order
        for subscription in self._subscriptions[event.event_type]:
            try:
                subscription.callback(event)
            except Exception as e:
                # Log error but continue processing other subscriptions
                print(f"Error in event handler for {event.event_type}: {e}")
    
    def get_pending_count(self) -> int:
        """Get number of pending events."""
        return len(self._pending_events)
    
    def get_history(self, event_type: str = None, limit: int = 10) -> List[Event]:
        """Get recent event history.
        
        Args:
            event_type: Filter by event type (None = all types)
            limit: Maximum number of events to return
            
        Returns:
            List of recent events (newest first)
        """
        history = self._event_history[::-1]  # Reverse to get newest first
        
        if event_type:
            history = [e for e in history if e.event_type == event_type]
        
        return history[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics.
        
        Returns:
            Dictionary with performance stats
        """
        return self._stats.copy()
    
    def clear_stats(self):
        """Reset statistics counters."""
        self._stats = {
            "total_events_published": 0,
            "total_events_processed": 0,
            "events_by_type": {},
            "average_processing_time": 0.0
        }
    
    def clear_history(self):
        """Clear event history."""
        self._event_history.clear()


# Global event bus instance (singleton pattern)
_global_event_bus: EventBus = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance.
    
    Returns:
        Global EventBus singleton
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus
