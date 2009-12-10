'''
Created on 23/11/2009

@author: brian
'''
import Queue as queue

from actors.plotter import Plotter

from actors.ramp import Ramp
from actors.summer import Summer
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
    connection2 = queue.Queue(0)
    connection3 = queue.Queue(0)
    connection4 = queue.Queue(0)

    src1 = Ramp(connection1)
    src2 = Ramp(connection2)
    src3 = RandomSource(connection3)
    summer = Summer([connection1, connection2, connection3], connection4)
    dst = Plotter(connection4)

    components = [src1, src2, src3, summer, dst]

    logging.info("Starting simulation")
    for component in components:
        component.start()
    logging.debug("Finished starting actors")


    plt.show()   # The program will stay "running" while this plot is open

    for component in components:
        component.join()

    logging.debug("Finished running actor")

if __name__ == '__main__':
    run_multi_sum()
