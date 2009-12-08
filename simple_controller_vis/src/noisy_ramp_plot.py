'''
Created on 23/11/2009

@author: brian
'''

from models.actors import Channel, Plotter, Ramp, Summer, RandomSource

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
    connection1 = Channel()
    connection2 = Channel()
    connection3 = Channel()

    src1 = Ramp(connection1)
    src2 = RandomSource(connection2)
    summer = Summer([connection1, connection2], connection3)
    dst = Plotter(connection3)

    components = [src1, src2, summer, dst]

    logging.info("Starting simulation")
    [component.start() for component in components]
    
    logging.debug("Finished starting actors")


    plt.show()   # The program will stay "running" while this plot is open

    [c.join() for c in components]
    logging.debug("Finished running simulation")

if __name__ == '__main__':
    run_noisy_ramp_plot()

