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

from models.actors import Actor

class CodeFile:
    """
    This class wraps an Actor or a model for the GUI.
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
    
        logging.info("%s module imported" % self.name.title())
        
        
        # TODO: we need to dynamically find the class that is not a unittest
        # inside "module"
        try:
            # Hopefully the module contains a class with the same name as the module
            block_class = getattr(module, self.name.title())
        except AttributeError:
            logging.debug("Module was not called the same as the filename")
            logging.debug(interrogate(module))
            modules = [c for c in dir(module) if callable(getattr(module, c)) and issubclass(getattr(module,c), Actor)]
            logging.debug("Got a list of classes that inherit from Actor: %s" % repr(modules))
            if len(modules) > 1:
                modules = [c for c in modules if c.lower() == self.name.lower()]
            block_class = getattr(module, modules[0])
        
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
        '''Return the name of this code file object'''
        return self.name
 
import unittest
class Test_Code_File(unittest.TestCase):
    src_dir = '/Volumes/Share/Dev/scipy-sim/simple_controller_vis/src'
    
    def test_siso_code_file(self):
        '''Test by loading a siso actor from a hardcoded path'''
        logging.info("starting test")
        c = CodeFile(self.src_dir + '/models/actors/sin.py')    
        self.assertEqual(c.num_inputs, 1)
        self.assertEqual(c.num_outputs, 1)
        
    def test_display_actor(self):
        '''Test that a plotter has one channel input'''
        c = CodeFile(self.src_dir + '/models/actors/stemmer.py')
        self.assertEqual(c.num_inputs, 1)
        self.assertEqual(c.num_outputs, 0)

    def test_dynamic_actor(self):
        '''Test the summer block can have multiple inputs'''
        c = CodeFile(self.src_dir + '/models/actors/summer.py')
        self.assertEqual(c.num_outputs, 1)
        self.assertEqual(c.num_inputs, None)
        
    def test_composite_model(self):
        '''Test a composite_actor for num of inputs and output channels'''
        c = CodeFile(self.src_dir + '/models/composite_actors/CTSinGenerator.py')
        self.assertEqual(c.num_outputs, 1)
        self.assertEqual(c.num_inputs, 0)
        
if __name__ == "__main__":
    unittest.main()
    #c = CodeFile(Test_Code_File.src_dir + '/models/composite_actors/CTSinGenerator.py')