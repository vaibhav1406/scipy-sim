from models.actors import Stemmer, Channel, Model
from models.composite_actors import DTSinGenerator


class DT_Sin_Plot(Model):
    '''
    This simulation is made up of a composite model containing a sin generator
    and a standard plotting actor.
    '''
    
    def __init__(self):
        super(DT_Sin_Plot, self).__init__()
        
        chan1 = Channel("DT")
        src = DTSinGenerator(chan1)
        pltr = Stemmer(chan1)

        self.components = [src, pltr]
        
        
if __name__ == "__main__":
    DT_Sin_Plot().run()
