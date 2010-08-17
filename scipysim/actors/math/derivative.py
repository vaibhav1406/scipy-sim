from scipysim.actors import Actor, Channel
import unittest
import numpy as np

class BundleDerivative(Actor):

    num_inputs = 1
    num_outputs = 1

    def process(self):
        obj = self.input_channel.get(True)     # this is blocking
        if obj is None:
            self.stop = True
            self.output_channel.put(None)
            return

        values = obj["Value"][:]
        new_values = np.diff(values)


        x = np.zeros(len(new_values),
                            dtype=
                            {
                                'names': ["Tag", "Value"],
                                'formats': ['f8', 'f8'],
                                'titles': ['Domain', 'Name']    # This might not get used...
                             }
                        )
        x['Tag'] = obj["Tag"][1:]
        x["Value"] = new_values
        self.output_channel.put(x)


from scipysim.actors.io import Bundle
class BundleDerivativeTests(unittest.TestCase):

    def setUp(self):
        '''
        Unit test setup code
        '''
        self.q_in = Channel()
        self.q_out = Channel()
        self.q_out2 = Channel()

    def test_first_order_diff(self):
        '''Test a first order diff'''
        input_values = [0, 1, 2, 3, 3, 3, 3, 1]
        outs = [1, 1, 1, 0, 0, 0, -2]


        self.input = [{'value':input_values[i], 'tag':i} for i in xrange(len(input_values))]

        bundler = Bundle(self.q_in, self.q_out)
        diffblock = BundleDerivative(self.q_out, self.q_out2, threshold=50)

        [self.q_in.put(i) for i in self.input + [None]]
        [block.start() for block in [bundler, diffblock]]

        [block.join() for block in [bundler, diffblock]]
        outputs = self.q_out2.get()
        self.assertNotEqual(outputs, None)

        [self.assertEquals(outs[i], outputs['Value'][i]) for i in xrange(len(outs))]
        self.assertEquals(self.q_out2.get(), None)

if __name__ == "__main__":
    unittest.main()
