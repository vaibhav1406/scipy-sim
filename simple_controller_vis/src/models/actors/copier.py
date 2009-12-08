import logging

from Actor import Actor

import Queue as queue

class Copier(Actor):
    '''
    This actor takes a source and copies it to a number of outputs.
    '''

    def __init__(self, input_queue, outputs):
        """
        Constructor for a Copier Actor.
        
        @param input_queue: The input data queue to be copied
        
        @param outputs: A list of queues to copy the data to.
        """
        super(Copier, self).__init__(input_queue=input_queue)
        self.output_queues = outputs


    def process(self):
        """Just copy the input data to all the outputs..."""
        logging.debug("Running copier process")

        obj = self.input_queue.get(True)     # this is blocking
        if obj is None:
            logging.info("We have finished copying the data")
            self.stop = True
            [q.put(None) for q in self.output_queues]
            return

        [q.put(obj) for q in self.output_queues]
        obj = None

import unittest
class CopierTests(unittest.TestCase):
    '''Test the Copier Actor'''
    def test_basic_copy(self):
        '''Test getting two for the price of one - cloning a queue'''
        q_in = queue.Queue()
        q_out1 = queue.Queue()
        q_out2 = queue.Queue()

        inp = {'value':15, 'tag':1}

        cloneQ = Copier(q_in, [q_out1,q_out2])
        cloneQ.start()
        q_in.put(inp)
        q_in.put(None)
        cloneQ.join()

        out1 = q_out1.get()
        self.assertEquals(out1['value'], inp['value'])
        self.assertEquals(out1['tag'], inp['tag'])
        self.assertEquals(q_out1.get(), None)
        
        out2 = q_out2.get()
        self.assertEquals(out2['value'], inp['value'])
        self.assertEquals(out2['tag'], inp['tag'])
        self.assertEquals(q_out2.get(), None)

if __name__ == "__main__":
    unittest.main()
