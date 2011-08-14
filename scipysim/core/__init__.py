'''
Scipy Simulator Core
'''

from actor import Actor, Source, DisplayActor
from channel import Channel, MakeChans, MakeNamedChans
from errors import InvalidSimulationInput, NoProcessFunctionDefined
from event import Event, LastEvent
from composite_actor import CompositeActor
from siso import Siso, SisoCTTestHelper, SisoTestHelper


from parser import fill_tree
from codefile import CodeFile