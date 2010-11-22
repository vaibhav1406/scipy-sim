'''
Created on Feb 3, 2010

@author: brianthorne
'''
import unittest

from split import SplitTests
from decimator import DecimatorTests
from delay import DelayTests
from interpolator import InterpolateTests
from eventfilter import EventFilterTests
from merge import MergeTests
from quantizer import QuantizerTests
from sampler import SamplerTests
from sink import SinkTests

#from ramp import RampTests # TODO
#from random_signal import RandomSourceTest # Todo


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
