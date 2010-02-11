'''
Created on 1/12/2009

@author: brian
'''

from scipysim.actors import Actor
import logging
import unittest

class Interpolator( Actor ):
    pass

    def process( self ):
        raise NotImplementedError



class InterpolateTests( unittest.TestCase ):
    def test_basic_intepolate( self ):
        Interpolator().process()


if __name__ == "__main__":
    unittest.main()
