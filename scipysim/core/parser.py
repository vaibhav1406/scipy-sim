import os
import logging
import re

from codefile import CodeFile

def fill_tree( tree, directory ):
    '''Parse a directory and add to an existing tree.
    Return a dictionary of the tree id: CodeFile'''
    codefiles = {}
    for file_tuple in os.walk( directory ):
        '''The tuples contains:
            [0] - The path
            [1] - Subdirectories
            [2] - Files
        '''
        # Find out where we are in the tree
        parent_node = os.path.dirname( os.path.relpath( file_tuple[0], directory ) )
        current_node = os.path.relpath( file_tuple[0], directory )
        if current_node is ".": current_node = ""
        logging.debug( "Current node is: <%s>, Parent node is: <%s>" % ( current_node, parent_node ) )

        # Search for interesting files
        python_file_regex = re.compile( "^(?!tests?).*[^_]\.py$", re.IGNORECASE )
        files = filter( python_file_regex.search, file_tuple[2] )
        logging.info( "Under the %s directory are %d files: \n%s" % ( os.path.basename( file_tuple[0] ), len( files ), files ) )

        logging.debug( "Add the files in directory to the current node" )
        for file in files:
            logging.debug( "Inserting %s underneath an existing node" % file )
            node = os.path.relpath( os.path.join( file_tuple[0], file ), directory )
            codefiles[node] = CodeFile( os.path.join( file_tuple[0], file ) )
            tree.insert( current_node, 'end', node, text=file, tags=( 'node' ) )

            logging.debug( "Inserted '%s' node under '%s' with ID: '%s'" % ( file, current_node, node ) )
            tree.set( node, 'ins', codefiles[node].num_inputs )
            tree.set( node, 'outs', codefiles[node].num_outputs )


        # Must add the (sub)directories to the tree as nodes under the current node.
        for subdir in file_tuple[1]:
            '''
            subdir is going to be a string like "trig"
            but the tree id will be math/trig
            '''
            node = os.path.relpath( os.path.join( file_tuple[0], subdir ), directory )
            logging.debug( "Child node is: <%s>" % node )
            tree.insert( current_node, 'end', node, text=subdir.title(), tags=( 'dir' ) )
    return codefiles