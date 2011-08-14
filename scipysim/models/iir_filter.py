
"""
A simple model that demonstrates discrete-time system simulation using an
IIR filter.

@author: Allan McInnes
"""
from scipysim.actors import CompositeActor, MakeChans, Event
from scipysim.actors.signal import Split, Delay
from scipysim.actors.math.trig import DTSinGenerator
from scipysim.actors.math import Summer
from scipysim.actors.math import Proportional as Gain
from scipysim.actors.display import StemPlotter

class IIR(CompositeActor):
    '''
    A model of an IIR filter.
    '''

    def __init__(self):

        wires = MakeChans(13, 'DT')

        # Initial condition
        wires[9].put(Event(0,0))

        self.components = [
            # Signal source
            DTSinGenerator(wires[0], simulation_length=200),
            DTSinGenerator(wires[1], amplitude = 0.1, freq = 0.45, simulation_length=200),
            Summer(inputs = [wires[0], wires[1]], output_channel = wires[2]),

            Split(wires[2], [wires[3], wires[4]]),
            StemPlotter(wires[3], title="Original signal", refresh_rate=5, xlabel="n", ylabel="value"),

            # The filter: y[n] = x[n] + 0.7x[n-1] + 0.7y[n-1]
            Summer(inputs = [wires[4], wires[10]], output_channel = wires[5]),
            Split(wires[5], [wires[6], wires[7]]),
            Delay(wires[6], wires[8], wait=1),
            Gain(wires[8], wires[9], gain = 0.7),
            Split(wires[9], [wires[10], wires[11]]),

            Summer(inputs = [wires[7], wires[11]], output_channel = wires[12]),

            # Plot
            StemPlotter(wires[12], title="Filtered signal", refresh_rate=5, xlabel="n", ylabel="value"),
        ]


if __name__ == '__main__':
    IIR().run()
