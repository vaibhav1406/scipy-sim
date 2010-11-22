import logging
import os
import re

from Tkinter import Label, Scrollbar
from Tkconstants import VERTICAL
from ttk import Treeview
 
from scipysim.core import CodeFile, fill_tree

PATH_TO_SCRIPT = os.path.dirname( os.path.realpath( __file__ ) )
EXAMPLES_DIRECTORY = os.path.split( PATH_TO_SCRIPT )[0]

class ExamplesGroup:
    """A group of actors to be displayed in a single block."""
    def __init__( self, name, frame, directory, set_callbacks ):
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

        self.scrollbar = Scrollbar( self.frame, orient=VERTICAL )

        #self.listbox = Listbox(self.frame, 
        #                       yscrollcommand=self.scrollbar.set, 
        #                       selectmode=BROWSE)
        src_dir = os.path.normpath( __file__ + '../../../' )
        self._draw_tree()

    def get_list( self ):
        """Return a list of the actors names."""
        return self.codefiles.keys()

    def get_dict( self ):
        """Return a dictionary of names: codefile instances."""
        return self.codefiles

    def get_example( self, name ):
        """Get the string of code for a particular actor"""
        return self.get_dict()[name].get_code()

    def get_selection( self, x ):
        """Set the code preview window to display the source
        code of the currently selected actor
        """
        logging.debug( "In 'get_selection' - Event: %s" % x )
        selected_name = self.tree.selection()
        logging.debug( "Selected: %s\nDictionary has:%s" % ( selected_name, self.codefiles.keys() ) )
        selected_name = selected_name[0]
        try:
            selected_codefile = self.get_dict()[selected_name]
        except KeyError, e:
            logging.debug( "The directory is probably selected." )
            return
        self.set_active_block( selected_codefile )
        self.set_text( self.get_example( selected_name ) )

    def _draw_tree( self ):
        """Print the names of the Actors as a tree"""
        label = Label( self.frame, text=self.name )
        label.pack()

        self.tree, self.codefiles = make_tree( self.frame, self.directory )
        logging.debug( "Finished drawing tree. Binding events now." )
        self.tree.pack()

        #self.scrollbar.config(command=self.listbox.yview)
        #self.scrollbar.pack(side=RIGHT, fill=Y)
        #self.listbox.pack(fill=BOTH, expand=1)
        #for i in self.codefiles:#self.get_list():
        #    self.listbox.insert(END, i)

        # left mouse click on a list item to display selection in source viewer

        # '<ButtonRelease-1>'
        self.tree.tag_bind( 'node', '<1>', self.get_selection )


# TODO: Remove the TK from this
def make_tree( mainframe, directory ):
    logging.debug( "Creating a new tree" )
    tree = Treeview( mainframe, columns=( 'ins', 'outs' ) )

    logging.debug( "Packing the tree into the GUI. Adding columns and headings" )

    tree.grid( column=2, row=4 )
    tree.heading( "#0", text="Block" )
    tree.heading( 'ins', text='Inputs' )
    tree.heading( 'outs', text="Outputs" )

    # Set the width and alignment of the two columns
    tree.column( 'ins', width=60, anchor='center' )
    tree.column( 'outs', width=60, anchor='center' )

    logging.debug( "Filling the tree with directory: %s" % directory )
    codefiles = fill_tree( tree, directory )
    logging.debug( "Done filling tree" )

    return tree, codefiles
