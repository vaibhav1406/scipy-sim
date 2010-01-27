# First we import the bits that every block will probably need
from Actor import Channel, Actor, MakeChans, Source

# Then we import the base actors
from compare import GreaterThan, LessThan, Compare
from copier import Copier
from constant import Constant
#from ctsin import CTSin # depreciated
from decimator import Decimator
from delay import Delay
from derivative import Derivative
#from dtsin import DTSin
from fileIO import WriteDataFile, ReadDataFile
from interpolate import Interpolator
from model import Model
from passthrough import PassThrough
from plotter import Plotter
from proportional import Proportional
from ramp import Ramp
from random_signal import RandomSource
from sampler import Sampler
from sin import Sin
from siso import Siso, TestSisoActor
from stemmer import Stemmer
from subtract import Subtractor
from summer import Summer

# Then we would import any compisite blocks
# But they are now in their own module


# This requires pygame... just for kicks
#from VideoSnapshot import VideoSnapshot
