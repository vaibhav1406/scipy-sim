'''
Created on 8/03/2010

@author: Brian Thorne
'''

from scipysim.actors import Actor, Channel, Siso

class CTIntegrator(Siso):
    '''
    Abstract base class for continuous-time integrator blocks.
   '''

    input_domains = ("CT",)
    output_domains = ("CT",)

    def __init__(self, input_channel, output_channel, init=0.0, init_time=0.0):
        '''
        Constructor for the discrete-time integrator actor. 
        '''
        super(CTIntegrator, self).__init__(input_channel=input_channel,
                                           output_channel=output_channel)

        self.y_old = init  # y[n-1] : the last output
        self.y = init      # y[n] : the output
        self.t_old = init_time

    def siso_process(self, event):
        event = self.integrate(event)
        return event

    def integrate(self, event):
        '''This method must be overridden. It implements the integration algorithm
        based on the current and previous events.
        
        @return an event
        '''
        raise NotImplementedError

class CTIntegratorForwardEuler(CTIntegrator):

    def integrate(self, event):
        ''' y[n] = y[n-1] + x[n]*(t[n]-t[n-1])'''
        self.y = self.y_old
        self.y_old += event['value'] * (event['tag'] - self.t_old)

        self.t_old = event['tag']

        # Generate output event
        out_event = {'tag':event['tag'], 'value':self.y_old}
        return out_event


import unittest
class CTIntegratorTests(unittest.TestCase):
    '''Test the integrator actors'''

    def setUp(self):
        '''
        Unit test setup code
        '''
        self.q_in = Channel()
        self.q_out = Channel()

    def test_forward_euler(self):
        '''Test forward Euler integration of a simple positive integer signal.
        '''
        inp = [{'value':i, 'tag':i} for i in xrange(0, 10, 1)]

        expected_output_values = [sum(range(i)) for i in xrange(1, 11)]

        block = CTIntegratorForwardEuler(self.q_in, self.q_out)

        block.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(None)
        block.join()

        for expected_output in expected_output_values:
            out = self.q_out.get()
            self.assertEquals(out['value'], expected_output)
        self.assertEquals(self.q_out.get(), None)

    def test_different_rate(self):
        '''Test that integration of a simple positive constant signal doesn't change with samplerate.
        '''
        from scipy import arange
        inp_1 = [{'value':10, 'tag':i} for i in arange(0, 10, 1)]
        inp_2 = [{'value':10, 'tag':i} for i in arange(0, 10, 0.1)]

        expected_output_values_1 = [10 * i for i in arange(0, 10, 1)]
        expected_output_values_2 = [10 * i for i in arange(0, 10, 0.1)]

        for Block in [CTIntegratorForwardEuler]:
            q_in1, q_out1, q_in2, q_out2 = Channel(), Channel(), Channel(), Channel()
            block1 = Block(q_in1, q_out1)
            block2 = Block(q_in2, q_out2)

            block1.start(); block2.start()
            [q_in1.put(val) for val in inp_1]
            [q_in2.put(val) for val in inp_2]
            q_in1.put(None); q_in2.put(None)
            block1.join(); block2.join()

            out = []
            for expected_output in expected_output_values_1:
                out.append(q_out1.get())

            out = [item['value'] for item in out]
            self.assertEquals(len(out), len(expected_output_values_1))

            #[self.assertEquals(out[i], expected_output[i]) for i, _ in enumerate(expected_output_values_1)]
            self.assertEquals(q_out1.get(), None)

            for expected_output in expected_output_values_2:
                out = q_out2.get()
                self.assertAlmostEquals(out['value'], expected_output)
            self.assertEquals(q_out2.get(), None)

if __name__ == '__main__':
    unittest.main()
    
