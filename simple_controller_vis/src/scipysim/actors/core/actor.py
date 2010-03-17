'''
Created on 19/11/2009

@author: brian
'''

from channel import Channel
import threading
import logging

from errors import NoProcessFunctionDefined

class Actor(threading.Thread):
    '''
    This is a base Actor class for use in a simulation.
    All blocks should inherit from this, including composite models.
    The class inherits from Thread which enables all the blocks to run concurrently.
    
    Attributes that are used in the GUI for connecting components include the
    domain and number of an Actors inputs and outputs. As a convention 
    None means any number or any domain events are allowed.
    
    Class Attributes:
    
    num_inputs - Either None or a integer number of how many channels the block takes.
    num_outputs - Same but for output of a block.
    output_domains - a tuple or list exactly num_outputs long containing information 
                     about the domain of the output - None, DE, DT or CT, BIN
    input_domains - Same for inputs.
    
    '''
    num_inputs = None
    num_outputs = None
    output_domains = (None,)
    input_domains = (None,)

    def __init__(self, input_channel=None, output_channel=None, *args, **kwargs):
        '''Constructor for a generic base actor.
        
        @param input_channel: If an input queue is not passed in, one will be created.
                            This enables scipysim to stop the thread by passing it a
                            message.
        
        @param output_channel: Optional channel for output from this actor to be put into.
        
        Any other named parameters will be passed on to the Thread constructor.
        '''
        super(Actor, self).__init__()

        # Every actor will have at least an input thread - even if its just a control
        if input_channel is None:
            input_channel = Channel()
        self.input_channel = input_channel

        # A sink doesn't require an output queue so this could be None
        self.output_channel = output_channel

        self.stop = False
        self.setDaemon(True)


    def run(self):
        '''
        Run this actors objects thread
        '''
        logging.debug("Started running an actor thread")
        while not self.stop:
            self.process()

    def process(self):
        '''
        The process function is called as often as possible by the threading 
        or multitasking library. No guarantees are made about timing, or that
        anything will have changed for the input queue(s)
        '''
        raise NoProcessFunctionDefined()

class DisplayActor(Actor):
    '''A display actor is a sink. It also draws to the screen'''
    num_inputs = 1
    num_outputs = 0

class Source(Actor):
    '''
    A Source is an abstract interface for some signal source.
    
    @requires: an output channel.
    '''
    num_inputs = 0
    num_outputs = 1

    def __init__(self, output_channel, simulation_time=None):
        super(Source, self).__init__(output_channel=output_channel)
        self.simulation_time = simulation_time

    def process(self):
        '''
        This abstract method gets called in a loop until the actor sets its "stop" variable to true
        '''
        raise NoProcessFunctionDefined()
