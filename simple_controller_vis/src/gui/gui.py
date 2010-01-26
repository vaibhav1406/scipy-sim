#!/usr/bin/env python
'''
A user interface for creating and running simulations.

@author: Brian Thorne
'''

from Tkinter import Frame, Button, Canvas, Tk, Text
from Tkconstants import LEFT, BOTH, END, X, Y, TOP, RIDGE

import subprocess
import os
from os import path
import tempfile
import glob
import logging

from codefile import CodeFile
from tabs import Notebook
from codegroup import ExamplesGroup

logging.basicConfig(level=logging.DEBUG)
logging.info("GUI module loaded, logging enabled")

WELCOME_MESSAGE = "Select an actor or model on the left to preview here."

# Find the path to this file
PATH_TO_SCRIPT = os.path.dirname(os.path.realpath(__file__))
EXAMPLES_DIRECTORY = os.path.join(os.path.split(PATH_TO_SCRIPT)[0],'models')
logging.info("Script address is '%s'" % PATH_TO_SCRIPT)
logging.info("Example path is %s" % (EXAMPLES_DIRECTORY))


def get_models_and_actors():
    """Return dictionaries with the names and paths of each model and actor to display."""
    # The models and actors are loaded from the models/actors directory.
    # TODO: Parse a tree instead of loading actors and models.
    
    model_filenames = [(path.split(a)[1], path.abspath(a)) for a in glob.glob(EXAMPLES_DIRECTORY + "/[A-z]*.py") ]
    actor_filenames = [(path.split(a)[1], path.abspath(a)) for a in glob.glob(EXAMPLES_DIRECTORY + "/actors/[A-z]*.py")]
    [logging.debug(a) for a in ["Models:"] + model_filenames + ["\nActors:"] + actor_filenames]

    models = [CodeFile(a[1]) for a in model_filenames if not a[0].startswith("__")]
    actors = [CodeFile(a[1]) for a in actor_filenames if not a[0].startswith("__")]    
    logging.info("%d model files loaded." % len(models))
    logging.info("%d actor files loaded" % len(actors))
    return (models, actors)

class ID_Generator:
    #could use count from itertools
    def __init__(self):
        self.generator = self._get_unique_id()
    
    def get_unique_id(self):
        return self.generator.next()
    
    def _get_unique_id(self):
        for i in xrange(1e8):
            yield i

