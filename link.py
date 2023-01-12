import simpy
import random
from common import *

# Perfect PointToPoint Link
class PointToPointLink(object):
  def __init__(self, env, capacity = float('inf'), min_delay=0, max_delay = 0):
    self.env = env
    self.capacity = capacity
    self.min_delay = min_delay
    self.max_delay = max_delay
    self.store = simpy.Store(self.env, capacity=capacity)

  def send(self, event):
    self.env.process(self.latency(event))

  def latency(self, event):
    yield self.env.timeout(random.randint(self.min_delay, self.max_delay))
    self.store.put(event)

  def receive(self):
    return self.store.get()

# Best Effort Broadcast Link
class BroadcastLink(object):
  def __init__(self, env, capacity = float('inf'), min_delay=0, max_delay = 0, timeout=1):
    self.env = env
    self.capacity = capacity
    self.min_delay = min_delay
    self.max_delay = max_delay

    self.in_link = self._new_link()
    self.out_links = {}

  def send(self, event):
    self.in_link.send(event)

  def get_new_out_link(self, name):
    new_link = self._new_link()
    self.out_links[name] = new_link
    return new_link

  def run(self):
    while True:
        event = yield self.in_link.receive()
        if event.name == "broadcast_send":
          for link in self.out_links.values():
            link.send(event)
        elif event.name == "broadcast_deliver":
          self.out_links[event.attributes["receiver"]].send(event)
        else:
          raise Exception("Unknown event name: %s" % event.name)

  def _new_link(self):
    return PointToPointLink(self.env, self.capacity, self.min_delay, self.max_delay)