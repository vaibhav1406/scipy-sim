'''
Created on Dec 7, 2009

@author: brianthorne
'''

import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Logger enabled")


from Actor import Actor
class Model(Actor):
    '''
    A Model is a full citizen actor, it has its own thread of 
    control, it takes parameters and can have input and output 
    channels.
    '''


    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        super(Model, self).__init__(*args, **kwargs)
        logging.debug("Constructed a generic 'model'")
    
    def process(self):
        '''
        The process function is called as often as possible by the threading or multitasking library
        No guarantees are made about timing, or that anything will have changed for the input queues
        '''
        raise NotImplementedError()
    
from sin import Sin
from ramp import Ramp
from Actor import Channel

class DTSinGenerator(Model):
    '''A discrete sinusoidal signal generator. 
    Generates points with a ramp source which feeds into a sin trig function.
    '''
    
    def __init__(self, out, amplitude=1.0, freq=0.1, phi=0.0, simulation_length=100):
        '''
        Construct a discrete sin generator model.
        
        @param out: output channel
        '''
        logging.debug("Constructing a DTSinGenerator")
        super(DTSinGenerator, self).__init__()
        
        logging.debug("Setting model paramaters.")
        self.amplitude = amplitude
        self.frequency = freq
        self.phase = phi
        self.simulation_length = simulation_length
        
        assert out.domain is "DT"
        self.out = out
        
        logging.info('Constructing the inner actors that make up this "model"')
        self.chan1 = Channel()
        
        self.ramp = Ramp(self.chan1, amplitude=1, freq=1.0/self.simulation_length, resolution=1, simulation_time=self.simulation_length)
        self.sin = Sin(self.chan1, self.out)
        logging.info("Inner actors have been constructed")
        
    def process(self):
        logging.info("Running the DTSinGen model, starting inner components")
        components = [self.ramp, self.sin]
        [comp.start() for comp in components]
        logging.info("Inner components started, waiting for simulation to finish.")
        [comp.join() for comp in components]
        self.stop = True
        logging.info("Model has finished running.")

from stemmer import Stemmer
import matplotlib.pyplot as plt
def run_dt_sin_plotter_model():
    logging.info("Starting a combined model and actor simulation")
    
    chan1 = Channel("DT")
    src = DTSinGenerator(chan1)
    pltr = Stemmer(chan1)
    logging.info("Model and actor have been constructed")
    
    components = [src, pltr]
    [c.start() for c in components]
    logging.info("Model and Actor have been started - simulation is running")
    plt.show()
    [c.join() for c in components]
    logging.info("Model and actor simulation is over.")
        
if __name__ == "__main__":
    run_dt_sin_plotter_model()
        
    