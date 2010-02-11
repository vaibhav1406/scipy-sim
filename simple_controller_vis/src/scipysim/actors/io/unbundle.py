'''
Created on Feb 2, 2010

@author: brianthorne
'''

from scipysim.actors import Actor
class Unbundle( Actor ):
    '''Given a bundled source, recreate the queue that made it'''

    def __init__( self, input_queue, output_queue ):
        super( Unbundle, self ).__init__( input_queue=input_queue, output_queue=output_queue )

    def process( self ):
        x = self.input_queue.get( True )
        if x is not None:
            [self.output_queue.put( {"tag": tag, 'value': value} ) for ( tag, value ) in x]
        else:
            self.output_queue.put( None )
            self.stop = True
