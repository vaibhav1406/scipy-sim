from scipysim.actors import Model, MakeChans
from scipysim.actors.signal import Ramp
from scipysim.actors.math import Summer
from scipysim.actors.display import Plotter

import logging
logging.basicConfig( level=logging.INFO )
logging.info( "Logger enabled" )

class Double_Ramp_Plot( Model ):
    '''
    A simple example simulation where two ramp sources 
    are connected to a summer block and then plotted.
    '''

    def __init__( self ):
        '''
        A basic simulation that sums two (default) Ramp sources 
        together and plots the combined output.
        '''
        connection1, connection2, connection3 = MakeChans( 3 )

        src1 = Ramp( connection1 )
        src2 = Ramp( connection2 )

        summer = Summer( [connection1, connection2], connection3 )
        dst = Plotter( connection3, title="Double Ramp Sum" )

        self.components = [src1, src2, summer, dst]

if __name__ == '__main__':
    Double_Ramp_Plot().run()
