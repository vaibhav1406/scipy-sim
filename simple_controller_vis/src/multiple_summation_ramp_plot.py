'''
Created on 23/11/2009

@author: brian
'''


from models.actors import Channel, Plotter, Ramp, Summer, Copier, RandomSource

import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.INFO)
logging.info("Logger enabled")


def run_multi_sum():
    '''
    This example connects 3 sources ( 2 ramps and a random) to a summer block
    The final output AND one of the ramps are dynamically plotted.
    
    The components are all generating the same sequence of tags so are always
    synchronised
    '''

    connection1 = Channel()
    connection1_1 = Channel()
    connection1_2 = Channel()
    connection2 = Channel()
    connection3 = Channel()
    connection4 = Channel()

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
