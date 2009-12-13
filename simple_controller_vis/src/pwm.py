'''
Created on 13/12/2009

@author: brian
'''


from models.actors import Plotter, Ramp, Summer, Copier, Sin, GreaterThan, Subtractor, Constant
from models import CTSinGenerator
import matplotlib.pyplot as plt
from models.actors.Actor import MakeChans

import logging
logging.basicConfig(level=logging.INFO)
logging.info("Logger enabled")


def run_multi_sum():
    '''
    This example connects 3 sources ( 2 ramps and a random) to a summer block
    The final output AND one of the ramps are dynamically plotted.
    
    The components are all generating the same sequence of tags so are always
    synchronised
    '''
    sim_time = 0.02
    sim_res = 1.0/0.001
    
    wire_names = ('ramp',
                  'sin',
                  'const_offset',
                  'offset_sin',
                  'ramp_probe',
                  'ramp_plot',
                  'offset_sin_probe',
                  'sin_plot',
                  'diff',
                  'pwm'
                  )
    raw_wires = MakeChans(len(wire_names))
    
    wires = dict(zip( wire_names, raw_wires ))
    
    ramp_src = Ramp(wires['ramp_probe'], freq=500, simulation_time=sim_time, resolution=sim_res)
    sin_src = CTSinGenerator(wires['sin'], amplitude=0.5, freq=50.0, phi=0.0, timestep=1.0/sim_res, simulation_time=sim_time)
    const_src = Constant(wires['const_offset'], 0.5, resolution=sim_res, simulation_time=sim_time)
    
    offset_sin_sum = Summer([wires['sin'], wires['const_offset'] ], wires['offset_sin_probe'])
    
    ramp_cloning_probe = Copier(wires['ramp_probe'], [wires['ramp'], wires['ramp_plot']])
    ramp_plotter = Plotter(wires['ramp_plot'])
    
    sin_cloning_probe = Copier(wires['offset_sin_probe'], [wires['offset_sin'], wires['sin_plot']])
    sin_plotter = Plotter(wires['sin_plot'])

    # Output = sin - ramp
    subtractor = Subtractor(wires['offset_sin'], wires['ramp'], wires['diff'])

    # Want to see when that is > 0
    comparison = GreaterThan(wires['diff'], wires['pwm'], threshold=0.0, boolean_output=True)
    
    pwm_plotter = Plotter(wires['pwm'])
    
    components = [ramp_src, 
                  sin_src,
                  const_src,
                  offset_sin_sum,
                  ramp_cloning_probe, 
                  ramp_plotter, 
                  sin_cloning_probe, 
                  sin_plotter, 
                  subtractor,
                  comparison,
                  pwm_plotter]

    logging.info("Starting simulation")
    [component.start() for component in components]
        
    logging.debug("Finished starting actors")

    logging.info('The program will stay "running" while the plot is open')
    plt.show()   

    [component.join() for component in components]
        

    logging.debug("Finished running simulation")

if __name__ == '__main__':
    run_multi_sum()
