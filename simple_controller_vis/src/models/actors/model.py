import logging

from Actor import Actor, DisplayActor

class Model(Actor):
    '''
    A Model is a full citizen actor, it has its own thread of 
    control, it takes parameters and can have input and output 
    channels. 
    A model can define a custom run function which starts and runs the simulation.
    Or a model can set up the model in __init__ and have all the actors in self.components
    then the default run function of a Model will run the simulation.
    '''


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
        function. 
        '''
        assert hasattr(self, 'components')
        
        logging.info("Starting simulation")
        [component.start() for component in self.components]
        logging.debug("Finished starting actors")
    
        if any(issubclass(a.__class__, DisplayActor) for a in self.components):
            import matplotlib.pyplot as plt
            logging.info('The program will stay "running" while the plot is open')
            plt.show()   
    
        [component.join() for component in self.components]

        logging.debug("Finished running simulation")
    
