'''
Created on 23/11/2009

@author: brian
'''

import Queue as queue

from actors.plotter import Plotter
from actors.ramp import Ramp
from actors.summer import Summer
from actors.delay import Delay
from actors.random_signal import RandomSource

import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.INFO)
logging.info("Logger enabled")


def run_multi_delay_ramp_sum_plot():
    connection1 = queue.Queue(0)
    connection2 = queue.Queue(0)
    connection3 = queue.Queue(0)
    connection4 = queue.Queue(0)
    connection5 = queue.Queue(0)
    
    res = 10
    simulation_length = 120
    
    src1 = Ramp(connection1, resolution=res, simulation_time=simulation_length)
    src2 = Ramp(connection2, resolution=res, simulation_time=simulation_length)
    src3 = RandomSource(connection3, resolution=res, simulation_time=simulation_length)

    # The following "magic number" is one time step, 
    # the delay must be an integer factor of this so the events line up 
    # for the summer block to work...
    time_step = 0.10008340283569642
    delay1 = Delay(connection2, connection5, 3 * time_step)

    summer = Summer([connection1, connection5, connection3], connection4)
    dst = Plotter(connection4)

    components = [src1, src2, src3, summer, dst, delay1]

    logging.info("Starting simulation")
    [component.start() for component in components]
    logging.info("Finished starting actors, opening plot...")


    plt.show()   # The program will stay "running" while this plot is open
    logging.info("Plot was closed")
    [component.join() for component in components]
        

    logging.debug("Finished running actor")

if __name__ == '__main__':
    run_multi_delay_ramp_sum_plot()
