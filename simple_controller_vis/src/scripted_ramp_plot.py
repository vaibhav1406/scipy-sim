'''
Created on 23/11/2009

@author: brian
'''
from models.actors import Plotter, Ramp, Channel

import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Logger enabled")


def run_ramp_plot():
    '''
    This example simulation connects a ramp source to a plotter
    '''
    connection = Channel()
    src = Ramp(connection)
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
    run_ramp_plot()