class Simulation_Canvas(object):
    """A canvas where blocks can be dragged around and connected up"""
    # The class attribute colours will hold all the colour info 
    # Randomly chosen from (visibone.com/colurlab)
    colours = {
         "background": "#CCFFCC",   # Pale weak green. A weak yellow is FFFFCC
         "block": "#00FF66", # a lime green
         "preview": "#0099FF", # a blue
         "selected": "#FFCCCC" # pale weak red
         }
    
    size = (width, height) = (550, 250)
    
    font = ("Helvetica", 10)
    
    
    def __init__(self, frame):
        # Create the canvas
        self.canvas = Canvas(frame, 
                             width=self.width, height=self.height,
                             relief=RIDGE, 
                             background =self.colours["background"], 
                             borderwidth =1)
        # Add event handlers for dragable items
        self.canvas.tag_bind ("DRAG", "<ButtonPress-1>", self.mouse_down)
        #self.canvas.tag_bind ("DRAG", "<ButtonRelease-1>", self.mouse_release)
        self.canvas.tag_bind ("DRAG", "<Enter>", self.enter)
        self.canvas.tag_bind ("DRAG", "<Leave>", self.leave)
        self.canvas.pack(side=TOP)
        
        # Some default locations
        self.PREVIEW_WIDTH = 80
        self.PREVIEW_LOCATION = (self.PREVIEW_X, self.PREVIEW_Y) = (15, 30)
        self.BLOCK_SIZE = (self.BLOCK_WIDTH, self.BLOCK_HEIGHT) = (70, 50)
        
        # Draw a "preview" area
        self.canvas.create_line(self.PREVIEW_WIDTH,0,self.PREVIEW_WIDTH,250,dash=True)
        
    def preview_actor(self, codefile):
        """
        Display a preview of an actor or compisite actor in the canvas,
        it will be dragable into desired position
        """
        logging.debug("Creating a preview of %(name)s on simulation canvas." % {'name':codefile.name})
        
        logging.debug("Delecting any existing items still tagged 'preview'")
        self.canvas.delete("preview")
        
        
        self.canvas.create_rectangle(*self.PREVIEW_LOCATION + self.BLOCK_SIZE, 
                                     fill=self.colours["preview"], 
                                     tags =["DRAG",                     # Anything moveable will have the "DRAG" tag
                                            "name:" + codefile.name,    # Every blocks name will tagged so we can group bits together
                                            "type:block",               # type: block/text
                                            "preview"
                                            ]
                                     )
        self.canvas.create_text (self.PREVIEW_X + (self.BLOCK_WIDTH/2), self.PREVIEW_Y + 25, 
                                 font=self.font, text = codefile.name, 
                                 tags =["DRAG", 
                                        "name:" + codefile.name,
                                        "type:text",
                                        "preview"
                                        ]
                                 )
    
    def mouse_down(self, event):
        logging.debug("The mouse was pressed at (%d, %d)" % (event.x, event.y))
        logging.debug("The mouse went down on a block. Binding mouse release...")
        selected = self.canvas.gettags("current")
        logging.debug("Currently selected items tags are %s" % selected.__repr__())
        self.selected_name = [a for a in selected if a.startswith("name:") ][0]
        logging.debug("Block selected was %s" % self.selected_name)
        self.select_location = (event.x, event.y)
        self.canvas.addtag('Selected', 'withtag', self.selected_name) 
        event.widget.itemconfigure("Selected", fill=self.colours["selected"])
        self.canvas.bind("<ButtonRelease-1>", self.mouse_release)
    
    def mouse_release(self, event):
        logging.debug("The mouse was released at (%d, %d)" % (event.x, event.y))
        if event.x >= 0 and event.x <= self.canvas.winfo_width() \
            and event.y >= 0 and event.y <= self.canvas.winfo_height():
                logging.debug("Valid move inside canvas. Relocating block.")
                self.canvas.move("Selected", event.x - self.select_location[0], event.y - self.select_location[1])
                if event.x >= self.PREVIEW_WIDTH:
                    if "preview" in self.canvas.gettags("Selected"):
                        logging.info("Moved out of preview zone, adding now component to model")
                        self.canvas.dtag("preview")
                        #TODO HERE - add to model compiler or what ever...
                    event.widget.itemconfigure("Selected", fill=self.colours["block"])
                else:
                    event.widget.itemconfigure("Selected", fill=self.colours["preview"])
                    self.canvas.addtag_withtag("preview", "Selected")
                
                #block = self.canvas.gettags("Selected")
                #logging.debug("Block moved was made up of these components: %s" % block.__repr__())
                self.canvas.dtag("Selected", "Selected")
                                
        else: 
            logging.info("Invalid move.")
        
        
    def enter(self, event):
        logging.debug("Enter")
        
    def leave(self, event):
        logging.debug("Leaving")

