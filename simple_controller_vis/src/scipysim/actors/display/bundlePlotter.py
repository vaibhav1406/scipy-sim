'''
This plotting actor creates an output image (png) and optionally opens it.
Since static images don't animate very well it gets all the input at once in a "bundle".

@see multiple_summation_r... for a model which uses both dynamic and static plots.
@see noisy_ramp_plot for a model which uses just this static plot.

@author: brianthorne
'''

from scipysim.actors.io import Bundle
from scipysim.actors import Actor, DisplayActor, Channel

import numpy
import logging

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

class BundlePlotter( Actor ):
    '''
    A plot that is NOT dynamic. It takes a packet or bundle of events
    and plots it all at once.
    '''
    def __init__( self, input_queue, title="Scipy Simulation Output", show=False ):
        '''A bundle plotter takes bundled data in the input queue.
        The individual discrete events must be compressed using the bundler first
        '''
        super( BundlePlotter, self ).__init__( input_queue=input_queue )
        self.title = title
        self.show = show

    def process( self ):
        '''Collect the data in one lot from the queue and create an image'''
        self.data = self.input_queue.get( True )     # this is blocking
        if self.data is None:
            self.stop = True
        else:
            url = self.save_image()
            if self.show:
                import webbrowser
                # I don't know why this is breaking things... but it is...
                webbrowser.open( url )

            logging.info( "Output graph is at '%s'" % url )

    def save_image( self ):
        self.x_axis_data = self.data["Tag"]
        self.y_axis_data = self.data["Value"]
        logging.info( "Creating static plot of %d items" % len( self.data ) )

        f = Figure()    # Could give the figure a size and dpi here
        canvas = FigureCanvas( f )

        a = f.add_subplot( 111 )
        a.plot( self.x_axis_data, self.y_axis_data )
        a.set_title( self.title )
        a.grid( True )

        # This creates a png image in the current directory
        canvas.print_figure( filename=self.title, dpi=150 )
        logging.info( "Saved output png image." )
        import os
        url = "file://" + os.getcwd() + "/" + self.title + ".png"
        logging.info( "Image was saved at %s" % url )
        return url
