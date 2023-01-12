import simpy
import random
from link import *

RANDOM_SEED = 42

def sender(name, link):
  counter = 0
  while True:
    with link.receive() as req:
      result = yield req | env.timeout(random.randint(1,5))
      if req not in result:
        event = Event("broadcast_send", {"sender": name, "message": "Hello World %d" % counter, "time": env.now})
        counter += 1
        bc_link.send(event)
        continue
      event = result[req]
      print("%s Received event '%s' at time %d" % (name, event, env.now))
      if event.name == "broadcast_send":
        bc_link.send(Event("broadcast_deliver", {"sender": name, "receiver": event.attributes["sender"], "message": event.attributes["message"], "time": env.now}))
      yield env.timeout(random.randint(1,5))

def receiver(name, link):
  while True:
    event = yield link.receive()
    print("%s Received event '%s' at time %d" % (name, event, env.now))
    bc_link.send(Event("broadcast_deliver", {"sender": name, "receiver": event.attributes["sender"], "message": event.attributes["message"], "time": env.now}))
    yield env.timeout(random.randint(1,5))


env = simpy.Environment()
random.seed(RANDOM_SEED)
bc_link = BroadcastLink(env, capacity=1, min_delay=1, max_delay=10, timeout=5)
link1 = bc_link.get_new_out_link("Sender")
link2 = bc_link.get_new_out_link("Receiver 1")
link3 = bc_link.get_new_out_link("Receiver 2")
env.process(sender("Sender", link1))
env.process(receiver("Receiver 1", link2))
env.process(receiver("Receiver 2", link3))
env.process(bc_link.run())
env.run(until=40)