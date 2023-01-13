import random
from common import *
from link import *

class Sender(Process):
    def __init__(self, env, pl: PointToPointLink, receiver: str, counter: int = 5, min_delay=0, max_delay=0):
        super().__init__(env)
        self.pl = pl
        self.pl.add_process(self.id)
        self.receiver = receiver
        self.counter = counter
        self.min_delay = min_delay
        self.max_delay = max_delay

    def run(self):
        for i in range(self.counter):
            with self.pl.get(self.id) as req:
              result = yield self.env.timeout(random.randint(self.min_delay, self.max_delay)) | req
              if req not in result:
                  # we timed out, need to send a message to receiver
                  event = Event(generate_id(), "pl_send", self.id, self.receiver, {"message": f"hello world {i}"})
                  self.env.process(self.pl.put(event))
                  continue
              # we got a request from our output pipe
              event = result[req]
              self.env.process(self.handle_event(event))

    def handle_event(self, event):
        raise NotImplementedError("Subclass must implement abstract method")


class Receiver(Process):
    def __init__(self, env, pl: PointToPointLink):
        super().__init__(env)
        self.pl = pl
        self.pl.add_process(self.id)

    def run(self):
        while True:
            with self.pl.get(self.id) as req:
                event = yield req
                self.env.process(self.handle_event(event))

    def handle_event(self, event):
        raise NotImplementedError("Subclass must implement abstract method")
