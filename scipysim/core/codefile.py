'''
Created on Jan 18, 2010

@author: brianthorne

TODO: Add GUI support. image, position, input connectors etc...
'''

'''
These should both work:
    from scipysim.actors import sin
or 
    import scipysim.actors.sin

TODO CHECK: If the filename is an absolute path this might not import 
properly because the Actor or Model may inherit from other files?
'''

from os import path
import sys
import inspect
import logging
logging.basicConfig( 
    level=logging.INFO, 
    #filename='scipysim_codefile_log.log' 
    )

from util import interrogate


from event import Event
from siso import Siso
from actor import Actor, Source

class CodeFile(object):
    """
    Wrapper around code defining an *Actor* or *Model*.
    
    CodeFile instances exist for every source module containing Actors
    and keep track of the path to the source as well as the actual class.
    """
    def __init__(self, filepath, name=None):
        """Wraps an Actor found in the Python file at the given path.

        Parses the Actor for the number of inputs, outputs and parameters.
        
        If the name of the Actor is not given this will attempt to use the
        stripped file name.

        Params
        ======

        filepath
            The relative (or absolute) path to the python file containing
            the *Actor* to load.

        name
            The name of the *Actor* class within the given file.

        """
        logging.debug("Trying to load a '%s' Actor from module found at '%s'" % (name, filepath))

        self.filepath = filepath
        assert path.exists(filepath)
        
        the_path, the_file = path.split(filepath)
        self.module_name, ext = path.splitext(the_file)
        assert 'py' in ext
        
        logging.debug("Adding '%s' to the Python Path" % the_path)
        sys.path.insert(0, the_path)
        
        logging.debug('Now trying to execute `import %s` to get the module containing the Class.' % self.module_name)
        module = __import__(self.module_name, level=10)
        logging.debug("'%s' module imported" % module)

        # Dynamically find the class that is not a unittest or part of the core
        # inside "module" - ideally we have been given its name!

        # If the Actor name wasn't given, set it to the name of the module
        self.name = self.module_name.title() if name is None else name
        
        try:
            # Hopefully the module contains a class with the same name as given
            block_class = getattr(module, self.name)
        except AttributeError:
            # If the name was given and an AttributeError was caught the user has
            # given us a bad name.
            if name is not None:
                raise NameError('Class "%s" was not found in module "%s".' % (self.name, self.module_name))
            # otherwise we have to try harder...
            logging.debug("Module was not called the same as the filename")
            block_class = None
        # TODO: Refactor this into a function
        if block_class is None:
            logging.debug(interrogate(module))

            modules = [
                        c for c in dir(module)
                                # filter out functions
                            if (not inspect.isfunction(getattr(module, c)))
                                # make sure its a class
                                and inspect.isclass(getattr(module, c)) 
                                # make sure its callable
                                and callable(getattr(module, c))
                                # make sure it inherits from something in the core
                                and any(issubclass(getattr(module, c), block) for block in [Actor, Siso, Source])
                        ]
            logging.debug("Classes inheriting from Actor: %s" % repr(modules))
            if len(modules) > 1:
                """
                If there is still more than one module chances are SISO, Actor and Models 
                are getting picked up.
                """
                from difflib import get_close_matches
                modules = get_close_matches(self.name, modules, 1, 0.1)
            assert len(modules) > 0
            logging.debug('Modules found that nearly match module name are: %s.' % modules)
            module_name = modules[0]
            block_class = getattr(module, module_name)
            self.name = module_name
        logging.debug("Actor's class is '%s'" % block_class)

        # Find out how many input and output channels the block can take.
        if issubclass(block_class, Siso):
            logging.debug("Inherits from SISO - we know that it has one input and one output")
            self.num_inputs = 1
            self.num_outputs = 1
        elif hasattr(block_class, "num_inputs") and hasattr(block_class, "num_outputs"):
            self.num_inputs = block_class.num_inputs
            self.num_outputs = block_class.num_outputs
        elif issubclass (block_class, Event):
            logging.debug("Skipping Event class")
        else:
            logging.error("Non siso module, and no info on how many inputs/outputs?")
            raise NotImplementedError()

        # Find out the domains for those channels
        assert hasattr(block_class, 'output_domains') and hasattr(block_class, 'input_domains')
        self.output_domains = block_class.output_domains
        self.input_domains = block_class.input_domains

        # Save the class itself in two ways, as .block_class and as .ClassName
        setattr(self, self.name, block_class)
        self.block_class = block_class

    def get_default_parameters(self):
        '''
        Return a dictionary mapping parameter names to default parameters, if
        there is no default parameter, None is used.
        '''
        if hasattr(self, 'params'): return self.params
        logging.debug('Loading the parameters and defaults for the %s Actor' % self.name)
        self.arg_spec = inspect.getargspec(self.block_class.__init__)

        
        # Iterate over the args list, e.g.,
        #  ['self','input_channel','refresh_rate','title','own_fig','xlabel','ylabel']
        # adding each argument name to our dictionary. Then iterate in reverse over
        # the defaults tuple to match up the default args with the arg names.
        
        parameters = {}
        for arg_name in self.arg_spec.args:
            if arg_name is not "self":
                parameters[arg_name] = None
        defaults = [None] if self.arg_spec.defaults is None else self.arg_spec.defaults
        for default_param, arg_name in zip(reversed(defaults), reversed(self.arg_spec.args)):
            parameters[arg_name] = default_param

        self.params = parameters
        return parameters

    def get_code(self):
        '''Load an actor or model file.

        TODO: Use inspect.getsource
        '''
        text = "".join(open(self.filepath, 'r').readlines())
        return text

    def __repr__(self):
        '''
        Create a string representation of the code file.
        TODO:
            ----------------------------------------
            |           Block Name                 |
           <| Input name (dt)  |  Output name (ct) |>
           <|     ...          |                   |
            ----------------------------------------
        '''
        return '''<%(name)s - %(inputs)s inputs, %(outputs)s outputs >''' % {
                "name": self.name,
                "inputs": self.num_inputs,
                "outputs": self.num_outputs
            }

