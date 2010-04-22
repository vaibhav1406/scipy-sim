#!/usr/bin/env python
'''
A user interface for creating and running simulations.

@author: Brian Thorne
'''
from Tkinter import Tk
from Tkinter import Frame, Button, Canvas, Text
from Tkconstants import LEFT, BOTH, END, X, Y, TOP, RIDGE
from ttk import *
import subprocess
import os
from os import path
import tempfile
import glob
import logging

# TODO: replace with ttk NoteBook
from tabs import Notebook as NoteBook

from codefile import CodeFile
from codegroup import ExamplesGroup

from simulation_canvas import SimulationCanvas


logging.basicConfig( level=logging.DEBUG )
logging.info( "GUI module loaded, logging enabled" )

WELCOME_MESSAGE = "Select an actor or model on the left to preview here."

# Find the path to this file
PATH_TO_SCRIPT = path.dirname( path.realpath( __file__ ) )
EXAMPLES_DIRECTORY = path.split( PATH_TO_SCRIPT )[0]
logging.info( "Script address is '%s'" % PATH_TO_SCRIPT )
logging.info( "Example path is %s" % ( EXAMPLES_DIRECTORY ) )


class App:
    """The base application"""

    def set_active_block( self, codefile ):
        logging.debug( "Loaded file: %s" % codefile.name )
        self.loadedComponent = codefile.name
        self.simulation.preview_actor( codefile )

    def __init__( self, frame ):
        self.componentLoaded = False
        # The frame for all the file management on the left.
        file_frame = Frame( frame )
        file_frame.pack( side=LEFT, fill=BOTH, expand=1 )

        # Get the contents for the models and actors.
        ( models, actors ) = [path.join( EXAMPLES_DIRECTORY, a ) for a in ["models", "actors"]]

        # Create the tree widgets for models, and actors.
        callbacks = ( self.write_to_win, self.set_active_block )

        logging.debug( "Searching Actors and Models packages and locating scipysim actors" )
        ExamplesGroup( "Models", file_frame, models, callbacks )
        ExamplesGroup( "Actors", file_frame, actors, callbacks )
        logging.info( "Finished locating blocks" )
        # The frame for the main window
        main_frame = Frame( frame )
        main_frame.pack( side=LEFT )

        logging.debug( "Setting up simulation canvas" )
        self.simulation = SimulationCanvas( main_frame )

        self._create_controls_frame( frame, main_frame )
        logging.debug( "Done creating buttons. Creating Notebook now." )
        # Create a few tabs (notebook style) for viewing the source code
        # One tab will show the models source
        # the other will show the selected components
        source_frame = Frame( main_frame )
        source_frame.pack( side=TOP )
        self.notebook = NoteBook( source_frame, TOP )

        logging.debug( "Getting the notebooks main frame (the Model src viewer)" )
        model_src_frame = Frame( self.notebook() )

        logging.debug( "Creating Model Source Text Editor" )
        # TODO: decide if this should be read only...
        self.modelSrcEdit = Text( model_src_frame, width=80 )
        self.modelSrcEdit.pack( side=TOP, fill=X )
        self.modelSrcEdit.insert( END, "Model Source Viewer" )

        component_src_frame = Frame( self.notebook() )

        logging.debug( "Creating component Source Text Editor" )
        self.textEdit = Text( component_src_frame, width=80 )
        self.textEdit.pack( side=TOP, fill=X )
        self.textEdit.insert( END, "Component Editor" )

        b1 = Button( component_src_frame, text="Run this file", command=lambda: self.test() if self.componentLoaded else None )
        # pack widgets before adding the frame 
        # to the Notebook (but not the frame itself)!
        b1.pack( side=TOP, fill=X, expand=0 )

        # An empty frame so the source viewer can be "minimised"
        blank_src_frame = Frame( self.notebook() )

        logging.debug( "Adding the screens to the notebook" )
        self.notebook.add_screen( component_src_frame, "Component Source" )
        self.notebook.add_screen( model_src_frame, "Model Source" )
        self.notebook.add_screen( blank_src_frame, "Hide Source Viewer" )

        self.console = Text( main_frame, height=10, width=80 )
        self.console.pack( fill=X )
        self.console.insert( END, "Output Console\n \n" )

        logging.debug( "Finished setting up scipy-simulator gui" )


    def save( self ):
        from tkFileDialog import asksaveasfilename
        f = asksaveasfilename( parent=root, defaultextension=".txt" )
        if not f:
            return
        try:
            text = self.textEdit.get( 1.0, END )
            writeFile( f, text )
        except IOError:
            from tkMessageBox import showwarning
            showwarning( "Save As", "Cannot save the file." )
            raise "Cancel"

    def test( self ):
        """
        Test the python file that is currently loaded in the component editor.
        Assuming it has tests that run on __main__
        """
        logging.debug( "Filename of currently loaded file is '%s'" % self.loadedComponent )
        pythonRunner = PythonRunner()
        pythonRunner.runFile( self.loadedComponent )

    def stop( self ):
        logging.debug( "Stop simulation button pressed" )
        raise NotImplemented

    def run( self ):
        """Get the text from the model source window, save as a temp file in the model dir, 
        run the tempfile with python.
        
        """
        logging.info( "Running simulation" )
        text = self.textEdit.get( 1.0, END )
        #temp = os.path.join(os.path.split(PATH_TO_SCRIPT)[0], 'local', 'temp.py')
        temp = tempfile.NamedTemporaryFile( 'w', dir=path.join( EXAMPLES_DIRECTORY, 'models' ) )
        writeFile( temp.name, text )
        pr = PythonRunner()
        output = pr.runFile( temp.name )
        self.write_to_console( output )

    def write_to_console( self, text ):
        """Appends some text to the output console"""
        if text is not None:
            self.console.insert( END, "\n" + text + "\n" )
        self.console.see( END )    # Scroll the console

    def write_to_win( self, text ):
        """Replaces the text in the editor."""
        self.componentLoaded = True
        self.textEdit.delete( 1.0, END )
        self.textEdit.insert( 'end', text )

    def help( self ):
        """Display some helpful message in the output console"""
        self.write_to_console( """Help for SciPy-Simulator""" )

    def _create_controls_frame( self, frame, main_frame ):
        logging.debug( "Creating and filling controls frame" )
        controls_frame = Frame( main_frame )
        controls_frame.pack( fill=X )
        run_button = Button( controls_frame, text="Test", command=lambda:self.run() if self.componentLoaded else None )
        run_button.pack( side=LEFT )
        stop_button = Button( controls_frame, text="Stop", command=self.stop )
        stop_button.pack( side=LEFT )
        save_button = Button( controls_frame, text="Save", command=self.save )
        save_button.pack( side=LEFT )
        help_button = Button( controls_frame, text="Help", command=self.help )
        help_button.pack( side=LEFT )
        quit_button = Button( controls_frame, text="QUIT", command=frame.quit )
        quit_button.pack( side=LEFT )


class PythonRunner:
    def __init__( self ):
        pass

    def runFile( self, file ):
        # FIX: This seems to work from the command line, but not when launched from
        # eclipse... ?
        try:
            proc = subprocess.Popen( 'python2.6 "' + file + '"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            output, err = proc.communicate()
            retcode = proc.wait()
            if retcode < 0:
                logging.error( "Child Python process was terminated by signal: %d" % retcode )
                return output + err
            else:
                logging.debug( "Child Python process returned: %d" % retcode )
                return output + err
        except OSError, e:
            logging.error( "Execution failed: %s" % e )


def writeFile( filepath, content ):
    '''Save a file to disk.'''
    try:
        if os.path.exists( os.path.split( filepath )[0] ):
            f = open( filepath, 'w' )
            f.seek( 0 )
            f.write( content )
            f.close()
    except Exception, e:
        print( "File write error occurred...", e )

if __name__ == "__main__":
    root = Tk()

    root.title( "Scipy-Simulator Gui" )

    app = App( root )
    logging.debug( "Entering mainloop..." )
    root.mainloop()
