'''IO module for scipy-simulator.

Bundle and Unbundle buffer a channel into a numpy record.
Reader and Writer read and write data channels into a file.
'''
from bundle import Bundle
from unbundle import Unbundle
from reader import Reader, TextReader
from writer import Writer
