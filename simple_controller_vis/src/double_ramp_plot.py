'''
Created on 23/11/2009

@author: brian
'''
try:
    import queue
except ImportError:
    import Queue as queue
   
from actors.plotter import Plotter

from actors.ramp import Ramp
from actors.summer import Summer
import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Logger enabled")


if __name__ == '__main__':
    connection1 = queue.Queue(0)
    connection2 = queue.Queue(0)
    connection3 = queue.Queue(0)
    
    src1 = Ramp(connection1)
    src2 = Ramp(connection2)
    summer = Summer(connection1, connection2, connection3)
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
