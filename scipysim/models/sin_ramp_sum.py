from scipysim.actors import Model, MakeChans
from scipysim.actors.signal import Ramp
from scipysim.actors.math.trig import CTSinGenerator
from scipysim.actors.math import Summer
from scipysim.actors.display import Plotter

import logging
logging.basicConfig( level=logging.INFO )
logging.info( "Logger enabled" )

class SinRampSum( Model ):
    '''
    Demonstrate sources, summation, and plotting.
    '''

    def __init__( self ):
        chan1, chan2, chan3 = MakeChans( 3 )

        src1 = Ramp( chan1 )
        src2 = CTSinGenerator( chan2, amplitude=1.0, freq=1.0 )

        summer = Summer( [chan1, chan2], chan3 )
        dst = Plotter( chan3, title="Sin/Ramp Sum" )

        self.components = [src1, src2, summer, dst]

if __name__ == '__main__':
    SinRampSum().run()
