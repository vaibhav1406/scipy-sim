import logging
from Actor import Actor

def TestSisoActor(test_case, block, inputs, expected_outputs):
    '''Helper function for testing SISO actors.
    '''
    [block.input_queue.put(val) for val in inputs + [None]]
    block.start()
    block.join()
    for expected_output in expected_outputs:
        out = block.output_queue.get()
        test_case.assertEquals(out['value'], expected_output['value'])
        test_case.assertEquals(out['tag'], expected_output['tag'])
    test_case.assertEquals(block.output_queue.get(), None)

def TestCTSisoActor(test_case, block, inputs, expected_outputs):
    '''Helper function for testing SISO actors. This one uses assertAlmostEqual.
    '''
    [block.input_queue.put(val) for val in inputs + [None]]
    block.start()
    block.join()
    for expected_output in expected_outputs:
        out = block.output_queue.get()
        test_case.assertAlmostEqual(out['value'], expected_output['value'], 6)
        test_case.assertAlmostEqual(out['tag'], expected_output['tag'], 6)
    test_case.assertEquals(block.output_queue.get(), None)

class Siso(Actor):
    '''This is a generic single input, single output actor.
    The constructor requires one input and one output.
    
    @requires: Derivative classes must override the siso_process function
    '''

    def __init__(self, input_queue, output_queue, child_handles_output=False):
        """Generic SISO constructor.
        This default block simply logs the
        data received and outputs it.

        @param input_queue: The input Channel to this actor.
        
        @param output_queue: The output channel.
        
        @param child_handles_output: If the actor wants to deal with its own
        output, make this true - for example if every input doesn't 
        get mapped to an output.
        @see scipysim.actors.Sampler
        """
        super(Siso, self).__init__(input_queue=input_queue, output_queue=output_queue)
        self.child_handles_output = child_handles_output

    def siso_process(self, data):
        '''A single input, single output function.
        
        @param data: The event (tagged signal element)
        
        @return: The output event.
        '''
        raise NotImplementedError("No siso process function found.")

    def process(self):
        """This gets called all the time by the Actor parent.
        It will look at the input queue - if it contains "None"
        the actor is stopped. Otherwise the element is popped off
        the channel and the function "siso_process" is called with 
        the data as a parameter, and the result is put on the output 
        queue.
        """
        logging.debug("Running generic SISO process")
        
        obj = self.input_queue.get(True)     # this is blocking
        if obj is None:
            logging.info('Siso process is finished with the data')
            self.stop = True
            self.output_queue.put(None)
            return
        data = self.siso_process(obj)
        if not self.child_handles_output:
            self.output_queue.put(data)
