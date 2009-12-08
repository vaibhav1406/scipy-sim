'''
This simulation is made up of a composite model containing a sin generator
and a standard plotting actor.
'''

from models.actors import Stemmer, Channel
from models.DTSinGenerator import DTSinGenerator
import matplotlib.pyplot as plt
import logging
logging.basicConfig(level=logging.INFO)

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