#!/usr/bin/env python

'''
This file defines a Plotter actor. The plotting uses a Tkinter GUI and 
runs in a seperate process. 
The "actor" is composed of:
    * a decorating actor *New_Process_Actor* which allows a class to run
      in a separate process. It has an additional actor:
    * Channel2Process which takes objects off the Channel and puts them 
      on a multiprocessing queue.
    * a BasePlotter instance which runs entirely in a seperate process
      doing the actual plotting.

Note: There is a process safe Queue in the multiprocessing module. It 
MUST be used to communicate between processes.

@author: Brian Thorne
@author: Allan McInnes
'''
from multiprocessing import Process
from multiprocessing import Queue as MQueue
from multiprocessing import Event as MEvent

from scipysim import Actor, Channel, Event
from scipysim.core.actor import DisplayActor

import time

import logging


def target(cls, args, kwargs):
    '''This is the function that gets run in a new process'''
    run_gui_loop = issubclass(cls, DisplayActor)
    if run_gui_loop:
        import Tkinter as Tk
        import matplotlib
        matplotlib.use('TkAgg')
        
        # Create new Tkinter window for the plot
        root = Tk.Tk()
        root.wm_title('ScipySim')
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
        self.mevent = MEvent()
        
        if 'input_channel' not in kwargs:
            kwargs['input_channel'] = self.args[0]
        
        chan = kwargs['input_channel']
        kwargs['input_channel'] = self.mqueue
        
        
        print 'chan: ', chan
        self.c2p = Channel2Process(chan, self.mevent, self.mqueue)
        
        self.c2p.start()


    def run(self):
        self.t = Process(target=target, args=(self.cls, self.args, self.kwargs))
        self.t.start()
        self.mevent.set() # signal that process is ready to receive
        self.c2p.join()
        self.t.join()

        
class Channel2Process(Actor):
    '''
    Gets objects off a Channel and puts them in a multiprocessing.Queue
    
    This Actor (thread) must be called from the side which has the channel.
    '''
    def __init__(self, channel, ready_event, queue):
        super(Channel2Process, self).__init__()
        self.channel = channel
        self.queue = queue
        self.ready_event = ready_event
        self.first_time = True
    
    def process(self):

        if self.first_time:
            # Make sure the other end of the Queue can receive before trying to send
            # (avoids race conditions on the underlying pipe, and Broken Pipe errors)
            self.ready_event.wait()
            logging.info("Channel2Process done waiting for process")
            self.first_time = False

        obj = self.channel.get(True)
        self.queue.put(obj)
 
        if obj.last:
            # Indicate that nothing else from this process will be put in queue
            self.queue.close()
            # Block on flushing the data to the pipe. Must be called after close
            self.queue.join_thread()
            self.stop = True
            logging.info("Channel2Process finished")


class BasePlotter(DisplayActor):
    def __init__(self, 
            root,
            input_channel,
            live=True,
            refresh_rate=50,
            title='ScipySim Plot',
            own_fig=True,
            xlabel=None,
            ylabel=None,
            ):
        '''An Actor that creates a figure, canvas and axis and plots data from
        a queue.

        @param root : a reference to the main Tk window
        @param input_channel : channel for plot data
        @param live : True if the plot should perform live updating
        @param refresh_rate : rate in updates/second of plot updates
        @param title : title of the plot
        @param own_fig : True if produces own figure
        @param xlabel : x-axis label string
        @param ylabel : y-axis label string
        
        '''
        super(BasePlotter, self).__init__(input_channel)

        # Data arrays
        self.x_axis_data = []
        self.y_axis_data = []

        # Live updating
        self.live = live
        if live:
            assert refresh_rate > 0
            self.refresh_rate = refresh_rate
            self.min_refresh_time = 1.0 / self.refresh_rate
            self.last_update = time.time()

        # Doing imports here to keep in local scope (and so its in the correct process)  
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas
        from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
        from matplotlib.figure import Figure
        
        # Save a reference to the main Tk window
        self.root = root

        # Creating the plot
        self.fig = Figure()
        self.axis = self.fig.add_subplot(1, 1, 1)
        self.title = self.axis.set_title(title)
        self.line = None
        
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
        self.canvas.show()

    def process(self):
        # Grab all values that are currently available
        while not self.input_channel.empty():
            obj = self.input_channel.get_nowait()  # Non-blocking
            if obj.last:
                self.stop = True

                self.input_channel.close()
                self.input_channel.join_thread()
                self.plot()
                logging.info("Plotter finished")

                return

            self.x_axis_data.append(obj['tag'])
            self.y_axis_data.append(obj['value'])

        # Update the plot if necessary
        if self.live:
            self.plot()

        # Wait for next update
        time.sleep(self.min_refresh_time)
        
    def plot(self):
        if not self.line:
            if len(self.x_axis_data) > 0:
                self.line, = self.axis.plot(self.x_axis_data, self.y_axis_data)
        else:
            self.line.set_data(self.x_axis_data, self.y_axis_data)
            axes = self.line.get_axes()
            self.line.recache()
            axes.relim()
            axes.autoscale_view()
        self.canvas.draw()

