'''
Created on 23/11/2009

@author: brian
'''
from scipysim.actors import MakeChans, Model
from scipysim.actors.signal import  Ramp, Delay, RandomSource
from scipysim.actors.math import Summer
from scipysim.actors.display import Plotter

import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Logger enabled")

class DelayedRampSum(Model):
    '''Delaying an input (by an integer timestep ) to the multi input summer.'''

    def __init__(self, res=10, simulation_length=40):
        super(DelayedRampSum, self).__init__()

        conns = MakeChans(5)

        src1 = Ramp(conns[0], resolution=res, simulation_time=simulation_length)
        src2 = Ramp(conns[1], resolution=res, simulation_time=simulation_length)
        src3 = RandomSource(conns[2], resolution=res, simulation_time=simulation_length)

        # The following "magic number" is one time step, (1/res)
        # the delay must be an integer factor of this so the events line up 
        # for the summer block to work...
        time_step = 1.0 / res
        delay1 = Delay(conns[1], conns[4], 3 * time_step)

        summer = Summer([conns[0], conns[4], conns[2]], conns[3])
        dst = Plotter(conns[3])

        self.components = [src1, src2, src3, summer, dst, delay1]


if __name__ == '__main__':
    DelayedRampSum().run()
