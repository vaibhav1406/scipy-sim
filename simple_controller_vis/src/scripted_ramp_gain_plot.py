'''
Created on 23/11/2009

@author: brian
'''
import Queue as queue

from actors.plotter import Plotter
from actors.proportional import Proportional
from actors.ramp import Ramp
import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Logger enabled")



def run_ramp_gain_plot():
    '''
    This example connects a ramp to a gain to a plotter.
    It could easily have used a different ramp to achieve the same effect.
    '''
    ramp2gain = queue.Queue(0)
    gain2plot = queue.Queue(0)


    src = Ramp(ramp2gain)
    filt = Proportional(ramp2gain, gain2plot)
    dst = Plotter(gain2plot)

    components = [src, filt, dst]

    logging.info("Starting simulation")
    logging.info("Starting Ramp input, gain, and dynamic plotter output")
    for component in components:
        component.start()
    logging.debug("Finished starting actors")


    plt.show()   # The program will stay "running" while this plot is open

    src.join()
    filt.join()
    dst.join()

    logging.debug("Finished running actor")

if __name__ == '__main__':
    run_ramp_gain_plot()
