import simpy
import random
import logging
from common import *

class PointToPointLink(Process):
    def __init__(self, env, processes = None, capacity=float("inf"), min_delay=0, max_delay=0):
        super().__init__(env)
        if processes is None:
            processes = set()
        self.processes = set(processes)
        self.in_pipes = {
            process: simpy.Store(env, capacity=capacity) for process in processes
        }
        self.out_pipes = {
            process: simpy.Store(env, capacity=capacity) for process in processes
        }
        self.delivered = set()
        self.capacity = capacity
        self.min_delay = min_delay
        self.max_delay = max_delay

        self.add_process(self.id)

    def add_process(self, process):
        logging.info(f"Adding Process {process} to PointToPointLink {self.id}")
        self.processes.add(process)
        self.in_pipes[process] = simpy.Store(self.env, capacity=self.capacity)
        self.out_pipes[process] = simpy.Store(self.env, capacity=self.capacity)

    def put(self, event):
        logging.info(f"PointToPointLink {self.id} sending event {event}")
        yield self.env.timeout(random.randint(self.min_delay, self.max_delay))
        source_process = event.source
        yield self.in_pipes[source_process].put(event)

    def get(self, process):
        destination_process = process
        return self.out_pipes[destination_process].get()
    
    def run(self):
        logging.info(f"PointToPointLink {self.id} started")
        while True:
            with self.get(self.id) as req:
                result = yield req | self.env.any_of([pipe.get() for pipe in self.in_pipes.values()])
                if req not in result:
                    # we got an event from one of the input pipes
                    event = list(dict(result).values())[0]
                    logging.info(f"PointToPointLink {self.id} processing event {event}")
                    destination_process = event.destination
                    yield self.out_pipes[destination_process].put(event)
                    if event.id not in self.delivered:
                        yield self.out_pipes[event.source].put(self._pl_deliver_event(event))
                        # self.env.process(self.put(self._pl_deliver_event(event)))
                        self.delivered.add(event.id)
                    continue
                # we got a request from our output pipe
                event = result[req]
                self.env.process(self.handle_event(event))

    def handle_event(self, event):
        logging.info(f"PointToPointLink {self.id} handling event {event}")
        yield self.env.timeout(1)

    def _pl_deliver_event(self, event):
        return Event(generate_id(), "pl_deliver", self.id, event.source, event.data)