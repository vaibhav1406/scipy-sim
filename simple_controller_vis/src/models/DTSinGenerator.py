from actors.sin import Sin
from actors.ramp import Ramp
from actors.Actor import Channel
from actors.model import Model

import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Logger enabled in DTSinGenerator")

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
