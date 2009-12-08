'''
Created on 23/11/2009

@author: brian
'''
from models.actors import Plotter, RandomSource, Channel
import matplotlib.pyplot as plt

import logging
#logging.basicConfig(level=logging.DEBUG)
#logging.info("Logger enabled")


def run_random_plot():
    '''
    Run a simple example connecting a random source with a plotter
    '''
    connection = Channel()
    src = RandomSource(connection)
    dst = Plotter(connection)

    components = [src, dst]

    logging.info("Starting simulation")
    [component.start() for component in components]
    
    logging.debug("Finished starting actors")
    plt.show()   # The program will stay "running" while this plot is open
    
    [component.join() for component in components]

    logging.debug("Finished running actor")

if __name__ == '__main__':
    run_random_plot()
