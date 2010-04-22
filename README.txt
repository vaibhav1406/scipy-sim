===============
Scipy Simulator
===============

Scipy Simulator provides a **concurrent** way of modelling and simulating 
heterogeneous systems in Python using scipy. You might find it most useful 
for tasks involving *embedded systems* or *signal processing*. 

Scipysim models are created in pure Python code, by instantiating various
actors representing different components of a systems, and connecting 
the actors to each other through channels. Here's a simple example of what
a model looks like::

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

You can find a number of other examples of models in the 'models' directory.

The scipysim project is inspired by the UC Berkeley Ptolemy project, but 
we are taking a slightly different approach to implementing the 
simulation engine. Our approach is based on implementing the simulator 
as a Kahn network of actors that communicate via tagged-signals. Each of 
these actors run in their own thread, and communicate via dedicated 
Channels - which are based on the thread safe FIFO queue implementation 
in the Python standard library. These base level actors can be composed 
together to create models, which are also actors in their own right - 
running in their own thread with all communication occurring through 
input and output channels.

Scipysim is still very much under active development, and contains a 
number of experimental or prototype components. The structure of the 
simulator is in a state of flux, so there are no guarantees that models
developed to work with a particular release will still work with the next release.

Testing Scipy Simulator
=======================

Scipy Simulator comes with a large collection of unit tests.
All the tests can be run as a suite using nosetests::

	nosetests
	
A helper script called test_scipysim.py has been placed in the scipysim 
module to launch nosetests::

	./scipysim/test_scipysim.py

If you downloaded from the repository the tests can be run with setuptools::

	python setup.py test

The tests can also be found in the module hierarchy and run individually::

	python ./scipysim/actors/io/test_io.py


Installing Scipy Simulator
==========================

You can install scipysim to your main site-packages folder with::

	sudo python setup.py install
	
on Linux or Mac OS X; and::
	
	python setup.py install
	
on Windows. To install in a more sandboxed "development" environment
substitute develop for install, e.g.::

	sudo python setup.py develop

This installs an egg at the current directory and links to the package 
in your site-packages folder.
 
Creating Binary Installers
==========================

Firstly to clean the obsolete .pyc or .pyo files use::

	python setup.py clean --all

Generate a built distribution like so::

	python setup.py bdist
	
On Windows, to make a nice pretty GUI installer::

	python setup.py bdist --format wininst

Similarly a source distribution can be created with::

	python setup.py sdist

Contributors
============

This project was initiated in the Department of Electrical & Computer 
Engineering at the University of Canterbury (http://www.elec.canterbury.ac.nz/) by:

* Brian Thorne (brian dot thorne at canterbury dot ac dot nz)

* Allan McInnes (allan dot mcinnes at canterbury dot ac dot nz)


Project Site
============
The main development occurs on Google Code at http://scipy-sim.googlecode.com


Contribute to scipysim
======================

First get the source code with mercurial:

	hg clone https://scipy-sim.googlecode.com/hg/ scipy-sim
	
And send us a patch by creating a new issue http://code.google.com/p/scipy-sim/issues/entry
