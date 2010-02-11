'''
Created on Feb 7, 2010

brianthorne


'''
from scipysim.actors import Channel, Model

from scipysim.actors.signal import Ramp
from scipysim.actors.display import Plotter


class  ControlStep(Model):
    '''This simulation...'''
    def __init__(self):
        '''Create the components'''
        super(ControlStep, self).__init__()
        connection = Channel()
        
        src = Ramp(connection)
        dst = Plotter(connection)
        
        self.components = [src, dst]

if __name__ == '__main__':
    ControlStep().run()