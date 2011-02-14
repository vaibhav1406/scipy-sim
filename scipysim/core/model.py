from time import sleep

from actor import Actor
from actor import DisplayActor
import logging

class Model(Actor):
    '''
    A Model is a full citizen actor, it has its own thread of 
    control, it takes parameters and can have input and output 
    channels. 
    A model can define a custom run function which starts and runs the simulation.
    Or a model can set up the model in __init__ and have all the actors in self.components
    then the default run function of a Model will run the simulation.
    '''

    components = []

    def __init__(self, *args, **kwargs):
        '''
        Abstract Constructor for a Model 
        '''
        super(Model, self).__init__(*args, **kwargs)
        logging.debug("Constructed a generic 'model'")

    def process(self):
        '''
        The Actor's process function is not required for a model as
        we create our own run.
        
        @see Actor class.
        '''
        pass

    def run(self):
        '''The run function starts the model or simulation usually by calling the process
        function. It counts as the "main" thread for a running simulation.
        '''
        assert hasattr(self, 'components')

        try:
            logging.info("Starting simulation")
            [component.start() for component in self.components]
            logging.debug("Finished starting actors")

            # Wait for threads to finish
            # Required for KeyboardInterrupt to be handled reliably
            # See: http://luke.maurits.id.au/blog/2008/03/threads-and-signals-in-python/
            while True:
                if not any([component.is_alive() for component in self.components]):
                    # All threads have stopped
                    break
                else:
                    # Some threads are still going
                    sleep(1)

            logging.debug("Finished running simulation")
        except KeyboardInterrupt:
            [component.terminate() for component in self.components]
            [component.join() for component in self.components]



