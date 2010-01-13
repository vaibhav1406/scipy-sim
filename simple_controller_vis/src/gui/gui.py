#!/usr/bin/env python
'''
A user interface for creating and running simulations.

@author: Brian Thorne
'''

from Tkinter import *
import commands
import os
from os import path
import tempfile
import glob
import logging

from tabs import Notebook

logging.basicConfig(level=logging.DEBUG)
logging.info("GUI module loaded, logging enabled")

WELCOME_MESSAGE = "Select an actor or model on the left to preview here."

# Find the path to this file
pathtoscript = os.path.dirname(os.path.realpath(__file__))
logging.info("Script address is '%s'" % pathtoscript)

def load_example(name, examplesDir=os.path.join(os.path.split(pathtoscript)[0],'models')):
    """Load an actor or model file."""
    text = "".join(open(os.path.join(examplesDir, name), 'r').readlines())
    return text

class ExamplesGroup:
    """A group of actors to be displayed in a block."""
    def __init__(self, name, frame, code, set_text_callback):
        self.name = name
        self.frame = frame
        self.code = code
        self.set_text = set_text_callback
        self.draw_list()

    def get_list(self):
        """Return a list of the actors names."""
        keys = self.code.keys()
        return keys

    def get_example(self, key):
        """Get the string of code for a particular actor"""
        return self.code[key]

    def get_selection(self, x):
        """Set the code preview window to display the source
        code of the currently selected actor
        """
        index = self.listbox.curselection()[0]
        seltext = self.listbox.get(index)
        self.set_text(self.get_example(seltext))

    def draw_list(self):
        """Print the names of the Actors as a select list box"""
        label = Label(self.frame, text=self.name)
        label.pack()
        scrollbar = Scrollbar(self.frame, orient=VERTICAL)

        
        self.listbox = Listbox(self.frame, yscrollcommand=scrollbar.set, selectmode=SINGLE)
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        
        self.listbox.pack(fill=BOTH, expand=1)
        for i in self.get_list():
            self.listbox.insert(END, i)

        # left mouse click on a list item to display selection
        self.listbox.bind('<ButtonRelease-1>', self.get_selection)

def get_models_and_actors():
    """Return dictionaries with the names and paths of each model and actor to display."""
    # The models and actors are loaded from the models/actors directory.
    model_filenames = [(path.split(a)[1], path.abspath(a)) for a in glob.glob("./../models/[A-z]*.py") ]
    logging.debug("Model files found: %s" % model_filenames)
    actor_filenames = [(path.split(a)[1], path.abspath(a)) for a in glob.glob("./../models/actors/[A-z]*.py")]
    logging.debug("Actor files found: %s" % actor_filenames)
    models_dict = dict( [[a[0], load_example(a[1])] for a in model_filenames if not a[0].startswith("__")] )
    actors_dict = dict( [[a[0], load_example(a[1])] for a in actor_filenames if not a[0].startswith("__")] )     
    return (models_dict, actors_dict)

class App:
    """The base application"""
    def __init__(self, frame):

        # The frame for all the file management on the left.
        file_frame = Frame(frame)
        file_frame.pack(side=LEFT, fill=BOTH, expand=1)

        # Get the contents for the models and actors.
        (models_dict, actors_dict) = get_models_and_actors()
        
        # Create the list box widgets for models, and actors.
        ExamplesGroup("Models", file_frame, models_dict, self.write_to_win)
        ExamplesGroup("Actors", file_frame, actors_dict, self.write_to_win)
        
        # The frame for the main window
        main_frame = Frame(frame)
        main_frame.pack(side=LEFT)


        # Text Editor
        self.textEdit = Text(main_frame, width=80)
        self.textEdit.pack(side=TOP, fill=X)
        self.textEdit.insert(END, WELCOME_MESSAGE)

        # Frame to hold all the main buttons
        controls_frame = Frame(main_frame)
        controls_frame.pack(fill=X)

        self.console = Text(main_frame, width=80)
        self.console.pack(fill=X)
        self.console.insert(END, "Output Console\n \n")


        run_button = Button(controls_frame, text="Test", fg="green", command=self.run)
        run_button.pack(side=LEFT)

        stop_button = Button(controls_frame, text="Stop", fg="red", command=self.stop)
        stop_button.pack(side=LEFT)

        save_button = Button(controls_frame, text="Save", command=self.save)
        save_button.pack(side=LEFT)

        help_button = Button(controls_frame, text="Help", command=self.help)
        help_button.pack(side=LEFT)

        quit_button = Button(controls_frame, text="QUIT", fg="white", command=frame.quit)
        quit_button.pack(side=LEFT)

    def save(self):
        from tkFileDialog import asksaveasfilename
        f = asksaveasfilename(parent=root, defaultextension=".txt")
        if not f:
            return
        try:
            text = self.textEdit.get(1.0, END)
            writeFile(f, text)
        except IOError:
            from tkMessageBox import showwarning
            showwarning("Save As", "Cannot save the file.")
            raise "Cancel"

    def test(self):
        """Test the module that is currently loaded in the text window
        ideally it has unit tests..."""
        logging.debug("Test module button pressed")
        raise NotImplemented
    
    def stop(self):
        logging.debug("Stop simulation button pressed")
        raise NotImplemented

    def run(self):
        """Get the text from the model source window, save as a temp file in the model dir, 
        run the tempfile with python.
        
        """
        text = self.textEdit.get(1.0, END)
        #temp = os.path.join(os.path.split(pathtoscript)[0], 'local', 'temp.py')
        temp = tempfile.NamedTemporaryFile('w', dir="./../models" )
        writeFile(temp.name, text)
        pr = PythonRunner()
        output = pr.runFile(temp.name)
        self.write_to_console(output)

    def write_to_console(self, text):
        """Appends some text to the output console"""
        if text is not None:
            self.console.insert(END, "\n" + text + "\n")
        self.console.see(END)    # Scroll the console

    def write_to_win(self, text):
        """Replaces the text in the editor."""
        self.textEdit.delete(1.0, END)
        self.textEdit.insert('end', text)

    def help(self):
        """Display some helpful message in the output console"""
        self.write_to_console("""Help for SciPy-Simulator""")


class PythonRunner:
    def __init__(self):
        pass

    def runFile(self, file):
        cmd = "python " + '"' + file + '"'
        (status, outtext) = commands.getstatusoutput(cmd)
        # TODO redirect the stdin to the bottom pane...
        # TODO do in seperate thread, so we can stop a long running simulation...
        if status:
            logging.error( "Error in running simulation. Status error number: %d. Output:\n%s" % (status, outtext) )
            

def writeFile(filepath, content):
    try:
        if os.path.exists(os.path.split(filepath)[0]):
            f = open(filepath, 'w')
            f.seek(0)
            f.write(content)
            f.close()
    except Exception, e:
        print("File write error occurred...", e)

if __name__ == "__main__":
    root = Tk()
    root.title("Scipy-Simulator Gui")

    app = App(root)

    root.mainloop()
