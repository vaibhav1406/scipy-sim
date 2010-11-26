
"""
A simple model that demonstrates continuous-time system simulation with a
feedback loop and discrete-event integrator.

@author: Allan McInnes
"""
from scipysim.actors import Model, MakeChans, Event
from scipysim.actors.signal import Split
from scipysim.actors.signal import Delay
from scipysim.actors.signal import Step
from scipysim.actors.math import Summer
from scipysim.actors.math import CTIntegratorQS1
from scipysim.actors.math import CTIntegratorForwardEuler as CTIntegrator
from scipysim.actors.display import StemPlotter

class FeedbackIntegral(Model):
    '''
    A model of a simple feedback system.
    '''

    def __init__(self):

        wires = MakeChans(8, 'CT')

        self.components = [
            # Signal source
            Step(wires[0], switch_time = 1, timestep=0.1, simulation_time=25),

            Split(wires[0], [wires[1], wires[2]]),
            StemPlotter(wires[2], title="Input", live=True, xlabel="t", ylabel="value"),

            # The system
            Summer(inputs = [wires[1], (wires[7],'-')], output_channel = wires[3]),
            CTIntegratorQS1(wires[3], wires[4], init=0.0, delta=0.01, maxstep=0.099),
            #CTIntegrator(wires[3], wires[4], init=0.0),
            Split(wires[4], [wires[5], wires[6]]),
            Delay(wires[5], wires[7], wait=0.1),  # for causality

            # Plot
            StemPlotter(wires[6], title="Output", live=True, xlabel="t", ylabel="value"),
        ]

        # Initial condition
        wires[7].put(Event(0.0, 0.0))


if __name__ == '__main__':
    FeedbackIntegral().run()
