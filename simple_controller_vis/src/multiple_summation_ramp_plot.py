'''
Created on 23/11/2009

@author: brian
'''
import Queue as queue

from actors.plotter import Plotter

from actors.ramp import Ramp
from actors.summer import Summer
from actors.copier import Copier
from actors.random_signal import RandomSource
import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.INFO)
logging.info("Logger enabled")


def run_multi_sum():
    '''
    This example connects 3 sources ( 2 ramps and a random) to a summer block
    The output is then dynamically plotted.
    
    The components are all generating the same sequence of tags so are always
    synchronised
    '''

    connection1 = queue.Queue(0)
    connection1_1 = queue.Queue(0)
    connection1_2 = queue.Queue(0)
    connection2 = queue.Queue(0)
    connection3 = queue.Queue(0)
    connection4 = queue.Queue(0)

    src1 = Ramp(connection1, freq=1.0/120)
    src2 = Ramp(connection2)
    src3 = RandomSource(connection3)
    
    cloning_probe = Copier(connection1,[connection1_1, connection1_2])
    progress_plotter = Plotter(connection1_2)
    
    summer = Summer([connection1_1, connection2, connection3], connection4)
    dst = Plotter(connection4)

    components = [src1, src2, src3, summer, dst, cloning_probe, progress_plotter]

    logging.info("Starting simulation")
    [component.start() for component in components]
        
    logging.debug("Finished starting actors")

    logging.info('The program will stay "running" while the plot is open')
    plt.show()   

    [component.join() for component in components]
        

    logging.debug("Finished running simulation")

if __name__ == '__main__':
    run_multi_sum()
