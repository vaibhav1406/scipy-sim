'''
Created on 23/11/2009

@author: brian
'''

from models.actors import Channel, Plotter, Ramp, Summer, RandomSource, Model

import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.INFO)
logging.info("Logger enabled")

class NoiseyRamp(Model):
    """
    This model simulates a ramp source and a random source being added together
    The signals are in sync - there are NO missing tags.
     ______
    |      |
    | ramp |----\
    |  /   |     \      ______     ________
    |______|      \____|      |    |      |
                       | Sum  |____| Plot |
                   ____|      |    |______|
     ______       /    |______|
    |      |     /
    | Rand |----/
    |______|
    
    """
    
    def __init__(self):
        '''Setup the simulation'''
        connection1 = Channel()
        connection2 = Channel()
        connection3 = Channel()
    
        src1 = Ramp(connection1)
        src2 = RandomSource(connection2)
        summer = Summer([connection1, connection2], connection3)
        dst = Plotter(connection3)
    
        self.components = [src1, src2, summer, dst]
    
if __name__ == '__main__':
    NoiseyRamp().run()

