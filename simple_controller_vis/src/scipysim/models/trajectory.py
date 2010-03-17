"""
A model based on the bouncing ball example in simulink.
"""
from scipysim.actors import Model, MakeChans
from scipysim.actors.signal import Ramp, Copier
from scipysim.actors.math import Summer, Constant
from scipysim.actors.math import CTIntegratorForwardEuler as Integrator
from scipysim.actors.display import Plotter

import logging
logging.basicConfig(level=logging.INFO)
logging.info("Logger enabled")

class ThrownBall(Model):
    '''
    A simple example simulation where ...
    '''

    def __init__(self):
        '''
        A basic simulation that ...
        '''
        wires = MakeChans(10)

        gravity = -9.81
        initial_position = 10 # vertical meters
        initial_velocity = 15 # m/s vertical, up is positive 

        self.components = [
            Constant(wires[0], value=gravity, resolution=100, simulation_time=4),
            Integrator(wires[0], wires[1], initial_position),
            Copier(wires[1], [wires[2], wires[3]]),
            Plotter(wires[2], title="Velocity", xlabel="Time (s)", ylabel="(m/s)"),
            Integrator(wires[3], wires[4], initial_velocity),
            Copier(wires[4], [wires[5], wires[6]]),
            Plotter(wires[5], title="Displacement", own_fig=True, xlabel="Time (s)", ylabel="(m)"),
        ]


if __name__ == '__main__':
    ThrownBall().run()
