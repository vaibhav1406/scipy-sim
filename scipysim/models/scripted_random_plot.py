'''
Created on 23/11/2009

@author: brian
'''
from scipysim.actors import Channel, Model
from scipysim.actors.display import Plotter
from scipysim.actors.signal import RandomSource

class RandomPlot( Model ):
    '''
    Run a simple example connecting a random source with a plotter
    '''
    def __init__( self ):
        '''Run the simulation'''
        super( RandomPlot, self ).__init__()
        connection = Channel()
        src = RandomSource( connection )
        dst = Plotter( connection )

        self.components = [src, dst]

if __name__ == '__main__':
    RandomPlot().run()
