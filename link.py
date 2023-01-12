import simpy
import random
from common import *

# PointToPoint Link (pl)
class PointToPointLinks(object):
  def __init__(self, name, env, processes, capacity = float('inf'), min_delay=0, max_delay = 0):
    self.env = env
    self.name = name
    self.capacity = capacity
    self.min_delay = min_delay
    self.max_delay = max_delay
    self.in_links = {process: simpy.Store(env, capacity=capacity) for process in processes}
    self.out_links = {process: simpy.Store(env, capacity=capacity) for process in processes}
    self.delivered = {}

  def send(self, event):
    print("Sending %s from %s to %s at time %d" % (event.name, event.source, event.destination, self.env.now))
    self.in_links[event.source].put(event)

  def receive(self, name):
    event = self.out_links[name].get()
    return event

  def run(self):
    print("Starting %s at time %d" % (self.name, self.env.now))
    while True:
      with self.receive(self.name) as req:
        result = yield req | self.env.any_of([self.in_links[process].get() for process in self.in_links])
        event = list(dict(result).values())[0]
        print("%s Receiving %s from %s at time %d" % (self.name, event.name, event.source, self.env.now))
        if event.destination != self.name:
          event = list(dict(result).values())[0]
          self.env.process(self.latency(event))
          continue
        elif event.name == "pl_send":
          continue
        else:
          raise Exception("Unknown event name: %s" % event.name)

  def latency(self, event):
    yield self.env.timeout(random.randint(self.min_delay, self.max_delay))
    self.out_links[event.destination].put(event)
    id = hash((event.name, event.source, event.data["message"], event.data["time"]))
    if event.name != "pl_deliver" and id not in self.delivered:
      pl_deliver_event = Event("pl_deliver", self.name, event.source, event.data)
      self.send(pl_deliver_event)
      self.delivered[id] = pl_deliver_event

# Best Effort Broadcast Link (beb)
class BroadcastLink(object):
  def __init__(self, name, env, pl, processes):
    self.env = env
    self.name = name
    self.pl = pl
    self.processes = processes

  def run(self):
    print("Starting %s at time %d" % (self.name, self.env.now))
    while True:
        event = yield self.pl.receive(self.name)
        print("%s Receiving %s from %s at time %d" % (self.name, event.name, event.source, self.env.now))
        if event.name == "beb_broadcast":
          for process in self.processes:
            self.pl.send(Event("pl_send", self.name, process, event.data | {"beb_origin": event.source}))
        elif event.name == "pl_deliver":
          origin = event.data["beb_origin"]
          self.pl.send(Event("beb_deliver", self.name, origin, event.data))
        elif event.name == "pl_send":
          continue
        else:
          raise Exception("Unknown event name: %s" % event.name)
