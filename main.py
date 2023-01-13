import simpy
import random
import logging
import datetime
from agent import *
from link import *

RANDOM_SEED = 42
SIM_TIME = 50

if __name__ == "__main__":
    logging.basicConfig(filename=f"./log/{datetime.datetime.now()}.log", level=logging.INFO)
    logging.info("Random seed: %s" % RANDOM_SEED)
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    pl = PointToPointLink(env, capacity=2, min_delay=1, max_delay=5)
    receiver = Receiver(env, pl)
    sender = Sender(env, pl, receiver.id, counter=1, min_delay=1, max_delay=5)
    logging.info("Starting simulation with sim time: %s" % SIM_TIME)
    env.run(until=SIM_TIME)
    logging.info("Simulation complete")
