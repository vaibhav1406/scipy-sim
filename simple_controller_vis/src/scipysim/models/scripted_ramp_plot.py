'''
Created on 23/11/2009

@author: brian
'''
from scipysim.actors.signal import Ramp
from scipysim.actors.display import Plotter
from scipysim.actors import Channel, Model

class RampPlot(Model):
    '''This example simulation connects a ramp source to a plotter.'''
    def __init__(self):
        '''Create the components'''
        super(RampPlot, self).__init__()
        connection = Channel()
        src = Ramp(connection)
        dst = Plotter(connection, xlabel='Time (s)', ylabel='Amplitude', title='Ramp Plot')

        self.components = [src, dst]

if __name__ == '__main__':
    RampPlot().run()