class BaseStemmer(BasePlotter):
    def __init__(self,
            root,
            input_channel,
            live=True,
            refresh_rate=50,
            title='ScipySim Stem-Plot',
            own_fig=True,
            xlabel=None,
            ylabel=None,
            ):
        '''Actor that creates a figure, canvas and axis, and stem-plots
        data from a queue.

        @param root : a reference to the main Tk window
        @param input_channel : channel for plot data
        @param refresh_rate : rate in updates/second of plot updates
        @param title : title of the plot
        @param own_fig : True if produces own figure
        @param xlabel : x-axis label string
        @param ylabel : y-axis label string

        '''
        super(BaseStemmer, self).__init__(root, input_channel, live, 
                                          refresh_rate, title, own_fig,
                                          xlabel, ylabel)

        self.markerline = None
        self.stemlines = None
        self.baseline = None

        import matplotlib.lines as lines
        self.lines = lines


    def plot(self):
        '''Override base-class plot function to use stemming instead.

        Simply using the stem() function works, but is quite slow. The method
        we use here provides much faster updating.

        '''
        if not self.markerline:
            if len(self.x_axis_data) > 0:
                self.markerline, self.stemlines, self.baseline = \
                    self.axis.stem(self.x_axis_data, self.y_axis_data)
        else:
            axes = self.markerline.get_axes()

            # The markerline can be built directly from the data
            self.markerline.set_data(self.x_axis_data, self.y_axis_data)
            self.markerline.recache()

            # The baseline should be built from the start and end points of
            # the x axis
            _ , baseline_y = self.baseline.get_data()
            self.baseline.set_data([min(self.x_axis_data),
                max(self.x_axis_data)], baseline_y.tolist())
            self.baseline.recache()

            # Construct new stemlines and add them to the current plot
            for x, y in zip(self.x_axis_data, self.y_axis_data)[len(self.stemlines):]:
                stemline = self.lines.Line2D([0], [0])
                stemline.update_from(self.stemlines[0]) # Copy format
                stemline.set_data([x, x], [baseline_y[0], y])
                stemline.recache()
                axes.add_line(stemline)
                self.stemlines.append(stemline)

            axes.relim()
            axes.autoscale_view()
        self.canvas.draw()


class Plotter(Actor):
    '''Plot continuous data as a smooth line.'''
    def __init__(self, *args, **kwargs):
        super(Plotter, self).__init__()
        self.npa = New_Process_Actor(BasePlotter, *args, **kwargs)
        
    def run(self):
        self.npa.start()
        self.npa.join()


class StemPlotter(Actor):
    '''Plot discrete data as a sequence of stems.'''
    def __init__(self, *args, **kwargs):
        super(StemPlotter, self).__init__()
        self.npa = New_Process_Actor(BaseStemmer, *args, **kwargs)

    def run(self):
        self.npa.start()
        self.npa.join()


def test_NPA():
    data = [Event(i, i**2) for i in xrange( 100 )]
    q1 = Channel()
    q2 = Channel()
    npa1 = New_Process_Actor(BasePlotter, input_channel=q1)
    npa2 = New_Process_Actor(BaseStemmer, input_channel=q2)

    import time, random

    print 'starting other process actor...'
    npa1.start()
    npa2.start()

    time.sleep(random.random() * 0.01)

    print 'Adding data to queue.', q1
    print 'Adding data to queue.', q2

    for d in data:
        q1.put(d)
        q2.put(d)
        time.sleep(0.1)

    q1.put(LastEvent())
    q2.put(LastEvent())

    print 'other calculations keep going...'
    npa1.join()
    npa2.join()
    print 'NPA is done'

if __name__ == "__main__":
    print 'testing npa...'

    test_NPA()
    
