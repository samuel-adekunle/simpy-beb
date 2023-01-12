import simpy
import random


class PointToPointLink(object):
  def __init__(self, env, capacity = float('inf'), min_delay=0, max_delay = 0):
    self.env = env
    self.capacity = capacity
    self.min_delay = min_delay
    self.max_delay = max_delay
    self.store = simpy.Store(self.env, capacity=capacity)

  def send(self, msg):
    self.env.process(self.latency(msg))

  def latency(self, msg):
    yield self.env.timeout(random.randint(self.min_delay, self.max_delay))
    self.store.put(msg)

  def receive(self):
    return self.store.get()

class BroadcastLink(object):
  def __init__(self, env, capacity = float('inf'), min_delay=0, max_delay = 0):
    self.env = env
    self.capacity = capacity
    self.min_delay = min_delay
    self.max_delay = max_delay
    self.links = []

  def get_new_link(self):
    link = PointToPointLink(self.env, self.capacity, self.min_delay, self.max_delay)
    self.links.append(link)
    return link

  def send(self, msg):
    for link in self.links:
      link.send(msg)
