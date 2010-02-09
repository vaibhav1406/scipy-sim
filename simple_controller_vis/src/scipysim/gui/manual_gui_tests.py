'''
Created on Feb 8, 2010
Works on Ubuntu.

* Tix is in the Python standard library but seems to be a third party extension to tk so doesn't 
  work off the bat.

* ttk is a third party Python addon, but needs either a new tk (8.5) or the tile extension.

@author: brianthorne
'''

from Tkinter import *
from ttk import *
from ttk import Treeview

from os import walk, path
import re
import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("GUI test module loaded, logging enabled")
# Find the path to this file
PATH_TO_SCRIPT = path.dirname(path.realpath(__file__))
EXAMPLES_DIRECTORY = path.split(PATH_TO_SCRIPT)[0]

def go(*args):
    print "Going"

root = Tk()
root.title("TreeView Test")

mainframe = Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

entry = Entry(mainframe, width=7)
entry.grid(column=2, row=1, sticky=(W, E))


Button(mainframe, text="Do Something", command=go).grid(column=3, row=3, sticky=W)

Label(mainframe, text="Testing Treeview").grid(column=1,row=4)



def fill_tree(tree, directory):
    '''Parse a directory and add to an existing tree'''
    for file_tuple in walk(directory):
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
        python_file_regex = re.compile("[^_]\.py$", re.IGNORECASE)          
        files = filter(python_file_regex.search, file_tuple[2])
        logging.info("Under the %s directory are %d files: \n%s" % (path.basename(file_tuple[0]), len(files), files))
        
        # Add the files to the parent node
        for file in files:
            # Inserted underneath an existing node:
            tree.insert(current_node, 'end', text=file)
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
            tree.insert(current_node, 'end', node, text=subdir.title())
            
        

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
    """
    # Inserted at the root, program chooses id as 'widgets'
    # if 0 is used in place of 'end' it would go to the start
    tree.insert('', 'end', 'widgets', text='Display')
    
    # Treeview chooses the id:
    id = tree.insert('', 'end', text='Math')
    
    
    
    # And again...
    trigID = tree.insert(id, 'end', text='Trig')
    
    sinID = tree.insert(trigID, 'end', text="Sin")
    tree.set(sinID, 'ins', 1)
    tree.set(sinID, 'outs', 1)
    """
import os
src_dir = os.path.normpath(__file__ + '../../../')
actor_dir = os.path.join(src_dir, 'actors')
make_tree(mainframe, actor_dir)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

entry.focus()
root.bind('<Return>', go)

root.mainloop()
