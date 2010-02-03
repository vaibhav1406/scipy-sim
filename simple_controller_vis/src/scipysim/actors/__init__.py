"""Scipy Simulator API.

From this module there are several submodules containing groups 
of actors.
"""
# First we import the bits that every block will probably need
from Actor import Channel, Actor, MakeChans, Source, DisplayActor
from model import Model
from siso import Siso, TestSisoActor, TestCTSisoActor

"""
# Then we import the base actors
from compare import GreaterThan, LessThan, Compare
from copier import Copier
from constant import Constant
#from ctsin import CTSin # depreciated
from decimator import Decimator
from delay import Delay
from derivative import Derivative
#from dtsin import DTSin
from interpolate import Interpolator
from passthrough import PassThrough
from proportional import Proportional
from ramp import Ramp
from random_signal import RandomSource
from sampler import Sampler
from sin import Sin
from subtract import Subtractor
from summer import Summer

from display import Plotter
from display import Stemmer
"""

# Then we can import submodules
import display
import io
import logic
import math
import signal
import string

# Then we would import any compisite blocks
# But they are now in their own module


# This requires pygame... just for kicks
#from VideoSnapshot import VideoSnapshot
