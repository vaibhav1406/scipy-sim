'''
Created on Feb 5, 2010

@author: brianthorne
'''

from scipysim.actors.io import Bundle
from scipysim.actors import Actor, DisplayActor, Channel
from bundlePlotter import BundlePlotter
import numpy

import unittest
class BundlePlotTests( unittest.TestCase ):
    def setUp( self ):
        self.q_in = Channel()
        self.q_out = Channel()
        self.q_out2 = Channel()
        self.input = [{'value': 1, 'tag': i } for i in xrange( 100 )]

    def tearDown( self ):
        del self.q_in
        del self.q_out

    def test_getting_bundle_data( self ):
        '''Test bundling a signal and getting the data back'''

        block = Bundle( self.q_in, self.q_out )
        block.start()
        [self.q_in.put( i ) for i in self.input + [None]]
        block.join()
        bundled_data = self.q_out.get()
        self.assertEqual( len( bundled_data ), 100 )
        self.assertEqual( type( bundled_data ), numpy.ndarray )
        values = bundled_data["Value"]
        self.assertTrue( all( values == 1 ) )
        tags = bundled_data["Tag"]
        [self.assertEquals( tags[i] , i ) for i in xrange( 100 ) ]

    def test_plotting( self ):
        bundler = Bundle( self.q_in, self.q_out )
        bundlingPlotter = BundlePlotter( self.q_out )
        [block.start() for block in [bundler, bundlingPlotter]]
        [self.q_in.put( i ) for i in self.input + [None]]
        [block.join() for block in [bundler, bundlingPlotter]]

if __name__ == "__main__":
    unittest.main()
