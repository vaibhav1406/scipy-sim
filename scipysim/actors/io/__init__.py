'''IO module for scipysim.

The Bundle and Unbundle actors buffer a channel into a numpy record for saving/sending in a 
memory efficient form.

The Reader and Writer actors read and write data channels into a file.
'''
from bundle import Bundle
from unbundle import Unbundle
from reader import Reader, TextReader
from writer import Writer
