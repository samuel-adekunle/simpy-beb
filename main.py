import simpy
import random
from link import *

RANDOM_SEED = 42

def sender(name, pl):
  counter = 0
  print("Starting %s at time %d" % (name, env.now))
  while True:
    with pl.receive(name) as req:
      result = yield req | env.timeout(random.randint(1,5))
      if req not in result:
        if counter < 1:
          event = Event("beb_broadcast", name, "beb", {"message": "Hello World %d" % counter, "time": env.now})
          pl.send(event)
          counter += 1
        continue
      event = result[req]
      if event.name == "pl_send":
        continue
      raise Exception("Unknown event name: %s" % event.name)

def receiver(name, pl):
  print("Starting %s at time %d" % (name, env.now))
  while True:
    with pl.receive(name) as req:
      result = yield req | env.timeout(random.randint(1,5))
      if req not in result:
        continue
      event = result[req]
      if event.name == "pl_send":
        continue
      raise Exception("Unknown event name: %s" % event.name)

env = simpy.Environment()
random.seed(RANDOM_SEED)
pl = PointToPointLinks("pl", env, ["pl", "beb", "Sender", "Receiver 1", "Receiver 2"], capacity=float("inf"), min_delay=1, max_delay=5)
beb = BroadcastLink("beb", env, pl, ["pl", "beb", "Sender", "Receiver 1", "Receiver 2"])
env.process(pl.run())
env.process(beb.run())
env.process(sender("Sender", pl))
env.process(receiver("Receiver 1", pl))
env.process(receiver("Receiver 2", pl))
env.run(until=100)