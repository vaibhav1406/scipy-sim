
import logging
from scipysim.actors import Actor, Channel


import unittest
import numpy

class Bundle( Actor ):
    '''
    This buffering/compressing/bundling actor takes a source 
    and waits for a preset number 
    of events (or for the signal to finish) before passing them on in one.
    
    They get passed on as a special condensed packet.
    '''

    def __init__( self, input_queue, output_queue, bundle_size=None ):
        """
        Constructor for a bundle block.

        @param input_queue: The input queue to be bundled

        @param output_queue: The output queue that has been bundled

        @param bundle_size: The max size of an output bundle. Default
        is to buffer the whole signal then output a single bundle.
        """
        super( Bundle, self ).__init__( input_queue=input_queue, output_queue=output_queue )
        self.bundle_size = bundle_size
        self.temp_data = []

    def process( self ):
        """Send packets of events at one time"""
        logging.debug( "Running buffer/bundle process" )
        obj = self.input_queue.get( True )     # this is blocking
        if obj is not None:
            self.temp_data.append( obj )
        if obj is None or self.bundle_size is not None and len( self.temp_data ) >= self.bundle_size:
            self.send_bundle()

            if obj is None:
                self.output_queue.put( None )
                self.stop = True
            else:
                self.temp_data = []

    def send_bundle( self ):
        '''Create a numpy data type that can carry all the i
        nformation then add it to the output queue'''
        x = numpy.zeros( len( self.temp_data ),
                            dtype=
                            {
                                'names': ["Tag", "Value"],
                                'formats': ['f8', 'f8'],
                                'titles': ['Domain', 'Name']    # This might not get used...
                             }
                        )
        x[:] = [ ( element['tag'], element['value'] ) for element in self.temp_data if element is not None]
        self.output_queue.put( x )


