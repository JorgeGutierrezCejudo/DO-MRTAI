"""
EventLogger.py - Event Logging System

Simple event logging system to track all events during simulation.
Stores events in chronological order and allows filtering by type.

Author: Jorge
Date: 2024
"""

class EventLogger:
    """
    Event logger that maintains a chronological list of all simulation events.
    
    Supports logging various event types (Task, Vehicle, Implement, Simulation)
    and retrieving events filtered by type.
    """
    
    def __init__(self):
        """Initialize empty event list."""
        self.events = []

    def log_event(self, event):
        """
        Add an event to the log.
        
        Args:
            event (Event): Event object to log
        """
        self.events.append(event)

    def get_events_by_type(self, event_type=None):
        """
        Retrieve logged events, optionally filtered by type.
        
        Args:
            event_type (str, optional): Filter by event type 
                                        (e.g., "Task", "Vehicle", "Implement", "Simulation")
        
        Returns:
            list: Filtered list of events (or all events if event_type=None)
        """
        if event_type:
            return [event for event in self.events if event.event_type == event_type]
        return self.events

    def __str__(self):
        """Return string representation of all logged events."""
        return "\n".join(str(event) for event in self.events)
