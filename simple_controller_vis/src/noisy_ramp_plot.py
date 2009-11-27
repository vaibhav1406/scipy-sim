'''
Created on 23/11/2009

@author: brian
'''
import Queue as queue

from actors.plotter import Plotter

from actors.ramp import Ramp
from actors.summer import Summer
from actors.random_signal import RandomSource
import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Logger enabled")


def run_noisy_ramp_plot():
    """
    This model simulates a ramp source and a random source being added together
    The signals are in sync - there are NO missing tags.
     ______
    |      |
    | ramp |----\
    |  /   |     \      ______     ________
    |______|      \____|      |    |      |
                       | Sum  |____| Plot |
                   ____|      |    |______|
     ______       /    |______|
    |      |     /
    | Rand |----/
    |______|
    
    """
    connection1 = queue.Queue(0)
    connection2 = queue.Queue(0)
    connection3 = queue.Queue(0)

    src1 = Ramp(connection1)
    src2 = RandomSource(connection2)
    summer = Summer([connection1, connection2], connection3)
    dst = Plotter(connection3)

    components = [src1, src2, summer, dst]

    logging.info("Starting simulation")
    for component in components:
        component.start()
    logging.debug("Finished starting actors")


    plt.show()   # The program will stay "running" while this plot is open

    src1.join()
    src2.join()
    summer.join()
    dst.join()

    logging.debug("Finished running actor")

if __name__ == '__main__':
    run_noisy_ramp_plot()

