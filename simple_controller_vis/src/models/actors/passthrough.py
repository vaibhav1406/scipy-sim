'''
This actor makes an "IF" like structure.
The first input is a boolean tagged signal, at the tags where it is true
the other channel's data gets passed on, otherwise discarded.

Created on 13/12/2009

@author: Brian
'''
import logging
#logging.basicConfig(level=logging.DEBUG)

from Actor import Actor, Channel
import unittest


class PassThrough(Actor):
    '''
    This actor takes a boolean tagged signal and a data channel.
    At the tag points where the boolean signal is True, the values from the input are
    passed on to the output, a second data channel can be added as an else clause.

    @note: For now this has to be used with discrete signals, or at least aligned continuous signals.
    '''

    def __init__(self, bool_input, data_input, output_queue, else_data_input=None):
        """
        Constructor for a PassThrough block

        @param bool_input: A boolean tagged signal.
        
        @param data_input: The data to be passed through if control was True.
        
        @param else_input: Optional alternative data to be passed on.

        @param output_queue: A single queue where the output will be put.
        """
        super(PassThrough, self).__init__(output_queue=output_queue)
        self.bool_input = bool_input
        self.data_input = data_input
        self.has_else_clause = else_data_input is not None
        if self.has_else_clause:
            self.else_data_input = else_data_input
        
        logging.info("We have set up a pass through actor")

    def process(self):
        """Wait for data from both input queues"""
        logging.debug("Running pass-through, blocking on both queues")

        # this is blocking on each queue in sequence
        bool_in = self.bool_input.get(True)
        logging.debug("Got a boolean value, waiting for data point")
        data_in = self.data_input.get(True)
        
        if self.has_else_clause:
            else_data_in = self.else_data_input.get(True)
            
        # We are finished iff all the input objects are None
        if bool_in is None and data_in is None:
            logging.info("We have finished PassingThrough the data")
            self.stop = True
            self.output_queue.put(None)
            return
        logging.debug("Received a boolean and a data point. Tags = (%e,%e)" % (bool_in['tag'], data_in['tag']))

        # For now we require the signals are in sync
        assert bool_in['tag'] == data_in['tag']

        if bool_in['value'] is True:
            logging.debug("The input was positive, passing data through")
            self.output_queue.put(data_in)
        else:
            if self.has_else_clause:
                self.output_queue.put(else_data_in)
            else:
                logging.debug("Discarding data.")
                
            

class PassThroughTests(unittest.TestCase):
    '''Test the IF actor'''
    def setUp(self):
        '''General set up that will be used in all tests'''
        self.data_in = Channel()
        self.bool_in = Channel()
        self.output = Channel()
        
        # Some fake boolean data
        self.every_second_point = [True, False] * 50
        self.no_points = [False] * 100
        
        # some fake pass through data, and add it to the queue
        self.data = range(100)
        [self.data_in.put({'tag':i, 'value':i}) for i in range(100)]
        self.data_in.put(None)
        
        # create the block
        self.block = PassThrough(self.bool_in, self.data_in, self.output)
        
    def test_all_points(self):
        '''Test that it passes through every point when given True control signal'''
        every_point = [True] * 100
        [self.bool_in.put({'tag':i, 'value':every_point[i]}) for i in self.data]
        self.bool_in.put(None)
        self.block.start()
        self.block.join()
        [self.assertEquals(self.output.get()['tag'], i) for i in self.data]
        self.assertEquals(None, self.output.get())
    
    def test_every_second_point(self):
        '''Test every second point is passed through
        and that the rest is discarded
        '''
        [self.bool_in.put(
                          {'tag':i, 'value':self.every_second_point[i]}
                         ) for i in self.data]
        self.bool_in.put(None)
        self.block.start()
        self.block.join()
        [self.assertEquals(self.output.get()['tag'], 
                           i) for i in self.data if i % 2 == 0]
        self.assertEquals(None, self.output.get())
        

    def test_no_points(self):
        '''Test that no points get passed through for an all False signal'''
        [self.bool_in.put(
                          {'tag':i, 
                           'value':self.no_points[i]
                           } ) for i in self.data]
        self.bool_in.put(None)
        self.block.start()
        self.block.join()
        self.assertEquals(None, self.output.get())

class ElsePassThroughTests(unittest.TestCase):
    '''Test the IF-Else actor'''
    def setUp(self):
        '''General set up that will be used in all tests'''
        self.data_in = Channel()
        self.alt_data_in = Channel()
        self.bool_in = Channel()
        self.output = Channel()
        
        # Some fake boolean data
        self.every_second_point = [True, False] * 50
        
        # some fake pass through data, and add it to the queue
        self.data = range(100)
        self.data_alt = 10*self.data
        [self.alt_data_in.put(
                              {'tag':i, 'value':self.data_alt[i]}
                              ) for i in range(100)]
        [self.data_in.put({'tag':i, 'value':i}) for i in range(100)]
        self.data_in.put(None)
        self.alt_data_in.put(None)
        
        # create the block
        self.block = PassThrough(self.bool_in, 
                                 self.data_in, 
                                 self.output, 
                                 else_data_input=self.alt_data_in)
        
    def test_every_second_alternative(self):
        '''Test merging with if - else actor.
        half the values come from one queue, and half from the other'''
        [self.bool_in.put(
                          {'tag':i, 'value':self.every_second_point[i]}
                         ) for i in self.data]
        self.bool_in.put(None)
        self.block.start()
        self.block.join()
        for i in self.data:
            output = self.output.get(True)
            self.assertEquals(output['tag'], i)
            if i % 2 == 0:
                self.assertEquals(output['value'], i)
            else:
                self.assertEquals(output['value'], self.data_alt[i])
        self.assertEquals(None, self.output.get())
        
                
if __name__ == "__main__":
    unittest.main()
    #suite = unittest.TestLoader().loadTestsFromTestCase(PassThroughTests)
    #unittest.TextTestRunner(verbosity=4).run(suite)

