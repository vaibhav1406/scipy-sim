
from models.actors import Model, MakeChans, Ramp, Summer
from models.actors.display import Plotter
import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.INFO)
logging.info("Logger enabled")

class Double_Ramp_Plot(Model):
    '''
    A simple example simulation where two ramp sources 
    are connected to a summer block and then plotted.
    '''
    
    def run(self):
        '''
        A basic simulation that sums two (default) Ramp sources 
        together and plots the combined output.
        '''
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
    Double_Ramp_Plot().run()
