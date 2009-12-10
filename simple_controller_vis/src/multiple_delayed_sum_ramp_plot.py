'''
Created on 23/11/2009

@author: brian
'''


from models.actors.Actor import Channel, MakeChans

from models.actors.plotter import Plotter
from models.actors.ramp import Ramp
from models.actors.summer import Summer
from models.actors.delay import Delay
from models.actors.random_signal import RandomSource

import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.INFO)
logging.info("Logger enabled")


def run_multi_delay_ramp_sum_plot():
    conns = MakeChans(5)
    
    res = 10
    simulation_length = 40
    
    src1 = Ramp(conns[0], resolution=res, simulation_time=simulation_length)
    src2 = Ramp(conns[1], resolution=res, simulation_time=simulation_length)
    src3 = RandomSource(conns[2], resolution=res, simulation_time=simulation_length)

    # The following "magic number" is one time step, (1/res)
    # the delay must be an integer factor of this so the events line up 
    # for the summer block to work...
    time_step = 1.0 / res
    delay1 = Delay(conns[1], conns[4], 3 * time_step)

    summer = Summer([conns[0], conns[4], conns[2]], conns[3])
    dst = Plotter(conns[3])

    components = [src1, src2, src3, summer, dst, delay1]

    logging.info("Starting simulation")
    [component.start() for component in components]
    logging.info("Finished starting actors, opening plot...")


    plt.show()   # The program will stay "running" while this plot is open
    logging.info("Plot was closed")
    [component.join() for component in components]
        

    logging.debug("Finished running simulation")

if __name__ == '__main__':
    run_multi_delay_ramp_sum_plot()
