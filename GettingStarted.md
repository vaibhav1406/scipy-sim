# Introduction #

Scipysim simulation models are written as python scripts that import and use various actors from the scipysim library. The current distribution of scipysim includes a number of example models in the `scipysim/models` directory. These are probably the best place to start when trying to figure out how to create your own models.

The guts of the scipysim implementation is in the `scipysim/core` and `scipysim/actors` directories. The `core` directory contains some very basic building blocks. The `actors` directory contains implementations of things like signal sources, integrators, summing points, and so on. It's still a fairly minimal collection at this point, but enough to perform some basic simulation tasks. Contributions of additional actors are most welcome!

# Example of a model #

Here's a simple example of a complete scipysim model for a ballistic trajectory.
```
from scipysim.actors import Model, MakeChans
from scipysim.actors.signal import Split
from scipysim.actors.math import Constant
from scipysim.actors.math import CTIntegratorForwardEuler as Integrator
from scipysim.actors.display import Plotter

class ThrownBall(Model):
    def __init__(self):
        wires = MakeChans(10)

        gravity = -9.81
        initial_position = 10 # vertical meters
        initial_velocity = 15 # m/s vertical, up is positive 

        self.components = [
            Constant(wires[0], value=gravity, resolution=100, simulation_time=4),
            Integrator(wires[0], wires[1], initial_velocity),
            Split(wires[1], [wires[2], wires[3]]),
            Plotter(wires[2], title="Velocity", own_fig=True, xlabel="Time (s)", ylabel="(m/s)"),
            Integrator(wires[3], wires[4], initial_position),
            Split(wires[4], [wires[5], wires[6]]),
            Plotter(wires[5], title="Displacement", own_fig=True, xlabel="Time (s)", ylabel="(m)"),
        ]


if __name__ == '__main__':
    ThrownBall().run()
```

The model is derived from the `Model` base class, and imports a bunch of scipysim actors which are used to construct the simulation. The simulation itself is defined by instantiating the actors with appropriate wiring (constructed using `MakeChans`) connecting outputs and inputs. All of the actors are placed into the `components` list of the model. In this case, the model consists of the following actors:
  * a `Constant` signal source that represents gravitational acceleration
  * two `Integrator` actors (simple Forward Euler fixed-step integrators in this case) that transform the acceleration into first a velocity, and then a position.
  * two `Split` actors that act as signal splitters, allowing information to both progagate through the simulation and be passed to `Plotter` actors for display
  * two `Plotter` actors that produce graphs of velocity and position as a function of time

# Running a model #
There is a `run_scipysim` shell script in the scipysim installation base directory. This is probably the easiest way to run a model, since it'll handle setting the path appropriately. With no arguments, the script will bring up a mostly non-functional GUI (you can place actors, but can't connect them). If you provide an argument, then `run_scipysim` will run the model you point it at. For example, typing
```
./run_scipysim scipysim/models/trajectory.py
```
will run the example model described above, and generate plots of velocity and displacement.