import simpy
import random
from agent import *
from link import *

RANDOM_SEED = 42

if __name__ == "__main__":
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    pl = PointToPointLink(env)
    receiver = Receiver(env, pl)
    sender = Sender(env, pl, receiver.id)
    env.run(until=100)
