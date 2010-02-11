'''
Created on 19/11/2009

@author: brian
'''

import Queue as queue
import threading
import logging

class InvalidSimulationInput( TypeError ):
    pass

class Channel( queue.Queue ):
    '''
    A Channel is a derived class of the Python Queue, used for communicating between Actors.
    
    A Channel must be created for a specific domain:
        * CT - Continuous Time
        * DT - Discrete Time
        * DE - Discrete Event
        
    @param domain: The two letter domain code as a string
    '''

    def __init__( self, domain="CT" ):
        '''Construct a queue with type information.
        '''
        queue.Queue.__init__( self )
        self.domain = domain

def MakeChans( num ):
    '''Make a list of channels.
    @param num of channels to create
    '''
    return [Channel() for i in xrange( num )]


class Actor( threading.Thread ):
    '''
    This is a base Actor class for use in a simulation.
    All blocks should inherit from this, including composite models.
    The class inherits from Thread which enables all the blocks to run concurrently.
    
    Attributes that are used in the GUI for connecting components include the
    domain and number of an Actors inputs and outputs. As a convention 
    None means any number or any domain is allowed.
    
    Class Atributes:
    
    num_inputs - Either None or a integer number of how many channels the block takes.
    num_outputs - Same but for output of a block.
    output_domains - a tuple or list exactly num_outputs long containing information 
                     about the domain of the output - None, DE, DT or CT
    input_domains - Same for inputs.
    
    '''
    num_inputs = None
    num_outputs = None
    output_domains = ( None, )
    input_domains = ( None, )

    def __init__( self, input_queue=None, output_queue=None, *args, **kwargs ):
        '''Constructor for a generic base actor.
        
        @param input_queue: If an input queue is not passed in, one will be created.
        
        @param output_queue: Optional queue for output to be put into.
        
        Any other named parameters will be passed on to the Thread constructor.
        '''
        super( Actor, self ).__init__()
        logging.debug( "Constructing a new Actor thread" )

        # Every actor will have at least an input thread - even if its just a control
        if input_queue is None:
            input_queue = queue.Queue( 0 )
        self.input_queue = input_queue

        # A sink doesn't require an output queue so this could be None
        self.output_queue = output_queue

        self.stop = False
        self.setDaemon( True )


    def run( self ):
        '''
        Run this actors objects thread
        '''
        logging.debug( "Started running an actor thread" )
        while not self.stop:
            #logging.debug("Some actor is processing now")
            self.process()

    def process( self ):
        '''
        The process function is called as often as possible by the threading 
        or multitasking library. No guarantees are made about timing, or that
        anything will have changed for the input queue(s)
        '''
        raise NotImplementedError()

class DisplayActor( Actor ):
    '''A display actor is a sink. It also draws to the screen'''
    num_inputs = 1
    num_outputs = 0

class Source( Actor ):
    '''
    A Source is an abstract interface for a signal source.
    Requires an output queue.
    '''
    num_inputs = 0
    num_outputs = 1

    def __init__( self, output_queue, simulation_time=None ):
        super( Source, self ).__init__( output_queue=output_queue )
        self.simulation_time = simulation_time

    def process( self ):
        '''
        This abstract method gets called in a loop untill the actor sets its stop variable to true
        '''
        raise NotImplementedError()
