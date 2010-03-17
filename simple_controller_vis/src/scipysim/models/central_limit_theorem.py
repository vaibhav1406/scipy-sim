from scipysim.actors import Channel, Model, MakeChans
from scipysim.actors.display import Plotter
from scipysim.actors.signal import Ramp, Copier, RandomSource
from scipysim.actors.math import Summer
from scipysim.actors.io import Bundle
from scipysim.actors.display import BundleHistPlotter

import logging
logging.basicConfig(level=logging.INFO)
logging.info("Starting dual ramp + noise sum.")

class MultiSumPlot(Model):
    '''
    This example connects N random sources to a summer block
    The final output is plotted AFTER all the processing is complete.
    
    The components are all generating the same sequence of tags, so are always
    synchronised.
    '''

    def __init__(self, N=5):
        '''Set up the simulation'''
        super(MultiSumPlot, self).__init__()
        wires = MakeChans(N + 2)

        # Create N random source blocks
        rndSources = [RandomSource(wires[i], resolution=15) for i in xrange(N)]

        # Create Summer Block
        summer = Summer(wires[:N], wires[N])
        # Create Bundler Block
        bundler = Bundle(wires[N ], wires[N + 1])

        dst = BundleHistPlotter(wires[N + 1], title="Summing %d Noise sources" % N, show=True)

        self.components = rndSources + [ summer, dst, bundler]

if __name__ == '__main__':
    for i in [1, 2, 3, 6, 12, 20]:
        MultiSumPlot(N=i).run()
