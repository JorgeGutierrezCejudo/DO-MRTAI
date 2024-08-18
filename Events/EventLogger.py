class EventLogger:
    def __init__(self):
        self.events = []

    def log_event(self, event):
        self.events.append(event)

    def get_events_by_type(self, event_type=None):
        if event_type:
            return [event for event in self.events if event.event_type == event_type]
        return self.events

    def __str__(self):
        return "\n".join(str(event) for event in self.events)
