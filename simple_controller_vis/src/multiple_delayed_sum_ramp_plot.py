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
from actors.delay import Delay
from actors.random_signal import RandomSource
import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Logger enabled")


if __name__ == '__main__':
    connection1 = queue.Queue(0)
    connection2 = queue.Queue(0)
    connection3 = queue.Queue(0)
    connection4 = queue.Queue(0)
    connection5 = queue.Queue(0)
    
    
    src1 = Ramp(connection1)
    src2 = Ramp(connection2)
    src3 = RandomSource(connection3)
    
    delay1 = Delay(connection2, connection5)
    
    summer = Summer([connection1, connection5, connection3], connection4)
    dst = Plotter(connection4)
    
    components = [src1, src2, src3, summer, dst, delay1]
    
    logging.info("Starting simulation")
    for component in components:
        component.start()
    logging.debug("Finished starting actors")
    

    plt.show()   # The program will stay "running" while this plot is open
    
    for component in components:
        component.join()
    
    logging.debug("Finished running actor")
