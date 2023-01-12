import simpy
import random
from link import *
RANDOM_SEED = 42

env = simpy.Environment()
random.seed(RANDOM_SEED)

bc_link = BroadcastLink(env, capacity=1, min_delay=1, max_delay=10)

link1 = bc_link.get_new_link()
link2 = bc_link.get_new_link()

def sender():
  while True:
    yield env.timeout(random.randint(1,5))
    msg = "Message sent at time %d" % env.now
    print(msg)
    bc_link.send(msg)

def receiver(name, link):
  while True:
    msg = yield link.receive()
    print("%s Received message '%s' at time %d" % (name, msg, env.now))
    yield env.timeout(random.randint(1,5))

env.process(sender())
env.process(receiver("Receiver 1", link1))
env.process(receiver("Receiver 2", link2))
env.run(until=40)