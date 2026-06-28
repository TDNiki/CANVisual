from collections import defaultdict

class EventHandler:
    # {
    #     event_id : str = [func link]
    # }

    def __init__(self):
        self._events = defaultdict(list)
    
    def sub(self, event_id, callback):
        self._events[event_id].append(callback)
    
    def unsub(self, event_id, callback):
        self._events[event_id].remove(callback)
    
    def invoke(self, event_id, *args, **kwargs):
        for call in self._events[event_id]:
            call(*args, **kwargs)
    
