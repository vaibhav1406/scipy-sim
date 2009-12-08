'''
A simple example simulation where two ramps 
are connected to a summer and then plotted.
'''
from models.actors import Channel, Plotter, Ramp, Summer

import matplotlib.pyplot as plt
from models.actors.Actor import MakeChans

import logging
logging.basicConfig(level=logging.INFO)
logging.info("Logger enabled")

def run_ramp_plot():
    '''A basic simulation that sums two Ramp sources together and plots.'''
    connection1, connection2, connection3 = MakeChans(3)

    src1 = Ramp(connection1)
    src2 = Ramp(connection2)
    
    summer = Summer([connection1, connection2], connection3)
    dst = Plotter(connection3)

    components = [src1, src2, summer, dst]

    logging.info("Starting actors in simulation")
    [component.start() for component in components]
    logging.info("Finished starting actors, running simulation...")

    plt.show()   # The program will stay "running" while this plot is open

    [component.join() for component in components]
    logging.info("Finished running simulation")


if __name__ == '__main__':
    run_ramp_plot()