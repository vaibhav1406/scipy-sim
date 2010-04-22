'''
Created on 23/11/2009

@author: brian
'''

from scipysim.actors import Channel, Model
from scipysim.actors.display.bundlePlotter import BundlePlotter
from scipysim.actors.io import Bundle
from scipysim.actors.signal import Ramp, RandomSource
from scipysim.actors.math import Summer

import logging
logging.basicConfig(level=logging.INFO)
logging.info("Logger enabled")

class NoiseyRamp(Model):
    """
    This model simulates a ramp source and a random source being added together
    The signals are in sync - there are NO missing tags.

    """

    def __init__(self):
        '''Setup the simulation'''
        connection1 = Channel()
        connection2 = Channel()
        connection3 = Channel()
        connection4 = Channel()

        src1 = Ramp(connection1)
        src2 = RandomSource(connection2)
        summer = Summer([connection1, connection2], connection3)

        bundler = Bundle(connection3, connection4)
        dst = BundlePlotter(connection4, title="Scipy-Simulation: Noise + Ramp Sum", show=True)
        #dst = Plotter(connection3)

        self.components = [src1, src2, summer, bundler, dst]

if __name__ == '__main__':
    NoiseyRamp().run()

