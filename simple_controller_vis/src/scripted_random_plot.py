'''
Created on 23/11/2009

@author: brian
'''
import Queue as queue
from actors.plotter import Plotter
from actors.random_signal import RandomSource
import matplotlib.pyplot as plt

import logging
#logging.basicConfig(level=logging.DEBUG)
#logging.info("Logger enabled")


def run_random_plot():
    '''
    Run a simple example connecting a random source with a plotter
    '''
    connection = queue.Queue(0)
    src = RandomSource(connection)
    dst = Plotter(connection)

    components = [src, dst]

    logging.info("Starting simulation")
    for component in components:
        component.start()
    logging.debug("Finished starting actors")


    plt.show()   # The program will stay "running" while this plot is open

    src.join()
    dst.join()

    logging.debug("Finished running actor")

if __name__ == '__main__':
    run_random_plot()
