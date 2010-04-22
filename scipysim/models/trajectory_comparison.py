"""
A model based on the bouncing ball example in simulink.
This version compares the fixed-step and discrete-event integrators.
"""
from scipysim.actors import Model, MakeChans
from scipysim.actors.signal import Copier
from scipysim.actors.math import Constant
from scipysim.actors.math import CTIntegratorForwardEuler as Integrator
from scipysim.actors.math import CTIntegratorDE1 as DEIntegrator
from scipysim.actors.display import Stemmer

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
            # Split into fixed-step and DE streams
            Copier(wires[0], [wires[1], wires[2]]),
            # Integrate to get velocity
            Integrator(wires[1], wires[3], initial_velocity),
            DEIntegrator(wires[2], wires[4], initial_velocity),
            # Integrate to get displacement
            Integrator(wires[3], wires[5], initial_position),
            DEIntegrator(wires[4], wires[6], initial_position),
            # Plot
            Stemmer(wires[5], title="Displacement (fixed-step integration)", own_fig=True, xlabel="Time (s)", ylabel="(m)"),
            Stemmer(wires[6], title="Displacement (discrete-event integration)", own_fig=True, xlabel="Time (s)", ylabel="(m)"),            
        ]


if __name__ == '__main__':
    ThrownBall().run()
