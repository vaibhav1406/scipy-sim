from scipysim.actors import Channel, CompositeActor
from scipysim.actors.display import StemPlotter
from scipysim.actors.math.trig import DTSinGenerator

class DT_Sin_Plot( CompositeActor ):
    '''
    This simulation is made up of a composite model containing a sin generator
    and a standard plotting actor.
    '''

    def __init__( self ):
        super( DT_Sin_Plot, self ).__init__()

        chan1 = Channel( "DT" )
        src = DTSinGenerator( chan1 )
        pltr = StemPlotter( chan1 )

        self.components = [src, pltr]


if __name__ == "__main__":
    DT_Sin_Plot().run()
