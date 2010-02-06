"""Scipy Simulator API: actors and components

From this module there are several submodules containing groups 
of actors.
"""
# First we import the bits that every block will probably need
from core.actor import Channel, Actor, MakeChans, Source, DisplayActor, InvalidSimulationInput
from core.model import Model
from core.siso import Siso, SisoCTTestHelper, SisoTestHelper

"""
# Then we can import submodules
import display
import io
import logic
import math
import signal
import string
"""
# Then we would import any compisite blocks
# But they are now in their own module


# This requires pygame... just for kicks
#from VideoSnapshot import VideoSnapshot
