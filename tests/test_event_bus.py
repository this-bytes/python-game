"""Tests for Event Bus System."""

import pytest
from src.core.event_bus import EventBus, EventPriority, Event


class TestEventBus:
    """Test suite for EventBus."""
    
    def test_initialization(self):
        """Test event bus initializes correctly."""
        bus = EventBus()
        assert bus.get_pending_count() == 0
        assert len(bus.get_history()) == 0
    
    def test_subscribe_and_publish(self):
        """Test basic subscribe and publish flow."""
        bus = EventBus()
        events_received = []
        
        def handler(event):
            events_received.append(event)
        
        bus.subscribe("test_event", handler)
        bus.publish("test_event", {"value": 42})
        bus.process_events()
        
        assert len(events_received) == 1
        assert events_received[0].event_type == "test_event"
        assert events_received[0].data["value"] == 42
    
    def test_multiple_subscribers(self):
        """Test multiple subscribers to same event."""
        bus = EventBus()
        handler1_calls = []
        handler2_calls = []
        
        bus.subscribe("event", lambda e: handler1_calls.append(e))
        bus.subscribe("event", lambda e: handler2_calls.append(e))
        
        bus.publish("event", {"msg": "hello"})
        bus.process_events()
        
        assert len(handler1_calls) == 1
        assert len(handler2_calls) == 1
    
    def test_priority_ordering(self):
        """Test events processed in priority order."""
        bus = EventBus()
        call_order = []
        
        bus.subscribe("event", lambda e: call_order.append("low"), EventPriority.LOW)
        bus.subscribe("event", lambda e: call_order.append("high"), EventPriority.HIGH)
        bus.subscribe("event", lambda e: call_order.append("normal"), EventPriority.NORMAL)
        bus.subscribe("event", lambda e: call_order.append("critical"), EventPriority.CRITICAL)
        
        bus.publish("event", {})
        bus.process_events()
        
        assert call_order == ["critical", "high", "normal", "low"]
    
    def test_unsubscribe(self):
        """Test unsubscribing from events."""
        bus = EventBus()
        events_received = []
        
        def handler(event):
            events_received.append(event)
        
        sub_id = bus.subscribe("event", handler)
        bus.publish("event", {"value": 1})
        bus.process_events()
        
        assert len(events_received) == 1
        
        bus.unsubscribe(sub_id)
        bus.publish("event", {"value": 2})
        bus.process_events()
        
        # Should still be 1, not 2
        assert len(events_received) == 1
    
    def test_event_history(self):
        """Test event history tracking."""
        bus = EventBus(max_history=3)
        
        bus.publish("event1", {"id": 1})
        bus.publish("event2", {"id": 2})
        bus.publish("event3", {"id": 3})
        bus.publish("event4", {"id": 4})
        bus.process_events()
        
        history = bus.get_history()
        assert len(history) == 3  # Max history is 3
        assert history[0].event_type == "event4"  # Newest first
        assert history[1].event_type == "event3"
        assert history[2].event_type == "event2"
    
    def test_filtered_history(self):
        """Test filtering event history by type."""
        bus = EventBus()
        
        bus.publish("type_a", {})
        bus.publish("type_b", {})
        bus.publish("type_a", {})
        bus.process_events()
        
        history_a = bus.get_history("type_a")
        assert len(history_a) == 2
        assert all(e.event_type == "type_a" for e in history_a)
    
    def test_statistics(self):
        """Test event bus statistics tracking."""
        bus = EventBus()
        
        bus.publish("event1", {})
        bus.publish("event2", {})
        bus.publish("event1", {})
        bus.process_events()
        
        stats = bus.get_stats()
        assert stats["total_events_published"] == 3
        assert stats["total_events_processed"] == 3
        assert stats["events_by_type"]["event1"] == 2
        assert stats["events_by_type"]["event2"] == 1
    
    def test_clear_stats(self):
        """Test clearing statistics."""
        bus = EventBus()
        
        bus.publish("event", {})
        bus.process_events()
        
        bus.clear_stats()
        stats = bus.get_stats()
        
        assert stats["total_events_published"] == 0
        assert stats["total_events_processed"] == 0
    
    def test_error_handling(self):
        """Test that errors in handlers don't stop event processing."""
        bus = EventBus()
        successful_calls = []
        
        def bad_handler(event):
            raise ValueError("Test error")
        
        def good_handler(event):
            successful_calls.append(event)
        
        bus.subscribe("event", bad_handler)
        bus.subscribe("event", good_handler)
        
        bus.publish("event", {})
        bus.process_events()
        
        # Good handler should still be called despite bad handler error
        assert len(successful_calls) == 1
