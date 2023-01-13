import simpy
import random
from common import *

class PointToPointLink(Process):
    def __init__(self, env, processes = None, capacity=float("inf"), min_delay=0, max_delay=0):
        super().__init__(env)
        if processes is None:
            processes = [self.id]
        self.processes = processes
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

    def add_process(self, process):
        self.processes.append(process)
        self.in_pipes[process] = simpy.Store(self.env, capacity=self.capacity)
        self.out_pipes[process] = simpy.Store(self.env, capacity=self.capacity)

    def put(self, event):
        yield self.env.timeout(random.randint(self.min_delay, self.max_delay))
        source_process = event.source
        yield self.in_pipes[source_process].put(event)

    def get(self, process):
        destination_process = process
        return self.out_pipes[destination_process].get()
    
    def run(self):
        while True:
            with self.get(self.id) as req:
                result = yield self.env.any_of([pipe.get() for pipe in self.in_pipes.values()]) | req
                if req not in result:
                    # we got an event from one of the input pipes
                    event = list(dict(result).values())[0]
                    destination_process = event.destination
                    yield self.out_pipes[destination_process].put(event)
                    if event.id not in self.delivered:
                        self.env.process(self.put(self._pl_deliver_event(event)))
                        self.delivered.add(event.id)
                    continue
                # we got a request from our output pipe
                event = result[req]
                self.env.process(self.handle_event(event))

    def handle_event(self, event):
      raise NotImplementedError("Subclass must implement abstract method")      

    def _pl_deliver_event(self, event):
        return Event(generate_id(), "pl_deliver", self.id, event.source, event.data)