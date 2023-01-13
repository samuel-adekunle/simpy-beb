import simpy
import random
import logging
from agent import *
from link import *

RANDOM_SEED = 42
SIM_TIME = 100

if __name__ == "__main__":
    logging.info("Random seed: %s" % RANDOM_SEED)
    random.seed(RANDOM_SEED)
    logging.basicConfig(filename="out.log", level=logging.DEBUG)
    env = simpy.Environment()
    pl = PointToPointLink(env)
    receiver = Receiver(env, pl)
    sender = Sender(env, pl, receiver.id)
    logging.info("Starting simulation with sim time: %s" % SIM_TIME)
    env.run(until=SIM_TIME)
    logging.info("Simulation complete")
