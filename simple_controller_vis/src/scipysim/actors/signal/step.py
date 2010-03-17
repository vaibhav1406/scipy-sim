'''
Created on Feb 7, 2010

brianthorne


'''

import logging
from numpy import linspace
from scipysim.actors import Source, Channel, Model


class Step(Source):
    '''This models a Heavyside step function'''

    def __init__(self, out, switch_time=0, resolution=10, simulation_time=120, endpoint=False):
        '''Create a step actor.
        
        Optional Parameters
        switch_time seconds to delay the "0" time where the heavyside steps to positive 1
        '''
        super(Step, self).__init__(output_channel=out, simulation_time=simulation_time)
        self.switch_time = switch_time
        self.resolution = resolution
        self.endpoint = endpoint


    def process(self):
        """Create the numbers..."""
        logging.debug("Running step process")

        tags = linspace(0, self.simulation_time, self.simulation_time * self.resolution, endpoint=self.endpoint)

        for tag in tags:
            value = 0 if (tag < self.switch_time) else 1

            data = {
                    "tag": tag,
                    "value": value
                    }
            self.output_channel.put(data)

            #time.sleep(random.random() * 0.001)     # Adding a delay so we can see the async
        logging.debug("Step process finished adding all data to channel")
        self.stop = True
        self.output_channel.put(None)

from scipysim.actors.display import Stemmer
from scipysim.actors.signal import Decimator
class StepPlot(Model):
    def __init__(self):
        output = Channel()
        reduced_output = Channel()
        step = Step(output, switch_time=15, resolution=100, simulation_time=30)
        reducer = Decimator(output, reduced_output, 100)
        plotter = Stemmer(reduced_output)
        self.components = [step, reducer, plotter]

if __name__ == '__main__':
    block = StepPlot()
    block.run()
