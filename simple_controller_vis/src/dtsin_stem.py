'''
Created on 04/12/2009

@author: allan
'''
from actors.Actor import Channel

from actors.stemmer import Stemmer
from actors.dtsin import DTSin

import matplotlib.pyplot as plt


import logging
logging.basicConfig(level=logging.INFO)
logging.info("Logger enabled")


def run_dtsin_stem():
    connection1 = Channel("DT")

    src = DTSin(connection1) 
    dst = Stemmer(connection1)

    components = [src, dst]

    logging.info("Starting simulation")
    for component in components:
        component.start()
    logging.debug("Finished starting actors")


    plt.show()   # The program will stay "running" while this plot is open

    [component.join() for component in components]
        

    logging.debug("Finished running simulation")

if __name__ == '__main__':
    run_dtsin_stem()
