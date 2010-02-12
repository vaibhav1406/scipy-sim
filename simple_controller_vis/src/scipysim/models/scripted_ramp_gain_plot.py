'''
Created on 23/11/2009

@author: brian
'''
from scipysim.actors.display import Plotter
from scipysim.actors import Channel, Model
from scipysim.actors.math import Proportional
from scipysim.actors.signal import Ramp

import logging
logging.basicConfig( level=logging.DEBUG )
logging.info( "Logger enabled" )

class RampGainPlot( Model ):
    '''
    This example connects a ramp to a gain to a plotter.
    It could easily have used a different ramp to achieve the same effect.
    '''

    def __init__( self ):
        '''Setup the sim'''
        super( RampGainPlot, self ).__init__()
        ramp2gain = Channel()
        gain2plot = Channel()

        src = Ramp( ramp2gain )
        filt = Proportional( ramp2gain, gain2plot )
        dst = Plotter( gain2plot )

        self.components = [src, filt, dst]

if __name__ == '__main__':
    SIM = RampGainPlot()
    SIM.run()
