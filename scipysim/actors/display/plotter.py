#!/usr/bin/env python

'''
This file defines a Plotter actor. The plotting uses a Tkinter GUI and 
runs in a seperate process. 
The "actor" is composited of:
    * a decorating actor *New_Process_Actor* which allows a class to run
      in a seperate process. It has an additional actor:
    * Channel2Process which takes objects off the Channel and puts them 
      on a multiprocessing queue.
    * a BasePlotter instance which runs entirely in a seperate process
      doing the actual plotting.

TODO: This version no longer does live plotting. 

Note: There is a process safe Queue in the multiprocessing module. It 
MUST be used to communicate between processes.

@author: Brian Thorne 2010
'''
from multiprocessing import Process, Condition
from multiprocessing import Queue as MQueue

import sys, os

from scipysim import Actor, Channel, Event
from scipysim.core.actor import DisplayActor

def target(cls, args, kwargs):
    '''This is the function that gets run in a new process'''
    run_gui_loop = issubclass(cls, DisplayActor)
    if run_gui_loop:
        import Tkinter as Tk
        import matplotlib
        matplotlib.use('TkAgg')
        
        # Create new Tkinter window for the plot
        root = Tk.Tk()
        root.wm_title('Scipy Sim')
        kwargs['root'] = root
    
    # Create the Actor that we are wrapping
    block = cls(**kwargs)
    
    block.start()
    
    if run_gui_loop:
        Tk.mainloop()

    block.join()


class New_Process_Actor(Actor):
    '''Create an Actor in a new process. Connected as usual with scipysim 
    channels. When this Actor is started, it launches a new process, creates
    an instance of the Actor class passed to it in a second thread, and starts
    that actor.
    '''
    def __init__(self, cls, *args, **kwargs):
        super(New_Process_Actor, self).__init__()
        self.cls = cls
        self.args = list(args)
        self.kwargs = kwargs
        self.mqueue = MQueue()
        
        if 'input_channel' not in kwargs:
            kwargs['input_channel'] = self.args[0]
        
        chan = kwargs['input_channel']
        kwargs['input_channel'] = self.mqueue
        
        
        print 'chan: ', chan
        self.c2p = Channel2Process(chan, self.mqueue)
        
        self.c2p.start()


    def run(self):
        self.t = Process(target=target, args=(self.cls, self.args, self.kwargs))
        self.t.start()
        self.c2p.join()
        self.t.join()
        
class Channel2Process(Actor):
    '''
    Gets objects off a Channel and puts them in a multiprocessing.Queue
    
    This Actor (thread) must be called from the side which has the channel.
    '''
    def __init__(self, channel, queue):
        super(Channel2Process, self).__init__()
        self.channel = channel
        self.queue = queue
    
    def process(self):
        obj = self.channel.get(True)
        if obj is not None:
            self.queue.put(obj)
        else:
            
            self.queue.put(None)
            # Indicate that nothing else from this process will be put in queue
            self.queue.close()
            # Block on flushing the data to the pipe. Must be called after close
            self.queue.join_thread()
            self.stop = True
    

class BasePlotter(DisplayActor):
    def __init__(self, 
            root,
            input_channel,
            refresh_rate=2,
            title='Scipy Simulator Plot',
            own_fig=True,
            xlabel=None,
            ylabel=None,
            ):
        '''An Actor that creates a figure, canvas and axis and plots data from
        a queue.
        
        '''
        super(BasePlotter, self).__init__(input_channel)

        # Data arrays
        self.x_axis_data = []
        self.y_axis_data = []

        # Doing imports here to keep in local scope (and so its in the correct process)  
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas
        from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
        from matplotlib.figure import Figure
        
        # Save a reference to the main Tk window
        self.root = root
        
        # Creating the plot
        self.fig = Figure(figsize=(5,4), dpi=120)
        self.axis = self.fig.add_subplot(1, 1, 1)
        self.title = self.axis.set_title(title)
        
        if xlabel is not None: self.axis.set_xlabel(xlabel)
        if ylabel is not None: self.axis.set_ylabel(ylabel)
        
        # Instantiate canvas
        self.canvas = FigureCanvas(self.fig, master=self.root)

        # Pack canvas into root window
        self.canvas.get_tk_widget().pack(expand=1)

        # Put the graph navigation toolbar in the window
        toolbar = NavigationToolbar2TkAgg( self.canvas, self.root )
        # We can have our own buttons etc here:
        #Tk.Button(master=toolbar, text='Quit', command=sys.exit).pack()

    def process(self):
        obj = self.input_channel.get()     # this is actually blocking
        if obj is None:
            self.stop = True

            self.input_channel.close()
            self.input_channel.join_thread()
            self.plot()

            return

        self.x_axis_data.append(obj['tag'])
        self.y_axis_data.append(obj['value'])
        obj = None
        
    def plot(self):
        self.axis.plot(self.x_axis_data, self.y_axis_data)
        self.canvas.show()

class Plotter(Actor):
    def __init__(self, *args, **kwargs):
        super(Plotter, self).__init__()
        self.npa = New_Process_Actor(BasePlotter, *args, **kwargs)
        
    def run(self):
        self.npa.start()
        self.npa.join()

def test_NPA():
    data = [Event(i, i**2) for i in xrange( 10 )]
    q1 = Channel()
    npa = New_Process_Actor(BasePlotter, input_channel=q1) 
    import time, random
    print 'starting other process actor...'
    npa.start()
    time.sleep(random.random() * 0.01)
    print 'Adding data to queue.', q1
    [q1.put(d) for d in data + [None]]

    print 'other calculations keep going...'
    npa.join()
    print 'NPA is done'

if __name__ == "__main__":
    print 'testing npa...'

    test_NPA()
    
