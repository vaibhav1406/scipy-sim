from scipysim.actors import Channel, Plotter, Ramp, Summer, Copier, RandomSource, Model

from scipysim.actors.buffer import Bundle
from scipysim.actors.display.bundlePlotter import BundlePlotter

class MultiSumPlot(Model):
    '''
    This example connects 3 sources ( 2 ramps and a random) to a summer block
    The final output AND one of the ramps are dynamically plotted.
    
    The components are all generating the same sequence of tags so are always
    synchronised
    '''
        
    def __init__(self):
        '''Set up the simulation'''
        super(MultiSumPlot, self).__init__()
        connection1 = Channel()
        connection1_1 = Channel()
        connection1_2 = Channel()
        connection2 = Channel()
        connection3 = Channel()
        connection4 = Channel()
        connection5 = Channel()
    
        src1 = Ramp(connection1, freq=1.0 / 120)
        src2 = Ramp(connection2)
        src3 = RandomSource(connection3)
        
        cloning_probe = Copier(connection1, [connection1_1, connection1_2])
        progress_plotter = Plotter(connection1_2)
        
        summer = Summer([connection1_1, connection2, connection3], connection4)
        
        bundler = Bundle(connection4, connection5)
        dst = BundlePlotter(connection5)
    
        self.components = [src1, src2, src3, summer, dst, cloning_probe, progress_plotter, bundler]

if __name__ == '__main__':
    MultiSumPlot().run()
