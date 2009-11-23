'''
Created on 23/11/2009

@author: brian
'''
try:
    import queue
except ImportError:
    import Queue as queue
   
from actors.plotter import Plotter
from actors.proportional import Proportional
from actors.ramp import Ramp
import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Logger enabled")



if __name__ == '__main__':
    ramp2gain = queue.Queue(0)
    gain2plot = queue.Queue(0)
    
    
    src = Ramp(ramp2gain)
    filt = Proportional(ramp2gain, gain2plot)
    dst = Plotter(gain2plot)
    
    components = [src, filt, dst]
    
    logging.info("Starting simulation with Ramp input, proportional gain, and dynamic plotter output")
    for component in components:
        component.start()
    logging.debug("Finished starting actors")
    

    plt.show()   # The program will stay "running" while this plot is open
    
    src.join()
    filt.join()
    dst.join()
    
    logging.debug("Finished running actor")