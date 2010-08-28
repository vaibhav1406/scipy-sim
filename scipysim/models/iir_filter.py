
"""
A simple model that demonstrates discrete-time system simulation using an
IIR filter.

@author: Allan McInnes
"""
from scipysim.actors import Model, MakeChans, Event
from scipysim.actors.signal import Split, Delay
from scipysim.actors.math.trig import DTSinGenerator
from scipysim.actors.math import Summer
from scipysim.actors.math import Proportional as Gain
from scipysim.actors.display import StemPlotter

class IIR(Model):
    '''
    A model of an IIR filter.
    '''

    def __init__(self):

        wires = MakeChans(10, 'DT')

        # Initial condition
        wires[7].put(Event(0,0))

        self.components = [
            # Signal source
            DTSinGenerator(wires[0], simulation_length=200),
            Split(wires[0], [wires[1], wires[2]]),
            StemPlotter(wires[1], title="Original signal", xlabel="n", ylabel="value"),

            # The filter: y[n] = x[n] - 0.5y[n-1]
            Summer([wires[2], wires[7]], wires[3]),
            Split(wires[3], [wires[4], wires[5]]),
            Delay(wires[4], wires[6], wait=1),  
            Gain(wires[6], wires[7], gain = -0.5),

            # Plot
            StemPlotter(wires[5], title="Filtered signal", xlabel="n", ylabel="value"),
        ]


if __name__ == '__main__':
    IIR().run()
