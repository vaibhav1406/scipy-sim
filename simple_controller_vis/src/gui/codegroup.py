from Tkinter import Listbox, Label, Scrollbar
from Tkconstants import VERTICAL, SINGLE, RIGHT, Y, BOTH, END

class ExamplesGroup:
    """A group of actors to be displayed in a block."""
    def __init__(self, name, frame, codefiles, set_callbacks):
        """Create a group of examples for display
        
        Params:
        name - the name of this block
        frame - the frame to be attached to.
        codefiles - a list of CodeFile objects to be displayed
        set-callbacks - what gets called when example is clicked on.
        """
        self.name = name
        self.frame = frame
        self.codefiles = codefiles
        self.set_text, self.set_filename = set_callbacks
        
        self.scrollbar = Scrollbar(self.frame, orient=VERTICAL)
        self.listbox = Listbox(self.frame, 
                               yscrollcommand=self.scrollbar.set, 
                               selectmode=SINGLE)
        
        self.draw_list()

    def get_list(self):
        """Return a list of the actors names."""
        names = [codefile.name for codefile in self.codefiles]
        return names
    
    def get_dict(self):
        """Return a dictionary of names: codefile instances."""
        return dict([[codefile.name, codefile] for codefile in self.codefiles])

    def get_example(self, name):
        """Get the string of code for a particular actor"""
        return self.get_dict()[name].get_code()

    def get_selection(self, x):
        """Set the code preview window to display the source
        code of the currently selected actor
        """
        index = self.listbox.curselection()[0]
        selected_name = self.listbox.get(index)
        selected_codefile = self.get_dict()[selected_name]
        self.set_filename(selected_codefile.filepath)
        self.set_text(self.get_example(selected_name))

    def draw_list(self):
        """Print the names of the Actors as a select list box"""
        label = Label(self.frame, text=self.name)
        label.pack()
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.pack(fill=BOTH, expand=1)
        for i in self.get_list():
            self.listbox.insert(END, i)

        # left mouse click on a list item to display selection
        self.listbox.bind('<ButtonRelease-1>', self.get_selection)