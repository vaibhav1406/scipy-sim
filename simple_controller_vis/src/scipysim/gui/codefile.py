'''
Created on Jan 18, 2010

@author: brianthorne
'''

from os import path
import sys
import inspect
import logging
#logging.basicConfig( level=logging.INFO )

from introspection import interrogate
from scipysim.actors import Siso

from scipysim.actors import Actor

class CodeFile:
    """
    This class wraps an Actor or a model for the GUI.
    It contains instructions for drawing, connecting and running a simulation.
    
    """
    def __init__( self, filepath, name=None ):
        """Wrap an Actor for the GUI, parses the number of inputs etc.
        If the name is not given it will be the stripped file name.
        TODO: Add GUI support. image, position, input connectors etc...
        """
        self.filepath = filepath
        assert path.exists( filepath )
        self.name = path.split( filepath )[1].split( '.' )[0] if name is None else name
        self.image = None
        logging.debug( "Loading a %s block from %s" % ( self.name, self.filepath ) )


        logging.debug( "Trying to load the module in Python" )
        """ We can use a import statement like: 
        from scipysim.actors import sin
        or import scipysim.actors.sin
        but not import sin unless sin was in the top directory or on the python path"""

        sys.path.insert( 0, path.split( filepath )[0] )
        module = __import__( self.name )

        logging.debug( "%s module imported" % self.name.title() )


        # TODO: we need to dynamically find the class that is not a unittest
        # inside "module"
        try:
            # Hopefully the module contains a class with the same name as the module
            block_class = getattr( module, self.name.title() )
        except AttributeError:
            # otherwise try harder...
            logging.debug( "Module was not called the same as the filename" )
            logging.debug( interrogate( module ) )

            modules = [c for c in dir( module ) if not inspect.isfunction( getattr( module, c ) ) and inspect.isclass( getattr( module, c ) ) and callable( getattr( module, c ) ) and issubclass( getattr( module, c ), Actor )]
            logging.debug( "Got a list of classes that inherit from Actor: %s" % repr( modules ) )
            if len( modules ) > 1:
                """
                If there is still more than one module chances are SISO, Actor and Models 
                are getting picked up. difflib
                """
                from difflib import get_close_matches
                modules = get_close_matches( self.name, modules, 1, 0.1 )
            assert len( modules ) > 0
            module_name = modules[0]
            block_class = getattr( module, module_name )

        # Find out how many input and output channels the block can take.
        #logging.debug(interrogate(block_class))
        if issubclass( block_class, Siso ):
            logging.debug( "Inherits from SISO - we know that it has one input and one output" )
            self.num_inputs = 1
            self.num_outputs = 1
        elif hasattr( block_class, "num_inputs" ) and hasattr( block_class, "num_outputs" ):
            self.num_inputs = block_class.num_inputs
            self.num_outputs = block_class.num_outputs
        else:
            logging.error( "Non siso module, and no info on how many inputs/outputs?" )
            raise NotImplementedError()

        # Find out the domains for those channels
        assert hasattr( block_class, 'output_domains' ) and hasattr( block_class, 'input_domains' )
        self.output_domains = block_class.output_domains
        self.input_domains = block_class.input_domains

    def get_code( self ):
        """Load an actor or model file."""
        text = "".join( open( self.filepath, 'r' ).readlines() )
        return text

    def __repr__( self ):
        '''Return the name of this code file object'''
        return self.name
        '''return "<%(name)s - %(inputs)d inputs, %(outputs)d outputs >" % {
                "name": self.name,
                "inputs": self.num_inputs,
                "outputs": self.num_outputs
            }'''

