'''
Created on Jan 18, 2010

@author: brianthorne
'''
from os import path

class CodeFile:
    """
    This class wraps an Actor ar a model for the GUI.
    It will contain instructions for drawing, connecting and running
    """
    def __init__(self, filepath, name=None):
        """If the name is not given it will be the stripped file name.
        TODO: Add GUI support. image, position, input connectors etc...
        """
        self.filepath = filepath
        self.name = path.split(filepath)[1] if name is None else name
        self.image = None
        
    def get_code(self):
        """Load an actor or model file."""
        
        text = "".join(open(self.filepath, 'r').readlines())
        return text        
