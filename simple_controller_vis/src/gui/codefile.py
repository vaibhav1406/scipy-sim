'''
Created on Jan 18, 2010

@author: brianthorne
'''

from os import path
import sys
import logging
logging.basicConfig(level=logging.DEBUG)
from introspection import interrogate
from models.actors.siso import Siso

class CodeFile:
    """
    This class wraps an Actor ar a model for the GUI.
    It will contain instructions for drawing, connecting and running a simulation.
    """
    def __init__(self, filepath, name=None):
        """If the name is not given it will be the stripped file name.
        TODO: Add GUI support. image, position, input connectors etc...
        """
        self.filepath = filepath
        assert path.exists(filepath)
        self.name = path.split(filepath)[1].split('.')[0] if name is None else name
        self.image = None
        logging.debug("Loading a %s block from %s" % (self.name, self.filepath))
        
        
        logging.debug("Trying to load the module in Python")
        """ We can use a import statement like: 
        from models.actors import sin
        or import models.actors.sin
        but not import sin unless sin was in the top directory or on the python path"""
        
        sys.path.insert(0,path.split(filepath)[0])
        module = __import__(self.name)
        
        #diffway = compile(self.get_code(), self.filepath, 'exec')
        #eval(diffway)    # Returns None, but has executed the file, anything in module is visible
        #logging.debug("Module was imported: \n%s" % interrogate(diffway))    # A code object type :-(
        
        logging.info("%s module imported" % self.name.title())
        logging.debug(interrogate(module))
        # Hopefully the module contains a class with the same name as the module
        block_class = getattr(module, self.name.title())
        logging.debug(interrogate(block_class))
        if issubclass(block_class, Siso):
            logging.info("Inherits from SISO - we know that it has one input and one output")
            self.num_inputs = 1
            self.num_outputs = 1
        elif hasattr(block_class, "num_inputs") and hasattr(block_class, "num_outputs"):
            self.num_inputs = block_class.num_inputs
            self.num_outputs = block_class.num_outputs
        else:
            logging.info("Non siso module, and no info on how many inputs/outputs?")
            raise NotImplementedError()
        
        
    def get_code(self):
        """Load an actor or model file."""
        text = "".join(open(self.filepath, 'r').readlines())
        return text        

    def __repr__(self):
        return self.name
    
def test_code_file():
    logging.info("starting test")
    c = CodeFile('/Volumes/Share/Dev/scipy-sim/simple_controller_vis/src/models/actors/sin.py')    
    
if __name__ == "__main__":
    test_code_file()