from models.actors.stemmer import Stemmer
from models.DTSinGenerator import DTSinGenerator
import matplotlib.pyplot as plt
import logging
from models.actors.Actor import Channel
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