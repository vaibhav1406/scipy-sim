
"""
A demonstration of combining continuous-time and discrete-time system
elements in a single simulation.

@author: Allan McInnes
"""
from scipysim.actors import CompositeActor, MakeChans, Event
from scipysim.actors.signal import Split, Delay, Ct2Dt
from scipysim.actors.math.trig import CTSinGenerator
from scipysim.actors.math import Summer
from scipysim.actors.math import Proportional as Gain
from scipysim.actors.display import Plotter, StemPlotter

class DSP(CompositeActor):
    '''
    A model of an IIR filter.
    '''

    def __init__(self):

        ct_wires = MakeChans(5, 'CT')
        dt_wires = MakeChans(11, 'DT')

        # Initial condition
        dt_wires[7].put(Event(0,0))

        self.components = [
            # Continuous-Time signal source
            CTSinGenerator(ct_wires[0]),
            CTSinGenerator(ct_wires[1], amplitude = 0.3, freq = 10),
            Summer(inputs = [ct_wires[0], ct_wires[1]], output_channel = ct_wires[2]),

            Split(ct_wires[2], [ct_wires[3], ct_wires[4]]),
            Plotter(ct_wires[3], title="CT signal", xlabel="t", ylabel="value", refresh_rate=5),

            # Tag-conversion actor
            Ct2Dt(ct_wires[4], dt_wires[0], 30),

            # Discrete-time system
            Split(dt_wires[0], [dt_wires[1], dt_wires[2]]),
            StemPlotter(dt_wires[1], title="Original DT signal", refresh_rate=5, xlabel="n", ylabel="value"),

            # The filter: y[n] = x[n] + 0.7x[n-1] + 0.7y[n-1]
            Summer(inputs = [dt_wires[2], dt_wires[8]], output_channel = dt_wires[3]),
            Split(dt_wires[3], [dt_wires[4], dt_wires[5]]),
            Delay(dt_wires[4], dt_wires[6], wait=1),
            Gain(dt_wires[6], dt_wires[7], gain = 0.7),
            Split(dt_wires[7], [dt_wires[8], dt_wires[9]]),

            Summer(inputs = [dt_wires[5], dt_wires[9]], output_channel = dt_wires[10]),

            # Plot
            StemPlotter(dt_wires[10], title="Filtered DT signal", refresh_rate=5, xlabel="n", ylabel="value"),
        ]


if __name__ == '__main__':
    DSP().run()
