import random
from common import *
from link import *

class Timer(Process):
    def __init__(self, env, pl: PointToPointLink, receiver: str, delay: int):
        super().__init__(env)
        self.pl = pl
        self.pl.add_process(self.id)
        self.receiver = receiver
        self.delay = delay

    def run(self):
        logging.info(f"Timer {self.id} started")
        while True:
            with self.pl.get(self.id) as req:
                event = yield req
                self.env.process(self.handle_event(event))

    def handle_event(self, event):
        logging.info(f"Timer {self.id} handling event {event} received from {event.source}")
        if self.counter <= 0:
            yield self.env.timeout(5)
            return
        event = Event(generate_id(), "pl_send", self.id, self.receiver, {"message": f"hello world {self.counter}"})
        self.counter -= 1
        self.env.process(self.pl.put(event))
        yield self.env.timeout(random.randint(self.min_delay, self.max_delay)

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
        logging.info(f"Sender {self.id} started")
        while True:
            with self.pl.get(self.id) as req:
              result = yield req | self.env.timeout(random.randint(self.min_delay, self.max_delay))
              if req not in result:
                if self.counter <= 0:
                    yield self.env.timeout(5)
                    continue
                  # we timed out, need to send a message to receiver
                event = Event(generate_id(), "pl_send", self.id, self.receiver, {"message": f"hello world {self.counter}"})
                self.counter -= 1
                self.env.process(self.pl.put(event))
                continue
              # we got a request from our output pipe
              event = result[req]
              self.env.process(self.handle_event(event))

    def handle_event(self, event):
        logging.info(f"Sender {self.id} handling event {event} received from {event.source}")
        yield self.env.timeout(1)


class Receiver(Process):
    def __init__(self, env, pl: PointToPointLink):
        super().__init__(env)
        self.pl = pl
        self.pl.add_process(self.id)

    def run(self):
        logging.info(f"Receiver {self.id} started")
        while True:
            with self.pl.get(self.id) as req:
                event = yield req
                self.env.process(self.handle_event(event))

    def handle_event(self, event):
        logging.info(f"Receiver {self.id} handling event {event} received from {event.source}")
        yield self.env.timeout(1)
