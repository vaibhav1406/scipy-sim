'''
A discrete sin stem plotter.

@note This simulation uses the DTSin class, an alternative would be to use the
trig function sin with an appropriate ramp source.


Created on 04/12/2009

@author: allan, brian
'''
import models.actors
from models.actors import Channel, Stemmer, DTSin


import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.INFO)
logging.info("Logger enabled")


def run_dtsin_stem():
    connection1 = Channel("DT")

    src = DTSin(connection1) 
    dst = Stemmer(connection1)

    components = [src, dst]

    logging.info("Starting discrete time sin stem plot simulation")
    [component.start() for component in components]
    logging.debug("Finished starting actors")

    plt.show()   # The program will stay "running" while this plot is open

    [component.join() for component in components]
        
    logging.info("Finished running simulation")

if __name__ == '__main__':
    run_dtsin_stem()
