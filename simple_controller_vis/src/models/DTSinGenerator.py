from actors.sin import Sin
from actors.ramp import Ramp
from actors.Actor import Channel
from actors.model import Model

import logging
logging.basicConfig(level=logging.info)
logging.info("Logger enabled in DTSinGenerator")

class DTSinGenerator(Model):
    '''A discrete sinusoidal signal generator. 
    Generates points with a ramp source which feeds into a sin trig function.
    
    Frequency is specified in cycles/sample ("digital frequency" or 
    "normalized frequency"), and phase in radians.
    '''
    
    def __init__(self, out, amplitude=1.0, freq=0.01, phi=0.0, simulation_length=100):
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
        
        # The values of the ramp will be ignored, it just provides the "clock"
        self.ramp = Ramp(self.chan1, resolution=1, simulation_time=self.simulation_length)
        # Note in this case we have connected the output of the last inner component directly to
        # the output of the model - this isn't always going to be the case.
        self.sin = Sin(self.chan1, self.out, amplitude=self.amplitude, freq=self.frequency, phi=self.phase)
        logging.info("Inner actors have been constructed")
        
    def process(self):
        logging.info("Running the DTSinGen model, starting inner components")
        components = [self.ramp, self.sin]
        [comp.start() for comp in components]
        logging.info("Inner components started, waiting for simulation to finish.")
        [comp.join() for comp in components]
        self.stop = True
        logging.info("Model has finished running.")
