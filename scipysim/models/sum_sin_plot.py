'''
Created on 03/12/2009

@author: allan
'''
from scipysim.actors import Channel, Model
from scipysim.actors.display import Plotter
from scipysim.actors.math import Summer
from scipysim.actors.math.trig import CTSinGenerator

import numpy

import logging
logging.basicConfig( level=logging.INFO )
logging.info( "Logger enabled" )

class SumSinPlot( Model ):
    """
    Summing two continous sinusoidal sources together and plotting. 
    """
    def __init__( self ):
        '''Setup the simulation'''
        super( SumSinPlot, self ).__init__()
        connection1 = Channel( domain="CT" )
        connection2 = Channel( domain="CT" )
        connection3 = Channel()

        # 2 Hz, 90 degree phase
        src1 = CTSinGenerator( connection1, 2, 2.0, numpy.pi / 2 )
        # 4 Hz, 45 degree phase
        src2 = CTSinGenerator( connection2, 1, 3.5, numpy.pi / 4 )

        summer = Summer( [connection1, connection2], connection3 )
        dst = Plotter( connection3, refresh_rate=1.0 / 2 )

        self.components = [src1, src2, summer, dst]

if __name__ == '__main__':
    SumSinPlot().run()
