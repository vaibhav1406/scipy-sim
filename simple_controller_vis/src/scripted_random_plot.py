'''
Created on 23/11/2009

@author: brian
'''
try:
    import queue
except ImportError:
    import Queue as queue
   
from actors.plotter import Plotter

from actors.random_signal import RandomSource
import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Logger enabled")


if __name__ == '__main__':
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
