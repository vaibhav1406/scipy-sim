'''
A discrete sin stem plotter.

@note This simulation uses the DTSin class, an alternative would be to use the
trig function sin with an appropriate ramp source - now implemented as DTSinGenerator.
@see DTSinStem.py


Created on 04/12/2009

@author: allan, brian
'''
#import scipysim.actors
from scipysim.actors import Channel, Model
from scipysim.actors.display import Stemmer
from scipysim.actors.dtsin import DTSin # has been removed from main actors imports


import logging
logging.basicConfig(level=logging.INFO)
logging.info("Logger enabled")

class DT_Sin_Stem(Model):
    
    def __init__(self):
        connection1 = Channel("DT")
    
        src = DTSin(connection1) 
        dst = Stemmer(connection1)
    
        self.components = [src, dst]


if __name__ == '__main__':
    simulation = DT_Sin_Stem()
    simulation.run()
