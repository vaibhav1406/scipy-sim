'''
Created on 23/11/2009

@author: brian
'''
from models.actors import Plotter, Proportional, Ramp, Channel
import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Logger enabled")



def run_ramp_gain_plot():
    '''
    This example connects a ramp to a gain to a plotter.
    It could easily have used a different ramp to achieve the same effect.
    '''
    ramp2gain = Channel()
    gain2plot = Channel()


    src = Ramp(ramp2gain)
    filt = Proportional(ramp2gain, gain2plot)
    dst = Plotter(gain2plot)

    components = [src, filt, dst]

    logging.info("Starting simulation")
    logging.info("Starting Ramp input, gain, and dynamic plotter output")
    [component.start() for component in components]
    
    logging.debug("Finished starting actors")


    plt.show()   # The program will stay "running" while this plot is open

    [c.join() for c in components]

    logging.debug("Finished running simulation")

if __name__ == '__main__':
    run_ramp_gain_plot()
