'''
Created on 13/12/2009

@author: brian
'''
from scipysim.actors import MakeChans, Model
from scipysim.actors.display import Plotter
from scipysim.actors.signal import Ramp, Copier
from scipysim.actors.logic import GreaterThan, PassThrough
from scipysim.actors.math.trig import CTSinGenerator
from scipysim.actors.math import Subtractor, Summer, Constant


import logging
logging.basicConfig( level=logging.INFO )
logging.info( "Logger enabled" )

class Pulse_Width_Modulator( Model ):
    """A PWM generation simulation.
    
    This example connects 3 sources ( 2 ramps and a random) to a summer block
    The final output AND one of the ramps are dynamically plotted.
    
    The components are all generating the same sequence of tags so are always
    synchronised.
    """

    def __init__( self, simulation_length=0.02, simulation_resolution=10000 ):
        self.sim_time = simulation_length
        self.sim_res = simulation_resolution

        wire_names = ( 'ramp',
                      'sin',
                      'const_offset',
                      'offset_sin',
                      'ramp_probe',
                      'ramp_plot',
                      'offset_sin_probe',
                      'sin_plot',
                      'diff',
                      'pwm_bool',
                      'on_value',
                      'off_value',
                      'pwm_value'
                      )
        raw_wires = MakeChans( len( wire_names ) )

        wires = dict( zip( wire_names, raw_wires ) )

        ramp_src = Ramp( wires['ramp_probe'], freq=500, simulation_time=self.sim_time, resolution=self.sim_res )
        sin_src = CTSinGenerator( wires['sin'], amplitude=0.5, freq=50.0, phi=0.0, timestep=1.0 / self.sim_res, simulation_time=self.sim_time )
        const_src = Constant( wires['const_offset'], 0.5, resolution=self.sim_res, simulation_time=self.sim_time )

        offset_sin_sum = Summer( [wires['sin'], wires['const_offset'] ], wires['offset_sin_probe'] )

        ramp_cloning_probe = Copier( wires['ramp_probe'], [wires['ramp'], wires['ramp_plot']] )
        ramp_plotter = Plotter( wires['ramp_plot'] )

        sin_cloning_probe = Copier( wires['offset_sin_probe'], [wires['offset_sin'], wires['sin_plot']] )
        sin_plotter = Plotter( wires['sin_plot'] )

        # Output = sin - ramp
        subtractor = Subtractor( wires['offset_sin'], wires['ramp'], wires['diff'] )

        # Want to see when that is > 0
        comparison = GreaterThan( wires['diff'], wires['pwm_bool'], threshold=0.0, boolean_output=True )
        if_device = PassThrough( wires['pwm_bool'], wires['on_value'], wires['pwm_value'], else_data_input=wires['off_value'] )
        output_value_on = Constant( wires['on_value'], 1.0, resolution=self.sim_res, simulation_time=self.sim_time )
        output_value_off = Constant( wires['off_value'], 0.0, resolution=self.sim_res, simulation_time=self.sim_time )

        pwm_plotter = Plotter( wires['pwm_value'], own_fig=True )

        self.components = [ramp_src,
                      sin_src,
                      const_src,
                      offset_sin_sum,
                      ramp_cloning_probe,
                      ramp_plotter,
                      sin_cloning_probe,
                      sin_plotter,
                      subtractor,
                      comparison,
                      if_device,
                      output_value_on,
                      output_value_off,
                      pwm_plotter
                      ]

if __name__ == '__main__':
    sim = Pulse_Width_Modulator()
    sim.run()
