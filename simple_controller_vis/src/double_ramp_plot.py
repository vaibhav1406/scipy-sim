'''
Created on 23/11/2009

@author: brian
'''
import Queue as queue

from actors.plotter import Plotter
from actors.ramp import Ramp
from actors.summer import Summer

import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Logger enabled")

def run_ramp_plot():
    connection1 = queue.Queue(0)
    connection2 = queue.Queue(0)
    connection3 = queue.Queue(0)

    src1 = Ramp(connection1)
    src2 = Ramp(connection2)
    summer = Summer([connection1, connection2], connection3)
    dst = Plotter(connection3)

    components = [src1, src2, summer, dst]

    logging.info("Starting simulation")
    [component.start() for component in components]
    logging.debug("Finished starting actors")

    plt.show()   # The program will stay "running" while this plot is open

    [component.join() for component in components]
    logging.debug("Finished running simulation")


if __name__ == '__main__':
    run_ramp_plot()