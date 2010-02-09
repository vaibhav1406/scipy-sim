import logging
import os
import re
from Tkinter import Label, Scrollbar, Button
from Tkconstants import VERTICAL, SINGLE, BROWSE, RIGHT, Y, BOTH, END, ANCHOR
from ttk import Treeview, Button

PATH_TO_SCRIPT = os.path.dirname(os.path.realpath(__file__))
EXAMPLES_DIRECTORY = os.path.split(PATH_TO_SCRIPT)[0]

class ExamplesGroup:
    """A group of actors to be displayed in a single block."""
    def __init__(self, name, frame, directory, set_callbacks):
        """Create a group of examples for display and selection.
        
        Params:
        name - the name of this block
        frame - the frame to be attached to.
        codefiles - a list of CodeFile objects to be displayed
        set-callbacks - a tuple of two functions: 
                        both get called when an example is clicked on.
                * The first is passed the text for the example.
                * The second is passed the Codefile object.
        """
        self.name = name
        self.frame = frame
        self.directory = directory
        
        self.set_text, self.set_active_block = set_callbacks
        
        self.scrollbar = Scrollbar(self.frame, orient=VERTICAL)
        
        #self.listbox = Listbox(self.frame, 
        #                       yscrollcommand=self.scrollbar.set, 
        #                       selectmode=BROWSE)
        src_dir = os.path.normpath(__file__ + '../../../')
        self._draw_tree()

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
        self.set_active_block(selected_codefile)
        self.set_text(self.get_example(selected_name))

    def _draw_tree(self):
        """Print the names of the Actors as a tree"""
        label = Label(self.frame, text=self.name)
        label.pack()
        
        self.tree = make_tree(self.frame, self.directory)
        
        
        #self.scrollbar.config(command=self.listbox.yview)
        #self.scrollbar.pack(side=RIGHT, fill=Y)
        #self.listbox.pack(fill=BOTH, expand=1)
        #for i in self.codefiles:#self.get_list():
        #    self.listbox.insert(END, i)

        # left mouse click on a list item to display selection in source viewer
        self.tree.bind('<ButtonRelease-1>', self.get_selection)
        
def fill_tree(tree, directory):
    '''Parse a directory and add to an existing tree.
    Return a dictionary of the tree id: CodeFile'''
    for file_tuple in os.walk(directory):
        '''The tuples contains:
            [0] - The path
            [1] - Subdirectories
            [2] - Files
        '''
        # Find out where we are in the tree
        parent_node = os.path.dirname(os.path.relpath(file_tuple[0], directory))
        current_node = os.path.relpath(file_tuple[0], directory)
        if current_node is ".": current_node = ""
        logging.debug("Current node is: <%s>, Parent node is: <%s>" % (current_node, parent_node))
        
        # Search for interesting files
        python_file_regex = re.compile("^(?!tests?).*[^_]\.py$", re.IGNORECASE)          
        files = filter(python_file_regex.search, file_tuple[2])
        logging.info("Under the %s directory are %d files: \n%s" % (os.path.basename(file_tuple[0]), len(files), files))
        
        # Add the files to the parent node
        for file in files:
            # Inserted underneath an existing node:
            tree.insert(current_node, 'end', text=file, tags=('node'))
            #tree.set(plotterID, 'ins', 1)
            #tree.set(plotterID, 'outs', 0)
        
        
        # Must add the (sub)directories to the tree as nodes under the current node.
        for subdir in file_tuple[1]:
            '''
            subdir is going to be a string like "trig"
            but the tree id will be math/trig
            '''
            node = os.path.relpath( os.path.join(file_tuple[0], subdir), directory)
            logging.debug("Child node is: <%s>" % node)
            tree.insert(current_node, 'end', node, text=subdir.title(), tags=('dir'))
            

def make_tree(mainframe, directory):
    # Make a tree
    tree = Treeview(mainframe, columns=('ins', 'outs'))
    # Pack the tree into the GUI
    tree.grid(column=2, row=4)
    tree.heading("#0", text="Block")
    tree.heading('ins', text='Inputs')
    tree.heading('outs', text="Outputs")
    
    # Set the width and alignment of the two columns
    tree.column('ins', width=60, anchor='center')
    tree.column('outs', width=60, anchor='center')
    
    
    actor_dir = os.path.join(EXAMPLES_DIRECTORY, 'actors')
    fill_tree(tree, actor_dir)
    def go(*args):
        print "going"
        print args[0]
    tree.tag_bind('node', '<1>', go)
    #tree.tag_configure('node', background='green')
    return tree