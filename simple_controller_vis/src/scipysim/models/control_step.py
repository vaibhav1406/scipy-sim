'''
Created on Feb 7, 2010

brianthorne


'''


from scipysim.actors import Channel, Model, MakeChans

from scipysim.actors.math import Constant
from scipysim.actors.signal import Step
from scipysim.actors.display import Plotter

import scipy
import scipy.signal

class ControlStep(Model):
    '''This simulation is a P controller responding to a step input.'''
    def __init__(self):
        '''Create the components'''
        super(ControlStep, self).__init__()

        # Simulation time in seconds
        T = 120
        freq = 50
        dt = 1.0 / freq

        p = 4.0 * 2 * scipy.pi

        # Defines the system transfer function (Numerator, Denominator)
        sys = scipy.signal.lti(p, [1, p])

        # Simulate the output of the system based on input u and time t
        yo = scipy.signal.lsim(sys, u, t)


        wires = MakeChans(5)

        # Create a time vector
        src = Constant(wires[0], value=0, resolution=freq, simulation_time=T)

        # Create the signal source
        signal = Step(wires[1], switch_time=60, resolution=50, simulation_time=120)

        dst = Plotter(wires[0])
        dst2 = Plotter(wires[1])

        self.components = [src, dst, dst2, signal]

if __name__ == '__main__':
    ControlStep().run()