class App:
    """The base application"""
    
    def set_active_block(self, codefile):
        logging.debug("Loaded file: %s" % codefile.name)
        self.loadedComponent = codefile.name
        self.simulation.preview_actor(codefile)
    
    def __init__(self, frame):
        self.componentLoaded = False
        # The frame for all the file management on the left.
        file_frame = Frame(frame)
        file_frame.pack(side=LEFT, fill=BOTH, expand=1)

        # Get the contents for the models and actors.
        (models, actors) = get_models_and_actors()
        self.loadedComponent = ""
        
        # Create the list box widgets for models, and actors.
        callbacks = (self.write_to_win, self.set_active_block)
        ExamplesGroup("Models", file_frame, models, callbacks)
        ExamplesGroup("Actors", file_frame, actors, callbacks)
        
        # The frame for the main window
        main_frame = Frame(frame)
        main_frame.pack(side=LEFT)

        self.simulation = Simulation_Canvas(main_frame)

        # Frame to hold all the main buttons
        controls_frame = Frame(main_frame)
        controls_frame.pack(fill=X)
        
        run_button = Button(controls_frame, text="Test", fg="green", command=lambda: self.run() if self.componentLoaded else None)
        run_button.pack(side=LEFT)

        stop_button = Button(controls_frame, text="Stop", fg="red", command=self.stop)
        stop_button.pack(side=LEFT)

        save_button = Button(controls_frame, text="Save", command=self.save)
        save_button.pack(side=LEFT)

        help_button = Button(controls_frame, text="Help", command=self.help)
        help_button.pack(side=LEFT)

        quit_button = Button(controls_frame, text="QUIT", fg="white", command=frame.quit)
        quit_button.pack(side=LEFT)

        # Create a few tabs (notebook style) for viewing the source code
        # One tab will show the models source
        # the other will show the selected components
        source_frame = Frame(main_frame)
        source_frame.pack(side=TOP)
        self.notebook = Notebook(source_frame, TOP)
        
        # Get the notebooks main frame as the Model src viewer
        model_src_frame = Frame(self.notebook())
        
        # Model Source Text Editor
        # TODO: decide if this should be read only...
        self.modelSrcEdit = Text(model_src_frame, width=80)
        self.modelSrcEdit.pack(side=TOP, fill=X)
        self.modelSrcEdit.insert(END, "Model Source Viewer")

        component_src_frame = Frame(self.notebook())
        
        # Component Source Text Editor 
        self.textEdit = Text(component_src_frame, width=80)
        self.textEdit.pack(side=TOP, fill=X)
        self.textEdit.insert(END, "Component Editor")       

        b1 = Button(component_src_frame, text="Run this file", command=lambda: self.test() if self.componentLoaded else None)
        # pack widgets before adding the frame 
        # to the Notebook (but not the frame itself)!
        b1.pack(side=TOP, fill=X, expand=0)
        
        # An empty frame so the source viewer can be "minimized"
        blank_src_frame = Frame(self.notebook())
        
        # Add the screens to the notebook
        self.notebook.add_screen(component_src_frame, "Component Source")
        self.notebook.add_screen(model_src_frame, "Model Source")
        self.notebook.add_screen(blank_src_frame, "Hide Source Viewer")

        

        self.console = Text(main_frame, width=80)
        self.console.pack(fill=X)
        self.console.insert(END, "Output Console\n \n")



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
        """
        Test the python file that is currently loaded in the component editor.
        Assuming it has tests that run on __main__
        """
        logging.debug("Filename of currently loaded file is '%s'" % self.loadedComponent)
        pythonRunner = PythonRunner()
        pythonRunner.runFile(self.loadedComponent)
    
    def stop(self):
        logging.debug("Stop simulation button pressed")
        raise NotImplemented

    def run(self):
        """Get the text from the model source window, save as a temp file in the model dir, 
        run the tempfile with python.
        
        """
        logging.info("Runing simulation")
        text = self.textEdit.get(1.0, END)
        #temp = os.path.join(os.path.split(PATH_TO_SCRIPT)[0], 'local', 'temp.py')
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
        self.componentLoaded = True
        self.textEdit.delete(1.0, END)
        self.textEdit.insert('end', text)

    def help(self):
        """Display some helpful message in the output console"""
        self.write_to_console("""Help for SciPy-Simulator""")


class PythonRunner:
    def __init__(self):
        pass

    def runFile(self, file):
        # FIX: This seems to work from the command line, but not when launched from
        # eclipse... ?
        try:
            retcode = subprocess.call('python2.6 "' + file + '"', shell=True)
            if retcode < 0:
                logging.error("Child Python process was terminated by signal: %d" % retcode)
            else:
                logging.debug("Child Python process returned: %d" % retcode)
        except OSError, e:
            logging.error("Execution failed: %s" % e)
            

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
