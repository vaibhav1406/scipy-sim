'''
Discrete-time integrator

@author: Brian Thorne
@author: Allan McInnes

Created on 9/12/2009
Additional integration algorithms added 08/02/2010
'''
from scipysim.actors import Actor, Channel, Siso

class DTIntegrator(Siso):
    '''
    A discrete-time integrator block.
    
    Implements three different discrete-time integration algorithms:
    
     * Backward Euler (aka Backward Rectangular)
     * Forward Euler (aka Forward Rectangular)
     * Trapezoidal
     
   Note that all three implementations current assume uniform unit intervals between
   input time tags.
   '''
    
    input_domains = ("DT",)
    output_domains = ("DT",)
    
    def __init__(self, input_queue, output_queue, init=0.0, alg='backward_euler'):
        '''
        Constructor for the discrete-time integrator actor. 
        '''
        super(DTIntegrator, self).__init__(input_queue=input_queue,
                                  output_queue=output_queue)
                                  
        self.y_old = init  # y[n-1] : the last output
        self.y = init      # y[n] : the output
        self.x_old = 0.0   # x[n] : the last input
        
        algorithm = { 
            'backward_euler' : self.backward_euler,
            'forward_euler' : self.forward_euler,
            'trapezoidal' : self.trapezoidal,
            }        
        self.integrate = algorithm[alg]

    def siso_process(self, obj):
        obj = self.integrate(obj)
        return obj
        
    def backward_euler(self, obj):
        ''' y[n] = y[n-1] + x[n] '''
        self.y = self.y_old + obj['value']
        self.y_old = self.y        
        obj['value'] = self.y
        return obj  
        
    def forward_euler(self, obj):
        ''' y[n] = y[n-1] + x[n-1] '''
        self.y = self.y_old
        self.y_old += obj['value']    
        obj['value'] = self.y
        return obj          

    def trapezoidal(self, obj):
        ''' y[n] = y[n-1] + 0.5*(x[n] + x[n-1]) '''
        self.y = self.y_old + 0.5*(obj['value'] + self.x_old)
        self.x_old = obj['value']
        self.y_old = self.y    
        obj['value'] = self.y
        return obj    

import unittest
class DTIntegratorTests(unittest.TestCase):
    '''Test the simple integrator actor'''

    def setUp(self):
        '''
        Unit test setup code
        '''
        self.q_in = Channel()
        self.q_out = Channel()

    def test_backward_euler(self):
        '''Test backward Euler integration of a simple positive integer signal.
        '''
        inp = [{'value':i, 'tag':i} for i in xrange(0, 10, 1)]

        expected_output_values = [sum(range(i)) for i in xrange(1,11)]

        block = DTIntegrator(self.q_in, self.q_out, alg='backward_euler')
        block.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(None)
        block.join()

        for expected_output in expected_output_values:
            out = self.q_out.get()
            self.assertEquals(out['value'], expected_output)
        self.assertEquals(self.q_out.get(), None)

    def test_forward_euler(self):
        '''Test forward Euler integration of a simple positive integer signal.
        '''
        inp = [{'value':i, 'tag':i} for i in xrange(0, 10, 1)]

        expected_output_values = [sum(range(i)) for i in xrange(0,10)]

        block = DTIntegrator(self.q_in, self.q_out, alg='forward_euler')
        block.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(None)
        block.join()

        for expected_output in expected_output_values:
            out = self.q_out.get()
            self.assertEquals(out['value'], expected_output)
        self.assertEquals(self.q_out.get(), None)
        
    def test_trapezoidal(self):
        '''Test trapezoidal integration of a simple positive integer signal.
        '''
        inp = [{'value':i, 'tag':i} for i in xrange(0, 10, 1)]
        
        x_avgs = [0.5*(x + (x-1)) for x in xrange(1, 11, 1)]
        expected_output_values = [sum(x_avgs[:i]) for i in range(10)]

        block = DTIntegrator(self.q_in, self.q_out, alg='trapezoidal')
        block.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(None)
        block.join()

        for expected_output in expected_output_values:
            out = self.q_out.get()
            self.assertEquals(out['value'], expected_output)
        self.assertEquals(self.q_out.get(), None)        
        
if __name__ == "__main__":
    unittest.main()
    