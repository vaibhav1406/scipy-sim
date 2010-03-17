===============
Scipy Simulator
===============

Scipy Simulator provides a concurrent way of modelling systems in Python using
scipy. You might find it most useful for tasks involving <embedded systems> and
<signal processing>. A model can be created in pure Python code - see all the 
examples in the models directory. Typical usage often looks like this::

    #!/usr/bin/env python

    from scipysim.actors.signal import Ramp
    from scipysim.actors.display import Plotter
    from scipysim.actors import Channel, Model

    class RampPlot( Model ):
        def __init__( self ):
	        super( RampPlot, self ).__init__()
	        connection = Channel()
	        src = Ramp( connection )
	        dst = Plotter( connection )
    	    self.components = [src, dst]

    RampPlot().run()


Paragraphs are separated by blank lines. *Italics*, **bold**,
and ``monospace`` look like this.


Contributors
============

This project has been started by the Electrical Engineering Department of Canterbury University by:

* Brian Thorne

* Allan McInnes


Project Site
============
The main development occurs on Google Code at http://scipy-sim.googlecode.com
